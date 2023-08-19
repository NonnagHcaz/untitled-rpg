import pygame

from game.sprites.status_bar.status_bar import (
    ExperienceBar,
    HealthBar,
    StaminaBar,
    ManaBar,
    TargetedStatusBar,
)


class UIStatusBar(TargetedStatusBar):
    def __init__(self, *args, **kwargs):
        kwargs["follow_target"] = False
        super().__init__(*args, **kwargs)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)


class UIHealthBar(UIStatusBar, HealthBar):
    pass


class UIStaminaBar(UIStatusBar, StaminaBar):
    pass


class UIManaBar(UIStatusBar, ManaBar):
    pass


class UIExperienceBar(UIStatusBar, ExperienceBar):
    pass
