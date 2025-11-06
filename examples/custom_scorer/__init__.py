"""Custom Scorer Example - RAGChecker-based evaluation.

This package demonstrates how to create and use custom scorers in Inspect AI
using RAGChecker for fine-grained evaluation of model responses.
"""

from .custom_scorer import custom_scorer
from .ragchecker_scorer import ragchecker_scorer

__all__ = ["custom_scorer", "ragchecker_scorer"]

