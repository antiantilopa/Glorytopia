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
    while i < len(GameObject.get_group_by_tag("game_screen:world_section:world:tile")):
        tile_child = GameObject.get_group_by_tag("game_screen:world_section:world:tile")[i]
        if not tile_child.contains_component(TileComponent):
            i += 1
            continue
        elif tile_child.get_component(TileComponent).pos == Vector2d(*pos):
            tile_child.destroy()
        else:
            i += 1
    new_tile = create_game_object(world, "game_screen:world_section:world:tile", at=InGrid(self.world_size, Vector2d(*pos)), shape=Shape.RECT, layer = 0)
    new_tile.add_component(TileComponent(self.world[pos[1]][pos[0]], Vector2d(*pos)))
    new_tile.add_component(SelectComponent())
    new_tile_sprite = create_game_object(new_tile, "game_screen:world_section:world:tile:sprite", at=InGrid((1, 1), (0, 0)), layer=0)
    new_tile_sprite.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].ttype.name, size=block_size))
    if self.world[pos[1]][pos[0]].building is not None:
        building = create_game_object(new_tile, "game_screen:world_section:world:tile:building", at=InGrid((1, 1), (0, 0)), layer = 1)
        building.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].building.name, size=block_size))
    if self.world[pos[1]][pos[0]].resource is not None:
        resource = create_game_object(new_tile, "game_screen:world_section:world:tile:resource", at=InGrid((1, 1), (0, 0)), layer = 1)
        resource.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].resource.name, size=block_size))
    if self.world[pos[1]][pos[0]].owner == -1:
        return
    print(f"update border for {Vector2d.from_tuple(pos)}", end=": ")
    update_tile_border(pos)
    for d in (Vector2d(-1, 0), Vector2d(1, 0), Vector2d(0, 1), Vector2d(0, -1)):
        if not (0 <= pos[0] + d.x < self.world_size[0] and 0 <= pos[1] + d.y < self.world_size[1]):
            continue
        if self.world[pos[1] + d.inty()][pos[0] + d.intx()] == None:
            continue
        if self.world[pos[1] + d.inty()][pos[0] + d.intx()].owner != -1:
            print(f"> update {Vector2d.from_tuple(pos) + d}", end=": ")
            update_tile_border((pos[0] + d.intx(), pos[1] + d.inty()))

def update_tile_border(pos: tuple[int, int]):
    new_tile = None
    for tile in GameObject.get_group_by_tag("game_screen:world_section:world:tile"):
        if tile.get_component(TileComponent).pos == Vector2d(*pos):
            new_tile = tile
            break
    if new_tile is None:
        print("not found")
        return
    print("found")
    i = 0
    while i < len(new_tile.childs):
        if "game_screen:world_section:world:tile:border" in new_tile.childs[i].tags:
            new_tile.childs[i].destroy()
        else:
            i += 1
    self = Client.object
    for d in (Vector2d(-1, 0), Vector2d(1, 0), Vector2d(0, 1), Vector2d(0, -1)):
        if not (0 <= pos[0] + d.x < self.world_size[0] and 0 <= pos[1] + d.y < self.world_size[1]):
            continue
        if (self.world[pos[1] + d.inty()][pos[0] + d.intx()] == None) or (self.world[pos[1] + d.inty()][pos[0] + d.intx()].owner != self.world[pos[1]][pos[0]].owner):
            create_line_game_object(new_tile, "game_screen:world_section:world:tile:border", at=d.complex_multiply(Vector2d(1, 1)) * block_size // 2, to=d.complex_multiply(Vector2d(1, -1)) * block_size // 2, color=self.get_main_color(self.order[self.world[pos[1]][pos[0]].owner]), width=5)
    new_tile.need_draw = True
    new_tile.need_blit_set_true()

def create_unit_game_object(unit_data: UnitData):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    unit = create_game_object(unit_layer, "game_screen:world_section:world:unit_layer:unit", at=InGrid(Client.object.world_size, unit_data.pos.as_tuple()), shape=Shape.RECT, layer=2)
    unit.add_component(UnitComponent(unit_data, unit_data.pos))
    unit.add_component(SelectComponent())
    sprite = create_game_object(unit, at=InGrid((1, 1), (0, 0)), layer=2, tags="game_screen:world_section:world:unit_layer:unit:sprite")
    sprite.add_component(SpriteComponent(nickname=unit_data.utype.name, size=block_size))
    health = create_game_object(unit, at=Position.LEFT_UP, size=block_size // 3, shape=Shape.CIRCLE, layer=3, color=Client.object.get_main_color(Client.object.order[unit_data.owner]), radius=block_size.x // 6, tags="game_screen:world_section:world:unit_layer:unit:health")
    create_label(health, text=f"{unit_data.health}", font=pg.font.SysFont("consolas", block_size.x // 4), color=Client.object.get_secondary_color(Client.object.order[unit_data.owner]), tags="game_screen:world_section:world:unit_layer:unit:health")

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
                    create_label(child, text=f"{unit_data.health}", font=pg.font.SysFont("consolas", block_size.x // 4), color=Client.object.get_secondary_color(Client.object.order[unit_data.owner]), tags="game_screen:world_section:world:unit_layer:unit:health")
            break

def update_city_name_label(city: GameObject):
    city_data = city.get_component(CityComponent).city_data
    city_owner = city_data.owner
    if city_owner == -1:
        return
    i = 0
    while i < len(city.childs):
        if "game_screen:world_section:world:city_layer:city:name_label" in city.childs[i].tags:
            city.childs[i].destroy()
            continue
        elif "game_screen:world_section:world:city_layer:city:name_label_background" in city.childs[i].tags:
            city.childs[i].destroy()
            continue
        else:
            i += 1

    city_name_label = create_label(city, "game_screen:world_section:world:city_layer:city:name_label", f"{city_data.level} {city_data.name}{("!" if city_data.is_capital else "")}", pg.font.SysFont("consolas", block_size.x // 6), Position.DOWN, color=Client.object.get_secondary_color(Client.object.order[city_owner]), layer=2, crop=0)
    city_name_label_background = create_game_object(city, "game_screen:world_section:world:city_layer:city:name_label_background", at=Position.DOWN, size=city_name_label.get_component(SurfaceComponent).size, shape=Shape.RECT, color=Client.object.get_main_color(Client.object.order[city_owner]), layer=1, crop=0)

def create_city_game_object(city_data: CityData):
    city_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:city_layer")
    for city in GameObject.get_group_by_tag("game_screen:world_section:world:city_layer:city"):
        if city.contains_component(CityComponent):
            if city.get_component(PositionComponent).pos == city_data.pos:
                city.get_component(CityComponent).city_data = city_data
                update_city_name_label(city)
                return
    
    city = create_game_object(city_layer, ["game_screen:world_section:world:city_layer:city"], at=InGrid(Client.object.world_size, city_data.pos), shape=Shape.RECT, layer=1)
    city.add_component(SelectComponent())
    city.add_component(CityComponent(city_data, city_data.pos))
    city_sprite = create_game_object(city, "game_screen:world_section:world:city_layer:city:sprite", size=block_size, layer=0)
    city_sprite.add_component(SpriteComponent(nickname="city", size=block_size))
    update_city_name_label(city)

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