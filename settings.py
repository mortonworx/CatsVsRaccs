import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def resource_path(*parts):
    return str(BASE_DIR.joinpath(*parts))


def load_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


TITLE = "Cats vs Raccoons - Turf Defenders"

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 620
FRAME_MS = 16

LANE_COUNT = 3
LANE_Y = [180, 310, 440]

LEFT_TURF_X = 110
RIGHT_TURF_X = WINDOW_WIDTH - 110

BACKGROUND_COLOR = "#b9e3a6"
LANE_COLOR = "#95c47d"
TEXT_COLOR = "#1f1f1f"

CAT_START_X = 80
RACCOON_START_X = WINDOW_WIDTH - 80
GOAL_PADDING = 35

SPRITE_SHEET_PATH = resource_path("assets", "cats_raccoons_walk_attack_pretty.png")
TITLE_ART_PATH = resource_path("assets", "title_screen_art.png")
BALANCE_CONFIG_PATH = resource_path("assets", "game_balance.json")

SPRITE_CELL_W = 96
SPRITE_CELL_H = 96
SPRITE_SCALE = 1.0
SPRITE_CAPTURE_PADDING = 0

TITLE_THEME_PATH = resource_path("assets", "audio", "music", "title_theme.wav")
BATTLE_THEME_PATH = resource_path("assets", "audio", "music", "battle_theme.wav")
EXPERT_THEME_PATH = resource_path("assets", "audio", "music", "expert_theme.wav")

UI_SELECT_SOUND_PATH = resource_path("assets", "audio", "sfx", "ui_select.wav")
SPAWN_SOUND_PATH = resource_path("assets", "audio", "sfx", "spawn_unit.wav")
ATTACK_SOUND_PATH = resource_path("assets", "audio", "sfx", "attack_swipe.wav")
HIT_SOUND_PATH = resource_path("assets", "audio", "sfx", "hit_impact.wav")
BREAKTHROUGH_SOUND_PATH = resource_path("assets", "audio", "sfx", "turf_breakthrough.wav")
NOT_ENOUGH_ENERGY_SOUND_PATH = resource_path("assets", "audio", "sfx", "not_enough_energy.wav")
WIN_SOUND_PATH = resource_path("assets", "audio", "sfx", "win_jingle.wav")
LOSE_SOUND_PATH = resource_path("assets", "audio", "sfx", "lose_sting.wav")

ANIMATION_FRAME_TIME = 0.14

BALANCE_DATA = load_json(BALANCE_CONFIG_PATH)

ENERGY_MAX = BALANCE_DATA["economy"]["energy_max"]
ATTACK_RANGE = BALANCE_DATA["combat"]["attack_range"]
ATTACK_COOLDOWN = BALANCE_DATA["combat"]["attack_cooldown"]

UNIT_ORDER = BALANCE_DATA["unit_key_order"]
UNIT_TYPES = BALANCE_DATA["units"]
DIFFICULTY_SETTINGS = BALANCE_DATA["difficulties"]
DIFFICULTY_ORDER = list(DIFFICULTY_SETTINGS.keys())

UNIT_KEYBINDS = {
    str(index): unit_kind
    for index, unit_kind in enumerate(UNIT_ORDER, start=1)
}

SPRITE_STYLES = {
    unit_kind: unit_data.get("sprite_style", unit_kind)
    for unit_kind, unit_data in UNIT_TYPES.items()
}


def default_unit_kind():
    return UNIT_ORDER[0]


def unit_label(unit_kind):
    return UNIT_TYPES[unit_kind].get("label", unit_kind.capitalize())


def unit_description(unit_kind):
    return UNIT_TYPES[unit_kind].get("description", "")


def ai_spawn_weight(unit_kind):
    return UNIT_TYPES[unit_kind].get("spawn_weight", 0)


def sprite_style(unit_kind):
    return SPRITE_STYLES[unit_kind]


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
