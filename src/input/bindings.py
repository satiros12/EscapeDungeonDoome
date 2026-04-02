"""
Key bindings - Maps pygame keys to InputAction values

This module provides the KeyBindingMap class which handles mapping
physical keyboard keys to game actions. It supports custom bindings
and provides default bindings for WebDoom controls.
"""

import pygame
from typing import Dict, Optional, Set

from input.actions import InputAction


class KeyBindingMap:
    """
    Maps pygame key constants to InputAction values.

    This class manages keyboard bindings for the game, allowing
    flexible remapping of keys and easy lookup of actions.

    Example:
        >>> binding_map = KeyBindingMap()
        >>> action = binding_map.get_action(pygame.K_w)
        >>> print(action)
        InputAction.MOVE_FORWARD

        # Custom binding
        >>> binding_map.register(pygame.K_UP, InputAction.MOVE_FORWARD)
    """

    def __init__(self):
        """Initialize the binding map with default WebDoom bindings."""
        self.bindings: Dict[int, InputAction] = {}
        self._setup_default_bindings()

    def _setup_default_bindings(self) -> None:
        """Set up default key bindings for WebDoom controls."""
        # Movement
        self.bindings[pygame.K_w] = InputAction.MOVE_FORWARD
        self.bindings[pygame.K_s] = InputAction.MOVE_BACKWARD
        self.bindings[pygame.K_a] = InputAction.MOVE_LEFT
        self.bindings[pygame.K_d] = InputAction.MOVE_RIGHT

        # Rotation
        self.bindings[pygame.K_LEFT] = InputAction.ROTATE_LEFT
        self.bindings[pygame.K_RIGHT] = InputAction.ROTATE_RIGHT

        # Game actions
        self.bindings[pygame.K_SPACE] = InputAction.ATTACK
        self.bindings[pygame.K_ESCAPE] = InputAction.PAUSE
        self.bindings[pygame.K_p] = InputAction.CONSOLE
        self.bindings[pygame.K_q] = InputAction.QUIT

    def register(self, key: int, action: InputAction) -> None:
        """
        Register a key binding.

        Args:
            key: Pygame key constant (e.g., pygame.K_w)
            action: InputAction to bind to the key
        """
        self.bindings[key] = action

    def unregister(self, key: int) -> None:
        """
        Remove a key binding.

        Args:
            key: Pygame key constant to remove
        """
        if key in self.bindings:
            del self.bindings[key]

    def get_action(self, key: int) -> Optional[InputAction]:
        """
        Get the action associated with a key.

        Args:
            key: Pygame key constant

        Returns:
            InputAction if bound, None otherwise
        """
        return self.bindings.get(key)

    def get_key(self, action: InputAction) -> Optional[int]:
        """
        Get the key bound to an action.

        Args:
            action: InputAction to look up

        Returns:
            Pygame key constant if found, None otherwise
        """
        for key, act in self.bindings.items():
            if act == action:
                return key
        return None

    def get_bound_keys(self) -> Set[int]:
        """
        Get all currently bound keys.

        Returns:
            Set of pygame key constants
        """
        return set(self.bindings.keys())

    def get_all_bindings(self) -> Dict[int, InputAction]:
        """
        Get a copy of all bindings.

        Returns:
            Dictionary mapping pygame keys to actions
        """
        return self.bindings.copy()

    def clear(self) -> None:
        """Clear all key bindings."""
        self.bindings.clear()

    def reset_to_defaults(self) -> None:
        """Reset all bindings to WebDoom defaults."""
        self.bindings.clear()
        self._setup_default_bindings()
