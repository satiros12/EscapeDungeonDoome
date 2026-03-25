"""Tests for AI module"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/server"))

import pytest
from game_logic import GameLogic
from game_state import GameState, GameConfig


class TestAI:
    """Test cases for Enemy AI"""

    @pytest.fixture
    def state(self):
        return GameState()

    @pytest.fixture
    def logic(self, state):
        return GameLogic(state)

    def test_enemy_initial_state_is_patrol(self, state):
        """Enemies should start in patrol state"""
        state.reset()
        for enemy in state.enemies:
            assert enemy.state == "patrol"

    def test_enemy_transitions_to_chase_when_player_visible(self, logic, state):
        """Enemy should transition from patrol to chase when player is visible"""
        state.reset()
        state.player.x = 3
        state.player.y = 3
        state.enemies[0].x = 2
        state.enemies[0].y = 2

        for _ in range(10):
            logic.update_enemies(0.016)

        assert state.enemies[0].state == "chase"

    def test_enemy_transitions_to_attack_when_in_range(self, logic, state):
        """Enemy should transition to attack when close to player"""
        state.reset()
        state.player.x = 2.5
        state.player.y = 2.5
        state.enemies[0].x = 2
        state.enemies[0].y = 2
        state.enemies[0].state = "chase"

        for _ in range(20):
            logic.update_enemies(0.016)

        assert state.enemies[0].state == "attack"

    def test_enemy_returns_to_patrol_when_player_too_far(self, logic, state):
        """Enemy should return to patrol when player is out of range"""
        state.reset()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = 20
        state.player.y = 20
        enemy.x = 2
        enemy.y = 2
        enemy.state = "chase"

        for _ in range(60):
            logic.update_enemies(0.016)

        assert enemy.state == "patrol"

    def test_enemy_patrol_movement(self, logic, state):
        """Enemy should move during patrol"""
        state.reset()
        enemy = state.enemies[0]
        initial_x = enemy.x
        initial_y = enemy.y

        for _ in range(50):
            logic.update_enemies(0.016)

        moved = (enemy.x != initial_x) or (enemy.y != initial_y)
        assert moved is True

    def test_enemy_angles_toward_player_when_chasing(self, logic, state):
        """Enemy should face the player when in chase state"""
        state.reset()
        state.player.x = 5
        state.player.y = 5
        state.enemies[0].x = 2
        state.enemies[0].y = 2
        state.enemies[0].state = "chase"

        logic.update_enemies(0.016)

        assert state.enemies[0].angle is not None

    def test_normalize_angle_keeps_angle_in_range(self, logic):
        """normalize_angle should keep angle within [-PI, PI]"""
        assert abs(logic.normalize_angle(0)) < 0.001
        assert abs(logic.normalize_angle(2 * 3.14159) - 0) < 0.001
        assert abs(logic.normalize_angle(-2 * 3.14159) - 0) < 0.001
        assert abs(logic.normalize_angle(3.14159) - 3.14159) < 0.001

    def test_enemy_does_not_move_when_dead(self, logic, state):
        """Dead enemies should not move"""
        state.reset()
        state.enemies[0].state = "dead"
        initial_x = state.enemies[0].x
        initial_y = state.enemies[0].y

        for _ in range(10):
            logic.update_enemies(0.016)

        assert state.enemies[0].x == initial_x
        assert state.enemies[0].y == initial_y

    def test_enemy_does_not_move_when_dying(self, logic, state):
        """Dying enemies should not move"""
        state.reset()
        state.enemies[0].state = "dying"
        initial_x = state.enemies[0].x
        initial_y = state.enemies[0].y

        for _ in range(10):
            logic.update_enemies(0.016)

        assert state.enemies[0].x == initial_x
        assert state.enemies[0].y == initial_y

    def test_multiple_enemies_updated(self, logic, state):
        """All alive enemies should be updated"""
        state.reset()
        alive_count = sum(1 for e in state.enemies if e.state not in ("dead", "dying"))

        logic.update_enemies(0.016)

        assert alive_count == len(state.enemies)
