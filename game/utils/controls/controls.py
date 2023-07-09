import os
import json

from .defaults import DEFAULT_KEYMAP, DEFAULT_FILENAME

import logging

logger = logging.getLogger(__name__)


class _Binding:
    def __init__(self, name, is_key, is_btn, value):
        pass


class Controls:
    def __init__(self, filename=DEFAULT_FILENAME):
        logger.debug(f"Initializing {self.__class__} object")
        self.filename = filename
        self.map = DEFAULT_KEYMAP

        self.read()
        logger.debug(f"{self.__class__} object initialized")

    # region file methods

    def read(self):
        logger.debug(f"Attempting to load key mapping from file at {self.filename}")
        try:
            with open(self.filename, "r") as fp:
                self.map = json.load(fp)
            logger.debug(f"Key mapping loaded from file at {self.filename}")
        except FileNotFoundError:
            logger.error(f"Key mapping file does not exist at {self.filename}")
            self.reset()

    def write(self):
        logger.debug(f"Attempting to write key mapping to file at {self.filename}")
        os.makedirs(os.path.split(self.filename)[0], exist_ok=True)
        with open(self.filename, "w") as fp:
            json.dump(self.map, fp)
        logger.debug(f"Key mapping written to file at {self.filename}")

    def reset(self):
        logger.debug(f"Attempting to reset key mapping to defaults")
        self.map = DEFAULT_KEYMAP
        self.write()
        logger.debug(f"Key mapping reset to defaults")

    # endregion

    # region "is" methods

    def is_movement(self, key):
        return any(
            [self.is_up(key), self.is_left(key), self.is_down(key), self.is_right(key)]
        )

    def is_up(self, key):
        return key in [self.map["MOVE_UP_PRIMARY"], self.map["MOVE_UP_SECONDARY"]]

    def is_left(self, key):
        return key in [self.map["MOVE_LEFT_PRIMARY"], self.map["MOVE_LEFT_SECONDARY"]]

    def is_down(self, key):
        return key in [self.map["MOVE_DOWN_PRIMARY"], self.map["MOVE_DOWN_SECONDARY"]]

    def is_right(self, key):
        return key in [self.map["MOVE_RIGHT_PRIMARY"], self.map["MOVE_RIGHT_SECONDARY"]]

    def is_dodge(self, key):
        return key in [self.map["DODGE_PRIMARY"], self.map["DODGE_SECONDARY"]]

    def is_crouch_hold(self, key):
        return key in [
            self.map["CROUCH_HOLD_PRIMARY"],
            self.map["CROUCH_HOLD_SECONDARY"],
        ]

    def is_crouch_toggle(self, key):
        return key in [
            self.map["CROUCH_TOGGLE_PRIMARY"],
            self.map["CROUCH_TOGGLE_SECONDARY"],
        ]

    def is_sprint_hold(self, key):
        return key in [
            self.map["SPRINT_HOLD_PRIMARY"],
            self.map["SPRINT_HOLD_SECONDARY"],
        ]

    def is_sprint_toggle(self, key):
        return key in [
            self.map["SPRINT_TOGGLE_PRIMARY"],
            self.map["SPRINT_TOGGLE_SECONDARY"],
        ]

    def is_walk_hold(self, key):
        return key in [self.map["WALK_HOLD_PRIMARY"], self.map["WALK_HOLD_SECONDARY"]]

    def is_walk_toggle(self, key):
        return key in [
            self.map["WALK_TOGGLE_PRIMARY"],
            self.map["WALK_TOGGLE_SECONDARY"],
        ]

    def is_inventory(self, key):
        return key in [self.map["INVENTORY_PRIMARY"], self.map["INVENTORY_SECONDARY"]]

    def is_pause(self, key):
        return key in [self.map["PAUSE_PRIMARY"], self.map["PAUSE_SECONDARY"]]

    def is_confirm(self, key):
        return key in [self.map["CONFIRM_PRIMARY"], self.map["CONFIRM_SECONDARY"]]

    def is_deny(self, key):
        return key in [self.map["DENY_PRIMARY"], self.map["DENY_SECONDARY"]]

    def is_quicksave(self, key):
        return key in [self.map["QUICKSAVE_PRIMARY"], self.map["QUICKSAVE_SECONDARY"]]

    def is_quickload(self, key):
        return key in [self.map["QUICKLOAD_PRIMARY"], self.map["QUICKLOAD_SECONDARY"]]

    # endregion

    # region "pressed" methods

    def _pressed(self, pressed_keys, pressed_btns, expected_names):
        return any(
            [pressed_keys[self.map[expected_name]] for expected_name in expected_names]
        )  # + [pressed_btns[self.map[expected_name]] for expected_name in expected_names])

    def pressed_up(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["MOVE_UP_PRIMARY", "MOVE_UP_SECONDARY"]
        )

    def pressed_left(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["MOVE_LEFT_PRIMARY", "MOVE_LEFT_SECONDARY"]
        )

    def pressed_down(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["MOVE_DOWN_PRIMARY", "MOVE_DOWN_SECONDARY"]
        )

    def pressed_right(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["MOVE_RIGHT_PRIMARY", "MOVE_RIGHT_SECONDARY"]
        )

    def pressed_dodge(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["DODGE_PRIMARY", "DODGE_SECONDARY"]
        )

    def pressed_crouch_hold(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["CROUCH_HOLD_PRIMARY", "CROUCH_HOLD_SECONDARY"]
        )

    def pressed_crouch_toggle(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys,
            pressed_btns,
            ["CROUCH_TOGGLE_PRIMARY", "CROUCH_TOGGLE_SECONDARY"],
        )

    def pressed_sprint_hold(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["SPRINT_HOLD_PRIMARY", "SPRINT_HOLD_SECONDARY"]
        )

    def pressed_sprint_toggle(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys,
            pressed_btns,
            ["SPRINT_TOGGLE_PRIMARY", "SPRINT_TOGGLE_SECONDARY"],
        )

    def pressed_walk_hold(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["WALK_HOLD_PRIMARY", "WALK_HOLD_SECONDARY"]
        )

    def pressed_walk_toggle(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["WALK_TOGGLE_PRIMARY", "WALK_TOGGLE_SECONDARY"]
        )

    def pressed_inventory(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["INVENTORY_PRIMARY", "INVENTORY_SECONDARY"]
        )

    def pressed_pause(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["PAUSE_PRIMARY", "PAUSE_SECONDARY"]
        )

    def pressed_confirm(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["CONFIRM_PRIMARY", "CONFIRM_SECONDARY"]
        )

    def pressed_deny(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["DENY_PRIMARY", "DENY_SECONDARY"]
        )

    def pressed_quicksave(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["QUICKSAVE_PRIMARY", "QUICKSAVE_SECONDARY"]
        )

    def pressed_quickload(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys, pressed_btns, ["QUICKLOAD_PRIMARY", "QUICKLOAD_SECONDARY"]
        )

    def pressed_primary_attack(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys,
            pressed_btns,
            ["PRIMARY_ATTACK_PRIMARY", "PRIMARY_ATTACK_SECONDARY"],
        )

    def pressed_secondary_attack(self, pressed_keys, pressed_btns):
        return self._pressed(
            pressed_keys,
            pressed_btns,
            ["SECONDARY_ATTACK_PRIMARY", "SECONDARY_ATTACK_SECONDARY"],
        )

    # endregion
