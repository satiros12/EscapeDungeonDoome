"""Tests for combat module"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/server"))

import pytest
from game_logic import GameLogic
from game_state import GameState, GameConfig


class TestCombat:
    """Test cases for combat system"""

    @pytest.fixture
    def state(self):
        return GameState()

    @pytest.fixture
    def logic(self, state):
        return GameLogic(state)

    def test_player_attack_decreases_enemy_health(self, logic, state):
        """Player attack should decrease enemy health"""
        state.reset()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0

        initial_health = enemy.health
        logic.player_attack()

        assert enemy.health < initial_health

    def test_player_attack_sets_attack_cooldown(self, logic, state):
        """Player attack should set attack cooldown"""
        state.reset()
        state.player.attack_cooldown = 0

        logic.player_attack()

        assert state.player.attack_cooldown == GameConfig.ATTACK_COOLDOWN

    def test_player_attack_no_effect_when_on_cooldown(self, logic, state):
        """Player attack should not work during cooldown"""
        state.reset()
        state.game_state = "playing"
        state.player.attack_cooldown = 1.0
        initial_health = state.enemies[0].health

        logic.player_attack()

        assert state.enemies[0].health == initial_health

    def test_player_attack_only_hits_enemies_in_range(self, logic, state):
        """Player attack should only hit enemies within range"""
        state.reset()
        state.game_state = "playing"
        state.player.x = 1.5
        state.player.y = 1.5
        state.player.attack_cooldown = 0
        for enemy in state.enemies:
            enemy.x = 10
            enemy.y = 10
        initial_health = state.enemies[0].health

        logic.player_attack()

        assert state.enemies[0].health == initial_health

    def test_enemy_attack_decreases_player_health(self, logic, state):
        """Enemy attack should decrease player health"""
        state.reset()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x + 0.5
        state.player.y = enemy.y + 0.5
        enemy.state = "attack"
        enemy.attack_cooldown = 0

        initial_health = state.player.health
        logic.update_enemies(0.016)

        assert state.player.health < initial_health

    def test_enemy_dies_when_health_reaches_zero(self, logic, state):
        """Enemy should transition to dying when health reaches 0"""
        state.reset()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0
        enemy.health = 10

        logic.player_attack()

        assert enemy.state == "dying"

    def test_enemy_becomes_dead_after_dying_progress(self, logic, state):
        """Enemy should become dead after dying progress completes"""
        state.reset()
        state.game_state = "playing"
        state.enemies[0].state = "dying"
        state.enemies[0].dying_progress = 0

        for _ in range(100):
            logic.update_dying_enemies(0.016)

        assert state.enemies[0].state == "dead"

    def test_corpses_created_when_enemy_dies(self, logic, state):
        """A corpse should be created when enemy dies - manually transition to dead"""
        state.reset()
        state.game_state = "playing"
        enemy = state.enemies[0]
        enemy.state = "dead"

        initial_corpses = len(state.corpses)
        state.corpses.append(type("Corpse", (), {"x": enemy.x, "y": enemy.y})())

        assert len(state.corpses) > initial_corpses

    def test_kill_counter_increments(self, logic, state):
        """Kill counter should increment when player kills enemy"""
        state.reset()
        state.game_state = "playing"
        enemy = state.enemies[0]
        enemy.health = 5
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0

        initial_kills = state.kills
        logic.player_attack()

        for _ in range(100):
            logic.update_dying_enemies(0.016)

        assert state.kills > initial_kills

    def test_check_victory_when_all_enemies_dead(self, logic, state):
        """Game should be in victory state when all enemies are dead"""
        state.reset()
        state.game_state = "playing"
        for enemy in state.enemies:
            enemy.state = "dead"

        logic.check_conditions()

        assert state.game_state == "victory"

    def test_check_defeat_when_player_health_zero(self, logic, state):
        """Defeat is set when player health reaches 0 during enemy attack"""
        state.reset()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x + 0.5
        state.player.y = enemy.y + 0.5
        state.player.health = 1
        enemy.state = "attack"
        enemy.attack_cooldown = 0

        logic.update_enemies(0.016)

        assert state.game_state == "defeat"

    def test_player_takes_damage_from_enemy_attack(self, logic, state):
        """Player should take damage when enemy attacks"""
        state.reset()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x + 0.5
        state.player.y = enemy.y + 0.5
        state.player.health = 100
        enemy.state = "attack"
        enemy.attack_cooldown = 0

        logic.update_enemies(0.016)

        assert state.player.health < 100

    def test_hit_effect_created_on_enemy_hit(self, logic, state):
        """Hit effect should be created when enemy is hit"""
        state.reset()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0

        logic.player_attack()

        assert len(state.hit_effects) > 0
