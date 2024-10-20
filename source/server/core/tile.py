from random_map import pangea
from shared.tile import TileData
from shared.tile_types import TileType, TileTypes

class Tile(TileData):
    
    def __init__(self):
        super().__init__()

    def buildBuilding(self, building):
        self.building = building
        
class BuildingTypes:
    id: int
    name: str
    terrain: TileType
    cost: int