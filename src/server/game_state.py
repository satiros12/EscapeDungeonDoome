"""Game state data classes for WebDoom server"""

import math
import os
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

_SHARED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shared")
_MAPS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "maps")
sys.path.insert(0, _SHARED_DIR)

try:
    from constants import GameConfig
    from config import load_config, ConfigLoader
except ImportError:
    pass


class GameConfig:
    FOV: float = math.pi / 3
    HALF_FOV: float = math.pi / 6
    NUM_RAYS: int = 320
    MAX_DEPTH: float = 16
    MOVE_SPEED: float = 3
    ROT_SPEED: float = 2
    ATTACK_RANGE: float = 1.5
    ATTACK_COOLDOWN: float = 0.5
    ENEMY_SPEED: float = 2.5
    DETECTION_RANGE: float = 5
    ENEMY_ATTACK_RANGE: float = 1.0
    ENEMY_ATTACK_COOLDOWN: float = 1
    PLAYER_MAX_HEALTH: int = 100
    ENEMY_MAX_HEALTH: int = 30
    PLAYER_DAMAGE: int = 10
    ENEMY_DAMAGE: int = 10
    PATROL_SPEED: float = 1
    FOV_CULL: float = 0.2
    RAY_STEP: float = 0.02
    COLLISION_MARGIN: float = 0.5
    LOST_PLAYER_DISTANCE: float = 12
    DT_MAX: float = 0.1
    MIN_BRIGHTNESS: float = 0.3


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
        self._available_maps = ['base']
        self._maps['base'] = {
            'name': 'Base Map',
            'grid': DEFAULT_MAP_DATA,
            'width': 16,
            'height': 16,
            'description': 'Classic starting map'
        }
        
        if not os.path.exists(_MAPS_DIR):
            return
        
        for filename in os.listdir(_MAPS_DIR):
            if filename.endswith('.json'):
                map_path = os.path.join(_MAPS_DIR, filename)
                try:
                    with open(map_path, 'r') as f:
                        map_data = json.load(f)
                        map_name = map_data.get('name', filename[:-5]).lower().replace(' ', '_')
                        self._maps[map_name] = map_data
                        if map_name not in self._available_maps:
                            self._available_maps.append(map_name)
                except Exception as e:
                    print(f"Error loading map {filename}: {e}")
    
    def get_current_map(self) -> Dict:
        """Get current map data"""
        return self._maps.get(self._current_map, self._maps.get('base', {'grid': DEFAULT_MAP_DATA}))
    
    def set_map(self, map_name: str) -> bool:
        """Set current map by name"""
        normalized = map_name.lower().replace(' ', '_')
        if normalized in self._maps:
            self._current_map = normalized
            return True
        return False
    
    def get_available_maps(self) -> List[str]:
        """Get list of available map names"""
        return self._available_maps
    
    def get_map_index(self) -> int:
        """Get current map index"""
        return self._available_maps.index(self._current_map) if self._current_map in self._available_maps else 0
    
    def get_next_map(self) -> str:
        """Get next map in carousel"""
        if not self._available_maps:
            return 'base'
        idx = self.get_map_index()
        return self._available_maps[(idx + 1) % len(self._available_maps)]
    
    def get_prev_map(self) -> str:
        """Get previous map in carousel"""
        if not self._available_maps:
            return 'base'
        idx = self.get_map_index()
        return self._available_maps[(idx - 1) % len(self._available_maps)]
    
    def get_map_data(self, map_name: str) -> Optional[Dict]:
        """Get map data by name"""
        normalized = map_name.lower().replace(' ', '_')
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "health": self.health,
            "attack_cooldown": self.attack_cooldown,
            "god_mode": self.god_mode,
            "speed_multiplier": self.speed_multiplier,
        }

    def reset(self):
        self.x = 1.5
        self.y = 1.5
        self.angle = 0.0
        self.health = GameConfig.PLAYER_MAX_HEALTH
        self.attack_cooldown = 0


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

    def __post_init__(self):
        self.map_manager = MapManager()

    def parse_map(self, map_data: List[str] = None):
        """Parse map and spawn entities"""
        self.player = Player()
        self.enemies = []
        self.corpses = []
        self.kills = 0
        self.hit_effects = []

        if map_data is None:
            map_data = self.map_manager.get_current_map().get('grid', MAP_DATA)
        
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
            "map_name": self.map_manager.get_current_map().get('name', 'Unknown'),
        }
