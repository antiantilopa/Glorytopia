class AbilityIndexes:
    carry = 0
    convert = 1
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
    surprise = 14

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
    utypes: list["UnitType"] = []

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
        UnitType.utypes.append(self)

class UnitTypes:

    warrior = UnitType(
        "warrior", 
        health = 10, 
        attack = 2, 
        defense = 2, 
        movement = 1, 
        attack_range = 1,
        cost = 2, 
        water = False, 
        abilities = [AbilityIndexes.dash, AbilityIndexes.fortify]
    )
    rider = UnitType(
        "rider", 
        health = 10, 
        attack = 2, 
        defense = 1, 
        movement = 2, 
        attack_range = 1,
        cost = 3, 
        water = False, 
        abilities = [AbilityIndexes.dash, AbilityIndexes.fortify, AbilityIndexes.escape]
    )
    archer = UnitType(
        "archer",
        health = 10, 
        attack = 2, 
        defense = 1, 
        movement = 1, 
        attack_range = 2,
        cost = 3, 
        water = False, 
        abilities = [AbilityIndexes.dash, AbilityIndexes.fortify]
    )
    defender = UnitType(
        "defender", 
        health = 15, 
        attack = 1, 
        defense = 3, 
        movement = 1, 
        attack_range = 1,
        cost = 3, 
        water = False, 
        abilities = [AbilityIndexes.fortify]
    )
    swordsman = UnitType(
        "swordsman", 
        health = 15, 
        attack = 3, 
        defense = 3, 
        movement = 1, 
        attack_range = 1,
        cost = 5, 
        water = False, 
        abilities = [AbilityIndexes.dash]
    )
    catapult = UnitType(
        "catapult", 
        health = 10, 
        attack = 4, 
        defense = 0, 
        movement = 1, 
        attack_range = 3,
        cost = 8, 
        water = False, 
        abilities = [AbilityIndexes.stiff]
    )
    knight = UnitType(
        "knight", 
        health = 10, 
        attack = 3.5, 
        defense = 1, 
        movement = 3, 
        attack_range = 1,
        cost = 8, 
        water = False, 
        abilities = [AbilityIndexes.dash, AbilityIndexes.fortify, AbilityIndexes.persist]
    )
    cloack = UnitType(
        "cloack", 
        health = 5, 
        attack = 0, 
        defense = 0.5, 
        movement = 2, 
        attack_range = 1,
        cost = 8, 
        water = False, 
        abilities = [AbilityIndexes.creep, AbilityIndexes.hide, AbilityIndexes.infiltrate, AbilityIndexes.dash, AbilityIndexes.stiff, AbilityIndexes.scout]
    )
    mindbender = UnitType(
        "mindbender", 
        health = 10, 
        attack = 0, 
        defense = 1, 
        movement = 1, 
        attack_range = 1,
        cost = 5, 
        water = False, 
        abilities = [AbilityIndexes.heal, AbilityIndexes.convert]
    )
    giant = UnitType(
        "giant", 
        health = 40, 
        attack = 5, 
        defense = 4, 
        movement = 1, 
        attack_range = 1,
        cost = 0,
        water = False, 
        abilities = [AbilityIndexes.static]
    )
    dagger = UnitType(
        "dagger", 
        health = 10, 
        attack = 2, 
        defense = 2, 
        movement = 1, 
        attack_range = 1,
        cost = 0, 
        water = False, 
        abilities = [AbilityIndexes.dash, AbilityIndexes.surprise]
    )

    @staticmethod
    def by_id(id: int) -> UnitType:
        for utype in UnitType.utypes:
            if utype.id == id:
                return utype
        raise KeyError(id)