"""Game state data classes for WebDoom server"""

import math
import os
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

import json

_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_SERVER_DIR))
_SHARED_DIR = os.path.join(_PROJECT_ROOT, "shared")
_MAPS_DIR = os.path.join(_PROJECT_ROOT, "maps")
sys.path.insert(0, _SHARED_DIR)

from constants import GameConfig


class ItemType(Enum):
    HEALTH_PACK = "health_pack"
    AMMO_SHOTGUN = "ammo_shotgun"
    AMMO_CHAINGUN = "ammo_chaingun"
    WEAPON_FISTS = "weapon_fists"
    WEAPON_SWORD = "weapon_sword"
    WEAPON_AXE = "weapon_axe"
    ARMOR_LIGHT = "armor_light"
    ARMOR_HEAVY = "armor_heavy"


@dataclass
class Item:
    x: float
    y: float
    item_type: str
    value: int = 0
    collected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "item_type": self.item_type,
            "value": self.value,
            "collected": self.collected,
        }


DEFAULT_MAP_DATA = [
    "################",
    "#              #",
    "#   E    #     #",
    "#        #     #",
    "#      ###     #",
    "#      # P     #",
    "#          E   #",
    "#    ###       #",
    "#    #         #",
    "#    #    #    #",
    "#        #     #",
    "#   ###        #",
    "#          E   #",
    "#              #",
    "#              #",
    "################",
]

MAP_DATA = DEFAULT_MAP_DATA
MAP_WIDTH = len(MAP_DATA[0])
MAP_HEIGHT = len(MAP_DATA)


class MapManager:
    def __init__(self):
        self._maps: Dict[str, Dict] = {}
        self._current_map: str = "base"
        self._available_maps: List[str] = []
        self._load_maps()

    def _load_maps(self):
        """Load all maps from maps directory"""
        self._available_maps = ["base"]
        self._maps["base"] = {
            "name": "Base Map",
            "grid": DEFAULT_MAP_DATA,
            "width": 16,
            "height": 16,
            "description": "Classic starting map",
        }

        if not os.path.exists(_MAPS_DIR):
            return

        for filename in os.listdir(_MAPS_DIR):
            if filename.endswith(".json"):
                map_path = os.path.join(_MAPS_DIR, filename)
                try:
                    with open(map_path, "r") as f:
                        map_data = json.load(f)
                        map_name = (
                            map_data.get("name", filename[:-5])
                            .lower()
                            .replace(" ", "_")
                        )
                        # Add default values for new fields
                        if "goal" not in map_data:
                            map_data["goal"] = None
                        if "items" not in map_data:
                            map_data["items"] = []
                        self._maps[map_name] = map_data
                        if map_name not in self._available_maps:
                            self._available_maps.append(map_name)
                except Exception as e:
                    print(f"Error loading map {filename}: {e}")

    def get_current_map(self) -> Dict:
        """Get current map data"""
        return self._maps.get(
            self._current_map, self._maps.get("base", {"grid": DEFAULT_MAP_DATA})
        )

    def set_map(self, map_name: str) -> bool:
        """Set current map by name"""
        normalized = map_name.lower().replace(" ", "_")
        if normalized in self._maps:
            self._current_map = normalized
            return True
        return False

    def get_available_maps(self) -> List[str]:
        """Get list of available map names"""
        return self._available_maps

    def get_map_index(self) -> int:
        """Get current map index"""
        return (
            self._available_maps.index(self._current_map)
            if self._current_map in self._available_maps
            else 0
        )

    def get_next_map(self) -> str:
        """Get next map in carousel"""
        if not self._available_maps:
            return "base"
        idx = self.get_map_index()
        return self._available_maps[(idx + 1) % len(self._available_maps)]

    def get_prev_map(self) -> str:
        """Get previous map in carousel"""
        if not self._available_maps:
            return "base"
        idx = self.get_map_index()
        return self._available_maps[(idx - 1) % len(self._available_maps)]

    def get_map_data(self, map_name: str) -> Optional[Dict]:
        """Get map data by name"""
        normalized = map_name.lower().replace(" ", "_")
        return self._maps.get(normalized)


import json


@dataclass
class Player:
    x: float = 1.5
    y: float = 1.5
    angle: float = 0.0
    health: int = GameConfig.PLAYER_MAX_HEALTH
    attack_cooldown: float = 0
    god_mode: bool = False
    speed_multiplier: float = 1.0
    current_weapon: str = "fists"
    ammo: Dict[str, int] = field(
        default_factory=lambda: {"shotgun": 50, "chaingun": 200}
    )
    armor: int = 0
    armor_type: str = "none"  # "none", "light", "heavy"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "health": self.health,
            "attack_cooldown": self.attack_cooldown,
            "god_mode": self.god_mode,
            "speed_multiplier": self.speed_multiplier,
            "current_weapon": self.current_weapon,
            "ammo": self.ammo,
            "armor": self.armor,
            "armor_type": self.armor_type,
        }

    def reset(self):
        self.x = 1.5
        self.y = 1.5
        self.angle = 0.0
        self.health = GameConfig.PLAYER_MAX_HEALTH
        self.attack_cooldown = 0
        self.current_weapon = "fists"
        self.ammo = {"shotgun": 50, "chaingun": 200}
        self.armor = 0
        self.armor_type = "none"


@dataclass
class Enemy:
    x: float
    y: float
    angle: float = 0.0
    health: int = GameConfig.ENEMY_MAX_HEALTH
    state: str = "patrol"
    patrol_dir: float = 0.0
    attack_cooldown: float = 0
    dying_progress: float = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "health": self.health,
            "state": self.state,
            "patrol_dir": self.patrol_dir,
            "attack_cooldown": self.attack_cooldown,
            "dying_progress": self.dying_progress,
        }


@dataclass
class Corpse:
    x: float
    y: float

    def to_dict(self) -> Dict[str, Any]:
        return {"x": self.x, "y": self.y}


@dataclass
class HitEffect:
    x: float
    y: float
    timer: float = 0.3

    def to_dict(self) -> Dict[str, Any]:
        return {"x": self.x, "y": self.y, "timer": self.timer}


@dataclass
class GameState:
    game_state: str = "menu"
    player: Player = field(default_factory=Player)
    enemies: List[Enemy] = field(default_factory=list)
    corpses: List[Corpse] = field(default_factory=list)
    kills: int = 0
    hit_effects: List["HitEffect"] = field(default_factory=list)
    pending_input: Dict[str, bool] = field(default_factory=dict)
    player_speed_multiplier: float = 1.0
    current_map: str = "base"
    goal: Optional[tuple] = None  # (x, y) position
    goal_reached: bool = False
    items: List[Item] = field(default_factory=list)

    def __post_init__(self):
        self.map_manager = MapManager()

    def parse_map(self, map_data: List[str] = None):
        """Parse map and spawn entities"""
        self.player = Player()
        self.enemies = []
        self.corpses = []
        self.kills = 0
        self.hit_effects = []
        self.goal = None
        self.goal_reached = False
        self.items = []

        # Get map info from map manager for items and goal
        map_info = self.map_manager.get_current_map()

        if map_data is None:
            map_data = map_info.get("grid", MAP_DATA)

        height = len(map_data)
        width = len(map_data[0]) if height > 0 else 0

        for y in range(height):
            for x in range(width):
                if y >= len(map_data) or x >= len(map_data[y]):
                    continue
                char = map_data[y][x]
                if char == "P":
                    self.player.x = x + 0.5
                    self.player.y = y + 0.5
                elif char == "E":
                    self.enemies.append(
                        Enemy(
                            x=x + 0.5,
                            y=y + 0.5,
                            angle=0.0,
                            health=GameConfig.ENEMY_MAX_HEALTH,
                            state="patrol",
                            patrol_dir=0.0,
                        )
                    )
                elif char == "F" and self.goal is None:
                    # Only set goal from grid if no explicit goal in map data
                    self.goal = (x + 0.5, y + 0.5)

        # Load items from map data
        self.load_items_from_map(map_info)

        # Override goal from explicit map data if present
        explicit_goal = map_info.get("goal")
        if (
            explicit_goal
            and isinstance(explicit_goal, (list, tuple))
            and len(explicit_goal) >= 2
        ):
            self.goal = (explicit_goal[0] + 0.5, explicit_goal[1] + 0.5)

    def load_items_from_map(self, map_info: Dict):
        """Load items from map info"""
        items_data = map_info.get("items", [])
        for item_data in items_data:
            self.items.append(
                Item(
                    x=item_data.get("x", 0),
                    y=item_data.get("y", 0),
                    item_type=item_data.get("type", "health_pack"),
                    value=item_data.get("value", 0),
                    collected=False,
                )
            )

    def set_map(self, map_name: str) -> bool:
        """Set the current map"""
        if self.map_manager.set_map(map_name):
            self.current_map = self.map_manager._current_map
            return True
        return False

    def get_available_maps(self) -> List[str]:
        """Get available maps"""
        return self.map_manager.get_available_maps()

    def get_map_info(self) -> Dict[str, Any]:
        """Get current map info"""
        return self.map_manager.get_current_map()

    def reset(self):
        """Reset game to initial state"""
        self.game_state = "menu"
        self.parse_map()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "game_state": self.game_state,
            "player": self.player.to_dict(),
            "enemies": [e.to_dict() for e in self.enemies],
            "corpses": [c.to_dict() for c in self.corpses],
            "kills": self.kills,
            "hit_effects": [h.to_dict() for h in self.hit_effects],
            "current_map": self.current_map,
            "map_name": self.map_manager.get_current_map().get("name", "Unknown"),
            "goal": self.goal,
            "goal_reached": self.goal_reached,
            "items": [i.to_dict() for i in self.items],
        }
