"""
Physics - handles collision detection and raycasting
"""

import math
from typing import List, Tuple, Dict, Any, Optional


class Physics:
    """Handles physics calculations and collision detection."""

    def __init__(self, state: "GameState"):
        self.state = state
        self.ray_step = 0.02
        self.max_depth = 20.0
        self.collision_margin = 0.35

    def is_wall(self, x: float, y: float) -> bool:
        """Check if a position is a wall."""
        grid = self._get_current_grid()
        if not grid:
            return True

        mx = int(x)
        my = int(y)
        width = len(grid[0]) if grid else 0
        height = len(grid) if grid else 0

        if mx < 0 or mx >= width or my < 0 or my >= height:
            return True

        return grid[my][mx] == "#"

    def _get_current_grid(self) -> List[str]:
        """Get current map grid from state."""
        return self.state.map_manager.get_current_map().get("grid", [])

    def has_line_of_sight(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Check if there's a clear line of sight between two points."""
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
        """Cast a ray and return distance and wall side."""
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
        """Check if a position collides with a wall (with margin)."""
        margin = self.collision_margin
        return (
            self.is_wall(x - margin, y - margin)
            or self.is_wall(x + margin, y - margin)
            or self.is_wall(x - margin, y + margin)
            or self.is_wall(x + margin, y + margin)
        )

    def distance_to_wall(self, x: float, y: float, angle: float) -> float:
        """Calculate distance from a point to the nearest wall in a direction."""
        result = self.cast_ray(angle, x, y)
        return result.get("dist", self.max_depth)

    def get_wall_normal(self, x: float, y: float) -> Tuple[float, float]:
        """Get the normal vector of the wall at a position."""
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
