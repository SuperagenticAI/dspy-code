"""
Model manager for handling different language model providers.
"""

from typing import Any

import requests
from rich.console import Console

from ..core.config import ConfigManager
from ..core.exceptions import ModelError
from ..core.logging import get_logger

# from ..validation import ConfigValidator  # Not implemented yet

console = Console()
logger = get_logger(__name__)


class ModelManager:
    """Manages connections to different language model providers."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        # self.validator = ConfigValidator()  # Not implemented yet
        self._clients = {}

    def get_active_model(self):
        """Get the currently active model client."""
        default_model = self.config_manager.config.default_model

        if not default_model:
            raise ModelError("No default model configured")

        # Determine provider from model name
        provider = self._get_provider_for_model(default_model)

        if provider not in self._clients:
            self._clients[provider] = self._create_client(provider)

        return self._clients[provider]

    def test_model(self, model_name: str) -> tuple[bool, str]:
        """
        Test connectivity to a specific model.

        Args:
            model_name: Name of the model to test

        Returns:
            Tuple of (success, message)
        """
        try:
            provider = self._get_provider_for_model(model_name)

            if provider == "ollama":
                return self._test_ollama_model(model_name)
            elif provider == "openai":
                return self._test_openai_model()
            elif provider == "anthropic":
                return self._test_anthropic_model()
            elif provider == "gemini":
                return self._test_gemini_model()
            else:
                return False, f"Unknown provider for model: {model_name}"

        except Exception as e:
            logger.error(f"Model test failed: {e}")
            return False, str(e)

    def is_model_configured(self, model_name: str) -> bool:
        """Check if a model is properly configured."""
        try:
            provider = self._get_provider_for_model(model_name)
            config = self.config_manager.get_model_config(provider)

            if provider == "ollama":
                return model_name in config.get("models", [])
            else:
                return config.get("api_key") is not None

        except Exception:
            return False

    def get_model_info(self, model_name: str) -> dict[str, Any] | None:
        """Get information about a model."""
        try:
            provider = self._get_provider_for_model(model_name)
            config = self.config_manager.get_model_config(provider)

            info = {
                "name": model_name,
                "provider": provider,
                "configured": self.is_model_configured(model_name),
            }

            if provider == "ollama":
                info["endpoint"] = config.get("endpoint")
                info["type"] = "local"
            else:
                info["type"] = "cloud"
                info["has_api_key"] = bool(config.get("api_key"))

            return info

        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None

    def _get_provider_for_model(self, model_name: str) -> str:
        """Determine provider from model name."""
        config = self.config_manager.config.models

        # Check Ollama models
        if model_name in config.ollama_models:
            return "ollama"

        # Check cloud models
        if model_name == config.openai_model:
            return "openai"
        elif model_name == config.anthropic_model:
            return "anthropic"
        elif model_name == config.gemini_model:
            return "gemini"

        # Default guessing based on model name patterns
        if model_name.startswith("gpt"):
            return "openai"
        elif model_name.startswith("claude"):
            return "anthropic"
        elif model_name.startswith("gemini"):
            return "gemini"
        else:
            return "ollama"  # Default to Ollama for unknown models

    def _create_client(self, provider: str):
        """Create a client for the specified provider."""
        config = self.config_manager.get_model_config(provider)

        if provider == "ollama":
            return self._create_ollama_client(config)
        elif provider == "openai":
            return self._create_openai_client(config)
        elif provider == "anthropic":
            return self._create_anthropic_client(config)
        elif provider == "gemini":
            return self._create_gemini_client(config)
        else:
            raise ModelError(f"Unknown provider: {provider}")

    def _create_ollama_client(self, config: dict[str, Any]):
        """Create Ollama client."""
        try:
            # Simple HTTP client for Ollama
            class OllamaClient:
                def __init__(self, endpoint):
                    self.endpoint = endpoint.rstrip("/")

                def generate(self, model, prompt):
                    response = requests.post(
                        f"{self.endpoint}/api/generate",
                        json={"model": model, "prompt": prompt, "stream": False},
                        timeout=30,
                    )
                    response.raise_for_status()
                    return response.json()["response"]

            return OllamaClient(config["endpoint"])

        except Exception as e:
            raise ModelError(f"Failed to create Ollama client: {e}")

    def _create_openai_client(self, config: dict[str, Any]):
        """Create OpenAI client."""
        try:
            import openai

            client = openai.OpenAI(api_key=config["api_key"])
            return client

        except ImportError:
            raise ModelError("OpenAI library not installed. Run: pip install openai")
        except Exception as e:
            raise ModelError(f"Failed to create OpenAI client: {e}")

    def _create_anthropic_client(self, config: dict[str, Any]):
        """Create Anthropic client."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=config["api_key"])
            return client

        except ImportError:
            raise ModelError("Anthropic library not installed. Run: pip install anthropic")
        except Exception as e:
            raise ModelError(f"Failed to create Anthropic client: {e}")

    def _create_gemini_client(self, config: dict[str, Any]):
        """Create Gemini client."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=config["api_key"])
            return genai

        except ImportError:
            raise ModelError(
                "Google Generative AI library not installed. Run: pip install google-generativeai"
            )
        except Exception as e:
            raise ModelError(f"Failed to create Gemini client: {e}")

    def _test_ollama_model(self, model_name: str) -> tuple[bool, str]:
        """Test Ollama model connectivity."""
        try:
            config = self.config_manager.get_model_config("ollama")
            endpoint = config["endpoint"]

            # Test endpoint connectivity
            response = requests.get(f"{endpoint}/api/tags", timeout=10)
            response.raise_for_status()

            # Check if model is available
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]

            if model_name in model_names:
                return True, "Model is available and accessible"
            else:
                return (
                    False,
                    f"Model '{model_name}' not found. Available: {', '.join(model_names[:5])}",
                )

        except requests.exceptions.ConnectionError:
            return False, f"Cannot connect to Ollama at {config['endpoint']}"
        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except Exception as e:
            return False, f"Connection failed: {e}"

    def _test_openai_model(self) -> tuple[bool, str]:
        """Test OpenAI model connectivity."""
        try:
            config = self.config_manager.get_model_config("openai")

            if not config.get("api_key"):
                return False, "No API key configured"

            import openai

            client = openai.OpenAI(api_key=config["api_key"])

            # Test with a simple completion
            response = client.chat.completions.create(
                model=config["model"], messages=[{"role": "user", "content": "Hello"}], max_tokens=5
            )

            return True, "API key valid and model accessible"

        except ImportError:
            return False, "OpenAI library not installed"
        except Exception as e:
            error_msg = str(e).lower()
            if "api key" in error_msg or "authentication" in error_msg:
                return False, "Invalid API key"
            elif "model" in error_msg:
                return False, f"Model '{config['model']}' not accessible"
            else:
                return False, f"Connection failed: {e}"

    def _test_anthropic_model(self) -> tuple[bool, str]:
        """Test Anthropic model connectivity."""
        try:
            config = self.config_manager.get_model_config("anthropic")

            if not config.get("api_key"):
                return False, "No API key configured"

            import anthropic

            client = anthropic.Anthropic(api_key=config["api_key"])

            # Test with a simple message
            response = client.messages.create(
                model=config["model"], max_tokens=5, messages=[{"role": "user", "content": "Hello"}]
            )

            return True, "API key valid and model accessible"

        except ImportError:
            return False, "Anthropic library not installed"
        except Exception as e:
            error_msg = str(e).lower()
            if "api key" in error_msg or "authentication" in error_msg:
                return False, "Invalid API key"
            elif "model" in error_msg:
                return False, f"Model '{config['model']}' not accessible"
            else:
                return False, f"Connection failed: {e}"

    def _test_gemini_model(self) -> tuple[bool, str]:
        """Test Gemini model connectivity."""
        try:
            config = self.config_manager.get_model_config("gemini")

            if not config.get("api_key"):
                return False, "No API key configured"

            import google.generativeai as genai

            genai.configure(api_key=config["api_key"])
            model = genai.GenerativeModel(config["model"])

            # Test with a simple prompt
            response = model.generate_content("Hello")

            return True, "API key valid and model accessible"

        except ImportError:
            return False, "Google Generative AI library not installed"
        except Exception as e:
            error_msg = str(e).lower()
            if "api key" in error_msg or "authentication" in error_msg:
                return False, "Invalid API key"
            elif "model" in error_msg:
                return False, f"Model '{config['model']}' not accessible"
            else:
                return False, f"Connection failed: {e}"
