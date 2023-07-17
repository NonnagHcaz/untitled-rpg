import datetime
import math
import os
import random
import pygame
from pygame.locals import (
    KEYDOWN,
    KEYUP,
    K_ESCAPE,
    K_F1,
    K_F9,
    K_r,
    QUIT,
    MOUSEBUTTONUP,
    K_PAGEUP,
    K_PAGEDOWN,
)

from game.components.camera.camera import Camera, CameraAwareLayeredUpdates
from game.components.sprites.cursor.cursor import Cursor

from game.components.sprites.shape.shape import Hitbox
from game.components.sprites.status_bar.status_bar import TargetedStatusBar


import logging
from game.components.sprites.text.textbox import TargetedTextBox
from game.components.sprites.ui.status_bar import UIHealthBar, UIManaBar, UIStaminaBar
from game.level import Dungeon

from game.scenes.scene import Scene
from game.utils import resource_path
from game.utils.asset_cache import _fn
from game.utils.controls import Controls
from game.utils.events import ADDENEMY

logger = logging.getLogger(__name__)

from .. import config

# pygame.mouse.set_visible(False)


class GameplayScene(Scene):
    def __init__(self, game, asset_cache, next_scene=None, previous_scene=None):
        super().__init__(
            game=game,
            asset_cache=asset_cache,
            next_scene=next_scene,
            previous_scene=previous_scene,
        )
        self.level = None
        self.player = None
        self.enemies = None
        self.hitboxes = None
        self.projectiles = None
        self.walls = None
        self.floors = None
        self.all_sprites = None
        self.debug = True
        self.zoom = 1
        self.font_file = resource_path("assets/fonts/PixeloidSans.ttf")

    def startup(self, current_time, persistent, surface):
        super().startup(current_time, persistent, surface)
        pygame.mouse.set_visible(False)
        pygame.time.set_timer(ADDENEMY, config.DEFAULT_ENEMY_SPAWN_TIMER)
        # pygame.mixer.music.load(self.bgm)
        # pygame.mixer.music.play(-1)
        self.cam = Camera()

        self.bgm = None
        self.font = None

        self.controls = Controls()

        self.ui_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.player_projectiles = pygame.sprite.Group()
        self.player_sprites = pygame.sprite.Group()
        self.projectiles.add(self.player_projectiles, self.enemy_projectiles)
        self.hitboxes = pygame.sprite.Group()
        self.status_bars = pygame.sprite.Group()
        self.texts = pygame.sprite.Group()

        level_width = 16 * 250
        level_height = 9 * 250

        self.level = Dungeon(
            width=level_width,
            height=level_height,
            display_width=self.screen.get_rect().width,
            display_height=self.screen.get_rect().height,
            cache=self.asset_cache,
        )

        self.floor = self.level.build_test_floor()
        self.walls = self.level.build_test_walls()

        self.respawn()

        self.cursor = Cursor(
            name="cursor",
            image=self.asset_cache[
                _fn(os.path.join(config.GFX_DIR, "crosshair_1.png"))
            ],
            cam=self.cam,
        )

        # cursor_text = TargetedTextBox(
        #     target=self.cursor,
        #     text=self.cursor.diagnostics_pretty,
        #     max_width=self.cursor.rect.width * 2,
        # )
        # self.cursor.text = cursor_text

        ui_bar_offset = 10

        ui_healthbar = UIHealthBar(
            width=min(self.screen_width * 0.3, 500),
            height=30,
            target=self.player,
            offset=0,
            current_attribute="health",
            max_attribute="base_health",
        )
        ui_healthbar.rect.topleft = (ui_bar_offset, ui_bar_offset)

        ui_manabar = UIManaBar(
            width=min(
                self.screen_width * 0.2 - ui_bar_offset / 2, 300 - ui_bar_offset / 2
            ),
            height=30,
            target=self.player,
            offset=0,
            current_attribute="mana",
            max_attribute="base_mana",
        )
        ui_manabar.rect.topleft = (
            ui_bar_offset,
            ui_bar_offset + ui_healthbar.height + ui_bar_offset,
        )

        ui_staminabar = UIStaminaBar(
            width=min(
                self.screen_width * 0.1 - ui_bar_offset / 2, 200 - ui_bar_offset / 2
            ),
            height=30,
            target=self.player,
            offset=0,
            current_attribute="stamina",
            max_attribute="base_stamina",
        )
        ui_staminabar.rect.topleft = (
            ui_bar_offset + ui_manabar.width + ui_bar_offset,
            ui_bar_offset + ui_healthbar.height + ui_bar_offset,
        )

        self.ui_sprites.add(self.cursor, ui_healthbar, ui_manabar, ui_staminabar)

        self.mp_line = pygame.sprite.Sprite()
        self.max_enemies = self.level.width // 100
        while len(self.enemies) < self.max_enemies:
            sprite = self.spawn_random_enemy()

        self.all_sprites = CameraAwareLayeredUpdates(
            target=self.player,
            world_size=pygame.Rect(0, 0, level_width, level_height),
            cam=self.cam,
        )

        self.all_sprites.add(self.floor, layer=-1)
        self.all_sprites.add(self.walls, layer=1)
        self.all_sprites.add(self.enemies, layer=2)
        # self.all_sprites.add(self.hitboxes, layer=3)
        self.all_sprites.add(self.status_bars, layer=3)
        self.all_sprites.add(self.texts, layer=3)
        self.all_sprites.add(self.player_sprites)
        for group in [self.player_sprites]:
            for sprite in group:
                self.all_sprites.move_to_front(sprite)

    def spawn_random_enemy(self):
        perc = 0.2
        x = random.randint(
            int(self.level.width * perc), int(self.level.width * (1.0 - perc))
        )
        y = random.randint(
            int(self.level.height * perc), int(self.level.height * (1.0 - perc))
        )
        sprite = self.level.spawn_random_enemy(pos=(x, y))
        sprite.debug = self.debug

        status_bar = TargetedStatusBar(
            font_file=self.font_file,
            target=sprite,
            offset=5,
            width=sprite.rect.width * 2,
            primary_color=config.HEALTH_RED,
            border_color=pygame.Color("white"),
            border_width=2,
            current_attribute="health",
            max_attribute="base_health",
        )

        debug_textbox = TargetedTextBox(
            target=sprite,
            angle=-90,
            font_file=self.font,
            text={"func": sprite.diagnostics_pretty, "args": [self.cam]},
            max_width=sprite.rect.width * 2,
        )

        sprite.status_bars = [status_bar]
        sprite.debug_textbox = debug_textbox

        self.enemies.add(sprite)
        # self.hitboxes.add(Hitbox(target=sprite))
        self.status_bars.add(status_bar)
        self.texts.add(debug_textbox)
        if self.all_sprites:
            self.all_sprites.add(status_bar, debug_textbox, sprite)
        logger.debug(f"Spawned {sprite.name} at {sprite.pos}")
        return sprite

    def cleanup(self):
        """Stop the music when scene is done."""
        # pygame.mixer.music.stop()
        pygame.time.set_timer(ADDENEMY, 0)
        pygame.mouse.set_visible(True)
        return super().cleanup()

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYDOWN:
            if (
                event.key == pygame.K_ESCAPE
                and self.current_time - self.start_time > 1 / 1000
            ):
                self.next_scene = "PAUSE"
                self.done = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_k:
                self.player.kill()
            elif event.key == pygame.K_r:
                self.respawn()
            elif event.key == pygame.K_p:
                self.possess()
        elif event.type == ADDENEMY:
            if len(self.enemies) < self.max_enemies:
                self.spawn_random_enemy()

    def handle_controls(self):
        if not self.player:
            return

        controls = self.controls
        pressed_keys = pygame.key.get_pressed()
        pressed_btns = pygame.mouse.get_pressed(num_buttons=5)

        if (
            controls.pressed_sprint_hold(pressed_keys, pressed_btns)
            and getattr(self.player, "stamina", 0) > 0
        ):
            self.player.is_crouching = 0
            self.player.is_sprinting = 1
            self.player.stamina = max(
                0,
                self.player.stamina - config.DEFAULT_SPRINT_STAMINA_DRAIN,
            )
        elif controls.pressed_crouch_hold(pressed_keys, pressed_btns):
            self.player.is_crouching = 1
            self.player.is_sprinting = 0
        else:
            self.player.is_crouching = 0
            self.player.is_sprinting = 0

        self.player.update_speed()

        _x = 0
        _y = 0

        if controls.pressed_up(pressed_keys, pressed_btns):
            # self.player.direction = self.player.Direction.NORTH
            _y -= self.player.speed
        if controls.pressed_down(pressed_keys, pressed_btns):
            # self.player.direction = self.player.Direction.SOUTH
            _y += self.player.speed
        if controls.pressed_left(pressed_keys, pressed_btns):
            # self.player.direction = self.player.Direction.WEST
            _x -= self.player.speed
        if controls.pressed_right(pressed_keys, pressed_btns):
            # self.player.direction = self.player.Direction.EAST
            _x += self.player.speed

        if pressed_keys[K_PAGEDOWN]:
            self.cam.zoom_out()
        elif pressed_keys[K_PAGEUP]:
            self.cam.zoom_in()

        self.zoom = self.cam.zoom_level
        start_vector = pygame.Vector2(self.player.pos) + self.cam
        end_vector = self.cursor.pos
        dx = end_vector[0] - start_vector[0]
        dy = end_vector[1] - start_vector[1]
        angle = math.degrees(math.atan2(-dy, dx)) % 360

        if start_vector[0] < end_vector[0]:
            self.player.direction = self.player.Direction.EAST
        else:
            self.player.direction = self.player.Direction.WEST

        self.player.is_attacking = False
        if pressed_btns[0]:  # left click
            # cursor_collides = self.cursor.collide(self.enemies)
            # for sprite in cursor_collides:
            #     sprite.blink()
            if (
                not self.player.attack_cooldown_timer
                and getattr(self.player, "mana", config.DEFAULT_PLAYER_MANA) > 0.0
            ):
                self.player.is_attacking = True
                sprite = self.level.spawn_orb("orb", self.player, angle)
                self.player_projectiles.add(sprite)
                self.projectiles.add(sprite)
                self.all_sprites.add(sprite)
                self.all_sprites.move_to_front(sprite)
                self.player.attack_cooldown_timer += getattr(
                    self.player, "attack_cooldown", config.DEFAULT_ATTACK_COOLDOWN
                )
                self.player.mana = max(
                    0,
                    self.player.mana - config.DEFAULT_MANA_DRAIN,
                )
        elif pressed_btns[1]:  # middle mouse button
            pass
        elif pressed_btns[2]:  # right click
            pass
        elif pressed_btns[3]:  # back btn
            pass
        elif pressed_btns[4]:  # next btn
            pass

        if self.player.mana <= 0.0:
            self.player.attack_cooldown_timer = 100
            self.player.force_attack_cooldown_until("mana", "-", "base_mana", "==", 0)

        # if pressed_btns[0]:  # and pygame.MOUSEBUTTONUP in [x.type for x in events]:

        if _x != 0 or _y != 0:
            if self.player.is_idle:
                self.player.counter = 0
                self.player.is_idle = False
            r = self.player.rect.move(_x, _y)

            logger.debug(
                f"Attempting to move {self.player.name} from {self.player.rect.midbottom} to {r.midbottom}"
            )
            _w, _h = self.level.size
            if r[0] > 0 and r[1] > 0 and r[0] + r[2] < _w and r[1] + r[3] < _h:
                self.player.move((r.x, r.y))
                self.player.pos = self.player.rect.center
                logger.info(f"{self.player.name} moved to {self.player.rect.midbottom}")
            else:
                logger.warning(f"{self.player.name} OOB")
        else:
            if not self.player.is_idle:
                self.player.counter = 0
                self.player.is_idle = True

    def check_collisions(self):
        player_enemies = pygame.sprite.spritecollide(
            self.player, self.enemies, dokill=False
        )
        player_enemy_projectile_collisions = pygame.sprite.spritecollide(
            self.player, self.enemy_projectiles, dokill=False
        )

        for enemy in player_enemies:
            self.player.blink()
            self.player.health -= enemy.damage
        for projectile in player_enemy_projectile_collisions:
            self.player.blink()
            self.player.health -= projectile.damage
            projectile.kill()

        for enemy in self.enemies:
            enemy_projectile_collisions = pygame.sprite.spritecollide(
                enemy, self.projectiles, dokill=False
            )
            for projectile in enemy_projectile_collisions:
                enemy.blink()
                enemy.health -= projectile.damage
                projectile.kill()

    def respawn(self):
        for sprite in self.player_sprites:
            sprite.kill()

        self.player = self.level.spawn_player()
        self.player.debug = self.debug

        # height = 10
        # offset = 5
        # offsets = [offset * (i + 1) + height * i for i in range(3)]

        # config = {
        #     "target": self.player,
        #     "width": self.player.rect.width * 2,
        #     "secondary_color": pygame.Color("black"),
        #     "border_color": pygame.Color("white"),
        #     "border_width": 2,
        # }

        # health_config = {
        #     "offset": offsets[0],
        #     "primary_color": config.HEALTH_RED,
        #     "current_attribute": "health",
        #     "max_attribute": "base_health",
        # }
        # health_config.update(config)
        # mana_config = {
        #     "offset": offsets[1],
        #     "primary_color": config.MANA_BLUE,
        #     "current_attribute": "mana",
        #     "max_attribute": "base_mana",
        # }
        # mana_config.update(config)
        # stamina_config = {
        #     "offset": offsets[2],
        #     "primary_color": config.STAMINA_GREEN,
        #     "current_attribute": "stamina",
        #     "max_attribute": "base_stamina",
        # }
        # stamina_config.update(config)
        # health_bar = TargetedStatusBar(font_file=self.font_file, **health_config)
        # mana_bar = TargetedStatusBar(font_file=self.font_file, **mana_config)
        # stamina_bar = TargetedStatusBar(font_file=self.font_file, **stamina_config)

        debug_textbox = TargetedTextBox(
            target=self.player,
            angle=-90,
            font_file=self.font,
            text={"func": self.player.diagnostics_pretty, "args": [self.cam]},
            max_width=self.player.rect.width * 2,
        )

        self.player.debug_textbox = debug_textbox
        # self.player.status_bars = [health_bar, mana_bar, stamina_bar]

        # self.status_bars.add(health_bar, mana_bar, stamina_bar)
        self.texts.add(debug_textbox)
        self.player_sprites.add(
            self.player, debug_textbox  # , health_bar, mana_bar, stamina_bar
        )

        try:
            self.all_sprites.add(self.player_sprites)
        except Exception as ex:
            logger.warning(
                f"Couldn't add {self.player_sprites} to all_sprites: {str(ex)}"
            )

        try:
            self.all_sprites.set_target(self.player)
        except Exception as ex:
            logger.warning(f"Couldn't set {self.player} as camera target: {str(ex)}")

    def possess(self):
        try:
            self.real_player = self.player.copy()
            self.player = random.choice([x for x in self.enemies])
            self.all_sprites.target = self.player
        except IndexError:
            logger.warning("No more sprites to possess")

    def update(self, surface, current_time, dt):
        super().update(surface, current_time)
        self.handle_controls()

        fake_surface = surface.copy()
        self.check_collisions()
        # self.cursor.update()
        # self.cursor.text.update()
        self.ui_sprites.update(surface)

        self.all_sprites.update(fake_surface)
        fake_surface.fill(pygame.Color("black"))
        self.all_sprites.draw(fake_surface)

        # fake_surface.blit(self.cursor.image, self.cursor.rect)
        # fake_surface.blit(self.cursor.text.image, self.cursor.text.rect)
        for sprite in self.ui_sprites:
            fake_surface.blit(sprite.image, sprite.rect)
        self.draw_mp_line(fake_surface)

        surface.blit(fake_surface, (0, 0))

    def pause(self):
        pass

    def save(self):
        pass

    def load(self):
        pass

    def quick_save(self):
        pass

    def quick_load(self):
        pass

    def draw_mp_line(self, surface):
        pygame.draw.line(
            surface,
            config.HEALTH_RED,
            pygame.Vector2(self.player.pos) + self.cam,
            self.cursor.pos,
        )