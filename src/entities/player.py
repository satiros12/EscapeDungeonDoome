"""
Player Entity - Player-specific entity implementation
"""

import math
from typing import Dict, Any, Optional
from entities.base import Entity
from entities.components import (
    PositionComponent,
    HealthComponent,
    CombatComponent,
    PlayerInputComponent,
)


class PlayerEntity(Entity):
    """
    Player entity with specialized components for gameplay.

    The player entity contains all components needed for player
    functionality including position, health, combat, and input.
    """

    def __init__(self, entity_id: str = "player"):
        """
        Initialize the player entity.

        Args:
            entity_id: Unique identifier for this player entity
        """
        super().__init__(entity_id)

        # Add default components
        self.add_component(PositionComponent(x=1.5, y=1.5, angle=0.0))
        self.add_component(HealthComponent(health=100, max_health=100))
        self.add_component(
            CombatComponent(attack_cooldown=0.5, attack_range=1.5, attack_damage=10)
        )
        self.add_component(PlayerInputComponent())

        # Game state properties (not components)
        self.god_mode: bool = False
        self.speed_multiplier: float = 1.0
        self.current_weapon: str = "fists"
        self.ammo: Dict[str, int] = {}
        self.armor: int = 0
        self.armor_type: str = "none"

    @property
    def position(self) -> PositionComponent:
        """Get the position component."""
        return self.get_component("PositionComponent")

    @property
    def health_component(self) -> HealthComponent:
        """Get the health component."""
        return self.get_component("HealthComponent")

    @property
    def combat(self) -> CombatComponent:
        """Get the combat component."""
        return self.get_component("CombatComponent")

    @property
    def input(self) -> PlayerInputComponent:
        """Get the input component."""
        return self.get_component("PlayerInputComponent")

    @property
    def x(self) -> float:
        """Get player X position."""
        return self.position.x if self.position else 0.0

    @x.setter
    def x(self, value: float) -> None:
        """Set player X position."""
        if self.position:
            self.position.x = value

    @property
    def y(self) -> float:
        """Get player Y position."""
        return self.position.y if self.position else 0.0

    @y.setter
    def y(self, value: float) -> None:
        """Set player Y position."""
        if self.position:
            self.position.y = value

    @property
    def angle(self) -> float:
        """Get player facing angle."""
        return self.position.angle if self.position else 0.0

    @angle.setter
    def angle(self, value: float) -> None:
        """Set player facing angle."""
        if self.position:
            self.position.angle = value

    @property
    def health(self) -> int:
        """Get player health."""
        return self.health_component.health if self.health_component else 0

    @health.setter
    def health(self, value: int) -> None:
        """Set player health."""
        if self.health_component:
            self.health_component.health = value

    @property
    def attack_cooldown(self) -> float:
        """Get attack cooldown."""
        return self.combat.attack_cooldown if self.combat else 0.0

    @attack_cooldown.setter
    def attack_cooldown(self, value: float) -> None:
        """Set attack cooldown."""
        if self.combat:
            self.combat.attack_cooldown = value

    def update(self, dt: float) -> None:
        """Update player entity."""
        # Update combat cooldown
        if self.combat:
            self.combat.update(dt)

    def reset(self) -> None:
        """Reset player to default state."""
        self.x = 1.5
        self.y = 1.5
        self.angle = 0.0

        if self.health_component:
            self.health_component.health = 100
            self.health_component.is_dead = False

        if self.combat:
            self.combat.attack_cooldown = 0.0

        self.god_mode = False
        self.speed_multiplier = 1.0
        self.current_weapon = "fists"
        self.ammo = {}
        self.armor = 0
        self.armor_type = "none"

    def to_dict(self) -> Dict[str, Any]:
        """Convert player entity to dictionary."""
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "health": self.health,
            "attack_cooldown": self.attack_cooldown,
            "god_mode": self.god_mode,
            "speed_multiplier": self.speed_multiplier,
            "current_weapon": self.current_weapon,
            "ammo": self.ammo,
            "armor": self.armor,
            "armor_type": self.armor_type,
        }
