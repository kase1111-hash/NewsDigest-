"""Integration tests for analyzer chain.

These tests verify that analyzers work correctly together.
"""

import pytest

from newsdigest.analyzers.filler import FillerDetector
from newsdigest.analyzers.speculation import SpeculationDetector
from newsdigest.analyzers.emotional import EmotionalDetector
from newsdigest.analyzers.sources import SourceDetector
from newsdigest.analyzers.quotes import QuoteExtractor


class TestAnalyzerChain:
    """Tests for multiple analyzers working together."""

    @pytest.fixture
    def analyzers(self):
        """Create all analyzer instances."""
        return {
            "filler": FillerDetector(),
            "speculation": SpeculationDetector(),
            "emotional": EmotionalDetector(),
            "sources": SourceDetector(),
            "quotes": QuoteExtractor(),
        }

    def test_analyzers_on_clean_factual_sentence(self, analyzers):
        """Test that factual sentences pass all analyzers cleanly."""
        text = "Apple reported revenue of $90 billion for Q4 2024."

        filler_result = analyzers["filler"].analyze(text)
        spec_result = analyzers["speculation"].analyze(text)
        emotional_result = analyzers["emotional"].analyze(text)

        assert filler_result["is_filler"] is False
        assert spec_result["is_speculative"] is False
        assert emotional_result["has_emotional_language"] is False

    def test_analyzers_detect_combined_issues(self, analyzers):
        """Test detection of content with multiple issues."""
        # Text with filler, emotional language, and speculation
        text = (
            "Here's what you need to know: in a shocking development, "
            "the company could potentially announce major changes."
        )

        filler_result = analyzers["filler"].analyze(text)
        spec_result = analyzers["speculation"].analyze(text)
        emotional_result = analyzers["emotional"].analyze(text)

        # Should detect at least some issues
        issues_detected = (
            filler_result["is_filler"] or
            spec_result["is_speculative"] or
            emotional_result["has_emotional_language"]
        )
        assert issues_detected is True

    def test_source_and_quote_extraction(self, analyzers):
        """Test source detection with quote extraction."""
        text = '"The economy is strong," said Fed Chair Jerome Powell in a statement.'

        source_result = analyzers["sources"].analyze(text)
        quote_result = analyzers["quotes"].analyze(text)

        # Should detect named source
        assert source_result.get("has_named_source") is True or \
               source_result.get("source_name") is not None or \
               len(source_result.get("sources", [])) > 0

        # Should detect quote
        assert quote_result.get("has_quote") is True or \
               len(quote_result.get("quotes", [])) > 0

    def test_unnamed_source_detection(self, analyzers):
        """Test detection of unnamed sources."""
        text = "Sources familiar with the matter say the deal is close."

        source_result = analyzers["sources"].analyze(text)

        # Should detect unnamed source
        assert source_result.get("has_unnamed_source") is True or \
               source_result.get("has_anonymous_source") is True or \
               "unnamed" in str(source_result).lower()


class TestAnalyzerConsistency:
    """Tests for analyzer consistency across inputs."""

    @pytest.fixture
    def filler_detector(self):
        """Create filler detector."""
        return FillerDetector()

    @pytest.fixture
    def speculation_detector(self):
        """Create speculation detector."""
        return SpeculationDetector()

    @pytest.fixture
    def emotional_detector(self):
        """Create emotional detector."""
        return EmotionalDetector()

    def test_filler_detection_consistency(self, filler_detector):
        """Test that filler detection is consistent."""
        filler_phrases = [
            "Here's what you need to know",
            "What happened next will surprise you",
            "Stay tuned for more updates",
            "But that's not all",
        ]

        for phrase in filler_phrases:
            result = filler_detector.analyze(phrase)
            assert result["is_filler"] is True, f"Failed to detect filler: {phrase}"

    def test_speculation_detection_consistency(self, speculation_detector):
        """Test that speculation detection is consistent."""
        speculative_phrases = [
            "This could potentially indicate a change",
            "Experts suggest this might be significant",
            "It would appear that markets may react",
            "The decision could signal future shifts",
        ]

        for phrase in speculative_phrases:
            result = speculation_detector.analyze(phrase)
            assert result["is_speculative"] is True, f"Failed to detect speculation: {phrase}"

    def test_emotional_detection_consistency(self, emotional_detector):
        """Test that emotional detection is consistent."""
        emotional_phrases = [
            "This is a shocking development",
            "The unprecedented announcement alarmed experts",
            "A stunning revelation emerged today",
            "The bombshell news sent shockwaves",
        ]

        for phrase in emotional_phrases:
            result = emotional_detector.analyze(phrase)
            assert result["has_emotional_language"] is True, f"Failed to detect emotion: {phrase}"

    def test_false_positive_resistance(self, filler_detector, speculation_detector, emotional_detector):
        """Test that analyzers don't produce false positives on clean text."""
        clean_sentences = [
            "The company reported $5 billion in revenue.",
            "CEO John Smith confirmed the merger.",
            "Stock prices increased by 2.5% today.",
            "The Federal Reserve raised rates by 0.25%.",
            "Unemployment fell to 3.5% in January.",
        ]

        for sentence in clean_sentences:
            filler = filler_detector.analyze(sentence)
            spec = speculation_detector.analyze(sentence)
            emotional = emotional_detector.analyze(sentence)

            assert filler["is_filler"] is False, f"False filler positive: {sentence}"
            assert spec["is_speculative"] is False, f"False speculation positive: {sentence}"
            assert emotional["has_emotional_language"] is False, f"False emotional positive: {sentence}"


class TestAnalyzerEdgeCases:
    """Tests for analyzer edge cases."""

    @pytest.fixture
    def all_analyzers(self):
        """Create all analyzers."""
        return [
            FillerDetector(),
            SpeculationDetector(),
            EmotionalDetector(),
            SourceDetector(),
            QuoteExtractor(),
        ]

    def test_empty_input(self, all_analyzers):
        """Test that all analyzers handle empty input."""
        for analyzer in all_analyzers:
            result = analyzer.analyze("")
            assert isinstance(result, dict)

    def test_single_word_input(self, all_analyzers):
        """Test that all analyzers handle single word input."""
        for analyzer in all_analyzers:
            result = analyzer.analyze("Hello")
            assert isinstance(result, dict)

    def test_very_long_input(self, all_analyzers):
        """Test that all analyzers handle very long input."""
        long_text = "The company announced results. " * 100

        for analyzer in all_analyzers:
            result = analyzer.analyze(long_text)
            assert isinstance(result, dict)

    def test_special_characters(self, all_analyzers):
        """Test that all analyzers handle special characters."""
        text = "Stock rose 15% to $123.45! CEO: 'Amazing!' #success"

        for analyzer in all_analyzers:
            result = analyzer.analyze(text)
            assert isinstance(result, dict)

    def test_unicode_input(self, all_analyzers):
        """Test that all analyzers handle unicode."""
        text = "会社は利益を発表した。L'entreprise a annoncé des bénéfices."

        for analyzer in all_analyzers:
            result = analyzer.analyze(text)
            assert isinstance(result, dict)

    def test_mixed_content(self, all_analyzers):
        """Test analyzers on mixed content with all patterns."""
        text = (
            "Here's what you need to know about this shocking story. "
            "The company could potentially announce changes, sources say. "
            '"This is significant," said CEO John Smith. '
            "Stay tuned for more unprecedented developments."
        )

        for analyzer in all_analyzers:
            result = analyzer.analyze(text)
            assert isinstance(result, dict)
