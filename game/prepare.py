"""
This module initializes the display and creates dictionaries of resources.
"""

import os
import pygame as pg
from pygame.locals import FULLSCREEN, RESIZABLE

from .utils import loaders

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
ORIGINAL_CAPTION = "Zelda Clone"
TEXTURE_SCALE = 1


# Initialization
pg.init()
os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
pg.display.set_caption(ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(SCREEN_SIZE, RESIZABLE)
SCREEN_RECT = SCREEN.get_rect()


# Resource loading (Fonts and music just contain path names).
FONTS = loaders.load_all_fonts(os.path.join("assets", "fonts"))
MUSIC = loaders.load_all_music(os.path.join("assets", "music"))
SFX = loaders.load_all_sfx(os.path.join("assets", "sound"))
MOV = loaders.load_all_movies(os.path.join("assets", "movies"))
GFX = loaders.load_all_gfx(os.path.join("assets", "graphics"))
