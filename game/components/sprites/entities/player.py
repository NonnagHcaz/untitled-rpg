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

    def diagnostics_pretty(self, cam=None):
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
                f"kills: {self.kill_count}"
                f"level: {self.level} ({self.experience})"
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

    def draw_bars(self, surface, *args, **kwargs):
        self.draw_health_bar(surface, *args, **kwargs)
        self.draw_mana_bar(surface, *args, **kwargs)
        self.draw_stamina_bar(surface, *args, **kwargs)

    def draw_health_bar(self, surface, *args, **kwargs):
        self._draw_bar(
            surface,
            config.DEFAULT_PLAYER_HEALTH_BAR_ORDER,
            config.DEFAULT_PLAYER_HEALTH_BAR_HEIGHT,
            config.DEFAULT_PLAYER_HEALTH_BAR_COLOR,
            self.health,
            self.base_health,
        )

    def draw_stamina_bar(self, surface, *args, **kwargs):
        self._draw_bar(
            surface,
            config.DEFAULT_PLAYER_STAMINA_BAR_ORDER,
            config.DEFAULT_PLAYER_STAMINA_BAR_HEIGHT,
            config.DEFAULT_PLAYER_STAMINA_BAR_COLOR,
            self.stamina,
            self.base_stamina,
        )

    def draw_mana_bar(self, surface, *args, **kwargs):
        self._draw_bar(
            surface,
            config.DEFAULT_PLAYER_MANA_BAR_ORDER,
            config.DEFAULT_PLAYER_MANA_BAR_HEIGHT,
            config.DEFAULT_PLAYER_MANA_BAR_COLOR,
            self.mana,
            self.base_mana,
        )

    def _draw_bar(self, surface, order, height, color, value, max_value):
        top = self.rect.top - order * (1 + height)
        _mod = 1
        _rect = pygame.Rect(
            self.rect.left - self.rect.left * _mod,
            top,
            self.rect.width * 2 * _mod,
            height,
        )
        _rect.midbottom = self.rect.centerx, top

        draw_player_status_bar(
            surface,
            _rect.topleft,
            _rect.size,
            pygame.Color("black"),
            pygame.Color("white"),
            color,
            value / max_value,
        )


def draw_player_status_bar(
    surf, pos, size, border_color, background_color, progress_color, progress
):
    pygame.draw.rect(surf, background_color, (*pos, *size))
    pygame.draw.rect(surf, border_color, (*pos, *size), 1)
    innerPos = (pos[0] + 1, pos[1] + 1)
    innerSize = ((size[0] - 2) * progress, size[1] - 2)
    rect = (
        round(innerPos[0]),
        round(innerPos[1]),
        round(innerSize[0]),
        round(innerSize[1]),
    )
    pygame.draw.rect(surf, progress_color, rect)
