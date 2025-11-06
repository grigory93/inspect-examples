#!/bin/bash
# Safe wrapper that pipes output to work around macOS file descriptor bug
# This mimics what happens when you run with "| tee" which makes it work

set -e

# Ensure we're in the right directory
cd "$(dirname "$0")/../.." || exit 1

echo "Running evaluation with file descriptor fix..."
echo ""

# Set environment variables
export PYTHONMULTIPROCESSING_START_METHOD=spawn
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export PYTHONUNBUFFERED=1

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

echo "Environment variables set:"
echo "  PYTHONMULTIPROCESSING_START_METHOD=$PYTHONMULTIPROCESSING_START_METHOD"
echo "  OBJC_DISABLE_INITIALIZE_FORK_SAFETY=$OBJC_DISABLE_INITIALIZE_FORK_SAFETY"
echo ""

# Run with pipe to work around the file descriptor issue
# This is equivalent to running manually with "| tee output.txt"
# The pipe changes how file descriptors are handled, avoiding the bug
python -u examples/custom_scorer/run_evaluation.py "$@" 2>&1 | cat

echo ""
echo "Evaluation complete!"
