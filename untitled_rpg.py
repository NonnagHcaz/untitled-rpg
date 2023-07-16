import sys
import os
import logging
from game import config
from game.scenes.menu import MainMenuScene, PauseMenuScene
from game.scenes.splash import SplashScene
from game.scenes.gameplay import GameplayScene
from game.scenes.loading import StartupScene

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/debug.log", filemode="w", level=logging.DEBUG)

from game.game import Game


if __name__ == "__main__":
    game = Game()
    config = {"game": game, "asset_cache": game.asset_cache}
    states = {
        "SPLASH": SplashScene(**config),
        "GAME": GameplayScene(**config),
        "STARTUP": StartupScene(**config),
        "MENU": MainMenuScene(**config),
        "PAUSE": PauseMenuScene(**config),
    }
    states["STARTUP"].next_state = "SPLASH"
    states["SPLASH"].next_state = "MENU"

    game.setup_states(states, "STARTUP")
    game.run()
