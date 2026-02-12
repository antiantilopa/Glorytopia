from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile
from shared.asset_types import TileType

class Tunneling(Ability):
    name = "tunneling"

    @staticmethod
    def after_movement(unit):
        if World.object.get(unit.pos).type == TileType.get("mountain"):
            World.object.get(unit.pos).has_road = True
