from .random_names import random_funny_name as random_name
from pygame_tools_tafh import Vector2d
from shared.unit_types import UnitType
from shared.city import CityData
from shared.tile_types import BuildingType

from .world import World
from .unit import Unit


class City(CityData):
    cities: list["City"] = []

    def __init__(self, pos: Vector2d, owner: int):
        CityData.__init__(self, pos, owner, random_name(), 1, 0, 0, False, False, [pos])
        City.cities.append(self)

    def init_domain(self):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if World.object.is_in(self.pos + Vector2d(dx, dy)):
                    if World.object.get(self.pos + Vector2d(dx, dy)).owner == -1:
                        self.domain.append(self.pos + Vector2d(dx, dy))
                        World.object.get(self.pos + Vector2d(dx, dy)).owner = self.owner

    def grow_population(self, count):
        self.population += count
        # something about upgrading city... TODO

    def create_unit(self, utype: UnitType):
        if self.fullness < self.level + 1:
            for unit in Unit.units:
                if unit.pos == self.pos:
                    return False
            unit = Unit(utype, self.owner, self.pos)
            self.fullness += 1
            return True
        return False

    def harvest(self, pos: Vector2d):
        World.object.get(pos).resources = False
        self.grow_population(1)
        return True
    
    def build(self, pos: Vector2d, btype: BuildingType):
        World.object.get(pos).building = btype
        World.object.get(pos).resources = False
        self.grow_population(btype.population)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, -1):
                if dx == dy == 0: continue
                if World.object.is_in(pos + Vector2d(dx, dy)):
                    if not (btype.adjacent_bonus is None):
                        if World.object.get(pos + Vector2d(dx, dy)).building == btype.adjacent_bonus:
                            self.grow_population(1)
                    if not (World.object.get(pos + Vector2d(dx, dy)).building is None):
                        if World.object.get(pos + Vector2d(dx, dy)).building.adjacent_bonus == btype:
                            self.grow_population(1)
        return True

    def destroy(self, pos: Vector2d):
        self.population -= World.object.get(pos).building.population
        for dx in (-1, 0, 1):
            for dy in (-1, 0, -1):
                if dx == dy == 0: continue
                if World.object.is_in(pos + Vector2d(dx, dy)):
                    if not (World.object.get(pos).building.adjacent_bonus is None):
                        if World.object.get(pos + Vector2d(dx, dy)).building == World.object.get(pos).building.adjacent_bonus:
                            self.population -= 1
                    if not (World.object.get(pos + Vector2d(dx, dy)).building is None):
                        if World.object.get(pos + Vector2d(dx, dy)).building.adjacent_bonus == World.object.get(pos).building:
                            self.population -= 1
        World.object.get(pos).building = None
        return True