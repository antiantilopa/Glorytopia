from engine_antiantilopa import *
from client.texture_assign.texture_assign import TextureAssignSystem
from client.widgets.fastgameobjectcreator import *
from client.widgets.select import SelectComponent
from client.globals.window_size import WindowSize
from shared import *
import pygame as pg

from shared.util.position import Pos, PosRange

from . import components
from . import selector
from . import replay

class Tile_R(TileData):
    obj: GameObject

    def on_create(self):
        self.obj = _create_tile_obj(self)

    def on_update(self):
        # HACK: WTF R U DUIN? maybe not destroying it...
        self.obj.destroy()
        self.obj = _create_tile_obj(self)
        selector.selector_info_update()

    def on_destroy(self):
        raise Exception("umm... sorry, wtf?")

class City_R(CityData):
    obj: GameObject

    def on_create(self):
        self.obj = _create_city_obj(self)

    def on_update(self):
        TextureAssignSystem.update_texture(self, self.obj)
        # _update_city_name_label(self, self.obj)
        # _update_city_upgrades(self, self.obj)
        selector.selector_info_update()

    def on_destroy(self):
        raise Exception("umm... sorry, wtf?")

class Unit_R(UnitData):
    obj: GameObject

    def on_create(self):
        self.obj = _create_unit_obj(self)

    def on_update(self):
        updates = self._get_updates()
        if "type" in updates:
            _remove_unit_obj(self)
            self.obj = _create_unit_obj(self)
        else:
            _update_unit_obj(self)
        selector.selector_info_update()

    def on_destroy(self):
        _remove_unit_obj(self.obj)

class TechNodeObj:
    technodeobjs: dict[str, GameObject] = {}

    @staticmethod
    def get_obj_by_technode(tech: TechNode) -> GameObject:
        if tech.name in TechNodeObj.technodeobjs:
            return TechNodeObj.technodeobjs[tech.name]
        raise KeyError(f"Tech {tech.name} not found in TechNodeObj technodeobjs.")

def _create_tile_obj(tile: TileData) -> GameObject:
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
    
    TextureAssignSystem.assign_texture(tile, new_tile, args=(replay.Replay.get_tile_data, replay.Replay.game_data.world_size))

    new_tile.need_draw = True
    new_tile.need_blit_set_true()
    return new_tile

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

    TextureAssignSystem.assign_texture(unit, unit_obj)

    return unit_obj

def _remove_unit_obj(unit_obj: GameObject):
    unit_layer = GameObject.get_game_object_by_tags("replay_screen:world_section:world:unit_layer")
    unit_layer.need_draw = True
    unit_obj.destroy()

def _update_unit_obj(unit: Unit_R):
    unit_layer = GameObject.get_game_object_by_tags("replay_screen:world_section:world:unit_layer")
    unit_obj = unit.obj
    unit_obj.get_component(components.UnitComponent).pos = unit.pos
    unit_obj.get_component(Transform).set_pos(InGrid(replay.Replay.game_data.world_size.as_tuple(), unit.pos.as_tuple()).get_pos(unit_layer))
    TextureAssignSystem.update_texture(unit, unit_obj)

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
    TextureAssignSystem.assign_texture(city, city_obj, args=(replay.Replay.get_tile_data, replay.Replay.game_data.world_size))
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