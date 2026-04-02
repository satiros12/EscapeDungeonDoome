"""Physics engine for WebDoom server"""

import math
from game_state import GameState, GameConfig


class Physics:
    def __init__(self, state: GameState):
        self.state = state

    def _get_current_grid(self):
        """Get current map grid from state"""
        map_info = self.state.map_manager.get_current_map()
        return map_info.get("grid", [])

    def is_wall(self, x: float, y: float) -> bool:
        """Check if a position is a wall"""
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

    def has_line_of_sight(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Check if there's a clear line of sight between two points"""
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

    def cast_ray(self, ray_angle: float, player_x: float, player_y: float) -> dict:
        """Cast a ray and return distance and wall side"""
        sin_val = math.sin(ray_angle)
        cos_val = math.cos(ray_angle)

        if abs(sin_val) < 0.0001:
            sin_val = 0.0001
        if abs(cos_val) < 0.0001:
            cos_val = 0.0001

        dist = 0.0
        step = GameConfig.RAY_STEP

        while dist < GameConfig.MAX_DEPTH:
            dist += step
            test_x = player_x + cos_val * dist
            test_y = player_y + sin_val * dist

            if self.is_wall(test_x, test_y):
                side = 0
                mx = int(test_x)
                my = int(test_y)
                prev_x = player_x + cos_val * (dist - step)
                prev_y = player_y + sin_val * (dist - step)
                if mx != int(prev_x):
                    side = 1
                return {"dist": dist, "side": side}

        return {"dist": GameConfig.MAX_DEPTH, "side": 0}

    def check_collision(self, x: float, y: float) -> bool:
        """Check if a position collides with a wall (with margin)"""
        margin = GameConfig.COLLISION_MARGIN
        # Check 4 corners around the position to avoid walking through walls
        return (
            self.is_wall(x - margin, y - margin)
            or self.is_wall(x + margin, y - margin)
            or self.is_wall(x - margin, y + margin)
            or self.is_wall(x + margin, y + margin)
        )
