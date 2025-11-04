# Quick Start Guide: Running the Browser Task

Follow these steps to quickly run your first browser task evaluation.

## Step 1: Install uv Package Manager

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv

# Or with pip (if you have pip)
pip install uv
```

## Step 2: Install Inspect AI and Model Provider

Navigate to the project directory and install dependencies:

```bash
cd inspect-examples

# Option A: OpenAI (Recommended for first try)
uv pip install -e ".[openai]"
export OPENAI_API_KEY=your-openai-api-key

# Option B: Anthropic
uv pip install -e ".[anthropic]"
export ANTHROPIC_API_KEY=your-anthropic-api-key

# Option C: Mistral
uv pip install -e ".[mistral]"
export MISTRAL_API_KEY=your-mistral-api-key

# Option D: Install all providers at once
uv pip install -e ".[all-providers]"
```

## Step 3: Ensure Docker is Running

```bash
# Check Docker status
docker ps

# If Docker is not running, start Docker Desktop (or Docker daemon on Linux)
```

## Step 4: Run Your First Evaluation

```bash
# Run with OpenAI GPT-4o-mini
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini

# Or with Anthropic Claude Haiku
inspect eval examples/browser/browser.py --model anthropic/claude-haiku-4-5

# Or with Mistral Small
inspect eval examples/browser/browser.py --model mistral/mistral-small-latest
```

## Step 5: View the Results

```bash
# Open the web-based log viewer
inspect view
```

This will open a browser window showing your evaluation results!

## Verify Installation

To verify everything is set up correctly:

```bash
# 1. Check browser example exists
ls examples/browser/

# 2. List available tasks
inspect list examples/browser/browser.py

# 3. Verify Docker is running
docker ps

# 4. Check API key is set
echo $OPENAI_API_KEY  # or other provider
```

## Step 6: Compare Multiple Models

```bash
# Run with multiple models
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini
inspect eval examples/browser/browser.py --model anthropic/claude-haiku-4-5
inspect eval examples/browser/browser.py --model mistral/mistral-small-latest

# Then view all results in the log viewer
inspect view
```

## Common Issues

**"Docker not found"**: Make sure Docker is installed and running  
**"API key not found"**: Check that you've exported your API key correctly  
**"Module not found"**: Install the model provider with `uv pip install -e ".[openai]"`  
**"uv not found"**: Install uv first with the install script or Homebrew

## Support

- Documentation: https://inspect.aisi.org.uk/
- GitHub Issues: https://github.com/UKGovernmentBEIS/inspect_ai/issues

