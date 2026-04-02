"""
World - Central entity container and system coordinator
"""

from world.world import World
from world.factories import WorldFactory
from world.query import EntityQuery, QueryBuilder
from world.entity_factory import (
    create_player_entity,
    create_enemy_entity,
    create_player_from_state,
    create_enemies_from_state,
)
from world.serialization import (
    serialize_world,
    deserialize_world,
    serialize_entity,
    deserialize_entity,
    serialize_component,
    deserialize_component,
)

__all__ = [
    "World",
    "WorldFactory",
    "EntityQuery",
    "QueryBuilder",
    "create_player_entity",
    "create_enemy_entity",
    "create_player_from_state",
    "create_enemies_from_state",
    "serialize_world",
    "deserialize_world",
    "serialize_entity",
    "deserialize_entity",
    "serialize_component",
    "deserialize_component",
]
