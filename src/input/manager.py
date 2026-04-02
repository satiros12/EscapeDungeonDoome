"""
Input Manager - Handles keyboard and mouse input

This module provides the InputManager class which wraps pygame's input
handling and converts key events to InputAction values. It maintains
backward compatibility with the original InputHandler interface while
providing new functionality for system integration.
"""

import pygame
from typing import Dict, Set, Optional

from input.actions import InputAction
from input.bindings import KeyBindingMap


class InputManager:
    """
    Manages player input from keyboard and mouse.

    This class wraps pygame's input handling and provides a bridge
    between raw key events and game actions. It supports:
    - Key state tracking (pressed/held)
    - Action-based input lookup via InputAction enum
    - Mouse position and button tracking
    - Backward compatibility with original InputHandler interface

    Example:
        >>> input_mgr = InputManager()
        >>> input_mgr.update()
        >>> actions = input_mgr.get_pressed_actions()
        >>> if InputAction.MOVE_FORWARD in actions:
        ...     print("Moving forward!")
    """

    def __init__(self):
        """Initialize the input manager."""
        # Key bindings map
        self.binding_map = KeyBindingMap()

        # Legacy key state (for backward compatibility)
        self.keys: Dict[str, bool] = {}

        # Action-based state
        self._pressed_actions: Set[InputAction] = set()

        # Mouse state
        self.mouse_position = (0, 0)
        self.mouse_buttons = [False, False, False]

    def update(self) -> None:
        """
        Update input state from pygame.

        This should be called once per frame to capture the current
        state of all keyboard and mouse inputs.
        """
        # Update from pygame key state
        pressed = pygame.key.get_pressed()

        # Update legacy key state for backward compatibility
        key_map = {
            pygame.K_w: "KeyW",
            pygame.K_s: "KeyS",
            pygame.K_a: "KeyA",
            pygame.K_d: "KeyD",
            pygame.K_LEFT: "ArrowLeft",
            pygame.K_RIGHT: "ArrowRight",
            pygame.K_SPACE: "Space",
            pygame.K_ESCAPE: "Escape",
        }

        self.keys = {}
        self._pressed_actions = set()

        for pygame_key, key_name in key_map.items():
            is_pressed = pressed[pygame_key]
            self.keys[key_name] = is_pressed

            # Also track actions
            action = self.binding_map.get_action(pygame_key)
            if action and is_pressed:
                self._pressed_actions.add(action)

        # Update mouse state
        self.mouse_position = pygame.mouse.get_pos()
        self.mouse_buttons = list(pygame.mouse.get_pressed())

    def get_pressed_actions(self) -> Set[InputAction]:
        """
        Get all currently pressed actions.

        Returns:
            Set of InputAction values that are currently active
        """
        return self._pressed_actions.copy()

    def is_action_pressed(self, action: InputAction) -> bool:
        """
        Check if a specific action is currently pressed.

        Args:
            action: InputAction to check

        Returns:
            True if the action is currently active
        """
        return action in self._pressed_actions

    def get_keys(self) -> Dict[str, bool]:
        """
        Get current key states (legacy compatibility).

        Returns:
            Dictionary mapping key names to pressed state
        """
        return self.keys.copy()

    def is_key_pressed(self, key: str) -> bool:
        """
        Check if a specific key is pressed (legacy compatibility).

        Args:
            key: Key name string

        Returns:
            True if the key is currently pressed
        """
        return self.keys.get(key, False)

    def get_mouse_position(self) -> tuple:
        """
        Get current mouse position.

        Returns:
            Tuple of (x, y) coordinates
        """
        return self.mouse_position

    def is_mouse_button_pressed(self, button: int) -> bool:
        """
        Check if a mouse button is pressed.

        Args:
            button: Button index (0=left, 1=middle, 2=right)

        Returns:
            True if the button is currently pressed
        """
        if 0 <= button < len(self.mouse_buttons):
            return self.mouse_buttons[button]
        return False

    def get_binding_map(self) -> KeyBindingMap:
        """
        Get the key binding map.

        Returns:
            The KeyBindingMap instance
        """
        return self.binding_map


# Backward compatibility alias
class InputHandler(InputManager):
    """
    Backward compatibility wrapper for InputManager.

    This class provides the same interface as the original InputHandler
    for backward compatibility with existing code.
    """

    def __init__(self):
        """Initialize the input handler (backward compatible)."""
        super().__init__()
