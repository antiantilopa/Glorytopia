from typing import Annotated
from netio import GenericType, Serializable, SerializeField
from . import unit as Unit
from . import tile as Tile

class EffectType(GenericType):
    stackable = True

    name: str

    ID = 0
    
    def __init_subclass__(cls):
        etype = cls(cls.name)
        EffectType.add(etype)

    def __init__(self, name = ""):
        self.name = name
        self.id = EffectType.ID
        EffectType.ID += 1

    @staticmethod
    def after_movement(effect: "Effect", unit: "Unit.UnitData"):
        pass

    @staticmethod
    def after_attack(effect: "Effect", unit: "Unit.UnitData", other: "Unit.UnitData"):
        pass

    @staticmethod
    def after_kill(effect: "Effect", unit: "Unit.UnitData", other: "Unit.UnitData"):
        pass

    @staticmethod
    def defense_bonus(effect: "Effect", unit: "Unit.UnitData") -> float:
        return 1

    @staticmethod
    def additional_move(effect: "Effect", unit: "Unit.UnitData"):
        pass

    @staticmethod
    def retaliation_bonus(effect: "Effect", unit: "Unit.UnitData", defense_result: int) -> int:
        return defense_result

    @staticmethod
    def retaliation_mitigate(effect: "Effect", unit: "Unit.UnitData", defense_result: int) -> int:
        return defense_result

    @staticmethod
    def attack_bonus(effect: "Effect", unit: "Unit.UnitData", attack_result: int) -> int:
        return attack_result
    
    @staticmethod
    def on_terrain_movement(effect: "Effect", unit: "Unit.UnitData", tile: "Tile.TileData", movement: int) -> int:
        return 0
    
    @staticmethod
    def save_moved(effect: "Effect", unit: "Unit.UnitData") -> bool:
        return False
    
    @staticmethod
    def save_attacked(effect: "Effect", unit: "Unit.UnitData") -> bool:
        return False

    @staticmethod
    def get_vision_range(effect: "Effect", unit: "Unit.UnitData") -> int:
        return 0
    
    @staticmethod
    def get_visibility(effect: "Effect", unit: "Unit.UnitData", player_id: int) -> bool:
        return 1

    @staticmethod
    def additional_attack(effect: "Effect", unit: "Unit.UnitData", other: "Unit.UnitData") -> int:
        return 0

    @staticmethod
    def additional_defense(effect: "Effect", unit: "Unit.UnitData", other: "Unit.UnitData") -> int:
        return 0

    @staticmethod
    def on_end_turn(effect: "Effect", unit: "Unit.UnitData"):
        pass

    @staticmethod
    def on_start_turn(effect: "Effect", unit: "Unit.UnitData"):
        pass

    @staticmethod
    def after_heal(effect: "Effect", unit: "Unit.UnitData"):
        pass

    @staticmethod
    def additional_heal(effect: "Effect", unit: "Unit.UnitData"):
        return 0
    
    @staticmethod
    def on_death(effect: "Effect", unit: "Unit.UnitData"):
        pass

    @staticmethod
    def on_spawn(effect: "Effect", unit: "Unit.UnitData"):
        pass

class Effect(Serializable):
    etype: Annotated[EffectType, SerializeField()]
    duration: Annotated[int, SerializeField()]
    args: Annotated[list[int], SerializeField()]

    def __init__(self, etype: EffectType, duration: int, args: list[int] = []):
        self.etype = etype
        self.duration = duration
        self.args = args