import random
from ..entity import Entity

import logging

logger = logging.getLogger(__name__)


class Enemy(Entity):
    def __init__(self, mingle_chance=0.2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mingle_chance = mingle_chance
        self.mingle_timer = 0

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        # Randomly choose to move a direction
        # If true, randomly choose direction to move
        # Else, randomly choose to change direction facing
        if not self.mingle_timer:
            self.mingle_timer = 30
            if random.random() < self.mingle_chance:
                move_x = random.choice([-1, 0, 1])
                move_y = random.choice([-1, 0, 1])
                # TODO: Validate movement
                if move_x == -1:
                    self.direction = self.Direction.WEST
                else:
                    self.direction = self.Direction.EAST

                self.rect.move_ip((move_x * self.walk_speed, move_y * self.walk_speed))
        else:
            self.mingle_timer = max(0, self.mingle_timer - 1)


class Zombie(Enemy):
    is_undead = True

    def __init__(self, kind=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind


class Goblin(Enemy):
    def __init__(self, kind=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind


class Orc(Enemy):
    def __init__(self, kind=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind


class Ogre(Enemy):
    def __init__(self, kind=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind


class Demon(Enemy):
    def __init__(self, kind=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind
