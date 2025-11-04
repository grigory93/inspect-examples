# Browser Example

This example demonstrates how to evaluate LLMs on their ability to use web browsing tools to navigate websites, extract information, and synthesize content.

## What This Tests

The browser task evaluates:
- **Tool Recognition**: Does the model know when to use the web browser?
- **Navigation**: Can it navigate to specific URLs?
- **Information Extraction**: Can it find relevant content on pages?
- **Synthesis**: Can it summarize and answer questions based on web content?

## Task Details

### Samples

The task includes 3 evaluation samples that test different aspects:

1. **Simple Yes/No Question** (`aisi_gov_uk_uk_government`)
   - Navigate to https://www.aisi.gov.uk/
   - Determine if UK AISI belongs to UK government
   - Expected answer: "Yes"

2. **Definition Extraction** (`aisi_gov_uk_controlarena`)
   - Find and extract definition of ControlArena
   - Expected: One sentence definition

3. **Extended Definition** (`aisi_gov_uk_inspect_sandboxing_toolkit`)
   - Find and extract extended definition of Inspect Sandboxing Toolkit
   - Expected: Comprehensive sentence

### Configuration

- **Solver**: `use_tools(web_browser())` + `generate()`
- **Scorer**: `model_graded_qa(model="openai/gpt-4o-mini")`
- **Sandbox**: Docker (using `compose.yaml`)
- **Limits**:
  - Message limit: 10 messages
  - Working time: 3 minutes
  - Token limit: 512K tokens

## Running the Task

### Basic Usage

```bash
# Run with a specific model
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini

# View results
inspect view
```

### Comparing Multiple Models

```bash
# Sequential evaluation
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini
inspect eval examples/browser/browser.py --model anthropic/claude-haiku-4-5
inspect eval examples/browser/browser.py --model mistral/mistral-small-latest

# Batch evaluation
inspect eval examples/browser/browser.py --model openai/gpt-4o-mini,anthropic/claude-haiku-4-5

# View all results
inspect view
```

### Using Helper Scripts

```bash
# From project root
./run_comparison.sh examples/browser/browser.py
```

## Requirements

- **Docker**: Must be installed and running for sandboxing
  - The `aisiuk/inspect-tool-support` image will be pulled automatically on first run
  - Verify Docker is running: `docker ps`
- **API Key**: For the model provider you're using (e.g., `OPENAI_API_KEY`)
- **Internet Access**: The browser needs to access external websites from within the Docker container

## Customization

### Adding More Samples

The browser task uses three samples to evaluate different aspects of web browsing. You can add more by editing `browser.py`:

**Current samples:**
1. Simple Yes/No question (UK government affiliation)
2. Definition extraction (ControlArena)
3. Extended definition (Inspect Sandboxing Toolkit)

**To add new samples**, edit the `EVAL_SAMPLES` list in `browser.py`:

```python
EVAL_SAMPLES = [
    # ... existing samples ...
    Sample(
        id="custom_navigation",
        input="Navigate to https://example.com and find the contact email address.",
        target="The contact email or grading guidance"
    ),
    Sample(
        id="multi_page_search",
        input="Search the Inspect AI documentation for information about tool approval policies.",
        target="Key information about tool approval"
    )
]
```

**Sample design tips:**
- Use descriptive IDs for tracking
- Make prompts clear and specific
- Include target answers or grading criteria
- Test with different complexity levels
- Cover various web navigation patterns

### Modifying Limits

Adjust the task limits in `browser.py`:

```python
@task
def browser():
    return Task(
        dataset=EVAL_SAMPLES,
        solver=[...],
        message_limit=20,        # Increase message limit
        working_limit=5 * 60,    # 5 minutes instead of 3
        token_limit=(1024*1000), # 1M tokens instead of 512K
        scorer=model_graded_qa(model="openai/gpt-4o-mini"),
        sandbox=("docker", "compose.yaml"),
    )
```

### Changing the Scorer

You can use different scoring methods:

```python
from inspect_ai.scorer import includes, match, model_graded_fact

# Exact match
scorer=match()

# Contains expected text
scorer=includes()

# Model grading for facts
scorer=model_graded_fact()

# Model grading for Q&A (current)
scorer=model_graded_qa(model="openai/gpt-4o-mini")
```

### Customizing Browser Tool Options

The `web_browser()` tool can be customized with various options:

```python
from inspect_ai.tool import web_browser
from inspect_ai.solver import use_tools

# Custom timeout (default is 180 seconds)
solver=[
    use_tools(web_browser(timeout=300)),  # 5 minute timeout
    generate()
]

# Disable mouse/keyboard interactions (navigation only)
solver=[
    use_tools(web_browser(interactive=False)),
    generate()
]

# Combine multiple options
solver=[
    use_tools(web_browser(timeout=300, interactive=False)),
    generate()
]
```

**Available options:**
- `timeout`: Maximum time in seconds for browser operations (default: 180)
- `interactive`: Enable/disable mouse and keyboard interactions (default: True)

## Expected Results

### Successful Evaluation

When a model successfully completes the task, you'll see:
- ✅ Web browser tool calls in the message history
- ✅ Navigation to target URLs
- ✅ Content extraction from pages
- ✅ Relevant answers to questions
- ✅ Scores indicating correctness

### Common Issues

**Docker not running**:
- Ensure Docker is installed and running: `docker ps` or `docker info`
- Start Docker Desktop (macOS/Windows) or Docker daemon (Linux)
- Pull the image manually if needed: `docker pull aisiuk/inspect-tool-support`

**Model doesn't use browser tool**:
- Some models may try to answer from knowledge instead
- Check if the model supports tool calling
- Review prompt engineering in the task

**Sandbox/Browser timeouts**:
- Increase `working_limit` in the task if pages are slow to load: `working_limit=5 * 60`
- Increase browser tool timeout: `web_browser(timeout=300)`
- Check Docker resource allocation (CPU, memory)
- Verify internet connectivity from within the Docker container

**Navigation failures**:
- Verify internet connectivity from Docker
- Check if target websites are accessible
- Review Docker network configuration in `compose.yaml`
- Ensure Docker container has network access: `network_mode: bridge` in compose.yaml

## Analysis

After running evaluations, analyze:

1. **Tool Usage Efficiency**: How many browser calls did the model make?
2. **Navigation Path**: Did it go directly to the right pages?
3. **Answer Quality**: How accurate were the extracted answers?
4. **Token Usage**: Was the model efficient with tokens?
5. **Time Taken**: How long did the evaluation take?

## Next Steps

- Compare multiple models on this task
- Add more complex navigation scenarios
- Test multi-page information synthesis
- Implement custom scorers for your use case
- Create similar tasks for other agentic capabilities

