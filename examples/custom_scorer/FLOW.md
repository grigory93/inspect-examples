# RAGChecker Custom Scorer - Evaluation Flow

This document visualizes how the RAGChecker custom scorer processes evaluations.

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     User runs command                            │
│  inspect eval examples/custom_scorer/custom_scorer.py --model   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Inspect AI Framework                          │
│  1. Loads task from custom_scorer.py                            │
│  2. Reads EVAL_SAMPLES dataset                                  │
│  3. Initializes ragchecker_scorer()                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │    For each sample in dataset:        │
        └───────────────┬───────────────────────┘
                        │
                        ▼
    ┌───────────────────────────────────────────────┐
    │          Solver Chain Execution               │
    │  • Sends question to LLM                      │
    │  • Model generates response                   │
    └───────────────────┬───────────────────────────┘
                        │
                        ▼
    ┌───────────────────────────────────────────────┐
    │         Custom Scorer Invoked                 │
    │  score(state: TaskState, target: Target)      │
    └───────────────────┬───────────────────────────┘
                        │
                        ▼
    ┌───────────────────────────────────────────────┐
    │         RAGChecker Evaluation                 │
    │  (See detailed flow below)                    │
    └───────────────────┬───────────────────────────┘
                        │
                        ▼
    ┌───────────────────────────────────────────────┐
    │         Score Object Returned                 │
    │  • value: F1 score (0-1)                      │
    │  • explanation: "P: X%, R: Y%, F1: Z%"        │
    │  • metadata: {precision, recall, f1}          │
    └───────────────────┬───────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              Inspect AI Records Results                          │
│  • Saves to log file                                            │
│  • Displays in terminal                                         │
│  • Available in inspect view                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed RAGChecker Evaluation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              score() Function Called                             │
│  Input: TaskState (with question and model response)            │
│         Target (with ground truth answer)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  1. Extract Components                           │
│  • question = state.input_text                                  │
│  • model_response = state.output.completion                     │
│  • ground_truth = target.text                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│             2. Format Data for RAGChecker                        │
│  rag_data = {                                                   │
│    "results": [{                                                │
│      "query": question,                                         │
│      "gt_answer": ground_truth,                                 │
│      "response": model_response,                                │
│      "retrieved_context": []                                    │
│    }]                                                           │
│  }                                                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│          3. Initialize RAGChecker Evaluator                      │
│  evaluator = RAGChecker(                                        │
│    extractor_name="openai/gpt-4o-mini",                        │
│    checker_name="openai/gpt-4o-mini"                           │
│  )                                                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              4. RAGChecker Processing                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  STEP A: Claim Extraction (using extractor LLM)       │    │
│  │                                                        │    │
│  │  From Model Response:                                  │    │
│  │    "Paris is the capital of France. It covers         │    │
│  │     105 square kilometers and has 2M people."          │    │
│  │                                                        │    │
│  │  Extract Claims:                                       │    │
│  │    • Claim 1: "Paris is the capital of France"        │    │
│  │    • Claim 2: "Paris covers 105 square kilometers"    │    │
│  │    • Claim 3: "Paris has 2M people"                   │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  STEP B: Claim Extraction (from ground truth)         │    │
│  │                                                        │    │
│  │  From Ground Truth:                                    │    │
│  │    "The capital of France is Paris and it's 105.4     │    │
│  │     square kilometers with a population of 2.1M"       │    │
│  │                                                        │    │
│  │  Extract Claims:                                       │    │
│  │    • GT Claim 1: "Paris is the capital of France"     │    │
│  │    • GT Claim 2: "Paris is 105.4 square kilometers"   │    │
│  │    • GT Claim 3: "Paris has population of 2.1M"       │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  STEP C: Claim Verification (using checker LLM)       │    │
│  │                                                        │    │
│  │  For each claim from model response, check if         │    │
│  │  supported by ground truth:                            │    │
│  │                                                        │    │
│  │  • Claim 1 vs GT Claims → ✅ SUPPORTED                │    │
│  │    (Paris is capital - exact match)                    │    │
│  │                                                        │    │
│  │  • Claim 2 vs GT Claims → ✅ SUPPORTED                │    │
│  │    (105 vs 105.4 km² - close enough)                  │    │
│  │                                                        │    │
│  │  • Claim 3 vs GT Claims → ✅ SUPPORTED                │    │
│  │    (2M vs 2.1M people - close enough)                 │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  STEP D: Calculate Metrics                            │    │
│  │                                                        │    │
│  │  Precision = (Supported claims in response) /          │    │
│  │              (Total claims in response)                │    │
│  │            = 3/3 = 100%                               │    │
│  │                                                        │    │
│  │  Recall = (Supported claims in response) /             │    │
│  │           (Total claims in ground truth)               │    │
│  │         = 3/3 = 100%                                  │    │
│  │                                                        │    │
│  │  F1 = 2 * (P * R) / (P + R)                          │    │
│  │     = 2 * (100 * 100) / (100 + 100) = 100%           │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
└───────────────┴─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                5. Create Score Object                            │
│  Score(                                                         │
│    value = 1.0,  # F1 score (100% converted to 0-1 scale)      │
│    explanation = "Precision: 100%, Recall: 100%, F1: 100%",    │
│    metadata = {                                                 │
│      "precision": 100.0,                                        │
│      "recall": 100.0,                                           │
│      "f1": 100.0                                               │
│    }                                                            │
│  )                                                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                Return to Inspect AI                              │
└─────────────────────────────────────────────────────────────────┘
```

## Example: Lower Score Scenario

```
Model Response: "Paris is the capital of France with 5 million people."
Ground Truth: "Paris is the capital of France and it's 105.4 square 
               kilometers with a population of 2.1 million people."

Extracted Claims (Response):
  1. "Paris is the capital of France"      ✅ Supported
  2. "Paris has 5 million people"          ❌ NOT Supported (wrong number)

Extracted Claims (Ground Truth):
  1. "Paris is the capital of France"
  2. "Paris is 105.4 square kilometers"
  3. "Paris has population of 2.1M"

Verification Results:
  • Response Claim 1: ✅ Matches GT Claim 1
  • Response Claim 2: ❌ Contradicts GT Claim 3 (5M vs 2.1M)
  • GT Claim 2: ❌ Not mentioned in response (area missing)

Metrics:
  Precision = 1/2 = 50%      (1 correct out of 2 claims made)
  Recall    = 1/3 = 33%      (1 covered out of 3 GT claims)
  F1        = 2*(50*33)/(50+33) = 40%

Score: 0.40
Explanation: "Precision: 50.0%, Recall: 33.3%, F1: 40.0%"
```

## Data Flow Diagram

```
┌──────────────┐
│   Sample     │
│  (Dataset)   │
└──────┬───────┘
       │
       │ input="What is the capital of France?"
       │ target="Paris is the capital..."
       ▼
┌──────────────┐
│     LLM      │
│  (via solver)│
└──────┬───────┘
       │
       │ response="Paris is the capital of France..."
       ▼
┌──────────────────────────────────────────┐
│      Custom Scorer                       │
│  ┌────────────────────────────────────┐  │
│  │  Input:                            │  │
│  │    • question                      │  │
│  │    • response                      │  │
│  │    • ground_truth                  │  │
│  └────────┬───────────────────────────┘  │
│           │                              │
│           ▼                              │
│  ┌────────────────────────────────────┐  │
│  │  RAGChecker                        │  │
│  │  ┌──────────┐    ┌──────────────┐ │  │
│  │  │Extractor │ -> │   Checker    │ │  │
│  │  │ (Claims) │    │(Verification)│ │  │
│  │  └──────────┘    └──────────────┘ │  │
│  └────────┬───────────────────────────┘  │
│           │                              │
│           ▼                              │
│  ┌────────────────────────────────────┐  │
│  │  Metrics                           │  │
│  │    • Precision                     │  │
│  │    • Recall                        │  │
│  │    • F1                           │  │
│  └────────┬───────────────────────────┘  │
└───────────┼──────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│          Score Object                    │
│  value: 0.87                            │
│  explanation: "P: 92%, R: 82%, F1: 87%" │
│  metadata: {precision, recall, f1}       │
└──────────────────────────────────────────┘
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Space                                │
│                                                                  │
│  custom_scorer.py         ragchecker_scorer.py                  │
│  ┌──────────────┐        ┌─────────────────────┐               │
│  │ EVAL_SAMPLES │        │ @scorer decorator   │               │
│  │   Sample 1   │        │ def ragchecker_     │               │
│  │   Sample 2   │        │     scorer():        │               │
│  │   Sample 3   │   -->  │   async def score() │               │
│  │              │        │     ...             │               │
│  └──────────────┘        └─────────────────────┘               │
│         │                         │                             │
└─────────┼─────────────────────────┼─────────────────────────────┘
          │                         │
          ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Inspect AI Framework                          │
│  ┌────────────┐   ┌──────────┐   ┌────────────────┐            │
│  │  Dataset   │-->│  Solver  │-->│    Scorer      │            │
│  │  Loader    │   │  Chain   │   │   Pipeline     │            │
│  └────────────┘   └──────────┘   └────────────────┘            │
│                                           │                      │
└───────────────────────────────────────────┼──────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Libraries                            │
│  ┌──────────────────────────────────────────────────────┐       │
│  │                 RAGChecker Library                    │       │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────┐    │       │
│  │  │RAGResults│  │RAGChecker│  │overall_metrics │    │       │
│  │  └──────────┘  └──────────┘  └────────────────┘    │       │
│  └──────────────────────────────────────────────────────┘       │
│                          │                                       │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────┐       │
│  │                  LiteLLM / OpenAI                     │       │
│  │  • Model access (gpt-4o-mini)                        │       │
│  │  • Claim extraction                                  │       │
│  │  • Claim verification                                │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Evaluation Timeline

```
Time ->

0s     User runs: inspect eval ...
       │
1s     Inspect AI loads task
       │
2s     Dataset loaded (3 samples)
       │
       ├─ Sample 1: "What is the capital of France?"
3s     │  Model generates response: "Paris is the capital..."
       │
4s     │  Scorer extracts claims from response
       │
5s     │  Scorer extracts claims from ground truth  
       │
6s     │  Scorer verifies claims
       │
7s     │  Score computed: P=92%, R=82%, F1=87%
       │  ✅ Sample 1 complete
       │
       ├─ Sample 2: "When was the US founded?"
8s     │  Model generates response
       │
9s     │  Claim extraction (response + GT)
       │
10s    │  Claim verification
       │
11s    │  Score computed: P=95%, R=88%, F1=91%
       │  ✅ Sample 2 complete
       │
       ├─ Sample 3: "When was the airplane invented?"
12s    │  Model generates response
       │
13s    │  Claim extraction
       │
14s    │  Claim verification
       │
15s    │  Score computed: P=88%, R=90%, F1=89%
       │  ✅ Sample 3 complete
       │
16s    All samples complete
       │
17s    Aggregate metrics calculated
       │
18s    Results saved to log file
       │
19s    Terminal output displayed
       │
       User runs: inspect view
```

## Summary

The evaluation flow can be summarized as:

1. **Load**: Task and dataset loaded by Inspect AI
2. **Generate**: LLM generates response for each question
3. **Extract**: RAGChecker extracts claims from response and ground truth
4. **Verify**: RAGChecker checks which claims are supported
5. **Compute**: Precision, recall, and F1 calculated
6. **Return**: Score object with metrics returned to Inspect AI
7. **Store**: Results saved and displayed

**Key insight**: RAGChecker performs semantic, claim-level evaluation rather than simple string matching, providing more nuanced and accurate scoring.

