from .world import World
from shared.tree import TechNode, Techs
from . import unit as Unit
from . import city as City
from shared.unit_types import UnitType
from shared.tile_types import TileType, BuildingType, BuildingTypes
from shared.error_codes import ErrorCodes
from engine_antiantilopa import Vector2d


class Player:
    
    id: int
    money: int
    vision: list[list[int]]
    techs: list[TechNode]
    units: list["Unit.Unit"]
    cities: list["City.City"]

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
            return ErrorCodes.ERR_NOT_IN_WORLD
        if World.object.get(pos).resource is None:
            return ErrorCodes.ERR_TILE_HAS_NO_RESOURCE
        if self.money < 2:
            return ErrorCodes.ERR_NOT_ENOUGH_MONEY
        for tech in self.techs:
            if World.object.get(pos).resource in tech.harvestables:
                for city in self.cities:
                    if pos in city.domain:
                        city.harvest(pos)
                        self.money -= 2
                        return ErrorCodes.SUCCESS
                return ErrorCodes.ERR_NOT_IN_DOMAIN
        return ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH
    
    def build(self, pos: Vector2d, btype: BuildingType):
        if World.object.is_in(pos) == False:
            return ErrorCodes.ERR_NOT_IN_WORLD
        if btype.required_resource is not None and World.object.get(pos).resource != btype.required_resource:
            return ErrorCodes.ERR_NOT_SUITABLE_RESOURCE
        if self.money < btype.cost:
            return ErrorCodes.ERR_NOT_ENOUGH_MONEY
        if not (World.object.get(pos).ttype in btype.ttypes):
            return ErrorCodes.ERR_NOT_SUITABLE_TILE_TYPE
        for tech in self.techs:
            if btype in tech.buildings:
                for city in self.cities:
                    if pos in city.domain:
                        city.build(pos, btype)
                        self.money -= btype.cost
                        return ErrorCodes.SUCCESS
                return ErrorCodes.ERR_NOT_IN_DOMAIN
        return ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH
    
    def destroy(self, pos: Vector2d):
        if World.object.is_in(pos) == False:
            return ErrorCodes.ERR_NOT_IN_WORLD
        if World.object.get(pos).building is None:
            return ErrorCodes.ERR_NOT_SUITABLE_BUILDING
        if self.money < BuildingTypes.destroy.cost:
            return ErrorCodes.ERR_NOT_ENOUGH_MONEY
        for tech in self.techs:
            if BuildingTypes.destroy in tech.buildings:
                for city in self.cities:
                    if pos in city.domain:
                        city.destroy(pos)
                        self.money -= BuildingTypes.destroy.cost
                        return ErrorCodes.SUCCESS
                return ErrorCodes.ERR_NOT_IN_DOMAIN
        return ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH

    def create_unit(self, pos: Vector2d, utype: UnitType):
        if World.object.is_in(pos) == False:
            return ErrorCodes.ERR_NOT_IN_WORLD
        if World.object.unit_mask[pos.inty()][pos.intx()] != 0:
            return ErrorCodes.ERR_NOT_EMPTY_TILE
        if self.money < utype.cost:
            return ErrorCodes.ERR_NOT_ENOUGH_MONEY
        for tech in self.techs:
            if utype in tech.units:
                for city in self.cities:
                    if pos == city.pos:
                        unit = city.create_unit(utype)
                        if unit is not None:
                            self.units.append(unit)
                            self.money -= utype.cost
                            return ErrorCodes.SUCCESS
                        return ErrorCodes.ERR_CITY_IS_FULL
                return ErrorCodes.ERR_NOT_YOUR_CITY
        return ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH

    def move_unit(self, unit: "Unit.Unit", pos: Vector2d):
        if pos in unit.get_possible_moves():
            unit.move(pos)
            return ErrorCodes.SUCCESS
        return ErrorCodes.ERR_DEFAULT

    def buy_tech(self, tech: TechNode):
        if tech in self.techs:
            return ErrorCodes.ERR_TECH_IS_ALREADY_RESEARCHED
        if tech.parent is not None and tech.parent not in self.techs:
            return ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH
        if tech.cost + len(self.cities) * tech.tier > self.money:
            return ErrorCodes.ERR_NOT_ENOUGH_MONEY
        self.techs.append(tech)
        self.money -= tech.cost + len(self.cities) * tech.tier
        return ErrorCodes.SUCCESS

    def conquer_city(self, pos: Vector2d):
        for unit in self.units:
            if unit.pos == pos:
                if unit.attacked or unit.moved:
                    return ErrorCodes.ERR_UNIT_HAS_ALREADY_MOVED_OR_ATTACKED
                for city in City.City.cities:
                    if city.pos == pos:
                        if city.owner >= 0:
                            Player.players[city.owner].cities.remove(city)
                        city.owner = self.id
                        self.cities.append(city)
                        if unit.attached_city is not None and unit.attached_city.owner == self.id:
                            unit.attached_city.fullness -= 1
                        unit.attached_city = city
                        city.fullness = 1
                        unit.attacked = True
                        unit.moved = True
                        return ErrorCodes.SUCCESS
                return ErrorCodes.ERR_NOT_A_CITY
        return ErrorCodes.ERR_NOT_YOUR_UNIT

    def update_vision(self) -> list[Vector2d]:
        changed = []
        for city in self.cities:
            for pos in city.domain:
                if self.vision[pos.inty()][pos.intx()] == 0:
                    changed.append(pos)
                self.vision[pos.inty()][pos.intx()] = 1
            if city.is_capital:
                vision_range = 2
                for dv in [Vector2d(i, j) for i in range(-vision_range, vision_range + 1) for j in range(-vision_range, vision_range + 1)]:
                    if World.object.is_in(city.pos + dv):
                        if self.vision[(city.pos + dv).inty()][(city.pos + dv).intx()] == 0:
                            changed.append(city.pos + dv)
                        self.vision[(city.pos + dv).inty()][(city.pos + dv).intx()] = 1
        for unit in self.units:
            vision_range = unit.get_vision_range()
            for dv in [Vector2d(i, j) for i in range(-vision_range, vision_range + 1) for j in range(-vision_range, vision_range + 1)]:
                if World.object.is_in(unit.pos + dv):
                    if self.vision[(unit.pos + dv).inty()][(unit.pos + dv).intx()] == 0:
                        changed.append(unit.pos + dv)
                    self.vision[(unit.pos + dv).inty()][(unit.pos + dv).intx()] = 1
        return changed
    
    def start_turn(self):
        for unit in self.units:
            unit.refresh()
        for city in self.cities:
            self.money += city.level + city.forge + city.is_capital
    
    def end_turn(self):
        for unit in self.units:
            if not unit.moved and not unit.attacked:
                unit.heal() 