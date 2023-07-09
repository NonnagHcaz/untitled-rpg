# https://gist.github.com/iminurnamez/8d51f5b40032f106a847

import pygame as pg


class GameState(object):
    """This is a prototype class for States.  All states should inherit from it.
    No direct instances of this class should be created. get_event and update
    must be overloaded in the childclass.  startup and cleanup need to be
    overloaded when there is data that must persist between States."""

    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.persist = {}
        self.screen = None
        self.total_frames = 0
        self.blink = False
        self.timer = 0.0

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
        """Update function for state.  Must be overloaded in children."""
        self.current_time = current_time
        self.total_frames += 1

        self.events = pg.event.get()
        self.pressed_keys = pg.key.get_pressed()
        self.pressed_btns = pg.mouse.get_pressed(num_buttons=5)
        self.mouse_pos = pg.mouse.get_pos()

        if self.current_time - self.timer > 1000.0 / 5.0:
            self.blink = not self.blink
            self.timer = self.current_time
