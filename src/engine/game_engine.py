"""
Game Engine - Core game engine coordinating all systems
"""

import pygame
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


class GameEngine:
    """Core game engine that coordinates all game systems."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.state = GameState()
        self.event_system = EventSystem()
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
            self._update_player(dt)
            self._update_enemies(dt)
            self._check_combat()
            self._check_win_condition()
            self._cast_rays()

    def _update_player(self, dt: float) -> None:
        """Update player position based on input."""
        player = self.state.player
        keys = self.state.pending_input

        if player.attack_cooldown > 0:
            player.attack_cooldown -= dt

        # Movement
        move_x = 0.0
        move_y = 0.0

        if keys.get("KeyW", False):
            move_x += math.cos(player.angle) * PLAYER_SPEED * dt
            move_y += math.sin(player.angle) * PLAYER_SPEED * dt
        if keys.get("KeyS", False):
            move_x -= math.cos(player.angle) * PLAYER_SPEED * dt
            move_y -= math.sin(player.angle) * PLAYER_SPEED * dt
        if keys.get("KeyA", False):
            move_x += math.cos(player.angle - math.pi / 2) * PLAYER_SPEED * dt
            move_y += math.sin(player.angle - math.pi / 2) * PLAYER_SPEED * dt
        if keys.get("KeyD", False):
            move_x += math.cos(player.angle + math.pi / 2) * PLAYER_SPEED * dt
            move_y += math.sin(player.angle + math.pi / 2) * PLAYER_SPEED * dt

        # Rotation
        if keys.get("ArrowLeft", False):
            player.angle -= PLAYER_ROTATION_SPEED * dt
        if keys.get("ArrowRight", False):
            player.angle += PLAYER_ROTATION_SPEED * dt

        # Apply movement with collision check
        new_x = player.x + move_x
        new_y = player.y + move_y

        if not self._is_wall(new_x, player.y):
            player.x = new_x
        if not self._is_wall(player.x, new_y):
            player.y = new_y

    def _update_enemies(self, dt: float) -> None:
        """Update enemy positions and AI."""
        player = self.state.player
        alive_enemies = [
            e for e in self.state.enemies if e.state not in ("dead", "dying")
        ]

        for enemy in alive_enemies:
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            dist = math.sqrt(dx * dx + dy * dy)

            # Simple chase AI
            if dist < 10:  # Detection range
                enemy.state = "chase"
                angle = math.atan2(dy, dx)
                enemy.angle = angle

                if dist > 1.0:
                    move_x = math.cos(angle) * ENEMY_SPEED * dt
                    move_y = math.sin(angle) * ENEMY_SPEED * dt

                    new_x = enemy.x + move_x
                    new_y = enemy.y + move_y

                    if not self._is_wall(new_x, enemy.y):
                        enemy.x = new_x
                    if not self._is_wall(enemy.x, new_y):
                        enemy.y = new_y

            # Attack
            if enemy.state == "chase" and dist <= 1.0:
                enemy.state = "attack"
                if enemy.attack_cooldown <= 0:
                    enemy.attack_cooldown = 1.0
                    if not player.god_mode:
                        player.health -= 10
                    if player.health <= 0:
                        self.state.game_state = "defeat"
                        self.event_system.emit(EventType.PLAYER_DEATH, {})

            # Update attack cooldown
            if enemy.attack_cooldown > 0:
                enemy.attack_cooldown -= dt

    def _check_combat(self) -> None:
        """Check for combat interactions."""
        player = self.state.player

        if player.attack_cooldown > 0:
            return

        # Check if attack key was pressed
        if self.state.pending_input.get("Space", False):
            player.attack_cooldown = ATTACK_COOLDOWN

            for enemy in self.state.enemies:
                if enemy.state in ("dead", "dying"):
                    continue

                dx = enemy.x - player.x
                dy = enemy.y - player.y
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < ATTACK_RANGE:
                    enemy.health -= ATTACK_DAMAGE
                    self.event_system.emit(EventType.ENEMY_HIT, {"enemy": enemy})

                    if enemy.health <= 0:
                        enemy.state = "dying"
                        enemy.dying_progress = 0
                        self.state.kills += 1
                        self.event_system.emit(EventType.ENEMY_DEATH, {"enemy": enemy})

    def _check_win_condition(self) -> None:
        """Check if player has won."""
        alive_enemies = [
            e for e in self.state.enemies if e.state not in ("dead", "dying")
        ]
        if len(alive_enemies) == 0 and self.state.game_state == "playing":
            self.state.game_state = "victory"
            self.event_system.emit(EventType.GAME_WIN, {})

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
        """Player performs an attack."""
        if "Space" not in self.state.pending_input:
            self.state.pending_input["Space"] = True

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
