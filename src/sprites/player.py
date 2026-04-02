"""
Player sprite - renders player character
"""

import pygame
from typing import Tuple


class PlayerSprite:
    """Renders the player character."""

    def __init__(self):
        self.width = 32
        self.height = 32
        self.color = (0, 255, 0)  # Green player
        self.surface = None
        self._create_surface()

    def _create_surface(self) -> None:
        """Create the player surface."""
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw a simple character shape
        # Body
        pygame.draw.rect(self.surface, self.color, (8, 8, 16, 24))
        # Head
        pygame.draw.circle(
            self.surface,
            (255, 200, 150),  # Skin tone
            (16, 8),
            8,
        )

    def get_surface(self) -> pygame.Surface:
        """Get the player surface."""
        return self.surface

    def render(self, screen: pygame.Surface, x: int, y: int, angle: float) -> None:
        """Render the player at screen position with rotation."""
        if self.surface:
            # Rotate the sprite based on angle
            rotated = pygame.transform.rotate(self.surface, angle)
            rect = rotated.get_rect(center=(x, y))
            screen.blit(rotated, rect)


class PlayerAnimator:
    """Animates player actions."""

    def __init__(self):
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.state = "idle"

    def update(self, dt: float) -> None:
        """Update animation frame."""
        self.animation_frame += dt * self.animation_speed

    def set_state(self, state: str) -> None:
        """Set player animation state."""
        if self.state != state:
            self.state = state
            self.animation_frame = 0

    def is_attacking(self) -> bool:
        """Check if player is in attack animation."""
        return self.state == "attack"
