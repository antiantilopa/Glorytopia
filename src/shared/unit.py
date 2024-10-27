from .vmath import Vector2d
from .unit_types import UnitType


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