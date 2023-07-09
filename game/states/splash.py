"""
The splash screen of the game. The first thing the user sees.
"""

import pygame as pg

from .state import GameState
from .. import prepare


class Splash(GameState):
    """This State is updated while our game shows the splash screen."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next = "GAME"
        self.timeout = 5
        self.cover = pg.Surface((prepare.SCREEN_SIZE)).convert()
        self.cover.fill(0)
        self.cover_alpha = 256
        self.alpha_step = 2
        self.image = prepare.GFX["splash1"]
        self.rect = self.image.get_rect(center=prepare.SCREEN_RECT.center)

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
        if event.type == pg.KEYDOWN:
            self.done = True
