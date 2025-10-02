from shared.player import PlayerData_
from shared.tile import TileData
from shared.asset_types import TileType, BuildingType, ResourceType, TerraForm
from engine_antiantilopa import Vector2d

from . import world as World
from . import player as Player

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
        
    def validate(self, player_data: PlayerData_):
        player = Player.Player.by_id(player_data.id)
        return player.vision[self.pos.y][self.pos.x]