from netio.serialization.serializer import sync_key
from shared.player import PlayerData_
from .random_names import random_funny_name as random_name
from shared.util.position import Pos
from shared.asset_types import UnitType, BuildingType
from shared.city import CityData

from .world import World
from . import unit as Unit
from . import player as Player

@sync_key("city")
class City(CityData):
    cities: list["City"] = []

    def __init__(self, pos: Pos, owner: int):
        CityData.__init__(self, pos, owner, random_name(), 1, 0, 0, False, False, False, [pos])
        City.cities.append(self)
        World.object.city_mask[self.pos.inty()][self.pos.intx()] = self

    def init_domain(self):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if World.object.is_in(self.pos + Pos(dx, dy)):
                    if World.object.get(self.pos + Pos(dx, dy)).owner == -1:
                        self.domain.append(self.pos + Pos(dx, dy))
                        World.object.get(self.pos + Pos(dx, dy)).change_owner(self.owner)

    def grow_population(self, count):
        self.population += count
        population_need = self.level + 1
        
        while self.population >= population_need:
            self.population -= population_need
            population_need = self.level + 1
            self.level_up()

    def level_up(self):
        self.level += 1
        if self.level == 2:
            self.forge = 1
        if self.level == 3:
            self.walls = 1
        if self.level == 4:
            self.grow_population(3)

    def create_unit(self, utype: UnitType):
        if self.fullness < self.level + 1:
            if World.object.get_unit(self.pos) is not None:
                return None
            unit = Unit.Unit(utype, self.owner, self.pos, self)
            World.object.unit_mask[self.pos.inty()][self.pos.intx()] = unit
            self.fullness += 1
            return unit
        return None

    def harvest(self, pos: Pos):
        World.object.get(pos).harvest()
        self.grow_population(1)
        return True

    def build(self, pos: Pos, btype: BuildingType):
        World.object.get(pos).build_building(btype)
        World.object.get(pos).resource = None
        if btype.adjacent_bonus is None:
            self.grow_population(btype.population)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == dy == 0: continue
                if World.object.is_in(pos + Pos(dx, dy)):
                    if World.object.get(pos + Pos(dx, dy)).owner != self.owner:
                        continue
                    if not (btype.adjacent_bonus is None):
                        if World.object.get(pos + Pos(dx, dy)).building == btype.adjacent_bonus:
                            self.grow_population(btype.population)
                    if not (World.object.get(pos + Pos(dx, dy)).building is None):
                        if World.object.get(pos + Pos(dx, dy)).building.adjacent_bonus == btype:
                            for city in City.cities:
                                if (pos + Pos(dx, dy)) in city.domain:
                                    city.grow_population(World.object.get(pos + Pos(dx, dy)).building.population)
                                    break
        return True

    def destroy(self):
        for pos in self.domain:
            World.object.get(pos).owner = -1
        World.object.city_mask[self.pos.inty()][self.pos.intx()] = None
        City.cities.remove(self)
        Player.Player.players[self.owner].cities.remove(self)
        del self

    def validate(self, player_data: PlayerData_):
        if not player_data.joined:
            return False
        player = Player.Player.by_id(player_data.id)
        if player.is_dead:
            return True
        return player.vision[self.pos.y][self.pos.x]