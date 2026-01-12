# Contributing to NewsDigest

Thank you for your interest in contributing to NewsDigest! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project follows a standard code of conduct. Please be respectful and constructive in all interactions. We welcome contributors of all experience levels.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Make (optional, for convenience commands)

### Finding Issues

- Look for issues labeled `good first issue` for beginner-friendly tasks
- Issues labeled `help wanted` are ready for contribution
- Feel free to ask questions on any issue before starting work

## Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/NewsDigest.git
   cd NewsDigest
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   # Install all development dependencies
   pip install -e ".[all]"

   # Or install specific extras
   pip install -e ".[dev]"  # Development tools only
   ```

4. **Download spaCy model**

   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Install pre-commit hooks**

   ```bash
   pre-commit install
   ```

6. **Verify setup**

   ```bash
   make test        # Run tests
   make lint        # Run linter
   make typecheck   # Run type checker
   ```

## Making Changes

### Branch Naming

Create a branch with a descriptive name:

```bash
git checkout -b feature/add-twitter-integration
git checkout -b fix/rss-parsing-error
git checkout -b docs/update-api-examples
```

### Commit Messages

Follow conventional commit format:

```
type(scope): short description

Longer description if needed.

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add batch extraction endpoint
fix(rss): handle malformed feed dates
docs(readme): add installation instructions
test(analyzers): add edge case tests for emotional detector
```

### Keep Changes Focused

- One feature or fix per pull request
- Keep pull requests small and reviewable
- Split large changes into multiple PRs if possible

## Pull Request Process

1. **Update your branch**

   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run all checks**

   ```bash
   make check  # Runs lint, typecheck, and tests
   ```

3. **Push your branch**

   ```bash
   git push origin your-branch-name
   ```

4. **Create a pull request**

   - Fill out the PR template completely
   - Link related issues
   - Add screenshots for UI changes
   - Request review from maintainers

5. **Address review feedback**

   - Respond to all comments
   - Push fixes as new commits
   - Re-request review when ready

6. **Merge requirements**

   - All CI checks must pass
   - At least one approving review
   - No unresolved conversations

## Coding Standards

### Python Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

- **Line length**: 88 characters
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Absolute imports, sorted alphabetically

```bash
# Format code
ruff format src/ tests/

# Check for issues
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

### Type Hints

All code must have type hints. We use strict mypy configuration:

```python
def extract_claims(
    text: str,
    min_confidence: float = 0.5,
) -> list[Claim]:
    """Extract claims from text.

    Args:
        text: The text to analyze.
        min_confidence: Minimum confidence threshold.

    Returns:
        List of extracted claims.
    """
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def process_article(url: str, mode: str = "standard") -> ExtractionResult:
    """Process an article from a URL.

    Fetches the article, extracts content, and applies semantic
    compression to remove noise.

    Args:
        url: The article URL to process.
        mode: Extraction mode ('conservative', 'standard', 'aggressive').

    Returns:
        ExtractionResult containing compressed content and statistics.

    Raises:
        IngestError: If the URL cannot be fetched.
        ExtractionError: If content extraction fails.

    Example:
        >>> result = process_article("https://example.com/article")
        >>> print(result.compression_ratio)
        0.85
    """
```

### Error Handling

- Use custom exception classes from `newsdigest.exceptions`
- Always include helpful error messages
- Log errors with appropriate levels

```python
from newsdigest.exceptions import ExtractionError

def extract(self, text: str) -> ExtractionResult:
    if not text.strip():
        raise ExtractionError("Cannot extract from empty text")
    ...
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/newsdigest --cov-report=html

# Run specific test file
pytest tests/unit/test_extractor.py

# Run tests matching pattern
pytest -k "test_emotional"

# Run excluding slow tests
pytest -m "not slow"
```

### Writing Tests

- Place tests in `tests/` mirroring the source structure
- Use descriptive test names
- Include docstrings explaining what's being tested
- Use fixtures for common setup

```python
import pytest
from newsdigest.analyzers.emotional import EmotionalAnalyzer


class TestEmotionalAnalyzer:
    """Tests for the emotional language analyzer."""

    @pytest.fixture
    def analyzer(self) -> EmotionalAnalyzer:
        """Create analyzer instance for tests."""
        return EmotionalAnalyzer()

    def test_detects_shocking_language(self, analyzer: EmotionalAnalyzer) -> None:
        """Verify 'shocking' is detected as emotional."""
        text = "The shocking revelation came today."
        result = analyzer.analyze(text)
        assert result.emotional_score > 0.5

    def test_neutral_text_scores_low(self, analyzer: EmotionalAnalyzer) -> None:
        """Verify neutral text has low emotional score."""
        text = "The meeting was held at 3pm."
        result = analyzer.analyze(text)
        assert result.emotional_score < 0.2
```

### Test Coverage

- Maintain minimum 80% code coverage
- Cover edge cases and error conditions
- Add regression tests for bug fixes

## Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update CHANGELOG.md for notable changes

### Building Documentation

```bash
# Build docs locally
make docs

# Serve docs for preview
mkdocs serve
```

## Questions?

- Open an issue for questions
- Join discussions on GitHub
- Check existing issues and documentation first

Thank you for contributing to NewsDigest!
