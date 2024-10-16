class TechNode:
    name: str
    cost: int
    units: list[0]
    buildings: list[0]
    achievments: list[0]
    harvestables: list[0]
    effects: list[0]
    defence: list[0]

    def __init__(self,
                name: str,
                cost: int,
                units: list,
                buildings: list,
                achievments: list,
                harvestables: list,
                defence: list) -> None:
        self.name = name
        self.cost = cost
        self.units = units
        self.buildings = buildings
        self.achievments = achievments
        self.harvestables = harvestables
        self.defence = defence
