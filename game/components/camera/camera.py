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
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        init_rect = self._init_rect

        for spr in self.sprites():
            rec = spritedict[spr]
            newrect = surface_blit(spr.image, spr.rect.move(self.cam))
            if rec is init_rect:
                dirty_append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))
                else:
                    dirty_append(newrect)
                    dirty_append(rec)
            spritedict[spr] = newrect

        return dirty
