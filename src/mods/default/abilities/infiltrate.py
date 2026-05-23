from shared.util.position import Pos
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
        queue: list[Pos] = []
        if World.object.get_unit(city.pos) is None:
            queue.append(city.pos)
        
        for pos in city.domain:
            if pos == city.pos:
                continue
            if World.object.get(pos).type.is_water:
                continue
            if World.object.get_unit(pos) is None:
                queue.append(pos)
        for i in range(3):
            if len(queue) <= i:
                return
            if World.object.get_unit(queue[i]) is not None:
                continue
            new_unit = Unit(UnitType.get("dagger"), unit.owner, queue[i], None)
            World.object.unit_mask[new_unit.pos.y][new_unit.pos.x] = new_unit
            Player.players[unit.owner].units.append(new_unit)

    @staticmethod
    def after_movement(unit):
        city = World.object.get_city(unit.pos)
        if city is None:
            return
        if city.owner == -1:
            return
        if city.owner != unit.owner:
            unit.health = 0
            World.object.unit_mask[unit.pos.y][unit.pos.x] = None
            Infiltrate.infiltrate(unit, city)
    
    @staticmethod
    def after_attack(unit, other):
        city = World.object.get_city(other.pos)
        if city is None:
            unit.attacked = False
            return
        if city.owner == -1:
            return
        if city.owner != unit.owner:
            unit.health = 0
            Infiltrate.infiltrate(unit, city)
            
    @staticmethod
    def save_moved(unit):
        return 1
    
    @staticmethod
    def retaliation_mitigate(unit, defense_result):
        return 0