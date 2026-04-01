import json
import os

SHARED_DIR = os.path.dirname(os.path.abspath(__file__))

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


import math


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
