# https://gist.github.com/iminurnamez/8d51f5b40032f106a847

import pygame

from game.camera.camera import CameraAwareLayeredUpdates


class Scene(object):
    """This is a prototype class for States.  All scenes should inherit from it.
    No direct instances of this class should be created. get_event and update
    must be overloaded in the childclass.  startup and cleanup need to be
    overloaded when there is data that must persist between States."""

    def __init__(self, game, asset_cache, next_scene=None, previous_scene=None):
        self.previous_scene = previous_scene
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.quit = False
        self.persist = {}
        self.screen = None
        self.total_frames = 0
        self.blink = False
        self.timer = 0.0
        self.zoom = 1.0

        self.game = game
        self.asset_cache = asset_cache
        self.next_scene = next_scene
        self.screen = self.game.screen.copy()
        self.screen_rect = self.screen.get_rect()
        self.screen_size = self.screen_rect.size
        self.screen_width, self.screen_height = self.screen_size

    def group_to_list(self, group):
        data = []
        for sprite in group:
            try:
                sprite_data = sprite.get_data()
            except AttributeError as ex:
                print(str(ex))
            else:
                data.append(sprite_data)
        return data

    @property
    def game_state(self):
        raw_game_state = self.game_groups
        game_state = {}
        for attr, val in raw_game_state.items():
            if isinstance(val, pygame.sprite.Group) or isinstance(
                val, CameraAwareLayeredUpdates
            ):
                game_state[attr] = self.group_to_list(val)
            elif isinstance(val, pygame.sprite.Sprite):
                try:
                    game_state[attr] = val.get_data()
                except AttributeError:
                    pass
        return game_state

    @property
    def game_groups(self):
        return {}

    def get_event(self, event):
        """Processes events that were passed from the main event loop.
        Must be overloaded in children."""
        pass

    def startup(self, current_time, persistant, surface):
        """Add variables passed in persistant to the proper attributes and
        set the start time of the State to the current time."""
        self.screen = surface.copy()
        self.persist = persistant
        self.start_time = current_time

    def cleanup(self):
        """Add variables that should persist to the self.persist dictionary.
        Then reset State.done to False."""
        self.done = False
        return self.persist

    def update(self, surface, current_time):
        """Update function for scene.  Must be overloaded in children."""
        self.current_time = current_time
        self.total_frames += 1

        if self.current_time - self.timer > 1000.0 / 5.0:
            self.blink = not self.blink
            self.timer = self.current_time
