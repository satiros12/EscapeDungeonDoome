"""
Game configuration constants
"""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_DARK_GRAY = (64, 64, 64)
COLOR_LIGHT_GRAY = (192, 192, 192)

# Player settings
PLAYER_SPEED = 3.0
PLAYER_ROTATION_SPEED = 3.0
PLAYER_START_HEALTH = 100

# Enemy settings
ENEMY_COUNT = 3
ENEMY_HEALTH = 30
ENEMY_SPEED = 1.5

# Combat settings
ATTACK_DAMAGE = 10
ATTACK_RANGE = 1.5
ATTACK_COOLDOWN = 0.5  # seconds

# Raycasting settings
FOV = 60
RAY_COUNT = 800
MAX_DEPTH = 20

# Map settings
TILE_SIZE = 1.0  # world units

# UI settings
HUD_HEIGHT = 60
HUD_COLOR = (32, 32, 32)
FONT_SIZE = 20
