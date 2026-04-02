"""
Renderer - handles all game rendering using Pygame
"""

import pygame
import math
import random
from typing import List, Tuple, Optional

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FOV, RAY_COUNT, MAX_DEPTH


class Renderer:
    """Handles all rendering operations."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Wall colors - more varied and colorful
        self.wall_colors = {
            0: (180, 140, 100),  # Brown/tan
            1: (120, 120, 140),  # Gray-blue
            2: (100, 150, 100),  # Greenish
            3: (150, 100, 100),  # Reddish
            4: (100, 100, 150),  # Blueish
            5: (140, 140, 100),  # Olive
        }

        # Floor and ceiling colors
        self.ceiling_color = (40, 40, 50)
        self.floor_color = (60, 50, 40)

    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Clear the screen with a color."""
        self.screen.fill(color)

    def present(self) -> None:
        """Flip the display."""
        pygame.display.flip()

    def render_floor_ceiling(self) -> None:
        """Render floor and ceiling with gradient."""
        # Ceiling - dark blue-gray gradient
        ceiling_height = self.height // 2
        for y in range(ceiling_height):
            shade = int(20 + (y / ceiling_height) * 30)
            color = (shade, shade + 5, shade + 15)  # Slight blue tint
            pygame.draw.line(self.screen, color, (0, y), (self.width, y))

        # Floor - brown-ish gradient (like dungeon floor)
        for y in range(ceiling_height, self.height):
            progress = (y - ceiling_height) / ceiling_height
            r = int(50 + progress * 30)
            g = int(40 + progress * 25)
            b = int(30 + progress * 20)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))

    def render_walls_raycasted(
        self, player, wall_distances: List[float], map_data: dict
    ) -> None:
        """Render walls using raycasting data with better textures."""
        num_rays = len(wall_distances)
        if num_rays == 0:
            return

        strip_width = self.width // num_rays
        if strip_width < 1:
            strip_width = 1

        # Get map grid for texture variation
        grid = map_data.get("grid", [])

        for i, distance in enumerate(wall_distances):
            # Fix fisheye effect
            ray_angle = -FOV / 2 + FOV * i / num_rays
            corrected_distance = distance * math.cos(
                player.angle - player.angle - ray_angle
            )
            corrected_distance = max(0.1, corrected_distance)

            # Calculate wall height based on distance
            wall_height = min(self.height, int(self.height / corrected_distance))

            # Calculate which map cell this ray hits for texture variation
            check_x = player.x + math.cos(player.angle + ray_angle) * distance
            check_y = player.y + math.sin(player.angle + ray_angle) * distance

            # Get base color based on position
            cell_x = int(check_x) if check_x > 0 else 0
            cell_y = int(check_y) if check_y > 0 else 0

            # Use position hash for variation
            color_index = (cell_x + cell_y) % len(self.wall_colors)
            base_color = self.wall_colors[color_index]

            # Apply fog/shading based on distance
            shade_factor = max(0.2, 1.0 - (corrected_distance / MAX_DEPTH))
            wall_color = (
                int(base_color[0] * shade_factor),
                int(base_color[1] * shade_factor),
                int(base_color[2] * shade_factor),
            )

            # Add side shading (vertical edges darker)
            x = i * strip_width
            y_top = (self.height - wall_height) // 2
            y_bottom = y_top + wall_height

            # Draw wall strip with slight texture
            pygame.draw.rect(
                self.screen, wall_color, (x, y_top, strip_width + 1, wall_height)
            )

            # Add top/bottom edge highlight
            if wall_height < self.height:
                pygame.draw.line(
                    self.screen,
                    tuple(max(0, c - 30) for c in wall_color),
                    (x, y_top),
                    (x + strip_width, y_top),
                    1,
                )

    def render_enemies(self, player, enemies: List, map_data: dict) -> None:
        """Render enemies as 2D sprites with better visibility."""
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
            sprite_size = int(min(self.height * 0.8, self.height / dist))
            sprite_size = max(30, min(250, sprite_size))

            # Vertical position
            sprite_y = self.height // 2 + (self.height // 4) - (sprite_size // 3)
            sprite_y = max(0, min(self.height - sprite_size, sprite_y))

            # Color based on state - more visible
            if enemy.state == "attack":
                color = (255, 50, 50)  # Bright red
                outline_color = (255, 200, 200)
            elif enemy.state == "chase":
                color = (220, 80, 60)  # Red-orange
                outline_color = (255, 150, 150)
            else:
                color = (160, 60, 60)  # Dark red
                outline_color = (200, 150, 150)

            # Draw enemy as rounded rectangle
            rect = pygame.Rect(
                screen_x - sprite_size // 2, sprite_y, sprite_size, sprite_size
            )

            # Fill
            pygame.draw.rect(self.screen, color, rect)

            # Outline
            pygame.draw.rect(self.screen, outline_color, rect, 3)

            # Add "eyes" to make it look like a creature
            eye_size = sprite_size // 6
            eye_y = sprite_y + sprite_size // 3
            pygame.draw.circle(
                self.screen,
                (255, 255, 0),
                (screen_x - sprite_size // 4, eye_y),
                eye_size,
            )
            pygame.draw.circle(
                self.screen,
                (255, 255, 0),
                (screen_x + sprite_size // 4, eye_y),
                eye_size,
            )

            # Health bar above enemy
            if enemy.health < 30:
                bar_width = sprite_size
                bar_height = 5
                health_pct = enemy.health / 30
                pygame.draw.rect(
                    self.screen,
                    (50, 0, 0),
                    (screen_x - bar_width // 2, sprite_y - 10, bar_width, bar_height),
                )
                pygame.draw.rect(
                    self.screen,
                    (255, 0, 0),
                    (
                        screen_x - bar_width // 2,
                        sprite_y - 10,
                        bar_width * health_pct,
                        bar_height,
                    ),
                )

    def render_crosshair(self) -> None:
        """Render crosshair in center of screen."""
        center_x = self.width // 2
        center_y = self.height // 2

        # Draw cross with better visibility
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (center_x - 15, center_y),
            (center_x + 15, center_y),
            3,
        )
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (center_x, center_y - 15),
            (center_x, center_y + 15),
            3,
        )

        # Center dot
        pygame.draw.circle(self.screen, (255, 0, 0), (center_x, center_y), 3)

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

        # Draw bar background
        pygame.draw.rect(
            self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height)
        )
        pygame.draw.rect(
            self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2
        )

        # Health fill with color gradient
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

        # Health text
        self.render_text(f"HP: {health}", bar_x + 100, bar_y - 15, (255, 255, 255), 20)

        # Kills counter
        self.render_text(f"KILLS: {kills}", 20, 30, (255, 100, 100), 28)

        # FPS
        if fps > 0:
            self.render_text(f"FPS: {fps}", self.width - 80, 20, (100, 255, 100), 18)
