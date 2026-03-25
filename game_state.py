"""Game state data classes for WebDoom server"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
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


MAP_DATA = [
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

MAP_WIDTH = len(MAP_DATA[0])
MAP_HEIGHT = len(MAP_DATA)


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
    hit_effects: List[HitEffect] = field(default_factory=dict)
    pending_input: Dict[str, bool] = field(default_factory=dict)
    player_speed_multiplier: float = 1.0

    def parse_map(self):
        """Parse map and spawn entities"""
        self.player = Player()
        self.enemies = []
        self.corpses = []
        self.kills = 0
        self.hit_effects = []

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                char = MAP_DATA[y][x]
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
        }
