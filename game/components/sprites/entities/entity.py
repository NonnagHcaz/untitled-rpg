from ..sprite import AnimatedSprite, MovableSprite, CombatantSprite


class Entity(AnimatedSprite, MovableSprite, CombatantSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.health <= 0:
            self.kill()
