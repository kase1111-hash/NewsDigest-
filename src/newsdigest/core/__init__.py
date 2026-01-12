"""Core extraction engine components."""

from newsdigest.core.article import Article, SourceType
from newsdigest.core.extractor import Extractor
from newsdigest.core.result import (
    Claim,
    ClaimType,
    ExtractionResult,
    ExtractionStatistics,
    RemovalReason,
    RemovedContent,
    Sentence,
    SentenceCategory,
)


__all__ = [
    "Article",
    "Claim",
    "ClaimType",
    "ExtractionResult",
    "ExtractionStatistics",
    "Extractor",
    "RemovalReason",
    "RemovedContent",
    "Sentence",
    "SentenceCategory",
    "SourceType",
]
