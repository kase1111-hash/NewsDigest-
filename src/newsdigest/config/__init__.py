"""Configuration management for NewsDigest."""

from newsdigest.config.environments import (
    Environment,
    apply_env_file,
    detect_environment,
    get_config_path,
    get_env_file_path,
    get_environment_info,
    is_development,
    is_production,
    is_staging,
    is_test,
    load_config,
    load_env_file,
)
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
    # Environment management
    "Environment",
    "detect_environment",
    "load_config",
    "get_config_path",
    "get_env_file_path",
    "load_env_file",
    "apply_env_file",
    "get_environment_info",
    "is_development",
    "is_staging",
    "is_production",
    "is_test",
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
