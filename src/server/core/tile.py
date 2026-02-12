from shared.player import PlayerData_
from shared.tile import TileData
from shared.asset_types import TileType, BuildingType, ResourceType, TerraForm
from shared.util.position import Pos

from . import world as World
from . import player as Player

class Tile(TileData):
    
    def __init__(self, pos: Pos, tile_type: TileType, resources: ResourceType):
        TileData.__init__(self, pos, tile_type, resources)

    def build_building(self, building: BuildingType):
        self.building = building
        for m in self.modificators:
            m.tmtype.on_building(m, building, self.owner, self)
        # WTF is that thing?! i can make it manualy!!!
        """
        ehal building cherez building
        vidit building v reke building
        sunul building v reku building
        building building building building. 
        """
        # YOU WAS NOT FUTILE AFTER ALL
    
    def harvest(self):
        for m in self.modificators:
            m.tmtype.on_harvest(m, self.owner, self)
        self.resource = None

    def terraform(self, terraform: TerraForm):
        if terraform is None:
            return
        for m in self.modificators:
            m.tmtype.on_terraform(m, terraform, self.owner, self)
        self.type = terraform.to_ttype
        self.resource = terraform.to_resource

    def validate(self, player_data: PlayerData_):
        if not player_data.joined:
            return
        player = Player.Player.by_id(player_data.id)
        return player.vision[self.pos.y][self.pos.x]
    
    def change_owner(self, new_owner: int):
        old_owner = self.owner
        for m in self.modificators:
            m.tmtype.on_owner_change(m, old_owner, new_owner, self)
        self.owner = new_owner