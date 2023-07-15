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
from game.components.sprites.text.text import TargetedText
from game.level import Dungeon

from game.states.state import GameState
from game.utils.asset_cache import _fn
from game.utils.controls import Controls

logger = logging.getLogger(__name__)

from .. import config

# pygame.mouse.set_visible(False)


class Gameplay(GameState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def startup(self, current_time, persistent, surface):
        super().startup(current_time, persistent, surface)
        # pygame.mixer.music.load(self.bgm)
        # pygame.mixer.music.play(-1)
        self.cam = Camera()

        self.bgm = None
        self.font = None

        self.controls = Controls()

        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.hitboxes = pygame.sprite.Group()
        self.status_bars = pygame.sprite.Group()
        self.texts = pygame.sprite.Group()

        level_width = 16 * 250
        level_height = 9 * 250

        self.cursor = Cursor(
            name="cursor",
            image=self.asset_cache[
                _fn(os.path.join(config.GFX_DIR, "crosshair_1.png"))
            ],
            cam=self.cam,
        )

        self.cursor.text = TargetedText(
            target=self.cursor,
            text=self.cursor.diagnostics_pretty,
            max_width=self.cursor.rect.width * 2,
        )

        self.level = Dungeon(
            width=level_width,
            height=level_height,
            display_width=self.screen.get_rect().width,
            display_height=self.screen.get_rect().height,
            cache=self.asset_cache,
        )

        self.floor = self.level.build_test_floor()
        self.walls = self.level.build_test_walls()

        self.player = self.level.spawn_player()
        self.player.debug = self.debug
        # self.hitboxes.add(Hitbox(target=self.player))

        i = 0
        height = 10
        offset = 5
        offsets = [offset * (i + 1) + height * i for i in range(3)]

        self.status_bars.add(
            TargetedStatusBar(
                target=self.player,
                offset=offsets[0],
                width=self.player.rect.width * 2,
                primary_color=pygame.Color("red"),
                secondary_color=pygame.Color("black"),
                border_color=pygame.Color("white"),
                border_width=2,
                current_attribute="health",
                max_attribute="base_health",
            )
        )
        i += 1
        self.status_bars.add(
            TargetedStatusBar(
                target=self.player,
                offset=offsets[1],
                width=self.player.rect.width * 2,
                primary_color=pygame.Color("green"),
                secondary_color=pygame.Color("black"),
                border_color=pygame.Color("white"),
                border_width=2,
                current_attribute="stamina",
                max_attribute="base_stamina",
            )
        )
        self.status_bars.add(
            TargetedStatusBar(
                target=self.player,
                offset=offsets[2],
                width=self.player.rect.width * 2,
                primary_color=pygame.Color("blue"),
                secondary_color=pygame.Color("black"),
                border_color=pygame.Color("white"),
                border_width=2,
                current_attribute="mana",
                max_attribute="base_mana",
            )
        )
        self.texts.add(
            TargetedText(
                target=self.player,
                angle=-90,
                font_file=self.font,
                text=self.player.diagnostics_pretty,
                max_width=self.player.rect.width * 2,
            )
        )

        self.mp_line = pygame.sprite.Sprite()

        for _ in range(self.level.width // 100):
            x = random.randint(int(self.level.width * 0.1), int(self.level.width * 0.9))
            y = random.randint(
                int(self.level.height * 0.1), int(self.level.height * 0.9)
            )
            sprite = self.level.spawn_random_enemy(pos=(x, y))
            sprite.debug = self.debug
            self.enemies.add(sprite)
            # self.hitboxes.add(Hitbox(target=sprite))
            self.status_bars.add(
                TargetedStatusBar(
                    target=sprite,
                    offset=5,
                    width=sprite.rect.width * 2,
                    primary_color=pygame.Color("red"),
                    border_color=pygame.Color("white"),
                    border_width=2,
                    current_attribute="health",
                    max_attribute="base_health",
                )
            )
            self.texts.add(
                TargetedText(
                    target=sprite,
                    angle=-90,
                    font_file=self.font,
                    text=sprite.diagnostics_pretty,
                    max_width=sprite.rect.width * 2,
                )
            )

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
        # self.all_sprites.add(self.cursor)
        for sprite in [self.player]:
            self.all_sprites.move_to_front(sprite)

    def cleanup(self):
        """Stop the music when scene is done."""
        # pygame.mixer.music.stop()
        return super().cleanup()

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.next_state = "PAUSE"
                self.done = True

    def handle_controls(self):
        if not self.player:
            return

        controls = self.controls
        pressed_keys = pygame.key.get_pressed()
        pressed_btns = pygame.mouse.get_pressed(num_buttons=5)

        if pressed_keys[pygame.K_ESCAPE]:
            self.next_state = "PAUSE"
            self.game.flip_state()

        if pressed_keys[pygame.K_k]:
            self.player.kill()

        if pressed_keys[pygame.K_r]:
            self.possess()

        if controls.pressed_sprint_hold(pressed_keys, pressed_btns):
            self.player.is_crouching = 0
            self.player.is_sprinting = 1
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

        if self.player.x + self.cam.x < self.cursor.x:
            self.player.direction = self.player.Direction.EAST
        else:
            self.player.direction = self.player.Direction.WEST

        if pressed_btns[0]:
            cursor_collides = self.cursor.collide(self.enemies)
            for sprite in cursor_collides:
                sprite.blink()
            else:
                if len(self.projectiles) < 20:
                    sprite = self.level.spawn_orb(self.player.pos, self.cursor.pos)
                    self.projectiles.add(sprite)
                    self.all_sprites.add(sprite)
                    self.all_sprites.move_to_front(sprite)

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
        player_projectiles = pygame.sprite.spritecollide(
            self.player, self.projectiles, dokill=False
        )

        for enemy in player_enemies:
            self.player.blink()
            self.player.health -= enemy.damage
        for projectile in player_projectiles:
            self.player.blink()
            self.player.health -= projectile.damage

        for enemy in self.enemies:
            enemy_projectiles = pygame.sprite.spritecollide(
                enemy, self.projectiles, dokill=False
            )
            for projectile in enemy_projectiles:
                enemy.blink()
                enemy.health -= projectile.damage

    def possess(self):
        print("respawn")
        try:
            self.all_sprites.target = random.choice([x for x in self.enemies])
            self.real_player = self.player
            self.player = self.all_sprites.target
        except IndexError:
            pass

    def update(self, surface, current_time, dt):
        super().update(surface, current_time)
        self.handle_controls()

        fake_surface = surface.copy()
        self.check_collisions()
        self.cursor.update()
        self.cursor.text.update()

        self.all_sprites.update(fake_surface)
        fake_surface.fill(pygame.Color("black"))
        self.all_sprites.draw(fake_surface)

        fake_surface.blit(self.cursor.image, self.cursor.rect)
        fake_surface.blit(self.cursor.text.image, self.cursor.text.rect)
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
            pygame.Color("red"),
            pygame.Vector2(self.player.pos) + self.cam,
            self.cursor.pos,
        )
