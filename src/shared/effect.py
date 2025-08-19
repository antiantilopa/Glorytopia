from shared.generic_types import GenericType
from . import unit as Unit
from . import tile as Tile

class Effect(GenericType["Effect"]):
    id = -1
    duration: int
    name: str
    stackable = True

    ID = 0

    def __init_subclass__(cls):
        Effect.add(cls)
        cls.id = Effect.ID
        Effect.ID += 1
    
    def __init__(self, duration = -1):
        self.duration = duration

    def after_movement(self, unit: "Unit.UnitData"):
        pass

    def after_attack(self, unit: "Unit.UnitData", other: "Unit.UnitData"):
        pass

    def after_kill(self, unit: "Unit.UnitData", other: "Unit.UnitData"):
        pass

    def defense_bonus(self, unit: "Unit.UnitData") -> float:
        return 1

    def additional_move(self, unit: "Unit.UnitData"):
        pass

    def retaliation_bonus(self, unit: "Unit.UnitData", defense_result: int) -> int:
        return defense_result

    def retaliation_mitigate(self, unit: "Unit.UnitData", defense_result: int) -> int:
        return defense_result

    def attack_bonus(self, unit: "Unit.UnitData", attack_result: int) -> int:
        return attack_result
    
    def on_terrain_movement(self, unit: "Unit.UnitData", tile: "Tile.TileData", movement: int) -> int:
        return 0
    
    def save_moved(self, unit: "Unit.UnitData") -> bool:
        return False
    
    def save_attacked(self, unit: "Unit.UnitData") -> bool:
        return False

    def get_vision_range(self, unit: "Unit.UnitData") -> int:
        return 0
    
    def get_visibility(self, unit: "Unit.UnitData") -> bool:
        return 1

    def additional_attack(self, unit: "Unit.UnitData", other: "Unit.UnitData") -> int:
        return 0

    def additional_defense(self, unit: "Unit.UnitData", other: "Unit.UnitData") -> int:
        return 0

    # TODO THIS SHIT IS NOT USED NOW
    def on_end_turn(self, unit: "Unit.UnitData"):
        pass

    def on_start_turn(self, unit: "Unit.UnitData"):
        pass

    def after_heal(self, unit: "Unit.UnitData"):
        pass

    def additional_heal(self, unit: "Unit.UnitData"):
        return 0
    
    def on_death(self, unit: "Unit.UnitData"):
        pass

    def on_spawn(self, unit: "Unit.UnitData"):
        pass

    def to_serializable(self):
        return [type(self).id, self.duration]