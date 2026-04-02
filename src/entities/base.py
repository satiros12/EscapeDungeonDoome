"""
Entity Base - Base class for all game entities
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Set


class Component(ABC):
    """Base class for all entity components."""

    def __init__(self):
        self._entity: Optional["Entity"] = None

    @property
    def entity(self) -> Optional["Entity"]:
        """Get the entity this component belongs to."""
        return self._entity

    @entity.setter
    def entity(self, value: "Entity") -> None:
        """Set the entity this component belongs to."""
        self._entity = value

    def on_attach(self, entity: "Entity") -> None:
        """
        Called when this component is attached to an entity.

        Args:
            entity: The entity this component is being attached to
        """
        pass

    def on_detach(self) -> None:
        """Called when this component is removed from an entity."""
        pass


class SerializableComponent(Component):
    """
    Base class for components that support serialization.

    Extends Component with to_dict() and from_dict() class methods
    for converting components to and from dictionary representations.
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert component to dictionary for serialization.

        Returns:
            Dictionary representation of the component
        """
        return {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SerializableComponent":
        """
        Create component from dictionary representation.

        Args:
            data: Dictionary containing component data

        Returns:
            New component instance
        """
        return cls()


class Entity(ABC):
    """
    Base class for all game entities.

    Entities are objects that have a unique identity and are composed
    of components. They represent game objects like players, enemies,
    items, etc.

    Attributes:
        id: Unique identifier for this entity
        components: Dictionary of components attached to this entity
    """

    def __init__(self, entity_id: str):
        """
        Initialize the entity.

        Args:
            entity_id: Unique identifier for this entity
        """
        self.id = entity_id
        self._components: Dict[str, Component] = {}
        self._tags: Set[str] = set()
        self.on_create()

    def on_create(self) -> None:
        """Called when the entity is created in the world."""
        pass

    def on_destroy(self) -> None:
        """Called when the entity is destroyed."""
        pass

    def on_component_added(self, component: Component) -> None:
        """
        Called when a component is added to this entity.

        Args:
            component: The component that was added
        """
        pass

    def on_component_removed(self, component_name: str) -> None:
        """
        Called when a component is removed from this entity.

        Args:
            component_name: Name of the component that was removed
        """
        pass

    def get_component(self, name: str) -> Optional[Component]:
        """
        Get a component by name.

        Args:
            name: Name of the component to retrieve

        Returns:
            The component if found, None otherwise
        """
        return self._components.get(name)

    def add_component(self, component: Component, name: str = None) -> None:
        """
        Add a component to this entity.

        Args:
            component: Component to add
            name: Optional name for the component (defaults to class name)
        """
        if name is None:
            name = component.__class__.__name__

        component.entity = self
        component.on_attach(self)
        self._components[name] = component
        self.on_component_added(component)

    def remove_component(self, name: str) -> None:
        """
        Remove a component from this entity.

        Args:
            name: Name of the component to remove
        """
        if name in self._components:
            component = self._components[name]
            component.on_detach()
            component.entity = None
            del self._components[name]
            self.on_component_removed(name)

    def has_component(self, name: str) -> bool:
        """
        Check if entity has a specific component.

        Args:
            name: Name of the component to check

        Returns:
            True if the component exists, False otherwise
        """
        return name in self._components

    @property
    def components(self) -> Dict[str, Component]:
        """Get all components attached to this entity."""
        return self._components

    @property
    def tags(self) -> Set[str]:
        """Get all tags attached to this entity."""
        return self._tags

    def add_tag(self, tag: str) -> None:
        """Add a tag to this entity."""
        self._tags.add(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this entity."""
        self._tags.discard(tag)

    def has_tag(self, tag: str) -> bool:
        """Check if entity has a specific tag."""
        return tag in self._tags

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update the entity for one frame.

        Args:
            dt: Delta time since last update in seconds
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entity to dictionary for serialization.

        Returns:
            Dictionary representation of the entity
        """
        return {
            "id": self.id,
            "components": {
                name: {"type": type(comp).__name__}
                for name, comp in self._components.items()
            },
        }
