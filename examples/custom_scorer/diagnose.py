#!/usr/bin/env python3
"""Diagnostic script to check multiprocessing setup."""

import os
import sys
import multiprocessing

print("=" * 70)
print("MULTIPROCESSING DIAGNOSTIC")
print("=" * 70)
print()

# Check platform
print(f"Platform: {sys.platform}")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

# Check multiprocessing method
try:
    current_method = multiprocessing.get_start_method()
    print(f"Current multiprocessing method: {current_method}")
    if current_method == "fork":
        print("  ⚠️  WARNING: Using 'fork' method - this causes issues on macOS!")
        print("     Solution: Set to 'spawn' instead")
    else:
        print("  ✓ Good: Using safe multiprocessing method")
except Exception as e:
    print(f"  ✗ Error getting multiprocessing method: {e}")

print()

# Check environment variables
print("Environment Variables:")
fork_safety = os.environ.get('OBJC_DISABLE_INITIALIZE_FORK_SAFETY', 'NOT SET')
print(f"  OBJC_DISABLE_INITIALIZE_FORK_SAFETY: {fork_safety}")
if fork_safety == "YES":
    print("    ✓ Fork safety disabled")
else:
    print("    ⚠️  Not set - may cause issues on macOS")

mp_method = os.environ.get('PYTHONMULTIPROCESSING_START_METHOD', 'NOT SET')
print(f"  PYTHONMULTIPROCESSING_START_METHOD: {mp_method}")
if mp_method == "spawn":
    print("    ✓ Set to spawn")
else:
    print("    ⚠️  Not set to spawn")

print()

# Try to set method
print("Attempting to set multiprocessing method to 'spawn'...")
try:
    multiprocessing.set_start_method('spawn', force=True)
    print(f"  ✓ Success! Method is now: {multiprocessing.get_start_method()}")
except Exception as e:
    print(f"  ✗ Failed: {e}")

print()
print("=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)
print()

# Provide recommendations
if sys.platform == 'darwin':
    print("For macOS, run one of these commands BEFORE running your script:")
    print()
    print("Option 1 - Set environment variables in terminal:")
    print("  export PYTHONMULTIPROCESSING_START_METHOD=spawn")
    print("  export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES")
    print("  python examples/custom_scorer/run_evaluation.py")
    print()
    print("Option 2 - Use the provided bash script:")
    print("  ./examples/custom_scorer/run_evaluation.sh")
    print()
    print("Option 3 - Add to your ~/.zshrc (permanent fix):")
    print("  echo 'export PYTHONMULTIPROCESSING_START_METHOD=spawn' >> ~/.zshrc")
    print("  echo 'export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES' >> ~/.zshrc")
    print("  source ~/.zshrc")
else:
    print("Your platform doesn't require these fixes.")

print()

