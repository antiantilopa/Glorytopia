from shared.util.position import Pos
from . import effect as Effect
from netio import SerializeField, Serializable
from typing import Annotated
from .asset_types import UnitType


class UnitData(Serializable):
    utype: Annotated[UnitType, SerializeField()]
    owner: Annotated[int, SerializeField()]
    pos: Annotated[Pos, SerializeField()]
    health: Annotated[int, SerializeField()]
    moved: Annotated[bool, SerializeField()]
    attacked: Annotated[bool, SerializeField()]
    effects: Annotated[list["Effect.Effect"], SerializeField()]
    attached_city_id: Annotated[int, SerializeField()]

    def __init__(self, utype: UnitType, owner: int, pos: Pos) -> None:
        self.utype = utype
        self.owner = owner
        self.pos = pos
        self.health = utype.health
        self.moved = True
        self.attacked = True
        self.attached_city_id = -1
        self.effects = []

    def add_effect(self, effect: "Effect.Effect"):
        if (not effect.etype.stackable and not any([effect.etype.name == i.etype.name for i in self.effects])) or effect.etype.stackable:
            self.effects.append(effect)
                
