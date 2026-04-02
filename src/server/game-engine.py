"""Game Engine - Main facade for game logic orchestration"""

import math
from game_state import GameState, GameConfig, Corpse
from physics import Physics
from systems.player_system import PlayerMovementSystem
from systems.enemy_ai_system import EnemyAISystem
from systems.combat_system import CombatSystem


class GameEngine:
    """Main game engine that orchestrates all systems"""

    def __init__(self, state: GameState = None):
        self.state = state or GameState()
        self.physics = Physics(self.state)
        
        self.player_system = PlayerMovementSystem(self.state, self.physics)
        self.enemy_system = EnemyAISystem(self.state, self.physics)
        self.combat_system = CombatSystem(self.state)
        
        self.logger = None

    def set_logger(self, logger):
        """Set logger callback"""
        self.logger = logger

    def log(self, msg: str, level: str = "INFO"):
        if self.logger:
            self.logger(msg, level)

    def update(self, dt: float) -> None:
        """Main game update - called every frame"""
        if self.state.game_state != "playing":
            return

        self.player_system.update(dt)
        self.enemy_system.update(dt)
        self.combat_system.update(dt)

    def player_attack(self) -> None:
        """Handle player attack action"""
        self.combat_system.player_attack()

    def reset(self) -> None:
        """Reset the game"""
        self.state.reset()

    def get_state(self) -> dict:
        """Get current game state as dictionary"""
        return self.state.to_dict()

    def set_input(self, keys: dict) -> None:
        """Set player input"""
        self.state.pending_input = keys
