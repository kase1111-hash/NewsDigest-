"""Tests for the core Extractor class."""

import pytest

from newsdigest.core.extractor import Extractor
from newsdigest.config.settings import Config


class TestExtractor:
    """Tests for Extractor class."""

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

    def test_extractor_invalid_mode_accepted(self) -> None:
        """Test that invalid modes are accepted (validation happens elsewhere)."""
        extractor = Extractor(mode="invalid")
        assert extractor.mode == "invalid"

    @pytest.mark.asyncio
    async def test_extract_not_implemented(self) -> None:
        """Test that extract raises NotImplementedError."""
        extractor = Extractor()
        with pytest.raises(NotImplementedError):
            await extractor.extract("https://example.com")

    @pytest.mark.asyncio
    async def test_extract_batch_not_implemented(self) -> None:
        """Test that extract_batch raises NotImplementedError."""
        extractor = Extractor()
        with pytest.raises(NotImplementedError):
            await extractor.extract_batch(["https://example.com"])

    def test_compare_not_implemented(self) -> None:
        """Test that compare raises NotImplementedError."""
        extractor = Extractor()
        with pytest.raises(NotImplementedError):
            extractor.compare("https://example.com")
