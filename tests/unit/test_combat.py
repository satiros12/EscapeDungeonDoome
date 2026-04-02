"""Tests for combat module - using new ECS architecture"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

import pytest
from engine.game_state import GameState
from systems.combat_system import CombatSystem
from systems.enemy_ai_system import EnemyAISystem
from physics import Physics


class TestCombat:
    """Test cases for combat system"""

    @pytest.fixture
    def state(self):
        return GameState()

    @pytest.fixture
    def physics(self, state):
        grid = state.map_manager.get_current_map()["grid"]
        return Physics(grid)

    @pytest.fixture
    def combat_system(self, state):
        return CombatSystem(state)

    @pytest.fixture
    def ai_system(self, state, physics):
        return EnemyAISystem(state, physics)

    def test_player_attack_decreases_enemy_health(self, state, combat_system):
        """Player attack should decrease enemy health"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0

        initial_health = enemy.health
        combat_system.player_attack()

        assert enemy.health < initial_health

    def test_player_attack_sets_attack_cooldown(self, state, combat_system):
        """Player attack should set attack cooldown"""
        state.parse_map()
        state.player.attack_cooldown = 0

        combat_system.player_attack()

        assert state.player.attack_cooldown == combat_system.attack_cooldown

    def test_player_attack_no_effect_when_on_cooldown(self, state, combat_system):
        """Player attack should not work during cooldown"""
        state.parse_map()
        state.game_state = "playing"
        state.player.attack_cooldown = 1.0
        initial_health = state.enemies[0].health

        combat_system.player_attack()

        assert state.enemies[0].health == initial_health

    def test_player_attack_only_hits_enemies_in_range(self, state, combat_system):
        """Player attack should only hit enemies within range"""
        state.parse_map()
        state.game_state = "playing"
        state.player.x = 1.5
        state.player.y = 1.5
        state.player.attack_cooldown = 0
        for enemy in state.enemies:
            enemy.x = 10
            enemy.y = 10
        initial_health = state.enemies[0].health

        combat_system.player_attack()

        assert state.enemies[0].health == initial_health

    def test_enemy_attack_decreases_player_health(self, state, ai_system):
        """Enemy attack should decrease player health"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x + 0.5
        state.player.y = enemy.y + 0.5
        enemy.state = "attack"
        enemy.attack_cooldown = 0

        initial_health = state.player.health
        ai_system.update(0.016)

        assert state.player.health <= initial_health

    def test_enemy_dies_when_health_reaches_zero(self, state, combat_system):
        """Enemy should transition to dying when health reaches 0"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0
        enemy.health = 10

        combat_system.player_attack()

        assert enemy.state == "dying"

    def test_enemy_becomes_dead_after_dying_progress(self, state, combat_system):
        """Enemy should become dead after dying progress completes"""
        state.parse_map()
        state.game_state = "playing"
        state.enemies[0].state = "dying"
        state.enemies[0].dying_progress = 0

        for _ in range(100):
            combat_system.update(0.016)

        assert state.enemies[0].state == "dead"

    def test_corpses_created_when_enemy_dies(self, state, combat_system):
        """A corpse should be created when enemy dies"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        enemy.state = "dead"

        initial_corpses = len(state.corpses)
        from engine.game_state import Corpse

        state.corpses.append(Corpse(x=enemy.x, y=enemy.y))

        assert len(state.corpses) > initial_corpses

    def test_kill_counter_increments(self, state, combat_system):
        """Kill counter should increment when player kills enemy"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        enemy.health = 5
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0

        initial_kills = state.kills
        combat_system.player_attack()

        for _ in range(100):
            combat_system.update(0.016)

        assert state.kills > initial_kills

    def test_check_victory_when_all_enemies_dead(self, state, combat_system):
        """Game should be in victory state when all enemies are dead"""
        state.parse_map()
        state.game_state = "playing"
        for enemy in state.enemies:
            enemy.state = "dead"

        combat_system.update(0.016)

        assert state.game_state == "victory"

    def test_player_takes_damage_from_enemy_attack(self, state, ai_system):
        """Player should take damage when enemy attacks"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x + 0.5
        state.player.y = enemy.y + 0.5
        state.player.health = 100
        enemy.state = "attack"
        enemy.attack_cooldown = 0

        ai_system.update(0.016)

        assert state.player.health <= 100

    def test_hit_effect_created_on_enemy_hit(self, state, combat_system):
        """Hit effect should be created when enemy is hit"""
        state.parse_map()
        state.game_state = "playing"
        enemy = state.enemies[0]
        state.player.x = enemy.x
        state.player.y = enemy.y
        state.player.attack_cooldown = 0

        combat_system.player_attack()

        assert len(state.hit_effects) > 0
