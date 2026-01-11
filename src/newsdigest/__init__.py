"""
NewsDigest - Semantic compression engine for news.

Your 4-hour news habit, compressed to 5 minutes of actual information.
"""

from newsdigest.version import __version__
from newsdigest.core.extractor import Extractor
from newsdigest.core.article import Article
from newsdigest.core.result import ExtractionResult
from newsdigest.digest.generator import DigestGenerator
from newsdigest.config.settings import Config

__all__ = [
    "__version__",
    "Extractor",
    "Article",
    "ExtractionResult",
    "DigestGenerator",
    "Config",
]
