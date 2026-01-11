"""Integration tests for digest generation.

These tests verify the digest generation pipeline.
"""

import pytest

from newsdigest.core.extractor import Extractor
from newsdigest.core.result import ExtractionResult


class TestDigestGeneration:
    """Integration tests for digest generation."""

    @pytest.fixture
    def extractor(self) -> Extractor:
        """Create an extractor instance."""
        return Extractor()

    @pytest.fixture
    def related_articles(self) -> list:
        """Create related articles about the same topic."""
        return [
            """
            Apple reported quarterly revenue of $90 billion, beating estimates.
            CEO Tim Cook said iPhone sales drove the growth.
            "We're seeing strong demand worldwide," Cook stated.
            """,
            """
            Tech giant Apple exceeded Wall Street expectations with $90B revenue.
            The company attributed success to iPhone and Services growth.
            Analysts had predicted $88 billion in revenue.
            """,
            """
            Apple's quarterly results show $90 billion in revenue.
            iPhone sales increased 8% year over year.
            The company's stock rose 3% after the announcement.
            """,
        ]

    @pytest.fixture
    def unrelated_articles(self) -> list:
        """Create unrelated articles on different topics."""
        return [
            """
            Apple reported quarterly revenue of $90 billion.
            CEO Tim Cook highlighted strong iPhone sales.
            """,
            """
            The Federal Reserve raised interest rates by 0.25%.
            Chair Powell cited ongoing inflation concerns.
            """,
            """
            Scientists discovered a new species of deep-sea fish.
            The creature was found at 3000 meters depth.
            """,
        ]

    @pytest.mark.asyncio
    async def test_batch_extraction(self, extractor, related_articles):
        """Test batch extraction of multiple articles."""
        results = await extractor.extract_batch(related_articles)

        assert len(results) == len(related_articles)
        for result in results:
            assert isinstance(result, ExtractionResult)
            assert result.statistics.original_words > 0

    @pytest.mark.asyncio
    async def test_batch_extraction_parallel(self, extractor, related_articles):
        """Test parallel batch extraction."""
        results = await extractor.extract_batch(
            related_articles,
            parallel=True,
            max_workers=3,
        )

        assert len(results) == len(related_articles)

    @pytest.mark.asyncio
    async def test_batch_extraction_sequential(self, extractor, related_articles):
        """Test sequential batch extraction."""
        results = await extractor.extract_batch(
            related_articles,
            parallel=False,
        )

        assert len(results) == len(related_articles)

    @pytest.mark.asyncio
    async def test_batch_with_failures_continues(self, extractor):
        """Test that batch extraction continues after failures."""
        articles = [
            "Valid article about technology trends.",
            "",  # Empty - might cause issues
            "Another valid article about markets.",
        ]

        results = await extractor.extract_batch(
            articles,
            fail_fast=False,
        )

        # Should have at least the valid articles
        assert len(results) >= 1

    def test_extract_sync_wrapper(self, extractor, related_articles):
        """Test synchronous extract wrapper."""
        for article in related_articles:
            result = extractor.extract_sync(article)
            assert isinstance(result, ExtractionResult)


class TestComparisonFeature:
    """Tests for the comparison feature."""

    @pytest.fixture
    def extractor(self) -> Extractor:
        """Create an extractor instance."""
        return Extractor()

    def test_compare_returns_result(self, extractor):
        """Test that compare returns an extraction result."""
        content = """
        In a shocking development, the company announced layoffs.
        This could potentially affect thousands of employees.
        CEO John Smith said the decision was difficult.
        "We had no choice," Smith stated in a press release.
        The news sent shockwaves through the industry.
        """

        result = extractor.compare(content)

        assert isinstance(result, ExtractionResult)
        assert result.original_text is not None or result.text is not None

    def test_compare_includes_sentences(self, extractor):
        """Test that compare includes sentence-level data."""
        content = """
        The Federal Reserve raised rates.
        This could signal more increases.
        Chair Powell confirmed the decision.
        """

        result = extractor.compare(content)

        # Result should have sentence data for comparison
        assert result.sentences is not None or result.text is not None


class TestOutputFormats:
    """Tests for different output format combinations."""

    @pytest.fixture
    def extractor(self) -> Extractor:
        """Create an extractor instance."""
        return Extractor()

    @pytest.fixture
    def sample_content(self) -> str:
        """Sample content for testing."""
        return """
        Microsoft announced a new AI partnership worth $10 billion.
        CEO Satya Nadella called it "transformative for the industry."
        The deal will accelerate AI development across multiple products.
        """

    def test_all_format_types_work(self, extractor, sample_content):
        """Test that all format types produce output."""
        result = extractor.extract_sync(sample_content)

        formats = ["markdown", "json", "text"]

        for fmt in formats:
            output = extractor.format(result, format=fmt)
            assert isinstance(output, str)
            assert len(output) > 0

    def test_stats_all_formats(self, extractor, sample_content):
        """Test stats output in all formats."""
        result = extractor.extract_sync(sample_content)

        formats = ["markdown", "json", "text"]

        for fmt in formats:
            output = extractor.format_stats(result, format=fmt)
            assert isinstance(output, str)

    def test_comparison_formatting(self, extractor, sample_content):
        """Test comparison output formatting."""
        result = extractor.compare(sample_content)

        # Test comparison formatting
        output = extractor.format_comparison(result, format="markdown")
        assert isinstance(output, str)
