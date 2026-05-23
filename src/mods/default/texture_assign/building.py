from typing import Callable

from client.globals.window_size import WindowSize
from client.texture_assign.texture_assign import TextureAssignSystem
from client.widgets.fastgameobjectcreator import *
from client.network.client import GamePlayer
from shared.asset_types import BuildingType
from shared.tile import TileData
from engine_antiantilopa import GameObject
from shared.util.position import Pos, PosRange

ARGUMENT_TYPE = tuple[Callable[[Pos], TileData], Pos]

@TextureAssignSystem.register_assign_default(BuildingType)
def assign_building_texture(tile: TileData, tile_obj: GameObject, flags: set[str] = set(), args: ARGUMENT_TYPE = (lambda _:None, Pos(0, 0))):
    building = create_game_object(
        parent=tile_obj, 
        tags="texture:tile:building", 
        at=InGrid((1, 1), (0, 0)), 
        layer = 3
    )
    get_tile, world_size = args
    if tile.building.adjacent_bonus == None:
        building.add_component(SpriteComponent(nickname=f"buildings:{tile.building.name}", size=WindowSize.get_block_size()))
    else:
        level = 0
        for d in PosRange(Pos(-1, -1), Pos(2, 2)):
            if (tile.pos + d).is_in_box(Pos(0, 0), world_size - Pos(1, 1)):
                if get_tile(tile.pos + d) is None:
                    continue
                if get_tile(tile.pos + d).owner == tile.owner:
                    if get_tile(tile.pos + d).building == tile.building.adjacent_bonus:
                        level += 1
        if level == 0:
            level = 1
        building.add_component(SpriteComponent(nickname=f"buildings:{tile.building.name}", size=WindowSize.get_block_size(), frame=level-1, frames_number=8, frame_direction=Vector2d(0, 1)))