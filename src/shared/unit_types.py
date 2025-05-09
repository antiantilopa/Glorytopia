class AbilityIndexes:
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
    defense: float
    movement: float
    attack_range: int
    cost: int
    water: bool
    abilities: list[int]

    ID = 0
    
    def __init__(self, 
                 name: str = "default", 
                 health: int = 0, 
                 attack: float = 0, 
                 defense: float = 0, 
                 movement: int = 0, 
                 attack_range: int = 0,
                 cost: int = 0, 
                 water: bool = False, 
                 abilities: list[int] = []) -> None:
        self.id = UnitType.ID
        UnitType.ID += 1
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.movement = movement
        self.attack_range = attack_range
        self.cost = cost
        self.water = water
        self.abilities = abilities

class UnitTypes:
    warrior = UnitType("warrior", 
                    health = 10, 
                    attack = 2, 
                    defense = 2, 
                    movement = 1, 
                    attack_range = 1,
                    cost = 2, 
                    water = False, 
                    abilities = [AbilityIndexes.dash, AbilityIndexes.fortify])

    objs = [
        warrior
    ]

    def by_id(id: int):
        for utype in UnitTypes.objs:
            if utype.id == id:
                return utype
        raise KeyError(id)