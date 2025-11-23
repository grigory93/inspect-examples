import os
import pandas as pd
from inspect_ai.log import list_eval_logs, read_eval_log

# Find folders starting with "logs_gaia_"
log_folders = [f for f in os.listdir(".") if os.path.isdir(f) and f.startswith("logs_gaia_")]

# Collect data from all logs
data = []
for folder in log_folders:
    for eval_log_info in list_eval_logs(log_dir=folder):
        log = read_eval_log(eval_log_info)
        
        # Extract metrics scores (overall)
        metrics_dict = {}
        if log.results is not None:
            for score in log.results.scores:
                for metric_name, metric in score.metrics.items():
                    metrics_dict[f"{score.name}_{metric_name}"] = metric.value
        
        data.append({
            "folder": folder,
            "model": log.eval.model,
            "dataset": log.eval.dataset.name,
            **metrics_dict
        })

# Create dataframe and print
df = pd.DataFrame(data)
print(df)

