"""Pathfinding module for WebDoom using A* algorithm"""

import heapq
import os
import sys
from typing import List, Tuple, Optional

# Add server directory to path for imports
_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
if _SERVER_DIR not in sys.path:
    sys.path.insert(0, _SERVER_DIR)

from game_state import GameState


class Pathfinding:
    """A* pathfinding for enemies to navigate around obstacles"""

    def __init__(self, state: GameState):
        self.state = state

    def _get_current_grid(self):
        """Get current map grid from state"""
        map_info = self.state.map_manager.get_current_map()
        return map_info.get("grid", [])

    def _get_grid_size(self):
        """Get current map grid dimensions"""
        grid = self._get_current_grid()
        if not grid:
            return (0, 0)
        return (len(grid[0]) if grid else 0, len(grid) if grid else 0)

    def find_path(
        self, start_x: float, start_y: float, end_x: float, end_y: float
    ) -> Optional[List[Tuple[float, float]]]:
        """Find path using A* algorithm from start to end position"""
        # Convert to grid coordinates
        start = (int(start_x), int(start_y))
        end = (int(end_x), int(end_y))

        width, height = self._get_grid_size()

        # Handle edge cases
        if not self._is_valid_grid(end, width, height):
            return None

        if start == end:
            return [(end_x, end_y)]

        # A* implementation
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, end)}

        # Track visited to avoid infinite loops
        visited = set()

        while open_set:
            _, current = heapq.heappop(open_set)

            if current in visited:
                continue
            visited.add(current)

            if current == end:
                return self._reconstruct_path(came_from, current, end_x, end_y)

            for neighbor in self._get_neighbors(current, width, height):
                if not self._is_walkable(neighbor):
                    continue

                tentative_g = g_score[current] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None  # No path found

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Manhattan distance heuristic for A*"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _get_neighbors(
        self, node: Tuple[int, int], width: int = None, height: int = None
    ) -> List[Tuple[int, int]]:
        """Get walkable neighbors (4-directional movement)"""
        if width is None or height is None:
            width, height = self._get_grid_size()
        x, y = node
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        # Filter valid grid positions
        return [n for n in neighbors if self._is_valid_grid(n, width, height)]

    def _is_valid_grid(
        self, node: Tuple[int, int], width: int = None, height: int = None
    ) -> bool:
        """Check if node is within map bounds"""
        if width is None or height is None:
            width, height = self._get_grid_size()
        x, y = node
        return 0 <= x < width and 0 <= y < height

    def _is_walkable(self, node: Tuple[int, int]) -> bool:
        """Check if node is walkable (not a wall)"""
        x, y = node
        # Check center of grid cell
        check_x = x + 0.5
        check_y = y + 0.5
        return not self._is_wall(check_x, check_y)

    def _is_wall(self, x: float, y: float) -> bool:
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

    def _reconstruct_path(
        self, came_from: dict, current: Tuple[int, int], end_x: float, end_y: float
    ) -> List[Tuple[float, float]]:
        """Reconstruct path from start to end, converting to world coordinates"""
        path = []
        while current in came_from:
            # Convert grid coords to world coords (center of cell)
            path.append((current[0] + 0.5, current[1] + 0.5))
            current = came_from[current]

        # Add start position
        path.append((end_x, end_y))
        return path[::-1]

    def has_line_of_sight(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Check if there's a clear line of sight between two points"""
        import math

        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 0.1:
            return True

        steps = max(1, int(dist * 10))

        for i in range(steps + 1):
            t = i / steps
            check_x = x1 + dx * t
            check_y = y1 + dy * t
            if self._is_wall(check_x, check_y):
                return False

        return True

    def get_next_path_node(
        self,
        path: List[Tuple[float, float]],
        current_x: float,
        current_y: float,
        threshold: float = 0.5,
    ) -> Optional[Tuple[float, float]]:
        """Get the next node in path that enemy should move towards"""
        if not path or len(path) < 2:
            return None

        # Find the first node that's far enough from current position
        for node in path:
            import math

            dist = math.sqrt((node[0] - current_x) ** 2 + (node[1] - current_y) ** 2)
            if dist > threshold:
                return node

        return None
