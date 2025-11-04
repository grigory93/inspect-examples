#!/bin/bash

# Example Commands for Running Browser Task Evaluation
# Copy and paste these commands to run your evaluation

# =============================================================================
# STEP 0: INSTALL UV PACKAGE MANAGER
# =============================================================================

# Install uv (if not already installed)
# curl -LsSf https://astral.sh/uv/install.sh | sh
# Or: brew install uv

# =============================================================================
# STEP 1: INSTALLATION
# =============================================================================

# Navigate to project directory
cd /Users/gkanevsky/inspect-examples

# Method 1: Install with specific provider(s)
uv pip install -e ".[openai]"      # For OpenAI models
# uv pip install -e ".[anthropic]"   # For Anthropic Claude
# uv pip install -e ".[mistral]"     # For Mistral
# uv pip install -e ".[ai21]"        # For AI21
# uv pip install -e ".[google]"      # For Google Gemini

# Method 2: Install multiple providers at once
# uv pip install -e ".[openai,anthropic,mistral]"

# Method 3: Install all providers
# uv pip install -e ".[all-providers]"

# =============================================================================
# STEP 2: SET API KEYS (Replace with your actual keys)
# =============================================================================

export OPENAI_API_KEY=sk-your-openai-api-key-here
# export ANTHROPIC_API_KEY=your-anthropic-key-here
# export MISTRAL_API_KEY=your-mistral-key-here
# export AI21_API_KEY=your-ai21-key-here
# export GOOGLE_API_KEY=your-google-key-here

# =============================================================================
# STEP 3: VERIFY DOCKER IS RUNNING
# =============================================================================

docker ps
# If this fails, start Docker Desktop (macOS/Windows) or Docker daemon (Linux)

# =============================================================================
# STEP 4: RUN SINGLE MODEL EVALUATION
# =============================================================================

# Test with OpenAI GPT-4o (recommended for first try)
inspect eval examples/browser/browser.py --model openai/gpt-4o

# Or test with other models:
# inspect eval examples/browser/browser.py --model anthropic/claude-sonnet-4-0
# inspect eval examples/browser/browser.py --model mistral/mistral-large-latest
# inspect eval examples/browser/browser.py --model google/gemini-2.0-flash-exp
# inspect eval examples/browser/browser.py --model ai21/jamba-1.5-large

# =============================================================================
# STEP 5: VIEW RESULTS
# =============================================================================

# Open the log viewer in your browser
inspect view

# =============================================================================
# STEP 6: COMPARE MULTIPLE MODELS
# =============================================================================

# Method 1: Run sequentially
inspect eval examples/browser/browser.py --model openai/gpt-4o
inspect eval examples/browser/browser.py --model anthropic/claude-sonnet-4-0
inspect eval examples/browser/browser.py --model mistral/mistral-large-latest

# Method 2: Run in batch (comma-separated)
inspect eval examples/browser/browser.py --model openai/gpt-4o,anthropic/claude-sonnet-4-0,mistral/mistral-large-latest

# Method 3: Use the provided script
./run_comparison.sh

# =============================================================================
# ADVANCED: ADDITIONAL OPTIONS
# =============================================================================

# Run with specific log file name
inspect eval examples/browser/browser.py --model openai/gpt-4o --log-dir ./my-logs

# Run with limited samples (if you add more to the dataset)
inspect eval examples/browser/browser.py --model openai/gpt-4o --limit 5

# View specific log file
inspect view ./logs/2024-01-01T12-00-00.json

# =============================================================================
# TROUBLESHOOTING COMMANDS
# =============================================================================

# Check if API key is set
echo $OPENAI_API_KEY

# Check installed packages
uv pip list | grep -E "(inspect-ai|openai|anthropic|mistral)"
# Or: uv pip freeze

# Check Docker status
docker info

# Check Inspect AI version
inspect --version

# List all available tasks in a file
inspect list examples/browser/browser.py

# =============================================================================
# CLEANUP
# =============================================================================

# Remove old log files (optional)
# rm -rf ./logs/*

# Unset API keys (for security)
# unset OPENAI_API_KEY
# unset ANTHROPIC_API_KEY

