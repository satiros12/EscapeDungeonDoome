"""
Renderer - handles all game rendering using Pygame
"""

import pygame
from typing import List, Tuple


class Renderer:
    """Handles all rendering operations."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Clear the screen with a color."""
        self.screen.fill(color)

    def render_walls(self, wall_data: List[dict]) -> None:
        """Render wall columns from raycasting data."""
        pass

    def render_sprite(self, x: int, y: int, image: pygame.Surface) -> None:
        """Render a sprite at screen position."""
        pass

    def render_rect(
        self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int]
    ) -> None:
        """Render a rectangle."""
        pygame.draw.rect(self.screen, color, (x, y, width, height))

    def render_text(
        self,
        text: str,
        x: int,
        y: int,
        color: Tuple[int, int, int] = (255, 255, 255),
        size: int = 20,
    ) -> None:
        """Render text at position."""
        font = pygame.font.Font(None, size)
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def render_hud(self, health: int, kills: int) -> None:
        """Render the heads-up display."""
        # Render health bar
        bar_width = 200
        bar_height = 20
        health_percent = max(0, min(100, health)) / 100

        # Background
        pygame.draw.rect(
            self.screen, (64, 64, 64), (10, self.height - 40, bar_width, bar_height)
        )
        # Health fill
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),
            (10, self.height - 40, bar_width * health_percent, bar_height),
        )

        # Render kills
        self.render_text(f"Kills: {kills}", 10, self.height - 65)

    def present(self) -> None:
        """Flip the display."""
        pygame.display.flip()
