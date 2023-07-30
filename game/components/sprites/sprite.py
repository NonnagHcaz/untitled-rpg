import math
import random
import pygame
from enum import Enum

import logging

from game import config

logger = logging.getLogger(__name__)


BLINK_MOD = 30


def calculate_level(experience):
    return int(0.1 * experience**0.5)


def calculate_experience(level):
    return int((10 * level) ** 2)


def calculate_experience_gain(current_experience):
    current_level = calculate_level(current_experience)
    next_level = current_level + 1

    current_level_experience = calculate_experience(current_level)
    next_level_experience = calculate_experience(next_level)

    experience_gain = next_level_experience - current_level_experience
    return experience_gain


class Sprite(pygame.sprite.Sprite):
    is_player = False
    is_enemy = False
    is_npc = False

    class Direction(Enum):
        NORTH = 0
        EAST = 1
        SOUTH = 2
        WEST = 3

    def __init__(
        self,
        name,
        image,
        debug=False,
        experience=0,
        _layer=0,
        pos=(0, 0),
        is_flipped=False,
        direction=Direction.EAST,
        *groups,
        **kwargs,
    ):
        super().__init__(*groups)

        self.experience = experience
        self.debug = debug
        self.name = name
        self.direction = direction
        self.is_flipped = is_flipped
        self.pos = pos
        self._layer = _layer

        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.original_image = self.image

        self.blink_timer = 0
        self.blink_color = (255, 255, 255)
        self.blink_persist = False

    def get_data_pretty(self, cam=None):
        n = self.name
        c = self.__class__
        r = self.rect
        d = self.direction
        fake_pos = None
        if cam:
            fake_pos = r.center - cam
        msg = "\n".join(
            [
                f"name: {n}",
                f"pos: {r.center} ({fake_pos})",
                f"dir: {d}",
                f"size: {r.size}",
                f"debug: {self.debug}",
            ]
        )

        return msg

    @property
    def level(self):
        return calculate_level(self.experience)

    @property
    def until_next_level(self):
        return calculate_experience(self.level + 1) - self.experience

    @property
    def vertices(self):
        l, t, w, h = self.rect
        return [(l, t), (l + w, t), (l + w, t + h), (l, t + h)]

    @property
    def data_attrs(self):
        return [
            "name",
            "debug",
            "experience",
            "pos",
            "direction",
            "_layer",
            "is_flipped",
        ]

    def get_data(self, *attrs):
        if not len(attrs):
            attrs = self.data_attrs
        # Create a dictionary to store the relevant attributes
        data = {"cls": self.__class__}

        for attr in attrs:
            try:
                data[attr] = getattr(self, attr, None)
            except:
                pass
        return data

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
        pygame.draw.rect(self.image, config.HEALTH_RED, self.rect, 3)

    def update(self, *args, **kwargs):
        self.draw()

    def draw(self):
        if self.blink_timer or self.blink_persist:
            if self.blink_timer % BLINK_MOD:
                self.image = self.original_image
            else:
                self.image = pygame.Surface(self.rect.size)
                self.image.fill(self.blink_color)
            self.blink_timer = max(0, self.blink_timer - 1)
            if not self.blink_timer:
                if self.blink_persist:
                    self.blink_timer = BLINK_MOD

        if self.debug:
            self.draw_hitbox()

    def blink(self, duration=1, color=(255, 0, 0), persist=False):
        self.original_image = self.image
        self.original_mask = self.mask
        self.blink_color = color
        self.blink_timer = duration * BLINK_MOD
        self.blink_persist = persist

        return True

    def unblink(self):
        self.blink_timer = 0
        self.blink_persist = False
        self.image = self.original_image
        self.mask = self.original_mask

        return True

    def check_collision(self, other):
        return pygame.sprite.collide_mask(self, other)

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
        self.mask = pygame.mask.from_surface(self.image)
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
        self.idle_masks = [pygame.mask.from_surface(x) for x in self.idle_frames]
        self.walk_masks = [pygame.mask.from_surface(x) for x in self.walk_frames]
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
                mask = self.idle_masks[self.counter]
            else:
                self.counter = (self.counter + 1) % len(self.walk_frames)
                frame = self.walk_frames[self.counter]
                mask = self.walk_masks[self.counter]

            self.image = frame
            self.mask = mask

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

    def update(self, surface, camera=None, *args, **kwargs):
        super().update(surface, camera)
        next(self.animation)


class LivingSprite(Sprite):
    def __init__(
        self,
        health=config.DEFAULT_HEALTH,
        base_health=config.DEFAULT_HEALTH,
        health_regen=config.DEFAULT_HEALTH_REGEN,
        base_health_regen=config.DEFAULT_HEALTH_REGEN,
        stamina=config.DEFAULT_STAMINA,
        base_stamina=config.DEFAULT_STAMINA,
        stamina_regen=config.DEFAULT_STAMINA_REGEN,
        base_stamina_regen=config.DEFAULT_STAMINA_REGEN,
        mana=config.DEFAULT_MANA,
        base_mana=config.DEFAULT_MANA,
        mana_regen=config.DEFAULT_MANA_REGEN,
        base_mana_regen=config.DEFAULT_MANA_REGEN,
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

    def update(
        self, regen_health=False, regen_stamina=False, regen_mana=False, *args, **kwargs
    ):
        super().update(*args, **kwargs)
        self.regenerate(regen_health, regen_stamina, regen_mana)

    def regenerate(self, regen_health=False, regen_stamina=False, regen_mana=False):
        if regen_health:
            self.health = min(self.base_health, self.health + self.health_regen)

        if regen_mana:
            self.mana = min(self.base_mana, self.mana + self.mana_regen)

        if regen_stamina:
            self.stamina = min(self.base_stamina, self.stamina + self.stamina_regen)

    @property
    def data_attrs(self):
        this_attrs = []
        for attr in ["health", "mana", "stamina"]:
            this_attrs += [attr, f"base_{attr}", f"{attr}_regen", f"base_{attr}_regen"]
        return super().data_attrs + this_attrs


class MovableSprite(Sprite):
    def __init__(
        self,
        walk_speed=config.DEFAULT_WALK_SPEED,
        walk_speed_modifier=config.DEFAULT_WALK_SPEED_MODIFIER,
        swim_speed_modifier=config.DEFAULT_SWIM_SPEED_MODIFIER,
        crouch_speed_modifier=config.DEFAULT_CROUCH_SPEED_MODIFIER,
        sprint_speed_modifier=config.DEFAULT_SPRINT_SPEED_MODIFIER,
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

    @property
    def data_attrs(self):
        return (
            super().data_attrs
            + ["walk_speed"]
            + [
                f"{attr}_speed_modifier"
                for attr in ["walk", "swim", "crouch", "sprint"]
            ]
        )

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
        damage=config.DEFAULT_DAMAGE,
        base_damage=config.DEFAULT_DAMAGE,
        blunt_resistance=config.DEFAULT_BLUNT_RESISTANCE,
        base_blunt_resistance=config.DEFAULT_BLUNT_RESISTANCE,
        magic_resistance=config.DEFAULT_MAGIC_RESISTANCE,
        base_magic_resistance=config.DEFAULT_MAGIC_RESISTANCE,
        fire_resistance=config.DEFAULT_FIRE_RESISTANCE,
        base_fire_resistance=config.DEFAULT_FIRE_RESISTANCE,
        water_resistance=config.DEFAULT_WATER_RESISTANCE,
        base_water_resistance=config.DEFAULT_WATER_RESISTANCE,
        electricity_resistance=config.DEFAULT_ELECTRICITY_RESISTANCE,
        base_electricity_resistance=config.DEFAULT_ELECTRICITY_RESISTANCE,
        ice_resistance=config.DEFAULT_ICE_RESISTANCE,
        base_ice_resistance=config.DEFAULT_ICE_RESISTANCE,
        poison_resistance=config.DEFAULT_POISON_RESISTANCE,
        base_poison_resistance=config.DEFAULT_POISON_RESISTANCE,
        dark_resistance=config.DEFAULT_DARK_RESISTANCE,
        base_dark_resistance=config.DEFAULT_DARK_RESISTANCE,
        light_resistance=config.DEFAULT_LIGHT_RESISTANCE,
        base_light_resistance=config.DEFAULT_LIGHT_RESISTANCE,
        bleed_resistance=config.DEFAULT_BLEED_RESISTANCE,
        base_bleed_resistance=config.DEFAULT_BLEED_RESISTANCE,
        attack_cooldown=config.DEFAULT_ATTACK_COOLDOWN,
        kill_count=0,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.damage = damage
        self.base_damage = base_damage

        self.blunt_resistance = blunt_resistance
        self.base_blunt_resistance = base_blunt_resistance
        self.magic_resistance = magic_resistance
        self.base_magic_resistance = base_magic_resistance
        self.fire_resistance = fire_resistance
        self.base_fire_resistance = base_fire_resistance
        self.water_resistance = water_resistance
        self.base_water_resistance = base_water_resistance
        self.electricity_resistance = electricity_resistance
        self.base_electricity_resistance = base_electricity_resistance
        self.poison_resistance = poison_resistance
        self.base_poison_resistance = base_poison_resistance
        self.ice_resistance = ice_resistance
        self.base_ice_resistance = base_ice_resistance
        self.dark_resistance = dark_resistance
        self.base_dark_resistance = base_dark_resistance
        self.light_resistance = light_resistance
        self.base_light_resistance = base_light_resistance
        self.bleed_resistance = bleed_resistance
        self.base_bleed_resistance = base_bleed_resistance

        self.attack_cooldown = attack_cooldown
        self.kill_count = kill_count

        self.draw_mult = 0
        self.attack_cooldown_timer = 0.0
        self.force_attack_cooldown = False
        self.force_until_config = {}
        self.is_attacking = False

    @property
    def data_attrs(self):
        this_attrs = [
            "damage",
            "base_damage",
            "blunt_resistance",
            "base_blunt_resistance",
            "attack_cooldown",
            "kill_count",
        ]
        for attr in [
            "magic",
            "fire",
            "water",
            "electricity",
            "posion",
            "ice",
            "dark",
            "light",
            "bleed",
        ]:
            this_attrs += [f"{attr}_resistance", f"base_{attr}_resistance"]
        return super().data_attrs + this_attrs

    def force_attack_cooldown_until(self, field1, operator1, field2, operator2, equals):
        self.force_until_config = {
            "f1": field1,
            "op1": operator1,
            "f2": field2,
            "op2": operator2,
            "eq": equals,
        }
        self.force_attack_cooldown = True

    def toggle_force_attack_cooldown(self):
        self.force_attack_cooldown = not self.force_attack_cooldown

    def _check_forced_done(self):
        if not (self.force_attack_cooldown or self.force_until_config):
            return True
        f1 = self.force_until_config.get("f1")
        f2 = self.force_until_config.get("f2")
        op1 = self.force_until_config.get("op1")
        op2 = self.force_until_config.get("op2")
        eq = self.force_until_config.get("eq")
        f1v = getattr(self, f1, None)
        f2v = getattr(self, f2, None)

        try:
            result = eval(f"{f1v} {op1} {f2v} {op2} {eq}")
        except Exception as ex:
            raise ex
        else:
            return result

    def update(self, surface, camera=None, *args, **kwargs):
        super().update(surface, camera)

        if self.force_attack_cooldown and self._check_forced_done():
            self.toggle_force_attack_cooldown()
            self.attack_cooldown_timer = 0

        if not self.force_attack_cooldown:
            self.attack_cooldown_timer = max(
                0.0,
                self.attack_cooldown_timer - self.attack_cooldown,
            )

    def attack(self, *others):
        results = {}
        for other in others:
            results[other] = other.defend(self)[self]

            if not other or not other.alive() or getattr(other, "health", 1) <= 0:
                self.kill_count += 1
                exp = calculate_experience_gain(self.experience)
                self.experience += exp * 10 if getattr(other, "is_boss", False) else exp
        return results

    def defend(self, *others):
        results = {}
        for other in others:
            # TODO: Implmenet absorbing damage if the entity has a specific trait based on damage type
            raw_damage = max(
                0, getattr(other, "damage", 0) - getattr(self, "blunt_resistance", 0)
            )
            magic_damage = max(
                0,
                getattr(other, "magic_damage", 0)
                - getattr(self, "magic_resistance", 0),
            )

            fire_damage = max(
                0,
                getattr(other, "fire_damage", 0) - getattr(self, "fire_resistance", 0),
            )

            water_damage = max(
                0,
                getattr(other, "water_damage", 0)
                - getattr(self, "water_resistance", 0),
            )
            fire_damage = min(
                0,
                getattr(self, "fire_resistance", 0)
                - max(
                    0,
                    getattr(other, "fire_damage", 0),
                ),
            )
            electricity_damage = max(
                0,
                getattr(other, "electricity_damage", 0)
                - getattr(self, "electricity_resistance", 0),
            )
            dark_damage = max(
                0,
                getattr(other, "dark_damage", 0) - getattr(self, "dark_resistance", 0),
            )
            light_damage = max(
                0,
                getattr(other, "light_damage", 0)
                - getattr(self, "light_resistance", 0),
            )
            ice_damage = max(
                0, getattr(other, "ice_damage", 0) - getattr(self, "ice_resistance", 0)
            )
            air_damage = max(
                0, getattr(other, "air_damage", 0) - getattr(self, "air_resistance", 0)
            )
            poison_damage = max(
                0,
                getattr(other, "poison_damage", 0)
                - getattr(self, "poison_resistance", 0),
            )

            anti_synergies = {
                ("dark", "light"): dark_damage - light_damage
                if getattr(self, "dark_resistance", 0)
                and getattr(other, "dark_damage", 0)
                else light_damage,
                ("fire", "water"): fire_damage - water_damage
                if getattr(self, "fire_resistance", 0)
                and getattr(other, "fire_damage", 0)
                else water_damage,
            }

            synergies = {
                ("electricity", "water"): water_damage * electricity_damage,
                ("electricity", "air"): air_damage * electricity_damage,
                ("fire", "ice"): ice_damage * fire_damage,
                ("dark", "fire"): fire_damage * dark_damage,
                ("poison", "dark"): poison_damage * dark_damage,
            }

            # Find max damage potential from other based on own blunt_resistance and resistances

            damage_taken = max(
                raw_damage,
                magic_damage,
                electricity_damage,
                max(*list(anti_synergies.values())),
                max(*list(synergies.values())),
            )

            self.health = max(
                0,
                self.health - damage_taken,
            )
            if damage_taken > 0:
                blink_color = config.HEALTH_RED
            else:
                blink_color = pygame.Color("white")
            self.blink(color=blink_color)
            results[other] = self.health
        return results
