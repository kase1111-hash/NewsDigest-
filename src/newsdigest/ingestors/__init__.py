"""Input source handlers for NewsDigest."""

from newsdigest.ingestors.base import BaseIngestor

__all__ = [
    "BaseIngestor",
    # Ingestors will be exported as implemented:
    # "URLFetcher",
    # "RSSParser",
    # "NewsAPIClient",
    # "EmailIngester",
    # "TwitterClient",
    # "PDFParser",
]
