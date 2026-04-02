"""
Game Engine - Core game engine coordinating all systems
"""

import math
from typing import List, Optional, Dict, Any

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    PLAYER_SPEED,
    PLAYER_ROTATION_SPEED,
    PLAYER_START_HEALTH,
    ENEMY_COUNT,
    ENEMY_HEALTH,
    ENEMY_SPEED,
    ATTACK_DAMAGE,
    ATTACK_RANGE,
    ATTACK_COOLDOWN,
    FOV,
    RAY_COUNT,
    MAX_DEPTH,
)
from engine.game_state import GameState, Player, Enemy, EnemyType
from engine.event_system import EventSystem, EventType
from physics import Physics
from physics.physics import IPhysics
from world.world import World
from world.factories import WorldFactory


class GameEngine:
    """Core game engine that coordinates all game systems."""

    def __init__(self, screen):
        self.screen = screen
        self.state = GameState()
        self.event_system = EventSystem()
        # Initialize physics with map grid after map is loaded
        self.physics: IPhysics = Physics()
        # Use World with WorldFactory instead of SystemRegistry
        self.world: World = WorldFactory.create_game_world(
            state=self.state,
            physics=self.physics,
            event_system=self.event_system,
        )
        # Keep backward compatibility - expose systems for direct access
        self._systems = {s.__class__.__name__: s for s in self.world._systems}
        self.dt = 0.0
        self.running = True
        self.paused = False

        # Raycasting data
        self.ray_angles: List[float] = []
        self.wall_distances: List[float] = []
        self._init_raycasting()

    def _init_raycasting(self) -> None:
        """Initialize raycasting angles."""
        fov_rad = math.radians(FOV)
        self.ray_angles = [
            -fov_rad / 2 + (fov_rad * i / RAY_COUNT) for i in range(RAY_COUNT)
        ]
        self.wall_distances = [MAX_DEPTH] * RAY_COUNT

    def start_game(self) -> None:
        """Start a new game."""
        self.state.game_state = "playing"
        self.state.parse_map()
        # Pass map to physics after loading
        grid = self.state.map_manager.get_current_map().get("grid", [])
        self.physics.set_map(grid)
        self.event_system.emit(EventType.GAME_START, {})

    def pause_game(self) -> None:
        """Pause the game."""
        if self.state.game_state == "playing":
            self.state.game_state = "pause"
            self.paused = True

    def resume_game(self) -> None:
        """Resume the game."""
        if self.state.game_state == "pause":
            self.state.game_state = "playing"
            self.paused = False

    def update(self, dt: float) -> None:
        """Update game state for one frame."""
        self.dt = dt

        if self.state.game_state == "playing":
            # Use world for game logic
            self.world.update(dt)
            # Raycasting for renderer (still needed)
            self._cast_rays()

    def _cast_rays(self) -> None:
        """Cast rays for raycasting rendering."""
        player = self.state.player
        grid = self.state.map_manager.get_current_map().get("grid", [])

        for i, angle in enumerate(self.ray_angles):
            ray_angle = player.angle + angle
            dist = self._cast_single_ray(player.x, player.y, ray_angle, grid)
            self.wall_distances[i] = dist

    def _cast_single_ray(
        self, x: float, y: float, angle: float, grid: List[str]
    ) -> float:
        """Cast a single ray and return distance."""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        if abs(sin_a) < 0.0001:
            sin_a = 0.0001
        if abs(cos_a) < 0.0001:
            cos_a = 0.0001

        dist = 0.0
        step = 0.02

        while dist < MAX_DEPTH:
            dist += step
            test_x = x + cos_a * dist
            test_y = y + sin_a * dist

            if self._is_wall_at(test_x, test_y, grid):
                return dist

        return MAX_DEPTH

    def _is_wall(self, x: float, y: float) -> bool:
        """Check if position is a wall."""
        grid = self.state.map_manager.get_current_map().get("grid", [])
        return self._is_wall_at(x, y, grid)

    def _is_wall_at(self, x: float, y: float, grid: List[str]) -> bool:
        """Check if position is a wall in given grid."""
        if not grid:
            return True

        mx = int(x)
        my = int(y)
        width = len(grid[0]) if grid else 0
        height = len(grid) if grid else 0

        if mx < 0 or mx >= width or my < 0 or my >= height:
            return True

        return grid[my][mx] == "#"

    def get_ray_data(self) -> List[float]:
        """Get wall distances for raycasting."""
        return self.wall_distances.copy()

    def attack(self) -> None:
        """Player performs an attack through combat system."""
        # Access combat system from world for backward compatibility
        combat_system = self._systems.get("CombatSystem")
        if combat_system:
            combat_system.player_attack()

    def get_state(self) -> Dict[str, Any]:
        """Get current game state for serialization."""
        return self.state.to_dict()


class GameConfig:
    """Game configuration values matching shared constants."""

    FOV = math.radians(FOV)
    HALF_FOV = FOV / 2
    NUM_RAYS = RAY_COUNT
    MAX_DEPTH = MAX_DEPTH
    MOVE_SPEED = PLAYER_SPEED
    ROT_SPEED = PLAYER_ROTATION_SPEED
    ATTACK_RANGE = ATTACK_RANGE
    ATTACK_COOLDOWN = ATTACK_COOLDOWN
    ENEMY_SPEED = ENEMY_SPEED
    DETECTION_RANGE = 10.0
    ENEMY_ATTACK_RANGE = 1.0
    ENEMY_ATTACK_COOLDOWN = 1.0
    PLAYER_MAX_HEALTH = PLAYER_START_HEALTH
    ENEMY_MAX_HEALTH = ENEMY_HEALTH
    PLAYER_DAMAGE = ATTACK_DAMAGE
    ENEMY_DAMAGE = 10
    PATROL_SPEED = 1.0
    RAY_STEP = 0.02
    COLLISION_MARGIN = 0.35
    LOST_PLAYER_DISTANCE = 12.0
    DT_MAX = 0.1
