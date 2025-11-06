"""Custom Scorer Example - Using RAGChecker for Evaluation.

This example demonstrates how to create a custom scorer in Inspect AI that uses
RAGChecker to evaluate model responses. RAGChecker provides fine-grained metrics
including precision, recall, and F1 scores by performing claim-level analysis.
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.solver import generate

from examples.custom_scorer.ragchecker_scorer import ragchecker_scorer

# Define the evaluation dataset with 3 sample questions
EVAL_SAMPLES = [
    Sample(
        id="france_capital",
        input="What is the capital of France and how big is it?",
        target=(
            "The capital of France is Paris and it's 105.4 square kilometers "
            "with a population of approximately 2.1 million people in the city proper."
        ),
    ),
    Sample(
        id="us_founding",
        input="When was the United States founded as a state and how many states did it originally have?",
        target=(
            "The United States declared independence on July 4, 1776, and was formally "
            "recognized as a sovereign nation with the Treaty of Paris in 1783. "
            "It originally consisted of 13 states: Delaware, Pennsylvania, New Jersey, "
            "Georgia, Connecticut, Massachusetts, Maryland, South Carolina, New Hampshire, "
            "Virginia, New York, North Carolina, and Rhode Island."
        ),
    ),
    Sample(
        id="airplane_invention",
        input="When was the airplane invented, by whom, and where?",
        target=(
            "The airplane was invented by the Wright brothers, Orville and Wilbur Wright, "
            "on December 17, 1903. The first successful powered flight took place at "
            "Kitty Hawk, North Carolina, USA. Their aircraft, the Wright Flyer, achieved "
            "the first controlled, sustained flight of a powered, heavier-than-air aircraft."
        ),
    ),
]


@task
def custom_scorer(
    extractor_model: str = "openai/gpt-4o-mini",
    checker_model: str = "openai/gpt-4o-mini"
):
    """Evaluate LLMs using RAGChecker-based custom scorer.
    
    This task demonstrates how to use a custom scorer that leverages RAGChecker
    to compute precision, recall, and F1 scores. The scorer performs fine-grained
    claim-level evaluation to assess:
    
    - **Precision**: How much of the model's response is correct (no hallucinations)
    - **Recall**: How much of the ground truth is covered by the model's response
    - **F1**: Harmonic mean of precision and recall
    
    The task includes 3 factual questions covering:
    1. Geography and demographics (Paris)
    2. Historical events (US founding)
    3. Invention history (airplane)
    
    Args:
        extractor_model: Model to use for RAGChecker's claim extraction phase.
            Defaults to "openai/gpt-4o-mini". This model breaks down responses
            and ground truth into individual claims for comparison.
        checker_model: Model to use for RAGChecker's claim verification phase.
            Defaults to "openai/gpt-4o-mini". This model verifies whether
            extracted claims are supported or contradicted.
    
    Requirements:
    - OpenAI API key set in environment (OPENAI_API_KEY)
    - RAGChecker package installed (pip install ragchecker)
    - Python spaCy English model (python -m spacy download en_core_web_sm)
    
    Returns:
        Task: An Inspect AI task configured with RAGChecker scoring.
        
    Examples:
        Run with default models (gpt-4o-mini for both):
        ```bash
        inspect eval examples/custom_scorer/custom_scorer.py --model openai/gpt-4o-mini
        ```
        
        Run with custom scorer models via task parameters:
        ```bash
        inspect eval examples/custom_scorer/custom_scorer.py \
            --model openai/gpt-4o-mini \
            -T extractor_model=openai/gpt-4o \
            -T checker_model=openai/gpt-4o
        ```
        
        Use different models for extraction vs checking (cost optimization):
        ```bash
        inspect eval examples/custom_scorer/custom_scorer.py \
            --model openai/gpt-4o \
            -T extractor_model=openai/gpt-4o-mini \
            -T checker_model=openai/gpt-4o
        ```
    """
    return Task(
        dataset=EVAL_SAMPLES,
        solver=[generate()],
        scorer=ragchecker_scorer(
            extractor_model=extractor_model,
            checker_model=checker_model
        ),
    )

