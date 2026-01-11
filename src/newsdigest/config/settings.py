"""Configuration settings for NewsDigest."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExtractionConfig(BaseModel):
    """Extraction-related settings."""

    mode: str = "standard"  # conservative, standard, aggressive
    min_sentence_density: float = 0.3
    unnamed_sources: str = "flag"  # keep, flag, remove
    speculation: str = "remove"  # keep, flag, remove
    max_hedges_per_sentence: int = 2
    emotional_language: str = "remove"  # keep, flag, remove


class DigestConfig(BaseModel):
    """Digest-related settings."""

    period: str = "24h"
    max_items: int = 100
    clustering_enabled: bool = True
    deduplication_enabled: bool = True
    similarity_threshold: float = 0.85
    min_novelty_score: float = 0.3


class OutputConfig(BaseModel):
    """Output-related settings."""

    format: str = "markdown"  # markdown, html, json, text
    show_stats: bool = True
    include_links: bool = True
    show_warnings: bool = True


class Config(BaseModel):
    """Main configuration for NewsDigest."""

    # Paths
    config_dir: Path = Field(default_factory=lambda: Path.home() / ".newsdigest")

    # Component configs
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    digest: DigestConfig = Field(default_factory=DigestConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)

    # Sources
    sources: List[Dict[str, Any]] = Field(default_factory=list)

    # NLP settings
    spacy_model: str = "en_core_web_sm"

    # HTTP settings
    http_timeout: int = 30
    http_retries: int = 3
    requests_per_second: float = 1.0

    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 3600
    cache_max_size: int = 1000

    @classmethod
    def from_file(cls, path: str | Path) -> "Config":
        """Load configuration from YAML file."""
        import yaml

        path = Path(path)
        if not path.exists():
            return cls()

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        return cls(**data)

    def save(self, path: Optional[str | Path] = None) -> None:
        """Save configuration to YAML file."""
        import yaml

        path = Path(path) if path else self.config_dir / "config.yml"
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)
