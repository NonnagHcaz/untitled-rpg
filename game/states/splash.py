"""
The splash screen of the game. The first thing the user sees.
"""

import pygame
from game.components.sprites.text.text import Text

from game.utils.asset_cache import _fn

from .state import GameState
from .. import config
import os


class SplashState(GameState):
    """This State is updated while our game shows the splash screen."""

    def __init__(self, game, asset_cache):
        super().__init__(game, asset_cache)
        self.timeout = 5

    def startup(self, current_time, persistant, surface):
        self.font_file = "assets/fonts/PixeloidSans.ttf"
        self.font = pygame.font.Font(self.font_file, 64)
        self.image = self.font.render(
            "A Game By NonnagHcaz", True, pygame.Color("white")
        )
        # self.image = self.asset_cache[_fn(os.path.join(config.GFX_DIR, "splash1.png"))]
        self.rect = self.image.get_rect(center=surface.get_rect().center)
        self.cover = surface.copy().convert()
        self.cover.fill(0)
        self.cover_alpha = 256
        self.alpha_step = 2
        return super().startup(current_time, persistant, surface)

    def update(self, surface, current_time, time_delta):
        """Updates the splash screen."""
        super().update(surface, current_time)
        surface.blit(self.image, self.rect)
        self.cover.set_alpha(self.cover_alpha)
        self.cover_alpha = max(self.cover_alpha - self.alpha_step, 0)
        surface.blit(self.cover, (0, 0))
        if self.current_time - self.start_time > 1000.0 * self.timeout:
            self.done = True

    def get_event(self, event):
        """Get events from Control. Currently changes to next state on any key
        press."""
        if event.type == pygame.KEYDOWN:
            self.done = True
