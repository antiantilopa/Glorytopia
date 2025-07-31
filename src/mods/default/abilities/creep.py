from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Creep(Ability):
    name = "creep"

    @staticmethod
    def on_terrain_movement(unit, tile, movement):
        return movement - 1 * (1 - 0.5 * tile.has_road)
