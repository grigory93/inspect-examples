# Design Document - RAGChecker Custom Scorer

This document explains the design decisions and implementation approach for the RAGChecker-based custom scorer in Inspect AI.

## Overview

The custom scorer integrates RAGChecker, a sophisticated evaluation framework, into Inspect AI's evaluation pipeline to provide fine-grained metrics (precision, recall, F1) for model responses.

## Design Goals

1. **Fine-grained Evaluation**: Move beyond binary pass/fail to quantify accuracy and completeness
2. **Semantic Understanding**: Evaluate based on meaning, not string matching
3. **Reusability**: Create a scorer that works across different question types
4. **Transparency**: Provide clear metrics that explain model performance
5. **Easy Integration**: Follow Inspect AI patterns for seamless usage

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Inspect AI Task                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Dataset    │→ │    Solver    │→ │ Custom Scorer    │  │
│  │  (Samples)   │  │  (generate)  │  │ (RAGChecker)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                              ↓
                    ┌──────────────────────────────────────────┐
                    │         RAGChecker Pipeline              │
                    │  ┌────────────┐  ┌──────────────────┐   │
                    │  │  Extractor │→ │     Checker      │   │
                    │  │  (Claims)  │  │ (Verification)   │   │
                    │  └────────────┘  └──────────────────┘   │
                    └──────────────────────────────────────────┘
                                              ↓
                    ┌──────────────────────────────────────────┐
                    │          Metrics Output                  │
                    │  • Precision                             │
                    │  • Recall                                │
                    │  • F1 Score                              │
                    └──────────────────────────────────────────┐
```

### Key Components

#### 1. Custom Scorer (`ragchecker_scorer.py`)

**Purpose**: Bridge between Inspect AI and RAGChecker

**Implementation Pattern**:
```python
@scorer(metrics=[metric()])
def ragchecker_scorer() -> Scorer:
    async def score(state: TaskState, target: Target) -> Score:
        # Implementation
        pass
    return score
```

**Key Decisions**:
- **Async function**: Follows Inspect AI's async pattern for scalability
- **Decorator pattern**: Uses `@scorer` decorator for proper integration
- **Error handling**: Gracefully handles missing dependencies and API errors
- **Metadata storage**: Stores all metrics (P/R/F1) for post-analysis

#### 2. Task Definition (`custom_scorer.py`)

**Purpose**: Define evaluation dataset and configuration

**Structure**:
```python
EVAL_SAMPLES = [...]  # Dataset definition

@task
def custom_scorer():
    return Task(
        dataset=EVAL_SAMPLES,
        solver=[generate()],
        scorer=ragchecker_scorer()
    )
```

**Key Decisions**:
- **Simple solver chain**: Uses only `generate()` to focus on scoring
- **Factual questions**: Selected questions with verifiable ground truth
- **Diverse domains**: Geography, history, science for broad coverage

## Implementation Details

### RAGChecker Integration

#### Data Format Conversion

RAGChecker expects a specific JSON structure:
```json
{
  "results": [
    {
      "query_id": "unique_id",
      "query": "Question text",
      "gt_answer": "Ground truth answer",
      "response": "Model response",
      "retrieved_context": []
    }
  ]
}
```

Our implementation converts Inspect AI's `TaskState` and `Target` objects into this format:

```python
rag_data = {
    "results": [
        {
            "query_id": state.sample_id or "sample_1",
            "query": state.input_text,
            "gt_answer": target.text,
            "response": state.output.completion,
            "retrieved_context": []
        }
    ]
}
```

**Note**: We use empty `retrieved_context` since we're evaluating Q&A, not RAG systems.

#### Model Configuration

We use OpenAI GPT-4o-mini for both extraction and checking:

```python
evaluator = RAGChecker(
    extractor_name="openai/gpt-4o-mini",
    checker_name="openai/gpt-4o-mini",
    batch_size_extractor=1,
    batch_size_checker=1
)
```

**Why GPT-4o-mini?**
- ✅ Cost-effective for evaluation
- ✅ Fast enough for real-time scoring
- ✅ Sufficiently accurate for claim extraction/checking
- ⚠️ Users can upgrade to `gpt-4o` for more accuracy

**Batch Size = 1**: 
- Evaluates one sample at a time
- Simpler error handling
- Could be increased for batch evaluation

### Score Representation

#### Primary Score Value

We use **F1 as the primary score** (0-1 scale):

```python
return Score(
    value=f1 / 100.0,  # Convert from 0-100 to 0-1
    ...
)
```

**Rationale**:
- F1 balances precision and recall
- Single number for ranking/comparison
- Standard ML metric, widely understood
- Penalizes extreme imbalances

**Alternative Approaches Considered**:
1. ❌ **Precision only**: Ignores completeness
2. ❌ **Recall only**: Ignores accuracy
3. ⚠️ **Weighted average**: Adds complexity, less standard
4. ✅ **F1**: Best balance, standard metric

#### Metadata Storage

All metrics are stored in metadata for detailed analysis:

```python
metadata={
    "precision": precision,  # 0-100
    "recall": recall,        # 0-100
    "f1": f1                # 0-100
}
```

This allows:
- Post-hoc analysis of precision/recall trade-offs
- Custom aggregations across samples
- Detailed reporting and visualization

#### Explanation String

Human-readable summary in explanation field:

```python
explanation=f"Precision: {precision:.1f}%, Recall: {recall:.1f}%, F1: {f1:.1f}%"
```

## Error Handling Strategy

### Graceful Degradation

The scorer handles errors at multiple levels:

#### 1. Import Errors

```python
try:
    from ragchecker import RAGResults, RAGChecker
except ImportError:
    return Score(value="E", explanation="RAGChecker not installed...")
```

**Why**: Allow the example to be loaded even if dependencies aren't installed yet.

#### 2. Missing Data

```python
if not model_response or not ground_truth:
    return Score(value="E", explanation="Missing model response or ground truth target")
```

**Why**: Protect against malformed samples or generation failures.

#### 3. Evaluation Errors

```python
try:
    # RAGChecker evaluation
    ...
except Exception as e:
    return Score(value="E", explanation=f"Error during RAGChecker evaluation: {str(e)}")
```

**Why**: Catch API errors, rate limits, or unexpected issues without crashing the entire evaluation.

### Error Score Convention

We use `value="E"` to indicate errors, following Inspect AI conventions. This:
- ✅ Distinguishes errors from low scores (0.0)
- ✅ Doesn't affect aggregate metrics
- ✅ Is visible in evaluation logs

## Dataset Design

### Sample Selection Criteria

We chose 3 questions that demonstrate different evaluation scenarios:

#### 1. France Capital (Geography + Demographics)
```python
Sample(
    id="france_capital",
    input="What is the capital of France and how big is it?",
    target="The capital of France is Paris and it's 105.4 square kilometers..."
)
```

**Tests**:
- Multiple facts (capital name, area, population)
- Numerical precision
- Common knowledge vs. specific facts

#### 2. US Founding (Historical Events)
```python
Sample(
    id="us_founding",
    input="When was the United States founded as a state and how many states did it originally have?",
    target="The United States declared independence on July 4, 1776..."
)
```

**Tests**:
- Historical dates
- Numerical facts (13 states)
- Optional details (state names)
- Completeness vs. accuracy trade-off

#### 3. Airplane Invention (Innovation History)
```python
Sample(
    id="airplane_invention",
    input="When was the airplane invented, by whom, and where?",
    target="The airplane was invented by the Wright brothers..."
)
```

**Tests**:
- Multiple entities (Wright brothers)
- Specific date (December 17, 1903)
- Location (Kitty Hawk, North Carolina)
- Technical details (powered flight)

### Sample Design Principles

1. **Verifiable Facts**: All answers are objectively verifiable
2. **Multiple Components**: Each question has 3-5 key facts
3. **Varying Difficulty**: From common knowledge to specific details
4. **Diverse Domains**: Geography, history, science
5. **Clear Ground Truth**: Comprehensive target answers provided

## Design Trade-offs

### 1. Evaluation Model Selection

**Decision**: Use GPT-4o-mini by default

**Pros**:
- ✅ Cost-effective ($0.15/1M input tokens vs $2.50 for GPT-4o)
- ✅ Fast evaluation (~2-3s per sample)
- ✅ Good enough for most use cases

**Cons**:
- ⚠️ Slightly less accurate than GPT-4o
- ⚠️ May miss subtle semantic differences

**Alternative**: Allow users to configure evaluation models

### 2. Batch Size = 1

**Decision**: Process one sample at a time

**Pros**:
- ✅ Simpler error handling
- ✅ Clear per-sample attribution
- ✅ Progress visible during evaluation

**Cons**:
- ⚠️ Slower for large datasets
- ⚠️ More API calls

**Future Enhancement**: Add batch processing option

### 3. F1 as Primary Score

**Decision**: Use F1 score as the main value

**Pros**:
- ✅ Balances precision and recall
- ✅ Standard ML metric
- ✅ Single number for ranking

**Cons**:
- ⚠️ May hide important P/R imbalances
- ⚠️ Not always intuitive

**Mitigation**: Store P/R in metadata and explanation

### 4. Empty Retrieval Context

**Decision**: Use empty `retrieved_context` array

**Pros**:
- ✅ Simpler for Q&A evaluation
- ✅ Focuses on generation quality
- ✅ No need for retrieval system

**Cons**:
- ⚠️ Can't use retrieval-specific metrics
- ⚠️ Not testing full RAG pipeline

**Future Enhancement**: Add retrieval context support for RAG evaluation

## Extension Points

The design supports several extensions:

### 1. Custom Metric Selection

Users can choose which RAGChecker metrics to use:

```python
from ragchecker.metrics import retriever_metrics, generator_metrics

# In scorer implementation:
evaluator.evaluate(rag_results, generator_metrics)
```

### 2. Different Evaluation Models

Change the models used for claim extraction and checking:

```python
evaluator = RAGChecker(
    extractor_name="openai/gpt-4o",
    checker_name="openai/gpt-4o"
)
```

### 3. Retrieval Context Support

Add retrieval context for full RAG evaluation:

```python
"retrieved_context": [
    {"doc_id": "doc1", "text": state.metadata.get("context", [])[0]},
    # ...
]
```

### 4. Custom Score Calculation

Modify how the final score is computed:

```python
# Precision-focused scoring
value = precision / 100.0

# Recall-focused scoring
value = recall / 100.0

# Custom weighted score
value = (0.7 * precision + 0.3 * recall) / 100.0
```

## Testing Strategy

### Verification Script

We provide `test_setup.py` to verify:
- ✅ All dependencies installed
- ✅ spaCy model available
- ✅ API keys configured
- ✅ Version compatibility

### Manual Testing

Users should test with:
1. **Single sample**: Verify basic functionality
2. **Multiple models**: Compare results
3. **Edge cases**: Empty responses, long responses
4. **Error conditions**: Missing API key, wrong model name

## Performance Considerations

### Evaluation Time

**Per Sample**:
- Claim extraction: ~1-2 seconds
- Claim checking: ~1-2 seconds
- Total: ~2-4 seconds per sample

**For 3 samples**: ~6-12 seconds

**Optimization Options**:
1. Use faster models (gpt-4o-mini)
2. Increase batch sizes
3. Cache evaluation results
4. Parallelize across samples

### Cost Estimation

**Per Sample** (with GPT-4o-mini):
- Extractor: ~500 tokens input, ~200 tokens output
- Checker: ~1000 tokens input, ~100 tokens output
- Cost: ~$0.0003 per sample

**For 100 samples**: ~$0.03

**For 1000 samples**: ~$0.30

## Future Enhancements

1. **Batch Processing**: Process multiple samples simultaneously
2. **Caching**: Cache claim extraction results
3. **Streaming**: Stream results as they're available
4. **Custom Metrics**: Allow users to define custom metric combinations
5. **Retrieval Support**: Full RAG evaluation with context
6. **Multi-language**: Support for non-English evaluation
7. **Custom Extractors**: Allow custom claim extraction logic

## References

- [RAGChecker Paper](https://arxiv.org/pdf/2408.08067)
- [RAGChecker GitHub](https://github.com/amazon-science/RAGChecker)
- [RefChecker Documentation](https://github.com/amazon-science/RefChecker)
- [Inspect AI Custom Scorers](https://inspect.ai-safety-institute.org.uk/scorers.html)
- [LiteLLM Documentation](https://docs.litellm.ai/)

## Conclusion

This implementation provides a robust, extensible custom scorer that brings RAGChecker's sophisticated evaluation capabilities to Inspect AI. The design balances ease of use, accuracy, and performance while maintaining clear extension points for future enhancements.

