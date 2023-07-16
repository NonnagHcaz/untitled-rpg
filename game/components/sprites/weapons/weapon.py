import math
import random
import pygame

import logging

from game.components.sprites.sprite import CombatantSprite, MovableSprite, Sprite

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


class Projectile(CombatantSprite, MovableSprite):
    def __init__(self, angle, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.angle = math.radians(angle)  # Convert angle to radians

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        _x = self.speed * math.cos(self.angle)
        _y = -self.speed * math.sin(self.angle)
        self.rect.move_ip(_x, _y)

        self.health -= 1
        if self.health <= 0:
            self.kill()


class Arrow(Projectile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MagicOrb(Projectile):
    def __init__(
        self,
        color=None,
        radius=4,
        border_color=pygame.Color("black"),
        border_width=1,
        *args,
        **kwargs
    ):
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
        image = self._create_orb_surface(color, radius, border_color, border_width)
        kwargs["image"] = image
        super().__init__(*args, **kwargs)

    def _create_orb_surface(self, color, radius, border_color, border_width):
        image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

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

        return image
