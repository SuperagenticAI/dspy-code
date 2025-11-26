"""
LLM Connector for DSPy Code.

Handles connections to various language models (local and cloud-based)
to power the interactive CLI's natural language understanding and code generation.
"""

import os
from typing import Any

import requests

from ..core.config import ConfigManager
from ..core.exceptions import ModelError
from ..core.logging import get_logger

logger = get_logger(__name__)


class LLMConnector:
    """
    Manages connections to language models for CLI intelligence.

    Supports:
    - Local models via Ollama
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    - Google (Gemini)
    """

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.current_model = None
        self.model_type = None
        self.api_key = None

    def connect_to_model(
        self, model_name: str, model_type: str, api_key: str | None = None
    ) -> bool:
        """
        Connect to a specific model.

        Args:
            model_name: Name of the model (e.g., "llama2", "gpt-4")
            model_type: Type of model ("ollama", "openai", "anthropic", "gemini")
            api_key: API key for cloud models

        Returns:
            True if connection successful
        """
        try:
            if model_type == "ollama":
                return self._connect_ollama(model_name)
            elif model_type == "openai":
                return self._connect_openai(model_name, api_key)
            elif model_type == "anthropic":
                return self._connect_anthropic(model_name, api_key)
            elif model_type == "gemini":
                return self._connect_gemini(model_name, api_key)
            else:
                raise ModelError(f"Unsupported model type: {model_type}")

        except Exception as e:
            logger.error(f"Failed to connect to {model_name}: {e}")
            raise ModelError(f"Connection failed: {e}")

    def _connect_ollama(self, model_name: str) -> bool:
        """Connect to local Ollama model."""
        endpoint = self.config_manager.config.models.ollama_endpoint or "http://localhost:11434"

        try:
            # Check if Ollama is running
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            response.raise_for_status()

            # Check if model exists (support full names with tags like gpt-oss:120b)
            models = response.json().get("models", [])
            available_models = [m.get("name", "") for m in models]

            # Check exact match first (with tag)
            if model_name in available_models:
                self.current_model = model_name
                self.model_type = "ollama"
                self.api_key = None
                logger.info(f"Connected to Ollama model: {model_name}")
                return True

            # Check if model exists without tag (for backward compatibility)
            model_base_names = [m.split(":")[0] for m in available_models]
            if model_name in model_base_names:
                # Find the full name with tag
                for full_name in available_models:
                    if full_name.startswith(model_name + ":") or full_name == model_name:
                        self.current_model = full_name
                        self.model_type = "ollama"
                        self.api_key = None
                        logger.info(f"Connected to Ollama model: {full_name}")
                        return True

            # Model not found
            raise ModelError(
                f"Model '{model_name}' not found in Ollama.\n"
                f"Available models: {', '.join(available_models)}\n"
                f"Tip: Use full name with tag, e.g., 'gpt-oss:120b'"
            )

        except requests.exceptions.ConnectionError:
            raise ModelError("Cannot connect to Ollama. Is it running? Try: ollama serve")
        except Exception as e:
            raise ModelError(f"Ollama connection error: {e}")

    def _connect_openai(self, model_name: str, api_key: str | None) -> bool:
        """Connect to OpenAI model."""
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ModelError("OpenAI API key required. Set OPENAI_API_KEY or provide --api-key")

        # Validate API key format
        if not api_key.startswith("sk-"):
            raise ModelError("Invalid OpenAI API key format. Should start with 'sk-'")

        self.current_model = model_name
        self.model_type = "openai"
        self.api_key = api_key

        logger.info(f"Connected to OpenAI model: {model_name}")
        return True

    def _connect_anthropic(self, model_name: str, api_key: str | None) -> bool:
        """Connect to Anthropic Claude model."""
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ModelError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY or provide --api-key"
            )

        # Validate API key format
        if not api_key.startswith("sk-ant-"):
            raise ModelError("Invalid Anthropic API key format. Should start with 'sk-ant-'")

        self.current_model = model_name
        self.model_type = "anthropic"
        self.api_key = api_key

        logger.info(f"Connected to Anthropic model: {model_name}")
        return True

    def _connect_gemini(self, model_name: str, api_key: str | None) -> bool:
        """Connect to Google Gemini model."""
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ModelError("Gemini API key required. Set GEMINI_API_KEY or provide --api-key")

        # Validate API key format
        if not api_key.startswith("AIza"):
            raise ModelError("Invalid Gemini API key format. Should start with 'AIza'")

        self.current_model = model_name
        self.model_type = "gemini"
        self.api_key = api_key

        logger.info(f"Connected to Gemini model: {model_name}")
        return True

    def list_available_ollama_models(self) -> list[str]:
        """List all available Ollama models with full names including tags."""
        endpoint = self.config_manager.config.models.ollama_endpoint or "http://localhost:11434"

        try:
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            response.raise_for_status()

            models = response.json().get("models", [])
            # Return full model names with tags (e.g., gpt-oss:120b)
            return [m.get("name", "") for m in models]

        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

    def generate_response(
        self, prompt: str, system_prompt: str | None = None, context: dict[str, Any] | None = None
    ) -> str:
        """
        Generate a response from the connected model.

        Args:
            prompt: User's prompt
            system_prompt: System instructions
            context: Additional context (DSPy reference, conversation history, etc.)

        Returns:
            Model's response
        """
        if not self.current_model:
            raise ModelError("No model connected. Use /connect command first.")

        if self.model_type == "ollama":
            return self._generate_ollama(prompt, system_prompt, context)
        elif self.model_type == "openai":
            return self._generate_openai(prompt, system_prompt, context)
        elif self.model_type == "anthropic":
            return self._generate_anthropic(prompt, system_prompt, context)
        elif self.model_type == "gemini":
            return self._generate_gemini(prompt, system_prompt, context)
        else:
            raise ModelError(f"Unsupported model type: {self.model_type}")

    def _generate_ollama(
        self, prompt: str, system_prompt: str | None, context: dict[str, Any] | None
    ) -> str:
        """Generate response from Ollama."""
        endpoint = self.config_manager.config.models.ollama_endpoint or "http://localhost:11434"

        # Allow overriding the HTTP timeout for slow/large models via environment.
        # Default is 120s (2 minutes) to better support large models.
        try:
            from os import getenv

            timeout = int(getenv("OLLAMA_HTTP_TIMEOUT", "120"))
        except Exception:
            timeout = 120

        # Build the full prompt with context
        full_prompt = self._build_prompt_with_context(prompt, system_prompt, context)

        try:
            response = requests.post(
                f"{endpoint}/api/generate",
                json={"model": self.current_model, "prompt": full_prompt, "stream": False},
                timeout=timeout,
            )
            response.raise_for_status()

            return response.json().get("response", "")

        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise ModelError(f"Failed to generate response: {e}")

    def _generate_openai(
        self, prompt: str, system_prompt: str | None, context: dict[str, Any] | None
    ) -> str:
        """Generate response from OpenAI."""
        try:
            # Prefer the modern OpenAI client (openai>=1.0)
            try:
                from openai import OpenAI

                client = OpenAI(api_key=self.api_key)
                use_new_client = True
            except Exception:
                # Fallback to legacy interface for openai<1.0
                import openai  # type: ignore[import-not-found]

                openai.api_key = self.api_key
                client = openai
                use_new_client = False
        except ImportError as exc:
            raise ModelError(
                "OpenAI SDK not installed!\n"
                "Install it with: pip install \"openai>=2.8.1\"  # or newer 2.x version\n"
                "DSPy Code doesn't include provider SDKs by default - install only what you need."
            ) from exc

        messages: list[dict[str, str]] = []

        # Add system prompt with context
        if system_prompt or context:
            full_system = self._build_system_prompt_with_context(system_prompt, context)
            messages.append({"role": "system", "content": full_system})

        messages.append({"role": "user", "content": prompt})

        try:
            if use_new_client:
                # New style client for openai>=1.0
                # NOTE:
                # - Some newer models (e.g., gpt-5-nano) no longer accept `max_tokens`
                #   and instead expect `max_completion_tokens`.
                # - Some also only support the default temperature.
                # - To stay compatible across the whole model family, we omit
                #   these tuning params and let the API use its defaults.
                response = client.chat.completions.create(
                    model=self.current_model,
                    messages=messages,
                )
                return response.choices[0].message.content or ""

            # Legacy interface for openai<1.0
            response = client.ChatCompletion.create(
                model=self.current_model,
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content  # type: ignore[no-any-return]

        except Exception as e:  # pragma: no cover - depends on external SDK behaviour
            logger.error(f"OpenAI generation error: {e}")
            raise ModelError(f"Failed to generate response: {e}")

    def _generate_anthropic(
        self, prompt: str, system_prompt: str | None, context: dict[str, Any] | None
    ) -> str:
        """Generate response from Anthropic."""
        try:
            import anthropic
        except ImportError:
            raise ModelError(
                "Anthropic SDK not installed!\n"
                "Install it with: pip install anthropic\n"
                "DSPy Code doesn't include provider SDKs - install only what you need."
            )

        client = anthropic.Anthropic(api_key=self.api_key)

        # Build full prompt with context
        full_prompt = self._build_prompt_with_context(prompt, system_prompt, context)

        try:
            response = client.messages.create(
                model=self.current_model,
                max_tokens=2000,
                messages=[{"role": "user", "content": full_prompt}],
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise ModelError(f"Failed to generate response: {e}")

    def _generate_gemini(
        self, prompt: str, system_prompt: str | None, context: dict[str, Any] | None
    ) -> str:
        """Generate response from Gemini."""
        try:
            # Prefer the modern Google Gen AI SDK (google-genai)
            try:
                from google import genai  # type: ignore[import-not-found]

                client = genai.Client(api_key=self.api_key)
                use_genai = True
            except Exception:
                # Fallback to legacy google-generativeai if present
                import google.generativeai as genai  # type: ignore[import-not-found]

                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.current_model)
                use_genai = False
        except ImportError as exc:
            raise ModelError(
                "Google Gemini SDK not installed!\n"
                "Install the official SDK with: pip install \"google-genai>=1.52.0\" \n"
                "DSPy Code doesn't include provider SDKs by default - install only what you need."
            ) from exc

        # Build full prompt with context
        full_prompt = self._build_prompt_with_context(prompt, system_prompt, context)

        try:
            if use_genai:
                # google-genai client API:
                #   from google import genai
                #   client = genai.Client(api_key=...)
                #   response = client.models.generate_content(model="...", contents="...")
                response = client.models.generate_content(
                    model=self.current_model,
                    contents=full_prompt,
                )
                return getattr(response, "text", "") or ""

            # Legacy google-generativeai behaviour
            response = model.generate_content(full_prompt)
            return response.text

        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise ModelError(f"Failed to generate response: {e}")

    def _build_prompt_with_context(
        self, prompt: str, system_prompt: str | None, context: dict[str, Any] | None
    ) -> str:
        """Build a complete prompt with DSPy reference context."""
        parts = []

        if system_prompt:
            parts.append(system_prompt)

        if context:
            # Add DSPy reference documentation
            if "dspy_reference" in context:
                parts.append(f"\n# DSPy Reference Documentation:\n{context['dspy_reference']}\n")

            # Add conversation history
            if "conversation_history" in context:
                parts.append(f"\n# Previous Conversation:\n{context['conversation_history']}\n")

            # Add current code context
            if "current_code" in context:
                parts.append(f"\n# Current Code Context:\n{context['current_code']}\n")

        parts.append(f"\n# User Request:\n{prompt}")

        return "\n".join(parts)

    def _build_system_prompt_with_context(
        self, system_prompt: str | None, context: dict[str, Any] | None
    ) -> str:
        """Build system prompt with context for chat models."""
        parts = []

        if system_prompt:
            parts.append(system_prompt)

        if context and "dspy_reference" in context:
            parts.append(
                f"\nYou have access to DSPy reference documentation:\n{context['dspy_reference']}"
            )

        return "\n".join(parts)

    def get_connection_status(self) -> dict[str, Any]:
        """Get current connection status."""
        return {
            "connected": self.current_model is not None,
            "model": self.current_model,
            "type": self.model_type,
            "has_api_key": self.api_key is not None,
        }
