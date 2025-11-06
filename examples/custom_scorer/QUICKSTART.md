# Quick Start - Custom Scorer with RAGChecker

Get started with RAGChecker-based scoring in 5 minutes!

## Prerequisites

- Python 3.10+
- OpenAI API key

## Step 1: Install Dependencies

```bash
# Install RAGChecker and required packages
pip install ragchecker litellm

# Or use uv (recommended)
uv pip install -e ".[ragchecker,openai]"

# Install spaCy English model (required by RAGChecker)
# If using uv, use this command instead:
uv pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# If using regular pip:
python -m spacy download en_core_web_sm
```

## Step 2: Set API Key

```bash
export OPENAI_API_KEY=your-openai-api-key-here
```

## Step 3: Run Evaluation

```bash
inspect eval examples/custom_scorer/custom_scorer.py --model openai/gpt-4o-mini
```

## Step 4: View Results

```bash
inspect view
```

You'll see:
- **Value**: F1 score (0-1 scale)
- **Metadata**: Precision, Recall, and F1 percentages
- **Explanation**: Detailed breakdown of scores

## Understanding the Scores

- **Precision**: How accurate is the response? (no errors/hallucinations)
- **Recall**: How complete is the response? (covers all key facts)
- **F1**: Balance of precision and recall

**Good scores**: F1 > 0.85 (85%)
**Acceptable**: F1 > 0.70 (70%)
**Needs work**: F1 < 0.70 (70%)

## What's Next?

1. **Try different models**:
   ```bash
   inspect eval examples/custom_scorer/custom_scorer.py --model openai/gpt-4o
   inspect eval examples/custom_scorer/custom_scorer.py --model anthropic/claude-3-5-sonnet-20241022
   ```

2. **Add your own questions**: Edit `EVAL_SAMPLES` in `custom_scorer.py`

3. **Customize the scorer**: Modify `ragchecker_scorer.py` to use different metrics or evaluation models

4. **Read the full documentation**: See `README.md` for detailed information

## Troubleshooting

**"RAGChecker not installed"**:
```bash
pip install ragchecker
```

**"No module named 'en_core_web_sm'"**:
```bash
# If using uv:
uv pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# If using pip:
python -m spacy download en_core_web_sm
```

**"No module named pip" (when using uv)**:
```bash
# Use uv to install the spaCy model directly:
uv pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

**"OpenAI API key not configured"**:
```bash
export OPENAI_API_KEY=your-key
echo $OPENAI_API_KEY  # Verify it's set
```

**Slow evaluation**: 
- RAGChecker uses LLMs for evaluation, so it takes time
- Use `gpt-4o-mini` for faster evaluation
- Consider reducing samples during development

## Example Output

```
Score:
  Value: 0.87
  Explanation: Precision: 92.3%, Recall: 82.1%, F1: 87.0%
  
Metadata:
  precision: 92.3
  recall: 82.1
  f1: 87.0
```

This means:
- ✅ 92.3% of what the model said was correct (high precision)
- ⚠️ 82.1% of key facts were included (good recall, but some missing)
- ✅ Overall F1 score of 87% is good

For more details, see the complete [README.md](README.md).

