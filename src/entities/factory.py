"""
Entity Factory - Creates entities from map data
"""

import random
from typing import List, Dict, Any, Optional
from entities.base import Entity
from entities.player import PlayerEntity
from entities.enemy import EnemyEntity


class EntityFactory:
    """
    Factory for creating game entities.

    The EntityFactory is responsible for:
    - Creating player entities
    - Creating enemy entities from map data
    - Managing entity IDs
    """

    # Mapping from map characters to enemy types
    ENEMY_TYPE_MAP = {
        "E": "imp",
        "D": "demon",
        "C": "cacodemon",
    }

    def __init__(self):
        """Initialize the entity factory."""
        self._entity_counter: int = 0

    def create_player(self, entity_id: str = "player") -> PlayerEntity:
        """
        Create a player entity.

        Args:
            entity_id: Optional custom ID for the player

        Returns:
            A new PlayerEntity instance
        """
        return PlayerEntity(entity_id)

    def create_enemy(
        self, enemy_type: str, x: float, y: float, entity_id: str = None
    ) -> EnemyEntity:
        """
        Create an enemy entity.

        Args:
            enemy_type: Type of enemy (imp, demon, cacodemon)
            x: X position
            y: Y position
            entity_id: Optional custom ID (auto-generated if not provided)

        Returns:
            A new EnemyEntity instance
        """
        if entity_id is None:
            entity_id = f"enemy_{self._entity_counter}"
            self._entity_counter += 1

        return EnemyEntity(entity_id, enemy_type, x, y)

    def create_enemies_from_map(self, map_data: List[str]) -> List[EnemyEntity]:
        """
        Create enemy entities from map data.

        Parses the map grid and creates enemies at positions
        marked by enemy characters.

        Args:
            map_data: List of strings representing the map grid

        Returns:
            List of created EnemyEntity instances
        """
        enemies: List[EnemyEntity] = []
        height = len(map_data)

        for y in range(height):
            if y >= len(map_data):
                continue

            row = map_data[y]
            width = len(row)

            for x in range(width):
                if x >= len(row):
                    continue

                char = row[x]

                if char in self.ENEMY_TYPE_MAP:
                    enemy_type = self.ENEMY_TYPE_MAP[char]
                    enemy = self.create_enemy(
                        enemy_type=enemy_type, x=x + 0.5, y=y + 0.5
                    )
                    enemies.append(enemy)

        return enemies

    def create_enemy_at_position(
        self, char: str, x: float, y: float
    ) -> Optional[EnemyEntity]:
        """
        Create an enemy at a specific position based on map character.

        Args:
            char: Map character (E, D, C, etc.)
            x: X position
            y: Y position

        Returns:
            EnemyEntity if character maps to an enemy type, None otherwise
        """
        if char not in self.ENEMY_TYPE_MAP:
            return None

        enemy_type = self.ENEMY_TYPE_MAP[char]
        return self.create_enemy(enemy_type, x, y)

    def reset(self) -> None:
        """Reset the entity counter."""
        self._entity_counter = 0
