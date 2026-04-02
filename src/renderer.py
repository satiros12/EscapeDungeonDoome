"""
Renderer - handles all game rendering using Pygame
Simplified version for better clarity
"""

import pygame
import math
from typing import List, Tuple

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FOV, RAY_COUNT, MAX_DEPTH


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
        """Render floor and ceiling with simple solid colors."""
        ceiling_height = self.height // 2

        # Ceiling - solid dark gray
        pygame.draw.rect(self.screen, (30, 30, 30), (0, 0, self.width, ceiling_height))

        # Floor - solid dark brown
        pygame.draw.rect(
            self.screen, (50, 40, 30), (0, ceiling_height, self.width, ceiling_height)
        )

        # Horizon line
        pygame.draw.line(
            self.screen,
            (80, 60, 40),
            (0, ceiling_height),
            (self.width, ceiling_height),
            2,
        )

    def render_walls_raycasted(
        self, player, wall_distances: List[float], map_data: dict
    ) -> None:
        """Render walls using raycasting data - simplified."""
        num_rays = len(wall_distances)
        if num_rays == 0:
            return

        strip_width = self.width // num_rays
        if strip_width < 1:
            strip_width = 1

        ceiling_height = self.height // 2

        for i, distance in enumerate(wall_distances):
            # Fix fisheye effect
            ray_angle = -FOV / 2 + FOV * i / num_rays
            corrected_distance = distance * math.cos(player.angle - ray_angle)
            corrected_distance = max(0.1, corrected_distance)

            # Calculate wall height based on distance
            wall_height = min(self.height, int(self.height / corrected_distance))

            # Simple shading based on distance - more dramatic
            shade = int(255 * (1.0 / (1.0 + corrected_distance * 0.5)))
            shade = max(30, min(255, shade))

            # Wall color - simple gray with distance shading
            wall_color = (shade, shade, shade)

            # Calculate position
            x = i * strip_width
            y_top = (self.height - wall_height) // 2

            # Draw wall
            pygame.draw.rect(
                self.screen, wall_color, (x, y_top, strip_width + 1, wall_height)
            )

            # Draw edges for depth
            if y_top > 0:
                # Top edge (ceiling line)
                pygame.draw.line(
                    self.screen,
                    (max(0, shade - 40), max(0, shade - 40), max(0, shade - 40)),
                    (x, y_top),
                    (x + strip_width, y_top),
                    1,
                )
            if y_top + wall_height < self.height:
                # Bottom edge (floor line)
                pygame.draw.line(
                    self.screen,
                    (min(255, shade + 30), min(255, shade + 30), min(255, shade + 30)),
                    (x, y_top + wall_height),
                    (x + strip_width, y_top + wall_height),
                    1,
                )

    def render_enemies(self, player, enemies: List, map_data: dict) -> None:
        """Render enemies as simple 2D sprites."""
        visible_enemies = []

        for enemy in enemies:
            if enemy.state in ("dead", "dying"):
                continue

            dx = enemy.x - player.x
            dy = enemy.y - player.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= 0.1:
                continue

            angle_to_enemy = math.atan2(dy, dx)
            relative_angle = angle_to_enemy - player.angle

            # Normalize angle
            while relative_angle > math.pi:
                relative_angle -= 2 * math.pi
            while relative_angle < -math.pi:
                relative_angle += 2 * math.pi

            fov_rad = math.radians(FOV)
            if abs(relative_angle) <= fov_rad / 2:
                visible_enemies.append(
                    {"enemy": enemy, "distance": dist, "angle": relative_angle}
                )

        # Sort by distance (far to near)
        visible_enemies.sort(key=lambda e: e["distance"], reverse=True)

        for enemy_data in visible_enemies:
            enemy = enemy_data["enemy"]
            dist = enemy_data["distance"]
            relative_angle = enemy_data["angle"]

            fov_rad = math.radians(FOV)
            screen_x = int(
                self.width // 2 + (relative_angle / (fov_rad / 2)) * (self.width // 2)
            )

            # Calculate sprite size
            sprite_size = int(min(self.height * 0.7, self.height / dist))
            sprite_size = max(20, min(200, sprite_size))

            # Vertical position - on the floor
            sprite_y = self.height // 2 + self.height // 4 - sprite_size // 3
            sprite_y = max(0, min(self.height - sprite_size, sprite_y))

            # Simple color based on state
            if enemy.state == "attack":
                color = (200, 0, 0)  # Red
            elif enemy.state == "chase":
                color = (180, 50, 50)  # Dark red
            else:
                color = (120, 40, 40)  # Darker red

            # Draw enemy as simple square
            rect = pygame.Rect(
                screen_x - sprite_size // 2, sprite_y, sprite_size, sprite_size
            )
            pygame.draw.rect(self.screen, color, rect)

            # White outline
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

            # Two white eyes
            eye_size = max(3, sprite_size // 8)
            eye_y = sprite_y + sprite_size // 3
            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (screen_x - sprite_size // 4, eye_y),
                eye_size,
            )
            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (screen_x + sprite_size // 4, eye_y),
                eye_size,
            )

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
        """Render the heads-up display."""
        # Health bar background
        bar_x, bar_y = 20, self.height - 50
        bar_width, bar_height = 200, 25

        pygame.draw.rect(
            self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height)
        )
        pygame.draw.rect(
            self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2
        )

        # Health fill
        health_percent = max(0, min(100, health)) / 100
        health_width = int(bar_width * health_percent)

        if health_percent > 0.5:
            health_color = (0, 255, 0)
        elif health_percent > 0.25:
            health_color = (255, 255, 0)
        else:
            health_color = (255, 0, 0)

        pygame.draw.rect(
            self.screen, health_color, (bar_x, bar_y, health_width, bar_height)
        )

        # Text
        self.render_text(f"HP: {health}", bar_x + 100, bar_y - 15, (255, 255, 255), 20)
        self.render_text(f"KILLS: {kills}", 20, 30, (255, 100, 100), 28)

        if fps > 0:
            self.render_text(f"FPS: {fps}", self.width - 80, 20, (100, 255, 100), 18)
