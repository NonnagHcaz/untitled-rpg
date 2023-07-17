import os
import logging
from game.scenes.menu import MainMenuScene, PauseMenuScene, OptionsMenuScene
from game.scenes.splash import SplashScene
from game.scenes.gameplay import GameplayScene
from game.scenes.loading import StartupScene

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/debug.log", filemode="w", level=logging.DEBUG)

from game.game import Game
from game import config

__version__ = (0, 0, 2)

config.CAPTION += f" v{'.'.join([str(x) for x in __version__])}"

if __name__ == "__main__":
    game = Game()
    kwargs = {"game": game, "asset_cache": game.asset_cache}
    scenes = {
        "SPLASH": SplashScene(**kwargs),
        "GAME": GameplayScene(**kwargs),
        "STARTUP": StartupScene(**kwargs),
        "MENU": MainMenuScene(**kwargs),
        "PAUSE": PauseMenuScene(**kwargs),
        "OPTIONS": OptionsMenuScene(**kwargs),
    }
    scenes["STARTUP"].next_scene = "SPLASH"
    scenes["SPLASH"].next_scene = "MENU"

    game.setup_scenes(scenes, "STARTUP")
    game.run()
