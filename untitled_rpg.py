import sys
import os
import logging
from game import config
from game.scenes.menu import MainMenu, PauseMenu

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/debug.log", filemode="w", level=logging.DEBUG)

from game.game import Game
from game.scenes import Gameplay, SplashState, StartupScene

if __name__ == "__main__":
    game = Game()
    config = {"game": game, "asset_cache": game.asset_cache}
    states = {
        "SPLASH": SplashState(**config),
        "GAME": Gameplay(**config),
        "STARTUP": StartupScene(**config),
        "MENU": MainMenu(**config),
        "PAUSE": PauseMenu(**config),
    }
    states["STARTUP"].next_state = "SPLASH"
    states["SPLASH"].next_state = "MENU"

    game.setup_states(states, "STARTUP")
    game.run()
