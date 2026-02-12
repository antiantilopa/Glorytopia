from shared.generic_object import GenericObject
from shared.util.position import Pos
from . import effect as Effect
from netio import SerializeField, Serializable
from typing import Annotated
from .asset_types import UnitType


class UnitData(GenericObject):
    type: Annotated[UnitType, SerializeField()]
    owner: Annotated[int, SerializeField()]
    pos: Annotated[Pos, SerializeField()]
    health: Annotated[int, SerializeField()]
    moved: Annotated[bool, SerializeField()]
    attacked: Annotated[bool, SerializeField()]
    effects: Annotated[list["Effect.Effect"], SerializeField()]
    attached_city_id: Annotated[int, SerializeField()]

    def __init__(self, unit_type: UnitType, owner: int, pos: Pos) -> None:
        self.type = unit_type
        self.owner = owner
        self.pos = pos
        self.health = unit_type.health
        self.moved = True
        self.attacked = True
        self.attached_city_id = -1
        self.effects = []

    def add_effect(self, effect: "Effect.Effect"):
        if (not effect.type.stackable and not any([effect.type.name == i.type.name for i in self.effects])) or effect.type.stackable:
            self.effects.append(effect)
                
