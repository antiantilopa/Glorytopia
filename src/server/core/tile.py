from shared.tile import SerializedTile, TileData
from shared.asset_types import TileType, BuildingType, ResourceType, TerraForm
from engine_antiantilopa import Vector2d
from .updating_object import UpdatingObject
from . import world as World

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
    
    def terraform(self, terraform: TerraForm):
        if terraform is None:
            return
        self.ttype = terraform.to_ttype
        self.resource = terraform.to_resource

    def set_from_data(self, tdata: TileData):
        self.owner = tdata.owner
        self.pos = tdata.pos
        self.ttype = tdata.ttype
        self.resource = tdata.resource
        self.building = tdata.building
        self.has_road = tdata.has_road

    @staticmethod
    def from_serializable(serializable: SerializedTile):
        tdata = TileData.from_serializable(serializable)
        tile = Tile(tdata.pos, tdata.ttype, tdata.resource)
        tile.set_from_data(tdata)

    def to_serializable(self):
        return TileData.to_serializable(self)

    @staticmethod
    def do_serializable(serializable: SerializedTile):
        tdata = TileData.from_serializable(serializable)
        World.World.object.get(tdata.pos).set_from_data(tdata)