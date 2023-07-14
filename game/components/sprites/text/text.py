import re
import pygame
import math


class FontManager(object):
    def __init__(self):
        self.cache = {"default": None}
        _attrs = dir(self)
        self._attrs = _attrs

    def add_font(self, filename, weight=None, is_italic=False, is_bold=False):
        if weight in self._attrs:
            return False
        self.cache[weight] = filename
        setattr(self, weight, filename)


class Text(pygame.sprite.Sprite):
    def __init__(
        self,
        text,
        font_file=None,
        size=12,
        color=(255, 255, 255),
        bold=False,
        italic=False,
        underline=False,
        strikethrough=False,
        weight=None,
        max_width=0,
        max_height=0,
    ):
        # Call the target class (Sprite) constructor
        super().__init__()

        self.text = text
        self.size = size
        self._size = size
        self.font_file = font_file
        self.color = color
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough
        self.weight = weight
        self.max_height = max_height
        self.max_width = max_width

        self._init_fonts()

        self.render()
        self.rect = self.image.get_rect()

    def _init_fonts(self):
        self.font = pygame.font.Font(self.font_file, self.size)
        # self.bold_font = pygame.font.Font(self.bold_font_file, self.size)
        # self.italic_font = pygame.font.Font(self.italic_font_file, self.size)

    def _render(self, lines, font, color):
        if not isinstance(lines, list):
            lines = self._split_text(lines, font, color)
        renders = []
        index = 0
        for line in lines:
            size = font.size(line)
            image = font.render(line, 1, color)
            renders.append({"size": size, "image": image, "index": index})
            index += 1
        surface_width = max([x["size"][0] for x in renders])
        surface_height = sum([x["size"][1] for x in renders])
        surface = pygame.Surface((surface_width, surface_height))
        left, top = (0, 0)
        for render in renders:
            width, height = render["size"]
            rect = (left, top, width, height)
            surface.blit(render["image"], rect)
            top += height + 1
        return surface

    def _split_text(self, line):
        fake_lines = line.split("\n")
        lines = []
        for fake_line in fake_lines:
            words = re.split(" *", fake_line)

            _line = ""
            for word in words:
                word += " "
                if self._check_width(_line + word) > 1:
                    lines.append(_line)
                    _line = ""
                _line += word
            if _line:
                lines.append(_line)

    def _check_width(self, line):
        return (
            1
            if not self.max_width
            else math.ceil(self.font.size(line)[0] / self.max_width)
        )

    def render(
        self,
        text=None,
        size=None,
        bold=None,
        italic=None,
        underline=None,
        strikethrough=None,
        *args,
        **kwargs
    ):
        # Check if the font size attribute has changed since the last time the Font objects were initialized. If so, we need to re-initialize the Font objects
        if text is not None:
            self.text = text
        if size is not None:
            self.size = size  # TODO: Validation
        if bold is not None:
            self.bold = bold
        if italic is not None:
            self.italic = italic
        if underline is not None:
            self.underline = underline
        if strikethrough is not None:
            self.strikethrough = strikethrough

        if isinstance(self.text, str):
            text = self.text
        else:
            text = self.text()

        if self.size != self._size:
            self._init_fonts()
            self._size = self.size

        font = self.font
        font.bold = self.bold
        font.italic = self.italic
        font.underline = self.underline
        font.strikethrough = self.strikethrough
        self.image = self._render(text.split("\n"), font, self.color)

    def update(self, *args, **kwargs):
        self.render(**kwargs)


class TargetedText(Text):
    def __init__(self, target, angle=90, offset=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = target
        self.angle = angle
        self.offset = offset

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        r0 = self.target.rect
        x0, y0 = r0.center
        w0, h0 = r0.size
        d0 = math.sqrt(w0**2 + h0**2)

        r1 = self.rect
        w1, h1 = r1.size
        d1 = math.sqrt(w1**2 + h1**2)

        d = (d0 + d1) / 2 + self.offset

        m = math.tan(self.angle % 360)

        self.rect.center = (x0, y0 + h0 / 2 + self.offset + h1 / 2)


def get_next_point(x0, y0, m, d):
    s = -1 if m < 0 else 1
    x1 = x0 + s * math.sqrt(d**2 / (1 + m**2))
    y1 = y0 + s * m * (x1 - x0)
    return (x1, y1)
