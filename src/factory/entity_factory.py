"""
Entity Factory - creates game entities
"""

import math
import random
from typing import List

from engine.game_state import Enemy, EnemyType, Item, ItemType


class EntityFactory:
    """Factory for creating game entities."""

    # Enemy configurations
    ENEMY_CONFIGS = {
        "imp": {"health": 30, "weapon": "fists", "speed": 2.5, "damage": 10},
        "demon": {"health": 60, "weapon": "fists", "speed": 2.0, "damage": 15},
        "cacodemon": {"health": 100, "weapon": "fists", "speed": 1.5, "damage": 20},
    }

    @staticmethod
    def create_enemy(x: float, y: float, enemy_type: str = "imp") -> Enemy:
        """Create an enemy with the specified type."""
        config = EntityFactory.ENEMY_CONFIGS.get(
            enemy_type, EntityFactory.ENEMY_CONFIGS["imp"]
        )

        return Enemy(
            x=x,
            y=y,
            angle=0.0,
            health=config["health"],
            state="patrol",
            patrol_dir=random.random() * 2 * math.pi,
            enemy_type=enemy_type,
            weapon=config["weapon"],
        )

    @staticmethod
    def create_enemies_from_map(grid: List[str]) -> List[Enemy]:
        """Create enemies from map data."""
        enemies = []

        ENEMY_MAP = {
            "E": "imp",
            "D": "demon",
            "C": "cacodemon",
        }

        for y, row in enumerate(grid):
            for x, char in enumerate(row):
                if char in ENEMY_MAP:
                    enemy_type = ENEMY_MAP[char]
                    enemy = EntityFactory.create_enemy(x + 0.5, y + 0.5, enemy_type)
                    enemies.append(enemy)

        return enemies

    @staticmethod
    def create_item(x: float, y: float, item_type: str, value: int = 0) -> Item:
        """Create an item."""
        return Item(
            x=x,
            y=y,
            item_type=item_type,
            value=value,
            collected=False,
        )

    @staticmethod
    def create_health_pack(x: float, y: float, value: int = 25) -> Item:
        """Create a health pack."""
        return EntityFactory.create_item(x, y, ItemType.HEALTH_PACK, value)

    @staticmethod
    def create_ammo(x: float, y: float, weapon_type: str, value: int = 10) -> Item:
        """Create ammo for a specific weapon."""
        ammo_types = {
            "shotgun": ItemType.AMMO_SHOTGUN,
            "chaingun": ItemType.AMMO_CHAINGUN,
        }
        item_type = ammo_types.get(weapon_type, ItemType.AMMO_SHOTGUN)
        return EntityFactory.create_item(x, y, item_type, value)
