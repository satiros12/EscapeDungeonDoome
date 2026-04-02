"""
Renderer - handles all game rendering using Pygame
"""

import pygame
import math
from typing import List, Tuple, Optional

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FOV, RAY_COUNT, MAX_DEPTH, COLOR_GRAY


class Renderer:
    """Handles all rendering operations."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Clear the screen with a color."""
        self.screen.fill(color)

    def present(self) -> None:
        """Flip the display."""
        pygame.display.flip()

    def render_floor_ceiling(self) -> None:
        """Render floor and ceiling with gradient."""
        # Ceiling (dark gray gradient)
        for y in range(self.height // 2):
            shade = int(30 + (y / (self.height // 2)) * 20)
            pygame.draw.line(
                self.screen, (shade, shade, shade), (0, y), (self.width, y)
            )

        # Floor (darker gradient)
        for y in range(self.height // 2, self.height):
            shade = int(40 - ((y - self.height // 2) / (self.height // 2)) * 30)
            pygame.draw.line(
                self.screen,
                (shade // 2, shade // 2, shade // 2),
                (0, y),
                (self.width, y),
            )

    def render_walls_raycasted(
        self, player, wall_distances: List[float], map_data: dict
    ) -> None:
        """Render walls using raycasting data."""
        num_rays = len(wall_distances)
        if num_rays == 0:
            return

        strip_width = self.width // num_rays

        for i, distance in enumerate(wall_distances):
            # Fix fisheye effect
            corrected_distance = distance * math.cos(
                player.angle - (player.angle - FOV / 2 + FOV * i / num_rays)
            )

            # Calculate wall height based on distance
            if corrected_distance > 0:
                wall_height = min(self.height, int(self.height / corrected_distance))
            else:
                wall_height = self.height

            # Calculate color based on distance (fog effect)
            shade = max(50, min(255, int(255 - (corrected_distance / MAX_DEPTH) * 200)))
            wall_color = (shade, shade, shade)

            # Draw wall strip
            x = i * strip_width
            y = (self.height - wall_height) // 2

            pygame.draw.rect(
                self.screen, wall_color, (x, y, strip_width + 1, wall_height)
            )

    def render_enemies(self, player, enemies: List, map_data: dict) -> None:
        """Render enemies as 2D sprites based on distance and angle."""
        visible_enemies = []

        for enemy in enemies:
            if enemy.state in ("dead", "dying"):
                continue

            # Calculate angle to enemy
            dx = enemy.x - player.x
            dy = enemy.y - player.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= 0.1:
                continue

            # Calculate relative angle
            angle_to_enemy = math.atan2(dy, dx)
            relative_angle = angle_to_enemy - player.angle

            # Normalize angle to -PI to PI
            while relative_angle > math.pi:
                relative_angle -= 2 * math.pi
            while relative_angle < -math.pi:
                relative_angle += 2 * math.pi

            # Check if enemy is in FOV
            fov_rad = math.radians(FOV)
            if abs(relative_angle) <= fov_rad / 2:
                visible_enemies.append(
                    {"enemy": enemy, "distance": dist, "angle": relative_angle}
                )

        # Sort by distance (far to near so near draws on top)
        visible_enemies.sort(key=lambda e: e["distance"], reverse=True)

        # Render enemies
        for enemy_data in visible_enemies:
            enemy = enemy_data["enemy"]
            dist = enemy_data["distance"]
            relative_angle = enemy_data["angle"]

            # Calculate screen position
            fov_rad = math.radians(FOV)
            screen_x = int(
                self.width // 2 + (relative_angle / (fov_rad / 2)) * (self.width // 2)
            )

            # Calculate sprite size based on distance
            sprite_size = int(min(self.height, self.height / dist))
            sprite_size = max(20, min(200, sprite_size))

            # Calculate vertical position (floor)
            sprite_y = self.height // 2 + (self.height // 4) - (sprite_size // 4)
            sprite_y = max(0, min(self.height - sprite_size, sprite_y))

            # Color based on enemy state
            if enemy.state == "chase":
                color = (200, 50, 50)  # Red when chasing
            elif enemy.state == "attack":
                color = (255, 100, 100)  # Bright red when attacking
            else:
                color = (150, 50, 50)  # Dark red otherwise

            # Draw enemy as rectangle (could be sprite)
            rect = pygame.Rect(
                screen_x - sprite_size // 2, sprite_y, sprite_size, sprite_size
            )
            pygame.draw.rect(self.screen, color, rect)

            # Draw outline
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

    def render_crosshair(self) -> None:
        """Render crosshair in center of screen."""
        center_x = self.width // 2
        center_y = self.height // 2

        # Draw cross
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (center_x - 10, center_y),
            (center_x + 10, center_y),
            2,
        )
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (center_x, center_y - 10),
            (center_x, center_y + 10),
            2,
        )

    def render_sprite(
        self, x: int, y: int, image: pygame.Surface, scale: float = 1.0
    ) -> None:
        """Render a sprite at screen position."""
        if scale != 1.0:
            width = int(image.get_width() * scale)
            height = int(image.get_height() * scale)
            image = pygame.transform.scale(image, (width, height))
        self.screen.blit(image, (x, y))

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
        rect = surface.get_rect(center=(x, y))
        self.screen.blit(surface, rect)

    def render_hud(self, health: int, kills: int, fps: int = 0) -> None:
        """Render the heads-up display (legacy method)."""
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

        # Render FPS if provided
        if fps > 0:
            self.render_text(f"FPS: {fps}", self.width - 80, 10, (0, 255, 0), 18)
