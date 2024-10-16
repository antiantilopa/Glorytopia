from enum import Enum

from .unit import UnitType


class UnitTypes(Enum):
    warrior = UnitType("warrior", 
                    health = 0, 
                    attack = 0, 
                    diffence = 0, 
                    movement = 0, 
                    attackrange = 0, 
                    cost = 0, 
                    water = False, 
                    abilities = [])
