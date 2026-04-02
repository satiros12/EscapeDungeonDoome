"""
Serialization - Functions for serializing and deserializing entities and worlds.
"""

from typing import Dict, Any, Optional, Type, Callable
import copy

from entities.base import Entity, Component
from entities.components import (
    PositionComponent,
    HealthComponent,
    AIComponent,
    CombatComponent,
    PlayerInputComponent,
    CollidableComponent,
    InventoryComponent,
    AnimationComponent,
    VelocityComponent,
    WeaponComponent,
)
from world.world import World


# Mapping of component class names to their classes for deserialization
_COMPONENT_CLASSES: Dict[str, Type[Component]] = {
    "PositionComponent": PositionComponent,
    "HealthComponent": HealthComponent,
    "AIComponent": AIComponent,
    "CombatComponent": CombatComponent,
    "PlayerInputComponent": PlayerInputComponent,
    "CollidableComponent": CollidableComponent,
    "InventoryComponent": InventoryComponent,
    "AnimationComponent": AnimationComponent,
    "VelocityComponent": VelocityComponent,
    "WeaponComponent": WeaponComponent,
}


def serialize_component(component: Component) -> Dict[str, Any]:
    """
    Serialize a single component to a dictionary.

    Args:
        component: The component to serialize

    Returns:
        Dictionary representation of the component
    """
    if isinstance(component, PositionComponent):
        return {
            "x": component.x,
            "y": component.y,
            "angle": component.angle,
        }
    elif isinstance(component, HealthComponent):
        return {
            "health": component.health,
            "max_health": component.max_health,
            "is_dead": component.is_dead,
        }
    elif isinstance(component, AIComponent):
        return {
            "enemy_type": component.enemy_type,
            "state": component.state,
            "target": component.target,
            "patrol_dir": component.patrol_dir,
            "attack_cooldown": component.attack_cooldown,
            "dying_progress": component.dying_progress,
        }
    elif isinstance(component, CombatComponent):
        return {
            "attack_cooldown": component.attack_cooldown,
            "attack_range": component.attack_range,
            "attack_damage": component.attack_damage,
        }
    elif isinstance(component, PlayerInputComponent):
        return {
            "keys": copy.deepcopy(component.keys),
            "is_attacking": component.is_attacking,
        }
    elif isinstance(component, CollidableComponent):
        return {
            "collision_radius": component.get_collision_radius(),
        }
    elif isinstance(component, InventoryComponent):
        return {
            "capacity": component.capacity,
            "items": copy.deepcopy(component.items),
        }
    elif isinstance(component, AnimationComponent):
        return {
            "current_animation": component.current_animation,
            "frame_index": component.frame_index,
            "animation_speed": component.animation_speed,
        }
    elif isinstance(component, VelocityComponent):
        return {
            "vx": component.vx,
            "vy": component.vy,
        }
    elif isinstance(component, WeaponComponent):
        return {
            "weapon_type": component.weapon_type,
            "attack_cooldown": component.attack_cooldown,
            "attack_range": component.attack_range,
            "attack_damage": component.attack_damage,
        }
    else:
        # For unknown components, return empty dict
        return {}


def deserialize_component(
    component_name: str, data: Dict[str, Any]
) -> Optional[Component]:
    """
    Deserialize a component from a dictionary.

    Args:
        component_name: The name of the component class
        data: The serialized data

    Returns:
        The deserialized component, or None if unknown
    """
    component_class = _COMPONENT_CLASSES.get(component_name)
    if component_class is None:
        return None

    if component_name == "PositionComponent":
        return PositionComponent(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            angle=data.get("angle", 0.0),
        )
    elif component_name == "HealthComponent":
        return HealthComponent(
            health=data.get("health", 100),
            max_health=data.get("max_health", 100),
        )
    elif component_name == "AIComponent":
        return AIComponent(
            enemy_type=data.get("enemy_type", "imp"),
            state=data.get("state", "patrol"),
            target=data.get("target"),
        )
    elif component_name == "CombatComponent":
        return CombatComponent(
            attack_cooldown=data.get("attack_cooldown", 0.5),
            attack_range=data.get("attack_range", 1.5),
            attack_damage=data.get("attack_damage", 10),
        )
    elif component_name == "PlayerInputComponent":
        component = PlayerInputComponent()
        component.keys = copy.deepcopy(data.get("keys", {}))
        component.is_attacking = data.get("is_attacking", False)
        return component
    elif component_name == "CollidableComponent":
        return CollidableComponent(
            collision_radius=data.get("collision_radius", 0.3),
        )
    elif component_name == "InventoryComponent":
        return InventoryComponent(
            capacity=data.get("capacity", 10),
        )
    elif component_name == "AnimationComponent":
        return AnimationComponent(
            current_animation=data.get("current_animation", "idle"),
            frame_index=data.get("frame_index", 0),
            animation_speed=data.get("animation_speed", 1.0),
        )
    elif component_name == "VelocityComponent":
        return VelocityComponent(
            vx=data.get("vx", 0.0),
            vy=data.get("vy", 0.0),
        )
    elif component_name == "WeaponComponent":
        return WeaponComponent(
            weapon_type=data.get("weapon_type", "fists"),
        )

    return None


def serialize_entity(entity: Entity) -> Dict[str, Any]:
    """
    Serialize an entity to a dictionary.

    Args:
        entity: The entity to serialize

    Returns:
        Dictionary representation of the entity
    """
    components_data = {}
    for name, component in entity.components.items():
        component_type = type(component).__name__
        components_data[name] = {
            "type": component_type,
            "data": serialize_component(component),
        }

    return {
        "id": entity.id,
        "tags": list(entity.tags),
        "components": components_data,
    }


def deserialize_entity(
    data: Dict[str, Any], entity_factory: Optional[Callable[[str], Entity]] = None
) -> Entity:
    """
    Deserialize an entity from a dictionary.

    Args:
        data: The serialized data
        entity_factory: Optional factory function to create the entity

    Returns:
        The deserialized entity

    Note:
        If no entity_factory is provided, the entity will be created with
        a basic Entity class. The caller must ensure the entity has an
        update() method or use a proper factory.
    """
    entity_id = data.get("id", "unknown")
    tags = data.get("tags", [])
    components_data = data.get("components", {})

    # Use factory if provided, otherwise create basic Entity
    # Note: Entity is abstract, so we need a factory for proper deserialization
    if entity_factory:
        entity = entity_factory(entity_id)
    else:
        # Create a minimal entity for deserialization purposes
        # This is a workaround - in production, use a proper entity factory
        from entities.base import Entity as BaseEntity

        class BasicEntity(BaseEntity):
            def update(self, dt: float) -> None:
                pass

        entity = BasicEntity(entity_id)

    # Add tags
    for tag in tags:
        entity.add_tag(tag)

    # Add components
    for name, component_info in components_data.items():
        component_type = component_info.get("type", name)
        component_data = component_info.get("data", {})

        component = deserialize_component(component_type, component_data)
        if component is not None:
            entity.add_component(component, name)

    return entity


def serialize_world(world: World) -> Dict[str, Any]:
    """
    Serialize the entire world to a dictionary.

    Args:
        world: The world to serialize

    Returns:
        Dictionary representation of the world
    """
    entities_data = []
    for entity in world.entities.values():
        entities_data.append(serialize_entity(entity))

    return {
        "entities": entities_data,
        "next_entity_id": world._next_entity_id,
    }


def deserialize_world(
    data: Dict[str, Any],
    world: Optional[World] = None,
    entity_factory: Optional[Callable[[str], Entity]] = None,
) -> World:
    """
    Deserialize a world from a dictionary.

    Args:
        data: The serialized data
        world: Optional existing world to populate (creates new if None)
        entity_factory: Optional factory function to create entities

    Returns:
        The deserialized world
    """
    if world is None:
        world = World()

    entities_data = data.get("entities", [])
    next_entity_id = data.get("next_entity_id", 0)

    # Clear existing entities
    world.clear()

    # Deserialize entities
    for entity_data in entities_data:
        entity = deserialize_entity(entity_data, entity_factory)
        world.create_entity(entity)

    # Restore next_entity_id counter
    world._next_entity_id = next_entity_id

    return world
