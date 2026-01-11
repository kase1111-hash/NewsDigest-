"""Result data structures for NewsDigest extraction."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class SentenceCategory(Enum):
    """Category of a sentence based on analysis."""

    FACTUAL = "factual"
    SPECULATION = "speculation"
    EMOTIONAL = "emotional"
    BACKGROUND = "background"
    QUOTE = "quote"
    FILLER = "filler"
    ENGAGEMENT_HOOK = "engagement_hook"


class ClaimType(Enum):
    """Type of extracted claim."""

    FACTUAL = "factual"
    STATISTICAL = "statistical"
    QUOTE = "quote"
    ATTRIBUTION = "attribution"


class RemovalReason(Enum):
    """Reason for removing content during extraction."""

    EMOTIONAL_ACTIVATION = "EMOTIONAL_ACTIVATION"
    SPECULATION = "SPECULATION"
    UNNAMED_SOURCE = "UNNAMED_SOURCE"
    BACKGROUND_REPEAT = "BACKGROUND_REPEAT"
    CIRCULAR_QUOTE = "CIRCULAR_QUOTE"
    HEDGE_PADDING = "HEDGE_PADDING"
    ENGAGEMENT_HOOK = "ENGAGEMENT_HOOK"
    LOW_DENSITY = "LOW_DENSITY"


@dataclass
class Sentence:
    """Represents an analyzed sentence."""

    text: str
    index: int

    # NLP data
    tokens: List[str] = field(default_factory=list)
    pos_tags: List[str] = field(default_factory=list)
    entities: List[dict] = field(default_factory=list)

    # Analysis scores (0.0 - 1.0)
    density_score: float = 0.0
    novelty_score: float = 0.0
    speculation_score: float = 0.0
    emotional_score: float = 0.0

    # Classification
    category: SentenceCategory = SentenceCategory.FACTUAL
    keep: bool = True
    removal_reason: Optional[str] = None

    # Source attribution
    has_named_source: bool = False
    has_unnamed_source: bool = False
    source_name: Optional[str] = None


@dataclass
class Claim:
    """Represents an extracted falsifiable claim."""

    text: str
    claim_type: ClaimType

    # Attribution
    source: Optional[str] = None
    source_type: str = "unknown"

    # Confidence (0.0 - 1.0)
    confidence: float = 0.0

    # Position
    sentence_index: int = 0


@dataclass
class RemovedContent:
    """Represents content that was removed during extraction."""

    text: str
    reason: RemovalReason
    sentence_index: int
    original_length: int = 0

    # For hedge padding - the compressed version
    compressed_version: Optional[str] = None


@dataclass
class ExtractionStatistics:
    """Statistics about the extraction process."""

    original_words: int = 0
    compressed_words: int = 0
    compression_ratio: float = 0.0
    original_density: float = 0.0
    compressed_density: float = 0.0

    # Breakdown
    novel_claims: int = 0
    background_removed: int = 0
    speculation_removed: int = 0
    repetition_collapsed: int = 0
    emotional_words_removed: int = 0
    unnamed_sources: int = 0
    named_sources: int = 0


@dataclass
class ExtractionResult:
    """Complete result of article extraction."""

    # Identifiers
    id: str
    url: Optional[str] = None

    # Article metadata
    title: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    processed_at: datetime = field(default_factory=datetime.utcnow)

    # Extracted content
    text: str = ""
    claims: List[Claim] = field(default_factory=list)

    # Named sources found
    sources_named: List[str] = field(default_factory=list)

    # Warnings (kept but flagged)
    warnings: List[dict] = field(default_factory=list)

    # Removed content
    removed: List[RemovedContent] = field(default_factory=list)

    # Statistics
    statistics: ExtractionStatistics = field(default_factory=ExtractionStatistics)

    # Original for comparison mode
    original_text: Optional[str] = None
    sentences: List[Sentence] = field(default_factory=list)
