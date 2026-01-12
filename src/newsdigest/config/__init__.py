"""Configuration management for NewsDigest."""

from newsdigest.config.secrets import (
    AWSSecretsManager,
    EnvLoader,
    SecretMasker,
    SecretsManager,
    SecretValue,
    get_env,
    get_env_loader,
    get_secret,
    get_secret_masker,
    init_env,
    mask_secrets,
    register_secret,
)
from newsdigest.config.settings import Config


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
