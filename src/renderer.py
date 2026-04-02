"""
Renderer - handles all game rendering using Pygame
Optimized version with lighting and shadows
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

        # Pre-rendered textures (cached for performance)
        self._create_textures()

        # Pre-rendered floor/ceiling surfaces
        self._floor_surface = None
        self._ceiling_surface = None
        self._create_floor_ceiling_surfaces()

        # Lighting surface for vignette
        self._vignette_surface = None
        self._create_vignette()

        # Torch flicker value
        self._torch_flicker = 0

    def set_physics(self, physics) -> None:
        """Set physics engine for line of sight checking."""
        self.physics = physics

    def _create_textures(self):
        """Create simple dungeon textures."""
        self.wall_texture = self._create_stone_wall_texture()
        self.floor_texture = self._create_wood_floor_texture()
        self.ceiling_texture = self._create_ceiling_texture()

    def _create_stone_wall_texture(self) -> pygame.Surface:
        """Create stone wall texture."""
        texture = pygame.Surface((64, 64))
        base_color = (100, 90, 80)
        texture.fill(base_color)

        for y in range(0, 64, 16):
            offset = 0 if (y // 16) % 2 == 0 else 8
            for x in range(-offset, 64, 16):
                pygame.draw.rect(texture, (70, 60, 50), (x, y, 14, 14), 1)
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
        base_color = (80, 55, 30)
        texture.fill(base_color)

        for x in range(0, 64, 8):
            pygame.draw.line(texture, (50, 35, 20), (x, 0), (x, 64), 1)

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
        base_color = (70, 70, 75)
        texture.fill(base_color)

        for x in range(0, 64, 16):
            for y in range(0, 64, 16):
                pygame.draw.rect(texture, (55, 55, 60), (x, y, 15, 15), 1)

        return texture

    def _create_floor_ceiling_surfaces(self):
        """Pre-render floor and ceiling for performance."""
        ceiling_height = self.height // 2

        self._ceiling_surface = pygame.Surface((self.width, ceiling_height))
        for x in range(0, self.width, 64):
            for y in range(0, ceiling_height, 64):
                self._ceiling_surface.blit(self.ceiling_texture, (x, y))

        floor_height = self.height - ceiling_height
        self._floor_surface = pygame.Surface((self.width, floor_height))
        for x in range(0, self.width, 64):
            for y in range(0, floor_height, 64):
                floor_copy = self.floor_texture.copy()
                floor_copy.fill((0, 0, 0), None, pygame.BLEND_MULT)
                self._floor_surface.blit(floor_copy, (x, y))

    def _create_vignette(self):
        """Create vignette overlay for lighting effect."""
        self._vignette_surface = pygame.Surface(
            (self.width, self.height), pygame.SRCALPHA
        )

        # Create radial gradient - darker at edges
        center_x = self.width // 2
        center_y = self.height // 2

        # Simple vignette - draw transparent ellipses from center
        for i in range(20, 0, -1):
            alpha = i * 3
            ellipse_w = center_x * i // 20
            ellipse_h = center_y * i // 20
            pygame.draw.ellipse(
                self._vignette_surface,
                (0, 0, 0, alpha),
                (
                    center_x - ellipse_w,
                    center_y - ellipse_h,
                    ellipse_w * 2,
                    ellipse_h * 2,
                ),
                0,
            )

    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Clear the screen with a color."""
        self.screen.fill(color)

    def present(self) -> None:
        """Flip the display."""
        pygame.display.flip()

    def render_floor_ceiling(self) -> None:
        """Render floor and ceiling using pre-rendered surfaces."""
        ceiling_height = self.height // 2

        # Draw ceiling
        self.screen.blit(self._ceiling_surface, (0, 0))

        # Draw floor
        self.screen.blit(self._floor_surface, (0, ceiling_height))

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
        """Render walls using raycasting - optimized."""
        num_rays = len(wall_distances)
        if num_rays == 0:
            return

        # Calculate strip width - larger strips for performance
        strip_width = max(2, self.width // num_rays)

        # Skip every other ray for 2x performance boost
        step = 2

        for i in range(0, num_rays, step):
            distance = wall_distances[i]
            if distance >= MAX_DEPTH:
                continue

            # Fix fisheye effect
            ray_angle = -FOV / 2 + FOV * i / num_rays
            corrected_distance = max(0.1, distance)

            # Calculate wall height
            wall_height = int(self.height / corrected_distance)
            wall_height = min(self.height, max(1, wall_height))

            # Calculate shading based on distance
            shade = 1.0 - (corrected_distance / MAX_DEPTH)
            shade = max(0.15, min(1.0, shade))

            # Wall color with distance shading
            r = int(180 * shade)
            g = int(160 * shade)
            b = int(140 * shade)
            wall_color = (r, g, b)

            # Draw wall strip
            x = (i // step) * strip_width
            y_top = (self.height - wall_height) // 2

            pygame.draw.rect(
                self.screen, wall_color, (x, y_top, strip_width + 1, wall_height)
            )

            # Edge highlights
            if wall_height < self.height:
                top_color = tuple(min(255, c + 20) for c in wall_color)
                pygame.draw.line(
                    self.screen, top_color, (x, y_top), (x + strip_width, y_top), 1
                )

                bottom_color = tuple(max(0, c - 30) for c in wall_color)
                pygame.draw.line(
                    self.screen,
                    bottom_color,
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

            sprite_size = int(min(self.height * 0.5, self.height / dist))
            sprite_size = max(12, min(100, sprite_size))

            sprite_y = self.height // 2 + self.height // 4 - sprite_size // 3
            sprite_y = max(0, min(self.height - sprite_size, sprite_y))

            # Color based on state with distance shading
            shade = max(0.3, 1.0 - dist / MAX_DEPTH)

            if enemy.state == "attack":
                base_color = (220, 0, 0)
            elif enemy.state == "chase":
                base_color = (180, 0, 0)
            else:
                base_color = (100, 0, 0)

            color = tuple(int(c * shade) for c in base_color)

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

    def render_lighting(self, player) -> None:
        """Render lighting effects - vignette and torch flicker."""
        # Update torch flicker
        self._torch_flicker = random.randint(-3, 3)

        # Apply vignette overlay
        self.screen.blit(self._vignette_surface, (0, 0))

        # Add subtle torch light circle around player (center of screen)
        center_x = self.width // 2
        center_y = self.height // 2

        # Create radial light gradient (simulating torch)
        light_radius = 200
        light_surface = pygame.Surface(
            (light_radius * 2, light_radius * 2), pygame.SRCALPHA
        )

        for r in range(light_radius, 0, -5):
            alpha = max(0, 40 - r // 5 + self._torch_flicker)
            pygame.draw.circle(
                light_surface, (255, 200, 100, alpha), (light_radius, light_radius), r
            )

        # Blit light circle centered on screen
        self.screen.blit(
            light_surface, (center_x - light_radius, center_y - light_radius)
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
