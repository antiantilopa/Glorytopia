from engine_antiantilopa import *
from client.globals.music import SoundManager
from client.network.client import GameClient, GamePlayer
from client.texture_assign.texture_assign import TextureAssignSystem
from client.widgets.fastgameobjectcreator import *
from client.widgets.select import SelectComponent
from client.globals.window_size import WindowSize
from shared import *
import pygame as pg

from shared.util.position import Pos, PosRange

from . import components
from . import selector

class GameRules:
    world_size: Pos = Pos(0, 0)
    world: list[list["Tile|None"]] = None

    @staticmethod
    def world_size_as_Vector2d():
        return Vector2d(GameRules.world_size.intx(), GameRules.world_size.inty())

    @staticmethod
    def set_world_size(size: Vector2d|Pos|tuple[int, int]):
        if isinstance(size, Vector2d): 
            GameRules.world_size = Pos(size.intx(), size.inty())
        elif isinstance(size, tuple):
            GameRules.world_size = Pos.from_tuple(size)
        elif isinstance(size, Pos):
            GameRules.world_size = size
        
        GameRules.world = [[None for _ in range(GameRules.world_size.x)] for _ in range(GameRules.world_size.y)]

    @staticmethod
    def get_tile(pos: Pos) -> "Tile|None":
        return GameRules.world[pos.inty()][pos.intx()]

    @staticmethod
    def set_tile(tile: "Tile"):
        GameRules.world[tile.pos.inty()][tile.pos.intx()] = tile

class Tile(TileData):
    obj: GameObject

    tiles: list["Tile"] = []
    tile_map: list[list["Tile|None"]] = None

    def client_on_create(self):
        if Tile.tile_map is None:
            Tile.tile_map = [[None for _ in range(GameRules.world_size.x)] for _ in range(GameRules.world_size.y)]
        if Tile.tile_map[self.pos.inty()][self.pos.intx()] is not None:
            old_tile = Tile.tile_map[self.pos.inty()][self.pos.intx()]
            old_tile.obj.destroy()
            Tile.tiles.remove(old_tile)
        Tile.tile_map[self.pos.inty()][self.pos.intx()] = self
        GameRules.set_tile(self)
        Tile.tiles.append(self)
        self.obj = _create_tile_obj(self)

    def client_on_update(self):
        updates = self._get_updates()
        if "resource" in updates:
            if self.resource == None:
                SoundManager.new_music("harvest", 0)
        if "building" in updates:
            if updates["building"] == None:
                SoundManager.new_music("build", 0)

        # HACK: WTF R U DUIN? maybe not destroying it...
        self.obj.destroy()
        self.obj = _create_tile_obj(self)
        selector.selector_info_update()

    def client_on_destroy(self):
        pass

class City(CityData):
    obj: GameObject

    cities: list["City"] = []
    city_map: list[list["City|None"]] = None

    def client_on_create(self):
        if City.city_map is None:
            City.city_map = [[None for _ in range(GameRules.world_size.x)] for _ in range(GameRules.world_size.y)]
        if City.city_map[self.pos.inty()][self.pos.intx()] is not None:
            old_city = City.city_map[self.pos.inty()][self.pos.intx()]
            old_city.obj.destroy()
            City.cities.remove(old_city)
        City.cities.append(self)
        self.obj = _create_city_obj(self)

    def client_on_update(self):
        updates = self._get_updates()
        if "owner" in updates:
            if self.owner == GameClient.object.me.id:
                if self.is_capital:
                    SoundManager.new_music("capital_conquer", 0)
                else:
                    SoundManager.new_music("city_conquer", 0)
            if updates["owner"] == GameClient.object.me.id:
                SoundManager.new_music("city_lose", 0)
        TextureAssignSystem.update_texture(self, self.obj)
        selector.selector_info_update()

    def client_on_destroy(self):
        pass

class Unit(UnitData):
    obj: GameObject

    units: list["Unit"] = []
    
    def client_on_create(self):
        Unit.units.append(self)
        self.obj = _create_unit_obj(self)

    def client_on_update(self):
        updates = self._get_updates()
        if "pos" in updates:
            SoundManager.new_music("unit_walk", 0)
        _update_unit_obj(self)
        selector.selector_info_update()

    def client_on_destroy(self):
        if self.owner == GameClient.object.me.id:
            SoundManager.new_music("unit_kill", 0)
        _remove_unit_obj(self)
        Unit.units.remove(self)

def _create_tile_obj(tile: Tile) -> GameObject:
    world = GameObject.get_game_object_by_tags("game_screen:world_section:world")
    vector_pos = Vector2d(*tile.pos.as_tuple())
    new_tile = create_game_object(
        parent=world, 
        tags="game_screen:world_section:world:tile", 
        at=InGrid(GameRules.world_size_as_Vector2d(), vector_pos), 
        shape=Shape.RECT, 
        layer = 0
    )

    new_tile.add_component(components.TileComponent(tile, vector_pos))
    new_tile.add_component(SelectComponent())

    TextureAssignSystem.assign_texture(tile, new_tile)

    new_tile.need_draw = True
    new_tile.need_blit_set_true()
    return new_tile

def _create_unit_obj(unit: Unit) -> GameObject:
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    unit_obj = create_game_object(
        parent=unit_layer, 
        tags="game_screen:world_section:world:unit_layer:unit", 
        at=InGrid(GameRules.world_size.as_tuple(), unit.pos.as_tuple()), 
        shape=Shape.RECT, 
        layer=2
    )
    unit_obj.add_component(components.UnitComponent(unit, unit.pos))
    unit_obj.add_component(SelectComponent())

    TextureAssignSystem.assign_texture(unit, unit_obj)

    return unit_obj

def _remove_unit_obj(unit: Unit):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    unit_layer.need_draw = True
    unit.obj.destroy()

def _update_unit_obj(unit: Unit):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    unit_obj = unit.obj
    unit_obj.get_component(components.UnitComponent).pos = unit.pos
    unit_obj.get_component(Transform).set_pos(InGrid(GameRules.world_size.as_tuple(), unit.pos.as_tuple()).get_pos(unit_layer))
    TextureAssignSystem.update_texture(unit, unit_obj)


def _create_city_obj(city: City) -> GameObject:
    city_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:city_layer")
    city_obj = create_game_object(
        parent=city_layer, 
        tags="game_screen:world_section:world:city_layer:city", 
        at=InGrid(GameRules.world_size.as_tuple(), city.pos.as_tuple()), 
        shape=Shape.RECT, 
        layer=1
    )
    city_obj.add_component(SelectComponent())
    city_obj.add_component(components.CityComponent(city, city.pos))
    TextureAssignSystem.assign_texture(city, city_obj)
    return city_obj

def __create_fog(pos: Pos):
    # not used untill vision is full
    ui_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:ui_layer")

    fog = create_game_object(
        parent=ui_layer,
        tags="FOG",
        at=InGrid(GameRules.world_size.as_tuple(), pos.as_tuple()),
        shape=Shape.RECT,
        color=(128, 128, 128)
    )
    fog.add_component(components.PositionComponent(pos))
    fog.get_component(SurfaceComponent).pg_surf.set_alpha(128)

def __update_city():
    # I need the code below for camera at start
    raise NotImplementedError("should not called that. how?")
    if len(GameObject.get_group_by_tag("game_screen:world_section:world:city_layer:city")) == 0: # bullshit TODO! camera starts at capital
        world = GameObject.get_game_object_by_tags("game_screen:world_section:world")
        world.get_component(Transform).set_pos(world.get_component(SurfaceComponent).size // 2 - self.cities_updates[0].pos * WindowSize.get_block_size())
    for city in self.cities_updates:
        create_city_game_object(city)
    selector.selector_info_update()