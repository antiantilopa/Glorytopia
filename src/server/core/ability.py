from typing import Type
from shared.generic_types import GenericType
from .tile import Tile
from . import unit as Unit

class Ability(GenericType[Type["Ability"]]):
    index: int
    
    def __init_subclass__(cls):
        Ability.add(cls)

    @staticmethod
    def after_movement(unit: "Unit.Unit"):
        pass

    @staticmethod
    def after_attack(unit: "Unit.Unit", other: "Unit.Unit"):
        pass

    @staticmethod
    def after_kill(unit: "Unit.Unit", other: "Unit.Unit"):
        pass

    @staticmethod
    def defense_bonus(unit: "Unit.Unit") -> float:
        return 1

    @staticmethod
    def additional_move(unit: "Unit.Unit"):
        pass

    @staticmethod
    def retaliation_bonus(unit: "Unit.Unit", defense_result: int) -> int:
        return defense_result

    @staticmethod
    def retaliation_mitigate(unit: "Unit.Unit", defense_result: int) -> int:
        return defense_result

    @staticmethod
    def attack_bonus(unit: "Unit.Unit", attack_result: int) -> int:
        return attack_result
    
    @staticmethod
    def on_terrain_movement(unit: "Unit.Unit", tile: Tile, movement: int) -> int:
        return 0
    
    @staticmethod
    def save_moved(unit: "Unit.Unit") -> bool:
        return False
    
    @staticmethod
    def save_attacked(unit: "Unit.Unit") -> bool:
        return False

    @staticmethod
    def get_vision_range(unit: "Unit.Unit") -> int:
        return 0
    
    @staticmethod
    def get_visibility(unit: "Unit.Unit") -> bool:
        return 1