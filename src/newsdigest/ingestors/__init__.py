"""Input source handlers for NewsDigest."""

from newsdigest.ingestors.base import BaseIngestor
from newsdigest.ingestors.rss import RSSParser
from newsdigest.ingestors.text import TextIngestor
from newsdigest.ingestors.url import URLFetcher


__all__ = [
    "BaseIngestor",
    "RSSParser",
    "TextIngestor",
    "URLFetcher",
    # Future ingestors:
    # "NewsAPIClient",
    # "EmailIngester",
    # "TwitterClient",
    # "PDFParser",
]
