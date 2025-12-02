# Inspect Tools: Think before using Think (Tool)

This example evaluates the utility of the `think()` tool on the [GAIA Benchmark](https://arxiv.org/abs/2311.12983) using the [Inspect AI](https://inspect.aisi.org.uk/) evaluation framework.

## Background

Earlier this year Anthropic introduced the ["think" tool](https://www.anthropic.com/engineering/claude-think-tool): *Enabling Claude to stop and think in complex tool use situations*. Anthropic both uses and contributes to the Inspect evaluation framework, so it's no surprise that the `think()` tool is part of the Inspect standard tools.

### The think() Tool

The `think()` tool provides models with the ability to pause and add an additional thinking step in the form of reasoning about available tools and the way to achieve its final goal in the context of other tools, current state, and all the information it needs to move forward.

Each call to `think()` tool returns an empty string and is designed to enable the model to include an additional thinking step as part of getting to the answer by adding a generated call message passed as "thought" in the tool input.

**When to use the think() tool:**

- Enable the model to stop and think about whether it has all the information it needs to move forward
- Improve sequential decision making when each action builds on previous ones and mistakes are costly
- Help perform long chains of tool calls in long multi-step conversations with the user and processing information in tool call results
- Improve model's tool use ability: analyze and reason about utilizing available tools, analyzing results of previous tool use, and planning its actions before acting
- Call complex tools and analyze tool outputs carefully in long chains of tool calls
- Follow detailed guidelines and verify compliance in policy-heavy environments

### The GAIA Benchmark

GAIA Benchmark (stands for General AI Assistant) "proposes real-world questions that require a set of fundamental abilities such as reasoning, multi-modality handling, web browsing, and generally tool-use proficiency. GAIA questions are conceptually simple for humans yet challenging for most advanced AIs."

## Project Structure

```
think_tool/
├── gaia_eval.py                 # Main evaluation script with think tool
├── compare_llms_with_think.py   # Visualization and comparison script
├── report_logs.py               # Log processing utilities
├── compose.yaml                 # Docker sandbox configuration
├── logs_data.csv                # Cached evaluation results
├── compare_*.png                # Bar chart comparisons
├── parallel_coords_*.png        # Parallel coordinates plots
└── TROUBLESHOOTING.md           # Common issues and solutions
```

## Prerequisites

### Environment Setup

1. **Install dependencies** using uv:
   ```bash
   uv sync
   ```

2. **Set up API keys** for the models you want to evaluate:
   ```bash
   export OPENAI_API_KEY=<your-openai-key>
   export ANTHROPIC_API_KEY=<your-anthropic-key>
   export MISTRAL_API_KEY=<your-mistral-key>  # optional
   ```

3. **Set up HuggingFace token** for GAIA dataset access:
   ```bash
   export HF_TOKEN=<your-hf-token>
   ```
   > **Note:** You need to request access to the GAIA dataset on HuggingFace first.

4. **Docker** is required for the sandbox environment. Make sure Docker Desktop is running.

## Running Evaluations

### Using the Evaluation Script

The main evaluation script is `gaia_eval.py`. Configure the run by modifying the variables at the bottom of the file:

```python
# Configuration options
models = [
    "openai/gpt-5-nano",
    "openai/gpt-5-mini",
    "openai/gpt-4o-mini",
    "openai/gpt-4.1-mini",
    "anthropic/claude-sonnet-4-5",
    "anthropic/claude-haiku-4-5",
    "anthropic/claude-sonnet-4-20250514",
    "anthropic/claude-3-5-haiku-20241022",
]

config_run_eval = True
config_eval_limit = 50           # Number of samples to evaluate
config_eval_max_samples = 10     # Parallel samples (adjust for Docker limits)
config_gaia_benchmark = gaia_level1
config_gaia_solver = gaia_solver_with_think  # or default_solver
```

Run the evaluation:

```bash
uv run python examples/think_tool/gaia_eval.py
```

### Running with and without Think Tool

To compare results with and without the think tool, you need to run two separate evaluations:

**With think tool:**
```python
config_gaia_solver = gaia_solver_with_think
config_log_dir = './logs_gaia_level1_50_think'
```

**Without think tool (default):**
```python
config_gaia_solver = default_solver
config_log_dir = './logs_gaia_level1_50_default'
```

### Using Command Line (Alternative)

You can also run GAIA evaluations directly from the command line:

```bash
uv run inspect eval inspect_evals/gaia_level1 --model openai/gpt-5-nano
```

## System Prompt for Think Tool

The effectiveness of the think tool depends heavily on the system prompt. The `gaia_eval.py` file includes a customized system prompt aligned with GAIA benchmark goals:

```python
gaia_system_prompt = """
You are an autonomous AI agent...

Use the think tool to think about the task and the tools available. 
It will not obtain new information or make any changes to the repository, 
but just log the thought. Use it when complex reasoning or brainstorming 
is needed before calling other tools. 

For example use think tool to:
- if you explore the resource (link) and find some information that appears 
  relevant, analyze with think tool its utility and relevance to the task 
  and how it can be used to lead to next steps in solving the task.
- if you receive some intermediate results, call think tool to brainstorm 
  ways to analyze the results and how to use them in the next steps.
- if you find some information that can be used to achieve the goal of the 
  task, call think tool to brainstorm ways to utilize the new information.
...
"""
```

## Generating Visualizations

After running evaluations, generate comparison visualizations using `compare_llms_with_think.py`.

### Prerequisites

Place your evaluation logs in folders matching this pattern:
- `logs_gaia_level1_50_default/` — results without think tool
- `logs_gaia_level1_50_think/` — results with think tool
- `logs2_gaia_level1_50_default/` — additional runs (optional)
- `logs2_gaia_level1_50_think/` — additional runs (optional)

### Generate All Visualizations

```bash
uv run python examples/think_tool/compare_llms_with_think.py
```

### Generate Specific Plot Types

```bash
# Bar charts only
uv run python examples/think_tool/compare_llms_with_think.py --bar-charts

# Parallel coordinates plots only
uv run python examples/think_tool/compare_llms_with_think.py --parallel-coords

# Force refresh cached data
uv run python examples/think_tool/compare_llms_with_think.py --refresh
```

### Generated Visualizations

**Bar Charts** (`compare_*.png`) compare metrics across all models:
- `compare_accuracy.png` — Accuracy comparison
- `compare_total_tokens.png` — Token usage comparison
- `compare_duration_seconds.png` — Duration comparison
- `compare_average_turns.png` — Average turns comparison

**Parallel Coordinates** (`parallel_coords_*.png`) show multi-metric comparison for each model individually, displaying accuracy, total tokens, duration, and average turns.

## Results

The evaluation was run on GAIA Level 1 benchmark (50 samples) with the following models:

| Model | Accuracy (no think) | Accuracy (with think) | Change |
|-------|--------------------|-----------------------|--------|
| anthropic/claude-sonnet-4-5 | 68% | 72% | +4% |
| anthropic/claude-sonnet-4-20250514 | 56% | 62% | +6% |
| anthropic/claude-haiku-4-5 | 54% | 40% | -14% |
| openai/gpt-5-mini | 64% | 62% | -2% |
| openai/gpt-4.1-mini | 26% | 28% | +2% |
| openai/gpt-5-nano | 24% | 22% | -2% |
| anthropic/claude-3-5-haiku-20241022 | 20% | 20% | 0% |
| openai/gpt-4o-mini | 10% | 12% | +2% |

### Key Findings

- **Claude Sonnet models** clearly benefited from the think tool with meaningful accuracy improvements
- Some models showed **no significant change or slight degradation** in performance
- The think tool adds additional costs (tokens, time) which may or may not be offset by accuracy gains
- Results demonstrate that for certain models and use cases, `think()` provides meaningful lift in accuracy with possibly no sacrifice in costs

### Cost Considerations

The think() tool comes with additional costs. Key metrics to consider:
- **Total tokens** — maps directly to API costs
- **Duration** — total evaluation time
- **Average turns** — number of assistant interactions

> **Warning:** Single runs can easily consume millions of tokens even for GAIA Level 1. Level 2 and Level 3 consume considerably more.

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues including:
- Docker network "Address Pools Fully Subnetted" error
- GAIA dataset download issues
- HuggingFace token setup
- Anthropic/OpenAI model names

## References

- [Anthropic Think Tool Blog Post](https://www.anthropic.com/engineering/claude-think-tool)
- [Inspect AI Documentation](https://inspect.aisi.org.uk/)
- [Inspect AI Think Tool Docs](https://inspect.aisi.org.uk/tools-standard.html#sec-think)
- [GAIA Benchmark Paper](https://arxiv.org/abs/2311.12983)
- [Inspect Evals Repository](https://github.com/UKGovernmentBEIS/inspect_evals)
- [LinkedIn Article: Inspect Tools - Think before using Think (Tool)](https://www.linkedin.com/pulse/inspect-tools-think-before-using-tool-gregory-kanevsky-9lvbc/)

## License

This example is part of the [inspect-examples](https://github.com/gkanevsky/inspect-examples) repository.

