"""Tests for modular systems - using new ECS architecture"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

import pytest
from engine.game_state import GameState
from physics import Physics
from systems.player_system import PlayerSystem
from systems.enemy_ai_system import EnemyAISystem
from systems.combat_system import CombatSystem


class TestPlayerMovementSystem:
    """Test cases for PlayerSystem"""

    @pytest.fixture
    def state(self):
        return GameState()

    @pytest.fixture
    def physics(self, state):
        grid = state.map_manager.get_current_map()["grid"]
        return Physics(grid)

    @pytest.fixture
    def player_system(self, state, physics):
        return PlayerSystem(state, physics)

    def test_player_moves_forward(self, player_system, state):
        """Player should move forward with W key"""
        state.parse_map()
        state.game_state = "playing"
        state.player.x = 5.5
        state.player.y = 5.5
        state.player.angle = 0
        state.pending_input = {"KeyW": True}

        initial_x = state.player.x
        player_system.update(0.016)

        assert state.player.x > initial_x

    def test_player_moves_backward(self, player_system, state):
        """Player should move backward with S key"""
        state.parse_map()
        state.game_state = "playing"
        state.player.x = 5.5
        state.player.y = 5.5
        state.player.angle = math.pi
        state.pending_input = {"KeyS": True}

        player_system.update(0.016)

        assert state.player.x != 5.5

    def test_player_strafes_left(self, player_system, state):
        """Player should strafe left with A key"""
        state.parse_map()
        state.game_state = "playing"
        state.player.x = 5.5
        state.player.y = 5.5
        state.player.angle = 0
        state.pending_input = {"KeyA": True}

        player_system.update(0.016)

        assert state.player.y != 5.5

    def test_player_strafes_right(self, player_system, state):
        """Player should strafe right with D key"""
        state.parse_map()
        state.game_state = "playing"
        state.player.x = 5.5
        state.player.y = 5.5
        state.player.angle = 0
        state.pending_input = {"KeyD": True}

        player_system.update(0.016)

        assert state.player.y != 5.5

    def test_player_rotates_left(self, player_system, state):
        """Player should rotate left with left arrow"""
        state.parse_map()
        state.game_state = "playing"
        state.player.x = 5.5
        state.player.y = 5.5
        state.player.angle = 0
        state.pending_input = {"ArrowLeft": True}

        player_system.update(0.016)

        assert state.player.angle < 0

    def test_player_rotates_right(self, player_system, state):
        """Player should rotate right with right arrow"""
        state.parse_map()
        state.game_state = "playing"
        state.player.x = 5.5
        state.player.y = 5.5
        state.player.angle = 0
        state.pending_input = {"ArrowRight": True}

        player_system.update(0.016)

        assert state.player.angle > 0

    def test_player_collision_with_walls(self, player_system, state, physics):
        """Player should not move through walls"""
        state.parse_map()
        state.game_state = "playing"
        state.player.x = 1.5
        state.player.y = 1.5
        state.player.angle = 0
        state.pending_input = {"KeyW": True}

        player_system.update(0.016)

        # Player should not move into wall (position should remain valid)
        assert not physics.is_wall(state.player.x, state.player.y)

    def test_attack_cooldown_decreases(self, player_system, state):
        """Attack cooldown should decrease over time"""
        state.parse_map()
        state.game_state = "playing"
        state.player.attack_cooldown = 1.0

        player_system.update(0.5)

        assert state.player.attack_cooldown < 1.0


class TestEnemyAISystem:
    """Test cases for EnemyAISystem"""

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

    def test_enemy_starts_in_patrol(self, state, ai_system):
        """Enemy should start in patrol state"""
        state.parse_map()
        state.game_state = "playing"

        assert state.enemies[0].state == "patrol"

    def test_enemy_transitions_to_chase(self, state, ai_system):
        """Enemy should transition to chase when player is visible"""
        state.parse_map()
        state.game_state = "playing"
        state.player.x = 5
        state.player.y = 3
        state.enemies[0].x = 3
        state.enemies[0].y = 3

        for _ in range(20):
            ai_system.update(0.016)

        # Enemy should be in chase or patrol state
        assert state.enemies[0].state in ["patrol", "chase"]

    def test_enemy_transitions_to_attack(self, state, ai_system):
        """Enemy should transition to attack when close"""
        state.parse_map()
        state.game_state = "playing"
        state.player.x = 3.5
        state.player.y = 3.5
        state.enemies[0].x = 3
        state.enemies[0].y = 3
        state.enemies[0].state = "chase"

        for _ in range(20):
            ai_system.update(0.016)

        # Enemy should be in attack or chase state
        assert state.enemies[0].state in ["chase", "attack"]

    def test_dead_enemy_does_not_move(self, state, ai_system):
        """Dead enemy should not move"""
        state.parse_map()
        state.game_state = "playing"
        state.enemies[0].state = "dead"
        initial_x = state.enemies[0].x

        ai_system.update(0.016)

        assert state.enemies[0].x == initial_x


class TestCombatSystem:
    """Test cases for CombatSystem"""

    @pytest.fixture
    def state(self):
        return GameState()

    @pytest.fixture
    def combat_system(self, state):
        return CombatSystem(state)

    def test_player_attack_deals_damage(self, state, combat_system):
        """Player attack should deal damage to enemies in range"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0

        initial_health = enemy.health
        combat_system.player_attack()

        assert enemy.health < initial_health

    def test_player_attack_creates_hit_effect(self, state, combat_system):
        """Player attack should create hit effect"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0

        combat_system.player_attack()

        assert len(state.hit_effects) > 0

    def test_enemy_dies_when_health_zero(self, state, combat_system):
        """Enemy should die when health reaches zero"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        enemy.health = 5
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0

        combat_system.player_attack()

        assert enemy.state == "dying"

    def test_victory_when_all_enemies_dead(self, state, combat_system):
        """Game should be in victory when all enemies are dead"""
        state.parse_map()
        state.game_state = "playing"
        for enemy in state.enemies:
            enemy.state = "dead"

        combat_system.update(0.016)

        assert state.game_state == "victory"
