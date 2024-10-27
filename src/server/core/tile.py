from shared.tile import TileData
from shared.tile_types import TileType
from pygame_tools_tafh.vmath import Vector2d


class Tile(TileData):
    
    def __init__(self, pos: Vector2d, ttype: TileType, resources: bool):
        super().__init__(pos, ttype, resources)

    def build_building(self, building):
        self.building = building
        
class BuildingTypes:
    id: int
    name: str
    terrain: TileType
    cost: int