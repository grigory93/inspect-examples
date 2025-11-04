# Important Gotchas & Fixes for Inspect Browser Examples

This document catalogs all the critical issues, fixes, and gotchas discovered while setting up the Inspect AI browser tool evaluation examples.

## 1. Docker Image - CRITICAL FIX

**Problem:** The old Docker image `aisiuk/inspect-web-browser-tool` is deprecated and will not work.

**Solution:** Use `aisiuk/inspect-tool-support` (unified tool support image)

```yaml
# ❌ WRONG - Old image
services:
  default:
    image: aisiuk/inspect-web-browser-tool

# ✅ CORRECT - New image
services:
  default:
    image: aisiuk/inspect-tool-support
    init: true
    command: tail -f /dev/null
    cpus: 1.0
    mem_limit: 0.5gb
```

**Why it matters:** The old image doesn't include all necessary browser tool dependencies and is no longer maintained.

---

## 2. Compose.yaml Location - CRITICAL

**Problem:** The `compose.yaml` file must be in the correct location relative to your task file.

**Solution:** Place `compose.yaml` in the same directory as your task Python file.

```
✅ CORRECT structure:
examples/
  ├── browser.py
  └── compose.yaml

❌ WRONG structure:
examples/
  └── browser.py
compose.yaml  # At root level
```

**In your task code:**
```python
@task
def browser():
    return Task(
        # Must reference compose.yaml correctly
        sandbox=("docker", "compose.yaml")  # ✅ Correct
        # sandbox="docker"  # ❌ Won't work properly
    )
```

---

## 3. Python Package Structure - REQUIRED

**Problem:** Task files in the root directory won't import correctly and don't follow Python best practices.

**Solution:** Move all evaluation tasks into a proper Python package directory.

```bash
# ❌ WRONG - Old structure
browser.py  # At root level
inspect eval browser.py

# ✅ CORRECT - Package structure
examples/
  ├── __init__.py
  └── browser.py
inspect eval examples/browser.py
```

**Why it matters:** 
- Proper imports and module resolution
- Follows Python packaging standards
- Makes compose.yaml paths work correctly
- Enables project scalability

---

## 4. Docker Configuration Details

**Problem:** Missing or incorrect Docker compose configuration causes silent failures or timeouts.

**Solution:** Use these specific settings:

```yaml
services:
  default:
    image: aisiuk/inspect-tool-support
    init: true              # ✅ REQUIRED - proper process management
    command: tail -f /dev/null  # ✅ REQUIRED - keeps container alive
    cpus: 1.0              # ✅ Prevents resource exhaustion
    mem_limit: 0.5gb       # ✅ Prevents memory issues
```

**Critical flags:**
- `init: true` - Ensures proper signal handling and process cleanup
- `command: tail -f /dev/null` - Keeps the container running for tool execution
- Resource limits prevent runaway processes

---

## 5. Docker Must Be Running - NON-NEGOTIABLE

**Problem:** Evaluations will fail immediately if Docker is not running.

**Solution:** Always verify Docker is running before starting evaluations:

```bash
# Check Docker status
docker ps

# If it fails, start Docker:
# - macOS/Windows: Open Docker Desktop
# - Linux: sudo systemctl start docker
```

**Error symptoms without Docker:**
- `Cannot connect to the Docker daemon`
- `docker.errors.DockerException`
- Sandbox initialization failures

---

## 6. Task Limits Configuration - PREVENTS TIMEOUTS

**Problem:** Without proper limits, browser tasks can hang indefinitely or consume excessive resources.

**Solution:** Always set these three limits in your task:

```python
@task
def browser():
    return Task(
        dataset=EVAL_SAMPLES,
        solver=[...],
        message_limit=10,          # ✅ Max messages in conversation
        working_limit=3 * 60,      # ✅ Max time in seconds (3 minutes)
        token_limit=(1024*500),    # ✅ Max tokens (512K)
        sandbox=("docker", "compose.yaml")
    )
```

**Why each matters:**
- `message_limit`: Prevents infinite loops in tool usage
- `working_limit`: Timeout for slow/stuck browsers
- `token_limit`: Prevents context overflow with large web pages

---

## 7. API Keys Must Be Exported - NOT JUST SET

**Problem:** Setting API keys in a file or local variable won't work.

**Solution:** Export them as environment variables:

```bash
# ❌ WRONG - Won't work
OPENAI_API_KEY=sk-...

# ✅ CORRECT - Must export
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export MISTRAL_API_KEY=...

# Verify they're set
echo $OPENAI_API_KEY
```

**Common mistake:** Setting in `.env` file without loading it. Inspect AI reads from environment variables, not .env files by default.

---

## 8. Package Manager - Use uv for Reliability

**Problem:** pip can have slow installation and dependency resolution issues.

**Solution:** Use uv package manager for 10-100x faster installations:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Use uv instead of pip
uv pip install -e ".[openai]"        # ✅ Much faster
pip install -e ".[openai]"           # ❌ Slower, more conflicts

# Don't mix them
uv pip install ...  # ✅ Stick to one
pip install ...     # ❌ Don't switch between them
```

---

## 9. Optional Dependencies Structure

**Problem:** Installing all providers when you only need one wastes time and space.

**Solution:** Use optional dependency groups in `pyproject.toml`:

```toml
[project.optional-dependencies]
openai = ["openai>=1.0.0"]
anthropic = ["anthropic>=0.18.0"]
all-providers = ["openai>=1.0.0", "anthropic>=0.18.0", ...]
```

```bash
# Install only what you need
uv pip install -e ".[openai]"              # ✅ Just OpenAI
uv pip install -e ".[openai,anthropic]"    # ✅ Two providers
uv pip install -e ".[all-providers]"       # ✅ Everything
```

---

## 10. Scorer Configuration

**Problem:** Basic scorers like `includes()` may not work well for complex browser tasks.

**Solution:** Use model-graded scoring for better evaluation:

```python
from inspect_ai.scorer import includes, model_graded_qa

# ❌ Too simplistic for complex outputs
scorer=includes()

# ✅ Better for nuanced evaluation
scorer=model_graded_qa(model="openai/gpt-4o-mini")
```

---

## 11. Command Path Changes After Restructure

**Problem:** Old documentation shows incorrect command paths.

**Solution:** Always use the package path:

```bash
# ❌ OLD - Won't work anymore
inspect eval browser.py --model openai/gpt-4o-mini
inspect list browser.py

# ✅ NEW - Correct package path
inspect eval examples/browser.py --model openai/gpt-4o-mini
inspect list examples/browser.py
```

---

## 12. Python Version Requirements

**Problem:** Older Python versions may have compatibility issues.

**Solution:** Use Python 3.11 (minimum 3.10):

```bash
# Check your version
python --version

# Should be 3.10+ (3.11 recommended)
# If not, install/upgrade Python first
```

Create `.python-version` file:
```
3.11
```

---

## 13. Internet Connectivity in Docker

**Problem:** Docker container must access external websites for browser tool.

**Solution:** Ensure Docker has network access (usually automatic, but can be blocked by firewalls/proxies):

```bash
# Test Docker network connectivity
docker run --rm alpine ping -c 2 google.com

# If it fails, check:
# - Firewall settings
# - Corporate proxy configuration
# - Docker network settings
```

---

## 14. Browser Tool Timeout Defaults

**Problem:** Default timeouts may be too short for slow websites or complex tasks.

**Solution:** Customize browser tool timeout:

```python
# Default timeout might be too short
use_tools(web_browser())

# Increase if needed
use_tools(web_browser(timeout=180))  # 3 minutes
use_tools(web_browser(timeout=300))  # 5 minutes
```

---

## 15. File Organization After Migration

**Problem:** After project restructure, old file references break.

**Solution:** Updated structure and references:

```
✅ Current Structure:
inspect-examples/
├── examples/        # All Python task files here
│   ├── __init__.py
│   ├── browser.py
│   └── compose.yaml
├── logs/                   # Auto-generated evaluation logs
├── pyproject.toml          # Dependencies configuration
├── README.md              # Documentation
└── *.sh                   # Helper scripts
```

**All commands updated:**
- All `inspect eval` commands use `examples/` prefix
- All imports reference the package properly
- Documentation consistently uses new paths

---

## 16. Sandbox Tuple Format

**Problem:** Sandbox parameter format is specific and easy to get wrong.

**Solution:** Use tuple format with both Docker and compose file:

```python
# ❌ WRONG - Missing compose file reference
sandbox="docker"

# ❌ WRONG - Wrong type
sandbox=["docker", "compose.yaml"]

# ✅ CORRECT - Tuple with both parameters
sandbox=("docker", "compose.yaml")
```

---

## Quick Troubleshooting Checklist

When browser tasks fail, check these in order:

1. ☐ Docker is running: `docker ps`
2. ☐ API key is exported: `echo $OPENAI_API_KEY`
3. ☐ Using correct Docker image: `aisiuk/inspect-tool-support`
4. ☐ compose.yaml in correct location (with task file)
5. ☐ Task file in package directory (`examples/`)
6. ☐ Using correct command path: `inspect eval examples/browser.py`
7. ☐ Task has all three limits: message_limit, working_limit, token_limit
8. ☐ Sandbox uses tuple format: `sandbox=("docker", "compose.yaml")`
9. ☐ Dependencies installed: `uv pip install -e ".[openai]"`
10. ☐ Python version >= 3.10: `python --version`

---

## Summary of Critical Changes from Initial Setup

| Component | Old/Wrong | New/Correct |
|-----------|-----------|-------------|
| Docker Image | `aisiuk/inspect-web-browser-tool` | `aisiuk/inspect-tool-support` |
| File Location | `browser.py` (root) | `examples/browser.py` |
| Command | `inspect eval browser.py` | `inspect eval examples/browser.py` |
| Sandbox Config | `sandbox="docker"` | `sandbox=("docker", "compose.yaml")` |
| compose.yaml | At project root | In `examples/` with task |
| Package Manager | pip (slow) | uv (fast, recommended) |
| Dependencies | All at once | Optional groups by provider |

---

## When to Use This Document

- ✅ Setting up Inspect AI browser examples for the first time
- ✅ Troubleshooting failing evaluations
- ✅ Migrating from old project structure
- ✅ Contributing new browser tasks
- ✅ Debugging Docker/sandbox issues

This document is based on real issues encountered during project setup and should be updated as new gotchas are discovered.