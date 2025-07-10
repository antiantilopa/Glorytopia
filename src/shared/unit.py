from engine_antiantilopa import Vector2d
from .asset_types import UnitType
from serializator.net import flags_to_int, int_to_flags

SerializedUnit = tuple[int, int, tuple[int, int], int, int]

class UnitData:
    utype: UnitType
    owner: int
    pos: Vector2d
    health: int
    moved: bool
    attacked: bool

    def __init__(self, utype: UnitType, owner: int, pos: Vector2d) -> None:
        self.utype = utype
        self.owner = owner
        self.pos = pos
        self.health = utype.health
        self.moved = True
        self.attacked = True

    def to_serializable(self) -> SerializedUnit:
        return [self.utype.id, self.owner, self.pos.as_tuple(), self.health, flags_to_int(self.moved, self.attacked)]

    @staticmethod
    def from_serializable(serializable: SerializedUnit) -> "UnitData":
        udata = UnitData(UnitType.by_id(serializable[0]), serializable[1], Vector2d.from_tuple(serializable[2]))
        udata.health = serializable[3]
        udata.moved, udata.attacked = int_to_flags(serializable[4], 2)
        return udata