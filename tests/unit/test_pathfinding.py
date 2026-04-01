"""Tests for the pathfinding module"""

import sys
import os

# Add server directory to path
SERVER_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "src",
    "server",
)
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

import pytest
from pathfinding import Pathfinding
from game_state import GameState


class TestPathfinding:
    """Test A* pathfinding implementation"""

    @pytest.fixture
    def pf(self):
        """Create pathfinding instance"""
        state = GameState()
        state.parse_map()
        return Pathfinding(state)

    def test_pathfinding_initialization(self, pf):
        """Test pathfinding initializes correctly"""
        assert pf is not None
        assert pf.state is not None

    def test_find_path_returns_list(self, pf):
        """Test find_path returns a list when path exists"""
        path = pf.find_path(1.5, 1.5, 3.5, 1.5)
        assert path is not None
        assert isinstance(path, list)
        assert len(path) > 0

    def test_find_path_direct(self, pf):
        """Test pathfinding finds direct route"""
        # Direct path from (1.5, 1.5) to (2.5, 1.5)
        path = pf.find_path(1.5, 1.5, 2.5, 1.5)
        assert path is not None
        # Should be very short
        assert len(path) <= 3

    def test_find_path_around_wall(self, pf):
        """Test pathfinding finds route around walls"""
        # From left side to right side of map
        path = pf.find_path(1.5, 1.5, 14.5, 1.5)
        assert path is not None
        # Path should be longer than direct (due to walls)
        assert len(path) > 2

    def test_find_path_no_path(self, pf):
        """Test find_path returns None when no path exists"""
        # Try to find path outside map bounds
        path = pf.find_path(1.5, 1.5, 100.0, 100.0)
        assert path is None

    def test_find_path_same_start_end(self, pf):
        """Test pathfinding with same start and end"""
        path = pf.find_path(5.5, 5.5, 5.5, 5.5)
        assert path is not None
        assert len(path) == 1

    def test_heuristic_manhattan(self, pf):
        """Test Manhattan distance heuristic"""
        a = (0, 0)
        b = (3, 4)
        h = pf._heuristic(a, b)
        assert h == 7  # 3 + 4

    def test_get_neighbors(self, pf):
        """Test neighbor generation"""
        node = (5, 5)
        neighbors = pf._get_neighbors(node)
        assert (6, 5) in neighbors
        assert (4, 5) in neighbors
        assert (5, 6) in neighbors
        assert (5, 4) in neighbors

    def test_is_valid_grid(self, pf):
        """Test grid validation"""
        assert pf._is_valid_grid((5, 5)) is True
        assert pf._is_valid_grid((-1, 5)) is False
        assert pf._is_valid_grid((5, -1)) is False
        assert pf._is_valid_grid((100, 100)) is False

    def test_is_walkable(self, pf):
        """Test walkable check"""
        # Center of floor tiles should be walkable
        assert pf._is_walkable((5, 5)) is True
        # Wall tiles should not be walkable
        assert pf._is_walkable((0, 0)) is False

    def test_get_next_path_node(self, pf):
        """Test getting next node in path"""
        path = [(1.5, 1.5), (2.5, 1.5), (3.5, 1.5)]
        next_node = pf.get_next_path_node(path, 1.5, 1.5)
        assert next_node is not None
        assert next_node == (2.5, 1.5)

    def test_get_next_path_node_none_when_close(self, pf):
        """Test get_next_path_node returns None when at end of path"""
        path = [(1.5, 1.5)]
        next_node = pf.get_next_path_node(path, 1.5, 1.5)
        assert next_node is None

    def test_has_line_of_sight(self, pf):
        """Test line of sight check"""
        # Direct line of sight
        assert pf.has_line_of_sight(1.5, 1.5, 3.5, 1.5) is True
        # Line of sight through a wall (using row 3 which has wall segments)
        # From (1.5, 3.5) to (10.5, 3.5) - there are walls between
        assert pf.has_line_of_sight(1.5, 3.5, 10.5, 3.5) is False

    def test_path_not_through_walls(self, pf):
        """Test that path doesn't go through walls"""
        # Map has walls at certain positions
        path = pf.find_path(1.5, 1.5, 14.5, 1.5)
        if path:
            for node in path:
                x, y = node
                # Check that path nodes are walkable
                assert pf._is_walkable((int(x), int(y))) is True
