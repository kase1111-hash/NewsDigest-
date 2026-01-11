"""Tests for the FillerDetector analyzer."""

import pytest

from newsdigest.analyzers.filler import FillerDetector


class TestFillerDetector:
    """Tests for FillerDetector analyzer."""

    @pytest.fixture
    def detector(self):
        """Create a FillerDetector instance."""
        return FillerDetector()

    def test_initialization(self, detector):
        """Test detector initializes correctly."""
        assert detector is not None
        assert hasattr(detector, "analyze")

    def test_clickbait_detection(self, detector):
        """Test detection of clickbait patterns."""
        text = "Here's what you need to know about this story."
        result = detector.analyze(text)
        assert result["is_filler"] is True
        assert "clickbait" in result.get("categories", []) or result.get("pattern_matches", [])

    def test_stay_tuned_detection(self, detector):
        """Test detection of 'stay tuned' patterns."""
        text = "Stay tuned for more updates on this developing story."
        result = detector.analyze(text)
        assert result["is_filler"] is True

    def test_what_happened_next(self, detector):
        """Test detection of 'what happened next' patterns."""
        text = "What happened next will surprise you."
        result = detector.analyze(text)
        assert result["is_filler"] is True

    def test_factual_sentence_not_filler(self, detector):
        """Test that factual sentences are not detected as filler."""
        text = "The Federal Reserve raised interest rates by 0.25%."
        result = detector.analyze(text)
        assert result["is_filler"] is False

    def test_quote_not_filler(self, detector):
        """Test that quotes are not detected as filler."""
        text = '"The economy is strong," said Powell.'
        result = detector.analyze(text)
        assert result["is_filler"] is False

    def test_multiple_filler_patterns(self, detector):
        """Test detection of multiple filler patterns."""
        text = "Here's what you need to know. Stay tuned for more."
        result = detector.analyze(text)
        assert result["is_filler"] is True

    def test_empty_string(self, detector):
        """Test handling of empty string."""
        result = detector.analyze("")
        assert result["is_filler"] is False

    def test_but_thats_not_all(self, detector):
        """Test detection of 'but that's not all' pattern."""
        text = "But that's not all there is to this story."
        result = detector.analyze(text)
        assert result["is_filler"] is True

    def test_confidence_score_present(self, detector):
        """Test that confidence score is included in result."""
        text = "Here's what you need to know."
        result = detector.analyze(text)
        assert "confidence" in result or "filler_score" in result
