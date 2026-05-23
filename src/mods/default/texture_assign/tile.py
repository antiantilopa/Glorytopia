from typing import Callable

from client.globals.window_size import WindowSize
from client.texture_assign.texture_assign import TextureAssignSystem
from client.widgets.fastgameobjectcreator import *
from client.network.client import GamePlayer
from shared.asset_types import BuildingType, ResourceType
from shared.tile import TileData
from engine_antiantilopa import GameObject
from shared.util.position import Pos, PosRange

ARGUMENT_TYPE = tuple[Callable[[Pos], TileData], Pos]

@TextureAssignSystem.register_assign_default(TileData)
def assign_tile_texture(tile: TileData, game_object: GameObject, flags: set[str] = set(), args: ARGUMENT_TYPE = (lambda _:None, Pos(0, 0))):
    new_tile_sprite = create_game_object(
        parent=game_object, 
        tags="texture:tile:sprite", 
        at=InGrid((1, 1), (0, 0)), 
        layer=0
    )
    new_tile_sprite.add_component(SpriteComponent(nickname=f"tiles:{tile.type.name}", size=WindowSize.get_block_size()))
    if tile.building is not None:
        TextureAssignSystem.assign_texture(tile, game_object, flags, args, as_cls=BuildingType)
    if tile.resource is not None:
        TextureAssignSystem.assign_texture(tile, game_object, flags, args, as_cls=ResourceType)
    if tile.owner != -1:
        _update_tile_border(tile, game_object, flags, args)

def _update_tile_border(tile: TileData, tile_obj: GameObject, flags, args: ARGUMENT_TYPE, update_near = True):
    i = 0
    while i < len(tile_obj.childs):
        if "texture:tile:border" in tile_obj.childs[i].tags:
            tile_obj.childs[i].destroy()
        else:
            i += 1
    get_tile, world_size = args
    for d in (Vector2d(-1, 0), Vector2d(1, 0), Vector2d(0, 1), Vector2d(0, -1)):
        if not (0 <= tile.pos.x + d.x < world_size.x and 0 <= tile.pos.y + d.y < world_size.y):
            continue
        if (get_tile(tile.pos + d) is None) or (get_tile(tile.pos + d).owner != tile.owner):
            create_line_game_object(
                parent=tile_obj, 
                tags="texture:tile:border", 
                at=d.complex_multiply(Vector2d(1, 1)) * WindowSize.get_block_size() // 2, 
                to=d.complex_multiply(Vector2d(1, -1)) * WindowSize.get_block_size() // 2, 
                color=GamePlayer.by_id(tile.owner).get_main_color(), 
                width=2 * (WindowSize.get_block_size().intx() // 15)
            )

    tile_obj.need_draw = True
    tile_obj.need_blit_set_true()
    if update_near:
        for d in (Pos(-1, 0), Pos(1, 0), Pos(0, 1), Pos(0, -1)):
            if not (0 <= tile.pos.x + d.x < world_size.x and 0 <= tile.pos.y + d.y < world_size.y):
                continue
            another_tile = get_tile(tile.pos + d)
            if another_tile == None:
                continue
            if another_tile.owner != -1:
                if hasattr(another_tile, "obj") and another_tile.obj is not None:
                    _update_tile_border(another_tile, another_tile.obj, flags, args, False)