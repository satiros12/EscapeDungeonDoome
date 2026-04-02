"""
Entity Query - Fluent interface for querying entities in the world
"""

from typing import List, Type, Optional, Callable, Any
from dataclasses import dataclass, field

from entities.base import Entity, Component


@dataclass
class QueryCriteria:
    """Stores the criteria for an entity query."""

    required_components: List[str] = field(default_factory=list)
    excluded_components: List[str] = field(default_factory=list)
    required_tags: List[str] = field(default_factory=list)
    excluded_tags: List[str] = field(default_factory=list)
    custom_filters: List[Callable[[Entity], bool]] = field(default_factory=list)


class EntityQuery:
    """
    Fluent interface for querying entities in the world.

    Provides a chainable API to filter entities by components and tags,
    with support for custom filtering logic.

    Example:
        >>> query = EntityQuery(world)
        >>> entities = (query
        ...     .with_component(Position)
        ...     .with_component(Velocity)
        ...     .without_tag("dead")
        ...     .execute())
    """

    def __init__(self, world: "World") -> None:
        """
        Initialize the entity query.

        Args:
            world: The world instance to query entities from
        """
        self._world = world
        self._criteria = QueryCriteria()

    def with_component(self, component_type: Type[Component]) -> "EntityQuery":
        """
        Require entities to have this component type.

        Args:
            component_type: The component type that entities must have

        Returns:
            Self for method chaining
        """
        component_name = component_type.__name__
        if component_name not in self._criteria.required_components:
            self._criteria.required_components.append(component_name)
        return self

    def without_component(self, component_type: Type[Component]) -> "EntityQuery":
        """
        Exclude entities that have this component type.

        Args:
            component_type: The component type that entities must NOT have

        Returns:
            Self for method chaining
        """
        component_name = component_type.__name__
        if component_name not in self._criteria.excluded_components:
            self._criteria.excluded_components.append(component_name)
        return self

    def with_tag(self, tag: str) -> "EntityQuery":
        """
        Require entities to have this tag.

        Args:
            tag: The tag that entities must have

        Returns:
            Self for method chaining
        """
        if tag not in self._criteria.required_tags:
            self._criteria.required_tags.append(tag)
        return self

    def without_tag(self, tag: str) -> "EntityQuery":
        """
        Exclude entities that have this tag.

        Args:
            tag: The tag that entities must NOT have

        Returns:
            Self for method chaining
        """
        if tag not in self._criteria.excluded_tags:
            self._criteria.excluded_tags.append(tag)
        return self

    def filter(self, predicate: Callable[[Entity], bool]) -> "EntityQuery":
        """
        Add a custom filter predicate.

        Args:
            predicate: A function that takes an Entity and returns True
                      if the entity should be included in results

        Returns:
            Self for method chaining
        """
        self._criteria.custom_filters.append(predicate)
        return self

    def execute(self) -> List[Entity]:
        """
        Execute the query and return matching entities.

        Returns:
            List of entities matching all criteria
        """
        results: List[Entity] = []

        for entity in self._world.entities.values():
            if self._matches_criteria(entity):
                results.append(entity)

        return results

    def first(self) -> Optional[Entity]:
        """
        Get the first entity matching the criteria.

        Returns:
            The first matching entity, or None if no matches
        """
        for entity in self._world.entities.values():
            if self._matches_criteria(entity):
                return entity
        return None

    def count(self) -> int:
        """
        Count entities matching the criteria without returning them.

        Returns:
            Number of entities matching the criteria
        """
        count = 0
        for entity in self._world.entities.values():
            if self._matches_criteria(entity):
                count += 1
        return count

    def _matches_criteria(self, entity: Entity) -> bool:
        """
        Check if an entity matches all query criteria.

        Args:
            entity: The entity to check

        Returns:
            True if the entity matches all criteria
        """
        # Check required components
        for component_name in self._criteria.required_components:
            if not entity.has_component(component_name):
                return False

        # Check excluded components
        for component_name in self._criteria.excluded_components:
            if entity.has_component(component_name):
                return False

        # Check required tags
        for tag in self._criteria.required_tags:
            if not entity.has_tag(tag):
                return False

        # Check excluded tags
        for tag in self._criteria.excluded_tags:
            if entity.has_tag(tag):
                return False

        # Check custom filters
        for custom_filter in self._criteria.custom_filters:
            if not custom_filter(entity):
                return False

        return True


class QueryBuilder:
    """
    Provides additional query methods for common patterns.

    Offers convenience methods for frequent query operations
    and supports creating pre-configured query builders.
    """

    def __init__(self, world: "World") -> None:
        """
        Initialize the query builder.

        Args:
            world: The world instance to query entities from
        """
        self._world = world

    def create_query(self) -> EntityQuery:
        """
        Create a new EntityQuery instance.

        Returns:
            A new EntityQuery for building queries
        """
        return EntityQuery(self._world)

    def get_all(self) -> List[Entity]:
        """
        Get all entities in the world.

        Returns:
            List of all entities
        """
        return list(self._world.entities.values())

    def get_by_id(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by its ID.

        Args:
            entity_id: The ID of the entity to retrieve

        Returns:
            The entity if found, None otherwise
        """
        return self._world.get_entity(entity_id)

    def get_with_components(self, *component_types: Type[Component]) -> List[Entity]:
        """
        Get entities that have all specified component types.

        Args:
            component_types: Variable number of component types to filter by

        Returns:
            List of entities matching all component types
        """
        return self._world.get_entities_with(*component_types)

    def get_by_tag(self, tag: str) -> List[Entity]:
        """
        Get all entities with a specific tag.

        Args:
            tag: The tag to filter by

        Returns:
            List of entities with the specified tag
        """
        return self._world.get_entities_by_tag(tag)

    def get_player_entities(self) -> List[Entity]:
        """
        Get all entities tagged as player.

        Returns:
            List of player entities
        """
        return self.create_query().with_tag("player").execute()

    def get_enemy_entities(self) -> List[Entity]:
        """
        Get all entities tagged as enemy.

        Returns:
            List of enemy entities
        """
        return self.create_query().with_tag("enemy").execute()

    def get_alive_entities(self) -> List[Entity]:
        """
        Get all entities that are not tagged as dead.

        Returns:
            List of alive entities
        """
        return self.create_query().without_tag("dead").execute()

    def get_nearby_entities(
        self, position: Any, radius: float, position_component: str = "position"
    ) -> List[Entity]:
        """
        Get entities within a certain radius of a position.

        Args:
            position: The position to check distance from (must have x, y)
            radius: The radius to search within
            position_component: Name of the position component

        Returns:
            List of entities within the radius
        """
        # Import here to avoid circular imports
        from math import sqrt

        def distance_filter(entity: Entity) -> bool:
            pos_comp = entity.get_component(position_component)
            if pos_comp is None:
                return False
            dx = pos_comp.x - position.x
            dy = pos_comp.y - position.y
            return sqrt(dx * dx + dy * dy) <= radius

        return self.create_query().filter(distance_filter).execute()

    def get_entities_with_any_tag(self, tags: List[str]) -> List[Entity]:
        """
        Get entities that have any of the specified tags.

        Args:
            tags: List of tags to match against

        Returns:
            List of entities with at least one of the tags
        """
        results = []
        for entity in self._world.entities.values():
            if any(entity.has_tag(tag) for tag in tags):
                results.append(entity)
        return results

    def get_entities_with_all_tags(self, tags: List[str]) -> List[Entity]:
        """
        Get entities that have all of the specified tags.

        Args:
            tags: List of tags that entities must have

        Returns:
            List of entities with all tags
        """
        return self.create_query().execute()
