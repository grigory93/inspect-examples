from datetime import datetime

import pandas as pd
from inspect_ai import eval_set
from inspect_ai.log import list_eval_logs, read_eval_log
from plotnine import (
    aes,
    coord_cartesian,
    element_line,  # For gridlines
    element_rect,  # For setting Y-axis limits
    element_text,
    facet_wrap,
    geom_col,
    geom_text,  # For text labels on bars
    ggplot,
    labs,
    position_dodge,  # For grouping
    scale_fill_brewer,
    stage,  # For ColorBrewer palettes
    theme,
    theme_minimal,
)

from inspect_evals.agentdojo import agentdojo
from inspect_evals.bold import bold
from inspect_evals.mmmu.mmmu import mmmu_multiple_choice, mmmu_open

config_run_eval = False
config_eval_limit = 100
config_log_dir = "./logs_200"

models = [
    "openai/gpt-4o-mini",
    "openai/gpt-5-nano",
    "mistral/mistral-small-latest",
    "anthropic/claude-haiku-4-5",
]

mmmu_subjects = [
    "Biology",
    "Chemistry",
    "Economics",
    "Electronics",
    "Finance",
    "Pharmacy",
    "Physics",
    "Psychology",
]

# run evaluation if config_run_eval is True
if config_run_eval is True:
    success, logs = eval_set(
        # tasks=[agentdojo(workspace="banking"), bold()],
        tasks=[mmmu_open(subjects=subject) for subject in mmmu_subjects]
        + [mmmu_multiple_choice(subjects=subject) for subject in mmmu_subjects],
        model=models,
        limit=config_eval_limit,
        log_dir=config_log_dir,
    )
    if success is False:
        raise Exception("Evaluation failed")
# read existing logs if config_run_eval is False
else:
    logs = []
    for eval_log_info in list_eval_logs(log_dir=config_log_dir):
        log = read_eval_log(eval_log_info)
        logs.append(log)

# create results dataframe
results = pd.DataFrame(
    columns=[
        "model",
        "eval_name",
        "dataset",
        "subject",
        "dataset_count",
        "correct_count",
        "score",
        "metric",
        "score_metric",
        "value",
        "input_tokens",
        "output_tokens",
        "total_tokens",
    ]
)
# read existing eval logs
if logs is not None:
    for log in logs:
        model_name = log.eval.model
        eval_name = log.eval.task.split("/", maxsplit=1)[1]
        dataset_name = log.eval.dataset.name
        dataset_count = log.eval.dataset.samples
        model_usage = log.stats.model_usage.get(model_name, {})
        input_tokens = model_usage.input_tokens
        output_tokens = model_usage.output_tokens
        total_tokens = model_usage.total_tokens
        if not log.samples:
            print(f"No samples found for {log.eval.task} with model {model_name} and dataset {dataset_name} with {log.eval.dataset.samples} samples")
            correct_count = 0
        else:
            score_name = log.eval.scorers[0].name
            correct_count = sum(1 for sample in log.samples if sample.scores[score_name].value == "C")
        subject = log.eval.task_args_passed["subjects"]
        for score in log.results.scores:
            score_name = score.name
            for metric_name, metric in score.metrics.items():
                metric_value = metric.value
                results.loc[len(results)] = {
                    "model": model_name,
                    "eval_name": eval_name,
                    "dataset": dataset_name,
                    "subject": subject,
                    "dataset_count": dataset_count,
                    "correct_count": correct_count,
                    "score": score_name,
                    "metric": metric_name,
                    "score_metric": f"{score_name}: {metric_name}",
                    "value": metric_value,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                }
else:
    raise Exception("No logs found")


# filter for the eval of interest
# dataset_filter = results["dataset"] == "AgentDojo"
metric_filter = results["metric"] == "accuracy"
results = results[metric_filter]

# Shorten model names for better legend readability
model_name_map = {
    "openai/gpt-4o-mini": "GPT-4o Mini",
    "mistral/mistral-small-latest": "Mistral Small",
    "anthropic/claude-haiku-4-5": "Claude Haiku 4.5",
}
results["model_short"] = results["model"].map(model_name_map).fillna(results["model"])

# Format eval names for better facet titles
eval_name_map = {
    "mmmu_multiple_choice": "Multiple Choice",
    "mmmu_open": "Open-Ended",
}
results["eval_name_formatted"] = (
    results["eval_name"].map(eval_name_map).fillna(results["eval_name"])
)

# Sort subjects alphabetically for better readability
results = results.sort_values(["eval_name_formatted", "subject", "model_short"])

# Convert subject to categorical to preserve alphabetical order in plot
subject_order = sorted(results["subject"].unique())
results["subject"] = pd.Categorical(
    results["subject"], categories=subject_order, ordered=True
)

# Create label for bar text showing "correct_count/dataset_count"
results["bar_label"] = (
    results["correct_count"].astype(str) + "/" + results["dataset_count"].astype(str)
)

# add this transformation to display the value as 0
results["value_display"] = results["value"].apply(lambda x: max(x, 0.02) if x == 0 else x)

print(results)

# Create a single position_dodge object to share between geom_col and geom_text
# This ensures text labels align perfectly with their corresponding bars
dodge_position = position_dodge(width=0.87)

# Build the plot using the Grammar of Graphics
plot = (
    # 1. Initialize the plot and define aesthetics
    ggplot(results, aes(x="subject", y="value_display", fill="model_short"))
    # 2. Add the column/bar geometry
    #    position_dodge() controls spacing between model groups (how much space each subject group takes)
    #    width controls individual bar thickness
    #    0.87 dodge with 0.82 bar width creates good separation with prominent, readable bars
    + geom_col(stat="identity", position="dodge", show_legend=True)
    # 2a. Add text labels on top of bars showing "correct_count/dataset_count"
    + geom_text(
        aes(
            label="bar_label",
            y=stage("value_display", after_scale="y+0.02")
        ),  # Only specify label, inherit fill from main aes for proper dodging
        position=dodge_position,  # Use the SAME dodge object as geom_col for perfect alignment
        va="bottom",  # Vertical alignment: bottom of text at top of bar
        size=7,  # Font size
    )
    # 2b. Apply ColorBrewer palette for professional, colorblind-friendly colors
    #     "Set2" palette: pastel colors that work well for categorical data
    + scale_fill_brewer(type="qualitative", palette="Set2")
    # 3. Facet the plot
    #    This creates a separate subplot for each unique value in 'eval_name_formatted'
    + facet_wrap("~ eval_name_formatted", ncol=1)
    # 3. Set Y-axis limits (with extra space at top for text labels)
    + coord_cartesian(ylim=(0.0, 1.08))
    # 4. Add labels and title
    + labs(
        title="MMMU Benchmark: LLM Performance Across Academic Subjects",
        subtitle=f"Evaluating {len(models)} models on {len(mmmu_subjects)} subjects | Sample size varies: 1-29 questions per subject | {datetime.now().strftime('%B %Y')}",
        y="Accuracy Score",
        x="Subject",
        fill="Model",  # Legend title for shortened model names
    )
    # 5. Apply a minimal theme
    + theme_minimal()
    # 6. (Optional) Customize theme elements
    + theme(
        # Add a border around each panel (facet)
        panel_border=element_rect(color="gray", fill=None, size=0.5),
        # Spacing between panels - nearly zero to reduce white space
        panel_spacing=0.01,  # Nearly zero spacing between vertically stacked facets
        # Add horizontal gridlines for easier value reading
        panel_grid_major_y=element_line(
            color="#d0d0d0", size=0.5
        ),  # Major Y-axis gridlines
        panel_grid_minor_y=element_line(
            color="#e8e8e8", size=0.25
        ),  # Minor Y-axis gridlines
        panel_grid_major_x=element_line(color="none"),  # Remove X-axis gridlines
        panel_grid_minor_x=element_line(color="none"),  # Remove minor X-axis gridlines
        # Rotate x-axis labels if needed
        axis_text_x=element_text(rotation=0, hjust=0.5),
        # Adjust title/subtitle/axis text sizes and styling
        plot_title=element_text(size=16, weight="bold"),  # Main title
        plot_subtitle=element_text(
            size=11, color="#666666"
        ),  # Subtitle with muted color
        axis_title=element_text(size=12),
        axis_title_x=element_text(margin={"t": 10}),  # Add space above x-axis title
        axis_title_y=element_text(
            margin={"r": 10}
        ),  # Add space to right of y-axis title
        strip_text_x=element_text(size=14, weight="bold"),  # Facet title text
        # Move legend to bottom with horizontal orientation
        legend_position="bottom",
        legend_direction="horizontal",
        # Adjust figure dimensions for 2 vertically stacked facets
        # Taller height to minimize white space and fill the figure area
        figure_size=(
            14,
            12,
        ),  # More height for vertical facet layout to reduce white space
    )
)

# 7. Save the plot
plot.save("compare_llms_bar_chart.png", dpi=300)
