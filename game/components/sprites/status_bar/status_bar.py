import pygame as pg

from game.components.sprites.shape.shape import Shape


class StatusBar(Shape):
    def __init__(
        self,
        orientation=0,
        width=0,
        height=10,
        primary_color=pg.Color("red"),
        secondary_color=pg.Color("black"),
        tertiary_color=pg.Color("black"),
        border_color=pg.Color("white"),
        border_width=2,
        alpha=pg.SRCALPHA,
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
        self.orientation = orientation

    @property
    def is_landscape(self):
        return not self.orientation

    @property
    def is_portrait(self):
        return not self.is_landscape

    def toggle_orientation(self):
        self.orientation = not self.orientation

    def update(self, primary_percent, *args, **kwargs):
        super().update(*args, **kwargs)
        self.image.fill(self.border_color)

        sl = self.border_width
        st = self.border_width
        sw = self.width - self.border_width * 2
        sh = self.height - self.border_width * 2

        self.image.fill(self.secondary_color, (sl, st, sw, sh))

        if self.is_landscape:
            primary_rect = (
                sl,
                st,
                sw * primary_percent,
                sh,
            )
        else:
            primary_rect = (
                sl,
                st + sh * (1 - primary_percent),
                sw,
                sh * primary_percent,
            )
        self.image.fill(self.primary_color, primary_rect)


class TargetedStatusBar(StatusBar):
    def __init__(
        self, target, offset, current_attribute, max_attribute, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.target = target
        self.offset = offset
        self.current_attribute = current_attribute
        self.max_attribute = max_attribute

    def update(self, *args, **kwargs):
        _c = getattr(self.target, self.current_attribute, 1)
        _m = getattr(self.target, self.max_attribute, 1)
        p = _c / _m

        super().update(p, *args, **kwargs)
        if self.is_landscape:
            self.rect.midbottom = self.target.rect.midtop
            self.rect.y -= self.offset
        else:
            self.rect.midright[0] = self.target.rect.midleft[0]
            self.rect.x -= self.offset


class HealthBar(TargetedStatusBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_color = pg.Color("white")
        self.primary_color = pg.Color("red")
        self.secondary_color = pg.Color("black")
        self.border_width = 2


class StaminaBar(TargetedStatusBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_color = pg.Color("white")
        self.primary_color = pg.Color("green")
        self.secondary_color = pg.Color("black")
        self.border_width = 2


class ManaBar(TargetedStatusBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_color = pg.Color("white")
        self.primary_color = pg.Color("blue")
        self.secondary_color = pg.Color("black")
        self.border_width = 2
