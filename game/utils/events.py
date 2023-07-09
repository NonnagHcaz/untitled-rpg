import pygame as pg

BASEID = pg.USEREVENT + 1
CUSTOM_EVENT_TYPE_POOL_SIZE = 100
CUSTOM_EVENT_TYPES = ["WORLD", "PLAYER", "ENEMY", "EFFECT"]

WORLD_EVENTS_BASEID = (
    BASEID + CUSTOM_EVENT_TYPES.index("WORLD") * CUSTOM_EVENT_TYPE_POOL_SIZE
)
PLAYER_EVENTS_BASEID = (
    BASEID + CUSTOM_EVENT_TYPES.index("PLAYER") * CUSTOM_EVENT_TYPE_POOL_SIZE
)
ENEMY_EVENTS_BASEID = (
    BASEID + CUSTOM_EVENT_TYPES.index("ENEMY") * CUSTOM_EVENT_TYPE_POOL_SIZE
)
EFFECT_EVENTS_BASEID = (
    BASEID + CUSTOM_EVENT_TYPES.index("EFFECT") * CUSTOM_EVENT_TYPE_POOL_SIZE
)

CUSTOM_EVENTS = {"id": BASEID, "events": {""}}


class CustomEvent(object):
    def __init__(self) -> None:
        pass


class CustomEventType(object):
    def __init__(self) -> None:
        pass


class CustomEventManager(object):
    def __init__(self) -> None:
        self.events = {}

    def add(self, name, id=-1):
        if id < 0:
            id = self.next_available_id

    @property
    def next_available_id(self):
        return self._find(sorted(list(self.events.keys())))

    def _find(self, data):
        data = list(sorted(data))
        if data[-1] <= len(data):
            return data[-1] + 1
        r = data[len(data // 2) :]
        l = data[: len(data // 2)]
