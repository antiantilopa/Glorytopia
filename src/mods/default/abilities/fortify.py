from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile
from shared.effect import Effect

class Fortify(Ability):
    name = "fortify"
    
    @staticmethod
    def defense_bonus(unit, attacker):
        res = 1
        city = World.object.get_city(unit.pos)
        if city is not None:
            if city.walls == True:
                res = 4
            else:
                res = 1.5
        return res
