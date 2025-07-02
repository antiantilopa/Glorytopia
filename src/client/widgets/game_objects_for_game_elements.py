from engine_antiantilopa import *
from shared import *
from client.respondings.client import Client
from .fastgameobjectcreator import *
from .select import SelectComponent

block_size = Vector2d(0, 0)

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

class TechComponent(Component):
    def __init__(self, tech: TechNode):
        super().__init__()
        self.tech = tech

def init_block_size_for_game_elements_creator(needed_block_size: Vector2d):
    global block_size
    block_size = needed_block_size

def create_tile_game_object(pos: tuple[int, int]):
    world = GameObject.get_game_object_by_tags("game_screen:world_section:world")
    self = Client.object
    i = 0
    while i < len(world.childs):
        tile_child = world.childs[i]
        if not tile_child.contains_component(PositionComponent):
            i += 1
            continue
        elif tile_child.get_component(PositionComponent).pos == Vector2d(*pos):
            tile_child.destroy()
        else:
            i += 1
    new_tile = create_game_object(world, "game_screen:world_section:world:tile", at=InGrid(self.world_size, Vector2d(*pos)), shape=Shape.RECT, layer = 0)
    new_tile.add_component(TileComponent(self.world[pos[1]][pos[0]], Vector2d(*pos)))
    new_tile.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].ttype.name, size=block_size))
    new_tile.add_component(SelectComponent())
    if self.world[pos[1]][pos[0]].building is not None:
        building = create_game_object(world, "game_screen:world_section:world:tile:building", at=InGrid(self.world_size, Vector2d(*pos)), shape=Shape.RECT, layer = 1)
        building.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].building.name, size=block_size))
        building.add_component(PositionComponent(Vector2d(*pos)))
    if self.world[pos[1]][pos[0]].resource is not None:
        resource = create_game_object(world, "game_screen:world_section:world:tile:resource", at=InGrid(self.world_size, Vector2d(*pos)), shape=Shape.RECT, layer = 1)
        resource.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].resource.name, size=block_size))
        resource.add_component(PositionComponent(Vector2d(*pos)))
    
def create_unit_game_object(unit_data: UnitData):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    unit = create_game_object(unit_layer, "game_screen:world_section:world:unit_layer:unit", at=InGrid(Client.object.world_size, unit_data.pos.as_tuple()), shape=Shape.RECT, layer=2)
    unit.add_component(UnitComponent(unit_data, unit_data.pos))
    unit.add_component(SelectComponent())
    sprite = create_game_object(unit, at=InGrid((1, 1), (0, 0)), layer=2, tags="game_screen:world_section:world:unit_layer:unit:sprite")
    sprite.add_component(SpriteComponent(nickname=unit_data.utype.name, size=block_size))
    health = create_game_object(unit, at=Position.LEFT_UP, size=block_size // 3, shape=Shape.CIRCLE, layer=3, color=ColorComponent.RED, radius=block_size.x // 6, tags="game_screen:world_section:world:unit_layer:unit:health")
    create_label(health, text=f"{unit_data.health}", font=pg.font.SysFont("consolas", block_size.x // 4), color=ColorComponent.WHITE, tags="game_screen:world_section:world:unit_layer:unit:health")

def remove_unit_game_object(pos: tuple[int, int]):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    for unit in unit_layer.childs:
        if unit.get_component(PositionComponent).pos == Vector2d(*pos):
            unit.need_blit_set_true()
            unit.destroy()
            break
    unit_layer.need_draw = True

def move_unit_game_object(pos: tuple[int, int], unit_data: UnitData):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    for unit in unit_layer.childs:
        if unit.get_component(PositionComponent).pos == Vector2d(*pos):
            unit.get_component(UnitComponent).unit_data = unit_data
            unit.get_component(UnitComponent).pos = unit_data.pos
            unit.get_component(Transform).set_pos(InGrid(Client.object.world_size, unit_data.pos).get_pos(unit_layer))
            for child in unit.childs:
                if "game_screen:world_section:world:unit_layer:unit:health" in child.tags:
                    child.childs[0].destroy()
                    create_label(child, text=f"{unit_data.health}", font=pg.font.SysFont("consolas", block_size.x // 4), color=ColorComponent.WHITE, tags="game_screen:world_section:world:unit_layer:unit:health")
            break

def create_city_game_object(city_data: CityData):
    city_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:city_layer")
    for city in city_layer.childs:
        if city.contains_component(CityComponent):
            if city.get_component(PositionComponent).pos == city_data.pos:
                city.get_component(CityComponent).city_data = city_data
                return

    city = create_game_object(city_layer, ["game_screen:world_section:world:city_layer:city"], at=InGrid(Client.object.world_size, city_data.pos), shape=Shape.RECT, layer=1)
    city.add_component(CityComponent(city_data, city_data.pos))
    city.add_component(SpriteComponent(nickname="city", size=block_size))
    city.add_component(SelectComponent())

def create_tech_tree_node(tech_win: GameObject, tech: TechNode, number: int, depth: int):
    width = 0
    if len(tech.childs) == 0:
        width = 1
    else:
        first_width = 0
        last_width = 0
        for i in range(len(tech.childs)):
            if i == 0:
                first_width = create_tech_tree_node(tech_win, tech.childs[i], number + width, depth + 1)
                width += first_width
            elif i == len(tech.childs) - 1:
                last_width = create_tech_tree_node(tech_win, tech.childs[i], number + width, depth + 1)
                width += last_width
            else:
                width += create_tech_tree_node(tech_win, tech.childs[i], number + width, depth + 1)
        create_line_game_object(tech_win, "TEST:line", at=InGrid((8, 8), (number * 2 + width - 1, depth * 2 + 0.5)), to=InGrid((8, 8), (number * 2 + width - 1, depth * 2 + 1)), color=ColorComponent.WHITE, width=5)
        if len(tech.childs) >= 2:
            create_line_game_object(tech_win, "TEST:line", at=InGrid((8, 8), (number * 2 + first_width - 1, depth * 2 + 1)), to=InGrid((8, 8), (number * 2 + 2 * width - last_width - 1, depth * 2 + 1)), color=ColorComponent.WHITE, width=5)
    if tech.parent is not None:
        create_line_game_object(tech_win, "TEST:line", at=InGrid((8, 8), (number * 2 + width - 1, depth * 2 - 0.5)), to=InGrid((8, 8), (number * 2 + width - 1, depth * 2 - 1)), color=ColorComponent.WHITE, width=5)
    
    
    tech_node = create_game_object(tech_win, f"game_screen:techs_window:tech_node", at=InGrid((8, 8), (number * 2 + width - 1, depth * 2)), shape=Shape.RECT)
    tech_node.add_component(TechComponent(tech))
    tech_node.add_component(SelectComponent())
    tech_node.add_component(SpriteComponent(nickname=tech.name, size=block_size))

    return width

def create_tech_tree():
    tech_win = GameObject.get_game_object_by_tags("game_screen:techs_window")

    roots = []
    for tech in TechNode.techs:
        if tech.parent is None:
            roots.append(tech)

    for i in range(len(roots)):
        create_tech_tree_node(tech_win, roots[i], i, 0)