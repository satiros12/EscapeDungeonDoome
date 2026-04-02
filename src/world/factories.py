"""
World Factory - Creates and configures World instances with core systems.
"""

from typing import Optional

from world.world import World
from systems.player_system import PlayerSystem
from systems.enemy_ai_system import EnemyAISystem
from systems.combat_system import CombatSystem
from engine.game_state import GameState
from physics.physics import Physics
from engine.event_system import EventSystem


class WorldFactory:
    """Factory for creating configured World instances."""

    @staticmethod
    def create_empty_world(event_system: Optional[EventSystem] = None) -> World:
        """
        Create an empty World without any systems.

        Args:
            event_system: Optional event system instance (uses global if None)

        Returns:
            A new empty World instance
        """
        return World(event_system=event_system)

    @staticmethod
    def create_game_world(
        state: GameState,
        physics: Physics,
        event_system: Optional[EventSystem] = None,
    ) -> World:
        """
        Create a World instance with core game systems.

        Creates a new World and adds the core systems required for gameplay:
        - PlayerSystem: Handles player movement and input
        - EnemyAISystem: Handles enemy AI behaviors
        - CombatSystem: Handles combat mechanics and damage

        Args:
            state: The GameState instance to use for game data
            physics: The Physics instance for collision detection
            event_system: Optional event system instance (uses global if None)

        Returns:
            A World instance configured with core game systems
        """
        world = World(event_system=event_system)

        # Create and add core systems
        player_system = PlayerSystem(state=state, physics=physics)
        enemy_ai_system = EnemyAISystem(state=state, physics=physics)
        combat_system = CombatSystem(state=state)

        world.add_system(player_system)
        world.add_system(enemy_ai_system)
        world.add_system(combat_system)

        return world
