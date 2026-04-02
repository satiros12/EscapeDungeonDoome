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
        self.height = 70

        # Colors
        self.bg_color = (20, 15, 25)
        self.border_color = (80, 60, 40)

    def render(
        self, screen: pygame.Surface, health: int, kills: int, weapon: str = "fists"
    ) -> None:
        """Render the HUD with improved visibility."""
        # Draw HUD background
        hud_y = self.screen_height - self.height
        pygame.draw.rect(
            screen, self.bg_color, (0, hud_y, self.screen_width, self.height)
        )

        # Top border
        pygame.draw.rect(screen, self.border_color, (0, hud_y, self.screen_width, 3))

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
        bar_width = 220
        bar_height = 35

        # Background with border
        pygame.draw.rect(screen, (30, 25, 35), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(
            screen, (100, 80, 60), (bar_x, bar_y, bar_width, bar_height), 2
        )

        # Health fill with color gradient
        health_percent = max(0, min(100, health)) / 100
        health_width = int(bar_width * health_percent)

        if health_percent > 0.5:
            # Green to yellow
            health_color = (50, 200, 50)
        elif health_percent > 0.25:
            health_color = (220, 200, 50)
        else:
            health_color = (220, 50, 50)

        if health_width > 0:
            pygame.draw.rect(
                screen,
                health_color,
                (bar_x + 2, bar_y + 2, health_width - 4, bar_height - 4),
            )

        # Health text
        font = pygame.font.Font(None, 26)
        text = font.render(f"HP: {health}", True, (255, 255, 255))
        screen.blit(text, (bar_x + 8, bar_y + 8))

        # HP label
        label_font = pygame.font.Font(None, 18)
        label = label_font.render("HEALTH", True, (180, 180, 180))
        screen.blit(label, (bar_x, bar_y - 18))

    def _render_kills(self, screen: pygame.Surface, kills: int) -> None:
        """Render the kill counter."""
        # Kill icon (skull-like)
        x = self.screen_width - 120
        y = self.screen_height - self.height + 20

        font_title = pygame.font.Font(None, 18)
        title = font_title.render("KILLS", True, (180, 180, 180))
        screen.blit(title, (x, y))

        font_kills = pygame.font.Font(None, 36)
        kills_text = font_kills.render(f"{kills}", True, (255, 100, 100))
        screen.blit(kills_text, (x, y + 18))

    def _render_weapon(self, screen: pygame.Surface, weapon: str) -> None:
        """Render the current weapon."""
        font = pygame.font.Font(None, 22)

        # Weapon background
        box_x = self.screen_width // 2 - 80
        box_y = self.screen_height - self.height + 20
        box_width = 160
        box_height = 35

        pygame.draw.rect(screen, (30, 25, 35), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(
            screen, (100, 80, 60), (box_x, box_y, box_width, box_height), 1
        )

        text = font.render(f"WEAPON: {weapon.upper()}", True, (200, 200, 200))
        text_rect = text.get_rect(
            center=(box_x + box_width // 2, box_y + box_height // 2)
        )
        screen.blit(text, text_rect)
