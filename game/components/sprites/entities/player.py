import logging

from game.components.sprites.entities.entity import Entity

logger = logging.getLogger(__name__)
from game import config
import pygame


class Player(Entity):
    is_player = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weapon = None

    def interact(self, other):
        pass

    def interact_with_coords(self, x, y):
        pass

    def get_data_pretty(self, cam=None):
        n = self.name
        c = self.__class__
        r = self.rect
        d = self.direction
        h = f"{self.health}/{self.base_health}"
        s = f"{self.stamina}/{self.base_stamina}"
        m = f"{self.mana}/{self.base_mana}"
        fake_pos = None
        if cam:
            fake_pos = r.center - cam

        msg = "\n".join(
            [
                f"name: {n}",
                f"pos: {r.center} ({fake_pos})",
                f"dir: {d}",
                f"size: {r.size}",
                f"h: {h}, s: {s}, m: {m}",
                f"cooldown: {self.attack_cooldown_timer} (forced: {self.force_attack_cooldown})",
                f"kills: {self.kill_count}",
                f"level: {self.level} ({self.experience})",
                f"debug: {self.debug}",
            ]
        )

        return msg

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        regen_stamina = not (self.is_sprinting or self.is_dodging or self.is_swimming)
        regen_health = True
        regen_mana = not self.is_attacking
        self.regenerate(
            regen_health=regen_health,
            regen_mana=regen_mana,
            regen_stamina=regen_stamina,
        )
