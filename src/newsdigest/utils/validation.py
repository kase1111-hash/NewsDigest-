"""Input validation and sanitation utilities for NewsDigest.

This module provides comprehensive input validation to ensure:
- URLs are valid and safe
- Text content is properly sanitized
- Configuration values are within expected ranges
- User inputs don't contain malicious content
"""

import html
import re
from typing import Any
from urllib.parse import urlparse


# =============================================================================
# CONSTANTS
# =============================================================================

# Maximum lengths for various inputs
MAX_URL_LENGTH = 2048
MAX_TEXT_LENGTH = 1_000_000  # 1MB of text
MAX_TITLE_LENGTH = 500
MAX_FEED_ITEMS = 100

# Allowed URL schemes
ALLOWED_SCHEMES = {"http", "https"}

# Blocked domains (example malicious patterns)
BLOCKED_DOMAIN_PATTERNS = [
    r".*\.onion$",  # Tor hidden services
    r"^localhost$",
    r"^127\.\d+\.\d+\.\d+$",
    r"^0\.0\.0\.0$",
    r"^10\.\d+\.\d+\.\d+$",  # Private networks
    r"^172\.(1[6-9]|2\d|3[01])\.\d+\.\d+$",
    r"^192\.168\.\d+\.\d+$",
]

# Dangerous HTML patterns to remove
DANGEROUS_HTML_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"<iframe[^>]*>.*?</iframe>",
    r"<object[^>]*>.*?</object>",
    r"<embed[^>]*>.*?</embed>",
    r"<applet[^>]*>.*?</applet>",
    r"on\w+\s*=",  # Event handlers like onclick=
    r"javascript:",
    r"vbscript:",
    r"data:text/html",
]


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================


class ValidationError(ValueError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str | None = None) -> None:
        """Initialize validation error.

        Args:
            message: Error message.
            field: Optional field name that failed validation.
        """
        super().__init__(message)
        self.field = field
        self.message = message


class SanitizationError(ValueError):
    """Raised when content cannot be safely sanitized."""

    pass


# =============================================================================
# URL VALIDATION
# =============================================================================


def validate_url(url: str, allow_private: bool = False) -> tuple[bool, str | None]:
    """Validate a URL for safety and correctness.

    Args:
        url: URL to validate.
        allow_private: Whether to allow private/local network URLs.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string"

    url = url.strip()

    # Check length
    if len(url) > MAX_URL_LENGTH:
        return False, f"URL exceeds maximum length of {MAX_URL_LENGTH}"

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL format: {e}"

    # Check scheme
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False, f"URL scheme must be one of: {', '.join(ALLOWED_SCHEMES)}"

    # Check for host
    if not parsed.netloc:
        return False, "URL must have a valid host"

    # Check for blocked domains (unless allow_private)
    if not allow_private:
        hostname = parsed.hostname or ""
        for pattern in BLOCKED_DOMAIN_PATTERNS:
            if re.match(pattern, hostname, re.IGNORECASE):
                return False, "URL host is not allowed (private/local network)"

    # Check for suspicious patterns
    if ".." in url or "\\" in url:
        return False, "URL contains suspicious path patterns"

    return True, None


def validate_url_strict(url: str) -> str:
    """Validate URL and raise exception if invalid.

    Args:
        url: URL to validate.

    Returns:
        Validated URL.

    Raises:
        ValidationError: If URL is invalid.
    """
    is_valid, error = validate_url(url)
    if not is_valid:
        raise ValidationError(error or "Invalid URL", field="url")
    return url.strip()


def is_valid_url(url: str) -> bool:
    """Quick check if URL is valid.

    Args:
        url: URL to check.

    Returns:
        True if valid.
    """
    is_valid, _ = validate_url(url)
    return is_valid


# =============================================================================
# TEXT VALIDATION & SANITATION
# =============================================================================


def sanitize_text(
    text: str,
    max_length: int | None = None,
    strip_html: bool = True,
    normalize_whitespace: bool = True,
) -> str:
    """Sanitize text content for safe processing.

    Args:
        text: Text to sanitize.
        max_length: Maximum allowed length (truncates if exceeded).
        strip_html: Whether to remove HTML tags.
        normalize_whitespace: Whether to normalize whitespace.

    Returns:
        Sanitized text.
    """
    if not text:
        return ""

    if not isinstance(text, str):
        text = str(text)

    # Apply max length
    if max_length and len(text) > max_length:
        text = text[:max_length]

    # Remove dangerous HTML patterns first
    if strip_html:
        for pattern in DANGEROUS_HTML_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

        # Remove remaining HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Decode HTML entities
        text = html.unescape(text)

    # Remove null bytes and other control characters (except newlines/tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize whitespace if requested
    if normalize_whitespace:
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse multiple spaces (but preserve newlines)
        text = re.sub(r"[^\S\n]+", " ", text)
        # Collapse multiple newlines to max 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

    return text


def sanitize_html(html_content: str, max_length: int | None = None) -> str:
    """Sanitize HTML content by removing dangerous elements.

    Args:
        html_content: HTML to sanitize.
        max_length: Maximum allowed length.

    Returns:
        Sanitized HTML.
    """
    if not html_content:
        return ""

    if max_length and len(html_content) > max_length:
        html_content = html_content[:max_length]

    # Remove dangerous patterns
    for pattern in DANGEROUS_HTML_PATTERNS:
        html_content = re.sub(pattern, "", html_content, flags=re.IGNORECASE | re.DOTALL)

    # Remove null bytes
    html_content = html_content.replace("\x00", "")

    return html_content


def validate_text_content(
    text: str,
    min_length: int = 0,
    max_length: int = MAX_TEXT_LENGTH,
    require_content: bool = False,
) -> tuple[bool, str | None]:
    """Validate text content.

    Args:
        text: Text to validate.
        min_length: Minimum required length.
        max_length: Maximum allowed length.
        require_content: Whether to require non-whitespace content.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if text is None:
        return False, "Text cannot be None"

    if not isinstance(text, str):
        return False, "Text must be a string"

    if len(text) < min_length:
        return False, f"Text must be at least {min_length} characters"

    if len(text) > max_length:
        return False, f"Text exceeds maximum length of {max_length}"

    if require_content and not text.strip():
        return False, "Text must contain non-whitespace content"

    return True, None


# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================


def validate_range(
    value: Any,
    min_val: float | None = None,
    max_val: float | None = None,
    name: str = "value",
) -> float:
    """Validate a numeric value is within range.

    Args:
        value: Value to validate.
        min_val: Minimum allowed value.
        max_val: Maximum allowed value.
        name: Name for error messages.

    Returns:
        Validated value as float.

    Raises:
        ValidationError: If validation fails.
    """
    try:
        num_value = float(value)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"{name} must be a number: {e}", field=name)

    if min_val is not None and num_value < min_val:
        raise ValidationError(f"{name} must be at least {min_val}", field=name)

    if max_val is not None and num_value > max_val:
        raise ValidationError(f"{name} must be at most {max_val}", field=name)

    return num_value


def validate_positive_int(
    value: Any, name: str = "value", allow_zero: bool = False
) -> int:
    """Validate value is a positive integer.

    Args:
        value: Value to validate.
        name: Name for error messages.
        allow_zero: If True, zero is allowed. Default is False.

    Returns:
        Validated value as int.

    Raises:
        ValidationError: If validation fails.
    """
    try:
        int_value = int(value)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"{name} must be an integer: {e}", field=name)

    if allow_zero:
        if int_value < 0:
            raise ValidationError(f"{name} must be non-negative", field=name)
    else:
        if int_value <= 0:
            raise ValidationError(f"{name} must be positive", field=name)

    return int_value


def validate_enum(value: Any, allowed: list[Any], name: str = "value") -> Any:
    """Validate value is one of allowed values.

    Args:
        value: Value to validate.
        allowed: List of allowed values.
        name: Name for error messages.

    Returns:
        Validated value.

    Raises:
        ValidationError: If validation fails.
    """
    if value not in allowed:
        raise ValidationError(
            f"{name} must be one of: {', '.join(str(v) for v in allowed)}",
            field=name,
        )
    return value


def validate_extraction_mode(mode: str) -> str:
    """Validate extraction mode.

    Args:
        mode: Mode to validate.

    Returns:
        Validated mode.

    Raises:
        ValidationError: If mode is invalid.
    """
    allowed = ["keep", "flag", "remove"]
    return validate_enum(mode, allowed, "extraction mode")


# =============================================================================
# RSS/FEED VALIDATION
# =============================================================================


def validate_feed_url(url: str) -> str:
    """Validate an RSS/Atom feed URL.

    Args:
        url: Feed URL to validate.

    Returns:
        Validated URL.

    Raises:
        ValidationError: If URL is invalid.
    """
    url = validate_url_strict(url)

    # Additional feed-specific checks could go here
    # (e.g., checking Content-Type header)

    return url


def validate_feed_item_count(count: int) -> int:
    """Validate feed item count.

    Args:
        count: Number of items.

    Returns:
        Validated count.

    Raises:
        ValidationError: If count is invalid.
    """
    count = validate_positive_int(count, "item_count")

    if count > MAX_FEED_ITEMS:
        raise ValidationError(
            f"Item count cannot exceed {MAX_FEED_ITEMS}",
            field="item_count",
        )

    return count


# =============================================================================
# ARTICLE VALIDATION
# =============================================================================


def validate_article_content(content: str) -> str:
    """Validate and sanitize article content.

    Args:
        content: Article content to validate.

    Returns:
        Validated and sanitized content.

    Raises:
        ValidationError: If content is invalid.
    """
    is_valid, error = validate_text_content(
        content,
        min_length=10,
        max_length=MAX_TEXT_LENGTH,
        require_content=True,
    )

    if not is_valid:
        raise ValidationError(error or "Invalid content", field="content")

    return sanitize_text(content, strip_html=False)


def validate_article_title(title: str) -> str:
    """Validate and sanitize article title.

    Args:
        title: Title to validate.

    Returns:
        Validated and sanitized title.

    Raises:
        ValidationError: If title is invalid.
    """
    if not title:
        return ""

    is_valid, error = validate_text_content(
        title,
        max_length=MAX_TITLE_LENGTH,
    )

    if not is_valid:
        raise ValidationError(error or "Invalid title", field="title")

    return sanitize_text(title, max_length=MAX_TITLE_LENGTH)
