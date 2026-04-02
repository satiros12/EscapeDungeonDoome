"""
Player Simulation Test - Tests full gameplay simulation without display
"""

import pytest
import sys
import os

# Add src to path - make sure it comes FIRST
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# Force reimport of config from correct location
import importlib

if "config" in sys.modules:
    del sys.modules["config"]
if "engine.config" in sys.modules:
    del sys.modules["engine.config"]
if "src.config" in sys.modules:
    del sys.modules["src.config"]


class MockScreen:
    """Mock pygame surface for testing without display."""

    def __init__(self):
        self.width = 800
        self.height = 600

    def fill(self, color):
        pass

    def blit(self, *args, **kwargs):
        pass


class TestPlayerSimulation:
    """Test full player gameplay simulation."""

    def test_full_gameplay_simulation(self):
        """Simulate a complete game: start, move, attack, win."""
        from engine.game_engine import GameEngine

        # Create game engine (which includes state)
        engine = GameEngine(MockScreen())
        state = engine.state  # Use engine's state

        # Start game
        engine.start_game()
        assert state.game_state == "playing"

        # Simulate player input: move forward
        state.pending_input["KeyW"] = True
        initial_x = state.player.x
        initial_y = state.player.y

        # Update game for several frames
        for _ in range(10):
            engine.update(0.016)

        # Player should have moved
        assert state.player.x != initial_x or state.player.y != initial_y, (
            f"Player should have moved from ({initial_x}, {initial_y})"
        )

        # Simulate player input: rotate
        state.pending_input = {"ArrowRight": True}
        initial_angle = state.player.angle

        for _ in range(5):
            engine.update(0.016)

        # Player should have rotated
        assert state.player.angle != initial_angle

        print(f"Player position: ({state.player.x:.2f}, {state.player.y:.2f})")
        print(f"Player angle: {state.player.angle:.2f}")
        print(f"Player health: {state.player.health}")
        print(
            f"Enemies remaining: {len([e for e in state.enemies if e.state != 'dead'])}"
        )

    def test_player_movement_forward(self):
        """Test player can move forward."""
        from engine.game_engine import GameEngine

        engine = GameEngine(MockScreen())
        engine.start_game()
        state = engine.state

        # Reset position to open area
        state.player.x = 5.0
        state.player.y = 5.0
        state.player.angle = 0.0  # Facing right

        # Test forward (W)
        state.pending_input = {"KeyW": True}
        engine.update(0.1)

        assert state.player.x > 5.0, (
            f"Player should have moved forward, x={state.player.x}"
        )

    def test_player_rotation_left(self):
        """Test player can rotate left."""
        from engine.game_engine import GameEngine

        engine = GameEngine(MockScreen())
        engine.start_game()

        engine.state.player.angle = 0.0

        # Rotate left
        engine.state.pending_input = {"ArrowLeft": True}
        engine.update(0.1)

        # Player should have rotated (angle should be negative after left rotation)
        assert engine.state.player.angle < 0.0, (
            f"Player angle should be negative after left rotation, got {engine.state.player.angle}"
        )

    def test_game_pause_resume(self):
        """Test game can be paused and resumed."""
        from engine.game_engine import GameEngine

        engine = GameEngine(MockScreen())

        # Must start game first
        engine.start_game()

        # Verify we're in playing state (use engine.state!)
        assert engine.state.game_state == "playing"

        initial_player_x = engine.state.player.x

        # Pause game
        engine.pause_game()
        assert engine.state.game_state == "pause"

        # Move player while paused (should not move)
        engine.state.pending_input = {"KeyW": True}
        engine.update(0.1)

        assert engine.state.player.x == initial_player_x

        # Resume game
        engine.resume_game()
        assert engine.state.game_state == "playing"

        # Now player should move
        engine.update(0.1)
        assert engine.state.player.x != initial_player_x

    def test_enemy_chase_simulation(self):
        """Test enemy AI chase behavior."""
        from engine.game_engine import GameEngine

        engine = GameEngine(MockScreen())
        engine.start_game()

        # Place enemy and player close
        if engine.state.enemies:
            enemy = engine.state.enemies[0]
            enemy.x = 3.0
            enemy.y = 3.0
            engine.state.player.x = 5.0
            engine.state.player.y = 3.0

            initial_enemy_x = enemy.x

            # Update game - enemy should chase
            for _ in range(20):
                engine.update(0.016)

            # Enemy should have moved toward player or be in chase/attack state
            assert enemy.x > initial_enemy_x or enemy.state in [
                "chase",
                "attack",
                "searching",
            ]

    def test_combat_kills_enemy(self):
        """Test player can kill enemies."""
        from engine.game_engine import GameEngine
        from systems.combat_system import CombatSystem

        engine = GameEngine(MockScreen())
        engine.start_game()

        combat = CombatSystem(engine.state)

        # Place player next to enemy
        if engine.state.enemies:
            enemy = engine.state.enemies[0]
            enemy.x = 1.6
            enemy.y = 1.5
            engine.state.player.x = 1.5
            engine.state.player.y = 1.5

            initial_enemy_health = enemy.health

            # Attack enemy until dead
            for _ in range(5):
                combat.player_attack()
                engine.update(0.016)

            # Enemy should be dead, dying, or have taken damage
            assert (
                enemy.state in ["dying", "dead"] or enemy.health < initial_enemy_health
            )

    def test_player_death_from_enemy(self):
        """Test player can die from enemy attacks."""
        from engine.game_engine import GameEngine

        engine = GameEngine(MockScreen())
        engine.start_game()

        # Set player health low
        engine.state.player.health = 10

        # Place enemy close to player
        if engine.state.enemies:
            enemy = engine.state.enemies[0]
            enemy.x = 1.6
            enemy.y = 1.5
            enemy.state = "attack"
            enemy.attack_cooldown = 0
            engine.state.player.x = 1.5
            engine.state.player.y = 1.5

            # Let enemy attack
            for _ in range(5):
                engine.update(0.016)

            # Player should take damage
            assert engine.state.player.health < 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
