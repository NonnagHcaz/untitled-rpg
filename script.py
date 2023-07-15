import sys
import os
import logging
from game import config
from game.states.menu import MenuState, PauseState

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/debug.log", filemode="w")

from game.game import Game
from game.states import Gameplay, SplashState, StartupState

if __name__ == "__main__":
    game = Game()
    config = {"game": game, "asset_cache": game.asset_cache}
    states = {
        "SPLASH": SplashState(**config),
        "GAME": Gameplay(**config),
        "STARTUP": StartupState(**config),
        "MENU": MenuState(**config),
        "PAUSE": PauseState(**config),
    }
    states["STARTUP"].next_state = "SPLASH"
    states["SPLASH"].next_state = "MENU"

    game.setup_states(states, "STARTUP")
    game.run()
