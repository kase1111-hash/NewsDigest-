"""Tests for the EmotionalDetector analyzer."""

import pytest

from newsdigest.analyzers.emotional import EmotionalDetector


class TestEmotionalDetector:
    """Tests for EmotionalDetector analyzer."""

    @pytest.fixture
    def detector(self):
        """Create an EmotionalDetector instance."""
        return EmotionalDetector()

    def test_initialization(self, detector):
        """Test detector initializes correctly."""
        assert detector is not None
        assert hasattr(detector, "analyze")

    def test_shocking_detection(self, detector):
        """Test detection of 'shocking' emotional language."""
        text = "In a shocking development, the CEO resigned."
        result = detector.analyze(text)
        assert result["has_emotional_language"] is True

    def test_stunning_detection(self, detector):
        """Test detection of 'stunning' emotional language."""
        text = "The stunning announcement caught investors off guard."
        result = detector.analyze(text)
        assert result["has_emotional_language"] is True

    def test_unprecedented_detection(self, detector):
        """Test detection of 'unprecedented' emotional language."""
        text = "This unprecedented move signals a major shift."
        result = detector.analyze(text)
        assert result["has_emotional_language"] is True

    def test_bombshell_detection(self, detector):
        """Test detection of 'bombshell' emotional language."""
        text = "The bombshell revelation rocked the industry."
        result = detector.analyze(text)
        assert result["has_emotional_language"] is True

    def test_alarmed_detection(self, detector):
        """Test detection of 'alarmed' emotional language."""
        text = "Experts are alarmed by the latest findings."
        result = detector.analyze(text)
        assert result["has_emotional_language"] is True

    def test_neutral_sentence_no_emotion(self, detector):
        """Test that neutral sentences are not detected as emotional."""
        text = "The Federal Reserve announced a rate increase."
        result = detector.analyze(text)
        assert result["has_emotional_language"] is False

    def test_factual_with_numbers_no_emotion(self, detector):
        """Test that factual sentences with numbers are not emotional."""
        text = "Revenue increased 15% year over year to $10 billion."
        result = detector.analyze(text)
        assert result["has_emotional_language"] is False

    def test_multiple_emotional_words(self, detector):
        """Test detection of multiple emotional words."""
        text = "The shocking and unprecedented scandal has left everyone alarmed."
        result = detector.analyze(text)
        assert result["has_emotional_language"] is True
        # Should detect multiple emotional words
        word_count = result.get("emotional_word_count", len(result.get("emotional_words", [])))
        assert word_count >= 2

    def test_empty_string(self, detector):
        """Test handling of empty string."""
        result = detector.analyze("")
        assert result["has_emotional_language"] is False

    def test_extraordinary_detection(self, detector):
        """Test detection of 'extraordinary' emotional language."""
        text = "This extraordinary development changes everything."
        result = detector.analyze(text)
        assert result["has_emotional_language"] is True

    def test_emotional_words_list_returned(self, detector):
        """Test that detected emotional words are returned."""
        text = "The shocking scandal was unprecedented."
        result = detector.analyze(text)
        assert "emotional_words" in result or "words_found" in result

    def test_shockwaves_detection(self, detector):
        """Test detection of 'shockwaves' emotional language."""
        text = "The news sent shockwaves through Wall Street."
        result = detector.analyze(text)
        assert result["has_emotional_language"] is True
