"""Semantic analysis modules for NewsDigest."""

from newsdigest.analyzers.base import BaseAnalyzer
from newsdigest.analyzers.claims import ClaimExtractor
from newsdigest.analyzers.emotional import EmotionalDetector
from newsdigest.analyzers.filler import FillerDetector
from newsdigest.analyzers.novelty import NoveltyScorer
from newsdigest.analyzers.quotes import QuoteIsolator
from newsdigest.analyzers.repetition import RepetitionCollapser
from newsdigest.analyzers.sources import SourceValidator
from newsdigest.analyzers.speculation import SpeculationStripper


__all__ = [
    "BaseAnalyzer",
    "ClaimExtractor",
    "EmotionalDetector",
    "FillerDetector",
    "NoveltyScorer",
    "QuoteIsolator",
    "RepetitionCollapser",
    "SourceValidator",
    "SpeculationStripper",
]
