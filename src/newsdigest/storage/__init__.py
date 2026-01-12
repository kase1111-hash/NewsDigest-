"""Data persistence for NewsDigest."""

from newsdigest.storage.analytics import (
    AggregateStats,
    AnalyticsStore,
    ExtractionRecord,
    SourceStore,
)
from newsdigest.storage.base import BaseStorage, SyncStorage
from newsdigest.storage.cache import (
    CacheEntry,
    FileCache,
    MemoryCache,
    cache_key_for_text,
    cache_key_for_url,
)

__all__ = [
    # Base
    "BaseStorage",
    "SyncStorage",
    # Cache
    "CacheEntry",
    "FileCache",
    "MemoryCache",
    "cache_key_for_text",
    "cache_key_for_url",
    # Analytics
    "AggregateStats",
    "AnalyticsStore",
    "ExtractionRecord",
    "SourceStore",
]
