import pygame
from .defaults import *
from enum import Enum

import logging

logger = logging.getLogger(__name__)


BLINK_MOD = 30


class Sprite(pygame.sprite.Sprite):
    is_player = False
    is_enemy = False
    is_npc = False

    class Direction(Enum):
        NORTH = 0
        EAST = 1
        SOUTH = 2
        WEST = 3

    def __init__(self, name=None, image=None, debug=False):
        super().__init__()

        self.image = image
        self._image = image
        self.debug = debug
        self.name = name
        self.direction = None
        self.rect = None
        self.is_flipped = False
        self.pos = (None, None)
        self._layer = 0
        if not self.image:
            self.rect = pygame.Rect((0, 0, 0, 0))
        else:
            self.rect = self.image.get_rect()
        self._image = self.image

        self.blink_timer = 0
        self.blink_color = (255, 255, 255)
        self.blink_persist = False

    def diagnostics_pretty(self, cam=None):
        n = self.name
        c = self.__class__
        r = self.rect
        d = self.direction
        fake_pos = None
        if cam:
            fake_pos = r.center - cam
        msg = f"name: {n}\nreal pos: {r.center}\nfake pos: {fake_pos}\n{d}\nsize: {r.size}\ndebug: {self.debug}"
        return msg

    @property
    def vertices(self):
        l, t, w, h = self.rect
        return [(l, t), (l + w, t), (l + w, t + h), (l, t + h)]

    @property
    def diagnostics(self):
        return {
            "cls": self.__class__,
            "name": self.name,
            "rect": self.rect,
            "dir": self.direction,
            "debug": self.debug,
        }

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    def spawn(self, pos, layer=0, direction=Direction.SOUTH, angle=0, flipped=False):
        self.direction = direction
        self._layer = layer
        if flipped:
            self.flip()
        if angle % 360:
            self.rotate(angle)
        self.pos = pos
        self.rect.topleft = self.pos

    def interact(self, other):
        pass

    def flip(self, flip_x=True, flip_y=False):
        center = self.rect.center
        self.image = pygame.transform.flip(self.image.copy(), flip_x, flip_y)
        self.rect = self.image.get_rect()
        self.rect.center = center
        return self.image

    def rotate(self, angle):
        center = self.rect.center
        self.image = pygame.transform.rotozoom(self.image.copy(), angle, 1)
        self.rect = self.image.get_rect()
        self.rect.center = center
        return self.image

    def draw_hitbox(self):
        pygame.draw.rect(self.image, pygame.Color("red"), self.rect, 3)

    def update(self, surface, camera=None):
        cam = camera
        self.draw()

    def draw(self):
        # if self.blink_timer or self.blink_persist:
        #     if not hasattr(self, "original_image"):
        #         self.original_image = self.image
        #     if self.blink_timer % BLINK_MOD:
        #         self.image = self.original_image
        #     else:
        #         self.image = pygame.Surface(self.rect.size)
        #         self.image.fill(self.blink_color)
        #     self.blink_timer = max(0, self.blink_timer - 1)
        #     if not self.blink_timer:
        #         if self.blink_persist:
        #             self.blink_timer = BLINK_MOD
        #         else:
        #             delattr(self, "original_image")

        if self.debug:
            self.draw_hitbox()

    def blink(self, duration=1, color=(255, 0, 0), persist=False):
        self.blink_color = color
        self.blink_timer = duration * BLINK_MOD
        self.blink_persist = persist

        return True

    def unblink(self):
        self.blink_timer = 0
        self.blink_persist = False
        try:
            delattr(self, "original_image")
        except AttributeError:
            pass

        return True

    def check_collision(self, other):
        return pygame.sprite.collide_rect(self.rect, other.rect)

    def check_collisions(self, others):
        return [self.check_collision(other) for other in others]

    def check_collisions_any(self, others):
        return any(self.check_collisions(others))

    def check_collisions_all(self, others):
        return all(self.check_collisions(others))


class MergedSprite(Sprite):
    def __init__(self, sprites=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sprites = sprites

        self.append([])

    def append(self, others):
        if not isinstance(others, list):
            others = [others]
        self.sprites += others
        self.image = MergedSprite.merge(self.sprites)
        self.rect = self.image.get_rect()
        return self.image

    @staticmethod
    def merge(sprites):
        rect = sprites[0].rect.copy()
        for sprite in sprites[1:]:
            rect.union_ip(sprite.rect)

        # Create a new transparent image with the combined size.
        image = pygame.Surface(rect.size, pygame.SRCALPHA)
        # Now blit all sprites onto the new surface.
        for sprite in sprites:
            image.blit(
                sprite.image, (sprite.rect.x - rect.left, sprite.rect.y - rect.top)
            )
        return image


class AnimatedSprite(Sprite):
    def __init__(self, idle_frames=[], walk_frames=[], black_frames=4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idle_frames = idle_frames
        self.walk_frames = walk_frames
        self.black_frames = black_frames
        self._direction = self.direction

        self.is_idle = True
        self.counter = 0
        self.flipped = False

        self.animation = self.handle_animation()

    def handle_animation(self):
        while True:
            if self.is_idle:
                self.counter = (self.counter + 1) % len(self.idle_frames)
                frame = self.idle_frames[self.counter]
            else:
                self.counter = (self.counter + 1) % len(self.walk_frames)
                frame = self.walk_frames[self.counter]

            self.image = frame

            if not self.is_flipped and self.direction == self.Direction.WEST:
                self.flip()
                self.flipped = True
            elif self.flipped and self.direction == self.Direction.EAST:
                self.flip()
                self.flipped = False

            # if self.debug:
            #     self.draw_hitbox()

            bf = self.black_frames
            if self.is_sprinting:
                bf = self.black_frames
            elif self.is_crouching:
                bf *= 4
            elif self.is_idle:
                bf *= 2
            for x in range(bf):
                yield None

    def update(self, surface, camera=None):
        super().update(surface, camera)
        next(self.animation)
        if self.debug:
            self.draw_hitbox()


class LivingSprite(Sprite):
    def __init__(
        self,
        health=DEFAULT_HEALTH,
        base_health=DEFAULT_HEALTH,
        health_regen=DEFAULT_HEALTH_REGEN,
        base_health_regen=DEFAULT_HEALTH_REGEN,
        stamina=DEFAULT_STAMINA,
        base_stamina=DEFAULT_STAMINA,
        stamina_regen=DEFAULT_STAMINA_REGEN,
        base_stamina_regen=DEFAULT_STAMINA_REGEN,
        mana=DEFAULT_MANA,
        base_mana=DEFAULT_MANA,
        mana_regen=DEFAULT_MANA_REGEN,
        base_mana_regen=DEFAULT_MANA_REGEN,
        experience=DEFAULT_EXPERIENCE,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.base_health = base_health
        self.health = health

        self.base_health_regen = base_health_regen
        self.health_regen = health_regen

        self.base_stamina = base_stamina
        self.stamina = stamina

        self.base_stamina_regen = base_stamina_regen
        self.stamina_regen = stamina_regen

        self.base_mana = base_mana
        self.mana = mana

        self.base_mana_regen = base_mana_regen
        self.mana_regen = mana_regen

        self.experience = experience

    @property
    def level(self):
        return self.experience // 10 + 1


class MovableSprite(Sprite):
    def __init__(
        self,
        walk_speed=DEFAULT_WALK_SPEED,
        walk_speed_modifier=DEFAULT_WALK_SPEED_MODIFIER,
        swim_speed_modifier=DEFAULT_SWIM_SPEED_MODIFIER,
        crouch_speed_modifier=DEFAULT_CROUCH_SPEED_MODIFIER,
        sprint_speed_modifier=DEFAULT_SPRINT_SPEED_MODIFIER,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.is_crouching = 0
        self.is_sprinting = 0
        self.is_swimming = 0
        self.is_dodging = 0

        self.walk_speed = walk_speed
        self.swim_speed_modifier = swim_speed_modifier
        self.walk_speed_modifier = walk_speed_modifier
        self.crouch_speed_modifier = crouch_speed_modifier
        self.sprint_speed_modifier = sprint_speed_modifier
        # self.walk_animation()

        self.update_speed()

    def update_speed(self):
        self.speed = self.walk_speed * self.walk_speed_modifier
        if self.is_crouching:
            self.speed = self.is_crouching * self.crouch_speed_modifier * self.speed
            if self.speed < 1:
                self.speed = 1

        if self.is_sprinting:
            self.speed = self.is_sprinting * self.sprint_speed_modifier * self.speed

        if self.is_swimming:
            self.speed = self.is_swimming * self.swim_speed_modifier * self.speed

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.update_speed()

    def move(self, pos, *args, **kwargs):
        self.pos = pos
        # self.rect = self.image.get_rect()
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]


class CombatantSprite(LivingSprite):
    def __init__(
        self,
        damage=DEFAULT_DAMAGE,
        base_damage=DEFAULT_DAMAGE,
        armor=DEFAULT_ARMOR,
        base_armor=DEFAULT_ARMOR,
        magic_resistance=DEFAULT_MAGIC_RESISTANCE,
        base_magic_resistance=DEFAULT_MAGIC_RESISTANCE,
        fire_resistance=DEFAULT_FIRE_RESISTANCE,
        base_fire_resistance=DEFAULT_FIRE_RESISTANCE,
        water_resistance=DEFAULT_WATER_RESISTANCE,
        base_water_resistance=DEFAULT_WATER_RESISTANCE,
        electricity_resistance=DEFAULT_ELECTRICITY_RESISTANCE,
        base_electricity_resistance=DEFAULT_ELECTRICITY_RESISTANCE,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.damage = damage
        self.base_damage = base_damage
        self.armor = armor
        self.base_armor = base_armor
        self.magic_resistance = magic_resistance
        self.base_magic_resistance = base_magic_resistance
        self.fire_resistance = fire_resistance
        self.base_fire_resistance = base_fire_resistance
        self.water_resistance = water_resistance
        self.base_water_resistance = base_water_resistance
        self.electricity_resistance = electricity_resistance
        self.base_electricity_resistance = base_electricity_resistance

        self.draw_mult = 0

    def attack(self, *others):
        results = {}
        for other in others:
            r = getattr(self, "damage", 0) - getattr(other, "armor", 0)
            # TODO: Implement resistances
            results[other] = self.draw_mult if r == 0 else r > 0
        return results

    def defend(self, *others):
        results = {}
        for other in others:
            r = getattr(self, "armor", 0) - getattr(other, "damage", 0)
            # TODO: Implement resistances
            results[other] = self.draw_mult if r == 0 else r > 0
        return results
