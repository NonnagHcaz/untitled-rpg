"""
The splash screen of the game. The first thing the user sees.
"""

import pygame

from .state import GameState
from .. import config


class MenuState(GameState):
    def __init__(self, game, asset_cache):
        super().__init__(game, asset_cache)

        self.options = {
            pygame.K_1: "Start Game",
            pygame.K_2: "Load Game",
            pygame.K_3: "Exit",
        }
        self.heading_text = "Menu"
        self.button_padding = 5
        self.button_margin = 5

        self.font_file = "assets/fonts/PixeloidSans.ttf"

    def get_event(self, event):
        """Get events from Control. Currently changes to next state on any key
        press."""
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event.key)

    def handle_events(self):
        pass

    def handle_keydown(self, key):
        if key in self.options:
            option = self.options[key]
            if option == "Start Game":
                print("Switching to GameplayState")
                self.next_state = "GAME"
                self.done = True
            elif option == "Load Game":
                self.next_state = "GAME"
                self.done = True
                self.game.load_game("savegame.dat", "GAME")
            elif option == "Exit":
                # self.done = True
                self.game.done = True

    def update(self, surface, current_time, dt):
        super().update(surface, current_time)
        self.render(surface)

    def render(self, surface):
        surface.fill((0, 0, 0))
        screen_width, screen_height = surface.get_rect().size

        # Draw heading
        heading_font = pygame.font.Font(self.font_file, 32)
        heading_text_surface = heading_font.render(
            self.heading_text, True, pygame.Color("white")
        )
        heading_text_rect = heading_text_surface.get_rect(
            center=(screen_width // 2, 100)
        )
        surface.blit(heading_text_surface, heading_text_rect)

        # Draw buttons
        button_font = pygame.font.Font(self.font_file, 24)
        button_height = button_font.get_height()
        total_height = button_height + self.button_padding * 2 + self.button_margin * 2
        current_y = (screen_height - total_height * len(self.options)) // 2

        for key, text in self.options.items():
            button_text_surface = button_font.render(text, True, pygame.Color("white"))
            button_text_rect = button_text_surface.get_rect(
                center=(screen_width // 2, current_y + button_height // 2)
            )
            pygame.draw.rect(
                surface,
                pygame.Color("green"),
                button_text_rect.inflate(
                    self.button_padding * 2, self.button_padding * 2
                ),
                1,
            )
            surface.blit(button_text_surface, button_text_rect)

            current_y += total_height

        pygame.display.flip()


class PauseState(MenuState):
    def __init__(self, game, asset_cache):
        super().__init__(game, asset_cache)
        self.options = {
            pygame.K_1: "Resume",
            pygame.K_2: "Save Game",
            pygame.K_3: "Quit to Menu",
        }
        self.heading_text = "Paused"

    def handle_keydown(self, key):
        if key in self.options:
            option = self.options[key]
            if option == "Resume":
                print("Switching to GameplayState")
                self.next_state = "GAME"
                self.done = True
            elif option == "Save Game":
                self.next_state = "GAME"
                self.done = True
                self.game.save_game("savegame.dat", "GAME")
            elif option == "Quit to Menu":
                self.next_state = "MENU"
                self.done = True
