from engine_antiantilopa import *
from shared import *
from client.respondings.client import Client
from .fastgameobjectcreator import *
from .select import SelectComponent



class PositionComponent(Component):
    def __init__(self, pos: Vector2d):
        super().__init__()
        self.pos = pos

class TileComponent(PositionComponent):
    def __init__(self, tile_data: TileData, pos: Vector2d):
        super().__init__(pos)
        self.tile_data = tile_data

class UnitComponent(PositionComponent):
    def __init__(self, unit_data: UnitData, pos: Vector2d):
        super().__init__(pos)
        self.unit_data = unit_data

class CityComponent(PositionComponent):
    def __init__(self, city_data: CityData, pos: Vector2d):
        super().__init__(pos)
        self.city_data = city_data

def create_tile_game_object(pos: tuple[int, int]):
    world = GameObject.get_game_object_by_tags("game_screen:world_section:world")
    self = Client.object
    for tile_child in world.childs:
        if not tile_child.contains_component(PositionComponent):
            continue
        if tile_child.get_component(PositionComponent).pos == Vector2d(*pos):
            tile_child.destroy()
    new_tile = create_game_object(world, "game_screen:world_section:world:tile", at=InGrid(self.world_size, Vector2d(*pos)), shape=Shape.RECT, layer = 0)
    new_tile.add_component(TileComponent(self.world[pos[1]][pos[0]], Vector2d(*pos)))
    new_tile.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].ttype.name, size=Vector2d(100, 100)))
    new_tile.add_component(SelectComponent())
    if self.world[pos[1]][pos[0]].building is not None:
        building = create_game_object(world, "game_screen:world_section:world:tile:building", at=InGrid(self.world_size, Vector2d(*pos)), shape=Shape.RECT, layer = 1)
        building.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].building.name, size=Vector2d(100, 100)))
        building.add_component(PositionComponent(Vector2d(*pos)))
    if self.world[pos[1]][pos[0]].resource is not None:
        resource = create_game_object(world, "game_screen:world_section:world:tile:resource", at=InGrid(self.world_size, Vector2d(*pos)), shape=Shape.RECT, layer = 1)
        resource.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].resource.name, size=Vector2d(100, 100)))
        resource.add_component(PositionComponent(Vector2d(*pos)))
    
def create_unit_game_object(unit_data: UnitData):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")

    unit = create_game_object(unit_layer, "game_screen:world_section:world:unit_layer:unit", at=InGrid(Client.object.world_size, unit_data.pos.as_tuple()), shape=Shape.RECT, layer=2)
    unit.add_component(UnitComponent(unit_data, unit_data.pos))
    unit.add_component(SpriteComponent(nickname=unit_data.utype.name, size=Vector2d(100, 100)))
    unit.add_component(SelectComponent())

def remove_unit_game_object(pos: tuple[int, int]):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    for unit in unit_layer.childs:
        if unit.get_component(PositionComponent).pos == Vector2d(*pos):
            unit.need_blit_set_true()
            unit.destroy()
            break

def move_unit_game_object(pos: tuple[int, int], unit_data: UnitData):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    for unit in unit_layer.childs:
        if unit.get_component(PositionComponent).pos == Vector2d(*pos):
            unit.get_component(UnitComponent).unit_data = unit_data
            unit.get_component(UnitComponent).pos = unit_data.pos
            unit.get_component(Transform).set_pos(InGrid(Client.object.world_size, unit_data.pos).get_pos(unit_layer))
            break

def create_city_game_object(city_data: CityData):
    city_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:city_layer")
    city = create_game_object(city_layer, ["game_screen:world_section:world:city_layer:city"], at=InGrid(Client.object.world_size, city_data.pos), shape=Shape.RECT, layer=100)
    city.add_component(CityComponent(city_data, city_data.pos))
    city.add_component(SpriteComponent(nickname="city", size=Vector2d(100, 100)))
    city.add_component(SelectComponent())