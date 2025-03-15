from .world import World
from shared.tree import TechNode
from .unit import Unit
from .city import City
from shared.unit_types import UnitType
from shared.tile_types import TileType, BuildingType, BuildingTypes
from pygame_tools_tafh import Vector2d


class Player:
    
    id: int
    money: int
    vision: list[list[int]]
    tree: list[TechNode]
    units: list[Unit]
    cities: list[City]

    def __init__(self, id: int):
        self.id = id
        self.money = 5
        self.vision = [[0 for i in range(World.size.x)] for _ in range(World.size.y)]
        self.tree = []
        self.units = []
        self.cities = []
    
    def harvest(self, pos: Vector2d):
        if World.object.is_in(pos) == False:
            return False
        if World.object.get(pos).resources == False:
            return False
        if self.money < 2:
            return False
        for tech in self.tree:
            if World.object.get(pos).ttype in tech.harvestables:
                for city in self.cities:
                    if pos in city.domain:
                        city.harvest(pos)
                        self.money -= 2
                        return True
                return False
        return False
    
    def build(self, pos: Vector2d, btype: BuildingType):
        if World.object.is_in(pos) == False:
            return False
        if World.object.get(pos).building != btype.prev:
            return False
        if self.money < btype.cost:
            return False
        if not (World.object.get(pos).ttype in btype.ttypes):
            return False
        for tech in self.tree:
            if btype in tech.buildings:
                for city in self.cities:
                    if pos in city.domain:
                        city.build(pos, btype)
                        self.money -= btype.cost
                        return True
                return False
        return False
    
    def destroy(self, pos: Vector2d):
        if World.object.is_in(pos) == False:
            return False
        if World.object.get(pos).building is None:
            return False
        if self.money < BuildingTypes.destroy.cost:
            return False
        for tech in self.tree:
            if BuildingTypes.destroy in tech.buildings:
                for city in self.cities:
                    if pos in city.domain:
                        city.destroy(pos)
                        self.money -= BuildingTypes.destroy.cost
                        return True
                return False
        return False
    
    def create_unit(self, pos: Vector2d, utype: UnitType):
        if World.object.is_in(pos) == False:
            return False
        if self.money < utype.cost:
            return False
        for tech in self.tree:
            if utype in tech.units:
                for city in self.cities:
                    if pos == city.pos:
                        if city.owner == self.id:
                            if city.create_unit(utype):
                                self.money -= utype.cost
                                return True
                            return False
                        return False
                    return False
                return False
        return False


