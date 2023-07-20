from game.scenes.scene import Scene


class StatisticsScene(Scene):
    def __init__(self, game, asset_cache, next_scene=None, previous_scene=None):
        super().__init__(
            game=game,
            asset_cache=asset_cache,
            next_scene=next_scene,
            previous_scene=previous_scene,
        )
        self.name = "Statistics"
        # Add statistics scene-specific initialization code here

    def get_event(self, event):
        # Add statistics scene-specific event handling code here
        pass

    def update(self, surface, current_time, dt):
        # Add statistics scene-specific update code here
        pass

    def render(self, surface):
        # Add statistics scene-specific rendering code here
        pass
