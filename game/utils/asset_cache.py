from pprint import pprint
import pygame
import os
import glob
import logging
import re

from game import config, utils

logger = logging.getLogger(__name__)


class Mapper(object):
    def __init__(self):
        self.map = {}

    @property
    def valid_fmts(self):
        return ["0x72"]

    def load(self, filepath, sheet=None, fmt="0x72", overwrite=False):
        if not os.path.exists(filepath):
            return None

        _loads = []
        if fmt is None:
            fmt = "0x72"  # TODO: Sample x lines and determine fmt
        if fmt not in self.valid_fmts:
            logger.error(f"bad fmt: {fmt}")
            return None

        if fmt == "0x72":
            tiles = self.parse_0x72_mapping(filepath)
            for name, rect in tiles.items():
                data = {
                    "sheet": sheet,
                    "name": name,
                    "mapper": filepath,
                    "fmt": fmt,
                    "rect": rect,
                    "type": "tileset",
                }
                _loads.append(data)
                if sheet:
                    key = (sheet, name)
                else:
                    key = (filepath, name)
                if key not in self.map or overwrite:
                    self.map[key] = data
            return _loads
        else:
            return None

    def parse_0x72_mapping(self, map_file, header=False, delimiter=" "):
        return parse_0x72_mapping(map_file, header, delimiter)

    def __getitem__(self, key):
        try:
            return self.map[key]
        except KeyError:
            return None


class AssetCache(object):
    def __init__(self):
        self.cache = {}
        self.map = Mapper()

    def _derive_type(self, filepath):
        ext = os.path.splitext(filepath)[-1].lower()
        if ext in (".png", ".jpg", ".bmp"):
            return "image"
        elif ext in (".ttf"):
            return "font"
        elif ext in (".wav", ".mp3", ".ogg", ".mdi"):
            return "sound"
        elif ext in (".txt", ".json"):
            return "txt"
        return None

    def load_any(
        self,
        file_or_dir,
        colorkey=(255, 0, 255),
        image_accept=(".png", ".jpg", ".bmp"),
        mapping_accept=(".txt", ".json"),
        scale_factor=1.0,
        flip_x=False,
        flip_y=False,
        overwrite=False,
        overrides={},
    ):
        if isinstance(file_or_dir, "str"):
            if os.path.isdir(file_or_dir):
                filepaths = utils.get_filepaths(file_or_dir, ".*")
            else:
                filepaths = [file_or_dir]
        else:
            return None

        assets = {x: [] for x in ["image", "sound", "font", "txt", None]}

        for filepath in filepaths:
            _type = self._derive_type(filepath)
            assets[_type].append(filepath)

    def load_images(
        self,
        directory,
        colorkey=(255, 0, 255),
        image_accept=(".png", ".jpg", ".bmp"),
        mapping_accept=(".txt", ".json"),
        scale_factor=1.0,
        flip_x=False,
        flip_y=False,
        overwrite=False,
        overrides={},
    ):
        """Load all graphics with extensions in the accept argument.  If alpha
        transparency is found in the image the image will be converted using
        convert_alpha().  If no alpha transparency is detected image will be
        converted using convert() and colorkey will be set to colorkey."""

        sheets = utils.get_filepaths(directory, *image_accept)
        mappings = utils.get_filepaths(directory, *mapping_accept)
        mapping_dict = {os.path.splitext(os.path.split(x)[1])[0]: x for x in mappings}

        images = []

        for sheet in sheets:
            name = os.path.splitext(os.path.split(sheet)[1])[0]
            mapping = mapping_dict.get(name)

            images.append(
                self.load_image(
                    sheet,
                    mapping,
                    colorkey,
                    image_accept,
                    mapping_accept,
                    scale_factor,
                    flip_x,
                    flip_y,
                    overwrite,
                    overrides,
                )
            )

        return images

    def load_image(
        self,
        sheet,
        mapping=None,
        colorkey=(255, 0, 255),
        image_accept=(".png", ".jpg", ".bmp"),
        mapping_accept=(".txt", ".json"),
        scale_factor=1.0,
        flip_x=False,
        flip_y=False,
        overwrite=False,
        overrides={},
    ):
        if isinstance(sheet, str) and os.path.isdir(sheet):
            return self.load_images(
                sheet,
                mapping,
                colorkey,
                image_accept,
                mapping_accept,
                scale_factor,
                flip_x,
                flip_y,
                overwrite,
                overrides,
            )

        name = _fn(sheet)
        overrides = overrides.copy().get(name, {})
        scale_factor = overrides.get("scale_factor", scale_factor)
        colorkey = overrides.get("colorkey", colorkey)
        image_accept = overrides.get("image_accept", image_accept)
        mapping_accept = overrides.get("mapping_accept", mapping_accept)
        overwrite = overrides.get("overwrite", overwrite)
        mapping = overrides.get("mapping", mapping)
        flip_x = overrides.get("flip_x", flip_x)
        flip_y = overrides.get("flip_y", flip_y)

        sheet_ext = os.path.splitext(os.path.split(sheet)[1])[1].lower()
        if isinstance(mapping, str):
            mapping_ext = os.path.splitext(os.path.split(mapping)[1])[1].lower()
        else:
            mapping_ext = ".txt"

        if sheet_ext not in [str(x).lower() for x in image_accept] or (
            mapping and mapping_ext not in [str(x).lower() for x in mapping_accept]
        ):
            logger.error(f"{sheet}, {mapping}")
            return None

        if mapping:
            self.map.load(filepath=mapping, sheet=sheet, overwrite=False)

        image = pygame.image.load(sheet)
        if image.get_alpha():
            image = image.convert_alpha()
        else:
            image = image.convert()
            image.set_colorkey(colorkey)

        if flip_x or flip_y:
            image = pygame.transform.flip(image, flip_x=flip_x, flip_y=flip_y)

        if scale_factor:
            image = pygame.transform.smoothscale_by(image, scale_factor)

        _name = ("image", name[0], name[1], scale_factor, flip_x, flip_y)
        if _name not in self.cache or overwrite:
            self.cache[_name] = image

        return image

    def load_sfxs(
        self,
        directory,
        accept=(".wav", ".mp3", ".ogg", ".mdi"),
        overwrite=False,
        overrides={},
    ):
        filepaths = utils.get_filepaths(directory, *accept)

        sfxs = []

        for filepath in filepaths:
            name = os.path.splitext(os.path.split(filepath)[1])[0]

            sfxs.append(
                self.load_sfx(
                    directory,
                    accept,
                    overwrite,
                    overrides,
                )
            )

        return sfxs

    def load_sfx(
        self,
        filepath,
        accept=(".wav", ".mp3", ".ogg", ".mdi"),
        overwrite=False,
        overrides={},
    ):
        ext = os.path.splitext(filepath)[-1]
        if ext.lower() not in accept:
            return None

        sfx = pygame.mixer.Sound(filepath)
        _name = _fn(filepath)
        _name = ("sound", _name[0], _name[1])
        if _name not in self.cache or overwrite:
            self.cache[_name] = sfx

        return sfx

    def load_sounds(
        self,
        directory,
        accept=(".wav", ".mp3", ".ogg", ".mdi"),
    ):
        filepaths = utils.get_filepaths(directory, *accept)

        sounds = []

        for filepath in filepaths:
            sounds.append(self.load_sound(filepath, accept))

        return sounds

    def load_sound(
        self,
        filepath,
        accept=(".wav", ".mp3", ".ogg", ".mdi"),
    ):
        ext = os.path.splitext(filepath)[-1]
        if ext.lower() not in accept:
            return None
        return filepath

    def load_fonts(
        self, directory, accept=(".ttf"), font_size=24, overwrite=False, overrides={}
    ):
        filepaths = utils.get_filepaths(directory, *accept)
        fonts = []
        for filepath in filepaths:
            fonts.append(
                self.load_font(filepath, accept, font_size, overwrite, overrides)
            )
        return fonts

    def load_font(
        self, filepath, accept=(".ttf"), font_size=24, overwrite=False, overrides={}
    ):
        ext = os.path.splitext(filepath)[-1]
        if ext.lower() not in accept:
            return None

        font = pygame.font.Font(filepath, font_size)
        _name = _fn(filepath)
        _name = ("font", _name[0], _name[1], font_size)
        if _name not in self.cache or overwrite:
            self.cache[_name] = font

        return font

    def validate_asset_type(self, test_type):
        kind = test_type.lower()
        if kind in ["image", "img", "sheet", "spritesheet", "sprite"]:
            return "image"
        elif kind in ["font"]:
            return "font"
        elif kind in ["sfx"]:
            return "sfx"
        elif kind in ["music", "bgm"]:
            return "music"
        elif kind in ["text", "txt", "mapping"]:
            return "txt"
        return None

    def __getitem__(self, key):
        if isinstance(key, str):
            key = (str(self._derive_type(key)).lower(), key)
        elif isinstance(key, tuple):
            key_type = self.validate_asset_type(key[0])
            if not key_type:
                key = (str(self._derive_type(key[0])).lower(),) + key
        else:
            raise f"{type(key)} not acceptable key type for AssetCache.__getitem__(key)"

        if len(key) < 2:
            raise f"{key} not acceptable key value for AssetCache.__getitem__(key)"

        kind = key[0]

        if len(key) == 2 and isinstance(key[1], tuple):
            key = (kind,) + key[1]

        if len(key) == 2:
            # Assume the filepath to a loose image/frame/fontfile
            this_file, this_name = _fn(key[1])
        else:
            # Assume filepath and name, no modifier
            this_file, this_name = key[1], key[2]

        if kind == "image":
            image_scale_factor = 1.0
            image_flip_x = False
            image_flip_y = False

            if len(key) >= 4:
                image_scale_factor = key[3]

            if len(key) >= 5:
                image_flip_x = key[4]
                image_flip_y = image_flip_x

            if len(key) >= 6:
                image_flip_y = key[5]

            key = (
                kind,
                this_file,
                this_name,
                image_scale_factor,
                image_flip_x,
                image_flip_y,
            )

        elif kind == "font":
            font_size = 24
            if len(key) >= 4:
                try:
                    _k2 = int(key[3])
                except ValueError:
                    font_size = 24
                else:
                    font_size = _k2
            key = (kind, this_file, this_name, font_size)
        try:
            return self.cache[key]
        except KeyError:
            _type = key[0]
            if _type == "image":
                try:
                    self.map[(this_file, this_name)]
                except TypeError:
                    logger.error(f"Missing {key} from Mapper")
                    return None
                except KeyError:
                    logger.error(f"Missing 'sheet' Mapper entry for {key}")
                sheet = self.cache[("image",) + _fn(key[1]) + (1.0, False, False)]

                image = self.strip_name_from_sheet(sheet, (this_file, this_name))
                if image_flip_x or image_flip_y:
                    image = pygame.transform.flip(
                        image, flip_x=image_flip_x, flip_y=image_flip_y
                    )

                if image_scale_factor != 1.0:
                    image = pygame.transform.smoothscale_by(image, image_scale_factor)
                self.cache[key] = image
                return image
            elif _type == "sound":
                sound = self.load_sound(this_file)
                self.cache[key] = sound
                return sound
            elif _type == "sfx":
                sfx = self.load_sfx(this_file)
                self.cache[key] = sfx
                return sfx
            elif _type == "font":
                font = self.load_font(this_file, font_size=font_size)
                self.cache[key] = font
                return font
        return None

    def strip_from_sheet(self, sheet, start, size, columns, rows=1):
        """Strips individual frames from a sprite sheet given a start location,
        sprite size, and number of columns and rows."""
        return strip_from_sheet(sheet, start, size, columns, rows)

    def strip_coords_from_sheet(self, sheet, coords, size):
        """Strip specific coordinates from a sprite sheet."""
        return strip_from_sheet(sheet, coords, size)

    def strip_name_from_sheet(self, sheet, name):
        """Strip specific name from a sprite sheet based on coordinate mapping file."""
        return strip_name_from_sheet(sheet, name, self.map)


def parse_0x72_mapping(map_file, header=False, delimiter=" "):
    tiles = {}
    with open(map_file, "r") as fp:
        lines = fp.readlines()

    for line in lines:
        line_parts = line.strip().split(delimiter)
        if len(line_parts) < 5:
            continue
        _n, _l, _t, _w, _h = line_parts[:5]
        if len(line_parts) == 5:
            tiles[_n] = pygame.Rect((float(_l), float(_t)), (float(_w), float(_h)))
        elif len(line_parts) >= 6:
            _f = int(line_parts[5])
            for x in range(_f):
                tiles[_n + f"_f{x}"] = pygame.Rect(
                    (float(_l) + float(_w) * x, float(_t)), (float(_w), float(_h))
                )
    return tiles


def _strip(sheet, rect):
    _mult = config.TEXTURE_SCALE
    sub_surf = pygame.transform.scale_by(sheet.subsurface(rect), _mult)
    return sub_surf


def strip_from_sheet(sheet, start, size, columns, rows=1):
    """Strips individual frames from a sprite sheet given a start location,
    sprite size, and number of columns and rows."""
    frames = []
    for j in range(rows):
        for i in range(columns):
            location = (start[0] + size[0] * i, start[1] + size[1] * j)
            rect = pygame.Rect(location, size)
            frames.append(_strip(sheet, rect))
    return frames


def strip_coords_from_sheet(sheet, coords, size):
    """Strip specific coordinates from a sprite sheet."""
    frames = []
    for coord in coords:
        location = (coord[0] * size[0], coord[1] * size[1])
        rect = pygame.Rect(location, size)
        frames.append(_strip(sheet, rect))
    return frames


def strip_name_from_sheet(sheet, key, mapper):
    rect = mapper[key]["rect"]
    return _strip(sheet, rect)


def get_cell_coordinates(rect, point, size):
    """Find the cell of size, within rect, that point occupies."""
    cell = [None, None]
    point = (point[0] - rect.x, point[1] - rect.y)
    cell[0] = (point[0] // size[0]) * size[0]
    cell[1] = (point[1] // size[1]) * size[1]
    return tuple(cell)


def cursor_from_image(image):
    """Take a valid image and create a mouse cursor."""
    colors = {(0, 0, 0, 255): "X", (255, 255, 255, 255): "."}
    rect = image.get_rect()
    icon_string = []
    for j in range(rect.height):
        this_row = []
        for i in range(rect.width):
            pixel = tuple(image.get_at((i, j)))
            this_row.append(colors.get(pixel, " "))
        icon_string.append("".join(this_row))
    return icon_string


def load_all_gfx(
    directory, colorkey=(255, 0, 255), accept=(".png", ".jpg", ".bmp"), overrides={}
):
    cache = AssetCache()
    return cache.load_images(
        directory=directory, colorkey=colorkey, image_accept=accept, overrides=overrides
    )


def load_all_music(directory, accept=(".wav", ".mp3", ".ogg", ".mdi")):
    """Create a dictionary of paths to music files in given directory
    if their extensions are in accept."""
    cache = AssetCache()
    return cache.load_sounds(directory=directory, accept=accept)


def load_all_fonts(directory, accept=(".ttf",)):
    """Create a dictionary of paths to font files in given directory
    if their extensions are in accept."""
    return load_all_music(directory, accept)


def load_all_movies(directory, accept=(".mpg",)):
    """Create a dictionary of paths to movie files in given directory
    if their extensions are in accept."""
    return load_all_music(directory, accept)


def load_all_sfx(directory, accept=(".wav", ".mp3", ".ogg", ".mdi"), overrides={}):
    """Load all sfx of extensions found in accept.  Unfortunately it is
    common to need to set sfx volume on a one-by-one basis.  This must be done
    manually if necessary in the setup module."""
    cache = AssetCache()
    return cache.load_sfxs(directory=directory, accept=accept, overrides=overrides)


def _fn(filepath):
    return (filepath, os.path.splitext(os.path.split(filepath)[1])[0])
