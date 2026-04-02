"""
HUD (Heads-Up Display) - displays game information
"""

import pygame
from typing import Tuple


class HUD:
    """Heads-up display for game information."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.height = 60

        # Colors
        self.bg_color = (32, 32, 32)
        self.health_color = (200, 0, 0)
        self.text_color = (255, 255, 255)

    def render(
        self, screen: pygame.Surface, health: int, kills: int, weapon: str = "fists"
    ) -> None:
        """Render the HUD."""
        # Draw background bar
        pygame.draw.rect(
            screen,
            self.bg_color,
            (0, self.screen_height - self.height, self.screen_width, self.height),
        )

        # Draw health bar
        self._render_health_bar(screen, health)

        # Draw kills
        self._render_kills(screen, kills)

        # Draw weapon
        self._render_weapon(screen, weapon)

    def _render_health_bar(self, screen: pygame.Surface, health: int) -> None:
        """Render the health bar."""
        bar_x = 20
        bar_y = self.screen_height - self.height + 15
        bar_width = 200
        bar_height = 30

        # Background
        pygame.draw.rect(screen, (64, 64, 64), (bar_x, bar_y, bar_width, bar_height))

        # Health fill
        health_percent = max(0, min(100, health)) / 100
        pygame.draw.rect(
            screen,
            self.health_color,
            (bar_x, bar_y, bar_width * health_percent, bar_height),
        )

        # Border
        pygame.draw.rect(
            screen, (128, 128, 128), (bar_x, bar_y, bar_width, bar_height), 2
        )

        # Text
        font = pygame.font.Font(None, 24)
        text = font.render(f"HP: {health}", True, self.text_color)
        screen.blit(text, (bar_x + 5, bar_y + 5))

    def _render_kills(self, screen: pygame.Surface, kills: int) -> None:
        """Render the kill counter."""
        font = pygame.font.Font(None, 28)
        text = font.render(f"Kills: {kills}", True, self.text_color)
        screen.blit(
            text, (self.screen_width - 150, self.screen_height - self.height + 20)
        )

    def _render_weapon(self, screen: pygame.Surface, weapon: str) -> None:
        """Render the current weapon."""
        font = pygame.font.Font(None, 24)
        text = font.render(f"Weapon: {weapon}", True, self.text_color)
        screen.blit(
            text, (self.screen_width // 2 - 50, self.screen_height - self.height + 20)
        )
