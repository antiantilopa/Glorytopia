from .world import World
from shared.tree import TechNode, Techs
from .unit import Unit
from .city import City
from shared.unit_types import UnitType
from shared.tile_types import TileType, BuildingType, BuildingTypes
from pygame_tools_tafh import Vector2d


class Player:
    
    id: int
    money: int
    vision: list[list[int]]
    techs: list[TechNode]
    units: list[Unit]
    cities: list[City]

    ID = 0
    players: list["Player"] = []

    def __init__(self):
        self.id = Player.ID
        Player.ID += 1
        self.money = 5
        self.vision = [[0 for i in range(World.object.size.x)] for _ in range(World.object.size.y)]
        self.techs = [Techs.base]
        self.units = []
        self.cities = []
        Player.players.append(self)
    
    def harvest(self, pos: Vector2d):
        if World.object.is_in(pos) == False:
            return 1
        if World.object.get(pos).resource is None:
            return 2
        if self.money < 2:
            return 3
        for tech in self.techs:
            if World.object.get(pos).resource in tech.harvestables:
                for city in self.cities:
                    if pos in city.domain:
                        city.harvest(pos)
                        self.money -= 2
                        return 0
                return 4
        return 5
    
    def build(self, pos: Vector2d, btype: BuildingType):
        if World.object.is_in(pos) == False:
            return 1
        if btype.required_resource is not None and World.object.get(pos).resource != btype.required_resource:
            return 2
        if self.money < btype.cost:
            return 3
        if not (World.object.get(pos).ttype in btype.ttypes):
            return 6
        for tech in self.techs:
            if btype in tech.buildings:
                for city in self.cities:
                    if pos in city.domain:
                        city.build(pos, btype)
                        self.money -= btype.cost
                        return 0
                return 4
        return 5
    
    def destroy(self, pos: Vector2d):
        if World.object.is_in(pos) == False:
            return False
        if World.object.get(pos).building is None:
            return False
        if self.money < BuildingTypes.destroy.cost:
            return False
        for tech in self.techs:
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
            return 1
        if self.money < utype.cost:
            return 3
        for tech in self.techs:
            if utype in tech.units:
                for city in self.cities:
                    if pos == city.pos:
                        unit = city.create_unit(utype)
                        if unit is not None:
                            self.units.append(unit)
                            self.money -= utype.cost
                            return 0
                        return 7
                return 4
        return 5

    def move_unit(self, unit: Unit, pos: Vector2d):
        if pos in unit.get_possible_moves():
            unit.move(pos)
            return True
        return False

    def buy_tech(self, tech: TechNode):
        if tech.cost + len(self.cities) * tech.tier > self.money:
            return 3
        if tech.parent is not None and tech.parent not in self.techs:
            return 8
        if tech in self.techs:
            return 9
        self.techs.append(tech)
        self.money -= tech.cost + len(self.cities) * tech.tier
        return 0

    def conquer_city(self, pos: Vector2d):
        for unit in self.units:
            if unit.pos == pos:
                if unit.attacked or unit.moved:
                    return 10
                for city in City.cities:
                    if city.pos == pos:
                        if city.owner >= 0:
                            Player.players[city.owner].cities.remove(city)
                        city.owner = Player.id
                        self.cities.append(city)
                        return 0
                return 4
        return 11

    def update_vision(self):
        for city in self.cities:
            for dv in [Vector2d(i, j) for i in range(-2, 3) for j in range(-2, 3)]:
                if World.object.is_in(city.pos + dv):
                    self.vision[(city.pos + dv).inty()][(city.pos + dv).intx()] = 1
        for unit in self.units:
            for dv in [Vector2d(i, j) for i in range(-1, 2) for j in range(-1, 2)]:
                if World.object.is_in(unit.pos + dv):
                    self.vision[(unit.pos + dv).inty()][(unit.pos + dv).intx()] = 1
        
    def start_turn(self):
        for unit in self.units:
            unit.refresh()
        for city in self.cities:
            self.money += city.level + city.forge
    
    def end_turn(self):
        for unit in self.units:
            if not unit.moved and not unit.attacked:
                unit.heal() 