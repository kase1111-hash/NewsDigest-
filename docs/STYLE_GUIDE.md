# Coding Conventions & Style Guide

**Project:** NewsDigest
**Version:** 1.0
**Last Updated:** 2026-01-11

---

## Table of Contents

1. [Python Style](#1-python-style)
2. [Naming Conventions](#2-naming-conventions)
3. [Code Organization](#3-code-organization)
4. [Documentation](#4-documentation)
5. [Type Hints](#5-type-hints)
6. [Error Handling](#6-error-handling)
7. [Testing](#7-testing)
8. [Git Conventions](#8-git-conventions)
9. [Tool Configuration](#9-tool-configuration)

---

## 1. Python Style

### 1.1 General Rules

- **Python Version**: 3.11+ required
- **Line Length**: 88 characters (Black/Ruff default)
- **Indentation**: 4 spaces (no tabs)
- **Encoding**: UTF-8 for all Python files
- **Formatter**: Ruff (replaces Black, isort)
- **Linter**: Ruff (replaces Flake8, pylint)

### 1.2 Imports

Order imports in three groups, separated by blank lines:

```python
# 1. Standard library
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# 2. Third-party packages
import click
import httpx
from pydantic import BaseModel

# 3. Local imports
from newsdigest.core.article import Article
from newsdigest.core.result import ExtractionResult
```

**Rules:**
- Use absolute imports, not relative
- One import per line for `from` imports with multiple items
- Avoid wildcard imports (`from module import *`)
- Sort alphabetically within each group (Ruff handles this)

### 1.3 String Formatting

- Use f-strings for string interpolation (Python 3.6+)
- Use double quotes `"` for strings (Ruff default)
- Use triple double quotes `"""` for docstrings

```python
# Good
name = "NewsDigest"
message = f"Processing {count} articles"

# Avoid
message = "Processing {} articles".format(count)
message = "Processing %d articles" % count
```

### 1.4 Collections

```python
# Trailing commas for multi-line collections
sources = [
    "https://example.com/feed1",
    "https://example.com/feed2",
    "https://example.com/feed3",  # Trailing comma
]

config = {
    "mode": "standard",
    "timeout": 30,
    "retries": 3,  # Trailing comma
}
```

### 1.5 Comprehensions

- Use comprehensions for simple transformations
- Break into multiple lines if complex
- Use regular loops if side effects are needed

```python
# Good - simple comprehension
urls = [article.url for article in articles if article.url]

# Good - multi-line for readability
results = [
    process_article(article)
    for article in articles
    if article.is_valid
]

# Avoid - too complex, use regular loop
# Bad: [x.foo() for x in items if x.bar and x.baz or x.qux]
```

---

## 2. Naming Conventions

### 2.1 General Rules

| Type | Convention | Example |
|------|------------|---------|
| Modules | `snake_case` | `article.py`, `url_fetcher.py` |
| Classes | `PascalCase` | `Extractor`, `ArticleParser` |
| Functions | `snake_case` | `extract_content()`, `parse_html()` |
| Methods | `snake_case` | `def process_article(self):` |
| Variables | `snake_case` | `article_count`, `max_retries` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Type Variables | `PascalCase` | `T`, `ArticleT` |
| Private | `_leading_underscore` | `_internal_cache` |
| Dunder | `__double_underscore__` | `__init__`, `__str__` |

### 2.2 Specific Patterns

**Boolean variables** - use `is_`, `has_`, `can_`, `should_`:
```python
is_valid = True
has_source = article.source is not None
can_extract = url.startswith("http")
should_retry = attempt < max_retries
```

**Collections** - use plural nouns:
```python
articles = []  # List of Article
sources = {}   # Dict of sources
urls = set()   # Set of URLs
```

**Functions** - use verbs:
```python
def extract_content(url: str) -> str: ...
def parse_article(html: str) -> Article: ...
def validate_config(config: dict) -> bool: ...
```

**Classes** - use nouns:
```python
class Extractor: ...
class ArticleParser: ...
class FillerDetector: ...
```

### 2.3 Abbreviations

- Avoid abbreviations unless universally understood
- Acceptable: `url`, `html`, `http`, `api`, `id`, `config`
- Spell out: `article` (not `art`), `content` (not `cont`)

---

## 3. Code Organization

### 3.1 Module Structure

```python
"""Module docstring describing purpose.

Extended description if needed.
"""

# Future imports (if needed)
from __future__ import annotations

# Standard library
import asyncio
from typing import List, Optional

# Third-party
import httpx

# Local
from newsdigest.core.article import Article

# Constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Module-level logger
logger = logging.getLogger(__name__)


# Classes
class MyClass:
    """Class docstring."""

    def __init__(self): ...


# Functions
def my_function(): ...


# Main block (if script)
if __name__ == "__main__":
    main()
```

### 3.2 Class Structure

```python
class Extractor:
    """Main extraction engine.

    Attributes:
        config: Configuration object.
        mode: Extraction mode (conservative/standard/aggressive).
    """

    # Class variables
    DEFAULT_MODE = "standard"

    def __init__(self, config: Optional[Config] = None) -> None:
        """Initialize extractor."""
        # Instance variables
        self.config = config or Config()
        self._cache: Dict[str, Article] = {}

    # Properties
    @property
    def mode(self) -> str:
        """Return current extraction mode."""
        return self._mode

    # Public methods
    async def extract(self, url: str) -> ExtractionResult:
        """Extract content from URL."""
        ...

    # Private methods
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        ...

    # Dunder methods
    def __repr__(self) -> str:
        return f"Extractor(mode={self.mode!r})"
```

### 3.3 Function Length

- Functions should do one thing
- Target: 20-30 lines maximum
- If longer, consider breaking into smaller functions

---

## 4. Documentation

### 4.1 Docstrings

Use Google-style docstrings:

```python
def extract_article(url: str, timeout: int = 30) -> Article:
    """Extract article content from URL.

    Fetches the URL, parses HTML, and extracts the main article
    content using readability algorithms.

    Args:
        url: The article URL to fetch.
        timeout: Request timeout in seconds.

    Returns:
        Article object with extracted content and metadata.

    Raises:
        FetchError: If the URL cannot be fetched.
        ParseError: If the HTML cannot be parsed.

    Example:
        >>> article = extract_article("https://example.com/news")
        >>> print(article.title)
        "Breaking News"
    """
```

### 4.2 Docstring Requirements

| Element | Required | Notes |
|---------|----------|-------|
| Module docstring | Yes | First line of every `.py` file |
| Class docstring | Yes | Describe purpose and attributes |
| Public method docstring | Yes | Args, Returns, Raises |
| Private method docstring | Recommended | Brief description |
| Function docstring | Yes | Same as public methods |

### 4.3 Comments

```python
# Good - explains WHY
# Use aggressive mode for press releases since they're already dense
if source_type == "press_release":
    mode = "aggressive"

# Avoid - explains WHAT (obvious from code)
# Set mode to aggressive
mode = "aggressive"

# Good - inline for non-obvious code
score = (claims * confidence) / words * 10.0  # Normalize to 0-1 range
```

### 4.4 TODO Comments

```python
# TODO: Add retry logic for rate limiting
# TODO(username): Implement caching by 2025-02-01
# FIXME: This breaks with empty input
# HACK: Workaround for upstream bug #123
```

---

## 5. Type Hints

### 5.1 Requirements

- All public functions must have type hints
- All class attributes should be typed
- Use `from __future__ import annotations` for forward references

### 5.2 Common Patterns

```python
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from collections.abc import Callable, Iterable, Sequence

# Basic types
def process(text: str, count: int, enabled: bool) -> str: ...

# Optional (can be None)
def fetch(url: str, timeout: Optional[int] = None) -> str: ...

# Union types (Python 3.10+ can use |)
def parse(source: Union[str, Path]) -> Article: ...
def parse(source: str | Path) -> Article: ...  # 3.10+

# Collections
def process_all(urls: List[str]) -> Dict[str, Article]: ...
def process_all(urls: list[str]) -> dict[str, Article]: ...  # 3.9+

# Callables
def apply(func: Callable[[str], str], text: str) -> str: ...

# Generics
from typing import TypeVar
T = TypeVar("T")
def first(items: Sequence[T]) -> T: ...
```

### 5.3 Class Attributes

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Article:
    id: str
    content: str
    url: Optional[str] = None
    tags: list[str] = field(default_factory=list)
```

---

## 6. Error Handling

### 6.1 Custom Exceptions

```python
class NewsDigestError(Exception):
    """Base exception for NewsDigest."""
    pass

class FetchError(NewsDigestError):
    """Error fetching content from URL."""

    def __init__(self, url: str, message: str) -> None:
        self.url = url
        super().__init__(f"Failed to fetch {url}: {message}")
```

### 6.2 Exception Handling

```python
# Good - specific exceptions
try:
    response = await client.get(url)
except httpx.TimeoutException:
    logger.warning(f"Timeout fetching {url}")
    raise FetchError(url, "Request timed out")
except httpx.HTTPError as e:
    logger.error(f"HTTP error: {e}")
    raise FetchError(url, str(e)) from e

# Avoid - bare except
try:
    process()
except:  # Never do this
    pass

# Avoid - catching Exception without re-raising
try:
    process()
except Exception:
    log_error()
    # Should re-raise or handle specifically
```

### 6.3 Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug("Processing article: %s", article_id)
logger.info("Extracted %d claims from article", len(claims))
logger.warning("No content found in article %s", article_id)
logger.error("Failed to parse HTML: %s", error)
logger.exception("Unexpected error")  # Includes traceback
```

---

## 7. Testing

### 7.1 Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── unit/
│   ├── test_extractor.py
│   ├── test_analyzers/
│   │   ├── test_filler.py
│   │   └── test_speculation.py
│   └── ...
├── integration/
│   └── test_pipeline.py
└── fixtures/
    └── articles/
```

### 7.2 Test Naming

```python
class TestExtractor:
    """Tests for Extractor class."""

    def test_extract_returns_result(self): ...
    def test_extract_with_invalid_url_raises_error(self): ...
    def test_extract_batch_processes_in_parallel(self): ...

# Or function style
def test_extractor_extract_returns_result(): ...
def test_extractor_with_invalid_url_raises_fetch_error(): ...
```

### 7.3 Test Structure (Arrange-Act-Assert)

```python
def test_extract_removes_filler(sample_article: Article) -> None:
    """Test that filler content is removed during extraction."""
    # Arrange
    extractor = Extractor(mode="standard")
    article = sample_article

    # Act
    result = extractor.extract(article.content)

    # Assert
    assert "here's what you need to know" not in result.text.lower()
    assert result.statistics.compression_ratio > 0.5
```

### 7.4 Fixtures

```python
@pytest.fixture
def extractor() -> Extractor:
    """Provide configured extractor for tests."""
    return Extractor(mode="standard")

@pytest.fixture
def sample_html() -> str:
    """Provide sample HTML content."""
    return Path("tests/fixtures/sample.html").read_text()
```

---

## 8. Git Conventions

### 8.1 Branch Naming

```
main              # Production-ready code
develop           # Integration branch
feature/add-rss   # New features
fix/parsing-error # Bug fixes
docs/api-guide    # Documentation
refactor/cleanup  # Code improvements
```

### 8.2 Commit Messages

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat: Add RSS feed parsing support

Implement RSSParser class with feedparser backend.
Supports RSS 2.0 and Atom feeds.

Closes #42

---

fix: Handle empty article content gracefully

Previously, empty content would cause a ZeroDivisionError
in the density calculation. Now returns density of 0.0.

---

docs: Update API documentation with examples
```

### 8.3 Pull Requests

- Reference related issues
- Include summary of changes
- Add test plan or evidence
- Keep focused (one feature/fix per PR)

---

## 9. Tool Configuration

### 9.1 Ruff (ruff.toml)

See `ruff.toml` in project root for full configuration.

Key settings:
- Line length: 88
- Target: Python 3.11
- Enabled rules: E, F, W, I, UP, B, C4, SIM

### 9.2 mypy (mypy.ini or pyproject.toml)

See `pyproject.toml` `[tool.mypy]` section.

Key settings:
- `strict = true`
- `python_version = "3.11"`
- Disallow untyped definitions

### 9.3 pytest (pyproject.toml)

See `pyproject.toml` `[tool.pytest.ini_options]` section.

Key settings:
- `asyncio_mode = "auto"`
- Coverage reporting enabled

### 9.4 Pre-commit

See `.pre-commit-config.yaml` for hooks:
- ruff (lint + format)
- mypy
- pytest (optional)

---

## Quick Reference

```
✅ DO:
- Use type hints everywhere
- Write docstrings for public APIs
- Follow naming conventions
- Keep functions small and focused
- Write tests for new code
- Use f-strings for formatting
- Handle exceptions specifically

❌ DON'T:
- Use wildcard imports
- Catch bare exceptions
- Write overly long functions
- Skip docstrings on public APIs
- Use abbreviations unnecessarily
- Commit without running linter
```

---

*End of Style Guide*
