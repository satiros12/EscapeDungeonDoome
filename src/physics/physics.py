"""
Physics - handles collision detection and raycasting

This module provides the Physics class which implements the IPhysics interface.
It handles collision detection, raycasting for rendering, and line of sight calculations.
"""

import math
from typing import Dict, Any, List, Tuple, Optional

from physics.interfaces import IPhysics


class Physics(IPhysics):
    """
    Handles physics calculations and collision detection.

    This class implements the IPhysics interface and provides:
    - Wall collision detection
    - Raycasting for rendering
    - Line of sight calculations
    - Distance and normal calculations

    Attributes:
        ray_step: Step size for ray marching
        max_depth: Maximum ray distance
        collision_margin: Margin for collision checking
    """

    def __init__(self, grid: Optional[List[str]] = None):
        """
        Initialize the physics engine.

        Args:
            grid: Optional map grid to use. If None, must call set_map() later.
        """
        self._grid: Optional[List[str]] = grid
        self.ray_step: float = 0.02
        self.max_depth: float = 20.0
        self.collision_margin: float = 0.35

    def set_map(self, grid: List[str]) -> None:
        """
        Set the map grid for physics calculations.

        Args:
            grid: List of strings representing map rows
        """
        self._grid = grid

    def get_map(self) -> Optional[List[str]]:
        """
        Get the current map grid.

        Returns:
            The current map grid or None if not set
        """
        return self._grid

    def is_wall(self, x: float, y: float) -> bool:
        """
        Check if a position contains a wall.

        Args:
            x: X coordinate to check
            y: Y coordinate to check

        Returns:
            True if position contains a wall, False otherwise
        """
        if not self._grid:
            return True

        mx = int(x)
        my = int(y)
        width = len(self._grid[0]) if self._grid else 0
        height = len(self._grid) if self._grid else 0

        if mx < 0 or mx >= width or my < 0 or my >= height:
            return True

        return self._grid[my][mx] == "#"

    def has_line_of_sight(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """
        Check if there's a clear line of sight between two points.

        Uses raycasting to determine if the path between two points
        is blocked by walls.

        Args:
            x1: Starting X coordinate
            y1: Starting Y coordinate
            x2: Target X coordinate
            y2: Target Y coordinate

        Returns:
            True if line of sight is clear, False if blocked
        """
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)
        steps = math.ceil(dist * 10)

        for i in range(steps):
            t = i / steps
            check_x = x1 + dx * t
            check_y = y1 + dy * t
            if self.is_wall(check_x, check_y):
                return False
        return True

    def cast_ray(
        self, ray_angle: float, player_x: float, player_y: float
    ) -> Dict[str, Any]:
        """
        Cast a ray from a point and return collision information.

        Args:
            ray_angle: Angle of the ray in radians
            player_x: Starting X coordinate
            player_y: Starting Y coordinate

        Returns:
            Dictionary with:
                - dist: Distance to wall
                - side: Wall side (0 or 1 for shading)
        """
        cos_val = math.cos(ray_angle)
        sin_val = math.sin(ray_angle)

        if abs(sin_val) < 0.0001:
            sin_val = 0.0001
        if abs(cos_val) < 0.0001:
            cos_val = 0.0001

        dist = 0.0

        while dist < self.max_depth:
            dist += self.ray_step
            test_x = player_x + cos_val * dist
            test_y = player_y + sin_val * dist

            if self.is_wall(test_x, test_y):
                side = 0
                mx = int(test_x)
                my = int(test_y)
                prev_x = player_x + cos_val * (dist - self.ray_step)
                prev_y = player_y + sin_val * (dist - self.ray_step)
                if mx != int(prev_x):
                    side = 1
                return {"dist": dist, "side": side}

        return {"dist": self.max_depth, "side": 0}

    def check_collision(self, x: float, y: float) -> bool:
        """
        Check if a position collides with any wall.

        Uses collision margin to prevent clipping through walls.

        Args:
            x: X coordinate to check
            y: Y coordinate to check

        Returns:
            True if position collides with wall, False otherwise
        """
        margin = self.collision_margin
        return (
            self.is_wall(x - margin, y - margin)
            or self.is_wall(x + margin, y - margin)
            or self.is_wall(x - margin, y + margin)
            or self.is_wall(x + margin, y + margin)
        )

    def distance_to_wall(self, x: float, y: float, angle: float) -> float:
        """
        Calculate distance from a point to the nearest wall in a direction.

        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
            angle: Direction angle in radians

        Returns:
            Distance to the nearest wall
        """
        result = self.cast_ray(angle, x, y)
        return result.get("dist", self.max_depth)

    def get_wall_normal(self, x: float, y: float) -> Tuple[float, float]:
        """
        Get the normal vector of the wall at a position.

        Args:
            x: X coordinate to check
            y: Y coordinate to check

        Returns:
            Tuple of (nx, ny) representing the wall normal
        """
        mx = int(x)
        my = int(y)

        left = self.is_wall(mx - 1, my)
        right = self.is_wall(mx + 1, my)
        up = self.is_wall(mx, my - 1)
        down = self.is_wall(mx, my + 1)

        nx = 0.0
        ny = 0.0

        if left and not right:
            nx = 1.0
        elif right and not left:
            nx = -1.0

        if up and not down:
            ny = 1.0
        elif down and not up:
            ny = -1.0

        # Normalize
        length = math.sqrt(nx * nx + ny * ny)
        if length > 0:
            nx /= length
            ny /= length

        return (nx, ny)
