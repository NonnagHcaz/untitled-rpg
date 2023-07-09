"""https://gist.github.com/iminurnamez/8d51f5b40032f106a847"""
import pygame as pg
from pygame.locals import K_RALT, K_RETURN, VIDEOEXPOSE, VIDEORESIZE

import logging

from game import prepare

logger = logging.getLogger(__name__)


class Game(object):
    """
    A single instance of this class is responsible for
    managing which individual game state is active
    and keeping it updated. It also handles many of
    pygame's nuts and bolts (managing the event
    queue, fps, updating the display, etc.).
    and its run method serves as the "game loop".
    """

    def __init__(self, caption):
        self.screen = pg.display.get_surface()
        self.screen_width, self.screen_height = self.screen.get_rect().size
        self.caption = caption
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = prepare.FRAMERATE
        self.show_fps = True
        self.current_time = 0.0
        self.keys = pg.key.get_pressed()
        self.state_dict = {}
        self.state_name = None
        self.state = None

    def setup_states(self, state_dict, start_state):
        """Given a dictionary of States and a State to start in,
        builds the self.state_dict."""
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, None, self.screen)

    def event_loop(self):
        """Process all events and pass them down to current State.  The f5 key
        globally turns on/off the display of FPS in the caption"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                break
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
                if self.keys[K_RALT] and self.keys[K_RETURN]:
                    pg.display.toggle_fullscreen()
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            elif event.type == VIDEORESIZE:
                r0 = self.screen.copy().get_rect()
                self.screen = pg.display.get_surface()
                r1 = self.screen.copy().get_rect()

            self.state.get_event(event)

    def flip_state(self):
        """When a State changes to done necessary startup and cleanup functions
        are called and the current State is changed."""
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist, self.screen)
        self.state.previous = previous

    def update(self, dt):
        """
        Check for state flip and update active state.

        dt: milliseconds since last frame
        """
        self.screen.fill((0, 0, 0))
        self.current_time = pg.time.get_ticks()
        self.keys = pg.key.get_pressed()
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()

        if not self.done:
            self.state.update(self.screen, self.current_time, dt)
            fps = self.clock.get_fps()
            with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
            pg.display.set_caption(with_fps)

    def toggle_show_fps(self, key):
        """Press f5 to turn on/off displaying the framerate in the caption."""
        if key == pg.K_F3:
            self.show_fps = not self.show_fps
            if not self.show_fps:
                pg.display.set_caption(self.caption)

    def run(self):
        """
        Pretty much the entirety of the game's runtime will be
        spent inside this while loop.
        """
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            pg.display.update()
        pg.quit()
