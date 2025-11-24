"""
Configuration validation for DSPy Code.

This module provides validation for API keys, model configurations,
and project settings.
"""

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .exceptions import ConfigurationError


class ConfigValidator:
    """Validates configuration settings for DSPy Code."""

    # API key patterns for different providers
    API_KEY_PATTERNS = {
        "openai": re.compile(r"^sk-[a-zA-Z0-9]{48}$"),
        "anthropic": re.compile(r"^sk-ant-[a-zA-Z0-9\-_]{95,}$"),
        "gemini": re.compile(r"^AIza[a-zA-Z0-9\-_]{35}$"),
    }

    # Valid model names for each provider
    VALID_MODELS = {
        "openai": {
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4-0125-preview",
            "gpt-4-1106-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-instruct",
        },
        "anthropic": {
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2",
        },
        "gemini": {
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.0-pro",
            "gemini-1.0-pro-001",
            "gemini-1.0-pro-latest",
            "gemini-1.0-pro-vision-latest",
        },
        "ollama": set(),  # Ollama models are dynamic, so we don't validate specific names
    }

    def __init__(self):
        pass

    def validate_api_key(self, provider: str, api_key: str) -> str:
        """
        Validate API key format for a specific provider.

        Args:
            provider: The model provider (openai, anthropic, gemini)
            api_key: The API key to validate

        Returns:
            Validated API key

        Raises:
            ConfigurationError: If validation fails
        """
        if not provider or not provider.strip():
            raise ConfigurationError("Provider cannot be empty")

        if not api_key or not api_key.strip():
            raise ConfigurationError("API key cannot be empty")

        provider = provider.lower().strip()
        api_key = api_key.strip()

        if provider not in self.API_KEY_PATTERNS:
            raise ConfigurationError(f"Unknown provider '{provider}'")

        pattern = self.API_KEY_PATTERNS[provider]
        if not pattern.match(api_key):
            raise ConfigurationError(
                f"Invalid API key format for {provider}. Please check your API key and try again."
            )

        return api_key

    def validate_model_name(self, provider: str, model: str) -> str:
        """
        Validate model name for a specific provider.

        Args:
            provider: The model provider
            model: The model name to validate

        Returns:
            Validated model name

        Raises:
            ConfigurationError: If validation fails
        """
        if not provider or not provider.strip():
            raise ConfigurationError("Provider cannot be empty")

        if not model or not model.strip():
            raise ConfigurationError("Model name cannot be empty")

        provider = provider.lower().strip()
        model = model.strip()

        if provider not in self.VALID_MODELS:
            raise ConfigurationError(f"Unknown provider '{provider}'")

        # For Ollama, we don't validate specific model names since they're dynamic
        if provider == "ollama":
            if not re.match(r"^[a-zA-Z0-9\-_.:]+$", model):
                raise ConfigurationError(
                    f"Invalid Ollama model name '{model}'. "
                    "Model names can only contain letters, numbers, hyphens, underscores, dots, and colons."
                )
            return model

        valid_models = self.VALID_MODELS[provider]
        if model not in valid_models:
            raise ConfigurationError(
                f"Invalid model '{model}' for provider '{provider}'. "
                f"Valid models: {', '.join(sorted(valid_models))}"
            )

        return model

    def validate_endpoint_url(self, url: str) -> str:
        """
        Validate endpoint URL format.

        Args:
            url: The endpoint URL to validate

        Returns:
            Validated URL

        Raises:
            ConfigurationError: If validation fails
        """
        if not url or not url.strip():
            raise ConfigurationError("Endpoint URL cannot be empty")

        url = url.strip()

        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ConfigurationError(f"Invalid URL format: {e}")

        if not parsed.scheme:
            raise ConfigurationError("URL must include a scheme (http:// or https://)")

        if parsed.scheme not in ("http", "https"):
            raise ConfigurationError("URL scheme must be http or https")

        if not parsed.netloc:
            raise ConfigurationError("URL must include a hostname")

        # Check for localhost/private IPs for Ollama
        if parsed.hostname in ("localhost", "127.0.0.1", "0.0.0.0"):
            return url

        # For remote URLs, require HTTPS
        if parsed.scheme != "https":
            raise ConfigurationError("Remote URLs must use HTTPS")

        return url

    def validate_project_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Validate complete project configuration.

        Args:
            config: The project configuration to validate

        Returns:
            Validated configuration

        Raises:
            ConfigurationError: If validation fails
        """
        if not isinstance(config, dict):
            raise ConfigurationError("Configuration must be a dictionary")

        validated_config = {}

        # Validate required fields
        required_fields = ["name", "version", "dspy_version"]
        for field in required_fields:
            if field not in config:
                raise ConfigurationError(f"Missing required field: {field}")
            validated_config[field] = self._validate_config_field(field, config[field])

        # Validate optional fields
        optional_fields = {
            "models": self._validate_models_config,
            "default_model": self._validate_default_model,
            "gepa_config": self._validate_gepa_config,
            "output_directory": self._validate_output_directory,
            "template_preferences": self._validate_template_preferences,
        }

        for field, validator in optional_fields.items():
            if field in config:
                validated_config[field] = validator(config[field])

        return validated_config

    def validate_models_config(self, models_config: dict[str, Any]) -> dict[str, Any]:
        """
        Validate models configuration section.

        Args:
            models_config: The models configuration to validate

        Returns:
            Validated models configuration

        Raises:
            ConfigurationError: If validation fails
        """
        if not isinstance(models_config, dict):
            raise ConfigurationError("Models configuration must be a dictionary")

        validated_config = {}

        # Validate Ollama configuration
        if "ollama_endpoint" in models_config:
            validated_config["ollama_endpoint"] = self.validate_endpoint_url(
                models_config["ollama_endpoint"]
            )

        if "ollama_models" in models_config:
            if not isinstance(models_config["ollama_models"], list):
                raise ConfigurationError("ollama_models must be a list")
            validated_config["ollama_models"] = [
                self.validate_model_name("ollama", model)
                for model in models_config["ollama_models"]
            ]

        # Validate cloud provider configurations
        cloud_providers = ["anthropic", "openai", "gemini"]
        for provider in cloud_providers:
            api_key_field = f"{provider}_api_key"
            model_field = f"{provider}_model"

            if api_key_field in models_config:
                validated_config[api_key_field] = self.validate_api_key(
                    provider, models_config[api_key_field]
                )

            if model_field in models_config:
                validated_config[model_field] = self.validate_model_name(
                    provider, models_config[model_field]
                )

        return validated_config

    def validate_gepa_config(self, gepa_config: dict[str, Any]) -> dict[str, Any]:
        """
        Validate GEPA optimizer configuration.

        Args:
            gepa_config: The GEPA configuration to validate

        Returns:
            Validated GEPA configuration

        Raises:
            ConfigurationError: If validation fails
        """
        if not isinstance(gepa_config, dict):
            raise ConfigurationError("GEPA configuration must be a dictionary")

        validated_config = {}

        # Validate numeric parameters
        numeric_params = {
            "max_iterations": (1, 1000),
            "population_size": (2, 200),
            "mutation_rate": (0.0, 1.0),
            "crossover_rate": (0.0, 1.0),
        }

        for param, (min_val, max_val) in numeric_params.items():
            if param in gepa_config:
                value = gepa_config[param]
                if not isinstance(value, (int, float)):
                    raise ConfigurationError(f"{param} must be a number")
                if not min_val <= value <= max_val:
                    raise ConfigurationError(f"{param} must be between {min_val} and {max_val}")
                validated_config[param] = value

        # Validate evaluation metric
        if "evaluation_metric" in gepa_config:
            metric = gepa_config["evaluation_metric"]
            valid_metrics = {"accuracy", "f1", "precision", "recall", "bleu", "rouge"}
            if metric not in valid_metrics:
                raise ConfigurationError(
                    f"Invalid evaluation metric '{metric}'. "
                    f"Valid options: {', '.join(sorted(valid_metrics))}"
                )
            validated_config["evaluation_metric"] = metric

        return validated_config

    def _validate_config_field(self, field: str, value: Any) -> Any:
        """Validate individual configuration fields."""
        if field == "name":
            if not isinstance(value, str) or not value.strip():
                raise ConfigurationError("Project name must be a non-empty string")
            return value.strip()

        elif field == "version":
            if not isinstance(value, str) or not value.strip():
                raise ConfigurationError("Version must be a non-empty string")
            # Validate semantic version format
            if not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9\-]+)?$", value.strip()):
                raise ConfigurationError("Version must follow semantic versioning (e.g., 1.0.0)")
            return value.strip()

        elif field == "dspy_version":
            if not isinstance(value, str) or not value.strip():
                raise ConfigurationError("DSPy version must be a non-empty string")
            return value.strip()

        else:
            return value

    def _validate_models_config(self, models_config: Any) -> dict[str, Any]:
        """Validate models configuration."""
        return self.validate_models_config(models_config)

    def _validate_default_model(self, default_model: Any) -> str:
        """Validate default model setting."""
        if not isinstance(default_model, str) or not default_model.strip():
            raise ConfigurationError("Default model must be a non-empty string")
        return default_model.strip()

    def _validate_gepa_config(self, gepa_config: Any) -> dict[str, Any]:
        """Validate GEPA configuration."""
        return self.validate_gepa_config(gepa_config)

    def _validate_output_directory(self, output_dir: Any) -> str:
        """Validate output directory setting."""
        if not isinstance(output_dir, str) or not output_dir.strip():
            raise ConfigurationError("Output directory must be a non-empty string")

        # Validate path format
        try:
            path = Path(output_dir.strip())
            if path.is_absolute():
                raise ConfigurationError("Output directory must be a relative path")
            return str(path)
        except Exception as e:
            raise ConfigurationError(f"Invalid output directory path: {e}")

    def _validate_template_preferences(self, preferences: Any) -> dict[str, Any]:
        """Validate template preferences."""
        if not isinstance(preferences, dict):
            raise ConfigurationError("Template preferences must be a dictionary")
        return preferences
