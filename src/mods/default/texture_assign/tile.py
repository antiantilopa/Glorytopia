



from client.globals.window_size import WindowSize
from client.scenes.game_screen.game_classes import GameRules, Tile
from client.texture_assign.texture_assign import TextureAssignSystem
from client.widgets.fastgameobjectcreator import *
from client.network.client import GamePlayer
from shared.tile import TileData
from engine_antiantilopa import GameObject
from shared.util.position import Pos, PosRange

@TextureAssignSystem.register_assign_default(TileData)
def assign_tile_texture(tile: TileData, game_object: GameObject, flags: set[str] = set()):
    new_tile_sprite = create_game_object(
        parent=game_object, 
        tags="texture:tile:sprite", 
        at=InGrid((1, 1), (0, 0)), 
        layer=0
    )
    new_tile_sprite.add_component(SpriteComponent(nickname=f"tiles:{tile.type.name}", size=WindowSize.get_block_size()))
    if tile.building is not None:
        _create_building_obj(tile, game_object)
    if tile.resource is not None:
        _create_resource_obj(tile, game_object)
    if tile.owner != -1:
        _update_tile_border(tile.pos, game_object)

def _create_building_obj(tile: Tile, tile_obj: GameObject):
    building = create_game_object(
        parent=tile_obj, 
        tags="texture:tile:building", 
        at=InGrid((1, 1), (0, 0)), 
        layer = 1
    )
    if tile.building.adjacent_bonus == None:
        building.add_component(SpriteComponent(nickname=f"buildings:{tile.building.name}", size=WindowSize.get_block_size()))
    else:
        level = 0
        for d in PosRange(Pos(-1, -1), Pos(2, 2)):
            if (tile.pos + d).is_in_box(Pos(0, 0), GameRules.world_size - Pos(1, 1)):
                if GameRules.get_tile(tile.pos + d) is None:
                    continue
                if GameRules.get_tile(tile.pos + d).owner == tile.owner:
                    if GameRules.get_tile(tile.pos + d).building == tile.building.adjacent_bonus:
                        level += 1
        if level == 0:
            level = 1
        building.add_component(SpriteComponent(nickname=f"buildings:{tile.building.name}", size=WindowSize.get_block_size(), frame=level-1, frames_number=8, frame_direction=Vector2d(0, 1)))

def _create_resource_obj(tile: Tile, tile_obj: GameObject):
    resource = create_game_object(
        parent=tile_obj, 
        tags="texture:tile:resource", 
        at=InGrid((1, 1), (0, 0)), 
        layer = 1
    )
    resource.add_component(SpriteComponent(nickname=f"resources:{tile.resource.name}", size=WindowSize.get_block_size()))

def _update_tile_border(pos: Pos, tile_obj: GameObject, update_near = True):
    tile = GameRules.get_tile(pos)
    if tile is None:
        return

    i = 0
    while i < len(tile_obj.childs):
        if "texture:tile:border" in tile_obj.childs[i].tags:
            tile_obj.childs[i].destroy()
        else:
            i += 1

    for d in (Vector2d(-1, 0), Vector2d(1, 0), Vector2d(0, 1), Vector2d(0, -1)):
        if not (0 <= pos[0] + d.x < GameRules.world_size.x and 0 <= pos.y + d.y < GameRules.world_size.y):
            continue
        if (GameRules.get_tile(pos + d) is None) or (GameRules.get_tile(pos + d).owner != tile.owner):
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
            if not (0 <= pos.x + d.x < GameRules.world_size.x and 0 <= pos.y + d.y < GameRules.world_size.y):
                continue
            if GameRules.get_tile(pos + d) == None:
                continue
            if GameRules.get_tile(pos + d).owner != -1:
                _update_tile_border(pos + d, GameRules.get_tile(pos + d).obj, False)