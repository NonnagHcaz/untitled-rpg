import math
import random
import pygame as pg
from game.components.sprites.entities.enemies.enemy import Enemy
from game.components.sprites.entities.entity import Entity
from game.components.sprites.entities.player.player import Player
from game.components.sprites.sprite import MovableSprite, Sprite, MergedSprite
from game.components.sprites.weapons.weapon import Arrow, Projectile
from . import prepare


class Level(object):
    def __init__(self, width, height, display_width, display_height, cache):
        self.cache = cache

        self.width = width
        self.height = height

        self.display_width = display_width
        self.display_height = display_height

    @property
    def size(self):
        return (self.width, self.height)

    def spawn_random_enemy(self, pos=(None, None)):
        dual_anim = [
            "tiny_zombie",
            "goblin",
            "imp",
            "skelet",
            "masked_orc",
            "orc_warrior",
            "orc_shaman",
            "wogol",
            "chort",
            "angel",
            "pumpkin_dude",
            "doc",
        ]
        idle_only = [
            "muddy",
            "swampy",
            "zombie",
            "ice_zombie",
            "necromancer",
            "slug",
            "tiny_slug",
        ]
        bosses = ["big_zombie", "ogre", "big_demon"]

        if random.random() < 0.05:
            choices = bosses
        else:
            choices = dual_anim

        return self.spawn_sprite(random.choice(choices), pos, is_enemy=True)

    def spawn_projectile(self, name, cam_pos, mouse_pos, image=None):
        if image is None:
            image = self.cache["name"]
        dx = mouse_pos[0] - cam_pos[0]
        dy = mouse_pos[1] - cam_pos[1]
        m = dy / dx
        angle = math.degrees(math.atan2(dy, dx))
        x = cam_pos[0] + 10
        y = m * x + 10
        sprite = Projectile(name=name, image=image, angle=angle)
        sprite.spawn(pos=(x, y))
        # sprite.spawn(x=self.width//2, y=self.height//2)
        return sprite

    def spawn_orb(self, cam_pos, mouse_pos, color=None, radius=8, border_width=0):
        name = "weapon_orb"
        image = pg.Surface((16, 16), pg.SRCALPHA)
        if color is None:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            color = (r, g, b)
        pg.draw.circle(
            surface=image,
            color=color,
            center=mouse_pos,
            radius=radius,
            width=border_width,
        )

        return self.spawn_projectile(name, cam_pos, mouse_pos, image)

    def spawn_arrow(self, cam_pos, mouse_pos):
        name = "weapon_arrow"
        image = self.cache[name]

        # sprite.spawn(x=self.width//2, y=self.height//2)
        return self.spawn_projectile(name, cam_pos, mouse_pos, image)

    def spawn_player(self):
        return self.spawn_male_wizzard(is_player=True)

    def spawn_sprite(
        self, name="knight_m", pos=(None, None), is_player=False, is_enemy=False
    ):
        idle_frames = [self.cache[f"{name}_idle_anim_f{x}"] for x in range(0, 4)]
        walk_frames = [self.cache[f"{name}_run_anim_f{x}"] for x in range(0, 4)]

        config = {
            "name": name,
            "image": idle_frames[0],
            "idle_frames": idle_frames,
            "walk_frames": walk_frames,
        }
        if is_player:
            sprite = Player(**config)
        elif is_enemy:
            sprite = Enemy(**config)
        else:
            sprite = Entity(**config)
        x, y = pos
        if x is None:
            x = self.width // 2
        elif x < 0:
            x = 0
        elif x > self.width - sprite.rect.width:
            x = self.width - sprite.rect.width

        if y is None:
            y = self.height // 2
        elif y < 0:
            y = 0
        elif y > self.height - sprite.rect.height:
            y = self.height - sprite.rect.height

        sprite.spawn(pos=(x, y))
        return sprite

    def spawn_male_knight(self, pos=(None, None), is_player=False):
        name = "knight_m"
        return self.spawn_sprite(name, pos, is_player)

    def spawn_female_knight(self, pos=(None, None), is_player=False):
        name = "knight_f"
        return self.spawn_sprite(name, pos, is_player)

    def spawn_male_wizzard(self, pos=(None, None), is_player=False):
        name = "wizzard_m"
        return self.spawn_sprite(name, pos, is_player)

    def spawn_female_wizzard(self, pos=(None, None), is_player=False):
        name = "wizzard_f"
        return self.spawn_sprite(name, pos, is_player)

    def spawn_male_elf(self, pos=(None, None), is_player=False):
        name = "elf_m"
        return self.spawn_sprite(name, pos, is_player)

    def spawn_female_elf(self, pos=(None, None), is_player=False):
        name = "elf_f"
        return self.spawn_sprite(name, pos, is_player)

    def spawn_male_lizard(self, pos=(None, None), is_player=False):
        name = "lizard_m"
        return self.spawn_sprite(name, pos, is_player)

    def spawn_female_lizard(self, pos=(None, None), is_player=False):
        name = "lizard_f"
        return self.spawn_sprite(name, pos, is_player)

    def spawn_male_dwarf(self, pos=(None, None), is_player=False):
        name = "dwarf_m"
        return self.spawn_sprite(name, pos, is_player)

    def spawn_female_dwarf(self, pos=(None, None), is_player=False):
        name = "dwarf_f"
        return self.spawn_sprite(name, pos, is_player)

    def build_floor(self):
        tiles = []

        floor_frames = [self.cache[f"floor_{x}"] for x in range(1, 9)]
        _t0 = floor_frames[0].get_rect()
        _tw, _th = _t0.width, _t0.height
        _y = _th * 2
        _x = _tw * 2
        for y in range(_y, self.height - _y, _th):
            for x in range(_x, self.width - _x, _tw):
                name = "floor_1"  # [random.randint(0, len(tiles) - 1)]
                image = floor_frames[0]
                sprite = Sprite(name=name, image=image)
                sprite.spawn(pos=(x, y))
                tiles.append(sprite)

        for x in range(0, self.width, _tw):
            y = self.height - _th * 1.5
            name = "edge_down"
            image = self.cache[name]
            sprite = Sprite(name=name, image=image)
            sprite.spawn(pos=(x, y))
            tiles.append(sprite)

        floor = MergedSprite(
            name="floor", image=MergedSprite.merge(tiles), sprites=tiles
        )

        return floor

    def build_walls(self):
        tiles = []
        _wh = 2
        _we = True
        _gw, _gh = self.width, self.height
        _gw50, _gh50 = _gw // 2, _gh // 2

        _t0 = self.cache["wall_edge_top_left"].get_rect()
        _tw, _th = _t0.width, _t0.height
        _bx, _by = _gw // _tw, _gh // _th

        padding = (0, 0, 0, 0)
        border = (1, 1, 1, 1)
        border_width = (2, 2, 2, 2)

        for y in range(0, _gh, _th):
            for x in range(0, _gw, _tw):
                if x == 0 and y < _gh - (_th * 2):
                    name = "wall_edge_left"
                elif x == _gw - (_tw * 1) and y < _gh - (_th * 2):
                    name = "wall_edge_right"
                elif x == _tw and y < _gh - (_th * 2) and y > _th:
                    name = "wall_right"
                elif x == _gw - _tw * 2 and y < _gh - (_th * 2) and y > _th:
                    name = "wall_left"
                elif (
                    (x > 0 and x < _gw50 - (_tw * 1))
                    or (x > _gw50 + (_tw * 0) and x <= _gw - (_tw * 2))
                ) and y < _th * 2:
                    name = "wall_mid"
                elif x == _gw50 - _tw and y == 0:
                    name = "doors_leaf_closed"
                elif y == _gh - (_th * 2):
                    name = "edge_down"
                else:
                    name = None
                if name:
                    image = self.cache[name]
                    sprite = Sprite(name=name, image=image)
                    sprite.spawn(pos=(x, y))
                    tiles.append(sprite)

        walls = MergedSprite(
            name="walls", image=MergedSprite.merge(tiles), sprites=tiles
        )

        return walls
