import logging

from game.components.sprites.entities.entity import Entity
from game.components.sprites.ui.hotbar import Hotbar

logger = logging.getLogger(__name__)


class Inventory:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True
        else:
            return False

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        else:
            return False

    def get_item_count(self, item):
        return self.items.count(item)

    def get_all_items(self):
        return self.items[:]


class Player(Entity):
    is_player = True

    def __init__(
        self, weapon=None, armor=None, inventory=None, hotbar=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.weapon = weapon
        self.armor = armor
        self.inventory = inventory or Inventory()
        self.hotbar = hotbar or Hotbar

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
