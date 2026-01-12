"""
NewsDigest - Semantic compression engine for news.

Your 4-hour news habit, compressed to 5 minutes of actual information.
"""

from newsdigest.config.settings import Config
from newsdigest.core.article import Article
from newsdigest.core.extractor import Extractor
from newsdigest.core.result import ExtractionResult
from newsdigest.digest.generator import DigestGenerator
from newsdigest.exceptions import (
    AnalysisError,
    ClusteringError,
    ConfigurationError,
    ContentExtractionError,
    DeduplicationError,
    DigestError,
    ExtractionError,
    FetchError,
    FormatterError,
    IngestError,
    InvalidConfigError,
    NewsDigestError,
    ParseError,
    PipelineError,
    RateLimitError,
)
from newsdigest.version import __version__


__all__ = [
    # Version
    "__version__",
    # Core classes
    "Extractor",
    "Article",
    "ExtractionResult",
    "DigestGenerator",
    "Config",
    # Exceptions
    "NewsDigestError",
    "ConfigurationError",
    "InvalidConfigError",
    "ExtractionError",
    "ContentExtractionError",
    "AnalysisError",
    "PipelineError",
    "IngestError",
    "FetchError",
    "ParseError",
    "RateLimitError",
    "FormatterError",
    "DigestError",
    "ClusteringError",
    "DeduplicationError",
]
