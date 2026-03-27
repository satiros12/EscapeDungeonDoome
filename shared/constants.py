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


class GameConfig:
    FOV = 3.141592653589793 / 3
    HALF_FOV = 3.141592653589793 / 6
    NUM_RAYS = 320
    MAX_DEPTH = 16
    MOVE_SPEED = 3
    ROT_SPEED = 2
    ATTACK_RANGE = 1.5
    ATTACK_COOLDOWN = 0.5
    ENEMY_SPEED = 2.5
    DETECTION_RANGE = 5
    ENEMY_ATTACK_RANGE = 1.0
    ENEMY_ATTACK_COOLDOWN = 1
    PLAYER_MAX_HEALTH = 100
    ENEMY_MAX_HEALTH = 30
    PLAYER_DAMAGE = 10
    ENEMY_DAMAGE = 10
    PATROL_SPEED = 1
    FOV_CULL = 0.2
    RAY_STEP = 0.02
    COLLISION_MARGIN = 0.5
    LOST_PLAYER_DISTANCE = 12
    DT_MAX = 0.1
    MIN_BRIGHTNESS = 0.3
