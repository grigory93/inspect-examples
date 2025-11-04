#!/bin/bash

# Setup script for Inspect Examples using uv package manager
# This script automates the entire setup process

set -e  # Exit on error

echo "🚀 Setting up Inspect Examples with uv"
echo "========================================"
echo ""

# =============================================================================
# STEP 1: Check if uv is installed
# =============================================================================

if ! command -v uv &> /dev/null; then
    echo "📦 uv not found. Installing uv..."
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "  Using Homebrew..."
            brew install uv
        else
            echo "  Using install script..."
            curl -LsSf https://astral.sh/uv/install.sh | sh
        fi
    else
        # Linux
        echo "  Using install script..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
    
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
    uv --version
fi

echo ""

# =============================================================================
# STEP 2: Determine which providers to install
# =============================================================================

echo "📋 Select model providers to install:"
echo "1) OpenAI (recommended)"
echo "2) Anthropic"
echo "3) Mistral"
echo "4) AI21"
echo "5) Google"
echo "6) All providers"
echo "7) Only inspect-ai (no providers yet)"
echo ""
read -p "Enter your choice (1-7, or comma-separated like 1,2,3): " provider_choice

# Parse the choice
providers=""

if [[ "$provider_choice" == *"6"* ]]; then
    providers="all-providers"
else
    [[ "$provider_choice" == *"1"* ]] && providers="${providers},openai"
    [[ "$provider_choice" == *"2"* ]] && providers="${providers},anthropic"
    [[ "$provider_choice" == *"3"* ]] && providers="${providers},mistral"
    [[ "$provider_choice" == *"4"* ]] && providers="${providers},ai21"
    [[ "$provider_choice" == *"5"* ]] && providers="${providers},google"
    providers=${providers#,}  # Remove leading comma
fi

# =============================================================================
# STEP 3: Install dependencies
# =============================================================================

echo ""
echo "📦 Installing inspect-ai and dependencies..."

if [ -z "$providers" ]; then
    # No providers selected, install base only
    uv pip install -e .
else
    # Install with selected providers
    uv pip install -e ".[$providers]"
fi

echo "✅ Installation complete"
echo ""

# =============================================================================
# STEP 4: Set up API keys
# =============================================================================

echo "🔑 API Key Setup"
echo "================"
echo ""
echo "You'll need to set environment variables for your chosen providers."
echo "You can either:"
echo "  1. Export them in your shell: export OPENAI_API_KEY=sk-..."
echo "  2. Add them to your ~/.bashrc or ~/.zshrc"
echo "  3. Create a .env file (not included in this example)"
echo ""

if [[ "$provider_choice" == *"1"* ]] || [[ "$provider_choice" == *"6"* ]]; then
    echo "For OpenAI:"
    echo "  export OPENAI_API_KEY=your-openai-api-key-here"
fi

if [[ "$provider_choice" == *"2"* ]] || [[ "$provider_choice" == *"6"* ]]; then
    echo "For Anthropic:"
    echo "  export ANTHROPIC_API_KEY=your-anthropic-api-key-here"
fi

if [[ "$provider_choice" == *"3"* ]] || [[ "$provider_choice" == *"6"* ]]; then
    echo "For Mistral:"
    echo "  export MISTRAL_API_KEY=your-mistral-api-key-here"
fi

if [[ "$provider_choice" == *"4"* ]] || [[ "$provider_choice" == *"6"* ]]; then
    echo "For AI21:"
    echo "  export AI21_API_KEY=your-ai21-api-key-here"
fi

if [[ "$provider_choice" == *"5"* ]] || [[ "$provider_choice" == *"6"* ]]; then
    echo "For Google:"
    echo "  export GOOGLE_API_KEY=your-google-api-key-here"
fi

echo ""

# =============================================================================
# STEP 5: Check Docker
# =============================================================================

echo "🐳 Checking Docker..."

if docker ps &> /dev/null; then
    echo "✅ Docker is running"
else
    echo "⚠️  Docker is not running or not installed"
    echo "   The browser task requires Docker for sandboxing."
    echo "   Please install Docker Desktop and start it:"
    echo "   https://docs.docker.com/get-docker/"
fi

echo ""

# =============================================================================
# STEP 6: Summary
# =============================================================================

echo "=========================================="
echo "✨ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Set your API key(s) as shown above"
echo "  2. Ensure Docker is running"
echo "  3. Run your first evaluation:"
echo "     inspect eval examples/browser/browser.py --model openai/gpt-4o"
echo "  4. View results:"
echo "     inspect view"
echo ""
echo "📖 For more info, see:"
echo "  - QUICKSTART.md for step-by-step guide"
echo "  - README.md for complete documentation"
echo "  - PLAN.md for implementation details"
echo ""

