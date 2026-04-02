"""
System Registry - Manages and coordinates all game systems
"""

from typing import Dict, Any, Optional
from systems.base import ISystem
from systems.player_system import PlayerSystem
from systems.enemy_ai_system import EnemyAISystem
from systems.combat_system import CombatSystem
from physics.physics import Physics
from input import InputManager


class SystemRegistry:
    """
    Registry that holds and coordinates all game systems.

    The SystemRegistry is responsible for:
    - Registering and retrieving systems
    - Initializing systems with required dependencies
    - Updating all systems in the game loop

    Attributes:
        player_system: System handling player movement and input
        enemy_ai_system: System handling enemy AI behaviors
        combat_system: System handling combat mechanics
        physics: Physics engine for collision and raycasting
    """

    def __init__(self):
        """Initialize the system registry."""
        self._systems: Dict[str, ISystem] = {}
        self._state: Any = None
        self._physics: Optional[Physics] = None
        self._input_manager: Optional[InputManager] = None

    def initialize(
        self, state: Any, physics: Physics, input_manager: Optional[InputManager] = None
    ) -> None:
        """
        Initialize all systems with required dependencies.

        Args:
            state: GameState instance
            physics: Physics instance for collision detection
            input_manager: InputManager instance for input handling
        """
        self._state = state
        self._physics = physics
        self._input_manager = input_manager

        # Create and register all systems
        self.player_system = PlayerSystem(state, physics, input_manager)
        self.enemy_ai_system = EnemyAISystem(state, physics)
        self.combat_system = CombatSystem(state)

        self._systems["player"] = self.player_system
        self._systems["enemy_ai"] = self.enemy_ai_system
        self._systems["combat"] = self.combat_system

    def set_input_manager(self, input_manager: InputManager) -> None:
        """
        Set the input manager after initialization.

        Args:
            input_manager: InputManager instance to use
        """
        self._input_manager = input_manager
        if hasattr(self, "player_system"):
            self.player_system.set_input_manager(input_manager)

    def register(self, name: str, system: ISystem) -> None:
        """
        Register a system with the registry.

        Args:
            name: Name to register the system under
            system: System instance to register
        """
        self._systems[name] = system

    def get(self, name: str) -> Optional[ISystem]:
        """
        Get a system by name.

        Args:
            name: Name of the system to retrieve

        Returns:
            The system if found, None otherwise
        """
        return self._systems.get(name)

    def update_all(self, dt: float) -> None:
        """
        Update all registered systems.

        Systems are updated in a specific order to ensure
        proper game flow:
        1. Player system (movement)
        2. Enemy AI system (behaviors)
        3. Combat system (damage, effects)

        Args:
            dt: Delta time since last update in seconds
        """
        # Update each system in order
        for system in self._systems.values():
            system.update(dt)

    @property
    def systems(self) -> Dict[str, ISystem]:
        """Get all registered systems."""
        return self._systems

    def get_player_system(self) -> PlayerSystem:
        """Get the player system."""
        return self.player_system

    def get_enemy_ai_system(self) -> EnemyAISystem:
        """Get the enemy AI system."""
        return self.enemy_ai_system

    def get_combat_system(self) -> CombatSystem:
        """Get the combat system."""
        return self.combat_system

    def get_physics(self) -> Physics:
        """Get the physics instance."""
        return self._physics

    def get_input_manager(self) -> Optional[InputManager]:
        """Get the input manager instance."""
        return self._input_manager
