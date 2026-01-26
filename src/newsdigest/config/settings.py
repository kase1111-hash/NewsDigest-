"""Configuration settings for NewsDigest."""

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class QuotesConfig(BaseModel):
    """Quote handling settings."""

    keep_attributed: bool = True
    keep_unattributed: bool = False
    flag_circular: bool = True


class ExtractionConfig(BaseModel):
    """Extraction-related settings."""

    mode: str = "standard"  # conservative, standard, aggressive
    min_sentence_density: float = 0.3
    unnamed_sources: str = "flag"  # keep, flag, remove
    speculation: str = "remove"  # keep, flag, remove
    max_hedges_per_sentence: int = 2
    emotional_language: str = "remove"  # keep, flag, remove
    quotes: QuotesConfig = Field(default_factory=QuotesConfig)


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
    sources: list[dict[str, Any]] = Field(default_factory=list)

    # NLP settings
    spacy_model: str = "en_core_web_sm"

    # HTTP settings with bounds checking
    http_timeout: int = Field(default=30, ge=1, le=300)
    http_retries: int = Field(default=3, ge=0, le=10)
    requests_per_second: float = Field(default=1.0, gt=0, le=100)

    # Cache settings with bounds checking
    cache_enabled: bool = True
    cache_ttl: int = Field(default=3600, ge=0, le=86400)  # Max 24 hours
    cache_max_size: int = Field(default=1000, ge=1, le=100000)

    # CORS settings for API
    cors_origins: list[str] = Field(default_factory=list)

    @classmethod
    def from_file(cls, path: str | Path) -> "Config":
        """Load configuration from YAML file.

        Args:
            path: Path to YAML configuration file.

        Returns:
            Config instance.
        """
        import yaml

        path = Path(path)
        if not path.exists():
            return cls()

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        return cls(**data)

    @classmethod
    def from_env(cls, prefix: str = "NEWSDIGEST_") -> "Config":
        """Load configuration from environment variables.

        Supports the following environment variables:
        - NEWSDIGEST_MODE: Extraction mode (conservative, standard, aggressive)
        - NEWSDIGEST_SPACY_MODEL: spaCy model name
        - NEWSDIGEST_HTTP_TIMEOUT: HTTP timeout in seconds
        - NEWSDIGEST_HTTP_RETRIES: Number of HTTP retries
        - NEWSDIGEST_REQUESTS_PER_SECOND: Rate limit
        - NEWSDIGEST_CACHE_ENABLED: Enable caching (true/false)
        - NEWSDIGEST_CACHE_TTL: Cache TTL in seconds
        - NEWSDIGEST_OUTPUT_FORMAT: Output format (markdown, json, text)
        - NEWSDIGEST_SIMILARITY_THRESHOLD: Similarity threshold for dedup
        - SENTRY_DSN: Sentry DSN for error reporting

        Args:
            prefix: Environment variable prefix.

        Returns:
            Config instance.
        """
        def get_env(key: str, default: str = "") -> str:
            return os.environ.get(f"{prefix}{key}", os.environ.get(key, default))

        def get_env_bool(key: str, default: bool = False) -> bool:
            val = get_env(key, str(default).lower())
            return val.lower() in ("true", "1", "yes", "on")

        def get_env_int(key: str, default: int) -> int:
            try:
                return int(get_env(key, str(default)))
            except ValueError:
                return default

        def get_env_float(key: str, default: float) -> float:
            try:
                return float(get_env(key, str(default)))
            except ValueError:
                return default

        # Build extraction config
        extraction = ExtractionConfig(
            mode=get_env("MODE", "standard"),
            min_sentence_density=get_env_float("MIN_SENTENCE_DENSITY", 0.3),
            unnamed_sources=get_env("UNNAMED_SOURCES", "flag"),
            speculation=get_env("SPECULATION", "remove"),
            max_hedges_per_sentence=get_env_int("MAX_HEDGES_PER_SENTENCE", 2),
            emotional_language=get_env("EMOTIONAL_LANGUAGE", "remove"),
            quotes=QuotesConfig(
                keep_attributed=get_env_bool("QUOTES_KEEP_ATTRIBUTED", True),
                keep_unattributed=get_env_bool("QUOTES_KEEP_UNATTRIBUTED", False),
                flag_circular=get_env_bool("QUOTES_FLAG_CIRCULAR", True),
            ),
        )

        # Build digest config
        digest = DigestConfig(
            period=get_env("DIGEST_PERIOD", "24h"),
            max_items=get_env_int("DIGEST_MAX_ITEMS", 100),
            clustering_enabled=get_env_bool("DIGEST_CLUSTERING", True),
            deduplication_enabled=get_env_bool("DIGEST_DEDUP", True),
            similarity_threshold=get_env_float("SIMILARITY_THRESHOLD", 0.85),
            min_novelty_score=get_env_float("MIN_NOVELTY_SCORE", 0.3),
        )

        # Build output config
        output = OutputConfig(
            format=get_env("OUTPUT_FORMAT", "markdown"),
            show_stats=get_env_bool("OUTPUT_SHOW_STATS", True),
            include_links=get_env_bool("OUTPUT_INCLUDE_LINKS", True),
            show_warnings=get_env_bool("OUTPUT_SHOW_WARNINGS", True),
        )

        return cls(
            extraction=extraction,
            digest=digest,
            output=output,
            spacy_model=get_env("SPACY_MODEL", "en_core_web_sm"),
            http_timeout=get_env_int("HTTP_TIMEOUT", 30),
            http_retries=get_env_int("HTTP_RETRIES", 3),
            requests_per_second=get_env_float("REQUESTS_PER_SECOND", 1.0),
            cache_enabled=get_env_bool("CACHE_ENABLED", True),
            cache_ttl=get_env_int("CACHE_TTL", 3600),
            cache_max_size=get_env_int("CACHE_MAX_SIZE", 1000),
        )

    def save(self, path: str | Path | None = None) -> None:
        """Save configuration to YAML file.

        Args:
            path: Path to save to. Defaults to config_dir/config.yml.
        """
        import yaml

        path = Path(path) if path else self.config_dir / "config.yml"
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)

    def to_env_vars(self, prefix: str = "NEWSDIGEST_") -> dict[str, str]:
        """Export configuration as environment variables.

        Args:
            prefix: Environment variable prefix.

        Returns:
            Dictionary of environment variable names to values.
        """
        return {
            f"{prefix}MODE": self.extraction.mode,
            f"{prefix}SPACY_MODEL": self.spacy_model,
            f"{prefix}HTTP_TIMEOUT": str(self.http_timeout),
            f"{prefix}HTTP_RETRIES": str(self.http_retries),
            f"{prefix}REQUESTS_PER_SECOND": str(self.requests_per_second),
            f"{prefix}CACHE_ENABLED": str(self.cache_enabled).lower(),
            f"{prefix}CACHE_TTL": str(self.cache_ttl),
            f"{prefix}OUTPUT_FORMAT": self.output.format,
            f"{prefix}SIMILARITY_THRESHOLD": str(self.digest.similarity_threshold),
        }
