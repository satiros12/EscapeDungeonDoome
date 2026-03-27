"""Enemy AI system"""

import math
import random
from systems.base import SystemBase
from game_state import GameState, GameConfig
from physics import Physics


class EnemyAISystem(SystemBase):
    """Handles enemy AI behaviors"""

    def __init__(self, state: GameState, physics: Physics):
        super().__init__()
        self.state = state
        self.physics = physics

    def update(self, dt: float) -> None:
        if self.state.game_state != "playing":
            return

        player = self.state.player
        alive_enemies = [
            e for e in self.state.enemies if e.state not in ("dead", "dying")
        ]

        for enemy in alive_enemies:
            self._update_enemy(enemy, player, dt)

    def _update_enemy(self, enemy, player, dt: float) -> None:
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.sqrt(dx * dx + dy * dy)
        angle_to_player = math.atan2(dy, dx)

        can_see = (
            dist < GameConfig.DETECTION_RANGE
            and self.physics.has_line_of_sight(enemy.x, enemy.y, player.x, player.y)
        )

        if enemy.state == "patrol":
            self._update_patrol(enemy, dt, can_see, dist)

        elif enemy.state == "chase":
            self._update_chase(enemy, player, dist, angle_to_player, dt, can_see)

        elif enemy.state == "attack":
            self._update_attack(enemy, player, dist)

    def _update_patrol(self, enemy, dt: float, can_see: bool, dist: float) -> None:
        enemy.x += math.cos(enemy.patrol_dir) * GameConfig.PATROL_SPEED * dt
        enemy.y += math.sin(enemy.patrol_dir) * GameConfig.PATROL_SPEED * dt

        if self.physics.is_wall(
            enemy.x + math.cos(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
            enemy.y + math.sin(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
        ):
            enemy.patrol_dir += math.pi / 2 + random.random() * math.pi

        if can_see and dist < GameConfig.DETECTION_RANGE:
            enemy.state = "chase"

    def _update_chase(self, enemy, player, dist: float, angle_to_player: float, dt: float, can_see: bool) -> None:
        if dist > GameConfig.ENEMY_ATTACK_RANGE:
            enemy.angle = angle_to_player
            new_x = enemy.x + math.cos(enemy.angle) * GameConfig.ENEMY_SPEED * dt
            new_y = enemy.y + math.sin(enemy.angle) * GameConfig.ENEMY_SPEED * dt
            if not self.physics.is_wall(new_x, enemy.y):
                enemy.x = new_x
            if not self.physics.is_wall(enemy.x, new_y):
                enemy.y = new_y
        else:
            enemy.state = "attack"

        if not can_see and dist > GameConfig.LOST_PLAYER_DISTANCE:
            enemy.state = "patrol"

    def _update_attack(self, enemy, player, dist: float) -> None:
        if dist > GameConfig.ENEMY_ATTACK_RANGE + GameConfig.COLLISION_MARGIN:
            enemy.state = "chase"
        elif enemy.attack_cooldown <= 0 and dist <= GameConfig.ENEMY_ATTACK_RANGE:
            enemy.attack_cooldown = GameConfig.ENEMY_ATTACK_COOLDOWN
            if not getattr(player, "god_mode", False):
                player.health -= GameConfig.ENEMY_DAMAGE
            if player.health <= 0:
                self.state.game_state = "defeat"

        if enemy.attack_cooldown > 0:
            enemy.attack_cooldown -= 0.016

    def normalize_angle(self, angle: float) -> float:
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
