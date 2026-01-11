"""Core extraction engine components."""

from newsdigest.core.article import Article, SourceType
from newsdigest.core.result import (
    ExtractionResult,
    ExtractionStatistics,
    Claim,
    ClaimType,
    RemovedContent,
    RemovalReason,
    Sentence,
    SentenceCategory,
)
from newsdigest.core.extractor import Extractor

__all__ = [
    "Article",
    "SourceType",
    "ExtractionResult",
    "ExtractionStatistics",
    "Claim",
    "ClaimType",
    "RemovedContent",
    "RemovalReason",
    "Sentence",
    "SentenceCategory",
    "Extractor",
]
