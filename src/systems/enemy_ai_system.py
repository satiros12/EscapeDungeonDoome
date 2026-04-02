"""
Enemy AI System - handles enemy behaviors and AI
"""

import math
import random
from systems.base import SystemBase
from engine.game_state import GameState, Enemy


class EnemyAISystem(SystemBase):
    """Handles enemy AI behaviors."""

    def __init__(self, state: GameState, physics: "Physics"):
        super().__init__()
        self.state = state
        self.physics = physics

        # AI configuration
        self.detection_range = 10.0
        self.attack_range = 1.0
        self.enemy_speed = 2.5
        self.patrol_speed = 1.0
        self.lost_player_distance = 12.0

    def update(self, dt: float) -> None:
        """Update all enemies."""
        if self.state.game_state != "playing":
            return

        player = self.state.player
        alive_enemies = [
            e for e in self.state.enemies if e.state not in ("dead", "dying")
        ]

        for enemy in alive_enemies:
            self._update_enemy(enemy, player, dt)

        # Update dying enemies
        for enemy in self.state.enemies:
            if enemy.state == "dying":
                enemy.dying_progress += dt
                if enemy.dying_progress >= 1.0:
                    enemy.state = "dead"
                    from engine.game_state import Corpse

                    self.state.corpses.append(Corpse(x=enemy.x, y=enemy.y))
                    self.state.kills += 1

    def _update_enemy(self, enemy: Enemy, player, dt: float) -> None:
        """Update a single enemy based on AI state."""
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.sqrt(dx * dx + dy * dy)
        angle_to_player = math.atan2(dy, dx)

        can_see = dist < self.detection_range and self.physics.has_line_of_sight(
            enemy.x, enemy.y, player.x, player.y
        )

        if enemy.state == "patrol":
            self._update_patrol(enemy, dt, can_see, dist)
        elif enemy.state == "chase":
            self._update_chase(enemy, player, dist, angle_to_player, dt, can_see)
        elif enemy.state == "attack":
            self._update_attack(enemy, player, dist, dt)

    def _update_patrol(
        self, enemy: Enemy, dt: float, can_see: bool, dist: float
    ) -> None:
        """Update enemy in patrol state."""
        # Move in patrol direction
        enemy.x += math.cos(enemy.patrol_dir) * self.patrol_speed * dt
        enemy.y += math.sin(enemy.patrol_dir) * self.patrol_speed * dt

        # Check for wall collision and change direction
        if self.physics.is_wall(
            enemy.x + math.cos(enemy.patrol_dir) * 0.5,
            enemy.y + math.sin(enemy.patrol_dir) * 0.5,
        ):
            enemy.patrol_dir += math.pi / 2 + random.random() * math.pi

        # Switch to chase if player is visible
        if can_see and dist < self.detection_range:
            enemy.state = "chase"

    def _update_chase(
        self,
        enemy: Enemy,
        player,
        dist: float,
        angle_to_player: float,
        dt: float,
        can_see: bool,
    ) -> None:
        """Update enemy in chase state."""
        # Move toward player
        if dist > self.attack_range:
            enemy.angle = angle_to_player
            new_x = enemy.x + math.cos(enemy.angle) * self.enemy_speed * dt
            new_y = enemy.y + math.sin(enemy.angle) * self.enemy_speed * dt

            if not self.physics.is_wall(new_x, enemy.y):
                enemy.x = new_x
            if not self.physics.is_wall(enemy.x, new_y):
                enemy.y = new_y
        else:
            enemy.state = "attack"

        # Lost player - return to patrol
        if not can_see and dist > self.lost_player_distance:
            enemy.state = "patrol"
            enemy.patrol_dir = random.random() * 2 * math.pi

    def _update_attack(self, enemy: Enemy, player, dist: float, dt: float) -> None:
        """Update enemy in attack state."""
        # Check if player is in range
        if dist > self.attack_range + 0.3:
            enemy.state = "chase"
        elif enemy.attack_cooldown <= 0 and dist <= self.attack_range:
            # Attack player
            enemy.attack_cooldown = 1.0
            if not player.god_mode:
                player.health -= 10

            if player.health <= 0:
                self.state.game_state = "defeat"

        # Update attack cooldown
        if enemy.attack_cooldown > 0:
            enemy.attack_cooldown -= dt

    def normalize_angle(self, angle: float) -> float:
        """Normalize angle to [-pi, pi] range."""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
