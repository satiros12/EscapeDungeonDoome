"""Tests for config and map loading - using new architecture"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

import pytest
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    PLAYER_SPEED,
    PLAYER_START_HEALTH,
    ENEMY_COUNT,
    ENEMY_HEALTH,
    ENEMY_SPEED,
    ATTACK_DAMAGE,
    ATTACK_RANGE,
    ATTACK_COOLDOWN,
    FOV,
    RAY_COUNT,
    MAX_DEPTH,
)
from engine.game_state import MapManager, ItemType, Item, Player


class TestConfig:
    """Test cases for config constants"""

    def test_screen_settings(self):
        """Screen settings should have valid values"""
        assert SCREEN_WIDTH == 800
        assert SCREEN_HEIGHT == 600
        assert FPS == 60

    def test_player_settings(self):
        """Player settings should have valid values"""
        assert PLAYER_SPEED > 0
        assert PLAYER_START_HEALTH > 0

    def test_enemy_settings(self):
        """Enemy settings should have valid values"""
        assert ENEMY_COUNT > 0
        assert ENEMY_HEALTH > 0
        assert ENEMY_SPEED > 0

    def test_combat_settings(self):
        """Combat settings should have valid values"""
        assert ATTACK_DAMAGE > 0
        assert ATTACK_RANGE > 0
        assert ATTACK_COOLDOWN > 0

    def test_raycasting_settings(self):
        """Raycasting settings should have valid values"""
        assert FOV > 0
        assert RAY_COUNT > 0
        assert MAX_DEPTH > 0


class TestMapManager:
    """Test cases for map selection in game state"""

    def test_map_manager_creation(self):
        """MapManager should initialize"""
        manager = MapManager()
        assert manager is not None

    def test_get_available_maps(self):
        """Should get list of available maps"""
        manager = MapManager()
        maps = manager.get_available_maps()

        assert len(maps) > 0
        assert "base" in maps

    def test_set_map(self):
        """Should set current map"""
        manager = MapManager()
        available = manager.get_available_maps()

        if len(available) > 1:
            new_map = available[1] if available[0] == "base" else available[0]
            result = manager.set_map(new_map)
            assert result is True
            assert manager._current_map == new_map

    def test_get_current_map(self):
        """Should get current map data"""
        manager = MapManager()
        map_data = manager.get_current_map()

        assert map_data is not None
        assert "grid" in map_data
        assert "name" in map_data


class TestItemTypes:
    """Test cases for item types"""

    def test_item_types_exist(self):
        """Should have all item types defined"""
        assert ItemType.HEALTH_PACK == "health_pack"
        assert ItemType.AMMO_SHOTGUN == "ammo_shotgun"
        assert ItemType.ARMOR_LIGHT == "armor_light"
        assert ItemType.ARMOR_HEAVY == "armor_heavy"

    def test_item_creation(self):
        """Should create items with correct properties"""
        item = Item(x=1.0, y=2.0, item_type="health_pack", value=25)
        assert item.x == 1.0
        assert item.y == 2.0
        assert item.item_type == "health_pack"
        assert item.value == 25
        assert item.collected == False


class TestPlayerFields:
    """Test cases for player fields"""

    def test_player_armor_fields(self):
        """Player should have armor and armor_type fields"""
        player = Player()
        assert hasattr(player, "armor")
        assert hasattr(player, "armor_type")
        assert player.armor == 0
        assert player.armor_type == "none"

    def test_player_ammo_fields(self):
        """Player should have ammo dictionary"""
        player = Player()
        assert hasattr(player, "ammo")
        assert isinstance(player.ammo, dict)


class TestMapLoading:
    """Test cases for loading maps from files"""

    @pytest.fixture
    def temp_maps_dir(self):
        """Create temporary maps directory"""
        maps_dir = tempfile.mkdtemp()

        map_data = {
            "name": "Test Map",
            "description": "A test map",
            "grid": ["####", "#P #", "##E#", "####"],
        }

        with open(os.path.join(maps_dir, "test.json"), "w") as f:
            json.dump(map_data, f)

        yield maps_dir

        # Cleanup
        import shutil

        shutil.rmtree(maps_dir)

    def test_load_maps_from_directory(self, temp_maps_dir):
        """Should load maps from directory"""
        # This tests the internal loading mechanism
        manager = MapManager()
        # The maps should be loaded on init
        assert manager.get_current_map() is not None
