from pygame_tools_tafh import Vector2d
from .unit_types import UnitType
from serializator.net import flags_to_int
from .city import CityData

class UnitData:
    utype: UnitType
    owner: int
    pos: Vector2d
    health: int
    attached_city: CityData
    moved: bool
    attacked: bool

    def __init__(self, utype: UnitType, owner: int, pos: Vector2d, attached_city: CityData) -> None:
        self.utype = utype
        self.owner = owner
        self.pos = pos
        self.health = utype.health
        self.attached_city = attached_city
        self.moved = True
        self.attacked = True

    def to_serializable(self):
        return [self.utype.id, self.owner, self.pos.as_tuple(), self.health, self.attached_city.pos.as_tuple(), flags_to_int(self.moved, self.attacked)]
    