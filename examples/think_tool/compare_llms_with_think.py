import argparse
import os
import re
from datetime import datetime
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from plotnine import (
    aes,
    coord_cartesian,
    element_line,
    element_rect,
    element_text,
    geom_col,
    geom_text,
    ggplot,
    labs,
    position_dodge,
    scale_fill_brewer,
    stage,
    theme,
    theme_minimal,
)

from report_logs import read_logs_into_table  # type: ignore


def create_parallel_coordinates_plot(
    df: pd.DataFrame,
    model_name: str,
    metrics: list[str] = ["accuracy", "total_tokens", "duration_seconds", "average_turns"],
    output_file: Optional[str] = None,
):
    """
    Create a parallel coordinates plot comparing 'no think' vs 'with think' for a single model.
    
    Args:
        df: DataFrame with columns: model, tools, and the metrics
        model_name: The model to visualize (e.g., 'anthropic/claude-sonnet-4-5')
        metrics: List of metric column names to include
        output_file: Path to save the output plot
    """
    # Default output file
    if output_file is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Create safe filename from model name
        safe_model_name = model_name.replace("/", "_").replace("-", "_")
        output_file = os.path.join(script_dir, f"parallel_coords_{safe_model_name}.png")
    
    # Filter for the specified model
    model_df = df[df["model"] == model_name].copy()
    
    if model_df.empty:
        print(f"No data found for model: {model_name}")
        print(f"Available models: {df['model'].unique().tolist()}")
        return
    
    if len(model_df) < 2:
        print(f"Need both 'default' and 'with think' data for model: {model_name}")
        return
    
    # Replace "default" with "no think" for display
    model_df["tools"] = model_df["tools"].replace("default", "no think")
    
    # Prepare data for plotting
    fig, axes = plt.subplots(1, len(metrics) - 1, figsize=(14, 6))
    if len(metrics) == 2:
        axes = [axes]
    
    # Define metric display names and whether lower is better
    metric_config = {
        "accuracy": {"display": "Accuracy", "lower_better": False, "format": "{:.0%}"},
        "total_tokens": {"display": "Total Tokens", "lower_better": True, "format": "{:,.0f}"},
        "average_turns": {"display": "Avg Turns", "lower_better": True, "format": "{:.1f}"},
        "duration_seconds": {"display": "Duration (s)", "lower_better": True, "format": "{:,.0f}"},
    }
    
    # Colors for each tool setup
    colors = {"no think": "#66c2a5", "with think": "#fc8d62"}  # Set2 palette colors
    
    # Get data for each tools configuration
    data_by_tools: dict[str, pd.Series] = {}
    for tools in ["no think", "with think"]:
        filtered = model_df[model_df["tools"] == tools]
        if not filtered.empty:
            data_by_tools[tools] = filtered.iloc[0]
    
    # Normalize data for each metric (min-max within the model's data range)
    normalized_data: dict[str, list[float]] = {}
    for tools, row in data_by_tools.items():
        normalized_data[tools] = []
        for metric in metrics:
            # Get min/max from all data for this metric (for proper scaling)
            metric_min = df[metric].min()
            metric_max = df[metric].max()
            value = row[metric]
            # Normalize to 0-1
            if metric_max - metric_min > 0:
                norm_value = (value - metric_min) / (metric_max - metric_min)
            else:
                norm_value = 0.5
            normalized_data[tools].append(norm_value)
    
    # Plot on each axis segment
    for i, ax in enumerate(axes):
        # Set up the axis
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.05, 1.05)  # Add padding for labels
        
        # Plot lines for each tools configuration
        for tools, norm_values in normalized_data.items():
            ax.plot(
                [0, 1], 
                [norm_values[i], norm_values[i + 1]], 
                color=colors[tools], 
                linewidth=3,
                marker='o',
                markersize=10,
                label=tools if i == 0 else None,
                alpha=0.8
            )
        
        # Remove x-axis tick labels (we'll add custom labels)
        ax.set_xticks([])
        ax.set_xlabel("")
        
        # Add value labels on the left axis
        for tools, row in data_by_tools.items():
            value = row[metrics[i]]
            norm_val = normalized_data[tools][i]
            fmt = str(metric_config.get(metrics[i], {}).get("format", "{:.2f}"))
            ax.text(-0.08, norm_val, fmt.format(value), 
                   ha='right', va='center', fontsize=9, color=colors[tools], fontweight='bold')
        
        # Add value labels on the right axis (only for last segment)
        if i == len(axes) - 1:
            for tools, row in data_by_tools.items():
                value = row[metrics[i + 1]]
                norm_val = normalized_data[tools][i + 1]
                fmt = str(metric_config.get(metrics[i + 1], {}).get("format", "{:.2f}"))
                ax.text(1.08, norm_val, fmt.format(value), 
                       ha='left', va='center', fontsize=9, color=colors[tools], fontweight='bold')
        
        # Style the axis
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
        
        # Add vertical lines at edges
        ax.axvline(0, color='#333333', linewidth=2)
        ax.axvline(1, color='#333333', linewidth=2)
    
    # Add title and subtitle
    short_model = model_name.split("/")[-1]
    fig.suptitle(
        f"Accuracy and Costs for {short_model}: Think Tool",
        fontsize=16, fontweight='bold', y=0.98
    )
    fig.text(
        0.5, 0.93,
        "Parallel coordinates plot | GAIA level 1 | 50 samples per model | with and without the 'think' tool",
        ha='center', va='top', fontsize=10, color='#666666'
    )
    
    # Add legend
    handles = [plt.Line2D([0], [0], color=colors[t], linewidth=3, marker='o', markersize=8) 
               for t in ["no think", "with think"]]
    fig.legend(handles, ["no think", "with think"], loc='lower center', ncol=2, fontsize=11,
               frameon=True, fancybox=True, shadow=True)
    
    # Add metric labels at top of each axis
    for i, metric in enumerate(metrics):
        config = metric_config.get(metric, {"display": metric, "lower_better": False})
        x_pos = 0.12 + (i / (len(metrics) - 1)) * 0.76
        direction = "↓ lower is better" if config.get("lower_better", False) else "↑ higher is better"
        fig.text(
            x_pos, 0.84, 
            f"{config['display']}",
            ha='center', va='bottom', fontsize=12, fontweight='bold'
        )
        fig.text(
            x_pos, 0.80, 
            f"({direction})",
            ha='center', va='bottom', fontsize=9, color='#666666'
        )
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.12, top=0.78, left=0.12, right=0.88)
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"\nParallel coordinates plot saved to: {output_file}")
    
    return fig


def create_comparison_plot(
    df: pd.DataFrame, 
    metric: str = "accuracy",
    output_file: Optional[str] = None
):
    """
    Create a bar chart comparing model performance with 'think' vs 'no think' tools.
    
    Args:
        df: DataFrame with columns: model, tools, and the specified metric
        metric: The column name to compare (e.g., 'accuracy', 'total_tokens', 'average_turns', 'duration_seconds')
        output_file: Path to save the output plot (defaults to script directory with metric name)
    """
    # Default to saving in the same directory as this script
    if output_file is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_dir, f"compare_{metric}.png")
    
    if df.empty:
        print("No data to plot")
        return
    
    # Check if metric exists in dataframe
    if metric not in df.columns:
        print(f"Error: Metric '{metric}' not found in dataframe")
        return
    
    # Sort models alphanumerically for consistent ordering
    df = df.sort_values(["model", "tools"]).copy()
    
    # Replace "default" with "no think"
    df["tools"] = df["tools"].replace("default", "no think")
    
    # Convert model to categorical to preserve alphabetical order in plot
    model_order = sorted(df["model"].unique())
    df["model"] = pd.Categorical(df["model"], categories=model_order, ordered=True)
    
    # Ensure tools ordering: no think first, then with think
    df["tools"] = pd.Categorical(df["tools"], categories=["no think", "with think"], ordered=True)
    
    # Configure metric-specific settings
    metric_configs = {
        "accuracy": {
            "title": "Performance on GAIA level 1 Benchmark: Think Tool",
            "subtitle_direction": "Higher is better",
            "y_label": "Accuracy",
            "format_fn": lambda x: f"{x*100:.1f}%",
            "y_limits": (0.0, 1.08),
            "add_min_value": True,
            "min_value": 0.02,
        },
        "total_tokens": {
            "title": "Token Usage on GAIA level 1 Benchmark: Think Tool",
            "subtitle_direction": "Lower is better",
            "y_label": "Total Tokens",
            "format_fn": lambda x: f"{x:,.0f}",
            "y_limits": None,  # Auto-scale
            "add_min_value": False,
        },
        "average_turns": {
            "title": "Average Turns on GAIA level 1 Benchmark: Think Tool",
            "subtitle_direction": "Number of assistant turns",
            "y_label": "Average Turns",
            "format_fn": lambda x: f"{x:.1f}",
            "y_limits": None,  # Auto-scale
            "add_min_value": False,
        },
        "duration_seconds": {
            "title": "Duration on GAIA level 1 Benchmark: Think Tool",
            "subtitle_direction": "Lower is better",
            "y_label": "Duration (seconds)",
            "format_fn": lambda x: f"{x:,.0f}",
            "y_limits": None,  # Auto-scale
            "add_min_value": False,
        },
    }
    
    config = metric_configs.get(metric, metric_configs["accuracy"])
    
    # Create display column and labels
    df["metric_display"] = df[metric]
    if config["add_min_value"]:
        df["metric_display"] = df["metric_display"].apply(
            lambda x: max(x, config["min_value"]) if x == 0 else x
        )
    
    df["metric_label"] = df[metric].apply(config["format_fn"])  # type: ignore
    
    print(f"\nData to plot ({metric}):")
    print(df[["model", "tools", metric, "total_samples"]])
    
    # Create a single position_dodge object for alignment
    dodge_position = position_dodge(width=0.87)
    
    # Build the plot
    plot = (
        # 1. Initialize the plot and define aesthetics
        ggplot(df, aes(x="model", y="metric_display", fill="tools"))
        # 2. Add the column/bar geometry
        + geom_col(stat="identity", position=dodge_position, show_legend=True)
        # 2a. Add text labels on top of bars
        + geom_text(
            aes(
                label="metric_label",
                y=stage("metric_display", after_scale="y+0.02")
            ),
            position=dodge_position,
            va="bottom",
            size=9,
        )
        # 2b. Apply ColorBrewer palette for professional colors
        + scale_fill_brewer(type="qualitative", palette="Set2")
        # 4. Add labels and title
        + labs(
            title=str(config["title"]),
            subtitle=f"{config['subtitle_direction']} | 50 samples per model | with and without the 'think' tool | {datetime.now().strftime('%B %d, %Y')}",
            y=str(config["y_label"]),
            x="",
            fill="",
        )
        # 5. Apply a minimal theme
        + theme_minimal()
        # 6. Customize theme elements
        + theme(
            # Add horizontal gridlines for easier value reading
            panel_grid_major_y=element_line(color="#d0d0d0", size=0.5),
            panel_grid_minor_y=element_line(color="#e8e8e8", size=0.25),
            panel_grid_major_x=element_line(color="none"),
            panel_grid_minor_x=element_line(color="none"),
            # Style text elements
            plot_title=element_text(size=16, weight="bold"),
            plot_subtitle=element_text(size=11, color="#666666"),
            axis_title=element_text(size=12),
            axis_title_x=element_text(margin={"t": 10}),
            axis_title_y=element_text(margin={"r": 10}),
            axis_text_x=element_text(rotation=45, hjust=1, size=10),
            # Move legend to bottom with horizontal orientation
            legend_position="bottom",
            legend_direction="horizontal",
            legend_title=element_text(size=11),
            # Set figure dimensions
            figure_size=(12, 8),
        )
    )
    
    # Add y-axis limits if specified
    if config["y_limits"] is not None:
        plot = plot + coord_cartesian(ylim=config["y_limits"])  # type: ignore
    
    # Save the plot
    plot.save(output_file, dpi=300)
    print(f"\nPlot saved to: {output_file}")
    
    return plot


def load_or_create_dataframe(cache_file: str, force_refresh: bool = False) -> pd.DataFrame:
    """
    Load dataframe from cache file if it exists, otherwise process logs and save to cache.
    
    Args:
        cache_file: Path to the cache CSV file
        force_refresh: If True, ignore cache and reprocess logs
        
    Returns:
        DataFrame with the log data
    """
    # Check if cache file exists and we're not forcing a refresh
    if os.path.exists(cache_file) and not force_refresh:
        print(f"Loading cached data from: {cache_file}")
        df = pd.read_csv(cache_file)
        print(f"Loaded {len(df)} rows from cache")
        return df
    
    # Find folders that match the regex pattern
    log_folders = [
        f for f in os.listdir(".") 
        if (
            os.path.isdir(f) and 
            re.match(r"logs[2|3]?_gaia_level1_50_(default|think)$", f)
        )
    ]
    
    print(f"Found log folders: {log_folders}")
    
    if not log_folders:
        print("No matching log folders found!")
        print("Looking for folders matching pattern: logs[2|3]?_gaia_level1_50_(default|think)")
        return pd.DataFrame()
    
    # Create dataframe from logs
    print("Processing logs...")
    df = read_logs_into_table(log_folders)
    
    if not df.empty:
        # Save to cache file
        df.to_csv(cache_file, index=False)
        print(f"Saved {len(df)} rows to cache: {cache_file}")
    
    return df


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate comparison plots for think tool evaluation")
    parser.add_argument(
        "--refresh", 
        action="store_true", 
        help="Force refresh of cached data (reprocess logs)"
    )
    parser.add_argument(
        "--bar-charts",
        action="store_true",
        help="Generate bar charts comparing metrics across models"
    )
    parser.add_argument(
        "--parallel-coords",
        action="store_true", 
        help="Generate parallel coordinates plots for each model"
    )
    args = parser.parse_args()
    
    # If no specific plot type is requested, generate all
    generate_all = not args.bar_charts and not args.parallel_coords
    
    # Define cache file path in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_file = os.path.join(script_dir, "logs_data.csv")
    
    # Load or create dataframe
    df = load_or_create_dataframe(cache_file, force_refresh=args.refresh)
    
    if df.empty:
        print("No data found")
    else:
        # Create bar chart comparison plots for all metrics
        if generate_all or args.bar_charts:
            metrics = ["accuracy", "total_tokens", "average_turns", "duration_seconds"]
            
            for metric in metrics:
                print(f"\n{'='*60}")
                print(f"Creating bar chart for: {metric}")
                print('='*60)
                create_comparison_plot(df, metric=metric)
        
        # Create parallel coordinates plots for all models
        if generate_all or args.parallel_coords:
            models = sorted(df["model"].unique())
            
            for model in models:
                print(f"\n{'='*60}")
                print(f"Creating parallel coordinates plot for: {model}")
                print('='*60)
                create_parallel_coordinates_plot(df, model_name=model)

