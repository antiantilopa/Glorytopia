from shared.tile import TileData
from shared.asset_types import TileType, BuildingType, ResourceType, TerraForm
from engine_antiantilopa import Vector2d
from . import world as World

class Tile(TileData):
    
    def __init__(self, pos: Vector2d, ttype: TileType, resources: ResourceType):
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
    
    def terraform(self, terraform: TerraForm):
        if terraform is None:
            return
        self.ttype = terraform.to_ttype
        self.resource = terraform.to_resource
        