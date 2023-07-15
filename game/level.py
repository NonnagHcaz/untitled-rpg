import math
import os
import random
import pygame
from game import config
from game.components.sprites.entities.enemies.enemy import Enemy
from game.components.sprites.entities.entity import Entity
from game.components.sprites.entities.player.player import Player
from game.components.sprites.sprite import MovableSprite, Sprite, MergedSprite
from game.components.sprites.weapons.weapon import Arrow, Projectile


class AutoTileset(object):
    def __init__(self, image, tile_width, tile_height=None) -> None:
        self.image = image
        self.rect = self.image.get_rect()
        self.tiles = self._split(tile_width, tile_height)

    def _split(self, tile_width=None, tile_height=None, tile_size=None):
        if tile_size and len(tile_size) == 2:
            tile_width, tile_height = tile_size

        self.tile_width = tile_width
        self.tile_height = tile_height or tile_width
        image_width, image_height = self.rect.size

        rows = image_height // tile_height
        cols = image_width // tile_width

        tiles = []
        for col in range(cols):
            for row in range(rows):
                sprite = None

        return tiles

    def neighbors(self, tile):
        return None


class Tile(Sprite):
    def __init__(self, name=None, image=None, debug=False):
        super().__init__(name, image, debug)

    def autotile(surface, tile_index, bitmask_value, tile_size):
        tile_sheet_width = 256
        tile_sheet_height = 192
        tile_per_row = tile_sheet_width // tile_size[0]
        row = tile_index // tile_per_row
        col = tile_index % tile_per_row

        x = col * tile_size[0]
        y = row * tile_size[1]

        source_rect = pygame.Rect(x, y, tile_size[0], tile_size[1])
        dest_rect = pygame.Rect(0, 0, tile_size[0], tile_size[1])

        surface.blit(surface, dest_rect, source_rect)


class BitMask(object):
    def __init__(self) -> None:
        self.mask = []


class Room(object):
    pass


class SpawnRoom(Room):
    def __init__(self) -> None:
        super().__init__()


class SmallRoom(Room):
    def __init__(self) -> None:
        super().__init__()


class LargeRoom(Room):
    def __init__(self) -> None:
        super().__init__()


class XLargeRoom(Room):
    def __init__(self) -> None:
        super().__init__()


class Level(object):
    def __init__(self, width, height, display_width, display_height, cache):
        self.cache = cache

        self.width = width
        self.height = height

        self.display_width = display_width
        self.display_height = display_height
        self.spritesheets = {
            "0x72d2": os.path.join(config.GFX_DIR, "0x72_DungeonTilesetII_v1.6.png"),
            "0x72ex": os.path.join(config.GFX_DIR, "dungeontileset-extended.png"),
        }

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

    def spawn_projectile(self, name, origin, angle, image=None):
        if image is None:
            image = self.cache[(self.spritesheets["0x72d2"], name)]
        x, y = origin.rect.center
        sprite = Projectile(
            name=name, image=image, angle=angle, walk_speed=10, damage=10
        )
        sprite.spawn(pos=(x, y))
        # sprite.spawn(x=self.width//2, y=self.height//2)
        return sprite

    def spawn_orb(
        self,
        name,
        origin,
        angle,
        color=None,
        radius=4,
        border_color=pygame.Color("black"),
        border_width=1,
    ):
        name = "weapon_orb"
        image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        # image.fill()
        if not color:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            color = (r, g, b)
        if not border_color:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            border_color = (r, g, b)
        if border_width:
            pygame.draw.circle(
                surface=image,
                color=border_color,
                center=(radius, radius),
                radius=radius,
                width=border_width,
            )
        pygame.draw.circle(
            surface=image, color=color, center=(radius, radius), radius=radius
        )

        return self.spawn_projectile(name, origin, angle, image)

    def spawn_arrow(self, origin, angle):
        name = "weapon_arrow"
        image = self.cache[(self.spritesheets["0x72d2"], name)]

        # sprite.spawn(x=self.width//2, y=self.height//2)
        return self.spawn_projectile(name, origin, angle, image)

    def spawn_player(self):
        return self.spawn_male_wizzard(is_player=True)

    def spawn_sprite(
        self, name="knight_m", pos=(None, None), is_player=False, is_enemy=False
    ):
        idle_frames = [
            self.cache[(self.spritesheets["0x72d2"], f"{name}_idle_anim_f{x}")]
            for x in range(0, 4)
        ]
        walk_frames = [
            self.cache[(self.spritesheets["0x72d2"], f"{name}_run_anim_f{x}")]
            for x in range(0, 4)
        ]

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

    def build_spawn_room(self, width=0, radius=0):
        pass

    def build_multilevel_room(self, width=0, radius=0):
        pass

    def build_room(self, width, height, border_radius=0, imperfect=True, **config):
        pass

    def build_test_floor(self):
        tiles = []

        floor_frames = [
            self.cache[(self.spritesheets["0x72d2"], f"floor_{x}")] for x in range(1, 9)
        ]
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
            image = self.cache[(self.spritesheets["0x72d2"], name)]
            sprite = Sprite(name=name, image=image)
            sprite.spawn(pos=(x, y))
            tiles.append(sprite)

        floor = MergedSprite(
            name="floor", image=MergedSprite.merge(tiles), sprites=tiles
        )

        return floor

    def build_test_walls(self):
        tiles = []
        _wh = 2
        _we = True
        _gw, _gh = self.width, self.height
        _gw50, _gh50 = _gw // 2, _gh // 2

        _t0 = self.cache[(self.spritesheets["0x72d2"], "wall_edge_top_left")].get_rect()
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
                    image = self.cache[(self.spritesheets["0x72d2"], name)]
                    sprite = Sprite(name=name, image=image)
                    sprite.spawn(pos=(x, y))
                    tiles.append(sprite)

        walls = MergedSprite(
            name="walls", image=MergedSprite.merge(tiles), sprites=tiles
        )

        return walls


class Dungeon(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Desert(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DesertDungeon(Desert, Dungeon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Jungle(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class JungleDungeon(Jungle, Dungeon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Tundra(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TundraDungeon(Tundra, Dungeon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Graveyard(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Forest(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Cave(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Beach(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Mountain(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Tundra(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
