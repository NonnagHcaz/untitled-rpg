import pygame

from game.components.sprites.sprite import Sprite


class Cursor(Sprite):
    def __init__(
        self,
        cam,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        self.cam = cam
        self.update()

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def real_rect(self):
        return self.rect.move(-self.cam)

    def get_pos(self):
        return self.real_rect.center

    def collide(self, others):
        # Assuming others is an iterable
        collisions = []
        for other in others:
            if self.real_rect.colliderect(other.rect):
                collisions.append(other)
        return collisions

    def update(self, *args, **kwargs):
        self.pos = pygame.mouse.get_pos()
        self.rect.center = self.pos
