#!/usr/bin/env python3
"""Run the custom scorer evaluation programmatically.

Example usage:
    python examples/custom_scorer/run_evaluation.py
"""

import os
import sys

# Set environment variables ONCE, early, before any other imports
if sys.platform == 'darwin':
    os.environ['PYTHONMULTIPROCESSING_START_METHOD'] = 'spawn'
    os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
    os.environ['PYTHONUNBUFFERED'] = '1'

# macOS TTY file descriptor workaround: re-exec with piping
if sys.platform == 'darwin' and sys.stdout.isatty() and not os.environ.get('_REEXECED'):
    import subprocess
    
    env = os.environ.copy()
    env['_REEXECED'] = '1'
    
    # Re-execute through a pipe to fix file descriptor issues
    proc = subprocess.Popen(
        [sys.executable, '-u'] + sys.argv,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    for line in proc.stdout:
        print(line, end='', flush=True)
    
    proc.wait()
    sys.exit(proc.returncode)

# Import multiprocessing after environment is configured
import multiprocessing

# Set multiprocessing method (should already be set via env var)
multiprocessing.set_start_method('spawn', force=True)
print(f"✓ Multiprocessing: {multiprocessing.get_start_method()}")


def main():
    """Run the custom scorer evaluation."""
    from inspect_ai import eval
    from examples.custom_scorer import custom_scorer
    
    logs = eval(
        custom_scorer(),
        model="openai/gpt-4o-mini",
        limit=4,
    )
    log = logs[0]
    print(f"\n{'='*70}")
    print(f"Evaluation complete!")
    print(f"Log: {log.location}")
    print(f"{'='*70}\n")
    return log


if __name__ == "__main__":
    main()

