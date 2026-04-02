"""
Enemy AI System - handles enemy behaviors and AI
"""

import math
import random
from typing import Optional, List
from systems.base import SystemBase
from engine.game_state import GameState, Enemy
from engine.event_system import (
    EventSystem,
    EventType,
    GameEvent as EngineGameEvent,
    get_event_system,
)
from entities.base import Entity
from entities.components import AIComponent, PositionComponent, HealthComponent


class EnemyAISystem(SystemBase):
    """
    Handles enemy AI behaviors.

    Supports both legacy GameState-based enemies and new World entity-based enemies.
    Uses EventSystem to detect enemy entity creation/destruction and component changes.
    """

    def __init__(
        self,
        state: GameState,
        physics: "Physics",
        event_system: Optional[EventSystem] = None,
    ):
        """
        Initialize the EnemyAISystem.

        Args:
            state: Legacy GameState instance
            physics: Physics instance for collision detection
            event_system: Optional EventSystem (uses global if None)
        """
        super().__init__()
        self.state = state
        self.physics = physics
        self.event_system = event_system or get_event_system()

        # World-based enemy entities (new architecture)
        self._world: Optional["World"] = None
        self._enemy_entities: List[Entity] = []

        # Event listeners for cleanup
        self._listeners: List["EventListener"] = []

        # AI configuration
        self.detection_range = 10.0
        self.attack_range = 1.0
        self.enemy_speed = 2.5
        self.patrol_speed = 1.0
        self.lost_player_distance = 12.0

        # Subscribe to events
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events from the EventSystem."""
        # ENTITY_CREATED - detect when enemy entities are created
        self._listeners.append(
            self.event_system.subscribe(
                EventType.ENTITY_CREATED, self._on_entity_created
            )
        )

        # ENTITY_DESTROYED - detect when enemy entities are destroyed
        self._listeners.append(
            self.event_system.subscribe(
                EventType.ENTITY_DESTROYED, self._on_entity_destroyed
            )
        )

        # COMPONENT_ADDED - detect when components are added to enemies
        self._listeners.append(
            self.event_system.subscribe(
                EventType.COMPONENT_ADDED, self._on_component_added
            )
        )

    def _on_entity_created(self, event: EngineGameEvent) -> None:
        """
        Handle ENTITY_CREATED event.

        Checks if the created entity is an enemy entity (has AIComponent
        or is tagged as 'enemy').

        Args:
            event: The game event
        """
        entity_id = event.data.get("entity_id")
        entity = event.data.get("entity")

        if entity is None:
            return

        # Check if this is an enemy entity
        is_enemy = False

        # Check by tag
        if entity.has_tag("enemy"):
            is_enemy = True

        # Check by component type
        if entity.has_component("AIComponent"):
            is_enemy = True

        if is_enemy and entity not in self._enemy_entities:
            self._enemy_entities.append(entity)

    def _on_entity_destroyed(self, event: EngineGameEvent) -> None:
        """
        Handle ENTITY_DESTROYED event.

        Removes the enemy entity reference if the destroyed entity was an enemy.

        Args:
            event: The game event
        """
        entity_id = event.data.get("entity_id")

        # Find and remove the entity from our list
        for entity in self._enemy_entities:
            if entity.id == entity_id:
                self._enemy_entities.remove(entity)
                break

    def _on_component_added(self, event: EngineGameEvent) -> None:
        """
        Handle COMPONENT_ADDED event.

        Detects when components are added to enemy entities.

        Args:
            event: The game event
        """
        entity_id = event.data.get("entity_id")
        component_name = event.data.get("component_name")

        # Check if AIComponent was added to an existing entity
        if component_name == "AIComponent":
            entity = self._world.get_entity(entity_id) if self._world else None
            if entity and entity not in self._enemy_entities:
                self._enemy_entities.append(entity)

    def set_world(self, world: "World") -> None:
        """
        Set the World instance for entity queries.

        Allows the system to query enemy entities from the new World architecture.

        Args:
            world: World instance to use for entity queries
        """
        self._world = world

        # Find existing enemy entities in the world
        self._find_enemy_entities()

    def _find_enemy_entities(self) -> None:
        """Find enemy entities in the World if available."""
        if self._world is None:
            return

        # Look for entities with AIComponent
        enemy_entities = self._world.get_entities_with(AIComponent)

        # Filter to only include active (non-dead) enemies
        self._enemy_entities = []
        for entity in enemy_entities:
            ai = entity.get_component("AIComponent")
            if ai and ai.state not in ("dead", "dying"):
                self._enemy_entities.append(entity)

    def update(self, dt: float) -> None:
        """Update all enemies."""
        if self.state.game_state != "playing":
            return

        # Try World-based enemies first, then fall back to legacy GameState
        if self._world is not None and self._enemy_entities:
            self._update_world_enemies(dt)
        else:
            # Fall back to legacy GameState enemies
            self._update_legacy_enemies(dt)

    def _update_world_enemies(self, dt: float) -> None:
        """Update enemies using World entity components."""
        # Get player entity
        player_entity = None
        if self._world:
            player_entities = self._world.get_entities_by_tag("player")
            if player_entities:
                player_entity = player_entities[0]

        if player_entity is None:
            # Fall back to legacy player
            player_entity = self.state.player

        # Update alive enemies
        alive_enemies = [
            e
            for e in self._enemy_entities
            if self._get_enemy_state(e) not in ("dead", "dying")
        ]

        for enemy in alive_enemies:
            self._update_world_enemy(enemy, player_entity, dt)

        # Update dying enemies
        for enemy in self._enemy_entities:
            if self._get_enemy_state(enemy) == "dying":
                self._update_dying_enemy(enemy, dt)

    def _update_world_enemy(self, enemy: Entity, player, dt: float) -> None:
        """Update a single enemy entity based on AI state."""
        position = enemy.get_component("PositionComponent")
        ai = enemy.get_component("AIComponent")

        if position is None or ai is None:
            return

        dx = player.x - position.x
        dy = player.y - position.y
        dist = math.sqrt(dx * dx + dy * dy)
        angle_to_player = math.atan2(dy, dx)

        can_see = dist < self.detection_range and self.physics.has_line_of_sight(
            position.x, position.y, player.x, player.y
        )

        enemy_state = ai.state

        if enemy_state == "patrol":
            self._update_world_patrol(enemy, dt, can_see, dist)
        elif enemy_state == "chase":
            self._update_world_chase(enemy, player, dist, angle_to_player, dt, can_see)
        elif enemy_state == "attack":
            self._update_world_attack(enemy, player, dist, dt)

    def _update_world_patrol(
        self, enemy: Entity, dt: float, can_see: bool, dist: float
    ) -> None:
        """Update enemy in patrol state using World components."""
        position = enemy.get_component("PositionComponent")
        ai = enemy.get_component("AIComponent")

        if position is None or ai is None:
            return

        # Move in patrol direction
        position.x += math.cos(ai.patrol_dir) * self.patrol_speed * dt
        position.y += math.sin(ai.patrol_dir) * self.patrol_speed * dt

        # Check for wall collision and change direction
        if self.physics.is_wall(
            position.x + math.cos(ai.patrol_dir) * 0.5,
            position.y + math.sin(ai.patrol_dir) * 0.5,
        ):
            ai.patrol_dir += math.pi / 2 + random.random() * math.pi

        # Switch to chase if player is visible
        if can_see and dist < self.detection_range:
            ai.state = "chase"

    def _update_world_chase(
        self,
        enemy: Entity,
        player,
        dist: float,
        angle_to_player: float,
        dt: float,
        can_see: bool,
    ) -> None:
        """Update enemy in chase state using World components."""
        position = enemy.get_component("PositionComponent")
        ai = enemy.get_component("AIComponent")

        if position is None or ai is None:
            return

        # Move toward player
        if dist > self.attack_range:
            position.angle = angle_to_player
            new_x = position.x + math.cos(position.angle) * self.enemy_speed * dt
            new_y = position.y + math.sin(position.angle) * self.enemy_speed * dt

            if not self.physics.is_wall(new_x, position.y):
                position.x = new_x
            if not self.physics.is_wall(position.x, new_y):
                position.y = new_y
        else:
            ai.state = "attack"

        # Lost player - return to patrol
        if not can_see and dist > self.lost_player_distance:
            ai.state = "patrol"
            ai.patrol_dir = random.random() * 2 * math.pi

    def _update_world_attack(
        self, enemy: Entity, player, dist: float, dt: float
    ) -> None:
        """Update enemy in attack state using World components."""
        position = enemy.get_component("PositionComponent")
        ai = enemy.get_component("AIComponent")
        health = enemy.get_component("HealthComponent")

        if position is None or ai is None:
            return

        # Check if player is in range
        if dist > self.attack_range + 0.3:
            ai.state = "chase"
        elif ai.attack_cooldown <= 0 and dist <= self.attack_range:
            # Attack player
            ai.attack_cooldown = 1.0

            # Check if player has god_mode
            god_mode = getattr(player, "god_mode", False)
            if not god_mode:
                # Damage the player
                if hasattr(player, "health"):
                    player.health -= 10

                if player.health <= 0:
                    self.state.game_state = "defeat"

        # Update attack cooldown
        if ai.attack_cooldown > 0:
            ai.attack_cooldown -= dt

    def _update_dying_enemy(self, enemy: Entity, dt: float) -> None:
        """Update a dying enemy entity."""
        ai = enemy.get_component("AIComponent")

        if ai is None:
            return

        ai.dying_progress += dt
        if ai.dying_progress >= 1.0:
            ai.state = "dead"
            from engine.game_state import Corpse

            position = enemy.get_component("PositionComponent")
            x = position.x if position else 0.0
            y = position.y if position else 0.0

            self.state.corpses.append(Corpse(x=x, y=y))
            self.state.kills += 1

            # Remove from active enemies list
            if enemy in self._enemy_entities:
                self._enemy_entities.remove(enemy)

    def _get_enemy_state(self, enemy: Entity) -> str:
        """Get the current state of an enemy entity."""
        ai = enemy.get_component("AIComponent")
        return ai.state if ai else "patrol"

    def _update_legacy_enemies(self, dt: float) -> None:
        """Update enemies using legacy GameState."""
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

    def shutdown(self) -> None:
        """Clean up event listeners and resources."""
        # Unsubscribe from all events
        for listener in self._listeners:
            self.event_system.unsubscribe(listener)
        self._listeners.clear()

        # Clear references
        self._enemy_entities.clear()
        self._world = None
