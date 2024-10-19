from enum import Enum


class Abilities(Enum):
    carry = 0
    covert = 1
    creep = 2
    dash = 3
    escape = 4
    fortify = 5
    heal = 6
    hide = 7
    infiltrate = 8
    persist = 9
    scout = 10
    splash = 11
    static = 12
    stiff = 13
    
class UnitType:
    id: int
    name: str
    health: int
    attack: float
    diffence: float
    movement: int
    attackrange: int
    cost: int
    water: bool
    abilities: list[int]

    ID = 0
    
    def __init__(self, 
                 name: str = "default", 
                 health: int = 0, 
                 attack: float = 0, 
                 diffence: float = 0, 
                 movement: int = 0, 
                 attackrange: int = 0, 
                 cost: int = 0, 
                 water: bool = False, 
                 abilities: list[int] = []) -> None:
        self.id = UnitType.ID
        UnitType.ID += 1
        self.name = name
        self.health = health
        self.attack = attack
        self.diffence = diffence
        self.movement = movement
        self.attackrange = attackrange
        self.cost = cost
        self.water = water
        self.abilities = abilities

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
