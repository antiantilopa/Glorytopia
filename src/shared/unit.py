from engine_antiantilopa import Vector2d
from shared.effect import Effect
from netio import SerializeField, Serializable
from typing import Annotated
from .asset_types import UnitType


class UnitData(Serializable):
    utype: Annotated[UnitType, SerializeField(by_id=True)]
    owner: Annotated[int, SerializeField()]
    pos: Annotated[Vector2d, SerializeField()]
    health: Annotated[int, SerializeField()]
    moved: Annotated[bool, SerializeField()]
    attacked: Annotated[bool, SerializeField()]
    effects: Annotated[list[Effect], SerializeField(by_id=True)]

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
                
