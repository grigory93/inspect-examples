"""RAGChecker-based custom scorer for Inspect AI.

This module implements a custom scorer that uses RAGChecker to evaluate
precision, recall, and F1 scores for model responses based on ground truth targets.
"""

from inspect_ai.scorer import Score, Scorer, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState


@scorer(
    metrics={
        "*": [mean(), stderr()], 
    }
)
def ragchecker_scorer(
    extractor_model: str = "openai/gpt-4o-mini",
    checker_model: str = "openai/gpt-4o-mini"
) -> Scorer:
    """Create a RAGChecker-based scorer for evaluating model responses.
    
    This scorer uses RAGChecker to compute precision, recall, and F1 scores
    by comparing model responses against ground truth targets. RAGChecker
    performs fine-grained claim-level evaluation to determine how accurate
    and complete the model's responses are.
    
    Args:
        extractor_model: Model name to use for RAGChecker's claim extraction.
            Defaults to "openai/gpt-4o-mini". This model breaks down responses
            and ground truth into individual claims for comparison.
        checker_model: Model name to use for RAGChecker's claim verification.
            Defaults to "openai/gpt-4o-mini". This model verifies whether
            extracted claims are supported or contradicted.
            
    Both parameters accept any model supported by LiteLLM, including:
    - OpenAI: "openai/gpt-4o", "openai/gpt-4o-mini", "openai/gpt-4-turbo"
    - Anthropic: "anthropic/claude-3-5-sonnet-20241022", "anthropic/claude-3-opus-20240229"
    - Other providers supported by LiteLLM
    
    The scorer requires:
    - OpenAI API access (via OPENAI_API_KEY environment variable)
    - RAGChecker package installed
    - LiteLLM for model access
    
    Returns:
        Scorer: A scorer function that computes RAGChecker metrics.
        
    Examples:
        Using default models (gpt-4o-mini for both):
        ```python
        scorer=ragchecker_scorer()
        ```
        
        Using same model for both extraction and checking:
        ```python
        scorer=ragchecker_scorer(
            extractor_model="openai/gpt-4o",
            checker_model="openai/gpt-4o"
        )
        ```
        
        Using different models (e.g., fast extraction, accurate checking):
        ```python
        scorer=ragchecker_scorer(
            extractor_model="openai/gpt-4o-mini",
            checker_model="openai/gpt-4o"
        )
        ```
        
        Complete task example:
        ```python
        from inspect_ai import Task, task
        from inspect_ai.dataset import Sample
        from inspect_ai.solver import generate
        from ragchecker_scorer import ragchecker_scorer
        
        @task
        def my_task():
            return Task(
                dataset=[
                    Sample(
                        input="What is the capital of France?",
                        target="The capital of France is Paris."
                    )
                ],
                solver=[generate()],
                scorer=ragchecker_scorer(
                    extractor_model="openai/gpt-4o",
                    checker_model="openai/gpt-4o"
                )
            )
        ```
    """
    
    async def score(state: TaskState, target: Target) -> Score:
        """Score a model response using RAGChecker metrics.
        
        Args:
            state: The current task state containing the model's response.
            target: The target/ground truth answer.
            
        Returns:
            Score: A score object containing precision, recall, and F1 metrics.
        """
        # Import RAGChecker (lazy import to avoid errors if not installed)
        try:
            from ragchecker import RAGResults, RAGChecker
            from ragchecker.metrics import overall_metrics
        except ImportError:
            return Score(
                value="E",
                explanation="RAGChecker not installed. Run: pip install ragchecker",
            )
        
        # Extract the necessary components
        question = state.input_text
        model_response = state.output.completion
        ground_truth = target.text
        
        # Handle cases where response or target is missing
        if not model_response or not ground_truth:
            return Score(
                value="E",
                explanation="Missing model response or ground truth target",
            )
        
        try:
            # Prepare data in RAGChecker format
            # RAGChecker expects a specific JSON structure
            rag_data = {
                "results": [
                    {
                        "query_id": state.sample_id or "sample_1",
                        "query": question,
                        "gt_answer": ground_truth,
                        "response": model_response,
                        "retrieved_context": []  # Not using retrieval context
                    }
                ]
            }
            
            # Initialize RAGResults from the data
            import json
            rag_results = RAGResults.from_json(json.dumps(rag_data))
            
            # Set up the RAGChecker evaluator
            # Using specified models for extraction and checking
            evaluator = RAGChecker(
                extractor_name=extractor_model,
                checker_name=checker_model,
                batch_size_extractor=1,
                batch_size_checker=1
            )
            
            # Evaluate with overall metrics (precision, recall, F1)
            evaluator.evaluate(rag_results, overall_metrics)
            
            # Extract the metrics
            metrics = rag_results.metrics
            precision = metrics.get("overall_metrics", {}).get("precision", 0.0)
            recall = metrics.get("overall_metrics", {}).get("recall", 0.0)
            f1 = metrics.get("overall_metrics", {}).get("f1", 0.0)
            
            return Score(
                value={
                    "precision": precision / 100.0,
                    "recall": recall / 100.0,
                    "f1": f1 / 100.0,
                },
                answer=model_response,
            )
            
        except Exception as e:
            return Score(
                value="E",
                explanation=f"Error during RAGChecker evaluation: {str(e)}",
            )
    
    return score

