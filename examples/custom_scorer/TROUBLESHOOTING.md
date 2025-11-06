# Troubleshooting Guide: macOS Multiprocessing Issues

## Problem: "bad value(s) in fds_to_keep" Error

This error occurs on macOS when Python's multiprocessing module encounters file descriptor conflicts. RAGChecker uses multiprocessing internally, which triggers this issue.

### Root Cause

- **Default fork method on macOS**: Python's default `fork` multiprocessing method duplicates file descriptors
- **RAGChecker's parallelism**: The underlying `refchecker` library spawns processes for batch processing
- **File descriptor duplication**: When processes fork (not spawn), file descriptors get duplicated, causing validation errors

## Solutions

### Solution 1: Use the Bash Script (Easiest) ⭐

Run the provided shell script that sets the correct environment variables:

```bash
cd /Users/gkanevsky/inspect-examples
./examples/custom_scorer/run_evaluation.sh
```

This script automatically:
- Sets `PYTHONMULTIPROCESSING_START_METHOD=spawn`
- Sets `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`
- Runs your Python script

### Solution 2: Set Environment Variables Manually

Before running Python, export these variables:

```bash
export PYTHONMULTIPROCESSING_START_METHOD=spawn
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
python examples/custom_scorer/run_evaluation.py
```

**To make permanent**, add to your `~/.zshrc` (macOS default shell):

```bash
echo 'export PYTHONMULTIPROCESSING_START_METHOD=spawn' >> ~/.zshrc
echo 'export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES' >> ~/.zshrc
source ~/.zshrc
```

### Solution 3: Use the Updated Python Script

The updated `run_evaluation.py` includes built-in fixes:

```python
# These are already in the updated script
multiprocessing.set_start_method('spawn', force=True)
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
```

Just run:

```bash
python examples/custom_scorer/run_evaluation.py
```

### Solution 4: For Inspect CLI Usage

If using the `inspect eval` CLI command:

```bash
export PYTHONMULTIPROCESSING_START_METHOD=spawn
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
inspect eval examples.custom_scorer:custom_scorer --model openai/gpt-4o-mini
```

## Understanding the Fixes

### 1. `PYTHONMULTIPROCESSING_START_METHOD=spawn`

**What it does**: Changes how Python creates new processes

- **fork** (default on macOS): Copies the entire parent process, including file descriptors → causes duplicates
- **spawn** (recommended): Creates a fresh Python interpreter for each process → no duplicates

**Trade-offs**:
- ✅ Fixes file descriptor issues
- ✅ Safer and more isolated processes
- ⚠️ Slightly slower startup (minimal impact for RAGChecker)

### 2. `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`

**What it does**: Disables Apple's CoreFoundation fork safety checks

- macOS High Sierra+ has safety checks that prevent forking after certain frameworks initialize
- This can cause issues with multiprocessing in scientific computing libraries
- Disabling is generally safe for Python data processing workflows

**When needed**:
- You're on macOS 10.13+ (High Sierra or later)
- Using libraries that interact with macOS system frameworks
- Getting fork safety warnings or crashes

### 3. `multiprocessing.set_start_method('spawn', force=True)`

**What it does**: Programmatically sets the multiprocessing method in Python

- `force=True`: Overrides any previous setting
- Must be called before any multiprocessing code runs
- Same effect as the environment variable but in Python

## Verification

After applying fixes, test with a simple script:

```python
import multiprocessing
import os

print(f"Multiprocessing start method: {multiprocessing.get_start_method()}")
print(f"Fork safety disabled: {os.environ.get('OBJC_DISABLE_INITIALIZE_FORK_SAFETY', 'NO')}")

# Should print:
# Multiprocessing start method: spawn
# Fork safety disabled: YES
```

## Alternative: Reduce Parallelism

If you still have issues, reduce batch sizes in RAGChecker (reduces multiprocessing load):

```python
evaluator = RAGChecker(
    extractor_name="openai/gpt-4o-mini",
    checker_name="openai/gpt-4o-mini",
    batch_size_extractor=1,  # Already set
    batch_size_checker=1,     # Already set
)
```

Our scorer already uses `batch_size=1`, which minimizes multiprocessing.

## Still Having Issues?

### Check Python Version

```bash
python --version
```

**Recommended**: Python 3.9+ (better multiprocessing on macOS)

### Check for Other Multiprocessing Code

If you have other code that sets multiprocessing methods:

```bash
grep -r "set_start_method" .
```

Make sure nothing sets it to `'fork'`.

### Try Running in a Fresh Terminal

Sometimes environment variables get cached:

1. Close all terminal windows
2. Open a new terminal
3. Set environment variables again
4. Run your script

### Verbose Error Output

To get more details about the error:

```bash
python -v examples/custom_scorer/run_evaluation.py 2>&1 | tee error_log.txt
```

This saves all output (including errors) to `error_log.txt` for analysis.

## Additional Resources

- [Python multiprocessing docs](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods)
- [macOS fork safety issue](https://bugs.python.org/issue43142)
- [RAGChecker documentation](https://github.com/amazon-science/RAGChecker)

## Quick Reference

```bash
# Method 1: Bash script
./examples/custom_scorer/run_evaluation.sh

# Method 2: Environment variables
export PYTHONMULTIPROCESSING_START_METHOD=spawn
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
python examples/custom_scorer/run_evaluation.py

# Method 3: Inspect CLI
export PYTHONMULTIPROCESSING_START_METHOD=spawn
inspect eval examples.custom_scorer:custom_scorer --model openai/gpt-4o-mini

# Method 4: Add to shell profile (permanent)
echo 'export PYTHONMULTIPROCESSING_START_METHOD=spawn' >> ~/.zshrc
echo 'export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES' >> ~/.zshrc
source ~/.zshrc
```

