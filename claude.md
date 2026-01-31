# NewsDigest

Semantic compression engine for news articles that extracts signal from noise by identifying and removing filler, speculation, and engagement-optimized content while preserving factual claims and attributed sources.

## Quick Reference

```bash
# Setup
make setup              # Full dev setup (venv + deps + models)
make install-dev        # Install with dev dependencies

# Development
make test               # Run all tests
make test-cov           # Run tests with coverage
make lint               # Run ruff linter
make format             # Format code with ruff
make type-check         # Run mypy
make check              # Run all checks (lint, type, security, tests)

# Build & Run
make build              # Build wheel + sdist
newsdigest extract <url>  # Extract single article
newsdigest compare <url>  # Side-by-side comparison
newsdigest digest         # Generate digest from sources
```

## Architecture

The project follows a pipeline pattern with clear separation of concerns:

```
Article → Parser → NLP Pipeline → Analyzers → Formatter → Output
```

### Key Directories

- `src/newsdigest/core/` - Core extraction engine (Extractor, Pipeline)
- `src/newsdigest/analyzers/` - 8 semantic analyzers (filler, speculation, sources, emotional, etc.)
- `src/newsdigest/ingestors/` - Input adapters (URL, RSS, NewsAPI, Email, Twitter, PDF)
- `src/newsdigest/formatters/` - Output formatters (Markdown, JSON, Text, HTML, Email)
- `src/newsdigest/cli/` - Click-based CLI commands
- `src/newsdigest/api/` - FastAPI REST endpoints
- `src/newsdigest/storage/` - Cache and database persistence

### Core Classes

- `Extractor` - Main entry point for extraction (`core/extractor.py`)
- `BaseAnalyzer` - Abstract base for all analyzers (`analyzers/base.py`)
- `BaseIngestor` - Abstract base for input sources (`ingestors/base.py`)
- `BaseFormatter` - Abstract base for output formats (`formatters/base.py`)

## Code Style

- **Linter/Formatter:** Ruff (double quotes, 88-char lines)
- **Type Checking:** mypy with strict mode
- **Docstrings:** Google style
- **Python:** 3.11+ with async/await support

### Conventions

- Classes: PascalCase
- Functions/methods: snake_case
- Constants: UPPER_SNAKE_CASE
- Private members: _leading_underscore
- Module logger: `logger = get_logger(__name__)`

## Testing

```bash
pytest                          # Run all tests
pytest tests/unit/              # Unit tests only
pytest tests/e2e/               # End-to-end tests
pytest -m integration           # Integration tests (slower)
pytest --cov=src/newsdigest     # With coverage
```

Coverage targets: Core 90%, Analyzers 85%, Ingestors/Formatters/API 80%, CLI 75%

## Configuration

- Config file: `~/.newsdigest/config.yml`
- Environment prefix: `NEWSDIGEST_`
- Key settings in `src/newsdigest/config/settings.py`

### Extraction Modes

1. **conservative** - Keeps more context, removes only obvious filler
2. **standard** (default) - Balanced approach
3. **aggressive** - Removes everything except core claims

## Error Handling

Custom exception hierarchy in `src/newsdigest/exceptions.py`:

- `NewsDigestError` (base)
- `ExtractionError`, `PipelineError`, `AnalysisError`
- `FetchError`, `ParseError`, `IngestError`
- `FormatterError`, `DigestError`, `ConfigurationError`

## Dependencies

Core dependencies are minimal. Optional features require extra installs:

```bash
pip install newsdigest[api]     # FastAPI REST API
pip install newsdigest[email]   # Email delivery
pip install newsdigest[newsapi] # NewsAPI integration
pip install newsdigest[ml]      # ML-enhanced features
pip install newsdigest[all]     # Everything
```

## Important Files

- `pyproject.toml` - Project metadata, dependencies, tool configs
- `ruff.toml` - Linter/formatter configuration
- `Makefile` - Development commands (22 targets)
- `docs/SPEC.md` - Full technical specification (1900+ lines)
- `docs/ARCHITECTURE.md` - System architecture
