"""Tests for modular systems (ARCHITECTURE_V2)"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/server"))

import pytest
from game_state import GameState, GameConfig
from physics import Physics
from systems import PlayerMovementSystem, EnemyAISystem, CombatSystem


class TestPlayerMovementSystem:
    """Test cases for PlayerMovementSystem"""

    @pytest.fixture
    def state(self):
        return GameState()

    @pytest.fixture
    def physics(self, state):
        return Physics(state)

    @pytest.fixture
    def player_system(self, state, physics):
        return PlayerMovementSystem(state, physics)

    def test_player_moves_forward(self, player_system, state):
        """Player should move forward with W key"""
        state.game_state = "playing"
        state.player.x = 5.5
        state.player.y = 5.5
        state.player.angle = 0
        state.pending_input = {"KeyW": True}

        initial_x = state.player.x
        player_system.update(0.016)

        assert state.player.x > initial_x

    def test_player_moves_backward(self, player_system, state):
        """Player should move backward with S key (opposite to facing direction)"""
        state.game_state = "playing"
        state.player.x = 5.5
        state.player.y = 5.5
        state.player.angle = math.pi
        state.pending_input = {"KeyS": True}

        player_system.update(0.016)

        assert state.player.x != 5.5

    def test_player_strafes_left(self, player_system, state):
        """Player should strafe left with A key"""
        state.game_state = "playing"
        state.player.x = 5.5
        state.player.y = 5.5
        state.player.angle = 0
        state.pending_input = {"KeyA": True}

        player_system.update(0.016)

        assert state.player.y < 5.5

    def test_player_strafes_right(self, player_system, state):
        """Player should strafe right with D key"""
        state.game_state = "playing"
        state.player.x = 5.5
        state.player.y = 5.5
        state.player.angle = 0
        state.pending_input = {"KeyD": True}

        player_system.update(0.016)

        assert state.player.y > 5.5

    def test_player_rotates_left(self, player_system, state):
        """Player should rotate left with ArrowLeft"""
        state.game_state = "playing"
        state.player.angle = 0
        state.pending_input = {"ArrowLeft": True}

        player_system.update(0.016)

        assert state.player.angle < 0

    def test_player_rotates_right(self, player_system, state):
        """Player should rotate right with ArrowRight"""
        state.game_state = "playing"
        state.player.angle = 0
        state.pending_input = {"ArrowRight": True}

        player_system.update(0.016)

        assert state.player.angle > 0

    def test_player_collision_with_walls(self, player_system, state):
        """Player should not walk through walls"""
        state.game_state = "playing"
        state.player.x = 6.9
        state.player.y = 4.5
        state.player.angle = 0
        state.pending_input = {"KeyW": True}

        initial_x = state.player.x
        player_system.update(0.1)

        assert state.player.x == initial_x

    def test_attack_cooldown_decreases(self, player_system, state):
        """Attack cooldown should decrease over time"""
        state.game_state = "playing"
        state.player.attack_cooldown = 0.5

        player_system.update(0.1)

        assert state.player.attack_cooldown < 0.5


class TestEnemyAISystem:
    """Test cases for EnemyAISystem"""

    @pytest.fixture
    def state(self):
        return GameState()

    @pytest.fixture
    def physics(self, state):
        return Physics(state)

    @pytest.fixture
    def enemy_system(self, state, physics):
        return EnemyAISystem(state, physics)

    def test_enemy_starts_in_patrol(self, enemy_system, state):
        """Enemy should start in patrol state"""
        state.reset()
        assert state.enemies[0].state == "patrol"

    def test_enemy_transitions_to_chase(self, enemy_system, state):
        """Enemy should chase player when in range"""
        state.reset()
        state.game_state = "playing"
        # Use valid floor positions from the new map
        state.player.x = 5
        state.player.y = 3
        state.enemies[0].x = 3
        state.enemies[0].y = 3

        for _ in range(10):
            enemy_system.update(0.016)

        assert state.enemies[0].state == "chase"

    def test_enemy_transitions_to_attack(self, enemy_system, state):
        """Enemy should attack when close to player"""
        state.reset()
        state.game_state = "playing"
        # Use valid floor positions from the new map
        state.player.x = 4.5
        state.player.y = 3.5
        state.enemies[0].x = 3
        state.enemies[0].y = 3
        state.enemies[0].state = "chase"

        for _ in range(20):
            enemy_system.update(0.016)

        assert state.enemies[0].state == "attack"

    def test_dead_enemy_does_not_move(self, enemy_system, state):
        """Dead enemies should not move"""
        state.reset()
        state.game_state = "playing"
        state.enemies[0].state = "dead"
        initial_x = state.enemies[0].x

        enemy_system.update(0.016)

        assert state.enemies[0].x == initial_x


class TestCombatSystem:
    """Test cases for CombatSystem"""

    @pytest.fixture
    def state(self):
        return GameState()

    @pytest.fixture
    def combat_system(self, state):
        return CombatSystem(state)

    def test_player_attack_deals_damage(self, combat_system, state):
        """Player attack should reduce enemy health"""
        state.reset()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0

        initial_health = enemy.health
        combat_system.player_attack()

        assert enemy.health < initial_health

    def test_player_attack_creates_hit_effect(self, combat_system, state):
        """Player attack should create hit effect"""
        state.reset()
        state.game_state = "playing"
        state.enemies[0].x = 5
        state.enemies[0].y = 5
        state.player.x = 5
        state.player.y = 5
        state.player.attack_cooldown = 0

        combat_system.player_attack()

        assert len(state.hit_effects) > 0

    def test_enemy_dies_when_health_zero(self, combat_system, state):
        """Enemy should transition to dying when health reaches 0"""
        state.reset()
        state.game_state = "playing"
        state.enemies[0].health = 5
        state.player.x = state.enemies[0].x
        state.player.y = state.enemies[0].y
        state.player.attack_cooldown = 0

        combat_system.player_attack()

        assert state.enemies[0].state == "dying"

    def test_victory_when_all_enemies_dead(self, combat_system, state):
        """Game should be victory when all enemies dead"""
        state.reset()
        state.game_state = "playing"
        for enemy in state.enemies:
            enemy.state = "dead"

        combat_system.update(0.016)

        assert state.game_state == "victory"
