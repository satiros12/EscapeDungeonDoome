"""Map loader and configuration management"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MapData:
    name: str
    description: str
    width: int
    height: int
    grid: List[str]
    
    @property
    def player_start(self) -> tuple:
        """Find player start position"""
        for y, row in enumerate(self.grid):
            for x, char in enumerate(row):
                if char == 'P':
                    return (x + 0.5, y + 0.5)
        return (1.5, 1.5)
    
    @property
    def enemy_positions(self) -> List[tuple]:
        """Find all enemy positions"""
        positions = []
        for y, row in enumerate(self.grid):
            for x, char in enumerate(row):
                if char == 'E':
                    positions.append((x + 0.5, y + 0.5))
        return positions


class ConfigLoader:
    def __init__(self, config_path: str = None):
        self._config: Dict[str, Any] = {}
        self._maps: Dict[str, MapData] = {}
        self._maps_dir = None
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            self._config = json.load(f)
    
    def load_maps(self, maps_dir: str) -> None:
        """Load all maps from the maps directory"""
        self._maps_dir = maps_dir
        self._maps = {}
        
        if not os.path.exists(maps_dir):
            return
        
        for filename in os.listdir(maps_dir):
            if filename.endswith('.json'):
                map_path = os.path.join(maps_dir, filename)
                try:
                    map_data = self._load_map(map_path)
                    if map_data:
                        self._maps[map_data.name.lower().replace(' ', '_')] = map_data
                except Exception as e:
                    print(f"Error loading map {filename}: {e}")
    
    def _load_map(self, map_path: str) -> Optional[MapData]:
        """Load a single map from JSON file"""
        with open(map_path, 'r') as f:
            data = json.load(f)
        
        required_fields = ['name', 'grid']
        for field in required_fields:
            if field not in data:
                return None
        
        return MapData(
            name=data.get('name', 'Unknown'),
            description=data.get('description', ''),
            width=data.get('width', len(data['grid'][0])),
            height=data.get('height', len(data['grid'])),
            grid=data['grid']
        )
    
    def get_map(self, map_name: str) -> Optional[MapData]:
        """Get a map by name"""
        return self._maps.get(map_name.lower().replace(' ', '_'))
    
    def get_map_names(self) -> List[str]:
        """Get list of all map names"""
        return list(self._maps.keys())
    
    def get_all_maps(self) -> List[MapData]:
        """Get all loaded maps"""
        return list(self._maps.values())
    
    def get_config(self, key: str = None) -> Any:
        """Get config value"""
        if key is None:
            return self._config
        
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        return value
    
    def get_game_config(self) -> Dict[str, Any]:
        """Get game configuration"""
        return self._config.get('game', {})
    
    def get_rendering_config(self) -> Dict[str, Any]:
        """Get rendering configuration"""
        return self._config.get('rendering', {})
    
    def get_weapons_config(self) -> Dict[str, Any]:
        """Get weapons configuration"""
        return self._config.get('weapons', {})
    
    def get_enemy_types_config(self) -> Dict[str, Any]:
        """Get enemy types configuration"""
        return self._config.get('enemy_types', {})


def get_shared_dir() -> str:
    """Get the shared directory path"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_maps_dir() -> str:
    """Get the maps directory path"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'maps')


def load_config() -> ConfigLoader:
    """Load configuration and maps"""
    loader = ConfigLoader()
    
    config_path = os.path.join(get_shared_dir(), 'config.json')
    if os.path.exists(config_path):
        loader.load_config(config_path)
    
    maps_dir = get_maps_dir()
    if os.path.exists(maps_dir):
        loader.load_maps(maps_dir)
    
    return loader
