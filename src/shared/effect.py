from shared.generic_types import GenericType
from shared.io.serializable import Serializable
from . import unit as Unit
from . import tile as Tile

class Effect(GenericType["Effect"], use_from_serializable = 0):
    id = -1
    duration: int
    name: str
    stackable = True
    args: list
    serialized_fields = ["id", "args"]

    ID = 0

    def __init_subclass__(cls):
        Effect.add(cls)
        cls.id = Effect.ID
        Effect.ID += 1

        @classmethod
        def from_serializable(cls: type[Effect], data):
            return Serializable.from_serializable.__func__(cls, data)
        
        def to_serializable(self):
            return Effect.to_serializable(self)
    
        cls.serialized_fields = cls.args
        cls.from_serializable = from_serializable
        cls.to_serializable = to_serializable
    
    def __init__(self, duration = -1):
        self.duration = duration

    @classmethod
    def from_serializable(cls: type["Effect"], data):
        return Effect.by_id(data[cls.serialized_fields.index("id")]).from_serializable(data[cls.serialized_fields.index("args")])

    def to_serializable(self):
        return [self.id, Serializable.to_serializable(self)]

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