from ..tile_types import ResourceType, BuildingType, TileType
from ..unit_types import UnitType

class TechNode:
    id: int
    name: str
    cost: int
    parent: "TechNode|None"
    tier: int
    units: list[UnitType]
    buildings: list[BuildingType]
    achievements: list[0]
    harvestables: list[ResourceType]
    defence: list[TileType]

    ID = 0
    techs: list["TechNode"] = []

    def __init__(self,
                 name: str,
                 cost: int,
                 parent: "TechNode|None",
                 tier: int,
                 units: list,
                 buildings: list,
                 achievements: list,
                 harvestables: list,
                 defence: list) -> None:
        self.id = TechNode.ID
        TechNode.ID += 1
        self.name = name
        self.cost = cost
        self.parent = parent
        self.tier = tier
        self.units = units
        self.buildings = buildings
        self.achievements = achievements
        self.harvestables = harvestables
        self.defence = defence
        TechNode.techs.append(self)
    
    @staticmethod
    def by_id(id: int) -> "TechNode":
        for tech in TechNode.techs:
            if tech.id == id:
                return tech
        raise KeyError(id)