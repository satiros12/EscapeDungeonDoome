"""
Renderer - handles all game rendering using Pygame
With dungeon textures and wood floor
"""

import pygame
import math
import random
from typing import List, Tuple

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FOV, RAY_COUNT, MAX_DEPTH


class Renderer:
    """Handles all rendering operations."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Physics for line of sight
        self.physics = None

        # Textures - create simple patterns
        self._create_textures()

    def set_physics(self, physics) -> None:
        """Set physics engine for line of sight checking."""
        self.physics = physics

    def _create_textures(self):
        """Create simple dungeon textures."""
        # Wall texture - stone bricks pattern
        self.wall_texture = self._create_stone_wall_texture()

        # Floor texture - wood planks
        self.floor_texture = self._create_wood_floor_texture()

        # Ceiling texture - stone
        self.ceiling_texture = self._create_ceiling_texture()

    def _create_stone_wall_texture(self) -> pygame.Surface:
        """Create stone wall texture."""
        texture = pygame.Surface((64, 64))
        base_color = (100, 90, 80)  # Brown-gray stone

        # Base fill
        texture.fill(base_color)

        # Add brick pattern
        for y in range(0, 64, 16):
            offset = 0 if (y // 16) % 2 == 0 else 8
            for x in range(-offset, 64, 16):
                # Brick border
                pygame.draw.rect(texture, (70, 60, 50), (x, y, 14, 14), 1)
                # Random stone variation
                for _ in range(3):
                    sx = random.randint(x + 1, x + 12)
                    sy = random.randint(y + 1, y + 12)
                    pygame.draw.rect(
                        texture,
                        (
                            random.randint(90, 110),
                            random.randint(80, 100),
                            random.randint(70, 90),
                        ),
                        (sx, sy, 3, 3),
                    )

        return texture

    def _create_wood_floor_texture(self) -> pygame.Surface:
        """Create wood plank floor texture."""
        texture = pygame.Surface((64, 64))
        base_color = (80, 55, 30)  # Dark wood

        # Base fill
        texture.fill(base_color)

        # Wood grain lines (planks)
        for x in range(0, 64, 8):
            pygame.draw.line(texture, (50, 35, 20), (x, 0), (x, 64), 1)

        # Wood grain
        for _ in range(20):
            x1 = random.randint(0, 60)
            x2 = random.randint(x1, x1 + 10)
            y1 = random.randint(0, 60)
            y2 = random.randint(y1, y1 + 20)
            pygame.draw.line(texture, (60, 40, 20), (x1, y1), (x2, y2), 1)

        return texture

    def _create_ceiling_texture(self) -> pygame.Surface:
        """Create stone ceiling texture."""
        texture = pygame.Surface((64, 64))
        base_color = (70, 70, 75)  # Blue-gray stone

        texture.fill(base_color)

        # Stone tile pattern
        for x in range(0, 64, 16):
            for y in range(0, 64, 16):
                pygame.draw.rect(texture, (55, 55, 60), (x, y, 15, 15), 1)

        return texture

    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Clear the screen with a color."""
        self.screen.fill(color)

    def present(self) -> None:
        """Flip the display."""
        pygame.display.flip()

    def render_floor_ceiling(self) -> None:
        """Render floor and ceiling with textures."""
        ceiling_height = self.height // 2

        # Draw ceiling with texture
        for x in range(0, self.width, 64):
            for y in range(0, ceiling_height, 64):
                self.screen.blit(self.ceiling_texture, (x, y))

        # Draw floor with texture
        for x in range(0, self.width, 64):
            for y in range(ceiling_height, self.height, 64):
                # Darken floor texture
                floor_copy = self.floor_texture.copy()
                floor_copy.fill((0, 0, 0), None, pygame.BLEND_MULT)
                self.screen.blit(floor_copy, (x, y))

        # Horizon line
        pygame.draw.line(
            self.screen,
            (30, 30, 30),
            (0, ceiling_height),
            (self.width, ceiling_height),
            4,
        )

    def render_walls_raycasted(
        self, player, wall_distances: List[float], map_data: dict
    ) -> None:
        """Render walls using raycasting data with textures."""
        num_rays = len(wall_distances)
        if num_rays == 0:
            return

        strip_width = self.width // num_rays
        if strip_width < 1:
            strip_width = 1

        for i, distance in enumerate(wall_distances):
            # Fix fisheye effect
            ray_angle = -FOV / 2 + FOV * i / num_rays
            corrected_distance = max(0.1, distance)

            # Calculate wall height based on distance
            wall_height = min(self.height, int(self.height / corrected_distance))

            # Calculate texture UV coordinates
            # Get world position
            check_x = player.x + math.cos(player.angle + ray_angle) * distance
            check_y = player.y + math.sin(player.angle + ray_angle) * distance

            # Texture coordinate based on position
            tex_x = int((check_x * 10) % 64)
            tex_y = int((check_y * 10) % 64)

            # Calculate shading based on distance
            shade = max(0.3, 1.0 - (corrected_distance / MAX_DEPTH))

            # Draw wall strip
            x = i * strip_width
            y_top = (self.height - wall_height) // 2

            # Get texture column
            tex_col = self.wall_texture.get_at((tex_x % 64, 0))

            # Draw scaled texture strip
            for ty in range(wall_height):
                world_y = (y_top + ty) / self.height
                tex_y = int(world_y * 64) % 64
                color = self.wall_texture.get_at((tex_x % 64, tex_y))

                # Apply shading
                shaded_color = (
                    int(color[0] * shade),
                    int(color[1] * shade),
                    int(color[2] * shade),
                )
                pygame.draw.line(
                    self.screen,
                    shaded_color,
                    (x, y_top + ty),
                    (x + strip_width, y_top + ty),
                )

            # Draw edges
            if wall_height < self.height:
                pygame.draw.line(
                    self.screen,
                    (
                        max(0, int(100 * shade - 30)),
                        max(0, int(90 * shade - 30)),
                        max(0, int(80 * shade - 30)),
                    ),
                    (x, y_top),
                    (x + strip_width, y_top),
                    1,
                )
                pygame.draw.line(
                    self.screen,
                    (
                        min(255, int(100 * shade + 20)),
                        min(255, int(90 * shade + 20)),
                        min(255, int(80 * shade + 20)),
                    ),
                    (x, y_top + wall_height),
                    (x + strip_width, y_top + wall_height),
                    1,
                )

    def render_enemies(self, player, enemies: List, map_data: dict) -> None:
        """Render enemies - only if visible (not behind walls)."""
        visible_enemies = []

        for enemy in enemies:
            if enemy.state in ("dead", "dying"):
                continue

            dx = enemy.x - player.x
            dy = enemy.y - player.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= 0.1:
                continue

            # Check line of sight
            if self.physics and not self.physics.has_line_of_sight(
                player.x, player.y, enemy.x, enemy.y
            ):
                continue

            angle_to_enemy = math.atan2(dy, dx)
            relative_angle = angle_to_enemy - player.angle

            while relative_angle > math.pi:
                relative_angle -= 2 * math.pi
            while relative_angle < -math.pi:
                relative_angle += 2 * math.pi

            fov_rad = math.radians(FOV)
            if abs(relative_angle) <= fov_rad / 2:
                visible_enemies.append(
                    {"enemy": enemy, "distance": dist, "angle": relative_angle}
                )

        visible_enemies.sort(key=lambda e: e["distance"], reverse=True)

        for enemy_data in visible_enemies:
            enemy = enemy_data["enemy"]
            dist = enemy_data["distance"]
            relative_angle = enemy_data["angle"]

            fov_rad = math.radians(FOV)
            screen_x = int(
                self.width // 2 + (relative_angle / (fov_rad / 2)) * (self.width // 2)
            )

            sprite_size = int(min(self.height * 0.6, self.height / dist))
            sprite_size = max(15, min(150, sprite_size))

            sprite_y = self.height // 2 + self.height // 4 - sprite_size // 3
            sprite_y = max(0, min(self.height - sprite_size, sprite_y))

            # Color based on state
            if enemy.state == "attack":
                color = (220, 0, 0)
            elif enemy.state == "chase":
                color = (180, 0, 0)
            else:
                color = (100, 0, 0)

            rect = pygame.Rect(
                screen_x - sprite_size // 2, sprite_y, sprite_size, sprite_size
            )
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

            # Eyes
            eye_size = max(2, sprite_size // 10)
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

        pygame.draw.line(
            self.screen,
            (0, 255, 0),
            (center_x - 10, center_y),
            (center_x + 10, center_y),
            2,
        )
        pygame.draw.line(
            self.screen,
            (0, 255, 0),
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
        bar_x, bar_y = 20, self.height - 50
        bar_width, bar_height = 200, 25

        pygame.draw.rect(self.screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(
            self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2
        )

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

        self.render_text(f"HP: {health}", bar_x + 100, bar_y - 15, (255, 255, 255), 20)
        self.render_text(f"KILLS: {kills}", 20, 30, (255, 100, 100), 28)

        if fps > 0:
            self.render_text(f"FPS: {fps}", self.width - 80, 20, (100, 255, 100), 18)
