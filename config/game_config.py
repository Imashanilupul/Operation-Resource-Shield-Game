"""
Game Configuration File
Contains all constants and settings for the game
"""

# ============ WINDOW SETTINGS ============
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
WINDOW_TITLE = "Operation Guardian: Multi-Agent Defense System"

# ============ GAME COLORS ============
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_MAGENTA = (255, 0, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_DARK_GRAY = (64, 64, 64)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_ORANGE = (255, 165, 0)
COLOR_PURPLE = (128, 0, 128)
COLOR_BROWN = (165, 42, 42)
COLOR_GREEN_DARK = (34, 139, 34)

# ============ ENTITY SETTINGS ============
PLAYER_SPEED = 5
PLAYER_SIZE = 15
PLAYER_CARRYING_CAPACITY = 3
PLAYER_STEALTH_DURATION = 180  # frames (3 seconds at 60 FPS)
PLAYER_STEALTH_COOLDOWN = 300  # frames

AGENT_SPEED = 1.5
AGENT_SIZE = 12
AGENT_VISION_RANGE = 90
AGENT_COMMUNICATION_RANGE = 300

# ============ RESOURCE SETTINGS ============
RESOURCE_SIZE = 8
RESOURCES_INITIAL_COUNT = 10
RESOURCES_SPAWN_RATE = 0.008  # Reduced probability per frame
RESOURCES_MAX_ON_MAP = 10
RESOURCE_VALUE = 1

# ============ OBSTACLE SETTINGS ============
OBSTACLE_SIZE_RANGE = (20, 60)
OBSTACLE_COUNT = 30

# ============ BASE CAMP SETTINGS ============
BASE_CAMP_SIZE = 40
BASE_CAMP_COLOR = COLOR_GREEN_DARK
BASE_CAMP_X = WINDOW_WIDTH // 2
BASE_CAMP_Y = WINDOW_HEIGHT // 2

# ============ THIEF HIDEOUT SETTINGS ============
HIDEOUT_SIZE = 30
HIDEOUT_COLOR = COLOR_RED
HIDEOUT_X = 100
HIDEOUT_Y = 100

# ============ GAME MECHANICS ============
WINNING_RESOURCES_FOR_THIEF = RESOURCES_INITIAL_COUNT  # Steal all to win
CATCHING_DISTANCE = 15  # Pixels to catch thief

# ============ AGENT ROLES ============
AGENT_ROLE_EXPLORER = "explorer"
AGENT_ROLE_COLLECTOR = "collector"
AGENT_ROLE_ATTACKER = "attacker"
AGENT_ROLE_STRATEGIST = "strategist"

# ============ MOVEMENT TYPES ============
MOVEMENT_PATROL = "patrol"
MOVEMENT_PURSUE = "pursue"
MOVEMENT_RETURN_HOME = "return_home"
MOVEMENT_COLLECT = "collect"

# ============ GAME STATE ============
GAME_STATE_RUNNING = "running"
GAME_STATE_PLAYER_WIN = "player_win"
GAME_STATE_AGENTS_WIN = "agents_win"
GAME_STATE_PAUSED = "paused"

# ============ UI SETTINGS ============
FONT_SIZE_SMALL = 16
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 32
UI_PADDING = 10
UI_LINE_HEIGHT = 25

# ============ DIFFICULTY SETTINGS ============
DIFFICULTY_EASY = {
    "agent_count": 2,
    "agent_speed_multiplier": 0.8,
    "resource_spawn_multiplier": 1.5,
}

DIFFICULTY_NORMAL = {
    "agent_count": 4,
    "agent_speed_multiplier": 1.0,
    "resource_spawn_multiplier": 1.0,
}

DIFFICULTY_HARD = {
    "agent_count": 6,
    "agent_speed_multiplier": 1.3,
    "resource_spawn_multiplier": 0.7,
}

# ============ MAP ZONES ============
ZONE_SIZE = 300  # Size of map sectors for Explorer
ZONES = {
    "top_left": (0, 0, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
    "top_right": (WINDOW_WIDTH // 2, 0, WINDOW_WIDTH, WINDOW_HEIGHT // 2),
    "bottom_left": (0, WINDOW_HEIGHT // 2, WINDOW_WIDTH // 2, WINDOW_HEIGHT),
    "bottom_right": (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, WINDOW_WIDTH, WINDOW_HEIGHT),
}

# ============ LOGGING ============
DEBUG_MODE = False
SHOW_AGENT_VISION = True
SHOW_COMMUNICATION = False
SHOW_FPS = True
