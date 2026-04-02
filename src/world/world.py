"""
World - Manages all entities, components, and systems in the game world.
"""

from typing import Dict, List, Set, Optional, Type, Any
import copy

from entities.base import Entity, Component
from systems.base import ISystem
from engine.event_system import EventSystem, EventType, get_event_system


class World:
    """
    Main world manager for the Entity-Component-System architecture.

    Manages all entities, provides fast component queries, and coordinates
    system updates. Integrates with the EventSystem for entity lifecycle events.

    Attributes:
        entities: Dictionary of all entities by ID
        _component_index: Index of entities by component type for fast queries
        _systems: List of registered systems
        _event_system: Reference to the global event system
    """

    def __init__(self, event_system: Optional[EventSystem] = None):
        """
        Initialize the world.

        Args:
            event_system: Optional event system instance (uses global if None)
        """
        self.entities: Dict[str, Entity] = {}
        self._component_index: Dict[Type, List[Entity]] = {}
        self._systems: List[ISystem] = []
        self._event_system = event_system or get_event_system()
        self._next_entity_id = 0

    def create_entity(
        self, entity: Optional[Entity] = None, entity_id: Optional[str] = None
    ) -> Entity:
        """
        Create a new entity in the world.

        Args:
            entity: Optional entity instance to add (creates new if None)
            entity_id: Optional custom ID for the entity

        Returns:
            The created entity
        """
        if entity is None:
            entity = Entity(entity_id or f"entity_{self._next_entity_id}")
            self._next_entity_id += 1
        else:
            if entity_id:
                entity.id = entity_id
            elif not entity.id:
                entity.id = f"entity_{self._next_entity_id}"
                self._next_entity_id += 1

        self.entities[entity.id] = entity
        self._index_entity(entity)

        self._event_system.emit(
            EventType.ENTITY_CREATED, {"entity_id": entity.id, "entity": entity}
        )

        return entity

    def destroy_entity(self, entity: Entity) -> None:
        """
        Destroy an entity and remove it from the world.

        Args:
            entity: The entity to destroy
        """
        if entity.id not in self.entities:
            return

        self._unindex_entity(entity)
        del self.entities[entity.id]

        self._event_system.emit(EventType.ENTITY_DESTROYED, {"entity_id": entity.id})

    def get_entities_with(self, *component_types: Type[Component]) -> List[Entity]:
        """
        Get all entities that have all specified component types.

        Args:
            component_types: Variable number of component types to filter by

        Returns:
            List of entities matching all component types
        """
        if not component_types:
            return list(self.entities.values())

        result = []
        for entity in self.entities.values():
            if all(entity.has_component(ct.__name__) for ct in component_types):
                result.append(entity)

        return result

    def add_system(self, system: ISystem) -> None:
        """
        Add a system to the world.

        Args:
            system: The system to add
        """
        self._systems.append(system)

    def remove_system(self, system: ISystem) -> None:
        """
        Remove a system from the world.

        Args:
            system: The system to remove
        """
        if system in self._systems:
            self._systems.remove(system)

    def update(self, dt: float) -> None:
        """
        Update all systems in the world.

        Args:
            dt: Delta time since last update in seconds
        """
        for system in self._systems:
            system.update(dt)

    def has_tag(self, entity: Entity, tag: str) -> bool:
        """
        Check if an entity has a specific tag.

        Args:
            entity: The entity to check
            tag: The tag to check for

        Returns:
            True if the entity has the tag, False otherwise
        """
        return entity.has_tag(tag)

    def add_tag(self, entity: Entity, tag: str) -> None:
        """
        Add a tag to an entity.

        Args:
            entity: The entity to tag
            tag: The tag to add
        """
        entity.add_tag(tag)

    def remove_tag(self, entity: Entity, tag: str) -> None:
        """
        Remove a tag from an entity.

        Args:
            entity: The entity to untag
            tag: The tag to remove
        """
        entity.remove_tag(tag)

    def clone_entity(self, entity: Entity, new_id: Optional[str] = None) -> Entity:
        """
        Create a clone of an entity (prototype pattern).

        Creates a new entity with the same components and tags as the original.
        Components are deep-copied to ensure independence.

        Args:
            entity: The entity to clone
            new_id: Optional new ID for the cloned entity

        Returns:
            The cloned entity
        """
        entity_type = type(entity)
        cloned = entity_type(new_id or f"{entity.id}_clone")

        for name, component in entity.components.items():
            cloned_component = copy.deepcopy(component)
            cloned.add_component(cloned_component, name)

        for tag in entity.tags:
            cloned.add_tag(tag)

        return self.create_entity(cloned)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by its ID.

        Args:
            entity_id: The ID of the entity to retrieve

        Returns:
            The entity if found, None otherwise
        """
        return self.entities.get(entity_id)

    def get_entities_by_tag(self, tag: str) -> List[Entity]:
        """
        Get all entities with a specific tag.

        Args:
            tag: The tag to filter by

        Returns:
            List of entities with the specified tag
        """
        return [e for e in self.entities.values() if e.has_tag(tag)]

    def clear(self) -> None:
        """Clear all entities and systems from the world."""
        self.entities.clear()
        self._component_index.clear()
        self._systems.clear()
        self._next_entity_id = 0

    def _index_entity(self, entity: Entity) -> None:
        """
        Add an entity to the component index.

        Args:
            entity: The entity to index
        """
        for name, component in entity.components.items():
            component_type = type(component)
            if component_type not in self._component_index:
                self._component_index[component_type] = []
            if entity not in self._component_index[component_type]:
                self._component_index[component_type].append(entity)

    def _unindex_entity(self, entity: Entity) -> None:
        """
        Remove an entity from the component index.

        Args:
            entity: The entity to unindex
        """
        for name, component in entity.components.items():
            component_type = type(component)
            if component_type in self._component_index:
                if entity in self._component_index[component_type]:
                    self._component_index[component_type].remove(entity)

    def _on_component_added(
        self, entity: Entity, component: Component, name: str
    ) -> None:
        """
        Handle component added to an entity.

        Args:
            entity: The entity that received the component
            component: The component that was added
            name: The name of the component
        """
        self._index_entity(entity)

        self._event_system.emit(
            EventType.COMPONENT_ADDED,
            {
                "entity_id": entity.id,
                "component_name": name,
                "component_type": type(component).__name__,
            },
        )

    def _on_component_removed(self, entity: Entity, name: str) -> None:
        """
        Handle component removed from an entity.

        Args:
            entity: The entity that lost the component
            name: The name of the removed component
        """
        self._unindex_entity(entity)

        self._event_system.emit(
            EventType.COMPONENT_REMOVED,
            {"entity_id": entity.id, "component_name": name},
        )
