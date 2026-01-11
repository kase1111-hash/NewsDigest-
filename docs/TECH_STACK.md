# Tech Stack & Dependencies

**Project:** NewsDigest
**Version:** 0.1.0
**Last Updated:** 2026-01-11

---

## Overview

This document defines the technology choices for NewsDigest, including justifications and alternatives considered.

---

## Core Platform

| Component | Choice | Version |
|-----------|--------|---------|
| **Language** | Python | 3.11+ |
| **Package Format** | Modern Python Package (pyproject.toml) | PEP 517/518 |
| **Package Manager** | pip / pipx | Latest |

### Why Python 3.11+?

- **NLP Ecosystem**: Best-in-class NLP libraries (spaCy, transformers, NLTK)
- **Async Support**: Native async/await for concurrent HTTP requests
- **Type Hints**: Full typing support for better code quality
- **Performance**: 3.11 is 10-60% faster than 3.10
- **Match Statements**: Structural pattern matching (3.10+)
- **ExceptionGroups**: Better error handling (3.11+)

### Alternatives Considered

| Alternative | Reason Not Chosen |
|-------------|-------------------|
| Node.js | Weaker NLP ecosystem, would require Python for ML anyway |
| Go | Limited NLP libraries, less suited for rapid prototyping |
| Rust | Steep learning curve, overkill for this use case |

---

## Dependencies by Category

### CLI Framework

| Package | Version | Purpose |
|---------|---------|---------|
| **click** | >=8.1.0 | Command-line interface framework |
| **rich** | >=13.0.0 | Terminal formatting, tables, progress bars |

#### Why Click?

- Mature, battle-tested (used by Flask, Ansible, etc.)
- Excellent documentation
- Composable commands and groups
- Automatic help generation
- Testing utilities built-in

#### Why Rich?

- Beautiful terminal output
- Progress bars for batch operations
- Tables for statistics display
- Syntax highlighting
- Markdown rendering in terminal

#### Alternatives Considered

| Alternative | Reason Not Chosen |
|-------------|-------------------|
| Typer | Built on Click; adds complexity without major benefit |
| argparse | More verbose, less developer-friendly |
| fire | Less control over CLI structure |

---

### HTTP & Networking

| Package | Version | Purpose |
|---------|---------|---------|
| **httpx** | >=0.25.0 | Async HTTP client |
| **tenacity** | >=8.2.0 | Retry logic with exponential backoff |

#### Why httpx?

- Async support (critical for batch processing)
- HTTP/2 support
- Familiar requests-like API
- Connection pooling
- Timeout configuration

#### Why tenacity?

- Decorator-based retry logic
- Configurable backoff strategies
- Works with both sync and async code
- Exception filtering

#### Alternatives Considered

| Alternative | Reason Not Chosen |
|-------------|-------------------|
| requests | No native async support |
| aiohttp | Less intuitive API than httpx |
| urllib3 | Lower-level, more boilerplate |

---

### HTML/XML Parsing

| Package | Version | Purpose |
|---------|---------|---------|
| **beautifulsoup4** | >=4.12.0 | HTML parsing and navigation |
| **lxml** | >=4.9.0 | Fast XML/HTML parser (BS4 backend) |
| **readability-lxml** | >=0.8.0 | Article content extraction |
| **feedparser** | >=6.0.0 | RSS/Atom feed parsing |

#### Why BeautifulSoup4 + lxml?

- BeautifulSoup: Forgiving parser, handles malformed HTML
- lxml backend: 10-100x faster than html.parser
- Wide ecosystem familiarity
- Excellent CSS selector support

#### Why readability-lxml?

- Port of Mozilla's Readability algorithm
- Proven article extraction heuristics
- Handles diverse site layouts
- Extracts title, author, content

#### Why feedparser?

- De facto standard for RSS/Atom parsing
- Handles feed variants gracefully
- Date parsing built-in
- Sanitizes content

#### Alternatives Considered

| Alternative | Reason Not Chosen |
|-------------|-------------------|
| newspaper3k | Heavier, less maintained |
| trafilatura | Good but less battle-tested |
| html5lib | Slower than lxml |

---

### NLP & Text Processing

| Package | Version | Purpose |
|---------|---------|---------|
| **spacy** | >=3.7.0 | NLP pipeline (tokenization, NER, POS) |

#### Why spaCy?

- Production-ready NLP pipeline
- Fast (Cython-optimized)
- Pre-trained models available
- Easy pipeline customization
- Entity recognition out of the box
- Sentence segmentation

#### spaCy Models

| Model | Size | Use Case |
|-------|------|----------|
| en_core_web_sm | ~12MB | Fast, good enough for most use cases |
| en_core_web_md | ~40MB | Better accuracy, word vectors |
| en_core_web_lg | ~560MB | Best accuracy, full word vectors |

Default: `en_core_web_sm` (downloaded during setup)

#### Alternatives Considered

| Alternative | Reason Not Chosen |
|-------------|-------------------|
| NLTK | Slower, less modern API |
| Stanza | Slower, more academic focus |
| Flair | Heavier, overkill for our needs |

---

### Configuration

| Package | Version | Purpose |
|---------|---------|---------|
| **pyyaml** | >=6.0.0 | YAML config file parsing |
| **python-dotenv** | >=1.0.0 | Environment variable loading |
| **pydantic** | >=2.0.0 | Configuration validation & settings |

#### Why This Stack?

- **PyYAML**: Standard YAML parser, handles complex configs
- **python-dotenv**: Load `.env` files for secrets
- **Pydantic**: Type-safe settings with validation

#### Why Pydantic v2?

- 5-50x faster than v1
- Better error messages
- Improved typing support
- Settings management built-in

---

### Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| **python-dateutil** | >=2.8.0 | Flexible date parsing |

#### Why python-dateutil?

- Parses diverse date formats
- Timezone handling
- Relative date calculations
- RSS feeds have inconsistent date formats

---

## Optional Dependencies

### API Server (Phase 3)

| Package | Version | Purpose |
|---------|---------|---------|
| **fastapi** | >=0.104.0 | REST API framework |
| **uvicorn** | >=0.24.0 | ASGI server |

#### Why FastAPI?

- Automatic OpenAPI documentation
- Pydantic integration (request/response validation)
- Async native
- Excellent performance
- Type hints everywhere

#### Why Uvicorn?

- Fastest Python ASGI server
- Production-ready
- HTTP/2 support

---

### Email (Phase 3)

| Package | Version | Purpose |
|---------|---------|---------|
| **aiosmtplib** | >=2.0.0 | Async SMTP client |

#### Why aiosmtplib?

- Async for non-blocking email sends
- Modern API
- TLS/SSL support

---

### NewsAPI Integration (Phase 3)

| Package | Version | Purpose |
|---------|---------|---------|
| **newsapi-python** | >=0.2.7 | NewsAPI.org client |

---

### Twitter/X Integration (Phase 4+)

| Package | Version | Purpose |
|---------|---------|---------|
| **tweepy** | >=4.14.0 | Twitter API client |

---

### PDF Parsing (Phase 4+)

| Package | Version | Purpose |
|---------|---------|---------|
| **pdfplumber** | >=0.10.0 | PDF text extraction |

#### Why pdfplumber?

- Accurate text extraction
- Table detection
- Handles complex layouts
- Built on pdfminer.six

---

### Machine Learning Enhancements (Optional)

| Package | Version | Purpose |
|---------|---------|---------|
| **transformers** | >=4.35.0 | Transformer models |
| **torch** | >=2.1.0 | PyTorch backend |
| **sentence-transformers** | >=2.2.0 | Sentence embeddings |

#### Use Cases

- **sentence-transformers**: Semantic similarity for deduplication
- **transformers**: Advanced text classification (optional)

#### Note

These are optional and significantly increase install size (~2GB+). The core extraction works without ML dependencies.

---

## Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| **pytest** | >=7.4.0 | Testing framework |
| **pytest-asyncio** | >=0.21.0 | Async test support |
| **pytest-cov** | >=4.1.0 | Coverage reporting |
| **ruff** | >=0.1.0 | Linting and formatting |
| **mypy** | >=1.7.0 | Static type checking |
| **pre-commit** | >=3.6.0 | Git hooks |

### Why Ruff?

- 10-100x faster than flake8 + black + isort combined
- Replaces multiple tools
- Written in Rust
- Excellent defaults

### Why mypy?

- Industry standard type checker
- Catches bugs before runtime
- Improves code documentation

---

## Dependency Installation Groups

```toml
[project.optional-dependencies]
# Core functionality only
# (installed by default with: pip install newsdigest)

# REST API support
api = ["fastapi>=0.104.0", "uvicorn>=0.24.0"]

# Email digest delivery
email = ["aiosmtplib>=2.0.0"]

# NewsAPI integration
newsapi = ["newsapi-python>=0.2.7"]

# Twitter/X integration
twitter = ["tweepy>=4.14.0"]

# PDF parsing
pdf = ["pdfplumber>=0.10.0"]

# ML-enhanced features (large download)
ml = [
    "transformers>=4.35.0",
    "torch>=2.1.0",
    "sentence-transformers>=2.2.0",
]

# Development tools
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
    "pre-commit>=3.6.0",
]

# Everything except ML
full = ["newsdigest[api,email,newsapi,twitter,pdf]"]

# Everything including ML
all = ["newsdigest[full,ml]"]
```

---

## Installation Commands

```bash
# Basic installation (CLI + core extraction)
pip install newsdigest

# With API server support
pip install newsdigest[api]

# With all integrations (no ML)
pip install newsdigest[full]

# With everything including ML
pip install newsdigest[all]

# Development installation
pip install -e ".[dev]"
```

---

## Version Pinning Strategy

### Production

- Use **minimum versions** with `>=` for flexibility
- Avoid upper bounds unless known incompatibility
- Lock versions in `requirements.lock` for reproducibility

### Development

- Use `pip-compile` from pip-tools to generate lockfile
- Regenerate lockfile monthly or when adding dependencies

---

## Security Considerations

### Dependency Auditing

- Run `pip-audit` in CI to check for known vulnerabilities
- Subscribe to security advisories for critical packages
- Update dependencies monthly

### Specific Concerns

| Package | Risk | Mitigation |
|---------|------|------------|
| lxml | C extension, potential memory issues | Keep updated, fuzz testing |
| pyyaml | YAML deserialization attacks | Use `safe_load()` only |
| httpx | SSRF if URLs not validated | Validate user-provided URLs |

---

## Size Estimates

| Installation | Approximate Size |
|--------------|------------------|
| Core only | ~150MB (includes spaCy + model) |
| With API | ~180MB |
| With full integrations | ~250MB |
| With ML dependencies | ~2.5GB |

---

## Platform Support

| Platform | Support Level |
|----------|---------------|
| Linux (x86_64) | Full |
| macOS (x86_64, ARM) | Full |
| Windows (x86_64) | Full |
| Linux (ARM64) | Full |

### Notes

- All core dependencies have wheels for major platforms
- spaCy models are platform-independent
- torch (ML optional) has platform-specific builds

---

## Summary

### Core Stack (Required)

```
Python 3.11+
├── click         # CLI framework
├── rich          # Terminal UI
├── httpx         # HTTP client
├── beautifulsoup4 + lxml  # HTML parsing
├── readability-lxml       # Article extraction
├── feedparser    # RSS parsing
├── spacy         # NLP pipeline
├── pyyaml        # Configuration
├── python-dotenv # Environment
├── pydantic      # Validation
├── python-dateutil  # Date handling
└── tenacity      # Retry logic
```

### Optional Integrations

```
├── fastapi + uvicorn  # REST API
├── aiosmtplib        # Email
├── newsapi-python    # NewsAPI
├── tweepy            # Twitter
├── pdfplumber        # PDF
└── transformers + torch + sentence-transformers  # ML
```

---

*End of Tech Stack Document*
