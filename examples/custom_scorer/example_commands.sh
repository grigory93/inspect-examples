#!/bin/bash
# Example commands for running the custom scorer evaluation

# This script contains example commands for running the RAGChecker-based
# custom scorer evaluation. These are not meant to be executed as a script,
# but rather as a reference for copy-pasting individual commands.
#
# NOTE: All inspect eval commands use the inspect_eval.sh wrapper script
# to handle macOS multiprocessing issues. If you're not on macOS, you can
# run inspect eval commands directly without the wrapper.

#######################
# Setup and Installation
#######################

# Install required dependencies
pip install ragchecker
pip install litellm

# Install spaCy model
# If using pip:
python -m spacy download en_core_web_sm

# If using uv (recommended to avoid "No module named pip" error):
uv pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Or install via project extras
uv pip install -e ".[ragchecker,openai]"

# Set OpenAI API key
export OPENAI_API_KEY=your-openai-api-key-here

#######################
# Basic Evaluation
#######################

# Run with OpenAI GPT-4o-mini (recommended for cost-effectiveness)
# Using wrapper script (handles macOS multiprocessing issues)
./examples/custom_scorer/inspect_eval.sh \
    examples.custom_scorer.custom_scorer:custom_scorer \
    --model openai/gpt-4o-mini

#######################
# Programmatic Evaluation (Python)
#######################

# Run evaluation from Python code (automatically handles macOS issues)
python examples/custom_scorer/run_evaluation.py

#######################
# Alternative: Direct inspect eval (Linux/Windows)
#######################

# If you're NOT on macOS, you can run inspect eval directly:
# inspect eval examples.custom_scorer.custom_scorer:custom_scorer --model openai/gpt-4o-mini
#
# On macOS, you MUST use one of these methods:
# 1. Use the wrapper script (recommended): ./examples/custom_scorer/inspect_eval.sh
# 2. Use Python script: python examples/custom_scorer/run_evaluation.py
# 3. Pipe the output: inspect eval ... 2>&1 | cat


#######################
# View Results
#######################

# Open the web viewer to see results
inspect view

# View specific log file
inspect view logs/2024-11-03T12-00-00_custom_scorer.json

# Check evaluation history
inspect history

#######################
# Compare Multiple Models
#######################

# Run evaluations with different models
./examples/custom_scorer/inspect_eval.sh \
    examples.custom_scorer.custom_scorer:custom_scorer \
    --model openai/gpt-4o-mini

./examples/custom_scorer/inspect_eval.sh \
    examples.custom_scorer.custom_scorer:custom_scorer \
    --model openai/gpt-4o

./examples/custom_scorer/inspect_eval.sh \
    examples.custom_scorer.custom_scorer:custom_scorer \
    --model anthropic/claude-3-5-sonnet-20241022

# Then view all results together
inspect view

#######################
# Batch Evaluation
#######################

# Run multiple models in one command (comma-separated)
./examples/custom_scorer/inspect_eval.sh \
    examples.custom_scorer.custom_scorer:custom_scorer \
    --model openai/gpt-4o-mini,openai/gpt-4o,anthropic/claude-3-5-sonnet-20241022

#######################
# List Available Tasks
#######################

# List tasks in the custom scorer example
inspect list examples.custom_scorer.custom_scorer

#######################
# Advanced Options
#######################

# Run with custom log directory
./examples/custom_scorer/inspect_eval.sh \
    examples.custom_scorer.custom_scorer:custom_scorer \
    --model openai/gpt-4o-mini \
    --log-dir ./my-logs

# Run with specific log level
./examples/custom_scorer/inspect_eval.sh \
    examples.custom_scorer.custom_scorer:custom_scorer \
    --model openai/gpt-4o-mini \
    --log-level debug

# Run with custom maximum connections
./examples/custom_scorer/inspect_eval.sh \
    examples.custom_scorer.custom_scorer:custom_scorer \
    --model openai/gpt-4o-mini \
    --max-connections 10

#######################
# Troubleshooting
#######################

# Check if RAGChecker is installed
python -c "import ragchecker; print(ragchecker.__version__)"

# Check if spaCy model is installed
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('SpaCy model loaded successfully')"

# If you get "No module named pip" error when downloading spaCy model:
# Use uv to install it directly:
uv pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Check if API key is set
echo $OPENAI_API_KEY

# Test with a single sample (for debugging)
# Edit custom_scorer.py to use only the first sample:
# EVAL_SAMPLES = EVAL_SAMPLES[:1]

#######################
# Development Workflow
#######################

# 1. Install dependencies
uv pip install -e ".[ragchecker,openai]"
python -m spacy download en_core_web_sm

# 2. Set API key
export OPENAI_API_KEY=your-key

# 3. Run evaluation
./examples/custom_scorer/inspect_eval.sh \
    examples.custom_scorer.custom_scorer:custom_scorer \
    --model openai/gpt-4o-mini

# 4. View results
inspect view

# 5. Iterate on scorer implementation and re-run

#######################
# Using with Other Providers
#######################

# Note: RAGChecker requires OpenAI-compatible models
# To use other providers with RAGChecker, they must be accessible via LiteLLM
# and support the required functionality (claim extraction and checking)

# For example, using Anthropic via LiteLLM proxy:
# (Requires setting up LiteLLM proxy separately)

