"""
This module initializes the display and creates dictionaries of resources.
"""

import os

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

FRAMERATE = 60
SCREEN_SIZE = SCREEN_SIZES["Full HD"]
ORIGINAL_CAPTION = "Untitled Adventure RPG"
TEXTURE_SCALE = 1

IMAGE_ACCEPTS = (".png", ".jpg", ".bmp")
FONT_ACCEPTS = ".ttf"
SOUND_ACCEPTS = (".wav", ".mp3", ".ogg", ".mdi")

ASSETS_DIR = "assets"
GFX_DIR = os.path.join(ASSETS_DIR, "graphics")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SFX_DIR = os.path.join(ASSETS_DIR, "sound")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
