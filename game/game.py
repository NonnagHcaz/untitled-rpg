"""Main Game controller

Built from:
https://github.com/Mekire/pygame-mutiscene-template-with-movie
https://gist.github.com/iminurnamez/8d51f5b40032f106a847

"""
import pygame
from pygame.locals import K_RALT, K_RETURN, VIDEOEXPOSE, VIDEORESIZE, RESIZABLE
import pickle
import logging
from game import config

from game.utils.asset_cache import AssetCache


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

    def __init__(self, screen_size=None, caption=config.CAPTION, fps=config.FRAMERATE):
        pygame.init()

        if screen_size is None:
            screen_size = self.get_largest_display()

        self.original_caption = caption
        self.original_screen_size = screen_size
        self.original_fps = fps

        self.screen_size = self.original_screen_size
        self.caption = self.original_caption
        self.fps = self.original_fps

        self.screen_width, self.screen_height = self.screen_size

        pygame.display.set_caption(self.caption)
        self.screen = pygame.display.set_mode(self.screen_size, RESIZABLE)

        self.done = False
        self.clock = pygame.time.Clock()
        self.keys = pygame.key.get_pressed()

        self.show_fps = True
        self.current_time = 0.0

        self.scene_dict = {}
        self.current_scene_name = None
        self.current_scene = None
        self.previous_scene = None
        self.next_scene = None

        self.asset_cache = AssetCache()

    def get_largest_display(self):
        # Get the user's screen size
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        # Find the largest screen size that fits within the user's screen
        largest_size = (0, 0)
        for size in config.SCREEN_SIZES.values():
            if size[0] <= screen_width and size[1] <= screen_height:
                if size[0] > largest_size[0] and size[1] > largest_size[1]:
                    largest_size = size

        return largest_size

    def save_game(self, filename, scene_name="GAME"):
        scene = self.scene_dict.get(scene_name, self.current_scene)

        game_state = {
            "player_position": (
                scene.player.rect.x,
                scene.player.rect.y,
            ),
            # Add more game state variables as needed
        }
        with open(filename, "wb") as file:
            pickle.dump(game_state, file)
        logger.info("Game saved.")

    def load_game(self, filename):
        try:
            with open(filename, "rb") as file:
                game_state = pickle.load(file)
            # Update other game state variables as needed
            logger.info("Game loaded.")
        except FileNotFoundError:
            logger.warning("No save file found.")

        self.current_scene.next_scene = "GAME"
        self.flip_scene()

    def setup_scenes(self, scene_dict, start_scene):
        """Given a dictionary of States and a State to start in,
        builds the self.scene_dict."""
        self.scene_dict = scene_dict
        self.current_scene_name = start_scene
        self.current_scene = self.scene_dict[self.current_scene_name]
        self.current_scene.startup(self.current_time, None, self.screen)

    def event_loop(self):
        """Process all events and pass them down to current State.  The f5 key
        globally turns on/off the display of FPS in the caption"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                break
            elif event.type == pygame.KEYDOWN:
                self.keys = pygame.key.get_pressed()
                self.toggle_show_fps(event.key)
                if self.keys[K_RALT] and self.keys[K_RETURN]:
                    pygame.display.toggle_fullscreen()
            elif event.type == VIDEORESIZE:
                r0 = self.screen.copy().get_rect()
                self.screen = pygame.display.get_surface()
                r1 = self.screen.copy().get_rect()

            self.current_scene.get_event(event)

    def flip_scene(self):
        """When a State changes to done necessary startup and cleanup functions
        are called and the current State is changed."""
        self.previous_scene, self.current_scene_name = (
            self.current_scene,
            self.current_scene.next_scene,
        )
        persist = self.current_scene.cleanup()
        try:
            self.next_scene = self.scene_dict[self.current_scene_name]
            self.next_scene.startup(self.current_time, persist, self.screen)
            self.next_scene.previous_scene = self.previous_scene
            self.current_scene = self.next_scene
        except KeyError:
            self.done = True

    def update(self, dt):
        """
        Check for scene flip and update active scene.

        dt: milliseconds since last frame
        """
        self.screen.fill((0, 0, 0))
        self.current_time = pygame.time.get_ticks()
        self.keys = pygame.key.get_pressed()
        if self.current_scene.quit:
            self.done = True
        elif self.current_scene.done:
            self.flip_scene()

        if not self.done:
            self.current_scene.update(self.screen, self.current_time, dt)
            fps = self.clock.get_fps()
            with_fps = f"{self.caption} - {fps:.2f} FPS - {self.current_scene.zoom*100:.0f}% Zoom"
            pygame.display.set_caption(with_fps)

    def toggle_show_fps(self, key):
        """Press f5 to turn on/off displaying the framerate in the caption."""
        if key == pygame.K_F3:
            self.show_fps = not self.show_fps
            if not self.show_fps:
                pygame.display.set_caption(self.caption)

    def run(self):
        """
        Pretty much the entirety of the game's runtime will be
        spent inside this while loop.
        """
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            pygame.display.update()
        pygame.quit()
