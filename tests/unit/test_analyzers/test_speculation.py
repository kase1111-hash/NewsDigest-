"""Tests for the SpeculationDetector analyzer."""

import pytest

from newsdigest.analyzers.speculation import SpeculationDetector


class TestSpeculationDetector:
    """Tests for SpeculationDetector analyzer."""

    @pytest.fixture
    def detector(self):
        """Create a SpeculationDetector instance."""
        return SpeculationDetector()

    def test_initialization(self, detector):
        """Test detector initializes correctly."""
        assert detector is not None
        assert hasattr(detector, "analyze")

    def test_could_detection(self, detector):
        """Test detection of 'could' speculation."""
        text = "This could signal a shift in policy."
        result = detector.analyze(text)
        assert result["is_speculative"] is True

    def test_might_detection(self, detector):
        """Test detection of 'might' speculation."""
        text = "Markets might react negatively to this news."
        result = detector.analyze(text)
        assert result["is_speculative"] is True

    def test_may_detection(self, detector):
        """Test detection of 'may' speculation."""
        text = "The company may announce layoffs next week."
        result = detector.analyze(text)
        assert result["is_speculative"] is True

    def test_would_appear_detection(self, detector):
        """Test detection of 'would appear' speculation."""
        text = "It would appear that negotiations have stalled."
        result = detector.analyze(text)
        assert result["is_speculative"] is True

    def test_potentially_detection(self, detector):
        """Test detection of 'potentially' speculation."""
        text = "This could potentially impact millions of users."
        result = detector.analyze(text)
        assert result["is_speculative"] is True

    def test_factual_sentence_not_speculative(self, detector):
        """Test that factual sentences are not detected as speculative."""
        text = "The company reported $5 billion in revenue."
        result = detector.analyze(text)
        assert result["is_speculative"] is False

    def test_direct_quote_not_speculative(self, detector):
        """Test that direct quotes are not detected as speculative."""
        text = '"This could change everything," said the CEO.'
        result = detector.analyze(text)
        # Quotes should generally not be flagged for speculation
        # as they are direct attribution
        assert "quote_context" in result or result["is_speculative"] is False

    def test_hedge_words_count(self, detector):
        """Test counting of hedge words."""
        text = "This could potentially maybe indicate a shift."
        result = detector.analyze(text)
        assert result["is_speculative"] is True
        # Should detect multiple hedge words
        hedge_count = result.get("hedge_count", len(result.get("hedges_found", [])))
        assert hedge_count >= 2

    def test_empty_string(self, detector):
        """Test handling of empty string."""
        result = detector.analyze("")
        assert result["is_speculative"] is False

    def test_suggests_detection(self, detector):
        """Test detection of 'suggests' speculation."""
        text = "Evidence suggests this trend will continue."
        result = detector.analyze(text)
        assert result["is_speculative"] is True

    def test_speculation_score_present(self, detector):
        """Test that speculation score is included."""
        text = "This might potentially signal a change."
        result = detector.analyze(text)
        assert "confidence" in result or "speculation_score" in result
