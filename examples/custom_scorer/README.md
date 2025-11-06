# Custom Scorer Example - RAGChecker Integration

This example demonstrates how to create a custom scorer in Inspect AI that uses **RAGChecker** to evaluate model responses with fine-grained precision, recall, and F1 metrics.

## What This Tests

The custom scorer evaluates:
- **Precision**: How accurate is the model's response? (no hallucinations or incorrect information)
- **Recall**: How complete is the model's response? (coverage of ground truth)
- **F1 Score**: Harmonic mean of precision and recall

Unlike simple string matching scorers, RAGChecker performs **claim-level evaluation**, breaking down responses into individual claims and checking each one against the ground truth.

## What is RAGChecker?

**RAGChecker** is a sophisticated evaluation framework designed for Retrieval-Augmented Generation (RAG) systems, but it works excellently for any Q&A evaluation. It provides:

- **Fine-grained evaluation**: Breaks responses into claims for detailed analysis
- **Multiple metrics**: Precision, recall, F1, and diagnostic metrics
- **LLM-based checking**: Uses language models to understand semantic equivalence
- **No retrieval required**: Works with just question, answer, and ground truth

For more details, see the [RAGChecker GitHub repository](https://github.com/amazon-science/RAGChecker).

## Task Details

### Samples

The task includes 3 factual questions to evaluate model knowledge:

1. **Geography & Demographics** (`france_capital`)
   - Question: "What is the capital of France and how big is it?"
   - Tests: Factual accuracy, numerical precision

2. **Historical Events** (`us_founding`)
   - Question: "When was the United States founded and how many states did it originally have?"
   - Tests: Historical knowledge, completeness

3. **Invention History** (`airplane_invention`)
   - Question: "When was the airplane invented, by whom, and where?"
   - Tests: Multiple facts in one answer, detail accuracy

### Configuration

- **Solver**: `generate()` - Simple text generation
- **Scorer**: `ragchecker_scorer()` - Custom scorer using RAGChecker
- **Evaluation Models**: OpenAI GPT-4o-mini (configurable)

## Requirements

### System Requirements
- Python 3.10+
- OpenAI API access

### Dependencies

Install the required packages:

```bash
# Install RAGChecker and its dependencies
pip install ragchecker

# Install spaCy English model (required by RAGChecker)
# If using regular pip:
python -m spacy download en_core_web_sm

# If using uv (see note below):
uv pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Install LiteLLM (for OpenAI model access)
pip install litellm
```

**Note for uv users**: The `python -m spacy download` command requires `pip` internally, which is not included in `uv` environments by default. Use the `uv pip install` command shown above instead.

Or add to `pyproject.toml`:

```toml
[project.optional-dependencies]
ragchecker = [
    "ragchecker>=0.1.9",
    "litellm>=1.0.0",
]
```

### API Keys

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=your-openai-api-key-here
```

## Running the Task

### Basic Usage (CLI)

```bash
# Run with a specific model
inspect eval examples/custom_scorer/custom_scorer.py --model openai/gpt-4o-mini

# View results
inspect view
```

### Programmatic Usage (Python)

You can also run the evaluation from Python code:

```python
from inspect_ai import eval
from examples.custom_scorer import custom_scorer

# Run evaluation
log = await eval(custom_scorer(), model="openai/gpt-4o-mini")

# Access results
print(f"Status: {log.status}")
for sample in log.samples:
    print(f"Sample {sample.id}: {sample.scores}")
```

For a complete example with result analysis, see `run_evaluation.py`:

```bash
python examples/custom_scorer/run_evaluation.py
```

### Comparing Multiple Models

**Using CLI:**
```bash
# Sequential evaluation
inspect eval examples/custom_scorer/custom_scorer.py --model openai/gpt-4o-mini
inspect eval examples/custom_scorer/custom_scorer.py --model openai/gpt-4o
inspect eval examples/custom_scorer/custom_scorer.py --model anthropic/claude-3-5-sonnet-20241022

# View all results
inspect view
```

**Using Python:**
```python
# See run_evaluation.py for the complete implementation
from inspect_ai import eval
from examples.custom_scorer import custom_scorer

models = ["openai/gpt-4o-mini", "openai/gpt-4o"]
results = {}

for model in models:
    log = await eval(custom_scorer(), model=model)
    results[model] = log

# Compare results
for model, log in results.items():
    print(f"{model}: {log.results.scores}")
```

## How It Works

### 1. Custom Scorer Implementation

The `ragchecker_scorer.py` module implements a custom scorer following the Inspect AI pattern:

```python
@scorer(metrics=[metric()])
def ragchecker_scorer() -> Scorer:
    async def score(state: TaskState, target: Target) -> Score:
        # Extract question, response, and ground truth
        question = state.input_text
        model_response = state.output.completion
        ground_truth = target.text
        
        # Prepare data for RAGChecker
        rag_data = {
            "results": [{
                "query": question,
                "gt_answer": ground_truth,
                "response": model_response,
                "retrieved_context": []
            }]
        }
        
        # Initialize and run RAGChecker
        rag_results = RAGResults.from_json(json.dumps(rag_data))
        evaluator = RAGChecker(
            extractor_name="openai/gpt-4o-mini",
            checker_name="openai/gpt-4o-mini"
        )
        evaluator.evaluate(rag_results, overall_metrics)
        
        # Extract and return scores
        metrics = rag_results.metrics
        return Score(
            value=metrics["overall_metrics"]["f1"] / 100.0,
            metadata={
                "precision": metrics["overall_metrics"]["precision"],
                "recall": metrics["overall_metrics"]["recall"],
                "f1": metrics["overall_metrics"]["f1"]
            }
        )
    
    return score
```

### 2. RAGChecker Evaluation Process

When you run the evaluation:

1. **Model generates response** to the input question
2. **Scorer extracts claims** from both the model response and ground truth
3. **Checker verifies claims** using an LLM to determine semantic equivalence
4. **Metrics are computed**:
   - **Precision** = (Correct claims in response) / (Total claims in response)
   - **Recall** = (Correct claims in response) / (Total claims in ground truth)
   - **F1** = 2 × (Precision × Recall) / (Precision + Recall)

### 3. Score Output

Each evaluation produces:
- **Value**: F1 score (0-1 scale)
- **Explanation**: Text showing precision, recall, and F1 percentages
- **Metadata**: Detailed metrics for analysis

## Expected Results

### High-Quality Responses

For accurate, complete responses, you should see:
- ✅ **Precision: 90-100%** - No hallucinations or errors
- ✅ **Recall: 80-100%** - Most/all key facts included
- ✅ **F1: 85-100%** - Well-balanced accuracy and completeness

### Common Score Patterns

**Perfect Score (100% P, R, F1)**:
- Model provides all facts correctly
- No additional incorrect information

**High Precision, Low Recall (e.g., 100% P, 50% R)**:
- Model is accurate but incomplete
- Missing some key facts from ground truth

**Low Precision, High Recall (e.g., 60% P, 90% R)**:
- Model covers most facts but includes errors
- May have hallucinations or inaccuracies

**Low Both (e.g., 50% P, 40% R)**:
- Model response has errors and is incomplete
- Needs significant improvement

## Customization

### Adding More Samples

Edit `EVAL_SAMPLES` in `custom_scorer.py`:

```python
EVAL_SAMPLES = [
    # ... existing samples ...
    Sample(
        id="your_sample_id",
        input="Your question here",
        target="The complete ground truth answer with all key facts."
    ),
]
```

**Tips for good samples:**
- Include questions with multiple factual components
- Provide comprehensive ground truth answers
- Use clear, unambiguous questions
- Cover different knowledge domains

### Changing Evaluation Models

You can change which models RAGChecker uses for claim extraction and verification.

In `ragchecker_scorer.py`, modify:

```python
evaluator = RAGChecker(
    extractor_name="openai/gpt-4o",  # More powerful extractor
    checker_name="openai/gpt-4o",    # More powerful checker
    batch_size_extractor=1,
    batch_size_checker=1
)
```

**Model options** (via LiteLLM):
- `openai/gpt-4o-mini` - Fast, cost-effective (default)
- `openai/gpt-4o` - More accurate, higher cost
- `openai/gpt-4-turbo` - Balance of speed and accuracy
- Other providers: See [RefChecker docs](https://github.com/amazon-science/RefChecker)

### Using Different RAGChecker Metrics

RAGChecker provides many metrics beyond precision/recall:

```python
from ragchecker.metrics import (
    overall_metrics,      # precision, recall, f1
    retriever_metrics,    # if using retrieval context
    generator_metrics,    # detailed generation analysis
    all_metrics          # everything
)

# In the scorer:
evaluator.evaluate(rag_results, all_metrics)
```

See [RAGChecker documentation](https://github.com/amazon-science/RAGChecker) for all available metrics.

### Custom Score Value

By default, the scorer uses F1 as the primary value. You can change this:

```python
# Use precision as primary score
return Score(
    value=precision / 100.0,
    explanation=f"Precision: {precision:.1f}%, Recall: {recall:.1f}%, F1: {f1:.1f}%",
    metadata={"precision": precision, "recall": recall, "f1": f1}
)

# Or create a custom weighted score
custom_score = (0.6 * precision + 0.4 * recall) / 100.0
return Score(
    value=custom_score,
    explanation=f"Custom Score: {custom_score:.3f}",
    metadata={"precision": precision, "recall": recall}
)
```

## Troubleshooting

### RAGChecker Not Installed

**Error**: "RAGChecker not installed"

**Solution**:
```bash
pip install ragchecker

# For spaCy model:
# If using pip:
python -m spacy download en_core_web_sm

# If using uv:
uv pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

### "No module named pip" Error (uv users)

**Error**: When running `python -m spacy download en_core_web_sm`

**Cause**: The spaCy download command requires pip, which is not included in uv environments by default.

**Solution**: Install the spaCy model directly with uv:
```bash
uv pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

**Verify it works**:
```bash
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('Model loaded')"
```

### OpenAI API Key Not Set

**Error**: "Error: OpenAI API key not configured"

**Solution**:
```bash
export OPENAI_API_KEY=your-key-here
# Verify it's set
echo $OPENAI_API_KEY
```

### Slow Evaluation

RAGChecker uses LLMs for claim extraction and checking, which can be slow.

**Solutions**:
- Use faster models: `openai/gpt-4o-mini`
- Reduce sample size during development
- Increase batch sizes (if supported):
  ```python
  evaluator = RAGChecker(
      extractor_name="openai/gpt-4o-mini",
      checker_name="openai/gpt-4o-mini",
      batch_size_extractor=8,  # Process more at once
      batch_size_checker=8
  )
  ```

### Rate Limits

If you hit OpenAI rate limits:
- Add delays between samples
- Use a different model provider
- Upgrade your OpenAI tier

### Unexpected Scores

If scores seem off:
- Check that ground truth targets are comprehensive
- Verify model responses contain the expected information
- Review the RAGChecker explanation in the score output
- Consider using more powerful evaluation models (gpt-4o instead of gpt-4o-mini)

## Understanding the Metrics

### Precision (0-100%)

**What it measures**: Accuracy of the model's response.

- **100%**: Every claim in the response is correct
- **50%**: Half the claims are correct, half are wrong or unsupported
- **0%**: All claims are incorrect or hallucinated

**Example**:
- Ground truth: "Paris is the capital of France with 2.1M people"
- Response: "Paris is the capital of France with 5M people"
- Precision: ~50% (capital correct, population wrong)

### Recall (0-100%)

**What it measures**: Completeness of the model's response.

- **100%**: All facts from ground truth are mentioned
- **50%**: Half the key facts are included
- **0%**: None of the key facts are mentioned

**Example**:
- Ground truth: "Paris is the capital of France with 2.1M people"
- Response: "Paris is the capital of France"
- Recall: ~50% (capital mentioned, population missing)

### F1 Score (0-100%)

**What it measures**: Balance between precision and recall.

- **High F1**: Response is both accurate and complete
- **Low F1**: Response has errors or is incomplete (or both)

F1 is the harmonic mean, which penalizes imbalanced scores:
- Precision 100%, Recall 50% → F1 ≈ 67%
- Precision 90%, Recall 90% → F1 = 90%

## Advanced Usage

### Programmatic Evaluation

The `run_evaluation.py` script demonstrates several advanced patterns:

1. **Basic evaluation from Python:**
   ```python
   log = await eval(custom_scorer(), model="openai/gpt-4o-mini")
   ```

2. **Multiple models comparison:**
   ```python
   results = {}
   for model in ["openai/gpt-4o-mini", "openai/gpt-4o"]:
       results[model] = await eval(custom_scorer(), model=model)
   ```

3. **Custom configuration:**
   ```python
   log = await eval(
       custom_scorer(),
       model="openai/gpt-4o-mini",
       model_args={"temperature": 0.7},
       log_dir="./custom_logs"
   )
   ```

4. **Result analysis:**
   ```python
   from inspect_ai.log import read_eval_log
   log = read_eval_log("logs/my-evaluation.json")
   # Analyze precision, recall, F1 metrics
   ```

See `run_evaluation.py` for complete working examples.

### Integrating with Other Scorers

You can combine RAGChecker with other scorers:

```python
from inspect_ai.scorer import accuracy, match

@task
def combined_scoring():
    return Task(
        dataset=EVAL_SAMPLES,
        solver=[generate()],
        scorer=[
            ragchecker_scorer(),  # Fine-grained metrics
            match(),              # Exact match check
        ]
    )
```

### Creating Variants

Create specialized versions for different use cases:

```python
@scorer(metrics=[metric()])
def ragchecker_high_precision() -> Scorer:
    """RAGChecker scorer optimized for precision evaluation."""
    # Implementation focusing on precision...
    
@scorer(metrics=[metric()])
def ragchecker_high_recall() -> Scorer:
    """RAGChecker scorer optimized for recall evaluation."""
    # Implementation focusing on recall...
```

### Using with Retrieval Context

If your task involves retrieval, you can include context:

```python
rag_data = {
    "results": [{
        "query": question,
        "gt_answer": ground_truth,
        "response": model_response,
        "retrieved_context": [
            {"doc_id": "doc1", "text": "Retrieved passage 1..."},
            {"doc_id": "doc2", "text": "Retrieved passage 2..."},
        ]
    }]
}
```

This enables additional RAGChecker metrics like:
- `claim_recall`: How much context supports the claims
- `context_precision`: Quality of retrieved context
- `context_utilization`: How well context was used

## Analysis

After running evaluations, analyze:

1. **Score Distribution**: Are models consistently high/low on precision vs recall?
2. **Per-Sample Performance**: Which questions are harder?
3. **Model Comparison**: Which models balance accuracy and completeness better?
4. **Error Patterns**: Do certain types of facts cause issues?

View detailed results:
```bash
inspect view
# Click on individual samples to see:
# - Model responses
# - Score breakdowns
# - Precision/recall/F1 values
```

## Benefits of RAGChecker Scoring

Compared to traditional scorers:

| Scorer Type | Precision | Recall | Semantic Understanding | Fine-grained |
|-------------|-----------|--------|----------------------|--------------|
| `match()` | ❌ All-or-nothing | ❌ All-or-nothing | ❌ Exact string | ❌ No |
| `includes()` | ❌ Partial | ❌ Partial | ❌ String contains | ❌ No |
| `model_graded_qa()` | ⚠️ Single score | ⚠️ Single score | ✅ Yes | ⚠️ Limited |
| **`ragchecker_scorer()`** | **✅ Detailed** | **✅ Detailed** | **✅ Yes** | **✅ Yes** |

RAGChecker provides:
- ✅ Separate precision and recall metrics
- ✅ Claim-level analysis
- ✅ Semantic understanding (not just string matching)
- ✅ Fine-grained feedback for improvement

## Next Steps

1. **Run the example**: Test with different models
2. **Add your own questions**: Create domain-specific evaluations
3. **Experiment with metrics**: Try different RAGChecker metric combinations
4. **Compare models**: See which models balance precision and recall best
5. **Tune evaluation models**: Test if better evaluation models (gpt-4o) provide more accurate scoring
6. **Integrate into CI/CD**: Add automated evaluation to your development workflow

## Resources

### RAGChecker
- [RAGChecker GitHub](https://github.com/amazon-science/RAGChecker)
- [RAGChecker Paper](https://arxiv.org/pdf/2408.08067)
- [RefChecker Documentation](https://github.com/amazon-science/RefChecker)

### Inspect AI
- [Custom Scorers Guide](https://inspect.ai-safety-institute.org.uk/scorers.html)
- [Scorer Examples](https://github.com/UKGovernmentBEIS/inspect_ai/blob/main/examples/scorer.py)
- [Inspect AI Documentation](https://inspect.ai-safety-institute.org.uk/)

### Model Access
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

