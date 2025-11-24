"""
UI components for DSPy Code.

Provides beautiful, Claude-like interface elements.
"""

from .animations import ThinkingAnimation, get_random_thinking_message
from .prompts import get_user_input
from .welcome import show_welcome_screen

__all__ = [
    "ThinkingAnimation",
    "get_random_thinking_message",
    "get_user_input",
    "show_welcome_screen",
]
