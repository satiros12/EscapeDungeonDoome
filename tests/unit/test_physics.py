"""Tests for physics module"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/server"))

import pytest
from physics import Physics
from game_state import GameState, GameConfig, MAP_DATA, MAP_WIDTH, MAP_HEIGHT


class TestPhysics:
    """Test cases for Physics class"""

    @pytest.fixture
    def state(self):
        return GameState()

    @pytest.fixture
    def physics(self, state):
        return Physics(state)

    def test_is_wall_returns_true_for_wall(self, physics):
        """is_wall should return True for wall positions"""
        assert physics.is_wall(0, 0) is True
        assert physics.is_wall(15, 15) is True

    def test_is_wall_returns_false_for_floor(self, physics):
        """is_wall should return False for floor positions"""
        assert physics.is_wall(1, 1) is False
        assert physics.is_wall(2, 2) is False
        assert physics.is_wall(5, 5) is False

    def test_is_wall_returns_true_for_out_of_bounds(self, physics):
        """is_wall should return True for out of bounds positions"""
        assert physics.is_wall(-1, 1) is True
        assert physics.is_wall(1, -1) is True
        assert physics.is_wall(MAP_WIDTH, 1) is True
        assert physics.is_wall(1, MAP_HEIGHT) is True

    def test_check_collision_returns_collision_status(self, physics):
        """check_collision should return True for wall collisions (with margin)"""
        assert physics.check_collision(0, 0) is True
        # Use position far from walls (middle of floor tile) to avoid margin collision
        assert physics.check_collision(1.5, 1.5) is False

    def test_has_line_of_sight_returns_true_when_clear(self, physics):
        """has_line_of_sight should return True when path is clear"""
        result = physics.has_line_of_sight(2, 2, 5, 5)
        assert result is True

    def test_has_line_of_sight_returns_false_when_blocked(self, physics):
        """has_line_of_sight should return False when blocked by wall"""
        result = physics.has_line_of_sight(1, 2, 14, 2)
        assert result is False

    def test_cast_ray_returns_distance_less_than_max_depth(self, physics):
        """cast_ray should return distance less than MAX_DEPTH when wall is within range"""
        result = physics.cast_ray(math.pi / 4, 4, 4)
        assert result["dist"] < GameConfig.MAX_DEPTH

    def test_cast_ray_returns_wall_distance(self, physics):
        """cast_ray should return distance to wall"""
        result = physics.cast_ray(0, 1.5, 1.5)
        assert result["dist"] < GameConfig.MAX_DEPTH

    def test_is_wall_center_of_tile(self, physics):
        """is_wall should correctly identify wall at center of tile"""
        assert physics.is_wall(0.5, 0.5) is True
        assert physics.is_wall(0.5, 14.5) is True

    def test_is_wall_edges_of_map(self, physics):
        """is_wall should handle edge cases of map"""
        assert physics.is_wall(MAP_WIDTH - 1, 1) is True
        assert physics.is_wall(1, MAP_HEIGHT - 1) is True
