from engine_antiantilopa import Vector2d
from shared.effect import Effect
from shared.io.serializable import Serializable
from .asset_types import UnitType
from serializator.net import flags_to_int, int_to_flags


SerializedEffect = tuple[int, int]
SerializedUnit = tuple[int, int, tuple[int, int], int, int, list[SerializedEffect]]
            
class UnitData(Serializable):
    utype: UnitType
    owner: int
    pos: Vector2d
    health: int
    moved: bool
    attacked: bool
    effects: list[Effect]
    serialized_fields = ["utype", "owner", "pos", "health", "moved", "attacked", "effects"]

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
                
