"""Semantic analysis modules for NewsDigest."""

from newsdigest.analyzers.base import BaseAnalyzer

__all__ = [
    "BaseAnalyzer",
    # Analyzers will be exported as implemented:
    # "FillerDetector",
    # "SpeculationStripper",
    # "EmotionalDetector",
    # "SourceValidator",
    # "RepetitionCollapser",
    # "NoveltyScorer",
    # "ClaimExtractor",
    # "QuoteIsolator",
]
