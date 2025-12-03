import os
import re
from datetime import datetime
from typing import Optional

import click

import matplotlib.pyplot as plt
import pandas as pd
from plotnine import (
    aes,
    coord_cartesian,
    element_line,
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

# Shared configuration for metrics
METRIC_CONFIG = {
    "accuracy": {
        "display": "Accuracy",
        "title": "Performance on GAIA level 1 Benchmark: Think Tool",
        "subtitle_direction": "Higher is better",
        "y_label": "Accuracy",
        "lower_better": False,
        "format": "{:.0%}",
        "format_fn": lambda x: f"{x*100:.1f}%",
        "y_limits": (0.0, 1.08),
        "add_min_value": True,
        "min_value": 0.02,
    },
    "total_tokens": {
        "display": "Total Tokens",
        "title": "Token Usage on GAIA level 1 Benchmark: Think Tool",
        "subtitle_direction": "Lower is better",
        "y_label": "Total Tokens",
        "lower_better": True,
        "format": "{:,.0f}",
        "format_fn": lambda x: f"{x:,.0f}",
        "y_limits": None,
        "add_min_value": False,
    },
    "average_turns": {
        "display": "Avg Turns",
        "title": "Average Turns on GAIA level 1 Benchmark: Think Tool",
        "subtitle_direction": "Number of assistant turns",
        "y_label": "Average Turns",
        "lower_better": True,
        "format": "{:.1f}",
        "format_fn": lambda x: f"{x:.1f}",
        "y_limits": None,
        "add_min_value": False,
    },
    "duration_seconds": {
        "display": "Duration (s)",
        "title": "Duration on GAIA level 1 Benchmark: Think Tool",
        "subtitle_direction": "Lower is better",
        "y_label": "Duration (seconds)",
        "lower_better": True,
        "format": "{:,.0f}",
        "format_fn": lambda x: f"{x:,.0f}",
        "y_limits": None,
        "add_min_value": False,
    },
}

# Colors for tool configurations (Set2 palette)
TOOL_COLORS = {"no think": "#66c2a5", "with think": "#fc8d62"}


def get_visuals_dir() -> str:
    """Get the visuals directory path, creating it if necessary."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    visuals_dir = os.path.join(script_dir, "visuals")
    os.makedirs(visuals_dir, exist_ok=True)
    return visuals_dir


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare dataframe for plotting: sort, replace labels, set categorical ordering."""
    df = df.sort_values(["model", "tools"]).copy()
    df["tools"] = df["tools"].replace("default", "no think")
    df["model"] = pd.Categorical(df["model"], categories=sorted(df["model"].unique()), ordered=True)
    df["tools"] = pd.Categorical(df["tools"], categories=["no think", "with think"], ordered=True)
    return df


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
    if output_file is None:
        safe_model_name = model_name.replace("/", "_").replace("-", "_")
        output_file = os.path.join(get_visuals_dir(), f"parallel_coords_{safe_model_name}.png")
    
    # Filter and prepare data for the specified model
    model_df = df[df["model"] == model_name].copy()
    
    if model_df.empty:
        print(f"No data found for model: {model_name}")
        print(f"Available models: {df['model'].unique().tolist()}")
        return
    
    if len(model_df) < 2:
        print(f"Need both 'default' and 'with think' data for model: {model_name}")
        return
    
    model_df["tools"] = model_df["tools"].replace("default", "no think")
    
    # Prepare plot
    fig, axes = plt.subplots(1, len(metrics) - 1, figsize=(14, 6))
    if len(metrics) == 2:
        axes = [axes]
    
    # Get data for each tools configuration
    data_by_tools: dict[str, pd.Series] = {}
    for tools in ["no think", "with think"]:
        filtered = model_df[model_df["tools"] == tools]
        if not filtered.empty:
            data_by_tools[tools] = filtered.iloc[0]
    
    # Normalize data for each metric (min-max scaling)
    normalized_data: dict[str, list[float]] = {}
    for tools, row in data_by_tools.items():
        normalized_data[tools] = []
        for metric in metrics:
            metric_min, metric_max = df[metric].min(), df[metric].max()
            value = row[metric]
            norm_value = (value - metric_min) / (metric_max - metric_min) if metric_max > metric_min else 0.5
            normalized_data[tools].append(norm_value)
    
    # Plot on each axis segment
    for i, ax in enumerate(axes):
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.05, 1.05)
        
        # Plot lines for each tools configuration
        for tools, norm_values in normalized_data.items():
            ax.plot([0, 1], [norm_values[i], norm_values[i + 1]], 
                   color=TOOL_COLORS[tools], linewidth=3, marker='o', markersize=10,
                   label=tools if i == 0 else None, alpha=0.8)
        
        ax.set_xticks([])
        ax.set_xlabel("")
        
        # Add value labels on the left axis
        for tools, row in data_by_tools.items():
            value = row[metrics[i]]
            fmt = str(METRIC_CONFIG.get(metrics[i], {}).get("format", "{:.2f}"))
            ax.text(-0.08, normalized_data[tools][i], fmt.format(value), 
                   ha='right', va='center', fontsize=9, color=TOOL_COLORS[tools], fontweight='bold')
        
        # Add value labels on the right axis (only for last segment)
        if i == len(axes) - 1:
            for tools, row in data_by_tools.items():
                value = row[metrics[i + 1]]
                fmt = str(METRIC_CONFIG.get(metrics[i + 1], {}).get("format", "{:.2f}"))
                ax.text(1.08, normalized_data[tools][i + 1], fmt.format(value), 
                       ha='left', va='center', fontsize=9, color=TOOL_COLORS[tools], fontweight='bold')
        
        # Style the axis - hide all spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_yticks([])
        ax.axvline(0, color='#333333', linewidth=2)
        ax.axvline(1, color='#333333', linewidth=2)
    
    # Add title and subtitle
    short_model = model_name.split("/")[-1]
    fig.suptitle(f"Accuracy and Costs for {short_model}: Think Tool", fontsize=16, fontweight='bold', y=0.98)
    fig.text(0.5, 0.93, "Parallel coordinates plot | GAIA level 1 | 50 samples per model | with and without the 'think' tool",
             ha='center', va='top', fontsize=10, color='#666666')
    
    # Add legend
    handles = [plt.Line2D([0], [0], color=TOOL_COLORS[t], linewidth=3, marker='o', markersize=8) 
               for t in ["no think", "with think"]]
    fig.legend(handles, ["no think", "with think"], loc='lower center', ncol=2, fontsize=11,
               frameon=True, fancybox=True, shadow=True)
    
    # Add metric labels at top of each axis
    for i, metric in enumerate(metrics):
        cfg = METRIC_CONFIG.get(metric, {"display": metric, "lower_better": False})
        x_pos = 0.12 + (i / (len(metrics) - 1)) * 0.76
        direction = "↓ lower is better" if cfg.get("lower_better", False) else "↑ higher is better"
        fig.text(x_pos, 0.84, str(cfg['display']), ha='center', va='bottom', fontsize=12, fontweight='bold')
        fig.text(x_pos, 0.80, f"({direction})", ha='center', va='bottom', fontsize=9, color='#666666')
    
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
        output_file: Path to save the output plot (defaults to visuals directory)
    """
    if output_file is None:
        output_file = os.path.join(get_visuals_dir(), f"compare_{metric}.png")
    
    if df.empty:
        print("No data to plot")
        return
    
    if metric not in df.columns:
        print(f"Error: Metric '{metric}' not found in dataframe")
        return
    
    df = prepare_dataframe(df)
    config = METRIC_CONFIG.get(metric, METRIC_CONFIG["accuracy"])
    
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


@click.command()
@click.option(
    "--refresh",
    is_flag=True,
    help="Force refresh of cached data (reprocess logs)"
)
@click.option(
    "--bar-charts",
    is_flag=True,
    help="Generate bar charts comparing metrics across models"
)
@click.option(
    "--parallel-coords",
    is_flag=True,
    help="Generate parallel coordinates plots for each model"
)
def main(refresh: bool, bar_charts: bool, parallel_coords: bool) -> None:
    """Generate comparison plots for think tool evaluation."""
    # If no specific plot type is requested, generate all
    generate_all = not bar_charts and not parallel_coords
    
    # Define cache file path in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_file = os.path.join(script_dir, "logs_data.csv")
    
    # Load or create dataframe
    df = load_or_create_dataframe(cache_file, force_refresh=refresh)
    
    if df.empty:
        print("No data found")
    else:
        # Create bar chart comparison plots for all metrics
        if generate_all or bar_charts:
            metrics = ["accuracy", "total_tokens", "average_turns", "duration_seconds"]
            
            for metric in metrics:
                print(f"\n{'='*60}")
                print(f"Creating bar chart for: {metric}")
                print('='*60)
                create_comparison_plot(df, metric=metric)
        
        # Create parallel coordinates plots for all models
        if generate_all or parallel_coords:
            models = sorted(df["model"].unique())
            
            for model in models:
                print(f"\n{'='*60}")
                print(f"Creating parallel coordinates plot for: {model}")
                print('='*60)
                create_parallel_coordinates_plot(df, model_name=model)


if __name__ == "__main__":
    main()

