"""
Raycasting - handles raycasting calculations for 3D rendering
"""

import math
from typing import List, Tuple, Dict, Any

from physics.physics import Physics


class Raycaster:
    """Handles raycasting calculations for rendering."""

    def __init__(self, physics: Physics):
        self.physics = physics

        # Raycasting configuration
        self.fov = math.pi / 3  # 60 degrees
        self.num_rays = 320
        self.max_depth = 20.0
        self.ray_step = 0.02

    def cast_rays(
        self, player_x: float, player_y: float, player_angle: float
    ) -> List[Dict[str, Any]]:
        """Cast multiple rays for the player's field of view."""
        results = []

        # Calculate angle step
        angle_step = self.fov / self.num_rays
        start_angle = player_angle - self.fov / 2

        for i in range(self.num_rays):
            ray_angle = start_angle + angle_step * i
            result = self.physics.cast_ray(ray_angle, player_x, player_y)

            # Apply fisheye correction
            result["dist"] = result["dist"] * math.cos(ray_angle - player_angle)

            results.append(
                {
                    "angle": ray_angle,
                    "distance": result["dist"],
                    "side": result["side"],
                }
            )

        return results

    def cast_single_ray(
        self, player_x: float, player_y: float, ray_angle: float
    ) -> Dict[str, Any]:
        """Cast a single ray."""
        return self.physics.cast_ray(ray_angle, player_x, player_y)

    def get_wall_heights(self, distances: List[float], screen_height: int) -> List[int]:
        """Calculate wall heights based on distances."""
        heights = []

        for dist in distances:
            if dist < 0.1:
                dist = 0.1

            # Calculate wall height (closer = taller)
            height = int(screen_height / dist)
            heights.append(min(height, screen_height))

        return heights

    def calculate_sprite_position(
        self,
        sprite_x: float,
        sprite_y: float,
        player_x: float,
        player_y: float,
        player_angle: float,
    ) -> Tuple[float, float, float]:
        """Calculate sprite position and distance relative to player."""
        dx = sprite_x - player_x
        dy = sprite_y - player_y
        dist = math.sqrt(dx * dx + dy * dy)

        # Calculate angle to sprite
        angle = math.atan2(dy, dx) - player_angle

        # Normalize angle to [-pi, pi]
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi

        return (angle, dist)


class ZBuffer:
    """Z-buffer for sprite rendering."""

    def __init__(self, width: int):
        self.width = width
        self.buffer = [float("inf")] * width

    def update(self, distances: List[float], ray_count: int) -> None:
        """Update z-buffer with new ray distances."""
        if not distances:
            return

        step = self.width / ray_count

        for i, dist in enumerate(distances):
            start_x = int(i * step)
            end_x = int((i + 1) * step)

            for x in range(start_x, min(end_x, self.width)):
                if x < self.width:
                    self.buffer[x] = min(self.buffer[x], dist)

    def is_visible(self, x: int, distance: float) -> bool:
        """Check if a sprite at x with given distance is visible."""
        if 0 <= x < self.width:
            return distance < self.buffer[x]
        return False

    def clear(self) -> None:
        """Clear the z-buffer."""
        self.buffer = [float("inf")] * self.width
