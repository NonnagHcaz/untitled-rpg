import pygame as pg
import os
import glob
import logging

logger = logging.getLogger(__name__)


class Mapper(object):
    def __init__(self):
        self.map = {}

    @property
    def valid_fmts(self):
        return ["0x72"]

    def load(self, filename, sheet=None, fmt="0x72", overwrite=False):
        if fmt is None:
            fmt = "0x72"  # TODO: Sample x lines and determine fmt
        if fmt not in self.valid_fmts:
            print(f"bad fmt: {fmt}")
            return None

        name = os.path.splitext(os.path.split(filename)[1])[0]

        if fmt == "0x72":
            tiles = self.parse_0x72_mapping(filename)
            for name, rect in tiles.items():
                if name not in self.map or overwrite:
                    self.map[name] = {
                        "sheet": sheet,
                        "mapping": filename,
                        "rect": rect,
                        "type": "tileset",
                    }
            return self.map
        else:
            return None

    def parse_0x72_mapping(self, map_file, header=False, delimiter=" "):
        return parse_0x72_mapping(map_file, header, delimiter)

    def __getitem__(self, name):
        try:
            return self.map[name]
        except:
            return None


class ImageCache(object):
    def __init__(self):
        self.cache = {}
        self.map = Mapper()

    def load_dir(
        self,
        directory,
        colorkey=(255, 0, 255),
        image_accept=(".png", ".jpg", ".bmp"),
        mapping_accept=(".txt", ".json"),
        overwrite=False,
    ):
        """Load all graphics with extensions in the accept argument.  If alpha
        transparency is found in the image the image will be converted using
        convert_alpha().  If no alpha transparency is detected image will be
        converted using convert() and colorkey will be set to colorkey."""

        sheets = []
        mappings = []
        for accept in image_accept:
            sheets += glob.glob(os.path.join(directory, f"*{accept}"), recursive=True)
        for accept in mapping_accept:
            mappings += glob.glob(os.path.join(directory, f"*{accept}"), recursive=True)
        mapping_dict = {os.path.splitext(os.path.split(x)[1])[0]: x for x in mappings}

        for sheet in sheets:
            name = os.path.splitext(os.path.split(sheet)[1])[0]
            mapping = mapping_dict.get(name)

            self.load(sheet=sheet, mapping=mapping, overwrite=False)

        return self.cache

    def load(
        self,
        sheet,
        mapping=None,
        colorkey=(255, 0, 255),
        image_accept=(".png", ".jpg", ".bmp"),
        mapping_accept=(".txt", ".json"),
        overwrite=False,
    ):
        if isinstance(sheet, str) and os.path.isdir(sheet):
            return self.load_dir(sheet, mapping, overwrite)

        name = os.path.splitext(os.path.split(sheet)[1])[0]
        sheet_ext = os.path.splitext(os.path.split(sheet)[1])[1].lower()
        if isinstance(mapping, str):
            mapping_ext = os.path.splitext(os.path.split(mapping)[1])[1].lower()

        if sheet_ext not in [str(x).lower() for x in image_accept] or (
            mapping and mapping_ext not in [str(x).lower() for x in mapping_accept]
        ):
            return None

        if mapping:
            self.map.load(filename=mapping, sheet=sheet, overwrite=False)

        name = os.path.splitext(os.path.split(sheet)[1])[0]
        img = pg.image.load(sheet)
        if img.get_alpha():
            img = img.convert_alpha()
        else:
            img = img.convert()
            img.set_colorkey(colorkey)

        self.cache[name] = img

        return img

    def __getitem__(self, name):
        try:
            return self.cache[name]
        except KeyError:
            try:
                tile = self.map[name]
                sheet = tile["sheet"]
            except TypeError:
                logger.error(f"Missing {name} from Mapper")
                return None
            except KeyError:
                logger.error(f"Missing 'sheet' Mapper entry for {name}")

            image = self.strip_name_from_sheet(
                self[os.path.splitext(os.path.split(sheet)[1])[0]], name
            )
            self.cache[name] = image
            return image

    def _get(self, name, sheet=None):
        print(self.map.map)

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
            tiles[_n] = pg.Rect((float(_l), float(_t)), (float(_w), float(_h)))
        elif len(line_parts) >= 6:
            _f = int(line_parts[5])
            for x in range(_f):
                tiles[_n + f"_f{x}"] = pg.Rect(
                    (float(_l) + float(_w) * x, float(_t)), (float(_w), float(_h))
                )
    return tiles


def _strip(sheet, rect):
    _mult = 1
    sub_surf = pg.transform.scale_by(sheet.subsurface(rect), _mult)
    return sub_surf


def strip_from_sheet(sheet, start, size, columns, rows=1):
    """Strips individual frames from a sprite sheet given a start location,
    sprite size, and number of columns and rows."""
    frames = []
    for j in range(rows):
        for i in range(columns):
            location = (start[0] + size[0] * i, start[1] + size[1] * j)
            rect = pg.Rect(location, size)
            frames.append(_strip(sheet, rect))
    return frames


def strip_coords_from_sheet(sheet, coords, size):
    """Strip specific coordinates from a sprite sheet."""
    frames = []
    for coord in coords:
        location = (coord[0] * size[0], coord[1] * size[1])
        rect = pg.Rect(location, size)
        frames.append(_strip(sheet, rect))
    return frames


def strip_name_from_sheet(sheet, name, mapper):
    rect = mapper[name]["rect"]
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
