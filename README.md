# Inspect AI Examples

This directory contains examples of using the Inspect AI framework to evaluate LLM agentic capabilities using web browsing tasks.

## Overview

The browser task tests a model's ability to:
- Use tools (specifically web_browser)
- Navigate websites and follow multi-step instructions
- Extract relevant information from web pages
- Synthesize and summarize information

### Project Structure

Complete directory layout:

```
inspect-examples/
├── 📁 examples/              # Python package with evaluation tasks
│   ├── __init__.py                   # Package initialization
│   └── browser/                      # Browser example
│       ├── __init__.py
│       ├── browser.py                # Browser task
│       ├── compose.yaml              # Docker configuration
│       └── README.md                 # Browser example documentation
│
├── 📁 logs/                          # Evaluation logs (auto-created)
│   └── *.json                        # Individual log files
│
├── 📁 .venv/                         # Virtual environment (optional)
│   └── ...                           # Python packages
│
├── 📄 pyproject.toml                 # Python project configuration & dependencies
├── 📄 uv.lock                        # uv lockfile (auto-generated)
├── 📄 .python-version                # Python version specification (3.11)
│
├── 📖 README.md                      # Complete documentation (this file)
├── 📖 QUICKSTART.md                  # 5-minute quick start guide
├── 📖 PLAN.md                        # Implementation plan & architecture
├── 📖 CHANGELOG.md                   # Project history and changes
│
├── 🔧 setup_with_uv.sh               # Interactive setup script
├── 🔧 run_comparison.sh              # Multi-model comparison script
└── 🔧 example_commands.sh            # Collection of example commands
```

## Quick Start

Get started in 5 minutes:

1. **Install uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Install dependencies**: `uv pip install -e ".[openai]"`
3. **Set API key**: `export OPENAI_API_KEY=your-key-here`
4. **Run evaluation**: `inspect eval examples/browser/browser.py --model openai/gpt-4o-mini`
5. **View results**: `inspect view`

For detailed instructions, see the sections below.

## Documentation Guide

| File | Purpose |
|------|---------|
| **README.md** | Complete documentation (you are here) - installation, usage, creating examples |
| **QUICKSTART.md** | Step-by-step beginner guide - get running in 5 minutes |
| **PLAN.md** | Implementation plan & architecture - design decisions and evaluation methodology |
| **CHANGELOG.md** | Project history and changes - what changed and when |
| **examples/browser/README.md** | Browser example documentation - task details and customization |

### Helper Scripts

| Script | Purpose |
|--------|---------|
| **setup_with_uv.sh** | Interactive setup - checks/installs uv, selects providers, installs dependencies |
| **run_comparison.sh** | Multi-model testing - runs evaluation across multiple models systematically |
| **example_commands.sh** | Command reference - copy/paste individual commands, troubleshooting examples |

## Prerequisites

**Requirements:**
- Python 3.10+ (3.11 recommended)
- Docker (for sandboxing)
- uv package manager
- API key for at least one model provider

### 1. Install uv Package Manager

First, install `uv` - a fast Python package manager written in Rust.

**Why uv?**
- ⚡ **10-100x faster** than pip for installations
- 🔒 **Better dependency resolution** with modern lockfiles
- 🎯 **Single tool** for package management, virtual environments, and Python version management
- 🔄 **Drop-in replacement** for pip commands

**Installation:**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv

# Or with pip
pip install uv

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Inspect AI and Dependencies

**Option A: Using the Automated Setup Script (Recommended)**

```bash
cd inspect-examples
./setup_with_uv.sh
```

This interactive script will:
1. Check if uv is installed (and install it if needed)
2. Let you select which providers to install
3. Install all dependencies
4. Provide instructions for setting API keys
5. Check if Docker is running

**Option B: Manual Installation**

```bash
# Install base inspect-ai
uv pip install inspect-ai

# Or use the project file to install with specific providers
cd inspect-examples

# Install with all providers
uv pip install -e ".[all-providers]"

# Or install with specific provider(s)
uv pip install -e ".[openai]"
uv pip install -e ".[openai,anthropic,mistral]"
```

**Using Virtual Environments:**

```bash
# Create a virtual environment
uv venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate

# Install dependencies in the venv
uv pip install -e ".[all-providers]"
```

### 3. Set Up Model Provider API Keys

**OpenAI:**
```bash
export OPENAI_API_KEY=your-openai-api-key
```

**Anthropic:**
```bash
export ANTHROPIC_API_KEY=your-anthropic-api-key
```

**AI21:**
```bash
export AI21_API_KEY=your-ai21-api-key
```

**Mistral:**
```bash
export MISTRAL_API_KEY=your-mistral-api-key
```

**Google:**
```bash
export GOOGLE_API_KEY=your-google-api-key
```

### 4. Supported Model Providers

**Currently configured:**
- **OpenAI**: GPT-4, GPT-4o, GPT-4 Turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus
- **Mistral**: Mistral Large, Mistral Medium
- **AI21**: Jamba 1.5 Large
- **Google**: Gemini 2.0 Flash, Gemini Pro

Install providers as needed:
```bash
# Single provider
uv pip install -e ".[openai]"

# Multiple providers
uv pip install -e ".[openai,anthropic,mistral]"

# All providers
uv pip install -e ".[all-providers]"
```

### 5. Docker Setup (Required for Sandboxing)

The browser task uses Docker for sandboxing to securely execute model-generated code:

```bash
# Install Docker if you haven't already
# Visit: https://docs.docker.com/get-docker/

# Verify Docker is running
docker ps
```

## pyproject.toml Structure

This project uses `pyproject.toml` for dependency management:

```toml
[project]
name = "inspect-examples"
dependencies = [
    "inspect-ai>=0.3.0",
]

[project.optional-dependencies]
openai = ["openai>=1.0.0"]
anthropic = ["anthropic>=0.18.0"]
mistral = ["mistralai>=1.0.0"]
ai21 = ["ai21>=2.0.0"]
google = ["google-genai>=0.2.0"]
all-providers = [
    # All provider packages
]
```

## Running the Browser Task

### Single Model Evaluation

Run the task with a specific model:

```bash
# Test with OpenAI GPT-4o-mini
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini

# Test with Anthropic Claude Haiku
inspect eval examples/browser/browser.py --model anthropic/claude-haiku-4-5

# Test with Mistral Small
inspect eval examples/browser/browser.py --model mistral/mistral-small-latest
```

### Using Helper Scripts

This project includes convenience scripts for easier setup and comparison:

```bash
# Guided setup with uv
./setup_with_uv.sh

# Compare multiple models automatically
./run_comparison.sh
```

## Common Commands Reference

```bash
# List available tasks in browser example
inspect list examples/browser/browser.py

# Run evaluation with specific model
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini

# Run the comparison script (evaluates multiple models)
./run_comparison.sh

# View all evaluation results
inspect view

# Check evaluation history
inspect history
```

## Viewing Results

### Using Inspect View (Web Interface)

After running evaluations, view the results in a web browser:

```bash
inspect view
```

This opens a web-based interface showing:
- Task summaries
- Individual sample results
- Message histories
- Tool usage
- Scores and metrics

### VS Code Extension

If you're using VS Code, install the Inspect VS Code Extension for integrated log viewing:

1. Open VS Code
2. Go to Extensions
3. Search for "Inspect AI"
4. Install the extension

### Log Files

By default, logs are saved to `./logs/` directory with timestamped filenames:

```
logs/
├── 2024-11-03T12-00-00_browser_gpt-4o-mini.json
├── 2024-11-03T12-15-00_browser_claude-haiku.json
└── ...
```

Each log contains:
- Complete message history
- Tool calls and responses
- Model outputs
- Scores and metrics
- Timing information
- Metadata

View logs with:
```bash
inspect view                           # Web interface
inspect view logs/specific-log.json    # Specific log
```

## Key Features

- **Fast Setup**: 5-minute installation with uv
- **Multi-Model Support**: Compare OpenAI, Anthropic, Mistral, Google, and AI21 models
- **Sandboxed Execution**: Docker isolation for secure code execution
- **Visual Interface**: Web-based log viewer with detailed insights
- **Extensible**: Easy to add custom evaluation tasks
- **Comprehensive Documentation**: Multiple guides for different use cases

## Understanding the Task

### Task Structure

Located in `examples/browser/browser.py`:

```python
@task
def browser():
    return Task(
        dataset=[...],          # Samples to evaluate
        solver=[...],           # How to solve (tools + generation)
        scorer=model_graded_qa(),  # How to score the results
        sandbox="docker"        # Security sandbox
    )
```

### Components

1. **Dataset**: Contains input prompts for the model
2. **Solver**: Chain of operations (use_tools + generate)
   - `use_tools(web_browser())`: Provides web browsing capability
   - `generate()`: Generates the final response
3. **Scorer**: `includes()` checks if key information is present in the output
4. **Sandbox**: Docker container for secure execution

## Comparison Metrics

When comparing models, consider:

1. **Task Success Rate**: Did the model complete the task?
2. **Tool Usage**: How effectively did the model use the web_browser tool?
3. **Information Quality**: How accurate and complete was the summary?
4. **Efficiency**: How many steps/tokens did it take?

## Usage Patterns

### Daily Evaluation Workflow

```bash
# 1. Activate environment (if using venv)
source .venv/bin/activate

# 2. Ensure API key is set
echo $OPENAI_API_KEY

# 3. Run evaluation
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini

# 4. View results
inspect view
```

### Creating New Examples

Each example should be organized in its own subfolder within `examples/`:

**Example Structure:**
```
examples/
└── example_name/
    ├── __init__.py              # Package initialization, exports tasks
    ├── task_file.py             # Main task definition(s)
    ├── compose.yaml             # Docker config (if using sandbox)
    ├── README.md                # Example-specific documentation
    └── [supporting files]       # Data files, helpers, etc.
```

**Step-by-Step Guide:**

1. **Create Example Folder**
```bash
mkdir examples/my_example
cd examples/my_example
```

2. **Create Task File** (`my_task.py`)
```python
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import generate

@task
def my_task():
    return Task(
        dataset=[
            Sample(
                input="Your evaluation prompt",
                target="Expected answer"
            )
        ],
        solver=[generate()],
        scorer=match()
    )
```

3. **Create Package Init** (`__init__.py`)
```python
"""My Example - Brief description"""
from .my_task import my_task
__all__ = ["my_task"]
```

4. **Create Documentation** (`README.md`)
```markdown
# My Example

## What This Tests
Description of capabilities evaluated.

## Running the Task
\`\`\`bash
inspect eval examples/my_example/my_task.py --model openai/gpt-4o-mini
\`\`\`

## Customization
How to modify and extend the task.
```

5. **Test Your Example**
```bash
inspect list examples/my_example/my_task.py
inspect eval examples/my_example/my_task.py --model openai/gpt-4o-mini
inspect view
```

**Example Categories:**

Examples can cover various domains:
- **Agentic Tasks**: Tool usage, multi-step problem solving (e.g., browser navigation)
- **Knowledge & Reasoning**: Factual knowledge, logic, math problems
- **Coding Tasks**: Code generation, understanding, debugging
- **Multimodal**: Image, audio, video understanding
- **Safety & Alignment**: Content moderation, bias evaluation, safety testing

## Development Workflow

### Adding a New Model Provider

1. Update `pyproject.toml`:
```toml
[project.optional-dependencies]
newprovider = ["newprovider-sdk>=1.0.0"]
```

2. Install it:
```bash
uv pip install -e ".[newprovider]"
```

3. Set API key:
```bash
export NEWPROVIDER_API_KEY=your-key
```

4. Run evaluation:
```bash
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini
```

### Modifying Existing Tasks

1. Edit the Python file:
```bash
nano examples/browser/browser.py
```

2. Run to test:
```bash
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini
```

3. View results:
```bash
inspect view
```

### Updating Documentation

When you change functionality, update these files:
- `README.md` - If changing features or usage
- `QUICKSTART.md` - If changing setup steps
- `PLAN.md` - If changing architecture
- `CHANGELOG.md` - Document the change

## Available Examples

### Browser Example

**Location**: `examples/browser/`

Tests LLM ability to use web browsing tools for navigation and information extraction.

**What it evaluates:**
- Tool usage (web_browser)
- Website navigation  
- Information extraction
- Question answering from web content

**Running:**
```bash
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini
```

**Documentation**: See `examples/browser/README.md`

### Custom Scorer Example (RAGChecker)

**Location**: `examples/custom_scorer/`

Demonstrates how to create custom scorers using RAGChecker for fine-grained evaluation with precision, recall, and F1 metrics.

**What it evaluates:**
- Response accuracy (precision)
- Response completeness (recall)
- Balanced quality (F1 score)
- Fine-grained claim-level analysis

**Running:**
```bash
# Install dependencies first
pip install ragchecker litellm
python -m spacy download en_core_web_sm

# Run evaluation
inspect eval examples/custom_scorer/custom_scorer.py --model openai/gpt-4o-mini
```

**Documentation**: See `examples/custom_scorer/README.md` and `examples/custom_scorer/QUICKSTART.md`

### Future Examples

Planned examples (contributions welcome):
- Coding evaluation
- Multi-agent collaboration
- Reasoning chains
- Safety testing
- Multimodal tasks
- Long-context understanding

## Best Practices

### ✅ Do

- **Organize by example**: Each example in its own subfolder (`browser/`, `coding/`, etc.)
- **Document thoroughly**: Include README.md with each example
- **Use clear naming**: Task names should describe what they evaluate
- **Include samples**: Provide diverse test cases in your dataset
- **Set appropriate limits**: Configure timeouts and token limits
- **Test multiple models**: Verify tasks work across providers
- **Follow structure**: Use the example template above
- **Update docs**: Add new examples to this README
- **Use the setup script**: For initial configuration
- **Commit project files**: `pyproject.toml` and `.python-version` to version control
- **Use uv for development**: `uv pip install -e ".[provider]"`

### ❌ Don't

- **Mix unrelated tasks**: Keep examples focused on specific capabilities
- **Skip documentation**: Always include README.md in example folders
- **Put files in root**: Keep all evaluation code in `examples/`
- **Hardcode paths**: Make examples portable
- **Commit secrets**: Never commit API keys to version control
- **Commit `.venv/`**: Add to `.gitignore`
- **Commit `uv.lock`**: Unless you want exact versions for collaboration
- **Edit `uv.lock` manually**: Let uv manage it
- **Mix pip and uv**: Choose one package manager per environment
- **Forget dependencies**: Document any special requirements

## Dependencies

### Required
- **Python** >= 3.10 (3.11 recommended)
- **Docker** - For sandboxing
- **inspect-ai** >= 0.3.0 - Core framework

### Optional (by provider)
- **openai** >= 1.0.0 - For OpenAI models
- **anthropic** >= 0.18.0 - For Anthropic Claude
- **mistralai** >= 1.0.0 - For Mistral models
- **ai21** >= 2.0.0 - For AI21 Jamba
- **google-genai** >= 0.2.0 - For Google Gemini

## Environment Variables

| Variable | Required For | Format |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI models | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic models | `sk-ant-...` |
| `MISTRAL_API_KEY` | Mistral models | String |
| `AI21_API_KEY` | AI21 models | String |
| `GOOGLE_API_KEY` | Google models | String |

## Troubleshooting

### Docker Issues

If you get Docker-related errors:

```bash
# Check if Docker is running
docker ps

# If not, start Docker Desktop (macOS/Windows)
# Or start Docker daemon (Linux)
sudo systemctl start docker
```

### API Key Issues

If you get authentication errors:

```bash
# Verify your API key is set
echo $OPENAI_API_KEY  # or other provider

# Re-export if needed
export OPENAI_API_KEY=your-key-here
```

### Model Not Found

Make sure you've installed the provider package:

```bash
uv pip install openai  # or anthropic, mistralai, etc.
# Or use the project extras: uv pip install -e ".[openai]"
```

### uv Command Not Found

If `uv` is not recognized after installation:

```bash
# Restart your terminal or source your profile
source ~/.zshrc  # or ~/.bashrc

# Or reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Module Not Found Errors

If you get import errors:

```bash
# Reinstall the package with dependencies
uv pip install -e ".[openai]"

# Verify installation
uv pip list | grep inspect-ai
```

### Permission Errors

If you get permission errors with uv:

```bash
# Don't use sudo with uv
uv pip install -e ".[openai]"
```

### Package Conflicts

If you encounter dependency conflicts:

```bash
# Try reinstalling in a fresh environment
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ".[all-providers]"
```

## Frequently Asked Questions

### Q: Do I need to use uv?
**A:** Recommended but not required. You can still use pip, but uv is much faster and better for modern Python projects.

### Q: Can I mix pip and uv?
**A:** Technically yes, but not recommended. Choose one and stick with it in a given environment.

### Q: What if I already have the project set up with pip?
**A:** No need to change anything. But if you want to migrate, just install uv and reinstall dependencies with `uv pip install -e ".[all-providers]"`

### Q: Does this change how I run evaluations?
**A:** No! All `inspect eval` commands remain exactly the same.

### Q: What about virtual environments?
**A:** uv works great with venvs. Use `uv venv` to create one, or use your existing venv with `uv pip`.

### Q: Is uv as reliable as pip?
**A:** Yes! uv is built by the creators of Ruff and is production-ready. It's used by many large projects.

### Q: What if I have issues with uv?
**A:** You can always fall back to pip. The `pyproject.toml` works with both pip and uv.

## Testing Your Examples

Before considering an example complete:

1. ✅ **Run with multiple models**: Test OpenAI, Anthropic, etc.
2. ✅ **Verify scores**: Ensure scoring works as expected
3. ✅ **Check logs**: Review output in inspect view
4. ✅ **Test edge cases**: Try with limited samples, timeouts
5. ✅ **Document limitations**: Note any known issues in README

## Next Steps

1. **Try the browser example**: Run your first evaluation
2. **Create your own example**: Follow the structure guide above
3. **Modify existing tasks**: Edit dataset samples to test different scenarios
4. **Experiment with solvers**: Try different solver chains (e.g., add chain_of_thought)
5. **Custom scoring**: Implement more sophisticated scorers for detailed evaluation
6. **Add metadata**: Track additional metrics in your evaluations

## Quick Reference

```bash
# Installation
curl -LsSf https://astral.sh/uv/install.sh | sh

# Project setup
cd inspect-examples
uv pip install -e ".[openai]"
export OPENAI_API_KEY=your-key

# Run evaluation
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini

# View results
inspect view

# List available tasks
inspect list examples/browser/browser.py

# Check evaluation history
inspect history

# Common uv commands
uv pip list              # List installed packages
uv pip tree              # Show dependency tree
uv pip freeze            # Freeze current environment
uv venv                  # Create virtual environment
```

## Resources

### Inspect AI
- [Inspect AI Documentation](https://inspect.aisi.org.uk/)
- [Inspect AI GitHub](https://github.com/UKGovernmentBEIS/inspect_ai)
- [Task Creation Guide](https://inspect.aisi.org.uk/tasks.html)
- [Tool Development](https://inspect.aisi.org.uk/tools-custom.html)
- [Scoring Methods](https://inspect.aisi.org.uk/scorers.html)
- [Browser Tools Guide](https://inspect.aisi.org.uk/tools-standard.html)
- [Model Providers](https://inspect.aisi.org.uk/providers.html)

### Tools & Infrastructure
- [uv Package Manager](https://github.com/astral-sh/uv)
- [Docker Documentation](https://docs.docker.com/)

### Getting Help
- Review existing examples in `examples/` for patterns
- Check this README for project structure
- Read Inspect AI documentation
- Open issues on GitHub for questions

