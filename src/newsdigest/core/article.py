"""Article data structures for NewsDigest."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class SourceType(Enum):
    """Type of content source."""

    URL = "url"
    RSS = "rss"
    NEWSAPI = "newsapi"
    EMAIL = "email"
    TWITTER = "twitter"
    PDF = "pdf"
    TEXT = "text"  # Direct text input


@dataclass
class Article:
    """Represents a parsed news article."""

    # Required fields
    id: str
    content: str

    # Metadata
    url: Optional[str] = None
    title: Optional[str] = None
    source_name: Optional[str] = None
    source_type: SourceType = SourceType.URL
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    fetched_at: datetime = field(default_factory=datetime.utcnow)

    # Computed fields
    word_count: int = 0
    language: str = "en"

    def __post_init__(self) -> None:
        """Compute word count after initialization."""
        if self.word_count == 0 and self.content:
            self.word_count = len(self.content.split())
