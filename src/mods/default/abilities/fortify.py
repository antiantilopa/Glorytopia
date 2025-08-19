from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile
from shared.effect import Effect

class Fortify(Ability):
    name = "fortify"
    
    @staticmethod
    def defense_bonus(unit):
        res = 1
        if World.object.cities_mask[unit.pos.y][unit.pos.x]:
            res = 1.5
            for city in City.cities:
                if city.pos == unit.pos:
                    if city.walls == True:
                        res = 4
                        break
                    else:
                        break
        return res
