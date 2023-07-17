"""
This module initializes the display and creates dictionaries of resources.
"""

import os

import pygame
from pygame.locals import (
    K_ESCAPE,
    K_RETURN,
    K_UP,
    K_LEFT,
    K_DOWN,
    K_RIGHT,
    K_CAPSLOCK,
    K_w,
    K_a,
    K_s,
    K_d,
    K_f,
    K_e,
    K_q,
    K_c,
    K_x,
    K_i,
    K_q,
    K_TAB,
    K_SPACE,
    K_LSHIFT,
    K_LCTRL,
    K_RSHIFT,
    K_RCTRL,
    K_F5,
    K_F9,
    K_F1,
)

from game.utils import resource_path


SCREEN_SIZES = {
    # "nHD": (640, 360),
    # "FWVGA": (854, 480),
    # "qHD": (960, 540),
    "HD": (1280, 720),
    # "WXGA": (1366, 768),
    # "HD+": (1600, 900),
    "Full HD": (1920, 1080),
    "QHD": (2560, 1440),
    # "QHD+": (3200, 1800),
    "4K UHD": (3840, 2160),
    "5K": (5120, 2880),
    "8K UHD": (7680, 4320),
    "16K UHD": (15360, 8640),
}

FRAMERATE = 60.0
CAPTION = "Untitled Adventure RPG"
TEXTURE_SCALE = 1

IMAGE_ACCEPTS = (".png", ".jpg", ".bmp")
FONT_ACCEPTS = ".ttf"
SOUND_ACCEPTS = (".wav", ".mp3", ".ogg", ".mdi")

ASSETS_DIR = resource_path("assets")
GFX_DIR = os.path.join(ASSETS_DIR, "graphics")
FONT_DIR = os.path.join(ASSETS_DIR, "fonts")
SFX_DIR = os.path.join(ASSETS_DIR, "sound")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")

DATA_DIR = resource_path("data")
SAVE_DIR = os.path.join(DATA_DIR, "save")
CONF_DIR = os.path.join(DATA_DIR, "conf")
for folder in [SAVE_DIR, CONF_DIR]:
    os.makedirs(folder, exist_ok=True)

M_BUTTON1 = -5
M_BUTTON2 = M_BUTTON1 + 1
M_BUTTON3 = M_BUTTON2 + 1
M_BUTTON4 = M_BUTTON3 + 1
M_BUTTON5 = M_BUTTON4 + 1

CONFIGURATION_FILE = os.path.join(CONF_DIR, "conf.ini")
CONTROLS_FILE = os.path.join(CONF_DIR, "controls.json")
AUTOSAVE_FILE = os.path.join(SAVE_DIR, "autosave.dat")
SAVE_FILE = os.path.join(SAVE_DIR, "save.dat")
DISPLAY_FILE = os.path.join(CONF_DIR, "display.json")
SOUND_FILE = os.path.join(CONF_DIR, "sound.json")

# region Movement Keys

DEFAULT_MOVE_UP_PRIMARY_KEY = K_w
DEFAULT_MOVE_UP_SECONDARY_KEY = K_UP

DEFAULT_MOVE_LEFT_PRIMARY_KEY = K_a
DEFAULT_MOVE_LEFT_SECONDARY_KEY = K_LEFT

DEFAULT_MOVE_DOWN_PRIMARY_KEY = K_s
DEFAULT_MOVE_DOWN_SECONDARY_KEY = K_DOWN

DEFAULT_MOVE_RIGHT_PRIMARY_KEY = K_d
DEFAULT_MOVE_RIGHT_SECONDARY_KEY = K_RIGHT

DEFAULT_DODGE_PRIMARY_KEY = K_SPACE
DEFAULT_DODGE_SECONDARY_KEY = None

DEFAULT_CROUCH_HOLD_PRIMARY_KEY = K_LCTRL
DEFAULT_CROUCH_HOLD_SECONDARY_KEY = K_RCTRL
DEFAULT_CROUCH_TOGGLE_PRIMARY_KEY = K_c
DEFAULT_CROUCH_TOGGLE_SECONDARY_KEY = None

DEFAULT_SPRINT_HOLD_PRIMARY_KEY = K_LSHIFT
DEFAULT_SPRINT_HOLD_SECONDARY_KEY = K_RSHIFT
DEFAULT_SPRINT_TOGGLE_PRIMARY_KEY = K_x
DEFAULT_SPRINT_TOGGLE_SECONDARY_KEY = None

DEFAULT_WALK_HOLD_PRIMARY_KEY = None
DEFAULT_WALK_HOLD_SECONDARY_KEY = None
DEFAULT_WALK_TOGGLE_PRIMARY_KEY = K_CAPSLOCK
DEFAULT_WALK_TOGGLE_SECONDARY_KEY = None

# endregion

DEFAULT_PRIMARY_ATTACK_PRIMARY_KEY = M_BUTTON1
DEFAULT_PRIMARY_ATTACK_SECONDARY_KEY = None

DEFAULT_SECONDARY_ATTACK_PRIMARY_KEY = M_BUTTON2
DEFAULT_SECONDARY_ATTACK_SECONDARY_KEY = None

DEFAULT_INVENTORY_PRIMARY_KEY = K_TAB
DEFAULT_INVENTORY_SECONDARY_KEY = K_i

DEFAULT_INTERACT_PRIMARY_KEY = K_e
DEFAULT_INTERACT_SECONDARY_KEY = None

DEFAULT_PAUSE_PRIMARY_KEY = K_ESCAPE
DEFAULT_PAUSE_SECONDARY_KEY = None

DEFAULT_CONFIRM_PRIMARY_KEY = K_RETURN
DEFAULT_CONFIRM_SECONDARY_KEY = None

DEFAULT_DENY_PRIMARY_KEY = K_ESCAPE
DEFAULT_DENY_SECONDARY_KEY = None

DEFAULT_QUICKSAVE_PRIMARY_KEY = K_F5
DEFAULT_QUICKSAVE_SECONDARY_KEY = None

DEFAULT_QUICKLOAD_PRIMARY_KEY = K_F9
DEFAULT_QUICKLOAD_SECONDARY_KEY = None

DEFAULT_CONSOLE_TOGGLE_PRIMARY_KEY = K_F1
DEFAULT_CONSOLE_TOGGLE_SECONDARY_KEY = None

DEFAULT_KEYMAP = {
    "MOVE_UP_PRIMARY": DEFAULT_MOVE_UP_PRIMARY_KEY,
    "MOVE_UP_SECONDARY": DEFAULT_MOVE_UP_SECONDARY_KEY,
    "MOVE_LEFT_PRIMARY": DEFAULT_MOVE_LEFT_PRIMARY_KEY,
    "MOVE_LEFT_SECONDARY": DEFAULT_MOVE_LEFT_SECONDARY_KEY,
    "MOVE_DOWN_PRIMARY": DEFAULT_MOVE_DOWN_PRIMARY_KEY,
    "MOVE_DOWN_SECONDARY": DEFAULT_MOVE_DOWN_SECONDARY_KEY,
    "MOVE_RIGHT_PRIMARY": DEFAULT_MOVE_RIGHT_PRIMARY_KEY,
    "MOVE_RIGHT_SECONDARY": DEFAULT_MOVE_RIGHT_SECONDARY_KEY,
    "DODGE_PRIMARY": DEFAULT_DODGE_PRIMARY_KEY,
    "DODGE_SECONDARY": DEFAULT_DODGE_SECONDARY_KEY,
    "CROUCH_HOLD_PRIMARY": DEFAULT_CROUCH_HOLD_PRIMARY_KEY,
    "CROUCH_HOLD_SECONDARY": DEFAULT_CROUCH_HOLD_SECONDARY_KEY,
    "CROUCH_TOGGLE_PRIMARY": DEFAULT_CROUCH_TOGGLE_PRIMARY_KEY,
    "CROUCH_TOGGLE_SECONDARY": DEFAULT_CROUCH_TOGGLE_SECONDARY_KEY,
    "SPRINT_HOLD_PRIMARY": DEFAULT_SPRINT_HOLD_PRIMARY_KEY,
    "SPRINT_HOLD_SECONDARY": DEFAULT_SPRINT_HOLD_SECONDARY_KEY,
    "SPRINT_TOGGLE_PRIMARY": DEFAULT_SPRINT_TOGGLE_PRIMARY_KEY,
    "SPRINT_TOGGLE_SECONDARY": DEFAULT_SPRINT_TOGGLE_SECONDARY_KEY,
    "WALK_HOLD_PRIMARY": DEFAULT_WALK_HOLD_PRIMARY_KEY,
    "WALK_HOLD_SECONDARY": DEFAULT_WALK_HOLD_SECONDARY_KEY,
    "WALK_TOGGLE_PRIMARY": DEFAULT_WALK_TOGGLE_PRIMARY_KEY,
    "WALK_TOGGLE_SECONDARY": DEFAULT_WALK_TOGGLE_SECONDARY_KEY,
    "PRIMARY_ATTACK_PRIMARY": DEFAULT_PRIMARY_ATTACK_PRIMARY_KEY,
    "PRIMARY_ATTACK_SECONDARY": DEFAULT_PRIMARY_ATTACK_SECONDARY_KEY,
    "SECONDARY_ATTACK_PRIMARY": DEFAULT_SECONDARY_ATTACK_PRIMARY_KEY,
    "SECONDARY_ATTACK_SECONDARY": DEFAULT_SECONDARY_ATTACK_SECONDARY_KEY,
    "INVENTORY_PRIMARY": DEFAULT_INVENTORY_PRIMARY_KEY,
    "INVENTORY_SECONDARY": DEFAULT_INVENTORY_SECONDARY_KEY,
    "INTERACT_PRIMARY": DEFAULT_INTERACT_PRIMARY_KEY,
    "INTERACT_SECONDARY": DEFAULT_INTERACT_SECONDARY_KEY,
    "PAUSE_PRIMARY": DEFAULT_PAUSE_PRIMARY_KEY,
    "PAUSE_SECONDARY": DEFAULT_PAUSE_SECONDARY_KEY,
    "CONFIRM_PRIMARY": DEFAULT_CONFIRM_PRIMARY_KEY,
    "CONFIRM_SECONDARY": DEFAULT_CONFIRM_SECONDARY_KEY,
    "DENY_PRIMARY": DEFAULT_DENY_PRIMARY_KEY,
    "DENY_SECONDARY": DEFAULT_DENY_SECONDARY_KEY,
    "QUICKSAVE_PRIMARY": DEFAULT_QUICKSAVE_PRIMARY_KEY,
    "QUICKSAVE_SECONDARY": DEFAULT_QUICKSAVE_SECONDARY_KEY,
    "QUICKLOAD_PRIMARY": DEFAULT_QUICKLOAD_PRIMARY_KEY,
    "QUICKLOAD_SECONDARY": DEFAULT_QUICKLOAD_SECONDARY_KEY,
    "CONSOLE_TOGGLE_PRIMARY": DEFAULT_CONSOLE_TOGGLE_PRIMARY_KEY,
    "CONSOLE_TOGGLE_SECONDARY": DEFAULT_CONSOLE_TOGGLE_SECONDARY_KEY,
}


# region Colors

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 250)

HEALTH_RED = (231, 76, 60)
MANA_BLUE = (52, 152, 219)
STAMINA_GREEN = (46, 204, 113)
GREEDY_GOLD = (255, 215, 0)
PRINCELY_PURPLE = (189, 147, 249)

# endregion Colors

# region Entities

DEFAULT_DROP_HEALTH_TIMER = 60000
DEFAULT_DROP_MANA_TIMER = 60000
DEFAULT_DROP_STAMINA_TIMER = 60000


# region Default Defaults

DEFAULT_HEALTH = 100
DEFAULT_HEALTH_REGEN = 0

DEFAULT_STAMINA = 100
DEFAULT_STAMINA_REGEN = 10
DEFAULT_STAMINA_DRAIN = 10
DEFAULT_SPRINT_STAMINA_DRAIN = DEFAULT_STAMINA_DRAIN
DEFAULT_SWIM_STAMINA_DRAIN = DEFAULT_STAMINA_DRAIN

DEFAULT_MANA = 100
DEFAULT_MANA_REGEN = 1
DEFAULT_MANA_DRAIN = 1

DEFAULT_EXPERIENCE = 0
DEFAULT_EXPERIENCE_MODIFIER = 1

DEFAULT_ARMOR = 0  # Blunt/unarmed
DEFAULT_FIRE_RESISTANCE = 0
DEFAULT_WATER_RESISTANCE = 0
DEFAULT_ELECTRICITY_RESISTANCE = 0
DEFAULT_MAGIC_RESISTANCE = 0
DEFAULT_POISON_RESISTANCE = 0
DEFAULT_ICE_RESISTANCE = 0
DEFAULT_DARK_RESISTANCE = 0
DEFAULT_LIGHT_RESISTANCE = 0
DEFAULT_BLEED_RESISTANCE = 0  # sharp/bladed
DEFAULT_STEALTH = 0

DEFAULT_WALK_SPEED = 3
DEFAULT_WALK_SPEED_MODIFIER = 1
DEFAULT_CROUCH_SPEED_MODIFIER = 0.25
DEFAULT_SPRINT_SPEED_MODIFIER = 2.5
DEFAULT_SWIM_SPEED_MODIFIER = 0

DEFAULT_DAMAGE = 1

DEFAULT_ATTACK_COOLDOWN = 5

# endregion


# region Player

DEFAULT_PLAYER_DAMAGE = 2
DEFAULT_PLAYER_DAMAGE_SCALE = 0.25

DEFAULT_PLAYER_HEALTH = 100
DEFAULT_PLAYER_HEALTH_BAR_BORDER = 2
DEFAULT_PLAYER_HEALTH_BAR_COLOR = HEALTH_RED
DEFAULT_PLAYER_HEALTH_BAR_HEIGHT = 10
DEFAULT_PLAYER_HEALTH_BAR_ORDER = 1
DEFAULT_PLAYER_HEALTH_SCALE = 0.1

DEFAULT_PLAYER_SPEED = 5
DEFAULT_PLAYER_SPEED_CROUCH_MODIFIER = -2
DEFAULT_PLAYER_SPEED_SPRINT_MODIFIER = 2

DEFAULT_PLAYER_STAMINA = 100
DEFAULT_PLAYER_STAMINA_BAR_BORDER = 2
DEFAULT_PLAYER_STAMINA_BAR_COLOR = STAMINA_GREEN
DEFAULT_PLAYER_STAMINA_BAR_HEIGHT = 10
DEFAULT_PLAYER_STAMINA_BAR_ORDER = 2
DEFAULT_PLAYER_STAMINA_SCALE = 0.25

DEFAULT_PLAYER_MANA = 100
DEFAULT_PLAYER_MANA_BAR_BORDER = 2
DEFAULT_PLAYER_MANA_BAR_COLOR = MANA_BLUE
DEFAULT_PLAYER_MANA_BAR_HEIGHT = 10
DEFAULT_PLAYER_MANA_BAR_ORDER = 3
DEFAULT_PLAYER_MANA_SCALE = 0.1

# endregion Player

# region Enemy

DEFAULT_ENEMY_DAMAGE = 5
DEFAULT_ENEMY_DAMAGE_SCALE = 0.1

DEFAULT_ENEMY_HEALTH = 5
DEFAULT_ENEMY_HEALTH_SCALE = 0.1

DEFAULT_ENEMY_SPEED = 10
DEFAULT_ENEMY_SPEED_CROUCH_MODIFIER = -5
DEFAULT_ENEMY_SPEED_SPRINT_MODIFIER = 5

DEFAULT_ENEMY_SPAWN_TIMER = 10000

# endregion Enemy

# endregion Entities

# region StatusBar

DEFAULT_STATUS_BAR_HEIGHT = 32
DEFAULT_STATUS_BAR_FONT_SIZE = 32
DEFAULT_STATUS_BAR_FONT_COLOR = BLACK
DEFAULT_STATUS_BAR_BACKGROUND_COLOR = WHITE

# endregion StatusBar
