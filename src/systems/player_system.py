"""
Player System - handles player movement and input
"""

import math
from typing import Optional
from systems.base import SystemBase
from engine.game_state import GameState
from physics.physics import Physics
from input import InputManager, InputAction


class PlayerSystem(SystemBase):
    """Handles player movement and input processing."""

    def __init__(
        self,
        state: GameState,
        physics: Physics,
        input_manager: Optional[InputManager] = None,
    ):
        super().__init__()
        self.state = state
        self.physics = physics
        self.input_manager = input_manager

    def set_input_manager(self, input_manager: InputManager) -> None:
        """
        Set the input manager for this system.

        Args:
            input_manager: InputManager instance
        """
        self.input_manager = input_manager

    def update(self, dt: float) -> None:
        """Update player based on input."""
        if self.state.game_state != "playing":
            return

        player = self.state.player

        # Get input using new InputAction system if available
        if self.input_manager is not None:
            self._update_with_input_manager(dt)
        else:
            # Fall back to legacy pending_input
            keys = self.state.pending_input
            self._update_with_keys(dt, keys)

    def _update_with_input_manager(self, dt: float) -> None:
        """Update player using InputManager and InputAction."""
        if self.input_manager is None:
            return

        player = self.state.player

        # Update attack cooldown
        if player.attack_cooldown > 0:
            player.attack_cooldown -= dt

        # Get pressed actions
        pressed_actions = self.input_manager.get_pressed_actions()

        # Get movement speed multiplier
        speed_mult = getattr(player, "speed_multiplier", 1.0) or 1.0
        speed_mult = (
            getattr(self.state, "player_speed_multiplier", speed_mult) or speed_mult
        )

        move_x = 0.0
        move_y = 0.0

        # Movement based on InputAction
        if InputAction.MOVE_FORWARD in pressed_actions:
            move_x += math.cos(player.angle) * 3.0 * speed_mult * dt
            move_y += math.sin(player.angle) * 3.0 * speed_mult * dt
        if InputAction.MOVE_BACKWARD in pressed_actions:
            move_x -= math.cos(player.angle) * 3.0 * speed_mult * dt
            move_y -= math.sin(player.angle) * 3.0 * speed_mult * dt
        if InputAction.MOVE_LEFT in pressed_actions:
            move_x += math.cos(player.angle - math.pi / 2) * 3.0 * speed_mult * dt
            move_y += math.sin(player.angle - math.pi / 2) * 3.0 * speed_mult * dt
        if InputAction.MOVE_RIGHT in pressed_actions:
            move_x += math.cos(player.angle + math.pi / 2) * 3.0 * speed_mult * dt
            move_y += math.sin(player.angle + math.pi / 2) * 3.0 * speed_mult * dt

        # Rotation based on InputAction
        if InputAction.ROTATE_LEFT in pressed_actions:
            player.angle -= 2.0 * dt
        if InputAction.ROTATE_RIGHT in pressed_actions:
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

    def _update_with_keys(self, dt: float, keys: dict) -> None:
        """Update player using legacy key dictionary."""
        player = self.state.player

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
