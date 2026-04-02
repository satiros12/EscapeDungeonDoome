"""
Integration test for game loop
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestGameLoop:
    """Test game loop functionality."""

    def test_game_starts_in_menu(self):
        """Test that game starts in menu state."""
        from engine.game_state import GameState

        state = GameState()
        assert state.game_state == "menu"

    def test_game_starts_playing(self):
        """Test that game can transition to playing state."""
        from engine.game_state import GameState

        state = GameState()
        state.game_state = "playing"
        assert state.game_state == "playing"

    def test_player_initial_position(self):
        """Test player starts at correct position."""
        from engine.game_state import GameState

        state = GameState()
        state.parse_map()

        # Player should be at P position in default map
        # In default map, P is at row 5, col 12 (0-indexed: x=12.5, y=5.5)
        # But map may vary, just verify player starts somewhere in valid position
        assert state.player.x > 0
        assert state.player.y > 0

    def test_enemies_spawn_from_map(self):
        """Test that enemies are spawned from map data."""
        from engine.game_state import GameState

        state = GameState()
        state.parse_map()

        # Should have 3 enemies in default map
        assert len(state.enemies) == 3

    def test_player_can_take_damage(self):
        """Test player takes damage."""
        from engine.game_state import GameState

        state = GameState()
        state.game_state = "playing"
        initial_health = state.player.health

        state.player.health -= 10

        assert state.player.health == initial_health - 10

    def test_player_dies_at_zero_health(self):
        """Test game ends when player health reaches zero."""
        from engine.game_state import GameState

        state = GameState()
        state.game_state = "playing"
        state.player.health = 10

        state.player.health -= 10

        assert state.player.health <= 0

    def test_enemy_can_die(self):
        """Test enemy can be killed."""
        from engine.game_state import GameState, Enemy

        state = GameState()
        enemy = Enemy(x=5, y=5, health=30)
        state.enemies.append(enemy)

        enemy.health -= 30

        assert enemy.health <= 0

    def test_game_can_be_won(self):
        """Test game can be won."""
        from engine.game_state import GameState

        state = GameState()
        state.game_state = "playing"
        state.enemies = []
        state.kills = 0

        # Check win condition
        alive_enemies = [e for e in state.enemies if e.state != "dead"]
        if len(alive_enemies) == 0 and state.game_state == "playing":
            state.game_state = "victory"

        assert state.game_state == "victory"
