from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from client.widgets.select import SelectComponent
from client.globals.window_size import WindowSize
from shared import *
import pygame as pg

from shared.util.position import Pos, PosRange

from . import components
from . import selector
from . import replay

class Tile:
    obj: GameObject

    tdata: TileData

    def __init__(self, tdata: TileData):
        self.tdata = tdata

    def on_create(self):
        self.obj = _create_tile_obj(self.tdata, 1)

    def on_update(self):
        # HACK: WTF R U DUIN? maybe not destroying it...
        self.obj.destroy()
        self.obj = _create_tile_obj(self.tdata)
        selector.selector_info_update()

    def on_destroy(self):
        raise Exception("umm... sorry, wtf?")

class City:
    obj: GameObject

    cdata: CityData

    def __init__(self, cdata: CityData):
        self.cdata = cdata

    def on_create(self):
        self.obj = _create_city_obj(self.cdata)

    def on_update(self):
        _update_city_name_label(self.cdata, self.obj)
        _update_city_upgrades(self.cdata, self.obj)
        selector.selector_info_update()

    def on_destroy(self):
        raise Exception("umm... sorry, wtf?")

class Unit:
    obj: GameObject

    udata: UnitData

    def __init__(self, udata: UnitData):
        self.udata = udata

    def on_create(self):
        self.obj = _create_unit_obj(self.udata)

    def on_update(self):
        _update_unit_obj(self)
        selector.selector_info_update()

    def on_destroy(self):
        _remove_unit_obj(self.obj)

def _create_tile_obj(tile: TileData, init: bool = 0) -> GameObject:
    world = GameObject.get_game_object_by_tags("replay_screen:world_section:world")
    vector_pos = Vector2d(*tile.pos.as_tuple())
    new_tile = create_game_object(
        parent=world, 
        tags="replay_screen:world_section:world:tile", 
        at=InGrid(replay.Replay.world_size_as_Vector2d(), vector_pos), 
        shape=Shape.RECT, 
        layer = 0
    )

    new_tile.add_component(components.TileComponent(tile, vector_pos))
    new_tile.add_component(SelectComponent())
    new_tile_sprite = create_game_object(
        parent=new_tile, 
        tags="replay_screen:world_section:world:tile:sprite", 
        at=InGrid((1, 1), (0, 0)), 
        layer=0
    )
    new_tile_sprite.add_component(SpriteComponent(nickname=tile.type.name, size=WindowSize.get_block_size()))
    if tile.building is not None:
        _create_building_obj(tile, new_tile)
    if tile.resource is not None:
        _create_resource_obj(tile, new_tile)
    if tile.owner != -1:
        _update_tile_border(tile.pos, new_tile, init == 0)
    new_tile.need_draw = True
    new_tile.need_blit_set_true()
    return new_tile

def _create_building_obj(tile: TileData, tile_obj: GameObject):
    building = create_game_object(
        parent=tile_obj, 
        tags="replay_screen:world_section:world:tile:building", 
        at=InGrid((1, 1), (0, 0)), 
        layer = 1
    )
    if tile.building.adjacent_bonus == None:
        building.add_component(SpriteComponent(nickname=tile.building.name, size=WindowSize.get_block_size()))
    else:
        level = 0
        for d in PosRange(Pos(-1, -1), Pos(2, 2)):
            if (tile.pos + d).is_in_box(Pos(0, 0), replay.Replay.game_data.world_size - Pos(1, 1)):
                if replay.Replay.get_tile_data(tile.pos + d) is None:
                    continue
                if replay.Replay.get_tile_data(tile.pos + d).owner == tile.owner:
                    if replay.Replay.get_tile_data(tile.pos + d).building == tile.building.adjacent_bonus:
                        level += 1
        if level == 0:
            level = 1
        building.add_component(SpriteComponent(nickname=tile.building.name, size=WindowSize.get_block_size(), frame=level-1, frames_number=8, frame_direction=Vector2d(0, 1)))

def _create_resource_obj(tile: TileData, tile_obj: GameObject):
    resource = create_game_object(
        parent=tile_obj, 
        tags="replay_screen:world_section:world:tile:resource", 
        at=InGrid((1, 1), (0, 0)), 
        layer = 1
    )
    resource.add_component(SpriteComponent(nickname=tile.resource.name, size=WindowSize.get_block_size()))

def _update_tile_border(pos: Pos, tile_obj: GameObject, update_near = True):
    tile = replay.Replay.get_tile_data(pos)
    if tile is None:
        return

    i = 0
    while i < len(tile_obj.childs):
        if "replay_screen:world_section:world:tile:border" in tile_obj.childs[i].tags:
            tile_obj.childs[i].destroy()
        else:
            i += 1

    for d in (Vector2d(-1, 0), Vector2d(1, 0), Vector2d(0, 1), Vector2d(0, -1)):
        if not (0 <= pos[0] + d.x < replay.Replay.game_data.world_size.x and 0 <= pos.y + d.y < replay.Replay.game_data.world_size.y):
            continue
        if (replay.Replay.get_tile_data(pos + d) is None) or (replay.Replay.get_tile_data(pos + d).owner != tile.owner):
            create_line_game_object(
                parent=tile_obj, 
                tags="replay_screen:world_section:world:tile:border", 
                at=d.complex_multiply(Vector2d(1, 1)) * WindowSize.get_block_size() // 2, 
                to=d.complex_multiply(Vector2d(1, -1)) * WindowSize.get_block_size() // 2, 
                color=replay.Replay.get_player_by_id(tile.owner).get_main_color(), 
                width=2 * (WindowSize.get_block_size().intx() // 15)
            )

    tile_obj.need_draw = True
    tile_obj.need_blit_set_true()
    if update_near:
        for d in (Pos(-1, 0), Pos(1, 0), Pos(0, 1), Pos(0, -1)):
            if not (0 <= pos.x + d.x < replay.Replay.game_data.world_size.x and 0 <= pos.y + d.y < replay.Replay.game_data.world_size.y):
                continue
            if replay.Replay.get_tile_data(pos + d) == None:
                continue
            if replay.Replay.get_tile_data(pos + d).owner != -1:
                _update_tile_border(pos + d, replay.Replay.get_tile(pos + d).obj, False)


def _create_unit_obj(unit: UnitData) -> GameObject:
    unit_layer = GameObject.get_game_object_by_tags("replay_screen:world_section:world:unit_layer")
    unit_obj = create_game_object(
        parent=unit_layer, 
        tags="replay_screen:world_section:world:unit_layer:unit", 
        at=InGrid(replay.Replay.game_data.world_size.as_tuple(), unit.pos.as_tuple()), 
        shape=Shape.RECT, 
        layer=2
    )
    unit_obj.add_component(components.UnitComponent(unit, unit.pos))
    unit_obj.add_component(SelectComponent())
    sprite = create_game_object(
        parent=unit_obj,
        tags="replay_screen:world_section:world:unit_layer:unit:sprite",
        at=InGrid((1, 1), (0, 0)), 
        layer=2, 
    )
    sprite.add_component(SpriteComponent(nickname=unit.type.name, size=WindowSize.get_block_size()))
    health = create_game_object(
        parent=unit_obj, 
        tags="replay_screen:world_section:world:unit_layer:unit:health",
        at=Position.LEFT_UP, 
        size=WindowSize.get_block_size() // 3, 
        shape=Shape.CIRCLE, 
        layer=3, 
        color=replay.Replay.get_player_by_id(unit.owner).get_main_color(), 
        radius=WindowSize.get_block_size().intx() // 6, 
    )
    
    create_label(
        parent=health, 
        tags="replay_screen:world_section:world:unit_layer:unit:health:number",
        text=f"{unit.health}", 
        font=pg.font.SysFont("consolas", WindowSize.get_block_size().intx() // 4), 
        color=replay.Replay.get_player_by_id(unit.owner).get_secondary_color(), 
    )
    return unit_obj

def _remove_unit_obj(unit_obj: GameObject):
    unit_layer = GameObject.get_game_object_by_tags("replay_screen:world_section:world:unit_layer")
    unit_layer.need_draw = True
    unit_obj.destroy()

def _update_unit_obj(unit: Unit):
    unit_layer = GameObject.get_game_object_by_tags("replay_screen:world_section:world:unit_layer")
    unit_obj = unit.obj
    unit_obj.get_component(components.UnitComponent).pos = unit.udata.pos
    unit_obj.get_component(Transform).set_pos(InGrid(replay.Replay.game_data.world_size.as_tuple(), unit.udata.pos.as_tuple()).get_pos(unit_layer))
    for child in unit_obj.childs:
        if "replay_screen:world_section:world:unit_layer:unit:health" in child.tags:
            child.childs[0].destroy()
            create_label(
                parent=child, 
                text=f"{unit.udata.health}", 
                font=pg.font.SysFont("consolas", WindowSize.get_block_size().intx() // 4), 
                color=replay.Replay.get_player_by_id(unit.udata.owner).get_secondary_color(),
                tags="replay_screen:world_section:world:unit_layer:unit:health:number"
            )

def _update_city_name_label(city: CityData, city_obj: GameObject):
    city_owner = city.owner
    if city_owner == -1:
        return

    i = 0
    while i < len(city_obj.childs):
        if "replay_screen:world_section:world:city_layer:city:name_label" in city_obj.childs[i].tags:
            city_obj.childs[i].destroy()
        elif "replay_screen:world_section:world:city_layer:city:name_label_background" in city_obj.childs[i].tags:
            city_obj.childs[i].destroy()
        else:
            i += 1
            
    city_name_label = create_label(
        parent=city_obj, 
        tags="replay_screen:world_section:world:city_layer:city:name_label", 
        text=f"{city.level} {city.name}{("!" if city.is_capital else "")}", 
        font=pg.font.SysFont("consolas", WindowSize.get_block_size().intx() // 6), 
        at=Position.DOWN, 
        color=replay.Replay.get_player_by_id(city.owner).get_secondary_color(), 
        layer=6, 
        crop=0
    )
    create_game_object(
        parent=city_obj, 
        tags="replay_screen:world_section:world:city_layer:city:name_label_background", 
        at=Position.DOWN, 
        size=city_name_label.get_component(SurfaceComponent).size, 
        shape=Shape.RECT, 
        color=replay.Replay.get_player_by_id(city.owner).get_main_color(), 
        layer=5, 
        crop=0
    )

def _update_city_upgrades(city: CityData, city_obj: GameObject):
    found_forge = any("replay_screen:world_section:world:city_layer:city:forge_sprite" in child.tags for child in city_obj.childs)
    found_walls = any("replay_screen:world_section:world:city_layer:city:walls_sprite" in child.tags for child in city_obj.childs)
    
    if not found_forge and city.forge:
        forge_sprite = create_game_object(
            parent=city_obj, 
            tags="replay_screen:world_section:world:city_layer:city:forge_sprite", 
            at=InGrid((1, 1), (0, 0)), 
            layer=1
        )
        forge_sprite.add_component(SpriteComponent(nickname="city_forge", size=WindowSize.get_block_size()))
        
    if not found_walls and city.walls:
        walls_sprite = create_game_object(
            parent=city_obj, 
            tags="replay_screen:world_section:world:city_layer:city:walls_sprite", 
            at=InGrid((1, 1), (0, 0)), 
            layer=2
        )
        walls_sprite.add_component(SpriteComponent(nickname="city_walls", size=WindowSize.get_block_size()))
        
def _create_city_obj(city: CityData) -> GameObject:
    city_layer = GameObject.get_game_object_by_tags("replay_screen:world_section:world:city_layer")
    city_obj = create_game_object(
        parent=city_layer, 
        tags="replay_screen:world_section:world:city_layer:city", 
        at=InGrid(replay.Replay.game_data.world_size.as_tuple(), city.pos.as_tuple()), 
        shape=Shape.RECT, 
        layer=1
    )
    city_obj.add_component(SelectComponent())
    city_obj.add_component(components.CityComponent(city, city.pos))
    city_sprite = create_game_object(
        parent=city_obj, 
        tags="replay_screen:world_section:world:city_layer:city:sprite", 
        size=WindowSize.get_block_size(), 
        layer=0
    )
    city_sprite.add_component(SpriteComponent(nickname="city", size=WindowSize.get_block_size()))
    _update_city_name_label(city, city_obj)
    _update_city_upgrades(city, city_obj)
    return city_obj

def update_fog_of_war():
    vision = replay.Replay.get_player_by_id(replay.Replay.watch_as).get_vision()
    for v in VectorRange(Vector2d(0, 0), replay.Replay.world_size_as_Vector2d()):
        if vision[v.inty()][v.intx()] == 1:
            for fog_obj in GameObject.get_group_by_tag("FOG"):
                if fog_obj.get_component(components.PositionComponent).pos == v:
                    fog_obj.need_blit_set_true()
                    fog_obj.need_draw_set_true()
                    fog_obj.destroy()
                    break
        else:
            found = False
            for fog_obj in GameObject.get_group_by_tag("FOG"):
                if fog_obj.get_component(components.PositionComponent).pos == v:
                    found = True
                    break
            if not found:
                _create_fog(v)

def _create_fog(pos: Pos):
    ui_layer = GameObject.get_game_object_by_tags("replay_screen:world_section:world:ui_layer")

    fog = create_game_object(
        parent=ui_layer,
        tags="FOG",
        at=InGrid(replay.Replay.game_data.world_size.as_tuple(), pos.as_tuple()),
        shape=Shape.RECT,
        color=(128, 128, 128)
    )
    fog.add_component(components.PositionComponent(pos))
    fog.get_component(SurfaceComponent).pg_surf.set_alpha(128)