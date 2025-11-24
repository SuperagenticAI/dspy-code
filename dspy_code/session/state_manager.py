"""
Session state management for DSPy Code.

Handles saving, loading, and managing interactive session state.
"""

import json
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ..core.logging import get_logger

logger = get_logger(__name__)

# Current session format version
SESSION_VERSION = "1.0.0"


@dataclass
class SessionState:
    """Represents the state of an interactive session."""

    version: str
    timestamp: datetime
    conversation_history: list[dict[str, str]]
    current_context: dict[str, Any]
    generated_files: list[str]
    model_config: dict[str, Any]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime to ISO format string
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionState":
        """Create from dictionary."""
        # Convert ISO format string back to datetime
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class SessionInfo:
    """Information about a saved session."""

    name: str
    path: Path
    timestamp: datetime
    message_count: int
    file_count: int
    model: str

    def __str__(self) -> str:
        """String representation for display."""
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.name} ({time_str}) - {self.message_count} messages, {self.file_count} files"


class SessionStateManager:
    """Manages session state including save, load, and auto-save."""

    def __init__(self, config_manager=None):
        """
        Initialize session state manager.

        Args:
            config_manager: Optional configuration manager
        """
        self.config_manager = config_manager

        # Session directory in user home
        self.session_dir = Path.home() / ".dspy_cli" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Auto-save state
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5 minutes in seconds
        self.auto_save_timer: threading.Timer | None = None
        self.last_session: InteractiveSession | None = None

        logger.info(f"Session directory: {self.session_dir}")

    def save_session(self, session: Any, name: str = None) -> Path:
        """
        Save current session to file.

        Args:
            session: InteractiveSession instance
            name: Optional custom name, defaults to timestamp

        Returns:
            Path to saved session file
        """
        # Generate name if not provided
        if name is None:
            name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Ensure .json extension
        if not name.endswith(".json"):
            name += ".json"

        # Create session state
        state = SessionState(
            version=SESSION_VERSION,
            timestamp=datetime.now(),
            conversation_history=session.conversation_history.copy(),
            current_context=session.current_context.copy(),
            generated_files=self._get_generated_files(session),
            model_config=self._get_model_config(session),
            metadata={"session_name": name, "cli_version": self._get_cli_version()},
        )

        # Save to file
        file_path = self.session_dir / name

        try:
            with open(file_path, "w") as f:
                json.dump(state.to_dict(), f, indent=2)

            logger.info(f"Session saved to: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            raise SessionSaveError(f"Failed to save session: {e}")

    def load_session(self, name: str) -> SessionState:
        """
        Load a saved session.

        Args:
            name: Session name or filename

        Returns:
            SessionState object

        Raises:
            SessionNotFoundError: If session doesn't exist
            IncompatibleVersionError: If session version is incompatible
            CorruptedSessionError: If session file is corrupted
        """
        # Ensure .json extension
        if not name.endswith(".json"):
            name += ".json"

        file_path = self.session_dir / name

        if not file_path.exists():
            raise SessionNotFoundError(f"Session not found: {name}")

        try:
            with open(file_path) as f:
                data = json.load(f)

            # Check version compatibility
            session_version = data.get("version", "0.0.0")
            if not self._is_compatible_version(session_version):
                raise IncompatibleVersionError(
                    f"Session version {session_version} is incompatible with current version {SESSION_VERSION}"
                )

            # Create session state
            state = SessionState.from_dict(data)

            logger.info(f"Session loaded from: {file_path}")
            return state

        except json.JSONDecodeError as e:
            raise CorruptedSessionError(f"Session file is corrupted: {e}")
        except KeyError as e:
            raise CorruptedSessionError(f"Session file is missing required field: {e}")
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            raise

    def list_sessions(self) -> list[SessionInfo]:
        """
        List all saved sessions.

        Returns:
            List of SessionInfo objects
        """
        sessions = []

        for file_path in self.session_dir.glob("*.json"):
            try:
                with open(file_path) as f:
                    data = json.load(f)

                # Extract info
                timestamp = datetime.fromisoformat(data["timestamp"])
                message_count = len(data.get("conversation_history", []))
                file_count = len(data.get("generated_files", []))
                model = data.get("model_config", {}).get("model", "unknown")

                sessions.append(
                    SessionInfo(
                        name=file_path.stem,
                        path=file_path,
                        timestamp=timestamp,
                        message_count=message_count,
                        file_count=file_count,
                        model=model,
                    )
                )

            except Exception as e:
                logger.warning(f"Failed to read session {file_path}: {e}")
                continue

        # Sort by timestamp, newest first
        sessions.sort(key=lambda s: s.timestamp, reverse=True)

        return sessions

    def delete_session(self, name: str) -> bool:
        """
        Delete a saved session.

        Args:
            name: Session name or filename

        Returns:
            True if deleted successfully
        """
        # Ensure .json extension
        if not name.endswith(".json"):
            name += ".json"

        file_path = self.session_dir / name

        if not file_path.exists():
            raise SessionNotFoundError(f"Session not found: {name}")

        try:
            file_path.unlink()
            logger.info(f"Session deleted: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False

    def start_auto_save(self, session: Any) -> None:
        """
        Start auto-save timer for session.

        Args:
            session: InteractiveSession instance
        """
        if not self.auto_save_enabled:
            return

        self.last_session = session
        self._schedule_auto_save()
        logger.debug("Auto-save started")

    def stop_auto_save(self) -> None:
        """Stop auto-save timer."""
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
            self.auto_save_timer = None
        logger.debug("Auto-save stopped")

    def _schedule_auto_save(self) -> None:
        """Schedule next auto-save."""
        if self.auto_save_timer:
            self.auto_save_timer.cancel()

        self.auto_save_timer = threading.Timer(self.auto_save_interval, self._perform_auto_save)
        self.auto_save_timer.daemon = True
        self.auto_save_timer.start()

    def _perform_auto_save(self) -> None:
        """Perform auto-save operation."""
        if self.last_session is None:
            return

        try:
            # Save with auto-save prefix
            name = f"autosave_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.save_session(self.last_session, name)

            # Clean up old auto-saves (keep last 5)
            self._cleanup_auto_saves()

            # Schedule next auto-save
            self._schedule_auto_save()

        except Exception as e:
            logger.error(f"Auto-save failed: {e}")
            # Still schedule next attempt
            self._schedule_auto_save()

    def _cleanup_auto_saves(self, keep_count: int = 5) -> None:
        """Clean up old auto-save files."""
        auto_saves = sorted(
            self.session_dir.glob("autosave_*.json"), key=lambda p: p.stat().st_mtime, reverse=True
        )

        # Delete old auto-saves
        for old_save in auto_saves[keep_count:]:
            try:
                old_save.unlink()
                logger.debug(f"Deleted old auto-save: {old_save.name}")
            except Exception as e:
                logger.warning(f"Failed to delete old auto-save: {e}")

    def _get_generated_files(self, session: Any) -> list[str]:
        """Get list of generated files from session."""
        # This would track files created during the session
        # For now, return empty list
        return []

    def _get_model_config(self, session: Any) -> dict[str, Any]:
        """Get model configuration from session."""
        if hasattr(session, "llm_connector") and session.llm_connector.current_model:
            return {
                "model": session.llm_connector.current_model,
                "type": session.llm_connector.model_type,
                "has_api_key": session.llm_connector.api_key is not None,
            }
        return {}

    def _get_cli_version(self) -> str:
        """Get CLI version."""
        # Would read from package metadata
        return "1.21.2"

    def _is_compatible_version(self, session_version: str) -> bool:
        """Check if session version is compatible."""
        # For now, accept all versions
        # In future, implement proper version comparison
        return True


# Import exceptions from core
from ..core.exceptions import (
    CorruptedSessionError,
    IncompatibleVersionError,
    SessionNotFoundError,
    SessionSaveError,
)
