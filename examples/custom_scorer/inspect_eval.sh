#!/bin/bash
# Wrapper for inspect eval CLI with macOS multiprocessing fixes
#
# Usage:
#   ./examples/custom_scorer/inspect_eval.sh [inspect eval arguments]
#
# Examples:
#   ./examples/custom_scorer/inspect_eval.sh examples.custom_scorer.custom_scorer:custom_scorer --model openai/gpt-4o-mini
#   ./examples/custom_scorer/inspect_eval.sh examples.custom_scorer.custom_scorer:custom_scorer --model openai/gpt-4o --limit 5

set -e

# Set macOS multiprocessing fixes
export PYTHONMULTIPROCESSING_START_METHOD=spawn
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export PYTHONUNBUFFERED=1

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "Running inspect eval with macOS fixes..."
echo ""

# Run inspect eval with piping to fix file descriptor issues
# The pipe is critical for avoiding the "bad value(s) in fds_to_keep" error
inspect eval "$@" 2>&1 | cat

echo ""
echo "✓ Evaluation complete"
