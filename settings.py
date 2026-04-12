from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def resource_path(*parts):
    return str(BASE_DIR.joinpath(*parts))


TITLE = "Cats vs Raccoons - Turf Defenders"

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 620
FRAME_MS = 16

LANE_COUNT = 3
LANE_Y = [180, 310, 440]

LEFT_TURF_X = 110
RIGHT_TURF_X = WINDOW_WIDTH - 110
STARTING_TURF_HP = 15

BACKGROUND_COLOR = "#b9e3a6"
LANE_COLOR = "#95c47d"
TEXT_COLOR = "#1f1f1f"

ENERGY_MAX = 120
ENERGY_REGEN_PER_SECOND = 18

AI_SPAWN_MIN = 1.4
AI_SPAWN_MAX = 2.5

CAT_START_X = 80
RACCOON_START_X = WINDOW_WIDTH - 80

GOAL_PADDING = 35

ATTACK_RANGE = 52
ATTACK_COOLDOWN = 0.75

SPRITE_SHEET_PATH = resource_path("assets", "cats_raccoons_walk_attack_pretty.png")
SPRITE_CELL_W = 96
SPRITE_CELL_H = 96
SPRITE_SCALE = 1.0
SPRITE_CAPTURE_PADDING = 0

ANIMATION_FRAME_TIME = 0.14

UNIT_TYPES = {
    "strong": {
        "cost": 50,
        "hp": 52,
        "damage": 14,
        "speed": 52.0,
    },
    "fast": {
        "cost": 30,
        "hp": 28,
        "damage": 8,
        "speed": 88.0,
    },
    "tough": {
        "cost": 75,
        "hp": 82,
        "damage": 10,
        "speed": 42.0,
    },
}

# Sprite sheet mapping.
# 4 columns x 6 rows:
# columns 0-1 walk, 2-3 attack
# rows 0-2 cats, 3-5 raccoons
SPRITE_MAP = {
    ("cats", "strong"): {
        "idle": [(0, 0), (1, 0)],
        "walk": [(0, 0), (1, 0)],
        "attack": [(2, 0), (3, 0)],
    },
    ("cats", "fast"): {
        "idle": [(0, 1), (1, 1)],
        "walk": [(0, 1), (1, 1)],
        "attack": [(2, 1), (3, 1)],
    },
    ("cats", "tough"): {
        "idle": [(0, 2), (1, 2)],
        "walk": [(0, 2), (1, 2)],
        "attack": [(2, 2), (3, 2)],
    },
    ("raccoons", "strong"): {
        "idle": [(0, 3), (1, 3)],
        "walk": [(0, 3), (1, 3)],
        "attack": [(2, 3), (3, 3)],
    },
    ("raccoons", "fast"): {
        "idle": [(0, 4), (1, 4)],
        "walk": [(0, 4), (1, 4)],
        "attack": [(2, 4), (3, 4)],
    },
    ("raccoons", "tough"): {
        "idle": [(0, 5), (1, 5)],
        "walk": [(0, 5), (1, 5)],
        "attack": [(2, 5), (3, 5)],
    },
}
