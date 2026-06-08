from typing import Callable

from netio import GenericType
from . import tile as tilemodule
from . import unit as unit

class Ability(GenericType):
    # Never should be serialized.
    name: str
    actions: dict[int, Callable[["unit.Unit"], None]] = {}

    ID = 0

    def __init_subclass__(cls):
        ability = cls(cls.name)
        Ability.add(ability)

    def __init__(self, name):
        self.name = name
        self.id = Ability.ID
        Ability.ID += 1

    @staticmethod
    def after_movement(unit: "unit.Unit"):
        pass

    @staticmethod
    def after_attack(unit: "unit.Unit", other: "unit.Unit"):
        pass

    @staticmethod
    def after_kill(unit: "unit.Unit", other: "unit.Unit"):
        pass

    @staticmethod
    def defense_bonus(unit: "unit.Unit", other: "unit.Unit") -> float:
        return 1

    @staticmethod
    def attack_bonus(unit: "unit.Unit", other: "unit.Unit") -> float:
        return 1

    @staticmethod
    def additional_move(unit: "unit.Unit"):
        pass

    @staticmethod
    def retaliation_bonus(unit: "unit.Unit", defense_result: int) -> int:
        return defense_result

    @staticmethod
    def retaliation_mitigate(unit: "unit.Unit", defense_result: int) -> int:
        return defense_result

    @staticmethod
    def on_terrain_movement(unit: "unit.Unit", tile: "tilemodule.Tile", movement: int) -> int:
        return 0
    
    @staticmethod
    def ignore_water(unit: "unit.Unit", tile: "tilemodule.Tile") -> int:
        return 0
    
    @staticmethod
    def ignore_stop_movement(unit: "unit.Unit", tile: "tilemodule.Tile") -> int:
        return 0
    
    @staticmethod
    def stop_movement(unit: "unit.Unit", tile: "tilemodule.Tile") -> bool:
        return 0

    @staticmethod
    def save_moved(unit: "unit.Unit") -> bool:
        return False
    
    @staticmethod
    def save_attacked(unit: "unit.Unit") -> bool:
        return False

    @staticmethod
    def get_vision_range(unit: "unit.Unit") -> int:
        return 0
    
    @staticmethod
    def get_visibility(unit: "unit.Unit", player_id: int) -> bool:
        return 1

    @staticmethod
    def additional_attack(unit: "unit.Unit", other: "unit.Unit") -> int:
        return 0

    @staticmethod
    def additional_defense(unit: "unit.Unit", other: "unit.Unit") -> int:
        return 0

    @staticmethod
    def on_start_turn(unit: "unit.Unit"):
        pass

    @staticmethod
    def after_heal(unit: "unit.Unit"):
        pass

    @staticmethod
    def additional_heal(unit: "unit.Unit"):
        return 0
    
    @staticmethod
    def on_death(unit: "unit.Unit"):
        pass

    @staticmethod
    def on_spawn(unit: "unit.Unit"):
        pass

    @staticmethod
    def on_end_turn(unit: "unit.Unit"):
        pass
    