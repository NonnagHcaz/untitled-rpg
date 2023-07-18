import os
from typing import Any
import pygame
from pygame.sprite import Group, Sprite
from game import config

from game.scenes.scene import Scene
from game.utils import resource_path

import logging

logger = logging.getLogger(__name__)


class MenuSprite(Sprite):
    def __init__(self, image: pygame.Surface, *groups: Group) -> None:
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect()

    def update(self, *args: Any, **kwargs: Any) -> None:
        return super().update(*args, **kwargs)

    def render(self, surface):
        pass

    @property
    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)


class MenuText(MenuSprite):
    def __init__(self, text, font, color=pygame.Color("white"), *groups):
        super().__init__(font.render(text, True, color), *groups)


class MenuButton(MenuText):
    def __init__(
        self,
        text,
        font,
        color=pygame.Color("white"),
        hover_color=config.STAMINA_GREEN,
        onclick=None,
        padding=(10, 5),
        border_color=pygame.Color("white"),
        border_width=2,
        hover_border_color=config.STAMINA_GREEN,
        hover_border_width=2,
        hover_background_color=None,
        focus_color=pygame.Color("yellow"),
        focus_border_color=pygame.Color("yellow"),
        focus_border_width=2,
        *groups,
    ):
        super().__init__(text, font, color, *groups)
        self.hover_color = hover_color
        self.onclick = onclick
        self.padding = padding
        self.border_color = border_color
        self.border_width = border_width
        self.hover_border_color = hover_border_color
        self.hover_border_width = hover_border_width
        self.hover_background_color = hover_background_color
        self.focus_color = focus_color
        self.focus_border_color = focus_border_color
        self.focus_border_width = focus_border_width
        self.is_focused = False
        self.text = text
        self.font = font
        self.color = color

    def update(self, *args, **kwargs):
        if self.is_focused:
            self.image = self._render_button(
                self.focus_color,
                self.focus_border_color,
                self.focus_border_width,
                self.hover_background_color,
            )
        elif self.is_hovered:
            self.image = self._render_button(
                self.hover_color,
                self.hover_border_color,
                self.hover_border_width,
                self.hover_background_color,
            )
        else:
            self.image = self._render_button(
                self.color,
                self.border_color,
                self.border_width,
                None,
            )

    def _render_button(
        self,
        text_color,
        border_color,
        border_width,
        background_color=None,
    ):
        button_width = self.font.size(self.text)[0] + self.padding[0] * 2
        button_height = self.font.get_height() + self.padding[1] * 2

        button_image = pygame.Surface((button_width, button_height))
        button_image.fill(background_color or pygame.Color("black"))
        button_image.fill(border_color, pygame.Rect(0, 0, button_width, border_width))
        button_image.fill(border_color, pygame.Rect(0, 0, border_width, button_height))
        button_image.fill(
            border_color,
            pygame.Rect(button_width - border_width, 0, border_width, button_height),
        )
        button_image.fill(
            border_color,
            pygame.Rect(0, button_height - border_width, button_width, border_width),
        )

        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(
            center=(button_width // 2, button_height // 2)
        )
        button_image.blit(text_surface, text_rect)

        return button_image


class MainMenuScene(Scene):
    def __init__(self, game, asset_cache, next_scene=None, previous_scene=None):
        super().__init__(
            game=game,
            asset_cache=asset_cache,
            next_scene=next_scene,
            previous_scene=previous_scene,
        )

        self.options = [
            ("Start Game", self.start_game),
            ("Load Game", self.load_game),
            ("Options", self.goto_options),
            ("Exit", self.exit_game),
        ]
        self.heading_text = config.CAPTION
        self.button_padding = (10, 5)
        self.button_margin = 5

        self.elements = []

        self.font_file = config.FONT_FILE
        self.heading_font_size = 32
        self.button_font_size = 24

        self.all_sprites = Group()
        self.buttons = Group()

    def startup(self, current_time, persistant, surface):
        self.current_button_index = 0  # reset focused button
        self.create_menu_elements()
        return super().startup(current_time, persistant, surface)

    def create_menu_elements(self):
        heading_font = pygame.font.Font(self.font_file, self.heading_font_size)
        heading_text_surface = heading_font.render(
            self.heading_text, True, pygame.Color("white")
        )
        heading_text_rect = heading_text_surface.get_rect(
            center=(self.screen_width // 2, self.screen_height // 4)
        )
        heading = MenuText(self.heading_text, heading_font)
        heading.rect = heading_text_rect

        button_font = pygame.font.Font(self.font_file, self.button_font_size)
        button_height = button_font.get_height()
        total_height = (
            button_height + self.button_padding[1] * 2 + self.button_margin * 2
        )
        current_y = (self.screen_height - total_height * len(self.options)) // 2

        for text, action in self.options:
            button = MenuButton(
                text,
                button_font,
                padding=self.button_padding,
                onclick=action,
            )
            button.rect = pygame.Rect(
                (self.screen_width - button.rect.width) // 2,
                current_y,
                button.rect.width,
                button.rect.height,
            )
            self.buttons.add(button)

            current_y += total_height

        self.all_sprites.add(heading)
        self.all_sprites.add(self.buttons)

        if self.buttons.sprites():
            self.buttons.sprites()[self.current_button_index].is_focused = True

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event.key)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.handle_click(event.pos)

    def handle_click(self, pos):
        for button in self.buttons.sprites():
            if button.rect.collidepoint(pos):
                button.onclick()

    def handle_keydown(self, key):
        if key == pygame.K_UP:
            self.move_focus_up()
        elif key == pygame.K_DOWN:
            self.move_focus_down()
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            self.execute_current_button()

    def move_focus_up(self):
        if self.buttons.sprites():
            self.buttons.sprites()[self.current_button_index].is_focused = False
            self.current_button_index = (self.current_button_index - 1) % len(
                self.buttons.sprites()
            )
            self.buttons.sprites()[self.current_button_index].is_focused = True

    def move_focus_down(self):
        if self.buttons.sprites():
            self.buttons.sprites()[self.current_button_index].is_focused = False
            self.current_button_index = (self.current_button_index + 1) % len(
                self.buttons.sprites()
            )
            self.buttons.sprites()[self.current_button_index].is_focused = True

    def execute_current_button(self):
        if self.buttons.sprites():
            button = self.buttons.sprites()[self.current_button_index]
            button.onclick()

    def start_game(self):
        logger.debug("Switching to GameplayState")
        self.next_scene = "GAME"
        self.done = True

    def load_game(self):
        self.next_scene = "GAME"
        self.done = True
        self.game.load_game(config.SAVE_FILE, "GAME")

    def goto_options(self):
        logger.debug("Switching to OptionMenuState")
        self.next_scene = "OPTIONS"
        self.done = True

    def exit_game(self):
        self.game.done = True

    def update(self, surface, current_time, dt):
        super().update(surface, current_time)
        self.all_sprites.update()
        self.buttons.update()
        self.render(surface)

    def render(self, surface):
        surface.fill((0, 0, 0))

        for sprite in self.all_sprites:
            surface.blit(sprite.image, sprite.rect)


class PauseMenuScene(MainMenuScene):
    def __init__(self, game, asset_cache, next_scene=None, previous_scene=None):
        super().__init__(
            game=game,
            asset_cache=asset_cache,
            next_scene=next_scene,
            previous_scene=previous_scene,
        )
        self.options = [
            ("Resume", self.resume_game),
            ("Save Game", self.save_game),
            ("Options", self.goto_options),
            ("Quit to Menu", self.quit_to_menu),
        ]
        self.heading_text = "Paused"

    def resume_game(self):
        logger.debug("Switching to GameplayState")
        self.next_scene = "GAME"
        self.done = True

    def save_game(self):
        self.next_scene = "GAME"
        self.done = True
        self.game.save_game(config.SAVE_FILE, "GAME")

    def quit_to_menu(self):
        self.next_scene = "MENU"
        self.done = True

    def get_event(self, event):
        super().get_event(event)
        if (
            self.current_time - self.start_time > 1 / 1000
            and event.type == pygame.KEYUP
            and event.key == pygame.K_ESCAPE
        ):
            self.resume_game()


class OptionsMenuScene(MainMenuScene):
    def __init__(self, game, asset_cache, next_scene=None, previous_scene=None):
        super().__init__(
            game=game,
            asset_cache=asset_cache,
            next_scene=next_scene,
            previous_scene=previous_scene,
        )
        self.options = [
            ("Back", self.goto_previous_scene),
            # ("Save Game", self.save_game),
            # ("Quit to Menu", self.quit_to_menu),
        ]
        self.heading_text = "Options"

    def goto_previous_scene(self):
        logger.debug(f"Switching to {self.previous_scene}")
        self.next_scene = self.previous_scene
        self.done = True

    def get_event(self, event):
        super().get_event(event)
        if (
            self.current_time - self.start_time > 1 / 1000
            and event.type == pygame.KEYUP
            and event.key == pygame.K_ESCAPE
        ):
            self.goto_previous_scene()
