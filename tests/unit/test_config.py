"""Tests for config and map loading"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/server"))

import pytest
from config import ConfigLoader, MapData, load_config


class TestConfigLoader:
    """Test cases for ConfigLoader"""

    @pytest.fixture
    def temp_config(self):
        """Create a temporary config file"""
        config_data = {
            "game": {
                "player_health": 100,
                "enemy_health": 30
            },
            "rendering": {
                "fov": 1.0,
                "num_rays": 320
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            return f.name

    @pytest.fixture
    def temp_maps(self, temp_config):
        """Create temporary maps directory"""
        maps_dir = tempfile.mkdtemp()
        
        map1 = {
            "name": "Test Map",
            "grid": ["####", "#P##", "##E#", "####"]
        }
        
        with open(os.path.join(maps_dir, 'test.json'), 'w') as f:
            json.dump(map1, f)
        
        return maps_dir

    def test_load_config(self, temp_config):
        """Config should load from JSON file"""
        loader = ConfigLoader(temp_config)
        
        assert loader.get_config('game.player_health') == 100
        assert loader.get_config('rendering.num_rays') == 320

    def test_load_maps(self, temp_maps):
        """Maps should load from directory"""
        loader = ConfigLoader()
        loader.load_maps(temp_maps)
        
        assert 'test_map' in loader.get_map_names()

    def test_get_game_config(self, temp_config):
        """Should get game config section"""
        loader = ConfigLoader(temp_config)
        
        game_config = loader.get_game_config()
        assert game_config['player_health'] == 100

    def test_get_map(self):
        """Should get map by name"""
        loader = ConfigLoader()
        maps_dir = os.path.join(os.path.dirname(__file__), '../../../maps')
        
        if os.path.exists(maps_dir):
            loader.load_maps(maps_dir)
            map_data = loader.get_map('base')
            assert map_data is not None
        else:
            pytest.skip("Maps directory not found")


class TestMapData:
    """Test cases for MapData"""

    def test_player_start_finding(self):
        """Should find player start position"""
        grid = [
            "####",
            "#P #",
            "##E#",
            "####"
        ]
        
        map_data = MapData("Test", "Desc", 4, 4, grid)
        assert map_data.player_start == (1.5, 1.5)

    def test_default_player_start(self):
        """Should return default if no player found"""
        grid = [
            "####",
            "#  #",
            "##E#",
            "####"
        ]
        
        map_data = MapData("Test", "Desc", 4, 4, grid)
        assert map_data.player_start == (1.5, 1.5)

    def test_enemy_positions(self):
        """Should find all enemy positions"""
        grid = [
            "####",
            "#P #",
            "##E#",
            "#E##"
        ]
        
        map_data = MapData("Test", "Desc", 4, 4, grid)
        positions = map_data.enemy_positions
        
        assert len(positions) == 2
        assert (2.5, 2.5) in positions
        assert (1.5, 3.5) in positions


class TestMapManager:
    """Test cases for map selection in game state"""

    def test_map_manager_creation(self):
        """MapManager should initialize"""
        from game_state import MapManager
        
        manager = MapManager()
        assert manager is not None

    def test_get_available_maps(self):
        """Should get list of available maps"""
        from game_state import MapManager
        
        manager = MapManager()
        maps = manager.get_available_maps()
        
        assert len(maps) > 0

    def test_get_next_map(self):
        """Should get next map in carousel"""
        from game_state import MapManager
        
        manager = MapManager()
        initial = manager.get_map_index()
        next_map = manager.get_next_map()
        
        assert next_map in manager.get_available_maps()

    def test_get_prev_map(self):
        """Should get previous map in carousel"""
        from game_state import MapManager
        
        manager = MapManager()
        prev_map = manager.get_prev_map()
        
        assert prev_map in manager.get_available_maps()

    def test_set_map(self):
        """Should set current map"""
        from game_state import MapManager
        
        manager = MapManager()
        available = manager.get_available_maps()
        
        if len(available) > 1:
            new_map = available[1] if available[0] == available[0] else available[0]
            result = manager.set_map(new_map)
            assert result is True
            assert manager._current_map == new_map
