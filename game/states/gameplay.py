import datetime
import math
import random
import pygame as pg
from pygame.locals import (
    KEYDOWN,
    KEYUP,
    K_ESCAPE,
    K_F1,
    K_F9,
    K_r,
    QUIT,
    MOUSEBUTTONUP,
)

from game.components.camera.camera import Camera, CameraAwareLayeredUpdates
from game.components.sprites.cursor.cursor import Cursor
from game.components.sprites.shape.shape import Hitbox
from game.components.sprites.status_bar.status_bar import TargetedStatusBar


import logging
from game.components.sprites.text.text import TargetedText
from game.level import Level

from game.states.state import GameState
from game.utils import MappedImageCache
from game.utils.controls.controls import Controls

logger = logging.getLogger(__name__)

from .. import prepare

# pg.mouse.set_visible(False)


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
        self.zoom = 3

        self.bgm = None
        self.font = prepare.FONTS["Roboto-Regular"]

    def startup(self, current_time, persistent, surface):
        super().startup(current_time, persistent, surface)
        # pg.mixer.music.load(self.bgm)
        # pg.mixer.music.play(-1)
        self.cam = Camera()

        self.controls = Controls()

        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.hitboxes = pg.sprite.Group()
        self.status_bars = pg.sprite.Group()
        self.texts = pg.sprite.Group()

        level_width = 16 * 1000
        level_height = 9 * 1000
        sheet_name = "0x72_DungeonTilesetII_v1.6"
        sheet = prepare.GFX[sheet_name]
        mapping = "assets/graphics/tile_list.txt"
        cache = MappedImageCache(sheet=sheet, mapping=mapping)
        self.cursor = Cursor(
            name="cursor", image=prepare.GFX["crosshair_1"], cam=self.cam
        )

        self.cursor.text = TargetedText(
            target=self.cursor,
            text=self.cursor.diagnostics_pretty,
            max_width=self.cursor.rect.width * 2,
        )

        self.level = Level(
            width=level_width,
            height=level_height,
            display_width=self.screen.get_rect().width,
            display_height=self.screen.get_rect().height,
            cache=cache,
        )

        self.floor = self.level.build_floor()
        self.walls = self.level.build_walls()

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
                primary_color=pg.Color("red"),
                secondary_color=pg.Color("black"),
                border_color=pg.Color("white"),
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
                primary_color=pg.Color("green"),
                secondary_color=pg.Color("black"),
                border_color=pg.Color("white"),
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
                primary_color=pg.Color("blue"),
                secondary_color=pg.Color("black"),
                border_color=pg.Color("white"),
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

        self.mp_line = pg.sprite.Sprite()

        for _ in range(10):
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
                    primary_color=pg.Color("red"),
                    border_color=pg.Color("white"),
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
            world_size=pg.Rect(0, 0, level_width, level_height),
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
        # pg.mixer.music.stop()
        return super().cleanup()

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True

    def handle_controls(self):
        if not self.player:
            return
        controls = self.controls
        pressed_keys = self.pressed_keys
        pressed_btns = self.pressed_btns

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

        # if pressed_btns[0]:  # and pg.MOUSEBUTTONUP in [x.type for x in events]:

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
        player_enemies = pg.sprite.spritecollide(
            self.player, self.enemies, dokill=False
        )
        player_projectiles = pg.sprite.spritecollide(
            self.player, self.projectiles, dokill=False
        )

        for enemy in player_enemies:
            self.player.blink()
            self.player.health -= enemy.damage
        for projectile in player_projectiles:
            self.player.blink()
            self.player.health -= projectile.damage

        for enemy in self.enemies:
            enemy_projectiles = pg.sprite.spritecollide(
                enemy, self.projectiles, dokill=False
            )
            for projectile in enemy_projectiles:
                enemy.blink()
                enemy.health -= projectile.damage

    def respawn(self):
        print("respawn")
        self.all_sprites.target = random.choice([x for x in self.enemies])

    def update(self, surface, current_time, time_delta):
        super().update(surface, current_time)

        for event in self.events:
            if event.type == QUIT:
                self.quit = True

        self.handle_controls()
        self.check_collisions()
        self.cursor.update()
        self.cursor.text.update()
        self.all_sprites.update(surface)
        surface.fill(pg.Color("black"))
        self.all_sprites.draw(surface)

        surface.blit(self.cursor.image, self.cursor.rect)
        surface.blit(self.cursor.text.image, self.cursor.text.rect)
        self.draw_mp_line(surface)

        # surface.blit(self.player.image, self.player.rect)

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
        pg.draw.line(
            surface,
            pg.Color("red"),
            pg.Vector2(self.player.pos) + self.cam,
            self.cursor.pos,
        )
