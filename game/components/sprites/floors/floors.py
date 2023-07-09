from ..sprite import Sprite, AnimatedSprite, CombatantSprite


class Floor(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Trap(Floor, AnimatedSprite, CombatantSprite):
    def __init__(self, *args, **kwargs):
        self.damage = 10
        super().__init__(*args, **kwargs)
