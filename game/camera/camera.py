import pygame


class Camera(pygame.Vector2):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zoom_level = 1.0
        self.max_level = 3.0
        self.min_level = 1.0

    def set_zoom(self, zoom_level):
        self.zoom_level = zoom_level

    def zoom_in(self, zoom_step=0.1):
        self.zoom_level = min(self.max_level, self.zoom_level + zoom_step)

    def zoom_out(self, zoom_step=0.1):
        self.zoom_level = max(self.min_level, self.zoom_level - zoom_step)

    def apply_zoom(self, position):
        return position * self.zoom_level

    def apply_inverse_zoom(self, position):
        return position / self.zoom_level


class CameraAwareLayeredUpdates(pygame.sprite.LayeredUpdates):
    def __init__(self, target, world_size, cam):
        super().__init__()

        self.cam = cam
        self.world_size = world_size
        self.set_target(target)

    def set_target(self, target):
        self.target = target
        if self.target:
            self.add(target)

    def update(self, surface, camera=None, *args, **kwargs):
        super().update(surface=surface, camera=camera or self.cam, *args, **kwargs)
        if self.target:
            x = -self.target.rect.center[0] + surface.get_rect().width / 2
            y = -self.target.rect.center[1] + surface.get_rect().height / 2

            zoomed_x = self.cam.apply_zoom(pygame.Vector2((x, y))).x
            zoomed_y = self.cam.apply_zoom(pygame.Vector2((x, y))).y

            self.cam += pygame.Vector2((zoomed_x, zoomed_y)) - self.cam
            self.cam.x = max(
                -(self.world_size.width - surface.get_rect().width), min(0, self.cam.x)
            )
            self.cam.y = max(
                -(self.world_size.height - surface.get_rect().height),
                min(0, self.cam.y),
            )

    def draw(self, surface, *args, **kwargs):
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
