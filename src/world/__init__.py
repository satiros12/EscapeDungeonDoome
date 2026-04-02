"""
World - Central entity container and system coordinator
"""

from world.world import World
from world.factories import WorldFactory
from world.query import EntityQuery, QueryBuilder

__all__ = ["World", "WorldFactory", "EntityQuery", "QueryBuilder"]
