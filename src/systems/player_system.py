"""
Player System - handles player movement and input
"""

import math
from typing import Optional, List
from systems.base import SystemBase
from engine.game_state import GameState
from engine.event_system import (
    EventSystem,
    EventType,
    GameEvent as EngineGameEvent,
    get_event_system,
)
from physics.physics import Physics
from input import InputManager, InputAction
from entities.base import Entity
from entities.components import PositionComponent, PlayerInputComponent


class PlayerSystem(SystemBase):
    """
    Handles player movement and input processing.

    Supports both legacy GameState-based player and new World entity-based player.
    Uses EventSystem to detect player entity creation/destruction and component changes.
    """

    def __init__(
        self,
        state: GameState,
        physics: Physics,
        input_manager: Optional[InputManager] = None,
        event_system: Optional[EventSystem] = None,
    ):
        """
        Initialize the PlayerSystem.

        Args:
            state: Legacy GameState instance
            physics: Physics instance for collision detection
            input_manager: Optional InputManager for modern input handling
            event_system: Optional EventSystem (uses global if None)
        """
        super().__init__()
        self.state = state
        self.physics = physics
        self.input_manager = input_manager
        self.event_system = event_system or get_event_system()

        # World-based player entity (new architecture)
        self._world: Optional["World"] = None
        self._player_entity: Optional[Entity] = None
        self._player_entity_id: Optional[str] = None

        # Event listeners for cleanup
        self._listeners: List["EventListener"] = []

        # Subscribe to events
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events from the EventSystem."""
        # ENTITY_CREATED - detect when player entity is created
        self._listeners.append(
            self.event_system.subscribe(
                EventType.ENTITY_CREATED, self._on_entity_created
            )
        )

        # ENTITY_DESTROYED - detect when player entity is destroyed
        self._listeners.append(
            self.event_system.subscribe(
                EventType.ENTITY_DESTROYED, self._on_entity_destroyed
            )
        )

        # COMPONENT_ADDED - detect when components are added to player
        self._listeners.append(
            self.event_system.subscribe(
                EventType.COMPONENT_ADDED, self._on_component_added
            )
        )

    def _on_entity_created(self, event: EngineGameEvent) -> None:
        """
        Handle ENTITY_CREATED event.

        Checks if the created entity is a player entity (has PlayerInputComponent
        or is tagged as 'player').

        Args:
            event: The game event
        """
        entity_id = event.data.get("entity_id")
        entity = event.data.get("entity")

        if entity is None:
            return

        # Check if this is a player entity
        is_player = False

        # Check by tag
        if entity.has_tag("player"):
            is_player = True

        # Check by component type
        if entity.has_component("PlayerInputComponent"):
            is_player = True

        if is_player:
            self._player_entity = entity
            self._player_entity_id = entity_id

    def _on_entity_destroyed(self, event: EngineGameEvent) -> None:
        """
        Handle ENTITY_DESTROYED event.

        Clears the player entity reference if the destroyed entity was the player.

        Args:
            event: The game event
        """
        entity_id = event.data.get("entity_id")

        if entity_id == self._player_entity_id:
            self._player_entity = None
            self._player_entity_id = None

    def _on_component_added(self, event: EngineGameEvent) -> None:
        """
        Handle COMPONENT_ADDED event.

        Detects when components are added to the player entity.

        Args:
            event: The game event
        """
        entity_id = event.data.get("entity_id")
        component_name = event.data.get("component_name")

        # Check if component was added to player entity
        if entity_id == self._player_entity_id:
            # Could log or react to specific component additions
            pass

    def set_world(self, world: "World") -> None:
        """
        Set the World instance for entity queries.

        Allows the system to query player entities from the new World architecture.

        Args:
            world: World instance to use for entity queries
        """
        self._world = world

        # Try to find existing player entity in the world
        self._find_player_entity()

    def _find_player_entity(self) -> None:
        """Find player entity in the World if available."""
        if self._world is None:
            return

        # Look for entities with PlayerInputComponent
        player_entities = self._world.get_entities_with(PlayerInputComponent)

        if player_entities:
            self._player_entity = player_entities[0]
            self._player_entity_id = self._player_entity.id
            return

        # Fall back to looking for entities tagged as 'player'
        player_entities = self._world.get_entities_by_tag("player")

        if player_entities:
            self._player_entity = player_entities[0]
            self._player_entity_id = self._player_entity.id

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

        # Try World-based player first, then fall back to legacy GameState
        if self._player_entity is not None and self._world is not None:
            self._update_world_player(dt)
        else:
            # Fall back to legacy GameState player
            self._update_legacy_player(dt)

    def _update_world_player(self, dt: float) -> None:
        """Update player using World entity components."""
        if self._player_entity is None:
            return

        # Get position component
        position = self._player_entity.get_component("PositionComponent")
        if position is None:
            return

        # Get input component
        input_comp = self._player_entity.get_component("PlayerInputComponent")

        # Update attack cooldown if available
        attack_cooldown = getattr(input_comp, "attack_cooldown", 0) if input_comp else 0
        if attack_cooldown > 0:
            attack_cooldown -= dt
            if input_comp:
                input_comp.attack_cooldown = attack_cooldown

        # Get movement speed multiplier
        speed_mult = getattr(position, "speed_multiplier", 1.0) or 1.0
        speed_mult = (
            getattr(self.state, "player_speed_multiplier", speed_mult) or speed_mult
        )

        move_x = 0.0
        move_y = 0.0

        # Get input from InputManager or from PlayerInputComponent
        pressed_actions = set()

        if self.input_manager is not None:
            pressed_actions = self.input_manager.get_pressed_actions()
        elif input_comp is not None and hasattr(input_comp, "keys"):
            # Convert legacy keys to actions
            keys = input_comp.keys
            if keys.get("KeyW", False):
                pressed_actions.add(InputAction.MOVE_FORWARD)
            if keys.get("KeyS", False):
                pressed_actions.add(InputAction.MOVE_BACKWARD)
            if keys.get("KeyA", False):
                pressed_actions.add(InputAction.MOVE_LEFT)
            if keys.get("KeyD", False):
                pressed_actions.add(InputAction.MOVE_RIGHT)
            if keys.get("ArrowLeft", False):
                pressed_actions.add(InputAction.ROTATE_LEFT)
            if keys.get("ArrowRight", False):
                pressed_actions.add(InputAction.ROTATE_RIGHT)

        # Movement based on InputAction
        if InputAction.MOVE_FORWARD in pressed_actions:
            move_x += math.cos(position.angle) * 3.0 * speed_mult * dt
            move_y += math.sin(position.angle) * 3.0 * speed_mult * dt
        if InputAction.MOVE_BACKWARD in pressed_actions:
            move_x -= math.cos(position.angle) * 3.0 * speed_mult * dt
            move_y -= math.sin(position.angle) * 3.0 * speed_mult * dt
        if InputAction.MOVE_LEFT in pressed_actions:
            move_x += math.cos(position.angle - math.pi / 2) * 3.0 * speed_mult * dt
            move_y += math.sin(position.angle - math.pi / 2) * 3.0 * speed_mult * dt
        if InputAction.MOVE_RIGHT in pressed_actions:
            move_x += math.cos(position.angle + math.pi / 2) * 3.0 * speed_mult * dt
            move_y += math.sin(position.angle + math.pi / 2) * 3.0 * speed_mult * dt

        # Rotation based on InputAction
        if InputAction.ROTATE_LEFT in pressed_actions:
            position.angle -= 2.0 * dt
        if InputAction.ROTATE_RIGHT in pressed_actions:
            position.angle += 2.0 * dt

        # Apply movement with collision checking
        if not self.physics.is_wall(position.x + move_x, position.y):
            position.x += move_x
        if not self.physics.is_wall(position.x, position.y + move_y):
            position.y += move_y

        # Keep angle in range
        while position.angle > math.pi:
            position.angle -= 2 * math.pi
        while position.angle < -math.pi:
            position.angle += 2 * math.pi

    def _update_legacy_player(self, dt: float) -> None:
        """Update player using legacy GameState."""
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

    def get_player_entity(self) -> Optional[Entity]:
        """
        Get the current player entity (World-based).

        Returns:
            The player Entity if available, None otherwise
        """
        return self._player_entity

    def has_world_player(self) -> bool:
        """
        Check if a World-based player entity exists.

        Returns:
            True if a World player entity is available
        """
        return self._player_entity is not None

    def shutdown(self) -> None:
        """Clean up event listeners and resources."""
        # Unsubscribe from all events
        for listener in self._listeners:
            self.event_system.unsubscribe(listener)
        self._listeners.clear()

        # Clear references
        self._player_entity = None
        self._player_entity_id = None
        self._world = None
