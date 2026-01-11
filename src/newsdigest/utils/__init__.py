"""Utility modules for NewsDigest."""

from newsdigest.utils.http import (
    HTTPClient,
    RateLimiter,
    RetryConfig,
    fetch_url,
    get_shared_client,
)
from newsdigest.utils.text import (
    STOP_WORDS,
    calculate_word_overlap,
    compile_patterns,
    extract_quoted_content,
    find_all_matches,
    fix_punctuation_spacing,
    get_content_words,
    has_excessive_punctuation,
    has_meaningful_content,
    has_numbers,
    has_quote,
    is_all_caps,
    match_any_pattern,
    normalize_whitespace,
    remove_words,
    strip_punctuation,
    word_count,
    word_in_set,
)

__all__ = [
    # HTTP utilities
    "HTTPClient",
    "RateLimiter",
    "RetryConfig",
    "fetch_url",
    "get_shared_client",
    # Text utilities
    "STOP_WORDS",
    "strip_punctuation",
    "normalize_whitespace",
    "fix_punctuation_spacing",
    "get_content_words",
    "word_count",
    "compile_patterns",
    "match_any_pattern",
    "find_all_matches",
    "word_in_set",
    "has_meaningful_content",
    "calculate_word_overlap",
    "has_quote",
    "has_numbers",
    "is_all_caps",
    "has_excessive_punctuation",
    "extract_quoted_content",
    "remove_words",
]
