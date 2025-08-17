from .updating_object import UpdatingObject
from .world import World
from .game_event import GameEvent
from . import unit as Unit
from . import city as City
from shared.asset_types import UnitType, BuildingType, BuildingType, TechNode, TerraForm
from shared.error_codes import ErrorCodes
from engine_antiantilopa import Vector2d, VectorRange
from serializator.net import flags_to_int, int_to_flags


SerializedPlayer = tuple[int, int, list[int], list[int], bool]

class Player(UpdatingObject):
    
    id: int
    money: int
    vision: list[list[int]]
    techs: list[TechNode]
    units: list["Unit.Unit"]
    cities: list["City.City"]
    is_dead: bool

    ID = 0
    players: list["Player"] = []

    def __init__(self, new_player: bool = True):
        UpdatingObject.__init__(self)
        self.black_list.extend(("units", "cities", "is_dead"))
        if not new_player:
            return
        self.id = Player.ID
        Player.ID += 1
        self.money = 8
        self.vision = [[0 for i in range(World.object.size.x)] for _ in range(World.object.size.y)]
        self.techs = [TechNode.get("base")]
        self.units = []  
        self.cities = []
        self.is_dead = False
        Player.players.append(self)
    
    def destroy(self):
        Player.players.remove(self)
        self.units = []
        self.cities = []
        UpdatingObject.destroy(self)

    @GameEvent.game_event
    def harvest(self, pos: Vector2d):
        if World.object.is_in(pos) == False:
            return ErrorCodes.ERR_NOT_IN_WORLD
        if World.object.get(pos).resource is None:
            return ErrorCodes.ERR_TILE_HAS_NO_RESOURCE
        if self.money < 2:
            return ErrorCodes.ERR_NOT_ENOUGH_MONEY
        if World.object.get(pos).owner != self.id:
            return ErrorCodes.ERR_NOT_IN_DOMAIN
        for tech in self.techs:
            if World.object.get(pos).resource in tech.harvestables:
                for city in self.cities:
                    if pos in city.domain:
                        city.harvest(pos)
                        self.money -= 2
                        return ErrorCodes.SUCCESS
                return ErrorCodes.ERR_NOT_IN_DOMAIN
        return ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH
    
    @GameEvent.game_event
    def build(self, pos: Vector2d, btype: BuildingType):
        if World.object.is_in(pos) == False:
            return ErrorCodes.ERR_NOT_IN_WORLD
        if btype.required_resource is not None and World.object.get(pos).resource != btype.required_resource:
            return ErrorCodes.ERR_NOT_SUITABLE_RESOURCE
        if self.money < btype.cost:
            return ErrorCodes.ERR_NOT_ENOUGH_MONEY
        if not (World.object.get(pos).ttype in btype.ttypes):
            return ErrorCodes.ERR_NOT_SUITABLE_TILE_TYPE
        if World.object.get(pos).owner != self.id:
            return ErrorCodes.ERR_NOT_IN_DOMAIN
        if btype.adjacent_bonus != None:
            found = 0
            for d in VectorRange(Vector2d(-1, -1), Vector2d(2, 2)):
                if d == Vector2d(0, 0): continue
                if not World.object.is_in(pos + d): continue
                if World.object.get(pos + d).owner != self.id: continue
                if not (btype.adjacent_bonus is None):
                    if World.object.get(pos + d).building == btype.adjacent_bonus:
                        found = 1
                        break
                if not (World.object.get(pos + d).building is None):
                    if World.object.get(pos + d).building.adjacent_bonus == btype:
                        found = 1
                        break
            if found == 0:
                return ErrorCodes.ERR_BUILDING_HAS_NOT_ADJACENT_BONUS_GIVING_BUILDING
        for tech in self.techs:
            if btype in tech.buildings:
                for city in self.cities:
                    if pos in city.domain:
                        city.build(pos, btype)
                        self.money -= btype.cost
                        return ErrorCodes.SUCCESS
                return ErrorCodes.ERR_NOT_IN_DOMAIN
        return ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH

    @GameEvent.game_event
    def terraform(self, pos: Vector2d, terraform: TerraForm):
        if World.object.is_in(pos) == False:
            return ErrorCodes.ERR_NOT_IN_WORLD
        if self.money < terraform.cost:
            return ErrorCodes.ERR_NOT_ENOUGH_MONEY
        if World.object.get(pos).ttype != terraform.from_ttype:
            return ErrorCodes.ERR_NOT_SUITABLE_TILE_TYPE
        if World.object.get(pos).owner != self.id:
            return ErrorCodes.ERR_NOT_IN_DOMAIN
        if World.object.get(pos).building is not None:
            return ErrorCodes.ERR_TILE_HAS_BUILDING
        if (terraform.from_resource is not None) and (World.object.get(pos).resource != terraform.from_resource):
            return ErrorCodes.ERR_NOT_SUITABLE_RESOURCE
        for tech in self.techs:
            if terraform in tech.terraforms:
                World.object.get(pos).terraform(terraform)
                self.money -= terraform.cost
                return ErrorCodes.SUCCESS
        return ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH

    @GameEvent.game_event
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

    @GameEvent.game_event
    def move_unit(self, unit: "Unit.Unit", pos: Vector2d):
        if unit.owner != self.id:
            return ErrorCodes.ERR_NOT_YOUR_UNIT
        if pos in unit.get_possible_moves():
            unit.move(pos)
            return ErrorCodes.SUCCESS
        return ErrorCodes.ERR_DEFAULT

    @GameEvent.game_event
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

    @GameEvent.game_event
    def conquer_city(self, pos: Vector2d):
        for unit in self.units:
            if unit.pos == pos:
                if unit.attacked or unit.moved:
                    return ErrorCodes.ERR_UNIT_HAS_ALREADY_MOVED_OR_ATTACKED
                for city in City.City.cities:
                    if city.pos == pos:
                        if city.owner == unit.owner:
                            return ErrorCodes.ERR_DEFAULT
                        if city.owner >= 0:
                            Player.players[city.owner].cities.remove(city)
                        else:
                            city.init_domain()
                        city.owner = self.id
                        for pos in city.domain:
                            World.object.get(pos).owner = city.owner
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
    
    @GameEvent.game_event
    def start_turn(self):
        for unit in self.units:
            unit.refresh()
        for city in self.cities:
            self.money += city.level + city.forge + city.is_capital
        return ErrorCodes.SUCCESS
    
    @GameEvent.game_event
    def end_turn(self):
        for unit in self.units:
            if not unit.moved and not unit.attacked:
                unit.heal() 
        return ErrorCodes.SUCCESS

    def to_serializable(self):
        return [
            self.id,
            self.money,
            [flags_to_int(*row) for row in self.vision],
            [tech.id for tech in self.techs], # super bad with mods. who cares now? TODO. maybe names?
            self.is_dead
        ]
    
    def set_from_data(self, data: SerializedPlayer):
        self.id = data[0]
        self.money = data[1]
        self.vision = [list(int_to_flags(row, World.object.size.x)) for row in data[2]]
        self.techs = [TechNode.by_id(tech_id) for tech_id in data[3]]
        self.is_dead = data[4]

    @staticmethod
    def from_serializable(serializable: SerializedPlayer) -> "Player":
        player = Player()
        player.set_from_data(serializable)
        for unit in Unit.Unit.units:
            if unit.owner == player.id:
                player.units.append(unit)
        for city in City.City.cities:
            if city.owner == player.id:
                player.cities.append(city)
        return player

    @staticmethod
    def do_serializable(data: SerializedPlayer):
        player_id = data[0]
        found = False
        for player in Player.players:
            if player.id == player_id:
                found = True
                player.set_from_data(data)
                break
        if not found:
            raise Exception("Invalid Player data.")
        