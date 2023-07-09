import sys

import logging
from game import prepare

logging.basicConfig(level=logging.DEBUG)  # , filename='debug.log', filemode='w')

from game.game import Game
from game.states import Gameplay, Splash

if __name__ == "__main__":
    game = Game(prepare.ORIGINAL_CAPTION)
    states = {"SPLASH": Splash(), "GAME": Gameplay()}
    game.setup_states(states, "SPLASH")
    game.run()
