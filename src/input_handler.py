"""
Input handler for keyboard and mouse input
"""

import pygame
from typing import Dict


class InputHandler:
    """Handles player input from keyboard and mouse."""

    def __init__(self):
        self.keys: Dict[str, bool] = {}
        self.mouse_position = (0, 0)
        self.mouse_buttons = [False, False, False]

    def update(self) -> None:
        """Update input state."""
        # Update held keys from pygame state
        pressed = pygame.key.get_pressed()
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
        for pygame_key, key_name in key_map.items():
            self.keys[key_name] = pressed[pygame_key]

        # Update mouse position
        self.mouse_position = pygame.mouse.get_pos()
        self.mouse_buttons = list(pygame.mouse.get_pressed())

    def get_keys(self) -> Dict[str, bool]:
        """Get current key states."""
        return self.keys.copy()

    def is_key_pressed(self, key: str) -> bool:
        """Check if a specific key is pressed."""
        return self.keys.get(key, False)

    def get_mouse_position(self) -> tuple:
        """Get current mouse position."""
        return self.mouse_position

    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is pressed (0=left, 1=middle, 2=right)."""
        if 0 <= button < len(self.mouse_buttons):
            return self.mouse_buttons[button]
        return False
