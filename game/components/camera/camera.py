import pygame as pg


class Camera(pg.Vector2):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CameraAwareLayeredUpdates(pg.sprite.LayeredUpdates):
    def __init__(self, target, world_size, cam):
        super().__init__()

        self.cam = cam
        self.world_size = world_size
        self.set_target(target)

    def set_target(self, target):
        self.target = target
        if self.target:
            self.add(target)

    def update(self, surface, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.target:
            x = -self.target.rect.center[0] + surface.get_rect().width / 2
            y = -self.target.rect.center[1] + surface.get_rect().height / 2
            # print((x, y), self.target.rect.center, surface.get_rect().size)
            self.cam += pg.Vector2((x, y)) - self.cam  # * 0.05
            self.cam.x = max(
                -(self.world_size.width - surface.get_rect().width), min(0, self.cam.x)
            )
            self.cam.y = max(
                -(self.world_size.height - surface.get_rect().height),
                min(0, self.cam.y),
            )

    def draw(self, surface):
        spritedict = self.spritedict
        dirty = self.lostsprites
        self.lostsprites = []
        init_rect = self._init_rect

        zoomed_cam = self.cam.apply_zoom(self.cam)

        for sprite in self.sprites():
            rect = spritedict[sprite]
            newrect = surface.blit(sprite.image, sprite.rect.move(zoomed_cam))
            if rect is init_rect:
                dirty.append(newrect)
            else:
                if newrect.colliderect(rect):
                    dirty.append(newrect.union(rect))
                else:
                    dirty.append(newrect)
                    dirty.append(rect)
            spritedict[sprite] = newrect

        return dirty
