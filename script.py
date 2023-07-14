import sys

import logging
from game import config
from game.states.menu import MenuState, PauseState

logging.basicConfig(level=logging.DEBUG)  # , filename='debug.log', filemode='w')

from game.game import Game
from game.states import Gameplay, SplashState, LoadState

if __name__ == "__main__":
    game = Game()
    config = {"game": game, "asset_cache": game.asset_cache}
    states = {
        "SPLASH": SplashState(**config),
        "GAME": Gameplay(**config),
        "START": LoadState(**config),
        "MENU": MenuState(**config),
        "PAUSE": PauseState(**config),
    }
    states["START"].next_state = "SPLASH"
    states["SPLASH"].next_state = "MENU"

    game.setup_states(states, "START")
    game.run()
