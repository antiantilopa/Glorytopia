from engine_antiantilopa import Vector2d
from shared.effect import Effect
from .asset_types import UnitType
from serializator.net import flags_to_int, int_to_flags


SerializedEffect = tuple[int, int]
SerializedUnit = tuple[int, int, tuple[int, int], int, int, list[SerializedEffect]]
            
class UnitData:
    utype: UnitType
    owner: int
    pos: Vector2d
    health: int
    moved: bool
    attacked: bool
    effects: list[Effect]

    def __init__(self, utype: UnitType, owner: int, pos: Vector2d) -> None:
        self.utype = utype
        self.owner = owner
        self.pos = pos
        self.health = utype.health
        self.moved = True
        self.attacked = True
        self.effects = []

    def add_effect(self, effect: Effect):
        if (not effect.stackable and not any([effect.name == i.name for i in self.effects])) or effect.stackable:
            self.effects.append(effect)
                

    def to_serializable(self) -> SerializedUnit:
        return [self.utype.id, self.owner, self.pos.as_tuple(), self.health, flags_to_int(self.moved, self.attacked), [(eff.id, eff.duration) for eff in self.effects]]

    @staticmethod
    def from_serializable(serializable: SerializedUnit) -> "UnitData":
        udata = UnitData(UnitType.by_id(serializable[0]), serializable[1], Vector2d.from_tuple(serializable[2]))
        udata.health = serializable[3]
        udata.moved, udata.attacked = int_to_flags(serializable[4], 2)
        
        return udata