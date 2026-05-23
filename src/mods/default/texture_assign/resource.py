from typing import Callable

from client.globals.window_size import WindowSize
from client.texture_assign.texture_assign import TextureAssignSystem
from client.widgets.fastgameobjectcreator import *
from client.network.client import GamePlayer
from shared.asset_types import ResourceType
from shared.tile import TileData
from engine_antiantilopa import GameObject
from shared.util.position import Pos, PosRange

ARGUMENT_TYPE = tuple[Callable[[Pos], TileData], Pos]

@TextureAssignSystem.register_assign_default(ResourceType)
def assign_resource_texture(tile: TileData, tile_obj: GameObject, flags: set[str] = set(), args: ARGUMENT_TYPE = (lambda _:None, Pos(0, 0))):
    resource = create_game_object(
        parent=tile_obj, 
        tags="texture:tile:resource", 
        at=InGrid((1, 1), (0, 0)), 
        layer = 2
    )
    resource.add_component(SpriteComponent(nickname=f"resources:{tile.resource.name}", size=WindowSize.get_block_size()))