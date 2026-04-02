"""
Enemy Entity - Enemy-specific entity implementation
"""

import math
import random
from typing import Dict, Any, Optional
from entities.base import Entity
from entities.components import (
    PositionComponent,
    HealthComponent,
    AIComponent,
    CombatComponent,
)


class EnemyEntity(Entity):
    """
    Enemy entity with specialized components for AI and combat.

    The enemy entity contains all components needed for enemy
    functionality including position, health, AI behavior, and combat.
    """

    def __init__(
        self, entity_id: str, enemy_type: str = "imp", x: float = 0.0, y: float = 0.0
    ):
        """
        Initialize the enemy entity.

        Args:
            entity_id: Unique identifier for this enemy
            enemy_type: Type of enemy (imp, demon, cacodemon)
            x: Starting X position
            y: Starting Y position
        """
        super().__init__(entity_id)

        # Get enemy configuration
        config = self._get_enemy_config(enemy_type)

        # Add default components
        self.add_component(PositionComponent(x=x, y=y, angle=0.0))
        self.add_component(
            HealthComponent(health=config["health"], max_health=config["health"])
        )
        self.add_component(
            AIComponent(enemy_type=enemy_type, state="patrol", target="player")
        )
        self.add_component(
            CombatComponent(
                attack_cooldown=1.0, attack_range=1.0, attack_damage=config["damage"]
            )
        )

        # Set initial patrol direction
        ai = self.get_component("AIComponent")
        if ai:
            ai.patrol_dir = random.random() * 2 * math.pi

        # Additional properties
        self.weapon: str = config["weapon"]
        self.armor: int = 0
        self.armor_type: str = "none"

    def _get_enemy_config(self, enemy_type: str) -> Dict[str, Any]:
        """
        Get configuration for enemy type.

        Args:
            enemy_type: Type of enemy

        Returns:
            Dictionary with health, speed, weapon, and damage
        """
        configs = {
            "imp": {"health": 30, "speed": 2.5, "weapon": "fists", "damage": 10},
            "demon": {"health": 60, "speed": 2.0, "weapon": "fists", "damage": 15},
            "cacodemon": {"health": 100, "speed": 1.5, "weapon": "fists", "damage": 20},
            "soldier_pistol": {
                "health": 20,
                "speed": 1.5,
                "weapon": "pistol",
                "damage": 5,
            },
            "soldier_shotgun": {
                "health": 25,
                "speed": 1.3,
                "weapon": "shotgun",
                "damage": 8,
            },
            "chaingunner": {
                "health": 35,
                "speed": 1.4,
                "weapon": "chaingun",
                "damage": 6,
            },
        }
        return configs.get(enemy_type, configs["imp"])

    @property
    def position(self) -> PositionComponent:
        """Get the position component."""
        return self.get_component("PositionComponent")

    @property
    def health_component(self) -> HealthComponent:
        """Get the health component."""
        return self.get_component("HealthComponent")

    @property
    def ai(self) -> AIComponent:
        """Get the AI component."""
        return self.get_component("AIComponent")

    @property
    def combat(self) -> CombatComponent:
        """Get the combat component."""
        return self.get_component("CombatComponent")

    @property
    def x(self) -> float:
        """Get enemy X position."""
        return self.position.x if self.position else 0.0

    @x.setter
    def x(self, value: float) -> None:
        """Set enemy X position."""
        if self.position:
            self.position.x = value

    @property
    def y(self) -> float:
        """Get enemy Y position."""
        return self.position.y if self.position else 0.0

    @y.setter
    def y(self, value: float) -> None:
        """Set enemy Y position."""
        if self.position:
            self.position.y = value

    @property
    def angle(self) -> float:
        """Get enemy facing angle."""
        return self.position.angle if self.position else 0.0

    @angle.setter
    def angle(self, value: float) -> None:
        """Set enemy facing angle."""
        if self.position:
            self.position.angle = value

    @property
    def health(self) -> int:
        """Get enemy health."""
        return self.health_component.health if self.health_component else 0

    @health.setter
    def health(self, value: int) -> None:
        """Set enemy health."""
        if self.health_component:
            self.health_component.health = value

    @property
    def state(self) -> str:
        """Get enemy AI state."""
        return self.ai.state if self.ai else "patrol"

    @state.setter
    def state(self, value: str) -> None:
        """Set enemy AI state."""
        if self.ai:
            self.ai.state = value

    @property
    def patrol_dir(self) -> float:
        """Get patrol direction."""
        return self.ai.patrol_dir if self.ai else 0.0

    @patrol_dir.setter
    def patrol_dir(self, value: float) -> None:
        """Set patrol direction."""
        if self.ai:
            self.ai.patrol_dir = value

    @property
    def attack_cooldown(self) -> float:
        """Get attack cooldown."""
        return self.ai.attack_cooldown if self.ai else 0.0

    @attack_cooldown.setter
    def attack_cooldown(self, value: float) -> None:
        """Set attack cooldown."""
        if self.ai:
            self.ai.attack_cooldown = value

    @property
    def dying_progress(self) -> float:
        """Get dying progress."""
        return self.ai.dying_progress if self.ai else 0.0

    @dying_progress.setter
    def dying_progress(self, value: float) -> None:
        """Set dying progress."""
        if self.ai:
            self.ai.dying_progress = value

    @property
    def enemy_type(self) -> str:
        """Get enemy type."""
        return self.ai.enemy_type if self.ai else "imp"

    def update(self, dt: float) -> None:
        """Update enemy entity."""
        # Update AI cooldown
        if self.ai:
            self.ai.update_cooldown(dt)

    def to_dict(self) -> Dict[str, Any]:
        """Convert enemy entity to dictionary."""
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "health": self.health,
            "state": self.state,
            "patrol_dir": self.patrol_dir,
            "attack_cooldown": self.attack_cooldown,
            "dying_progress": self.dying_progress,
            "enemy_type": self.enemy_type,
            "weapon": self.weapon,
            "armor": self.armor,
            "armor_type": self.armor_type,
        }
