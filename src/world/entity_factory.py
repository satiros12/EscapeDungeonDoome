"""
Entity Factory - Converts GameState data to Entity objects

This module provides factory functions to create Entity objects from
GameState Player and Enemy dataclasses.
"""

from typing import List
from engine.game_state import Player, Enemy, GameState
from entities.player import PlayerEntity
from entities.enemy import EnemyEntity
from entities.base import Entity
from entities.components import CollidableComponent


def create_player_entity(player_data: Player) -> PlayerEntity:
    """
    Create a PlayerEntity from Player dataclass data.

    Args:
        player_data: Player dataclass instance from GameState

    Returns:
        PlayerEntity configured with data from player_data
    """
    entity = PlayerEntity(entity_id="player")

    # Update position component
    position = entity.get_component("PositionComponent")
    if position:
        position.x = player_data.x
        position.y = player_data.y
        position.angle = player_data.angle

    # Update health component
    health = entity.get_component("HealthComponent")
    if health:
        health.health = player_data.health
        health.max_health = 100
        health.is_dead = player_data.health <= 0

    # Update combat component
    combat = entity.get_component("CombatComponent")
    if combat:
        combat.attack_cooldown = player_data.attack_cooldown

    # Add collidable component
    entity.add_component(CollidableComponent(collision_radius=0.3))

    # Set additional properties
    entity.god_mode = player_data.god_mode
    entity.speed_multiplier = player_data.speed_multiplier
    entity.current_weapon = player_data.current_weapon
    entity.ammo = player_data.ammo.copy() if player_data.ammo else {}
    entity.armor = player_data.armor
    entity.armor_type = player_data.armor_type

    # Add tags
    entity.add_tag("player")
    if player_data.health > 0:
        entity.add_tag("alive")
    else:
        entity.add_tag("dead")

    return entity


def create_enemy_entity(enemy_data: Enemy, entity_id: str = None) -> EnemyEntity:
    """
    Create an EnemyEntity from Enemy dataclass data.

    Args:
        enemy_data: Enemy dataclass instance from GameState
        entity_id: Optional unique identifier for the entity

    Returns:
        EnemyEntity configured with data from enemy_data
    """
    if entity_id is None:
        entity_id = f"enemy_{enemy_data.x}_{enemy_data.y}"

    entity = EnemyEntity(
        entity_id=entity_id,
        enemy_type=enemy_data.enemy_type,
        x=enemy_data.x,
        y=enemy_data.y,
    )

    # Update position component
    position = entity.get_component("PositionComponent")
    if position:
        position.angle = enemy_data.angle

    # Update health component
    health = entity.get_component("HealthComponent")
    if health:
        health.health = enemy_data.health
        health.is_dead = enemy_data.health <= 0

    # Update AI component
    ai = entity.get_component("AIComponent")
    if ai:
        ai.state = enemy_data.state
        ai.patrol_dir = enemy_data.patrol_dir
        ai.attack_cooldown = enemy_data.attack_cooldown
        ai.dying_progress = enemy_data.dying_progress

    # Update combat component
    combat = entity.get_component("CombatComponent")
    if combat:
        combat.attack_cooldown = enemy_data.attack_cooldown

    # Add collidable component
    entity.add_component(CollidableComponent(collision_radius=0.3))

    # Set additional properties
    entity.weapon = enemy_data.weapon
    entity.armor = enemy_data.armor
    entity.armor_type = enemy_data.armor_type

    # Add tags
    entity.add_tag("enemy")
    if enemy_data.health > 0:
        entity.add_tag("alive")
    else:
        entity.add_tag("dead")

    return entity


def create_player_from_state(state: GameState) -> PlayerEntity:
    """
    Create a PlayerEntity from GameState.

    Args:
        state: GameState instance containing player data

    Returns:
        PlayerEntity configured with data from state.player
    """
    return create_player_entity(state.player)


def create_enemies_from_state(state: GameState) -> List[EnemyEntity]:
    """
    Create a list of EnemyEntity objects from GameState.

    Args:
        state: GameState instance containing enemies data

    Returns:
        List of EnemyEntity objects configured with data from state.enemies
    """
    entities = []
    for idx, enemy_data in enumerate(state.enemies):
        entity_id = f"enemy_{idx}"
        entity = create_enemy_entity(enemy_data, entity_id)
        entities.append(entity)
    return entities
