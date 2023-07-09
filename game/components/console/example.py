"""
	Example of the use of the Console
	For showing/hiding console press F1
"""
from random import randint
from datetime import datetime

import pygame as pg

from .console import Console, get_console_config


class TestObject:
    """Testing object that will be govern by console.
    Print moving square on the screen with the console
    """

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((800, 600))
        self.clock = pg.time.Clock()

        self.pos = [0, 0]
        self.exit = False
        self.surf = pg.Surface((50, 50))
        self.surf.fill((255, 255, 255))

        """ Console integration code - START
            ********************************
        """
        # Generate random console config (no parameter) or specify the layout by nums 1 to 6
        console_config = get_console_config(1)

        # Create console based on the config - feel free to implement custom code to read the config directly from json
        self.console = Console(self, self.screen.get_width(), console_config)

        """ Console integration code - END
            ********************************
        """

    def update(self):
        while not self.exit:
            # Reset the screen
            self.screen.fill((125, 125, 0))

            # Move the square randomly
            self.pos[0] += randint(-2, 2)
            self.pos[1] += randint(-2, 2)

            # Test of puting something to the console
            # self.console.write('position X: ' + str(self.pos[0]))

            if self.pos[0] > 500:
                self.pos[0] = 500
            if self.pos[0] < 100:
                self.pos[0] = 100
            if self.pos[1] > 500:
                self.pos[1] = 500
            if self.pos[1] < 100:
                self.pos[1] = 100

            # Process the keys
            events = pg.event.get()
            for event in events:
                # Exit on closing of the window
                if event.type == pg.QUIT:
                    self.exit = True
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.exit = True
                elif event.type == pg.KEYUP:
                    # Toggle console on/off the console
                    if event.key == pg.K_F1:
                        # Toggle the console - if on then off if off then on
                        self.console.toggle()

            # Update the game situation - blit square on screen and position
            self.screen.blit(self.surf, (int(self.pos[0]), int(self.pos[1])))

            # Read and process events related to the console in case console is enabled
            self.console.update(events)

            # Display the console if enabled or animation is still in progress
            self.console.show(self.screen)

            pg.display.update()
            self.clock.tick(30)

    def move(self, line):
        """first argumet is movement on x-axis
        second argument is movement on y-axis
        """
        move_x, move_y = line.split(",")
        self.pos[0] += int(move_x)
        self.pos[1] += int(move_y)

    def cons_get_pos(self):
        """Example of function that can be passed to console to show dynamic
        data in the console
        """
        return str(self.pos)

    def cons_get_time(self):
        """Example of function that can be passed to console to show dynamic
        data in the console
        """
        return str(datetime.now())

    def cons_get_details(self):
        """Example of function that can be passed to console to show dynamic
        data in the console
        """

        return str(
            "Input text buffer possition: "
            + str(self.console.console_input.buffer_position)
            + " Input text position: "
            + str(len(self.console.console_input.input_string))
        )

    def cons_get_input_spacing(self):
        return str(
            "TextInput spacing: "
            + str(self.console.console_input.line_spacing)
            + " Cursor pos: "
            + str(self.console.console_input.cursor_position)
            + " Buffer pos: "
            + str(self.console.console_input.buffer_offset)
        )


if __name__ == "__main__":
    # Initiate testing 'game'
    t = TestObject()

    # Enter the infinite loop - press Esc to exit or type 'exit' into the console
    t.update()
