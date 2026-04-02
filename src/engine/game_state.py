"""
Game State - manages all game state data
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


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


class MapManager:
    """Manages map data and loading."""

    def __init__(self):
        self._maps: Dict[str, Dict] = {}
        self._current_map: str = "base"
        self._available_maps: List[str] = ["base"]
        self._load_default_maps()

    def _load_default_maps(self) -> None:
        """Load default maps."""
        self._maps["base"] = {
            "name": "Base Map",
            "grid": DEFAULT_MAP_DATA,
            "width": 16,
            "height": 16,
            "description": "Classic starting map",
        }

    def get_current_map(self) -> Dict:
        """Get current map data."""
        return self._maps.get(
            self._current_map, self._maps.get("base", {"grid": DEFAULT_MAP_DATA})
        )

    def set_map(self, map_name: str) -> bool:
        """Set current map by name."""
        normalized = map_name.lower().replace(" ", "_")
        if normalized in self._maps:
            self._current_map = normalized
            return True
        return False

    def get_available_maps(self) -> List[str]:
        """Get list of available map names."""
        return self._available_maps


class ItemType:
    """Item type constants."""

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
    """Represents an item in the game."""

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


@dataclass
class Player:
    """Represents the player."""

    x: float = 1.5
    y: float = 1.5
    angle: float = 0.0
    health: int = 100
    attack_cooldown: float = 0
    god_mode: bool = False
    speed_multiplier: float = 1.0
    current_weapon: str = "fists"
    ammo: Dict[str, int] = field(default_factory=dict)
    armor: int = 0
    armor_type: str = "none"

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

    def reset(self) -> None:
        """Reset player to default state."""
        self.x = 1.5
        self.y = 1.5
        self.angle = 0.0
        self.health = 100
        self.attack_cooldown = 0
        self.current_weapon = "fists"
        self.ammo = {}
        self.armor = 0
        self.armor_type = "none"


class EnemyType:
    """Enemy type constants."""

    IMP = "imp"
    DEMON = "demon"
    CACODEMON = "cacodemon"
    SOLDIER_PISTOL = "soldier_pistol"
    SOLDIER_SHOTGUN = "soldier_shotgun"
    CHAINGUNNER = "chaingunner"


ENEMY_TYPE_MAP = {
    "E": EnemyType.IMP,
    "D": EnemyType.DEMON,
    "C": EnemyType.CACODEMON,
}


@dataclass
class Enemy:
    """Represents an enemy."""

    x: float
    y: float
    angle: float = 0.0
    health: int = 30
    state: str = "patrol"
    patrol_dir: float = 0.0
    attack_cooldown: float = 0
    dying_progress: float = 0
    enemy_type: str = "imp"
    weapon: str = "fists"
    armor: int = 0
    armor_type: str = "none"

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
            "enemy_type": self.enemy_type,
            "weapon": self.weapon,
            "armor": self.armor,
            "armor_type": self.armor_type,
        }


@dataclass
class Corpse:
    """Represents a dead enemy."""

    x: float
    y: float

    def to_dict(self) -> Dict[str, Any]:
        return {"x": self.x, "y": self.y}


@dataclass
class HitEffect:
    """Represents a hit effect."""

    x: float
    y: float
    timer: float = 0.3

    def to_dict(self) -> Dict[str, Any]:
        return {"x": self.x, "y": self.y, "timer": self.timer}


class GameState:
    """Main game state class."""

    def __init__(self):
        self.game_state: str = "menu"
        self.player: Player = Player()
        self.enemies: List[Enemy] = []
        self.corpses: List[Corpse] = []
        self.kills: int = 0
        self.hit_effects: List[HitEffect] = []
        self.pending_input: Dict[str, bool] = {}
        self.player_speed_multiplier: float = 1.0
        self.current_map: str = "base"
        self.goal: Optional[tuple] = None
        self.goal_reached: bool = False
        self.items: List[Item] = []

        self.map_manager = MapManager()

    def parse_map(self, map_data: List[str] = None) -> None:
        """Parse map and spawn entities."""
        self.player = Player()
        self.enemies = []
        self.corpses = []
        self.kills = 0
        self.hit_effects = []
        self.goal = None
        self.goal_reached = False
        self.items = []

        map_info = self.map_manager.get_current_map()

        if map_data is None:
            map_data = map_info.get("grid", DEFAULT_MAP_DATA)

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
                elif char in ENEMY_TYPE_MAP:
                    enemy_type = ENEMY_TYPE_MAP[char]
                    enemy = self._create_enemy(x + 0.5, y + 0.5, enemy_type)
                    self.enemies.append(enemy)

    def _create_enemy(self, x: float, y: float, enemy_type: str) -> Enemy:
        """Create an enemy with the specified type."""
        import random

        configs = {
            EnemyType.IMP: {"health": 30, "weapon": "fists", "speed": 2.5},
            EnemyType.DEMON: {"health": 60, "weapon": "fists", "speed": 2.0},
            EnemyType.CACODEMON: {"health": 100, "weapon": "fists", "speed": 1.5},
        }

        config = configs.get(enemy_type, configs[EnemyType.IMP])

        return Enemy(
            x=x,
            y=y,
            angle=0.0,
            health=config["health"],
            state="patrol",
            patrol_dir=random.random() * 2 * math.pi,
            enemy_type=enemy_type.value if hasattr(enemy_type, "value") else enemy_type,
            weapon=config["weapon"],
        )

    def reset(self) -> None:
        """Reset game to initial state."""
        self.game_state = "menu"
        self.parse_map()

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        current_map_data = self.map_manager.get_current_map()
        grid = current_map_data.get("grid", DEFAULT_MAP_DATA)

        return {
            "game_state": self.game_state,
            "player": self.player.to_dict(),
            "enemies": [e.to_dict() for e in self.enemies],
            "corpses": [c.to_dict() for c in self.corpses],
            "kills": self.kills,
            "hit_effects": [h.to_dict() for h in self.hit_effects],
            "current_map": self.current_map,
            "map_name": current_map_data.get("name", "Unknown"),
            "grid": grid,
            "map_width": len(grid[0]) if grid else 0,
            "map_height": len(grid) if grid else 0,
            "goal": self.goal,
            "goal_reached": self.goal_reached,
            "items": [i.to_dict() for i in self.items],
        }
