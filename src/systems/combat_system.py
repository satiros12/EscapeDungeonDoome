"""
Combat System - handles combat mechanics and damage
"""

import math
from typing import Optional, List, TYPE_CHECKING

from systems.base import SystemBase, GameEvent
from engine.game_state import GameState, Enemy, Corpse, HitEffect
from engine.event_system import EventSystem, EventType, get_event_system
from entities.components import HealthComponent, CombatComponent, PositionComponent

if TYPE_CHECKING:
    from world.world import World
    from entities.enemy import EnemyEntity
    from entities.player import PlayerEntity


class CombatSystem(SystemBase):
    """Handles combat mechanics with event-driven architecture."""

    def __init__(self, state: GameState, event_system: Optional[EventSystem] = None):
        """
        Initialize the combat system.

        Args:
            state: The game state instance
            event_system: Optional event system (uses global if None)
        """
        super().__init__()
        self.state = state
        self.event_system = event_system or get_event_system()
        self.world: Optional["World"] = None

        # Combat configuration
        self.attack_range = 1.5
        self.attack_damage = 10
        self.attack_cooldown = 0.5

        # Event listener references for cleanup
        self._entity_created_listener = None
        self._entity_destroyed_listener = None
        self._enemy_hit_listener = None
        self._player_damage_listener = None

        # Cached entities for ECS mode
        self._player_entity: Optional["PlayerEntity"] = None
        self._enemy_entities: List["EnemyEntity"] = []

        # Subscribe to events
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant game events."""
        # ENTITY_CREATED - track combat entities
        self._entity_created_listener = self.event_system.subscribe(
            EventType.ENTITY_CREATED, self._on_entity_created
        )

        # ENTITY_DESTROYED - remove destroyed entities from tracking
        self._entity_destroyed_listener = self.event_system.subscribe(
            EventType.ENTITY_DESTROYED, self._on_entity_destroyed
        )

        # ENEMY_HIT - handle enemy hit events
        self._enemy_hit_listener = self.event_system.subscribe(
            EventType.ENEMY_HIT, self._on_enemy_hit
        )

        # PLAYER_DAMAGE - handle player damage events
        self._player_damage_listener = self.event_system.subscribe(
            EventType.PLAYER_DAMAGE, self._on_player_damage
        )

    def _on_entity_created(self, event: GameEvent) -> None:
        """
        Handle entity created event.

        Args:
            event: The game event containing entity data
        """
        entity = event.data.get("entity")
        entity_id = event.data.get("entity_id")

        if entity is None:
            return

        # Check if it's a player entity
        if entity_id == "player" or hasattr(entity, "id") and entity.id == "player":
            self._player_entity = entity

        # Check if it's an enemy entity
        elif hasattr(entity, "get_component"):
            if entity.get_component("AIComponent") is not None:
                self._enemy_entities.append(entity)

    def _on_entity_destroyed(self, event: GameEvent) -> None:
        """
        Handle entity destroyed event.

        Args:
            event: The game event containing entity data
        """
        entity_id = event.data.get("entity_id")

        # Remove from player reference
        if self._player_entity and self._player_entity.id == entity_id:
            self._player_entity = None

        # Remove from enemy list
        self._enemy_entities = [e for e in self._enemy_entities if e.id != entity_id]

    def _on_enemy_hit(self, event: GameEvent) -> None:
        """
        Handle enemy hit event.

        Args:
            event: The game event containing hit data
        """
        entity_id = event.data.get("entity_id")
        damage = event.data.get("damage", 0)

        # Find the enemy entity
        for enemy in self._enemy_entities:
            if enemy.id == entity_id:
                # Apply damage through health component
                health = enemy.get_component("HealthComponent")
                if health:
                    died = health.take_damage(damage)
                    if died:
                        # Emit enemy death event
                        self.event_system.emit(
                            EventType.ENEMY_DEATH,
                            {"entity_id": entity_id, "x": enemy.x, "y": enemy.y},
                        )
                break

    def _on_player_damage(self, event: GameEvent) -> None:
        """
        Handle player damage event.

        Args:
            event: The game event containing damage data
        """
        damage = event.data.get("damage", 0)

        # Apply damage to player
        if self._player_entity:
            health = self._player_entity.get_component("HealthComponent")
            if health:
                died = health.take_damage(damage)
                if died:
                    self.event_system.emit(
                        EventType.PLAYER_DEATH, {"entity_id": self._player_entity.id}
                    )

    def set_world(self, world: "World") -> None:
        """
        Set the world instance for entity queries.

        Args:
            world: The world instance to use
        """
        self.world = world
        self._refresh_entity_cache()

    def _refresh_entity_cache(self) -> None:
        """Refresh cached entities from the world."""
        if not self.world:
            return

        # Query player entity
        player = self.world.get_entity("player")
        if player:
            self._player_entity = player

        # Query enemy entities
        from entities.enemy import EnemyEntity

        self._enemy_entities = self.world.get_entities_with(EnemyEntity)

    def update(self, dt: float) -> None:
        """Update combat state."""
        if self.state.game_state != "playing":
            return

        # Process any pending events
        self.event_system.process_events()

        # Update based on mode (ECS or legacy)
        if self.world:
            self._update_ecs(dt)
        else:
            self._update_legacy(dt)

    def _update_ecs(self, dt: float) -> None:
        """Update combat using ECS entities."""
        # Update dying enemies
        self._update_dying_enemies_ecs(dt)

        # Update hit effects (still uses legacy for now)
        self._update_hit_effects(dt)

        # Check win condition
        self._check_win_condition()

    def _update_legacy(self, dt: float) -> None:
        """Update combat using legacy GameState."""
        self._update_dying_enemies(dt)
        self._update_hit_effects(dt)
        self._check_win_condition()

    def player_attack(self) -> None:
        """Player attacks nearby enemies."""
        # Get player and enemies based on mode
        if self.world:
            self._player_attack_ecs()
        else:
            self._player_attack_legacy()

    def _player_attack_ecs(self) -> None:
        """Player attack using ECS entities."""
        if not self._player_entity:
            return

        combat = self._player_entity.get_component("CombatComponent")
        if combat and combat.attack_cooldown > 0:
            return

        # Reset cooldown
        if combat:
            combat.attack_cooldown = self.attack_cooldown

        player_pos = self._player_entity.get_component(PositionComponent)
        if not player_pos:
            return

        # Find and attack enemies in range
        for enemy in self._enemy_entities:
            ai = enemy.get_component("AIComponent")
            if ai and ai.state in ("dying", "dead"):
                continue

            enemy_pos = enemy.get_component(PositionComponent)
            if not enemy_pos:
                continue

            dx = enemy_pos.x - player_pos.x
            dy = enemy_pos.y - player_pos.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < self.attack_range:
                # Apply damage
                health = enemy.get_component(HealthComponent)
                if health:
                    health.take_damage(self.attack_damage)

                    # Emit enemy hit event
                    self.event_system.emit(
                        EventType.ENEMY_HIT,
                        {
                            "entity_id": enemy.id,
                            "damage": self.attack_damage,
                            "x": enemy_pos.x,
                            "y": enemy_pos.y,
                        },
                    )

                    # Check for death
                    if health.is_dead:
                        ai.state = "dying"
                        ai.dying_progress = 0
                        self.event_system.emit(
                            EventType.ENEMY_DEATH,
                            {"entity_id": enemy.id, "x": enemy_pos.x, "y": enemy_pos.y},
                        )

    def _player_attack_legacy(self) -> None:
        """Player attack using legacy GameState."""
        if self.state.player.attack_cooldown > 0:
            return

        self.state.player.attack_cooldown = self.attack_cooldown
        player = self.state.player

        for enemy in self.state.enemies:
            if enemy.state in ("dying", "dead"):
                continue

            dx = enemy.x - player.x
            dy = enemy.y - player.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < self.attack_range:
                enemy.health -= self.attack_damage
                self.state.hit_effects.append(HitEffect(x=enemy.x, y=enemy.y))

                # Emit enemy hit event
                self.event_system.emit(
                    EventType.ENEMY_HIT,
                    {
                        "entity_id": f"enemy_{enemy.x}_{enemy.y}",
                        "damage": self.attack_damage,
                        "x": enemy.x,
                        "y": enemy.y,
                    },
                )

                if enemy.health <= 0:
                    enemy.state = "dying"
                    enemy.dying_progress = 0
                    self.event_system.emit(
                        EventType.ENEMY_DEATH,
                        {
                            "entity_id": f"enemy_{enemy.x}_{enemy.y}",
                            "x": enemy.x,
                            "y": enemy.y,
                        },
                    )

    def _update_dying_enemies(self, dt: float) -> None:
        """Update dying enemy animations (legacy)."""
        for enemy in self.state.enemies:
            if enemy.state == "dying":
                enemy.dying_progress += dt
                if enemy.dying_progress >= 1.0:
                    enemy.state = "dead"
                    self.state.corpses.append(Corpse(x=enemy.x, y=enemy.y))
                    self.state.kills += 1

    def _update_dying_enemies_ecs(self, dt: float) -> None:
        """Update dying enemy animations (ECS)."""
        for enemy in self._enemy_entities:
            ai = enemy.get_component("AIComponent")
            if ai and ai.state == "dying":
                ai.dying_progress += dt
                if ai.dying_progress >= 1.0:
                    ai.state = "dead"
                    # Add corpse to game state
                    self.state.corpses.append(Corpse(x=enemy.x, y=enemy.y))
                    self.state.kills += 1

    def _update_hit_effects(self, dt: float) -> None:
        """Update hit effect timers."""
        for effect in self.state.hit_effects[:]:
            effect.timer -= dt
            if effect.timer <= 0:
                self.state.hit_effects.remove(effect)

    def _check_win_condition(self) -> None:
        """Check if player has won the game."""
        if self.world:
            alive_enemies = [
                e
                for e in self._enemy_entities
                if e.get_component("AIComponent")
                and e.get_component("AIComponent").state != "dead"
            ]
        else:
            alive_enemies = [e for e in self.state.enemies if e.state != "dead"]

        if len(alive_enemies) == 0 and self.state.game_state == "playing":
            self.state.game_state = "victory"
            self.event_system.emit(EventType.GAME_WIN, {})

    def emit_attack_event(self, attacker_id: str, target_id: str, damage: int) -> None:
        """
        Emit a custom attack event.

        Args:
            attacker_id: ID of the attacking entity
            target_id: ID of the target entity
            damage: Amount of damage dealt
        """
        self.event_system.emit(
            EventType.ENEMY_HIT,
            {
                "entity_id": target_id,
                "damage": damage,
                "attacker_id": attacker_id,
            },
        )

    def emit_damage_event(
        self, target_id: str, damage: int, source: str = "enemy"
    ) -> None:
        """
        Emit a custom damage event.

        Args:
            target_id: ID of the entity taking damage
            damage: Amount of damage
            source: Source of the damage
        """
        if target_id == "player":
            self.event_system.emit(
                EventType.PLAYER_DAMAGE, {"damage": damage, "source": source}
            )
        else:
            self.event_system.emit(
                EventType.ENEMY_HIT,
                {"entity_id": target_id, "damage": damage, "source": source},
            )

    def cleanup(self) -> None:
        """Clean up event listeners."""
        if self._entity_created_listener:
            self.event_system.unsubscribe(self._entity_created_listener)
        if self._entity_destroyed_listener:
            self.event_system.unsubscribe(self._entity_destroyed_listener)
        if self._enemy_hit_listener:
            self.event_system.unsubscribe(self._enemy_hit_listener)
        if self._player_damage_listener:
            self.event_system.unsubscribe(self._player_damage_listener)

        self._entity_created_listener = None
        self._entity_destroyed_listener = None
        self._enemy_hit_listener = None
        self._player_damage_listener = None
