from shared.unit_types import UnitType
from shared.unit import UnitData
from shared.vmath import Vector2d
from enum import Enum

class Unit(UnitData):
    
    def refresh(self):
        self.moved = False
        self.attacked = False

    def doesReach(self, pos: Vector2d, world: ...):
        pass

    def calc_attack(self):
        # TODO calculate attack damage after all modifiers
        raise NotImplementedError
    
    def calc_defense(self):
        # TODO calculate defense after all modifiers
        raise NotImplementedError
    
    def calc_damage(self, damage: int):
        # TODO apply damage to unit
        raise NotImplementedError