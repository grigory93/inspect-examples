# Plan: Browser Task Evaluation with Inspect AI

## Overview

This plan outlines how to use the Inspect AI framework to evaluate and compare multiple LLMs on an **agentic web browsing task**. The task tests whether models can effectively use tools (specifically web browsing) to navigate websites, extract information, and synthesize responses.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Inspect AI Framework                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐     ┌──────────────┐                  │
│  │   Dataset    │────▶│   Solver     │                  │
│  │  (Samples)   │     │  Chain       │                  │
│  └──────────────┘     └──────────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                   │
│                    │  use_tools()    │                   │
│                    │  web_browser()  │                   │
│                    └─────────────────┘                   │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                   │
│                    │   generate()    │                   │
│                    └─────────────────┘                   │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                   │
│                    │    Scorer       │                   │
│                    │    JLLM()       │                   │
│                    └─────────────────┘                   │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                   │
│                    │  Evaluation     │                   │
│                    │  Logs & Metrics │                   │
│                    └─────────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Phase 1: Environment Setup (5-10 minutes)

1. **Install uv Package Manager**
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or with Homebrew
   brew install uv
   ```

2. **Install Inspect AI and Model Providers**
   
   Navigate to the project directory:
   ```bash
   cd inspect-examples
   ```
   
   Then choose your installation method:
   
   | Provider(s)  | Install Command                              | Environment Variable    |
   |-------------|---------------------------------------------|-------------------------|
   | OpenAI      | `uv pip install -e ".[openai]"`             | `OPENAI_API_KEY`       |
   | Anthropic   | `uv pip install -e ".[anthropic]"`          | `ANTHROPIC_API_KEY`    |
   | Mistral     | `uv pip install -e ".[mistral]"`            | `MISTRAL_API_KEY`      |
   | AI21        | `uv pip install -e ".[ai21]"`               | `AI21_API_KEY`         |
   | Google      | `uv pip install -e ".[google]"`             | `GOOGLE_API_KEY`       |
   | All         | `uv pip install -e ".[all-providers]"`      | All keys as needed     |

3. **Set API Keys**
   ```bash
   export OPENAI_API_KEY=your-key-here
   export ANTHROPIC_API_KEY=your-key-here
   # etc.
   ```

4. **Verify Docker**
   ```bash
   docker ps  # Should not error
   ```
   
   The browser task requires Docker for secure sandboxing of tool execution.

### Phase 2: Understanding the Task (5 minutes)

The `examples/browser/browser.py` task structure:

```python
@task
def browser():
    return Task(
        dataset=[Sample(...)],           # What to evaluate
        solver=[                         # How to solve it
            use_tools(web_browser()),    # Provide web browser tool
            generate()                   # Generate final answer
        ],
        scorer=includes(),               # How to score
        sandbox="docker"                 # Security isolation
    )
```

**What it tests:**
- Can the model recognize it needs to use the web_browser tool?
- Can it navigate to the specified URL?
- Can it find relevant information on the page?
- Can it synthesize a coherent summary?

### Phase 3: Single Model Test (5 minutes)

**Goal:** Verify everything works with one model

```bash
# Start with OpenAI (or your preferred model)
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini
```

**What to observe:**
- Model makes tool calls to web_browser
- Browser navigates to the website
- Model extracts and summarizes information
- Task completes with a score

**View results:**
```bash
inspect view
```

### Phase 4: Multi-Model Comparison (10-30 minutes)

**Goal:** Compare agentic capabilities across multiple LLMs

**Option A: Sequential Evaluation**
```bash
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini
inspect eval examples/browser/browser.py --model anthropic/claude-haiku-4-5
inspect eval examples/browser/browser.py --model mistral/mistral-small-latest
```

**Option B: Batch Evaluation**
```bash
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini,anthropic/claude-haiku-4-5,mistral/mistral-small-latest
```

**Option C: Using the Script**
```bash
# Edit run_comparison.sh to uncomment models you want to test
./run_comparison.sh
```

### Phase 5: Analysis (10-15 minutes)

**Open the Log Viewer:**
```bash
inspect view
```

**Compare across models:**

1. **Success Rate**
   - Did the model complete the task?
   - Did it use the web_browser tool correctly?

2. **Tool Usage Efficiency**
   - How many browser calls did it make?
   - Did it navigate efficiently?

3. **Output Quality**
   - Was the summary accurate?
   - Did it include key information?
   - Was it well-structured?

4. **Token Usage**
   - How many input/output tokens?
   - Cost implications?

5. **Latency**
   - How long did the evaluation take?

## Files Created

| File | Purpose |
|------|---------|
| `examples/browser/` | Browser example folder with task and documentation |
| `README.md` | Comprehensive documentation including guide for creating examples |
| `QUICKSTART.md` | Step-by-step getting started guide |
| `PLAN.md` | This file - implementation plan |
| `CHANGELOG.md` | Project history and changes |
| `examples/browser/README.md` | Browser-specific documentation |
| `run_comparison.sh` | Script to automate multi-model testing |
| `pyproject.toml` | Python project configuration with dependencies |
| `setup_with_uv.sh` | Interactive setup script for uv |

## Expected Outcomes

### Successful Run Indicators

✅ Task completes without errors  
✅ Model makes web_browser tool calls  
✅ Browser navigates to target URL  
✅ Model extracts relevant information  
✅ Summary is generated  
✅ Score is computed  

### Log Artifacts

Each evaluation creates a JSON log in `./logs/` containing:
- Complete message history
- Tool calls and responses
- Web pages visited
- Model generations
- Scores and metadata
- Timing information

## Comparison Metrics Matrix

When comparing models, evaluate on these dimensions:

| Metric | Description | Good Example | Poor Example |
|--------|-------------|--------------|--------------|
| **Tool Recognition** | Does model know to use browser? | Immediately calls web_browser | Tries to answer without browsing |
| **Navigation** | Can it get to the right page? | Direct navigation | Gets lost/confused |
| **Information Extraction** | Does it find relevant content? | Finds key information | Misses important details |
| **Synthesis** | Quality of summary | Clear, accurate summary | Vague or incorrect |
| **Efficiency** | Number of steps/tokens | 3-5 browser calls | 20+ calls or loops |
| **Cost** | Token usage × price | Minimal tokens | Excessive usage |

## Advanced Extensions

Once the basic evaluation works, you can:

1. **Add More Samples to Browser Example**
   - Edit `examples/browser/browser.py` to test different websites
   - Add samples requiring different skills (search, multi-page navigation, etc.)

2. **Customize Scoring**
   - Implement custom scorers for more nuanced evaluation
   - Use model grading for subjective quality

3. **Add Solver Variants**
   - Test with `chain_of_thought()` solver
   - Try `self_critique()` for improved outputs
   - Experiment with different solver chains

4. **Detailed Analysis**
   - Export logs to dataframes for statistical analysis
   - Create visualization dashboards
   - Track metrics over time

## Troubleshooting Guide

| Issue | Solution |
|-------|----------|
| Docker not found | Install Docker Desktop and ensure it's running |
| API key error | Verify environment variable is set: `echo $OPENAI_API_KEY` |
| Module not found | Install provider: `uv pip install -e ".[openai]"` |
| uv not found | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Sandbox timeout | Increase timeout in task configuration |
| Network errors | Check firewall/proxy settings for Docker |

## Time Estimates

- **Initial Setup**: 15-20 minutes
- **Single Model Test**: 5-10 minutes (includes model inference time)
- **3-Model Comparison**: 15-30 minutes
- **Analysis**: 10-20 minutes per model
- **Total for Full Comparison**: 45-90 minutes

## Next Steps After Completion

1. ✅ Verify basic browser task works
2. ✅ Run comparison across 2-3 models
3. ✅ Analyze results in Inspect View
4. 📊 Document findings and model rankings
5. 🔬 Design more complex browser tasks
6. 🚀 Explore other Inspect AI capabilities (agents, custom tools, etc.)

## Resources

- **Inspect AI Docs**: https://inspect.aisi.org.uk/
- **Browser Tools Guide**: https://inspect.aisi.org.uk/tools-standard.html
- **Model Providers**: https://inspect.aisi.org.uk/providers.html
- **GitHub Examples**: https://github.com/UKGovernmentBEIS/inspect_ai/tree/main/examples

## Success Criteria

You'll know this is working correctly when:

1. ✅ You can run `inspect eval examples/browser/browser.py --model openai/gpt-4o-mini` successfully
2. ✅ The log viewer shows detailed execution traces
3. ✅ You can compare results across multiple models
4. ✅ You understand the relative strengths/weaknesses of each model on agentic tasks
5. ✅ You can create new examples following the browser example structure

---

**Ready to start?** Follow the QUICKSTART.md guide to run your first evaluation!

