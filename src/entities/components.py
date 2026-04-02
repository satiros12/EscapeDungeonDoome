"""
Components - Abstract and concrete component classes for entities
"""

import math
from abc import ABC
from typing import Optional, Tuple, Dict, Any
from entities.base import Component, SerializableComponent


class PositionComponent(Component):
    """
    Component for entity position and orientation.

    Attributes:
        x: X coordinate position
        y: Y coordinate position
        angle: Facing angle in radians
    """

    def __init__(self, x: float = 0.0, y: float = 0.0, angle: float = 0.0):
        super().__init__()
        self.x = x
        self.y = y
        self.angle = angle

    def move(self, dx: float, dy: float) -> None:
        """
        Move the entity by the given delta.

        Args:
            dx: Change in X coordinate
            dy: Change in Y coordinate
        """
        self.x += dx
        self.y += dy

    def rotate(self, da: float) -> None:
        """
        Rotate the entity by the given angle delta.

        Args:
            da: Change in angle in radians
        """
        self.angle += da
        # Normalize angle to [-pi, pi]
        while self.angle > math.pi:
            self.angle -= 2 * math.pi
        while self.angle < -math.pi:
            self.angle += 2 * math.pi

    def get_position(self) -> Tuple[float, float]:
        """
        Get the entity's position as a tuple.

        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)

    def get_direction(self) -> Tuple[float, float]:
        """
        Get the direction vector based on current angle.

        Returns:
            Tuple of (dx, dy) direction components
        """
        return (math.cos(self.angle), math.sin(self.angle))

    def distance_to(self, x: float, y: float) -> float:
        """
        Calculate distance to another point.

        Args:
            x: Target X coordinate
            y: Target Y coordinate

        Returns:
            Distance to the target point
        """
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert component to dictionary for serialization.

        Returns:
            Dictionary representation of the component
        """
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PositionComponent":
        """
        Create component from dictionary representation.

        Args:
            data: Dictionary containing component data

        Returns:
            New PositionComponent instance
        """
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            angle=data.get("angle", 0.0),
        )


class HealthComponent(Component):
    """
    Component for entity health and damage handling.

    Attributes:
        health: Current health points
        max_health: Maximum health points
        is_dead: Whether the entity is dead
    """

    def __init__(self, health: int = 100, max_health: int = 100):
        super().__init__()
        self.health = health
        self.max_health = max_health
        self.is_dead = False

    def take_damage(self, amount: int) -> bool:
        """
        Apply damage to the entity.

        Args:
            amount: Amount of damage to apply

        Returns:
            True if entity died from the damage, False otherwise
        """
        if self.is_dead:
            return True

        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            return True
        return False

    def heal(self, amount: int) -> None:
        """
        Heal the entity by the given amount.

        Args:
            amount: Amount of health to restore
        """
        if self.is_dead:
            return

        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    @property
    def health_percentage(self) -> float:
        """
        Get health as a percentage of max health.

        Returns:
            Health percentage (0.0 to 1.0)
        """
        return self.health / self.max_health if self.max_health > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert component to dictionary for serialization.

        Returns:
            Dictionary representation of the component
        """
        return {
            "health": self.health,
            "max_health": self.max_health,
            "is_dead": self.is_dead,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthComponent":
        """
        Create component from dictionary representation.

        Args:
            data: Dictionary containing component data

        Returns:
            New HealthComponent instance
        """
        return cls(
            health=data.get("health", 100),
            max_health=data.get("max_health", 100),
        )


class AIComponent(Component):
    """
    Component for enemy AI behavior.

    Attributes:
        enemy_type: Type of enemy (imp, demon, etc.)
        state: Current AI state (patrol, chase, attack, dying)
        target: Target entity ID to track
        patrol_dir: Direction for patrolling in radians
        attack_cooldown: Time until next attack possible
        dying_progress: Progress of death animation (0.0 to 1.0)
    """

    def __init__(
        self,
        enemy_type: str = "imp",
        state: str = "patrol",
        target: Optional[str] = None,
    ):
        super().__init__()
        self.enemy_type = enemy_type
        self.state = state
        self.target = target
        self.patrol_dir: float = 0.0
        self.attack_cooldown: float = 0.0
        self.dying_progress: float = 0.0

    def update_cooldown(self, dt: float) -> None:
        """
        Update attack cooldown timer.

        Args:
            dt: Delta time since last update
        """
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def can_attack(self) -> bool:
        """
        Check if entity can attack.

        Returns:
            True if attack cooldown is zero and not dying
        """
        return self.attack_cooldown <= 0 and self.state != "dying"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert component to dictionary for serialization.

        Returns:
            Dictionary representation of the component
        """
        return {
            "enemy_type": self.enemy_type,
            "state": self.state,
            "target": self.target,
            "patrol_dir": self.patrol_dir,
            "attack_cooldown": self.attack_cooldown,
            "dying_progress": self.dying_progress,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIComponent":
        """
        Create component from dictionary representation.

        Args:
            data: Dictionary containing component data

        Returns:
            New AIComponent instance
        """
        return cls(
            enemy_type=data.get("enemy_type", "imp"),
            state=data.get("state", "patrol"),
            target=data.get("target"),
        )


class CombatComponent(Component):
    """
    Component for combat mechanics.

    Attributes:
        attack_cooldown: Time until next attack possible
        attack_range: Maximum range for attacks
        attack_damage: Damage dealt per attack
    """

    def __init__(
        self,
        attack_cooldown: float = 0.5,
        attack_range: float = 1.5,
        attack_damage: int = 10,
    ):
        super().__init__()
        self.attack_cooldown = attack_cooldown
        self.attack_range = attack_range
        self.attack_damage = attack_damage

    def can_attack(self) -> bool:
        """
        Check if can perform an attack.

        Returns:
            True if attack cooldown is ready
        """
        return self.attack_cooldown <= 0

    def perform_attack(self) -> bool:
        """
        Perform an attack, consuming the cooldown.

        Returns:
            True if attack was performed, False if on cooldown
        """
        if self.can_attack():
            self.attack_cooldown = 0.5  # Reset to default
            return True
        return False

    def update(self, dt: float) -> None:
        """
        Update combat component state.

        Args:
            dt: Delta time since last update
        """
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert component to dictionary for serialization.

        Returns:
            Dictionary representation of the component
        """
        return {
            "attack_cooldown": self.attack_cooldown,
            "attack_range": self.attack_range,
            "attack_damage": self.attack_damage,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CombatComponent":
        """
        Create component from dictionary representation.

        Args:
            data: Dictionary containing component data

        Returns:
            New CombatComponent instance
        """
        return cls(
            attack_cooldown=data.get("attack_cooldown", 0.5),
            attack_range=data.get("attack_range", 1.5),
            attack_damage=data.get("attack_damage", 10),
        )


class PlayerInputComponent(Component):
    """
    Component for player input state.

    This component stores the current input state for the player,
    tracking which keys are pressed.
    """

    def __init__(self):
        super().__init__()
        self.keys: dict = {}
        self.is_attacking: bool = False

    def update_keys(self, keys: dict) -> None:
        """
        Update the current input state.

        Args:
            keys: Dictionary of key states
        """
        self.keys = keys

    def is_key_pressed(self, key: str) -> bool:
        """
        Check if a specific key is pressed.

        Args:
            key: Key name to check

        Returns:
            True if the key is currently pressed
        """
        return self.keys.get(key, False)


class CollidableComponent(Component):
    """
    Component for entities that can collide with walls and other entities.

    Attributes:
        collision_radius: Radius used for collision detection
        on_collision: Optional callback for collision events
    """

    def __init__(
        self,
        collision_radius: float = 0.3,
        on_collision: Optional[callable] = None,
    ):
        """
        Initialize the collidable component.

        Args:
            collision_radius: Radius for collision detection
            on_collision: Optional callback called when collision occurs
        """
        super().__init__()
        self._collision_radius = collision_radius
        self._on_collision = on_collision

    def get_collision_radius(self) -> float:
        """
        Get the collision radius.

        Returns:
            The collision radius value
        """
        return self._collision_radius

    def set_collision_radius(self, radius: float) -> None:
        """
        Set a new collision radius.

        Args:
            radius: New radius value
        """
        self._collision_radius = radius

    def on_collision_hit(self, other: "Entity") -> None:
        """
        Handle collision with another entity.

        Args:
            other: The entity this entity collided with
        """
        if self._on_collision is not None:
            self._on_collision(other)


class InventoryComponent(Component):
    """
    Component for entity inventory management.

    This is a placeholder for the inventory system to be implemented
    in a future feature.

    Attributes:
        capacity: Maximum number of items the inventory can hold
        items: List of item IDs currently in the inventory
    """

    def __init__(self, capacity: int = 10):
        super().__init__()
        self.capacity = capacity
        self.items: list[str] = []

    def add_item(self, item_id: str) -> bool:
        """
        Add an item to the inventory.

        Args:
            item_id: The ID of the item to add

        Returns:
            True if item was added, False if inventory is full
        """
        if len(self.items) >= self.capacity:
            return False
        self.items.append(item_id)
        return True

    def remove_item(self, item_id: str) -> bool:
        """
        Remove an item from the inventory.

        Args:
            item_id: The ID of the item to remove

        Returns:
            True if item was removed, False if item not found
        """
        if item_id in self.items:
            self.items.remove(item_id)
            return True
        return False

    def get_items(self) -> list[str]:
        """
        Get all items in the inventory.

        Returns:
            List of item IDs
        """
        return self.items.copy()


class AnimationComponent(Component):
    """
    Component for entity animation state.

    This is a placeholder for the animation system to be implemented
    in a future feature.

    Attributes:
        current_animation: Name of the currently playing animation
        frame_index: Current frame in the animation
        animation_speed: Speed multiplier for animation playback
    """

    def __init__(
        self,
        current_animation: str = "idle",
        frame_index: int = 0,
        animation_speed: float = 1.0,
    ):
        super().__init__()
        self.current_animation = current_animation
        self.frame_index = frame_index
        self.animation_speed = animation_speed
        self._is_playing: bool = False

    def play(self) -> None:
        """Start playing the current animation."""
        self._is_playing = True

    def stop(self) -> None:
        """Stop playing the current animation."""
        self._is_playing = False

    def set_animation(self, animation_name: str) -> None:
        """
        Set a new animation to play.

        Args:
            animation_name: Name of the animation to play
        """
        if animation_name != self.current_animation:
            self.current_animation = animation_name
            self.frame_index = 0


class VelocityComponent(Component):
    """
    Component for physics-based movement.

    This component stores velocity information for entities that
    use physics-based movement rather than direct position manipulation.

    Attributes:
        vx: Velocity in the X direction
        vy: Velocity in the Y direction
    """

    def __init__(self, vx: float = 0.0, vy: float = 0.0):
        super().__init__()
        self.vx = vx
        self.vy = vy

    def set_velocity(self, vx: float, vy: float) -> None:
        """
        Set the velocity components.

        Args:
            vx: Velocity in the X direction
            vy: Velocity in the Y direction
        """
        self.vx = vx
        self.vy = vy

    def get_velocity(self) -> tuple[float, float]:
        """
        Get the current velocity.

        Returns:
            Tuple of (vx, vy) velocity components
        """
        return (self.vx, self.vy)

    def apply_force(self, fx: float, fy: float) -> None:
        """
        Apply a force to modify velocity.

        Args:
            fx: Force in the X direction
            fy: Force in the Y direction
        """
        self.vx += fx
        self.vy += fy


class WeaponComponent(CombatComponent):
    """
    Component for weapon-specific combat logic.

    Extends CombatComponent with weapon-specific attributes and methods.

    Attributes:
        weapon_type: Type of weapon (fists, pistol, shotgun, etc.)
    """

    def __init__(self, weapon_type: str = "fists"):
        super().__init__(
            attack_cooldown=0.5,
            attack_range=1.5,
            attack_damage=10,
        )
        self.weapon_type = weapon_type

    def get_damage(self) -> int:
        """
        Get the damage dealt by this weapon.

        Returns:
            Attack damage value
        """
        return self.attack_damage

    def get_range(self) -> float:
        """
        Get the attack range of this weapon.

        Returns:
            Attack range in units
        """
        return self.attack_range

    def is_ready(self) -> bool:
        """
        Check if the weapon is ready to fire.

        Returns:
            True if attack cooldown is ready
        """
        return self.can_attack()
