import pygame as pg

from game import prepare


class MappedImageCache(object):
    def __init__(self, sheet, mapping, *args, **kwargs):
        self.cache = {}
        self.mapping = mapping
        self.map = CoordinateMap()
        self.map.read(self.mapping)

        self.sheet = sheet

    def __getitem__(self, name):
        try:
            return self.cache[name]
        except KeyError:
            image = self.map.strip_name_from_sheet(self.sheet, name)
            self.cache[name] = image
            return image


class CoordinateMap(object):
    def __init__(self, *args, **kwargs):
        self.map = {}

    def read(self, filename):
        return self.read_lines(filename)

    def read_lines(self, filename, header=False, delimiter=" "):
        with open(filename, "r") as fp:
            lines = fp.readlines()

        for line in lines:
            _n, _l, _t, _w, _h = line.split()
            self.map[_n] = pg.Rect((float(_l), float(_t)), (float(_w), float(_h)))

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


def _strip(sheet, rect):
    _mult = prepare.TEXTURE_SCALE
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
    rect = mapper[name]
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
