from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile
from shared.asset_types import TileType

class HighGround(Ability):
    name = "high_ground"
    
    @staticmethod
    def additional_defense(unit: Unit, other: Unit) -> int:
        if World.object.get(unit.pos).type == TileType.get("mountain"):
            return 1
        return 0

    @staticmethod
    def additional_attack(unit: Unit, other: Unit) -> int:
        if World.object.get(other.pos).type == TileType.get("mountain"):
            return 1
        elif World.object.get(unit.pos).type == TileType.get("mountain"):
            return 1
        return 0

    @staticmethod
    def on_terrain_movement(unit, tile, movement):
        if tile.type == TileType.get("mountain"):
            return movement - 1
        return 0