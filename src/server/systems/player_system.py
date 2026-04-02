"""Player movement system"""

import math
from systems.base import SystemBase
from game_state import GameState, GameConfig
from physics import Physics


class PlayerMovementSystem(SystemBase):
    """Handles player movement and input processing"""

    def __init__(self, state: GameState, physics: Physics):
        super().__init__()
        self.state = state
        self.physics = physics

    def update(self, dt: float) -> None:
        if self.state.game_state != "playing":
            return

        player = self.state.player
        keys = self.state.pending_input

        speed_mult = getattr(player, "speed_multiplier", 1.0) or 1.0
        speed_mult = (
            getattr(self.state, "player_speed_multiplier", speed_mult) or speed_mult
        )

        move_x = 0.0
        move_y = 0.0

        if keys.get("KeyW", False):
            move_x += math.cos(player.angle) * GameConfig.MOVE_SPEED * speed_mult * dt
            move_y += math.sin(player.angle) * GameConfig.MOVE_SPEED * speed_mult * dt
        if keys.get("KeyS", False):
            move_x -= math.cos(player.angle) * GameConfig.MOVE_SPEED * speed_mult * dt
            move_y -= math.sin(player.angle) * GameConfig.MOVE_SPEED * speed_mult * dt
        if keys.get("KeyA", False):
            move_x += (
                math.cos(player.angle - math.pi / 2)
                * GameConfig.MOVE_SPEED
                * speed_mult
                * dt
            )
            move_y += (
                math.sin(player.angle - math.pi / 2)
                * GameConfig.MOVE_SPEED
                * speed_mult
                * dt
            )
        if keys.get("KeyD", False):
            move_x += (
                math.cos(player.angle + math.pi / 2)
                * GameConfig.MOVE_SPEED
                * speed_mult
                * dt
            )
            move_y += (
                math.sin(player.angle + math.pi / 2)
                * GameConfig.MOVE_SPEED
                * speed_mult
                * dt
            )

        if keys.get("ArrowLeft", False):
            player.angle -= GameConfig.ROT_SPEED * dt
        if keys.get("ArrowRight", False):
            player.angle += GameConfig.ROT_SPEED * dt

        if not self.physics.is_wall(player.x + move_x, player.y):
            player.x += move_x
        if not self.physics.is_wall(player.x, player.y + move_y):
            player.y += move_y

        if player.attack_cooldown > 0:
            player.attack_cooldown -= dt
