"""
Components - Abstract and concrete component classes for entities
"""

import math
from abc import ABC
from typing import Optional, Tuple
from entities.base import Component


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
