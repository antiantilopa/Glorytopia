from netio.serialization.serializer import Serializable
from shared.player import SharedPlayerData
from shared.asset_types import Nation, UnitType, BuildingType, BuildingType, TechNode, TerraForm
from shared.error_codes import ErrorCode
from shared.util.position import Pos, PosRange
from . import unit
from . import city
from . import world

class Player:
    units: list["unit.Unit"]
    cities: list["city.City"]
    vision: list[list[bool]]
    money: int
    techs: list[TechNode]
    pdata: SharedPlayerData
    is_dead: bool
    id: int

    ID = 0
    players: list["Player"] = []

    def __init__(self, new_player: bool = True, nation: Nation = None):
        if not new_player:
            return
        self.pdata = None
        self.money = 8
        self.techs = [TechNode.get("base")]
        self.vision = [[0 for i in range(world.World.object.size.x)] for _ in range(world.World.object.size.y)]
        self._vision_changes = []
        self.is_dead = False
        self.id = Player.ID
        Player.ID += 1
        self.set_nation(nation)
        self.units = []  
        self.cities = []
        Player.players.append(self)
    
    def set_pdata(self, pdata: SharedPlayerData):
        self.pdata = pdata
        pdata.id = self.id
        self.set_nation(pdata.nation)

    def set_nation(self, nation: Nation):
        self.nation = nation
        if nation is None:
            return
        self.techs.append(TechNode.get(nation.base_tech.name))

    def destroy(self):
        Player.players.remove(self)
        self.units = []
        self.cities = []

    def harvest(self, pos: Pos):
        if world.World.object.is_in(pos) == False:
            return ErrorCode.ERR_NOT_IN_WORLD
        if world.World.object.get(pos).resource is None:
            return ErrorCode.ERR_TILE_HAS_NO_RESOURCE
        if self.money < 2:
            return ErrorCode.ERR_NOT_ENOUGH_MONEY
        if world.World.object.get(pos).owner != self.id:
            return ErrorCode.ERR_NOT_IN_DOMAIN
        for tech in self.techs:
            if world.World.object.get(pos).resource in tech.harvestables:
                for city in self.cities:
                    if pos in city.domain:
                        city.harvest(pos)
                        self.money -= 2
                        return ErrorCode.SUCCESS
                return ErrorCode.ERR_NOT_IN_DOMAIN
        return ErrorCode.ERR_THERE_IS_NO_SUITABLE_TECH
    
    def build(self, pos: Pos, btype: BuildingType):
        if world.World.object.is_in(pos) == False:
            return ErrorCode.ERR_NOT_IN_WORLD
        if btype.required_resource is not None and world.World.object.get(pos).resource != btype.required_resource:
            return ErrorCode.ERR_NOT_SUITABLE_RESOURCE
        if self.money < btype.cost:
            return ErrorCode.ERR_NOT_ENOUGH_MONEY
        if not (world.World.object.get(pos).type in btype.ttypes):
            return ErrorCode.ERR_NOT_SUITABLE_TILE_TYPE
        if world.World.object.get(pos).owner != self.id:
            return ErrorCode.ERR_NOT_IN_DOMAIN
        if btype.adjacent_bonus != None:
            found = 0
            for d in PosRange(Pos(-1, -1), Pos(2, 2)):
                if d == Pos(0, 0): continue
                if not world.World.object.is_in(pos + d): continue
                if world.World.object.get(pos + d).owner != self.id: continue
                if not (btype.adjacent_bonus is None):
                    if world.World.object.get(pos + d).building == btype.adjacent_bonus:
                        found = 1
                        break
                if not (world.World.object.get(pos + d).building is None):
                    if world.World.object.get(pos + d).building.adjacent_bonus == btype:
                        found = 1
                        break
            if found == 0:
                return ErrorCode.ERR_BUILDING_HAS_NOT_ADJACENT_BONUS_GIVING_BUILDING
        for tech in self.techs:
            if btype in tech.buildings:
                for city in self.cities:
                    if pos in city.domain:
                        city.build(pos, btype)
                        self.money -= btype.cost
                        return ErrorCode.SUCCESS
                return ErrorCode.ERR_NOT_IN_DOMAIN
        return ErrorCode.ERR_THERE_IS_NO_SUITABLE_TECH

    def terraform(self, pos: Pos, terraform: TerraForm):
        if world.World.object.is_in(pos) == False:
            return ErrorCode.ERR_NOT_IN_WORLD
        if self.money < terraform.cost:
            return ErrorCode.ERR_NOT_ENOUGH_MONEY
        if world.World.object.get(pos).type != terraform.from_ttype:
            return ErrorCode.ERR_NOT_SUITABLE_TILE_TYPE
        if world.World.object.get(pos).owner != self.id:
            return ErrorCode.ERR_NOT_IN_DOMAIN
        if world.World.object.get(pos).building is not None:
            return ErrorCode.ERR_TILE_HAS_BUILDING
        if (terraform.from_resource is not None) and (world.World.object.get(pos).resource != terraform.from_resource):
            return ErrorCode.ERR_NOT_SUITABLE_RESOURCE
        for tech in self.techs:
            if terraform in tech.terraforms:
                world.World.object.get(pos).terraform(terraform)
                self.money -= terraform.cost
                return ErrorCode.SUCCESS
        return ErrorCode.ERR_THERE_IS_NO_SUITABLE_TECH

    def create_unit(self, pos: Pos, utype: UnitType):
        if world.World.object.is_in(pos) == False:
            return ErrorCode.ERR_NOT_IN_WORLD
        if world.World.object.get_unit(pos) is not None:
            return ErrorCode.ERR_NOT_EMPTY_TILE
        city = world.World.object.get_city(pos)
        if city is None or city.owner != self.id:
            return ErrorCode.ERR_NOT_YOUR_CITY
        if self.money < utype.cost:
            return ErrorCode.ERR_NOT_ENOUGH_MONEY
        for tech in self.techs:
            if utype in tech.units:
                unit = city.create_unit(utype)
                if unit is not None:
                    self.units.append(unit)
                    self.money -= utype.cost
                    return ErrorCode.SUCCESS
                return ErrorCode.ERR_CITY_IS_FULL
        return ErrorCode.ERR_THERE_IS_NO_SUITABLE_TECH

    def move_unit(self, unit: "unit.Unit", pos: Pos):
        if unit.owner != self.id:
            return ErrorCode.ERR_NOT_YOUR_UNIT
        if pos in unit.get_possible_moves():
            unit.move_and_attack(pos)
            return ErrorCode.SUCCESS
        return ErrorCode.ERR_DEFAULT

    def buy_tech(self, tech: TechNode):
        if tech in self.techs:
            return ErrorCode.ERR_TECH_IS_ALREADY_RESEARCHED
        if tech.parent is not None and tech.parent not in self.techs:
            return ErrorCode.ERR_THERE_IS_NO_SUITABLE_TECH
        if tech.cost + len(self.cities) * tech.tier > self.money:
            return ErrorCode.ERR_NOT_ENOUGH_MONEY
        self.techs.append(tech)
        self.money -= tech.cost + len(self.cities) * tech.tier
        return ErrorCode.SUCCESS

    def conquer_city(self, pos: Pos):
        unit = world.World.object.get_unit(pos)
        city = world.World.object.get_city(pos)
        if unit is None:
            return ErrorCode.ERR_NOT_YOUR_UNIT
        if city is None:
            return ErrorCode.ERR_NOT_A_CITY
        if unit.attacked or unit.moved:
            return ErrorCode.ERR_UNIT_HAS_ALREADY_MOVED_OR_ATTACKED
        if city.owner == unit.owner:
            return ErrorCode.ERR_DEFAULT
        if city.owner >= 0:
            Player.players[city.owner].cities.remove(city)
        else:
            city.init_domain()
        city.owner = self.id
        for pos in city.domain:
            world.World.object.get(pos).owner = city.owner
        self.cities.append(city)
        if unit.attached_city is not None and unit.attached_city.owner == self.id:
            unit.attached_city.fullness -= 1
        unit.attached_city = city
        city.fullness = 1
        unit.attacked = True
        unit.moved = True
        return ErrorCode.SUCCESS
    
    def act(self, unit: "unit.Unit", action_id: int):
        if unit.owner != self.id:
            return ErrorCode.ERR_NOT_YOUR_UNIT
        unit.act(action_id)
        return ErrorCode.SUCCESS

    def update_vision(self):
        self.vision = [[0 for _ in range(world.World.object.size.x)] for _ in range(world.World.object.size.y)]
        for city in self.cities:
            for pos in city.domain:
                self.vision[pos.inty()][pos.intx()] = 1
            if city.is_capital:
                vision_range = 2
                for dv in [Pos(i, j) for i in range(-vision_range, vision_range + 1) for j in range(-vision_range, vision_range + 1)]:
                    if world.World.object.is_in(city.pos + dv):
                        self.vision[(city.pos + dv).inty()][(city.pos + dv).intx()] = 1
        for unit in self.units:
            vision_range = unit.get_vision_range()
            for dv in [Pos(i, j) for i in range(-vision_range, vision_range + 1) for j in range(-vision_range, vision_range + 1)]:
                if world.World.object.is_in(unit.pos + dv):
                    self.vision[(unit.pos + dv).inty()][(unit.pos + dv).intx()] = 1
    
    def start_turn(self):
        for unit in self.units:
            unit.refresh()
        for city in self.cities:
            self.money += city.level + city.forge + city.is_capital
        return ErrorCode.SUCCESS
    
    def end_turn(self):
        for unit in self.units:
            if not unit.moved and not unit.attacked:
                unit.heal() 
            unit.end_turn()
        return ErrorCode.SUCCESS
    
    def calc_is_dead(self):
        self.is_dead = False
        if len(self.units) + len(self.cities) == 0:
            self.is_dead = True
        return self.is_dead

    @staticmethod
    def by_id(id: int) -> "Player":
        for player in Player.players:
            if player.id == id:
                return player
        return None