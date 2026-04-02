"""
Player System - handles player movement and input
"""

import math
from systems.base import SystemBase
from engine.game_state import GameState


class PlayerSystem(SystemBase):
    """Handles player movement and input processing."""

    def __init__(self, state: GameState, physics: "Physics"):
        super().__init__()
        self.state = state
        self.physics = physics

    def update(self, dt: float) -> None:
        """Update player based on input."""
        if self.state.game_state != "playing":
            return

        player = self.state.player
        keys = self.state.pending_input

        # Update attack cooldown
        if player.attack_cooldown > 0:
            player.attack_cooldown -= dt

        # Get movement speed
        speed_mult = getattr(player, "speed_multiplier", 1.0) or 1.0
        speed_mult = (
            getattr(self.state, "player_speed_multiplier", speed_mult) or speed_mult
        )

        move_x = 0.0
        move_y = 0.0

        # Forward/backward movement
        if keys.get("KeyW", False):
            move_x += math.cos(player.angle) * 3.0 * speed_mult * dt
            move_y += math.sin(player.angle) * 3.0 * speed_mult * dt
        if keys.get("KeyS", False):
            move_x -= math.cos(player.angle) * 3.0 * speed_mult * dt
            move_y -= math.sin(player.angle) * 3.0 * speed_mult * dt

        # Strafe left/right
        if keys.get("KeyA", False):
            move_x += math.cos(player.angle - math.pi / 2) * 3.0 * speed_mult * dt
            move_y += math.sin(player.angle - math.pi / 2) * 3.0 * speed_mult * dt
        if keys.get("KeyD", False):
            move_x += math.cos(player.angle + math.pi / 2) * 3.0 * speed_mult * dt
            move_y += math.sin(player.angle + math.pi / 2) * 3.0 * speed_mult * dt

        # Rotation
        if keys.get("ArrowLeft", False):
            player.angle -= 2.0 * dt
        if keys.get("ArrowRight", False):
            player.angle += 2.0 * dt

        # Apply movement with collision checking
        if not self.physics.is_wall(player.x + move_x, player.y):
            player.x += move_x
        if not self.physics.is_wall(player.x, player.y + move_y):
            player.y += move_y

        # Keep angle in range
        while player.angle > math.pi:
            player.angle -= 2 * math.pi
        while player.angle < -math.pi:
            player.angle += 2 * math.pi
