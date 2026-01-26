"""URL fetcher for NewsDigest."""

import asyncio
from urllib.parse import urlparse

import httpx

from newsdigest.core.article import Article, SourceType
from newsdigest.ingestors.base import BaseIngestor
from newsdigest.parsers.article import ArticleExtractor
from newsdigest.utils.validation import (
    sanitize_html,
    validate_url_strict,
)


class URLFetcher(BaseIngestor):
    """Fetches article content from URLs.

    Features:
    - Async HTTP with httpx
    - Automatic redirect handling
    - User-agent rotation
    - Rate limiting per domain
    - Timeout handling
    - Retry with exponential backoff
    - Input URL validation
    - HTML sanitization
    """

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (compatible; NewsDigest/0.1; +https://github.com/newsdigest)"
    )

    def __init__(self, config: dict | None = None) -> None:
        """Initialize URL fetcher.

        Args:
            config: Configuration dictionary.
        """
        super().__init__(config)
        self.timeout = self.config.get("timeout", 30)
        self.retries = self.config.get("retries", 3)
        self.user_agent = self.config.get("user_agent", self.DEFAULT_USER_AGENT)
        self.requests_per_second = self.config.get("requests_per_second", 1.0)

        self._article_extractor = ArticleExtractor(config)
        self._domain_last_request: dict[str, float] = {}
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client (connection pooling)."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={"User-Agent": self.user_agent},
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "URLFetcher":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.close()

    async def ingest(self, source: str) -> Article:
        """Fetch and parse article from URL.

        Args:
            source: URL to fetch.

        Returns:
            Article object with content and metadata.

        Raises:
            ValidationError: If URL is invalid.
            httpx.HTTPError: If fetch fails after retries.
        """
        # Validate URL before fetching
        validated_url = validate_url_strict(source)

        html = await self._fetch_with_retry(validated_url)

        # Sanitize HTML before parsing
        html = sanitize_html(html)

        article = self._article_extractor.extract(html, validated_url)
        article.source_type = SourceType.URL
        return article

    async def ingest_batch(
        self,
        sources: list[str],
        max_concurrent: int = 5,
    ) -> list[Article]:
        """Fetch multiple URLs concurrently.

        Args:
            sources: List of URLs to fetch.
            max_concurrent: Maximum concurrent requests.

        Returns:
            List of Article objects (failed fetches excluded).
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_one(url: str) -> Article | None:
            async with semaphore:
                try:
                    return await self.ingest(url)
                except Exception:
                    return None

        tasks = [fetch_one(url) for url in sources]
        results = await asyncio.gather(*tasks)

        return [a for a in results if a is not None]

    async def _fetch_with_retry(self, url: str) -> str:
        """Fetch URL with retry logic.

        Args:
            url: URL to fetch.

        Returns:
            HTML content.

        Raises:
            httpx.HTTPError: If all retries fail.
        """
        # Rate limiting per domain
        await self._rate_limit(url)

        last_error = None
        client = await self._get_client()
        for attempt in range(self.retries):
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.text

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429:
                    # Rate limited, wait longer
                    await asyncio.sleep(2 ** (attempt + 2))
                elif e.response.status_code >= 500:
                    # Server error, retry
                    await asyncio.sleep(2**attempt)
                else:
                    # Client error, don't retry
                    raise

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_error = e
                await asyncio.sleep(2**attempt)

        raise last_error or httpx.HTTPError(f"Failed to fetch {url}")

    async def _rate_limit(self, url: str) -> None:
        """Apply rate limiting for domain.

        Args:
            url: URL being fetched.
        """
        if self.requests_per_second <= 0:
            return

        domain = urlparse(url).netloc
        import time

        current_time = time.time()
        min_interval = 1.0 / self.requests_per_second

        if domain in self._domain_last_request:
            elapsed = current_time - self._domain_last_request[domain]
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)

        self._domain_last_request[domain] = time.time()

    async def fetch_raw(self, url: str) -> str:
        """Fetch raw HTML without parsing.

        Args:
            url: URL to fetch.

        Returns:
            Raw HTML content.
        """
        return await self._fetch_with_retry(url)
