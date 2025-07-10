from shared.tile import TileData
from shared.asset_types import TileType, BuildingType, ResourceType
from engine_antiantilopa import Vector2d
from .updating_object import UpdatingObject


class Tile(TileData, UpdatingObject):
    
    def __init__(self, pos: Vector2d, ttype: TileType, resources: ResourceType):
        UpdatingObject.__init__(self)
        TileData.__init__(self, pos, ttype, resources)

    def build_building(self, building: BuildingType):
        self.building = building
        # WTF is that thing?! i can make it manualy!!!
        """
        ehal building cherez building
        vidit building v reke building
        sunul building v reku building
        building building building building. 
        """