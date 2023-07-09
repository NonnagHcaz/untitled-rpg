import math
import pygame as pg
from .defaults import *
from ..sprite import Sprite, MovableSprite

import logging

logger = logging.getLogger(__name__)


class Weapon(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def use(self):
        pass

    def use_on(self, other):
        pass


class BladedWeapon(Weapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BluntWeapon(Weapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MagicWeapon(Weapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RangedWeapon(Weapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Bow(RangedWeapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Sword(BladedWeapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Dagger(BladedWeapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Wand(MagicWeapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Projectile(MovableSprite):
    def __init__(self, angle, damage=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.angle = angle
        self.timer = 30
        self.damage = damage
        self.update_speed()

    def update(self, *args, **kwargs):
        _x = self.speed * math.cos(self.angle)
        _y = self.speed * math.sin(self.angle)
        self.rect.move_ip(_x, _y)
        self.timer -= 1

        if self.timer <= 0:
            self.kill()


class Arrow(Projectile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
