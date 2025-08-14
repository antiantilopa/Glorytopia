from server.core.ability import Ability
from server.core.player import Player
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile
from shared.asset_types import UnitType

class Infiltrate(Ability):
    name = "infiltrate"

    def infiltrate(unit: Unit, city: City):
        queue = []
        if World.object.unit_mask[city.pos.y][city.pos.x] == 0:
            queue.append(city.pos)
        
        for pos in city.domain:
            if pos == city.pos:
                continue
            if World.object.unit_mask[pos.y][pos.x] == 0:
                queue.append(pos)
        for i in range(3):
            if len(queue) <= i:
                return
            if World.object.unit_mask[queue[i].y][queue[i].x] == 1:
                continue
            new_unit = Unit(UnitType.get("dagger"), unit.owner, queue[i], None)
            World.object.unit_mask[new_unit.pos.y][new_unit.pos.x] = 1
            Player.players[unit.owner].units.append(new_unit)

    @staticmethod
    def after_movement(unit):
        if World.object.cities_mask[unit.pos.y][unit.pos.x]:
            for city in City.cities:
                if city.pos == unit.pos:
                    if city.owner != unit.owner:
                        unit.health = 0
                        World.object.unit_mask[unit.pos.y][unit.pos.x] = 0
                        Infiltrate.infiltrate(unit, city)
                        break
                    else:
                        break
    
    @staticmethod
    def after_attack(unit, other):
        if World.object.cities_mask[other.pos.y][other.pos.x]:
            for city in City.cities:
                if city.pos == unit.pos:
                    if city.owner != unit.owner:
                        unit.health = 0
                        Infiltrate.infiltrate(unit, city)
                        break
                    else:
                        break
