"""
The splash screen of the game. The first thing the user sees.
"""

import glob
import os
import re
import pygame

from game import utils

from .scene import Scene
from .. import config


class LoadingScene(Scene):
    def __init__(self, game, asset_cache, next_scene=None, previous_scene=None):
        super().__init__(
            game=game,
            asset_cache=asset_cache,
            next_scene=next_scene,
            previous_scene=previous_scene,
        )


class StartupScene(LoadingScene):
    def __init__(self, game, asset_cache, next_scene=None, previous_scene=None):
        super().__init__(
            game=game,
            asset_cache=asset_cache,
            next_scene=next_scene,
            previous_scene=previous_scene,
        )

        self.assets = [
            ("font", filepath, 24)
            for filepath in utils.get_filepaths(config.FONT_DIR, *config.FONT_ACCEPTS)
        ]
        self.assets += [
            ("image", filepath)
            for filepath in utils.get_filepaths(config.GFX_DIR, *config.IMAGE_ACCEPTS)
        ]

        self.assets += [
            ("sound", filepath)
            for filepath in utils.get_filepaths(config.SFX_DIR, *config.SOUND_ACCEPTS)
        ]

        self.assets += [
            ("sound", filepath)
            for filepath in utils.get_filepaths(config.MUSIC_DIR, *config.SOUND_ACCEPTS)
        ]

        self.mappers = utils.get_filepaths(config.GFX_DIR, ".txt")

        self.total_assets = len(self.assets)

        self.loaded_assets = 0
        self.wait = False

    def get_event(self, event):
        """Get events from Control. Currently changes to next scene on any key
        press."""
        if event.type == pygame.KEYDOWN and self.wait:
            self.done = True

    def handle_events(self):
        if self.loaded_assets >= len(self.assets):
            self.wait = True

    @property
    def is_done_loading(self):
        return self.loaded_assets >= len(self.assets)

    def update(self, surface, current_time, dt):
        super().update(surface, current_time)
        self.handle_events()
        # Load the assets
        if self.is_done_loading:
            self.loading_text = f"Loading done! Press any key to continue..."
        else:
            for asset in self.assets:
                asset_type = asset[0]
                if asset_type == "image":
                    filename = asset[1]
                    mapper = re.sub(
                        "|".join([x for x in config.IMAGE_ACCEPTS]), ".txt", filename
                    )
                    if mapper not in self.mappers:
                        mapper = None
                    image = self.asset_cache.load_image(filename, mapper)
                    if isinstance(image, list):
                        _x = len(image) - 1
                        self.total_assets += _x
                        self.loaded_assets += _x
                elif asset_type == "font":
                    filename = asset[1]
                    size = asset[2]
                    self.asset_cache.load_font(filename, font_size=size)
                elif asset_type == "sound":
                    filename = asset[1]
                    self.asset_cache.load_sound(filename)
                # Add more asset types as needed

                # Update the loaded assets count
                self.loaded_assets += 1
                self.loading_text = (
                    f"Loading... {self.loaded_assets}/{self.total_assets}"
                )
        self.render(surface)

    def render(self, surface):
        screen_width, screen_height = surface.get_rect().size
        loading_bar_width = min(400, screen_width * 0.75)
        loading_bar_height = 20
        loading_bar_x = (screen_width - loading_bar_width) // 2
        loading_bar_y = (screen_height - loading_bar_height) // 2
        surface.fill((0, 0, 0))

        # Draw loading bar
        bar_width = int(loading_bar_width * (self.loaded_assets / self.total_assets))
        loading_bar_rect = pygame.Rect(
            loading_bar_x, loading_bar_y, bar_width, loading_bar_height
        )
        pygame.draw.rect(surface, config.STAMINA_GREEN, loading_bar_rect)

        # Draw loading text

        font = pygame.font.Font(os.path.join(config.FONT_DIR, "PixeloidSans.ttf"), 24)
        text_surface = font.render(self.loading_text, True, pygame.Color("white"))
        text_rect = text_surface.get_rect(
            center=(screen_width // 2, screen_height // 2 + 50)
        )
        surface.blit(text_surface, text_rect)

        pygame.display.flip()
