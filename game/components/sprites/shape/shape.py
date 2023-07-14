import pygame
import math

from game.components.sprites.sprite import Sprite


class Shape(Sprite):
    def __init__(
        self,
        width=0,
        height=0,
        primary_color=pygame.Color("white"),
        secondary_color=pygame.Color("black"),
        tertiary_color=pygame.Color("black"),
        border_color=pygame.Color("black"),
        border_width=0,
        alpha=pygame.SRCALPHA,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.width = width
        self.height = height or width
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.tertiary_color = tertiary_color
        self.border_color = border_color
        self.border_width = border_width
        self.alpha = alpha

        self.image = pygame.Surface((self.width, self.height), self.alpha)
        self.rect = self.image.get_rect()
        self.draw()

    def draw(self):
        self.image.fill((0, 0, 0, 0))


class Polygon(Shape):
    def __init__(
        self,
        sides=4,
        width=0,
        height=0,
        primary_color=pygame.Color("white"),
        secondary_color=pygame.Color("black"),
        tertiary_color=pygame.Color("black"),
        border_color=pygame.Color("black"),
        border_width=0,
        alpha=pygame.SRCALPHA,
        *args,
        **kwargs,
    ):
        self.sides = sides
        super().__init__(
            width=width,
            height=height,
            primary_color=primary_color,
            secondary_color=secondary_color,
            tertiary_color=tertiary_color,
            border_color=border_color,
            border_width=border_width,
            alpha=alpha,
            *args,
            **kwargs,
        )

    @property
    def vertices(self):
        n = self.sides
        l = self.width
        vertices = []
        radius = l / 2  # Calculate the radius of the bounding circle

        for i in range(n):
            angle = (2 * math.pi * i) / n  # Calculate the angle for each vertex
            x = radius * math.cos(angle)  # Calculate the x-coordinate of the vertex
            y = radius * math.sin(angle)  # Calculate the y-coordinate of the vertex
            vertices.append((x, y))

        return vertices

    def draw(self):
        pygame.draw.polygon(
            self.image, self.border_color, self.vertices, self.border_width
        )
        # pygame.draw.polygon(self.image, self.primary_color, self.vertices)


class Hitbox(Polygon):
    def __init__(
        self,
        target,
        sides=4,
        width=0,
        height=0,
        primary_color=(0, 0, 0, 0),
        secondary_color=(0, 0, 0, 0),
        tertiary_color=(0, 0, 0, 0),
        border_color=pygame.Color("red"),
        border_width=3,
        alpha=pygame.SRCALPHA,
        *args,
        **kwargs,
    ):
        self.target = target
        if not width:
            width = self.target.rect.width
        if not height:
            height = self.target.rect.height
        super().__init__(
            sides=sides,
            width=width,
            height=height,
            primary_color=primary_color,
            secondary_color=secondary_color,
            tertiary_color=tertiary_color,
            border_color=border_color,
            border_width=border_width,
            alpha=alpha,
            *args,
            **kwargs,
        )

    # @property
    # def vertices(self):
    #     l, t, w, h = self.rect
    #     return [(l, t), (l + w, t), (l + w, t + h), (l, t + h)]

    def update(self):
        self.rect.center = self.target.rect.center


class Crosshair(Shape):
    def __init__(
        self,
        width=0,
        height=0,
        primary_color=pygame.Color("white"),
        secondary_color=pygame.Color("black"),
        tertiary_color=pygame.Color("black"),
        border_color=pygame.Color("black"),
        border_width=0,
        alpha=pygame.SRCALPHA,
        *args,
        **kwargs,
    ):
        super().__init__(
            width=width,
            height=height,
            primary_color=primary_color,
            secondary_color=secondary_color,
            tertiary_color=tertiary_color,
            border_color=border_color,
            border_width=border_width,
            alpha=alpha,
            *args,
            **kwargs,
        )

    def draw(self):
        self.image.fill((0, 0, 0, 0))
        inner_width = 6
        self.image.fill(
            self.primary_color,
            (self.width / 2 - inner_width / 2, 0, inner_width, self.height),
        )
        self.image.fill(
            self.primary_color,
            (0, self.height / 2 - inner_width / 2, self.width, inner_width),
        )
        inner_width /= 2
        self.image.fill(
            self.secondary_color,
            (self.width / 2 - inner_width / 2, 0, inner_width, self.height),
        )
        self.image.fill(
            self.secondary_color,
            (0, self.height / 2 - inner_width / 2, self.width, inner_width),
        )
