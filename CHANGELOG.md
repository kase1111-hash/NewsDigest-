# Changelog

All notable changes to NewsDigest will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- REST API with FastAPI (endpoints: /health, /extract, /extract/batch, /digest, /compare)
- Storage layer with MemoryCache, FileCache, AnalyticsStore, and SourceStore
- CLI commands: extract, compare, stats, digest, sources, watch, analytics, setup
- Polyform Small Business License 1.0.0

## [0.1.0] - 2024-01-15

### Added
- Core semantic extraction engine with 8 analyzers:
  - Filler detection
  - Speculation stripping
  - Source validation
  - Emotional language detection
  - Repetition collapsing
  - Novelty scoring
  - Claims extraction
  - Quote isolation
- Content ingestion from multiple sources:
  - URL fetching with async HTTP client
  - RSS/Atom feed parsing
  - Direct text input
- Output formatters:
  - JSON with detailed metadata
  - Markdown with tables
  - Plain text
- Digest generation with topic clustering and deduplication
- Configuration management system:
  - YAML configuration files
  - Environment variable support
  - Secret management
- Comprehensive error handling with custom exception types
- Logging and telemetry infrastructure
- Metrics collection system
- CI/CD pipeline with GitHub Actions:
  - Automated testing (Python 3.11, 3.12)
  - Code quality checks (ruff, mypy, bandit)
  - Release automation to PyPI
- Docker containerization support
- Pre-commit hooks for code quality
- Semantic versioning with bump2version
- Extensive documentation:
  - Technical specification (SPEC.md)
  - Architecture documentation
  - OpenAPI specification
  - Postman collection

### Infrastructure
- pytest test suite with 483 test functions
- Code coverage requirement of 80%
- Strict type checking with mypy
- Security scanning with bandit

[Unreleased]: https://github.com/kase1111-hash/NewsDigest/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kase1111-hash/NewsDigest/releases/tag/v0.1.0
