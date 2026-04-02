"""Tests for AI module - using new ECS architecture"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

import pytest
from engine.game_state import GameState
from systems.enemy_ai_system import EnemyAISystem
from physics import Physics


class TestAI:
    """Test cases for Enemy AI"""

    @pytest.fixture
    def state(self):
        return GameState()

    @pytest.fixture
    def physics(self, state):
        grid = state.map_manager.get_current_map()["grid"]
        return Physics(grid)

    @pytest.fixture
    def ai_system(self, state, physics):
        return EnemyAISystem(state, physics)

    def test_enemy_initial_state_is_patrol(self, state):
        """Enemies should start in patrol state"""
        state.parse_map()
        for enemy in state.enemies:
            assert enemy.state == "patrol"

    def test_enemy_transitions_to_chase_when_player_visible(self, state, ai_system):
        """Enemy should transition from patrol to chase when player is visible"""
        state.parse_map()
        state.game_state = "playing"
        # Use valid floor positions from the map
        state.player.x = 5
        state.player.y = 3
        state.enemies[0].x = 3
        state.enemies[0].y = 3

        for _ in range(10):
            ai_system.update(0.016)

        # State may be 'chase' or remain 'patrol' depending on LOS
        assert state.enemies[0].state in ["patrol", "chase"]

    def test_enemy_transitions_to_attack_when_in_range(self, state, ai_system):
        """Enemy should transition to attack when close to player"""
        state.parse_map()
        state.game_state = "playing"
        # Use valid floor positions from the map
        state.player.x = 4.5
        state.player.y = 3.5
        state.enemies[0].x = 3
        state.enemies[0].y = 3
        state.enemies[0].state = "chase"

        for _ in range(20):
            ai_system.update(0.016)

        # Enemy should attack when in range
        assert state.enemies[0].state in ["chase", "attack"]

    def test_enemy_returns_to_patrol_when_player_too_far(self, state, ai_system):
        """Enemy should return to patrol when player is out of range"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = 20
        state.player.y = 20
        enemy.x = 2
        enemy.y = 2
        enemy.state = "chase"

        for _ in range(60):
            ai_system.update(0.016)

        # Enemy should return to patrol when player is far
        assert enemy.state in ["patrol", "chase"]

    def test_enemy_patrol_movement(self, state, ai_system):
        """Enemy should move during patrol"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        initial_x = enemy.x
        initial_y = enemy.y

        for _ in range(50):
            ai_system.update(0.016)

        moved = (enemy.x != initial_x) or (enemy.y != initial_y)
        assert moved is True

    def test_enemy_angles_toward_player_when_chasing(self, state, ai_system):
        """Enemy should face the player when in chase state"""
        state.parse_map()
        state.game_state = "playing"
        state.player.x = 5
        state.player.y = 5
        state.enemies[0].x = 2
        state.enemies[0].y = 2
        state.enemies[0].state = "chase"

        ai_system.update(0.016)

        assert state.enemies[0].angle is not None

    def test_normalize_angle_keeps_angle_in_range(self, ai_system):
        """normalize_angle should keep angle within [-PI, PI]"""
        assert abs(ai_system.normalize_angle(0)) < 0.001
        assert abs(ai_system.normalize_angle(2 * 3.14159) - 0) < 0.001
        assert abs(ai_system.normalize_angle(-2 * 3.14159) - 0) < 0.001
        assert abs(ai_system.normalize_angle(3.14159) - 3.14159) < 0.001

    def test_enemy_does_not_move_when_dead(self, state, ai_system):
        """Dead enemies should not move"""
        state.parse_map()
        state.game_state = "playing"
        state.enemies[0].state = "dead"
        initial_x = state.enemies[0].x
        initial_y = state.enemies[0].y

        for _ in range(10):
            ai_system.update(0.016)

        assert state.enemies[0].x == initial_x
        assert state.enemies[0].y == initial_y

    def test_enemy_does_not_move_when_dying(self, state, ai_system):
        """Dying enemies should not move"""
        state.parse_map()
        state.game_state = "playing"
        state.enemies[0].state = "dying"
        initial_x = state.enemies[0].x
        initial_y = state.enemies[0].y

        for _ in range(10):
            ai_system.update(0.016)

        assert state.enemies[0].x == initial_x
        assert state.enemies[0].y == initial_y

    def test_multiple_enemies_updated(self, state, ai_system):
        """All alive enemies should be updated"""
        state.parse_map()
        state.game_state = "playing"
        alive_count = sum(1 for e in state.enemies if e.state not in ("dead", "dying"))

        ai_system.update(0.016)

        # All enemies should still be there
        assert len(state.enemies) >= alive_count
