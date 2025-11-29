"""
Configuration management for DSPy Code.
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .exceptions import ConfigurationError


@dataclass
class ModelConfig:
    """Configuration for language models."""

    ollama_endpoint: str | None = "http://localhost:11434"
    ollama_models: list[str] = field(default_factory=list)
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-4.5-sonnet"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.1"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-pro-2.5"
    reflection_model: str | None = None  # Model for GEPA reflection (defaults to default_model)


@dataclass
class GepaConfig:
    """Configuration for GEPA optimizer."""

    max_iterations: int = 10
    population_size: int = 20
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    evaluation_metric: str = "accuracy"


@dataclass
class CodebaseRAGConfig:
    """Configuration for codebase RAG system."""

    enabled: bool = False  # Disabled by default for faster responses
    # Performance options
    fast_mode: bool = True  # Enabled by default for faster responses
    skip_pattern_searches: bool = False  # Skip additional pattern-specific searches
    codebases: list[str] = field(default_factory=lambda: ["dspy-code", "dspy", "gepa"])
    cache_dir: str | None = None  # Defaults to .dspy_code/cache/codebase_index in CWD
    max_cache_size_mb: int = 100
    index_refresh_days: int = 7
    use_tfidf: bool = True
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            "tests/",
            "test_*.py",
            "__pycache__/",
            "*.pyc",
            ".git/",
            ".venv/",
            "venv/",
            "build/",
            "dist/",
            "*.egg-info/",
            "node_modules/",
            "experimental/",
            "examples/",
        ]
    )
    search_top_k: int = 5
    max_context_tokens: int = 4000
    include_related: bool = True


@dataclass
class ProjectConfig:
    """Main project configuration."""

    name: str
    version: str = "0.1.0"
    dspy_version: str = "2.4.0"
    models: ModelConfig = field(default_factory=ModelConfig)
    default_model: str | None = None
    gepa_config: GepaConfig = field(default_factory=GepaConfig)
    codebase_rag: CodebaseRAGConfig = field(default_factory=CodebaseRAGConfig)
    output_directory: str = "generated"
    template_preferences: dict[str, Any] = field(default_factory=dict)
    mcp_servers: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def load_from_file(cls, config_path: Path) -> "ProjectConfig":
        """Load configuration from file."""
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path) as f:
                if config_path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            # Convert nested dicts to dataclasses
            if "models" in data:
                data["models"] = ModelConfig(**data["models"])
            if "gepa_config" in data:
                data["gepa_config"] = GepaConfig(**data["gepa_config"])
            if "codebase_rag" in data:
                data["codebase_rag"] = CodebaseRAGConfig(**data["codebase_rag"])

            # Ensure mcp_servers exists and is a dict
            if "mcp_servers" not in data or data["mcp_servers"] is None:
                data["mcp_servers"] = {}

            # Handle legacy 'model' key - convert to 'default_model'
            if "model" in data and "default_model" not in data:
                model_value = data.pop("model")
                # If it's a dict (legacy format), extract the model name
                if isinstance(model_value, dict):
                    # Legacy format: model: {provider: ..., model_name: ...}
                    if "model_name" in model_value:
                        data["default_model"] = model_value["model_name"]
                    elif "name" in model_value:
                        data["default_model"] = model_value["name"]
                    # Could also set provider-specific model in models config
                    if "provider" in model_value and "model_name" in model_value:
                        provider = model_value["provider"]
                        model_name = model_value["model_name"]
                        if "models" not in data:
                            data["models"] = {}
                        if provider == "ollama":
                            if "ollama_models" not in data["models"]:
                                data["models"]["ollama_models"] = []
                            if model_name not in data["models"]["ollama_models"]:
                                data["models"]["ollama_models"].append(model_name)
                            data["default_model"] = model_name
                        elif provider == "openai":
                            data["models"]["openai_model"] = model_name
                            data["default_model"] = f"openai/{model_name}"
                        elif provider == "anthropic":
                            data["models"]["anthropic_model"] = model_name
                            data["default_model"] = f"anthropic/{model_name}"
                        elif provider == "gemini":
                            data["models"]["gemini_model"] = model_name
                            data["default_model"] = f"gemini/{model_name}"
                elif isinstance(model_value, str):
                    # Simple string format: model: "llama3.2"
                    data["default_model"] = model_value
                else:
                    # Fallback: try to convert to string
                    data["default_model"] = str(model_value)

            # Filter out any keys that aren't valid ProjectConfig fields
            valid_fields = {
                "name",
                "version",
                "dspy_version",
                "models",
                "default_model",
                "gepa_config",
                "codebase_rag",
                "output_directory",
                "template_preferences",
                "mcp_servers",
            }
            filtered_data = {k: v for k, v in data.items() if k in valid_fields}

            # Ensure required 'name' field exists (use default if missing)
            if "name" not in filtered_data:
                filtered_data["name"] = "my-dspy-code-project"

            # Ensure 'models' is a ModelConfig instance
            if "models" not in filtered_data or not isinstance(
                filtered_data["models"], ModelConfig
            ):
                if "models" in filtered_data and isinstance(filtered_data["models"], dict):
                    filtered_data["models"] = ModelConfig(**filtered_data["models"])
                else:
                    filtered_data["models"] = ModelConfig()

            config = cls(**filtered_data)

            # Load API keys from environment variables
            config._load_api_keys_from_env()

            return config
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def _load_api_keys_from_env(self):
        """Load API keys from environment variables if not set in config."""
        import os

        # Load from .env file if it exists
        env_file = Path.cwd() / ".env"
        if env_file.exists():
            self._load_dotenv(env_file)

        # Override with environment variables (priority order)
        if not self.models.openai_api_key or self.models.openai_api_key == "null":
            self.models.openai_api_key = os.getenv("OPENAI_API_KEY")

        if not self.models.anthropic_api_key or self.models.anthropic_api_key == "null":
            self.models.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.models.gemini_api_key or self.models.gemini_api_key == "null":
            self.models.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def _load_dotenv(self, env_file: Path):
        """Load environment variables from .env file."""
        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        import os

                        os.environ[key] = value
        except Exception:
            # Silently fail if .env can't be loaded
            pass

    def save_to_file(self, config_path: Path, minimal: bool = False) -> None:
        """
        Save configuration to file.

        Args:
            config_path: Path to save the configuration file
            minimal: If True, save only essential fields with comments
        """
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)

            if minimal and config_path.suffix.lower() in [".yaml", ".yml"]:
                # Save minimal YAML with helpful comments
                self._save_minimal_yaml(config_path)
            else:
                # Save full configuration
                data = asdict(self)

                with open(config_path, "w") as f:
                    if config_path.suffix.lower() == ".json":
                        json.dump(data, f, indent=2)
                    else:
                        yaml.dump(data, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")

    def _save_minimal_yaml(self, config_path: Path) -> None:
        """Save a minimal YAML configuration with helpful comments."""
        minimal_config = f"""# DSPy Code Configuration
# This is a minimal configuration file. For all available options, see:
# dspy_config_example.yaml (created alongside this file)

# IMPORTANT: Store API keys in environment variables or .env file!
# Create a .env file (add to .gitignore):
#   OPENAI_API_KEY=sk-...
#   ANTHROPIC_API_KEY=sk-ant-...
#   GEMINI_API_KEY=...

# Project information
name: {self.name}
version: {self.version}
dspy_version: {self.dspy_version}

# Output directory for generated components
output_directory: {self.output_directory}

# Model configuration
# Configure at least one model to use DSPy Code
models:
  # Local models via Ollama (free, private)
  ollama_endpoint: {self.models.ollama_endpoint}
  ollama_models: {self.models.ollama_models if self.models.ollama_models else []}

  # Cloud providers (API keys loaded from environment variables)
  # Set OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY in .env file
  openai_api_key: null  # Loaded from OPENAI_API_KEY env var
  openai_model: {self.models.openai_model}

  anthropic_api_key: null  # Loaded from ANTHROPIC_API_KEY env var
  anthropic_model: {self.models.anthropic_model}

  gemini_api_key: null  # Loaded from GEMINI_API_KEY env var
  gemini_model: {self.models.gemini_model}

  # Reflection model for GEPA optimization (optional)
  reflection_model: null  # Uses default_model if not set

# Default model (e.g., "gpt-4", "llama2")
default_model: {self.default_model or "null"}

# Optimization settings (used by 'dspy-code optimize')
gepa_config:
  max_iterations: {self.gepa_config.max_iterations}
  population_size: {self.gepa_config.population_size}
  mutation_rate: {self.gepa_config.mutation_rate}
  crossover_rate: {self.gepa_config.crossover_rate}
  evaluation_metric: {self.gepa_config.evaluation_metric}

# Template preferences
template_preferences: {{}}

# MCP servers (Model Context Protocol)
mcp_servers: {{}}

# For more configuration options, see dspy_config_example.yaml
"""
        config_path.write_text(minimal_config)

    @classmethod
    def create_default(cls, project_name: str) -> "ProjectConfig":
        """Create default configuration for a new project."""
        return cls(name=project_name, models=ModelConfig(), gepa_config=GepaConfig())


class ConfigManager:
    """Manages project configuration."""

    CONFIG_FILENAME = "dspy_config.yaml"

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.config_path = self.project_root / self.CONFIG_FILENAME
        self._config: ProjectConfig | None = None

    @property
    def config(self) -> ProjectConfig:
        """Get current configuration, loading if necessary."""
        if self._config is None:
            self.load_config()
        return self._config

    def load_config(self) -> ProjectConfig:
        """Load configuration from file."""
        if self.config_path.exists():
            self._config = ProjectConfig.load_from_file(self.config_path)
        else:
            # Create default config if none exists
            project_name = self.project_root.name
            self._config = ProjectConfig.create_default(project_name)

        return self._config

    def save_config(self, minimal: bool = False) -> None:
        """
        Save current configuration to file.

        Args:
            minimal: If True, save only essential fields with comments
        """
        if self._config is None:
            raise ConfigurationError("No configuration to save")

        self._config.save_to_file(self.config_path, minimal=minimal)

    def update_config(self, **kwargs) -> None:
        """Update configuration with new values."""
        config = self.config

        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                raise ConfigurationError(f"Unknown configuration key: {key}")

        self.save_config()

    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        project_name = self.config.name
        self._config = ProjectConfig.create_default(project_name)
        self.save_config()

    def is_project_initialized(self) -> bool:
        """Check if current directory is a DSPy Code project."""
        return self.config_path.exists()

    def get_model_config(self, provider: str) -> dict[str, Any]:
        """Get configuration for a specific model provider."""
        models = self.config.models

        if provider == "ollama":
            return {"endpoint": models.ollama_endpoint, "models": models.ollama_models}
        elif provider == "anthropic":
            return {"api_key": models.anthropic_api_key, "model": models.anthropic_model}
        elif provider == "openai":
            return {"api_key": models.openai_api_key, "model": models.openai_model}
        elif provider == "gemini":
            return {"api_key": models.gemini_api_key, "model": models.gemini_model}
        else:
            raise ConfigurationError(f"Unknown provider: {provider}")

    def set_model_config(self, provider: str, **kwargs) -> None:
        """Set configuration for a specific model provider."""
        models = self.config.models

        if provider == "ollama":
            if "endpoint" in kwargs:
                models.ollama_endpoint = kwargs["endpoint"]
            if "models" in kwargs:
                models.ollama_models = kwargs["models"]
        elif provider == "anthropic":
            if "api_key" in kwargs:
                models.anthropic_api_key = kwargs["api_key"]
            if "model" in kwargs:
                models.anthropic_model = kwargs["model"]
        elif provider == "openai":
            if "api_key" in kwargs:
                models.openai_api_key = kwargs["api_key"]
            if "model" in kwargs:
                models.openai_model = kwargs["model"]
        elif provider == "gemini":
            if "api_key" in kwargs:
                models.gemini_api_key = kwargs["api_key"]
            if "model" in kwargs:
                models.gemini_model = kwargs["model"]
        else:
            raise ConfigurationError(f"Unknown provider: {provider}")

        self.save_config()

    def get_mcp_servers(self) -> dict[str, dict[str, Any]]:
        """Get all MCP server configurations."""
        return self.config.mcp_servers.copy()

    def get_mcp_server(self, server_name: str) -> dict[str, Any] | None:
        """Get a specific MCP server configuration."""
        return self.config.mcp_servers.get(server_name)

    def add_mcp_server(self, server_name: str, server_config: dict[str, Any]) -> None:
        """Add or update an MCP server configuration."""
        self.config.mcp_servers[server_name] = server_config
        self.save_config()

    def remove_mcp_server(self, server_name: str) -> bool:
        """Remove an MCP server configuration.

        Returns:
            True if server was removed, False if it didn't exist
        """
        if server_name in self.config.mcp_servers:
            del self.config.mcp_servers[server_name]
            self.save_config()
            return True
        return False

    def has_mcp_server(self, server_name: str) -> bool:
        """Check if an MCP server configuration exists."""
        return server_name in self.config.mcp_servers
