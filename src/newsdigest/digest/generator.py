"""Digest generation for NewsDigest."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Union

from newsdigest.config.settings import Config


@dataclass
class DigestItem:
    """A single item in a digest."""

    id: str
    summary: str
    article_count: int = 1
    sources: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    earliest: Optional[datetime] = None
    latest: Optional[datetime] = None
    original_words: int = 0
    compressed_words: int = 0


@dataclass
class DigestTopic:
    """A topic cluster in a digest."""

    name: str
    emoji: str = ""
    items: List[DigestItem] = field(default_factory=list)


@dataclass
class Digest:
    """Complete digest output."""

    generated_at: datetime = field(default_factory=datetime.utcnow)
    period: str = "24h"
    topics: List[DigestTopic] = field(default_factory=list)
    sources_processed: int = 0
    articles_analyzed: int = 0
    total_original_words: int = 0
    total_compressed_words: int = 0
    emotional_removed: int = 0
    unnamed_sources_flagged: int = 0
    speculation_stripped: int = 0
    duplicates_collapsed: int = 0


class DigestGenerator:
    """Generates daily/periodic digests from multiple sources."""

    def __init__(self, config: Optional[Config] = None) -> None:
        """
        Initialize digest generator.

        Args:
            config: Configuration object.
        """
        self.config = config or Config()
        self._sources: List[dict] = []

    def add_rss(self, url: str, name: Optional[str] = None) -> None:
        """Add RSS feed to digest sources."""
        self._sources.append({
            "type": "rss",
            "url": url,
            "name": name or url,
        })

    def add_newsapi(self, query: str, **kwargs) -> None:
        """Add NewsAPI search to digest sources."""
        self._sources.append({
            "type": "newsapi",
            "query": query,
            **kwargs,
        })

    def generate(
        self,
        period: str = "24h",
        format: str = "markdown",
    ) -> Union[str, Digest]:
        """
        Generate digest for specified period.

        Args:
            period: Time period (e.g., '24h', '7d').
            format: Output format ('markdown', 'json', 'html', 'dict').

        Returns:
            Formatted string or Digest object if format='dict'.
        """
        # Implementation will be added in enhanced analysis phase
        raise NotImplementedError("Digest generation not yet implemented")
