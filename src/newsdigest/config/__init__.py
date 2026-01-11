"""Configuration management for NewsDigest."""

from newsdigest.config.settings import Config
from newsdigest.config.secrets import (
    AWSSecretsManager,
    EnvLoader,
    SecretMasker,
    SecretValue,
    SecretsManager,
    get_env,
    get_env_loader,
    get_secret,
    get_secret_masker,
    init_env,
    mask_secrets,
    register_secret,
)

__all__ = [
    "Config",
    # Secrets management
    "SecretValue",
    "EnvLoader",
    "SecretsManager",
    "AWSSecretsManager",
    "SecretMasker",
    "get_env_loader",
    "init_env",
    "get_secret_masker",
    "get_env",
    "get_secret",
    "mask_secrets",
    "register_secret",
]
