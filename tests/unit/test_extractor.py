"""Tests for the core Extractor class."""

import pytest

from newsdigest.core.extractor import Extractor
from newsdigest.config.settings import Config
from newsdigest.core.article import Article, SourceType


class TestExtractorInitialization:
    """Tests for Extractor initialization."""

    def test_extractor_initialization(self, default_config: Config) -> None:
        """Test that Extractor initializes correctly."""
        extractor = Extractor(config=default_config)
        assert extractor.config == default_config
        assert extractor.mode == "standard"

    def test_extractor_default_config(self) -> None:
        """Test that Extractor uses default config when none provided."""
        extractor = Extractor()
        assert extractor.config is not None
        assert extractor.mode == "standard"

    def test_extractor_custom_mode(self) -> None:
        """Test that Extractor accepts custom mode."""
        extractor = Extractor(mode="aggressive")
        assert extractor.mode == "aggressive"

    def test_extractor_conservative_mode(self) -> None:
        """Test that Extractor accepts conservative mode."""
        extractor = Extractor(mode="conservative")
        assert extractor.mode == "conservative"


class TestExtractorURLDetection:
    """Tests for URL detection in Extractor."""

    def test_is_url_http(self) -> None:
        """Test HTTP URL detection."""
        extractor = Extractor()
        assert extractor._is_url("http://example.com") is True

    def test_is_url_https(self) -> None:
        """Test HTTPS URL detection."""
        extractor = Extractor()
        assert extractor._is_url("https://example.com/path") is True

    def test_is_url_plain_text(self) -> None:
        """Test that plain text is not detected as URL."""
        extractor = Extractor()
        assert extractor._is_url("This is just text") is False

    def test_is_url_ftp_rejected(self) -> None:
        """Test that FTP URLs are rejected."""
        extractor = Extractor()
        assert extractor._is_url("ftp://example.com") is False

    def test_is_url_empty_string(self) -> None:
        """Test empty string handling."""
        extractor = Extractor()
        assert extractor._is_url("") is False

    def test_is_url_with_query_params(self) -> None:
        """Test URL with query parameters."""
        extractor = Extractor()
        assert extractor._is_url("https://example.com/path?foo=bar&baz=1") is True


class TestExtractorRSSDetection:
    """Tests for RSS feed detection in Extractor."""

    def test_looks_like_rss_feed_path(self) -> None:
        """Test /feed path detection."""
        extractor = Extractor()
        assert extractor._looks_like_rss("https://example.com/feed") is True

    def test_looks_like_rss_rss_path(self) -> None:
        """Test /rss path detection."""
        extractor = Extractor()
        assert extractor._looks_like_rss("https://example.com/rss") is True

    def test_looks_like_rss_atom_path(self) -> None:
        """Test /atom path detection."""
        extractor = Extractor()
        assert extractor._looks_like_rss("https://example.com/atom.xml") is True

    def test_looks_like_rss_xml_extension(self) -> None:
        """Test .xml extension detection."""
        extractor = Extractor()
        assert extractor._looks_like_rss("https://example.com/news.xml") is True

    def test_looks_like_rss_regular_url(self) -> None:
        """Test regular URL is not RSS."""
        extractor = Extractor()
        assert extractor._looks_like_rss("https://example.com/article") is False


class TestExtractorFormatting:
    """Tests for Extractor formatting methods."""

    def test_format_unknown_raises(self, sample_extraction_result) -> None:
        """Test that unknown format raises ValueError."""
        extractor = Extractor()
        with pytest.raises(ValueError, match="Unknown format"):
            extractor.format(sample_extraction_result, format="unknown")

    def test_format_markdown(self, sample_extraction_result) -> None:
        """Test markdown formatting."""
        extractor = Extractor()
        result = extractor.format(sample_extraction_result, format="markdown")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_json(self, sample_extraction_result) -> None:
        """Test JSON formatting."""
        extractor = Extractor()
        result = extractor.format(sample_extraction_result, format="json")
        assert isinstance(result, str)
        # Should be valid JSON
        import json
        parsed = json.loads(result)
        assert "text" in parsed or "claims" in parsed

    def test_format_text(self, sample_extraction_result) -> None:
        """Test text formatting."""
        extractor = Extractor()
        result = extractor.format(sample_extraction_result, format="text")
        assert isinstance(result, str)

    def test_format_case_insensitive(self, sample_extraction_result) -> None:
        """Test that format is case-insensitive."""
        extractor = Extractor()
        result1 = extractor.format(sample_extraction_result, format="MARKDOWN")
        result2 = extractor.format(sample_extraction_result, format="markdown")
        assert result1 == result2


class TestExtractorConfigBuild:
    """Tests for Extractor configuration building."""

    def test_build_config_dict(self) -> None:
        """Test that config dict is built correctly."""
        config = Config()
        extractor = Extractor(config=config)

        config_dict = extractor._config_dict

        assert "extraction" in config_dict
        assert "output" in config_dict
        assert "spacy_model" in config_dict
        assert config_dict["extraction"]["mode"] == "standard"

    def test_build_config_dict_aggressive_mode(self) -> None:
        """Test config dict with aggressive mode."""
        config = Config()
        extractor = Extractor(config=config, mode="aggressive")

        config_dict = extractor._config_dict

        assert config_dict["extraction"]["mode"] == "aggressive"
