#!/usr/bin/env python3
"""Test script to verify RAGChecker setup.

This script checks if all required dependencies are installed and configured
correctly for running the RAGChecker custom scorer example.
"""

import sys
import os


def check_import(module_name: str, package_name: str = None) -> bool:
    """Check if a module can be imported."""
    package_name = package_name or module_name
    try:
        __import__(module_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        print(f"   Install with: pip install {package_name}")
        return False


def check_spacy_model() -> bool:
    """Check if spaCy English model is installed."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy English model (en_core_web_sm) is installed")
        return True
    except OSError:
        print("❌ spaCy English model (en_core_web_sm) is NOT installed")
        print("   If using uv:")
        print("   uv pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl")
        print("   If using pip:")
        print("   python -m spacy download en_core_web_sm")
        return False
    except ImportError:
        print("❌ spaCy is NOT installed")
        print("   Install with: pip install spacy (or: uv pip install spacy)")
        return False


def check_api_key(key_name: str) -> bool:
    """Check if an API key is set."""
    key_value = os.environ.get(key_name)
    if key_value:
        # Show only first 8 characters for security
        masked = key_value[:8] + "..." if len(key_value) > 8 else key_value
        print(f"✅ {key_name} is set ({masked})")
        return True
    else:
        print(f"❌ {key_name} is NOT set")
        print(f"   Set with: export {key_name}=your-key-here")
        return False


def check_ragchecker_version() -> bool:
    """Check RAGChecker version."""
    try:
        import ragchecker
        version = getattr(ragchecker, "__version__", "unknown")
        print(f"✅ RAGChecker version: {version}")
        return True
    except ImportError:
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("RAGChecker Custom Scorer - Setup Verification")
    print("=" * 60)
    print()
    
    all_passed = True
    
    print("Checking required packages...")
    print("-" * 60)
    
    # Check core packages
    all_passed &= check_import("inspect_ai", "inspect-ai")
    all_passed &= check_import("ragchecker")
    if check_import("ragchecker"):
        check_ragchecker_version()
    all_passed &= check_import("litellm")
    all_passed &= check_import("spacy")
    
    print()
    print("Checking spaCy model...")
    print("-" * 60)
    all_passed &= check_spacy_model()
    
    print()
    print("Checking API keys...")
    print("-" * 60)
    all_passed &= check_api_key("OPENAI_API_KEY")
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("✅ All checks passed! You're ready to run the example.")
        print()
        print("Run the evaluation with:")
        print("  inspect eval examples/custom_scorer/custom_scorer.py --model openai/gpt-4o-mini")
        print()
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print()
        print("Quick setup:")
        print("  # Install packages")
        print("  pip install ragchecker litellm  # or: uv pip install ragchecker litellm")
        print()
        print("  # Install spaCy model")
        print("  # If using uv:")
        print("  uv pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl")
        print("  # If using pip:")
        print("  python -m spacy download en_core_web_sm")
        print()
        print("  # Set API key")
        print("  export OPENAI_API_KEY=your-key-here")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())

