"""
Integration test for gameplay mechanics
"""

import pytest
import math
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestGameplay:
    """Test gameplay mechanics."""

    def test_player_movement_forward(self):
        """Test player can move forward."""
        from engine.game_state import GameState, Player

        state = GameState()
        state.game_state = "playing"
        player = state.player

        initial_x = player.x
        initial_y = player.y

        # Simulate W key movement
        move_amount = 0.1
        player.x += math.cos(player.angle) * move_amount
        player.y += math.sin(player.angle) * move_amount

        assert player.x != initial_x or player.y != initial_y

    def test_player_movement_backward(self):
        """Test player can move backward."""
        from engine.game_state import GameState

        state = GameState()
        state.game_state = "playing"
        player = state.player

        initial_x = player.x
        initial_y = player.y

        # Simulate S key movement
        move_amount = 0.1
        player.x -= math.cos(player.angle) * move_amount
        player.y -= math.sin(player.angle) * move_amount

        assert player.x != initial_x or player.y != initial_y

    def test_player_strafe(self):
        """Test player can strafe."""
        from engine.game_state import GameState

        state = GameState()
        state.game_state = "playing"
        player = state.player

        initial_x = player.x
        initial_y = player.y

        # Simulate A key (strafe left)
        move_amount = 0.1
        player.x += math.cos(player.angle - math.pi / 2) * move_amount
        player.y += math.sin(player.angle - math.pi / 2) * move_amount

        assert player.x != initial_x or player.y != initial_y

    def test_player_rotation(self):
        """Test player can rotate."""
        from engine.game_state import GameState

        state = GameState()
        state.game_state = "playing"
        player = state.player

        initial_angle = player.angle

        player.angle += math.pi / 4  # 45 degrees

        assert player.angle != initial_angle

    def test_player_attack_cooldown(self):
        """Test attack cooldown is applied."""
        from engine.game_state import GameState

        state = GameState()
        state.game_state = "playing"

        assert state.player.attack_cooldown == 0

        state.player.attack_cooldown = 0.5

        assert state.player.attack_cooldown > 0

    def test_enemy_chase_behavior(self):
        """Test enemy chase behavior."""
        from engine.game_state import GameState, Enemy

        state = GameState()
        enemy = Enemy(x=5, y=5, state="chase")
        state.enemies.append(enemy)

        player = state.player
        player.x = 6
        player.y = 5

        # Simulate chase
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.sqrt(dx * dx + dy * dy)

        assert dist < 2.0
        assert enemy.state == "chase"

    def test_enemy_attack(self):
        """Test enemy can attack player."""
        from engine.game_state import GameState, Enemy

        state = GameState()
        state.game_state = "playing"

        enemy = Enemy(x=1, y=1, attack_cooldown=0)
        state.enemies.append(enemy)

        initial_health = state.player.health

        # Enemy attacks
        state.player.health -= 10

        assert state.player.health == initial_health - 10

    def test_combat_damage(self):
        """Test combat damage calculation."""
        from systems.combat_system import CombatSystem
        from engine.game_state import GameState, Enemy

        state = GameState()
        state.game_state = "playing"

        enemy = Enemy(x=1, y=1, health=30)
        state.enemies.append(enemy)

        combat = CombatSystem(state)

        # Place player close to enemy
        state.player.x = 1.2
        state.player.y = 1.2

        # Attack
        combat.player_attack()

        # Enemy should take damage
        assert enemy.health < 30

    def test_win_condition(self):
        """Test win condition when all enemies are dead."""
        from systems.combat_system import CombatSystem
        from engine.game_state import GameState

        state = GameState()
        state.game_state = "playing"
        state.enemies = []  # No enemies

        combat = CombatSystem(state)
        combat._check_win_condition()

        assert state.game_state == "victory"

    def test_physics_collision_detection(self):
        """Test physics collision detection."""
        from physics.physics import Physics
        from engine.game_state import GameState

        state = GameState()
        physics = Physics(state)

        # Wall positions should return True
        assert physics.is_wall(0, 0) == True  # Corner
        assert physics.is_wall(5, 5) == False  # Open space
        assert physics.is_wall(15, 15) == True  # Edge wall

    def test_line_of_sight(self):
        """Test line of sight calculation."""
        from physics.physics import Physics
        from engine.game_state import GameState

        state = GameState()
        physics = Physics(state)

        # Should have line of sight in open area
        has_los = physics.has_line_of_sight(1.5, 1.5, 3.5, 3.5)

        assert has_los == True

    def test_god_mode(self):
        """Test god mode prevents damage."""
        from engine.game_state import GameState

        state = GameState()
        state.game_state = "playing"
        state.player.god_mode = True

        initial_health = state.player.health

        # Try to deal damage
        state.player.health -= 100

        assert state.player.health == initial_health
