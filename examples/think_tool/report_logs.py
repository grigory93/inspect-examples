import os
import re
import json
import requests
import pandas as pd
from inspect_ai.log import EvalSample, list_eval_logs, read_eval_log
from inspect_ai.model import ChatMessageAssistant, ModelUsage

from datetime import datetime

def parse_time(t: str | datetime) -> datetime | None:
    if isinstance(t, datetime):
        return t
    try:
        return datetime.fromisoformat(t)
    except Exception:
        return None

def list_mistral_models() -> list[str]:
    """
    List available Mistral models using the Mistral API via requests.
    Returns a list of model IDs.
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("Warning: MISTRAL_API_KEY environment variable not set.")
        return []

    url = "https://api.mistral.ai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        
        if "data" in response_json:
             return [model["id"] for model in response_json["data"]]
        else:
            print(f"Unexpected response format from Mistral API: {response.text}")
            return []
    except requests.RequestException as e:
        print(f"Error calling Mistral API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return []


def read_logs_into_table(log_folders: list[str]) -> pd.DataFrame:
    # Collect data from all logs
    data = []
    for folder in log_folders:
        for eval_log_info in list_eval_logs(log_dir=folder):
            log = read_eval_log(eval_log_info)

            # Extract metrics scores (overall)
            # if log.status == "success" and log.results is not None:
            if log.results is not None:
                metrics_dict = {}
                for score in log.results.scores:
                    for metric_name, metric in score.metrics.items():
                        metrics_dict[f"{score.name}_{metric_name}"] = metric.value
                total_samples = log.results.total_samples        
                completed_samples = log.results.completed_samples
                accuracy = log.results.scores[0].metrics["accuracy"].value

                model_name = log.eval.model
                # Compute duration in seconds between started_at and completed_at
                # Assume started_at and completed_at are either datetime or ISO string (handle both)
                started_at = log.stats.started_at
                completed_at = log.stats.completed_at
                s = parse_time(started_at)
                e = parse_time(completed_at)
                duration_seconds = (e - s).total_seconds() if s and e else None

                model_usage: ModelUsage = log.stats.model_usage.get(model_name, ModelUsage())
                input_tokens = model_usage.input_tokens
                output_tokens = model_usage.output_tokens
                total_tokens = model_usage.total_tokens
                reasoning_tokens = model_usage.reasoning_tokens
                
                average_turns = None
                if log.samples:
                    turns = [0] * completed_samples
                    for i, sample in enumerate(log.samples):
                        if isinstance(sample, EvalSample):
                            turns[i] = sum([1 if isinstance(message, ChatMessageAssistant) else 0 for message in sample.messages])
                    average_turns = sum(turns) / completed_samples if completed_samples > 0 else 0

                data.append({
                    # "folder": folder,
                    "model": model_name,
                    "tools": "default" if folder.endswith("_default") else "with think",
                    "dataset": log.eval.dataset.name,
                    "subset": log.eval.task_display_name,
                    "total_samples": total_samples,
                    # "completed_samples": completed_samples,
                    "average_turns": average_turns,
                    "duration_seconds": duration_seconds,
                    # "input_tokens": input_tokens,
                    # "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    # "reasoning_tokens": reasoning_tokens,
                    "accuracy": accuracy,
                    # **metrics_dict,
                })

    return pd.DataFrame(data)

if __name__ == "__main__":
    # List Mistral models
    print("Available Mistral Models:")
    models = list_mistral_models()
    for model in models:
        print(f" - {model}")
    print("-" * 20)

    # Find folders that match the regex pattern 
    log_folders = [
        f for f in os.listdir(".") 
        if (
            os.path.isdir(f) and 
            re.match(r"logs[2|3]?_gaia_level1_50_(default|think)$", f)
        )
    ]

    # Create dataframe and print
    df = read_logs_into_table(log_folders)
    print(df)
