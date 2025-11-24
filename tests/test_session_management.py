"""
Unit tests for session management.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from dspy_code.core.exceptions import SessionNotFoundError
from dspy_code.session import SessionInfo, SessionState, SessionStateManager


class MockSession:
    """Mock interactive session for testing."""

    def __init__(self):
        self.conversation_history = [
            {"role": "user", "content": "test message 1"},
            {"role": "assistant", "content": "test response 1"},
        ]
        self.current_context = {"last_generated": "test code", "type": "module"}
        self.llm_connector = MockLLMConnector()


class MockLLMConnector:
    """Mock LLM connector."""

    def __init__(self):
        self.current_model = "test-model"
        self.model_type = "test"
        self.api_key = "test-key"


@pytest.fixture
def temp_session_dir():
    """Create temporary session directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def session_manager(temp_session_dir):
    """Create session manager with temp directory."""
    manager = SessionStateManager()
    manager.session_dir = temp_session_dir
    return manager


@pytest.fixture
def mock_session():
    """Create mock session."""
    return MockSession()


def test_session_manager_initialization(session_manager):
    """Test session manager initializes correctly."""
    assert session_manager.session_dir.exists()
    assert session_manager.auto_save_enabled is True
    assert session_manager.auto_save_interval == 300


def test_save_session(session_manager, mock_session):
    """Test saving a session."""
    file_path = session_manager.save_session(mock_session, "test_session")

    assert file_path.exists()
    assert file_path.name == "test_session.json"

    # Verify content
    with open(file_path) as f:
        data = json.load(f)

    assert data["version"] == "1.0.0"
    assert len(data["conversation_history"]) == 2
    assert data["current_context"]["last_generated"] == "test code"


def test_save_session_auto_name(session_manager, mock_session):
    """Test saving session with auto-generated name."""
    file_path = session_manager.save_session(mock_session)

    assert file_path.exists()
    assert file_path.name.startswith("session_")
    assert file_path.name.endswith(".json")


def test_load_session(session_manager, mock_session):
    """Test loading a saved session."""
    # Save first
    session_manager.save_session(mock_session, "test_load")

    # Load
    state = session_manager.load_session("test_load")

    assert isinstance(state, SessionState)
    assert len(state.conversation_history) == 2
    assert state.current_context["last_generated"] == "test code"
    assert state.model_config["model"] == "test-model"


def test_load_nonexistent_session(session_manager):
    """Test loading non-existent session raises error."""
    with pytest.raises(SessionNotFoundError):
        session_manager.load_session("nonexistent")


def test_list_sessions(session_manager, mock_session):
    """Test listing saved sessions."""
    # Save multiple sessions
    session_manager.save_session(mock_session, "session1")
    session_manager.save_session(mock_session, "session2")
    session_manager.save_session(mock_session, "session3")

    # List
    sessions = session_manager.list_sessions()

    assert len(sessions) == 3
    assert all(isinstance(s, SessionInfo) for s in sessions)
    assert {s.name for s in sessions} == {"session1", "session2", "session3"}


def test_list_sessions_empty(session_manager):
    """Test listing sessions when none exist."""
    sessions = session_manager.list_sessions()
    assert len(sessions) == 0


def test_delete_session(session_manager, mock_session):
    """Test deleting a session."""
    # Save first
    session_manager.save_session(mock_session, "test_delete")

    # Verify exists
    sessions = session_manager.list_sessions()
    assert len(sessions) == 1

    # Delete
    result = session_manager.delete_session("test_delete")
    assert result is True

    # Verify deleted
    sessions = session_manager.list_sessions()
    assert len(sessions) == 0


def test_delete_nonexistent_session(session_manager):
    """Test deleting non-existent session raises error."""
    with pytest.raises(SessionNotFoundError):
        session_manager.delete_session("nonexistent")


def test_session_state_to_dict():
    """Test SessionState serialization."""
    state = SessionState(
        version="1.0.0",
        timestamp=datetime.now(),
        conversation_history=[{"role": "user", "content": "test"}],
        current_context={"key": "value"},
        generated_files=[],
        model_config={},
        metadata={},
    )

    data = state.to_dict()

    assert data["version"] == "1.0.0"
    assert isinstance(data["timestamp"], str)
    assert data["conversation_history"][0]["role"] == "user"


def test_session_state_from_dict():
    """Test SessionState deserialization."""
    data = {
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "conversation_history": [{"role": "user", "content": "test"}],
        "current_context": {"key": "value"},
        "generated_files": [],
        "model_config": {},
        "metadata": {},
    }

    state = SessionState.from_dict(data)

    assert state.version == "1.0.0"
    assert isinstance(state.timestamp, datetime)
    assert len(state.conversation_history) == 1


def test_session_info_str():
    """Test SessionInfo string representation."""
    info = SessionInfo(
        name="test_session",
        path=Path("/tmp/test.json"),
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
        message_count=10,
        file_count=2,
        model="gpt-4",
    )

    str_repr = str(info)
    assert "test_session" in str_repr
    assert "2025-01-01" in str_repr
    assert "10 messages" in str_repr


def test_auto_save_start_stop(session_manager, mock_session):
    """Test auto-save start and stop."""
    # Start auto-save
    session_manager.start_auto_save(mock_session)
    assert session_manager.last_session == mock_session
    assert session_manager.auto_save_timer is not None

    # Stop auto-save
    session_manager.stop_auto_save()
    assert session_manager.auto_save_timer is None


def test_version_compatibility(session_manager):
    """Test version compatibility checking."""
    # Current version should be compatible
    assert session_manager._is_compatible_version("1.0.0") is True

    # Future versions should be compatible (for now)
    assert session_manager._is_compatible_version("2.0.0") is True


def test_session_with_empty_context(session_manager):
    """Test saving session with empty context."""
    session = MockSession()
    session.current_context = {}
    session.conversation_history = []

    file_path = session_manager.save_session(session, "empty_session")
    assert file_path.exists()

    # Load and verify
    state = session_manager.load_session("empty_session")
    assert len(state.conversation_history) == 0
    assert len(state.current_context) == 0
