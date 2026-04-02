"""
Physics Interfaces - Abstract interfaces for physics implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional


class IPhysics(ABC):
    """
    Abstract interface for physics implementations.

    This interface defines the contract for physics calculations
    including collision detection, raycasting, and line of sight.

    Implementations:
        - Physics: Standard raycast-based physics
        - Future: AStarPhysics for pathfinding-based movement
    """

    @abstractmethod
    def is_wall(self, x: float, y: float) -> bool:
        """
        Check if a position contains a wall.

        Args:
            x: X coordinate to check
            y: Y coordinate to check

        Returns:
            True if position contains a wall, False otherwise
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass


class IMapProvider(ABC):
    """
    Interface for providing map data to physics.

    Allows decoupling physics from direct GameState access.
    """

    @abstractmethod
    def get_map_grid(self) -> List[str]:
        """
        Get the current map grid.

        Returns:
            List of strings representing map rows
        """
        pass

    @abstractmethod
    def get_map_dimensions(self) -> Tuple[int, int]:
        """
        Get map dimensions.

        Returns:
            Tuple of (width, height) in cells
        """
        pass
