#!/bin/bash

# Browser Task Model Comparison Script
# This script runs the browser task across multiple LLM providers for comparison

echo "🚀 Starting Browser Task Model Comparison"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Define models to test
# Uncomment the models you have API keys for
MODELS=(
    "openai/gpt-4o"
    # "anthropic/claude-sonnet-4-0"
    # "mistral/mistral-large-latest"
    # "google/gemini-2.0-flash-exp"
    # "ai21/jamba-1.5-large"
)

# Check which task to run
TASK_FILE="${1:-examples/browser/browser.py}"
echo "📋 Using task file: $TASK_FILE"
echo ""

# Run evaluation for each model
for model in "${MODELS[@]}"; do
    echo "🔍 Testing model: $model"
    echo "----------------------------"
    
    # Run the evaluation
    inspect eval "$TASK_FILE" --model "$model"
    
    if [ $? -eq 0 ]; then
        echo "✅ Completed: $model"
    else
        echo "❌ Failed: $model"
    fi
    
    echo ""
done

echo "=========================================="
echo "✨ Comparison complete!"
echo ""
echo "To view results, run:"
echo "  inspect view"
echo ""
echo "Logs are saved in: ./logs/"

