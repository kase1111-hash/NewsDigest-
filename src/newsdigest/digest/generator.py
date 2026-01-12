"""Digest generation for NewsDigest."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from newsdigest.config.settings import Config
from newsdigest.core.extractor import Extractor
from newsdigest.core.result import ExtractionResult
from newsdigest.digest.clustering import TopicClusterer
from newsdigest.digest.dedup import Deduplicator
from newsdigest.formatters import JSONFormatter, MarkdownFormatter, TextFormatter
from newsdigest.ingestors import RSSParser


@dataclass
class DigestItem:
    """A single item in a digest."""

    id: str
    summary: str
    article_count: int = 1
    sources: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    topic: str | None = None
    subtopic: str | None = None
    earliest: datetime | None = None
    latest: datetime | None = None
    original_words: int = 0
    compressed_words: int = 0


@dataclass
class DigestTopic:
    """A topic cluster in a digest."""

    name: str
    emoji: str = ""
    items: list[DigestItem] = field(default_factory=list)


@dataclass
class Digest:
    """Complete digest output."""

    generated_at: datetime = field(default_factory=datetime.utcnow)
    period: str = "24h"
    topics: list[DigestTopic] = field(default_factory=list)
    sources_processed: int = 0
    articles_analyzed: int = 0
    total_original_words: int = 0
    total_compressed_words: int = 0
    emotional_removed: int = 0
    unnamed_sources_flagged: int = 0
    speculation_stripped: int = 0
    duplicates_collapsed: int = 0


class DigestGenerator:
    """Generates daily/periodic digests from multiple sources.

    The generator:
    1. Fetches articles from configured sources (RSS, NewsAPI)
    2. Extracts content from each article
    3. Deduplicates across sources
    4. Clusters by topic
    5. Merges related items
    6. Formats output
    """

    def __init__(self, config: Config | None = None) -> None:
        """Initialize digest generator.

        Args:
            config: Configuration object.
        """
        self.config = config or Config()
        self._sources: list[dict] = []

        # Initialize components
        self._extractor = Extractor(config)
        self._rss_parser = RSSParser({"fetch_full_content": True})
        self._clusterer = TopicClusterer()
        self._deduplicator = Deduplicator(
            {"similarity_threshold": self.config.digest.similarity_threshold}
        )

        # Initialize formatters
        self._formatters = {
            "markdown": MarkdownFormatter(),
            "json": JSONFormatter(),
            "text": TextFormatter(),
        }

    def add_rss(
        self,
        url: str,
        name: str | None = None,
        category: str | None = None,
    ) -> None:
        """Add RSS feed to digest sources.

        Args:
            url: RSS feed URL.
            name: Display name for source.
            category: Category for clustering.
        """
        self._sources.append({
            "type": "rss",
            "url": url,
            "name": name or url,
            "category": category,
        })

    def add_newsapi(self, query: str, **kwargs: Any) -> None:
        """Add NewsAPI search to digest sources.

        Args:
            query: Search query.
            **kwargs: Additional NewsAPI parameters.
        """
        self._sources.append({
            "type": "newsapi",
            "query": query,
            **kwargs,
        })

    def add_url(self, url: str, name: str | None = None) -> None:
        """Add single URL to digest sources.

        Args:
            url: Article URL.
            name: Display name.
        """
        self._sources.append({
            "type": "url",
            "url": url,
            "name": name,
        })

    async def generate_async(
        self,
        period: str = "24h",
        format: str = "markdown",
    ) -> str | Digest:
        """Generate digest for specified period (async).

        Args:
            period: Time period (e.g., '24h', '7d').
            format: Output format ('markdown', 'json', 'text', 'dict').

        Returns:
            Formatted string or Digest object if format='dict'.
        """
        # Parse period
        since = self._parse_period(period)

        # Fetch articles from all sources
        all_articles = await self._fetch_all_sources(since)

        # Extract content from each article
        extraction_results = await self._extract_all(all_articles)

        # Deduplicate
        original_count = len(extraction_results)
        extraction_results = self._deduplicator.deduplicate(extraction_results)
        duplicates_removed = original_count - len(extraction_results)

        # Cluster by topic
        clusters = self._clusterer.cluster(extraction_results)

        # Build digest
        digest = self._build_digest(
            clusters,
            extraction_results,
            period,
            duplicates_removed,
        )

        # Format output
        if format == "dict":
            return digest

        formatter = self._formatters.get(format.lower())
        if not formatter:
            raise ValueError(f"Unknown format: {format}")

        return formatter.format_digest(digest)

    def generate(
        self,
        period: str = "24h",
        format: str = "markdown",
    ) -> str | Digest:
        """Generate digest for specified period (sync).

        Args:
            period: Time period (e.g., '24h', '7d').
            format: Output format ('markdown', 'json', 'text', 'dict').

        Returns:
            Formatted string or Digest object if format='dict'.
        """
        return asyncio.run(self.generate_async(period, format))

    async def _fetch_all_sources(
        self, since: datetime | None
    ) -> list[dict[str, Any]]:
        """Fetch articles from all configured sources.

        Args:
            since: Only fetch articles after this time.

        Returns:
            List of article dictionaries with source info.
        """
        all_articles = []

        for source in self._sources:
            source_type = source.get("type")

            if source_type == "rss":
                try:
                    if since:
                        articles = await self._rss_parser.get_new_items(
                            source["url"], since
                        )
                    else:
                        articles = await self._rss_parser.parse(source["url"])

                    for article in articles:
                        all_articles.append({
                            "article": article,
                            "source_name": source.get("name"),
                            "category": source.get("category"),
                        })
                except Exception:
                    # Skip failed sources
                    continue

            elif source_type == "url":
                # Single URL
                all_articles.append({
                    "url": source["url"],
                    "source_name": source.get("name"),
                })

        return all_articles

    async def _extract_all(
        self, articles: list[dict[str, Any]]
    ) -> list[ExtractionResult]:
        """Extract content from all articles.

        Args:
            articles: Article dictionaries.

        Returns:
            List of extraction results.
        """
        results = []

        for article_info in articles:
            try:
                if "article" in article_info:
                    # Already have Article object from RSS
                    article = article_info["article"]
                    result = self._extractor._process_article(article)
                elif "url" in article_info:
                    # Need to fetch URL
                    result = await self._extractor.extract(article_info["url"])
                else:
                    continue

                results.append(result)
            except Exception:
                # Skip failed extractions
                continue

        return results

    def _parse_period(self, period: str) -> datetime | None:
        """Parse period string to datetime.

        Args:
            period: Period string like '24h', '7d'.

        Returns:
            Datetime for start of period.
        """
        now = datetime.utcnow()

        # Parse period
        if period.endswith("h"):
            hours = int(period[:-1])
            return now - timedelta(hours=hours)
        elif period.endswith("d"):
            days = int(period[:-1])
            return now - timedelta(days=days)
        elif period.endswith("w"):
            weeks = int(period[:-1])
            return now - timedelta(weeks=weeks)

        return None

    def _build_digest(
        self,
        clusters: dict[str, list[ExtractionResult]],
        all_results: list[ExtractionResult],
        period: str,
        duplicates_removed: int,
    ) -> Digest:
        """Build Digest object from clusters.

        Args:
            clusters: Topic clusters.
            all_results: All extraction results.
            period: Time period string.
            duplicates_removed: Number of duplicates removed.

        Returns:
            Digest object.
        """
        topics = []

        for topic_name, articles in clusters.items():
            name, emoji = self._clusterer.get_topic_info(topic_name)

            items = []
            for article in articles:
                item = DigestItem(
                    id=article.id,
                    summary=article.text[:500] if article.text else "",
                    article_count=1,
                    sources=[article.source] if article.source else [],
                    urls=[article.url] if article.url else [],
                    topic=topic_name,
                    earliest=article.published_at,
                    latest=article.published_at,
                    original_words=article.statistics.original_words,
                    compressed_words=article.statistics.compressed_words,
                )
                items.append(item)

            topics.append(DigestTopic(name=name, emoji=emoji, items=items))

        # Sort topics by item count
        topics.sort(key=lambda t: len(t.items), reverse=True)

        # Calculate aggregate stats
        total_original = sum(r.statistics.original_words for r in all_results)
        total_compressed = sum(r.statistics.compressed_words for r in all_results)
        emotional = sum(r.statistics.emotional_words_removed for r in all_results)
        speculation = sum(r.statistics.speculation_removed for r in all_results)
        unnamed = sum(r.statistics.unnamed_sources for r in all_results)

        return Digest(
            period=period,
            topics=topics,
            sources_processed=len(self._sources),
            articles_analyzed=len(all_results),
            total_original_words=total_original,
            total_compressed_words=total_compressed,
            emotional_removed=emotional,
            unnamed_sources_flagged=unnamed,
            speculation_stripped=speculation,
            duplicates_collapsed=duplicates_removed,
        )

    def clear_sources(self) -> None:
        """Clear all configured sources."""
        self._sources = []

    def get_sources(self) -> list[dict]:
        """Get list of configured sources.

        Returns:
            List of source dictionaries.
        """
        return self._sources.copy()
