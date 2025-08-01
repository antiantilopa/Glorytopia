from engine_antiantilopa import *
from shared import *
from client.respondings.client import Client
from .fastgameobjectcreator import *
from .select import SelectComponent
from .sound import SoundComponent

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

    group = GameObject.get_group_by_tag("game_screen:world_section:world:tile")
    i = 0
    while i < len(group):
        if group[i].get_component(TileComponent).pos == Vector2d(*pos):
            group[i].destroy()
        else:
            i += 1

    new_tile = create_game_object(
        parent=world, 
        tags="game_screen:world_section:world:tile", 
        at=InGrid(self.world_size, Vector2d(*pos)), 
        shape=Shape.RECT, 
        layer = 0
    )

    new_tile.add_component(TileComponent(self.world[pos[1]][pos[0]], Vector2d(*pos)))
    new_tile.add_component(SelectComponent())
    new_tile_sprite = create_game_object(
        parent=new_tile, 
        tags="game_screen:world_section:world:tile:sprite", 
        at=InGrid((1, 1), (0, 0)), 
        layer=0
    )
    new_tile_sprite.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].ttype.name, size=block_size))
    if self.world[pos[1]][pos[0]].building is not None:
        building = create_game_object(
            parent=new_tile, 
            tags="game_screen:world_section:world:tile:building", 
            at=InGrid((1, 1), (0, 0)), 
            layer = 1
        )
        if self.world[pos[1]][pos[0]].building.adjacent_bonus == None:
            building.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].building.name, size=block_size))
        else:
            level = 0
            for d in VectorRange(Vector2d(-1, -1), Vector2d(2, 2)):
                if (Vector2d.from_tuple(pos) + d).is_in_box(Vector2d(0, 0), Vector2d.from_tuple(self.world_size) - Vector2d(1, 1)):
                    if self.world[pos[1] + d.inty()][pos[0] + d.intx()] is None:
                        continue
                    if self.world[pos[1] + d.inty()][pos[0] + d.intx()].owner == self.world[pos[1]][pos[0]].owner:
                        if self.world[pos[1] + d.inty()][pos[0] + d.intx()].building == self.world[pos[1]][pos[0]].building.adjacent_bonus:
                            level += 1
            if level == 0:
                level = 1
            building.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].building.name, size=block_size, frame=level-1, frames_number=8, frame_direction=Vector2d(0, 1)))
    if self.world[pos[1]][pos[0]].resource is not None:
        resource = create_game_object(
            parent=new_tile, 
            tags="game_screen:world_section:world:tile:resource", 
            at=InGrid((1, 1), (0, 0)), 
            layer = 1
        )
        resource.add_component(SpriteComponent(nickname=self.world[pos[1]][pos[0]].resource.name, size=block_size))
    if self.world[pos[1]][pos[0]].owner == -1:
        return
    
    update_tile_border(pos)
    for d in (Vector2d(-1, 0), Vector2d(1, 0), Vector2d(0, 1), Vector2d(0, -1)):
        if not (0 <= pos[0] + d.x < self.world_size[0] and 0 <= pos[1] + d.y < self.world_size[1]):
            continue
        if self.world[pos[1] + d.inty()][pos[0] + d.intx()] == None:
            continue
        if self.world[pos[1] + d.inty()][pos[0] + d.intx()].owner != -1:
            update_tile_border((pos[0] + d.intx(), pos[1] + d.inty()))
    
    new_tile.need_draw = True
    new_tile.need_blit_set_true()

def update_tile_border(pos: tuple[int, int]):
    new_tile = next((x for x in GameObject.get_group_by_tag("game_screen:world_section:world:tile") 
                     if x.get_component(TileComponent).pos == Vector2d(*pos)), None)
    if new_tile is None:
        return
    

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
            create_line_game_object(
                parent=new_tile, 
                tags="game_screen:world_section:world:tile:border", 
                at=d.complex_multiply(Vector2d(1, 1)) * block_size // 2, 
                to=d.complex_multiply(Vector2d(1, -1)) * block_size // 2, 
                color=self.get_main_color(self.order[self.world[pos[1]][pos[0]].owner]), 
                width=2 * (block_size.x // 15)
            )

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
    
    create_label(
        parent=health, 
        text=f"{unit_data.health}", 
        font=pg.font.SysFont("consolas", block_size.x // 4), 
        color=Client.object.get_secondary_color(Client.object.order[unit_data.owner]), 
        tags="game_screen:world_section:world:unit_layer:unit:health"
    )

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
    if unit_data.pos != Vector2d(*pos):
        SoundComponent(nickname="unit_walk").play_once()
    for unit in unit_layer.childs:
        if unit.get_component(PositionComponent).pos == Vector2d(*pos):
            unit.get_component(UnitComponent).unit_data = unit_data
            unit.get_component(UnitComponent).pos = unit_data.pos
            unit.get_component(Transform).set_pos(InGrid(Client.object.world_size, unit_data.pos).get_pos(unit_layer))
            for child in unit.childs:
                if "game_screen:world_section:world:unit_layer:unit:health" in child.tags:
                    child.childs[0].destroy()
                    create_label(
                        parent=child, 
                        text=f"{unit_data.health}", 
                        font=pg.font.SysFont("consolas", block_size.x // 4), 
                        color=Client.object.get_secondary_color(Client.object.order[unit_data.owner]), 
                        tags="game_screen:world_section:world:unit_layer:unit:health"
                    )
            break

def update_city_name_label(city: GameObject):
    city_data = city.get_component(CityComponent).city_data
    city_owner = city_data.owner
    if city_owner == -1:
        return

    map(
        lambda x: x.destroy() if 
        "game_screen:world_section:world:city_layer:city:name_label" in x.tags or 
        "game_screen:world_section:world:city_layer:city:name_label_background" in x.tags else None, 
        city.childs
    )

    city_name_label = create_label(
        parent=city, 
        tags="game_screen:world_section:world:city_layer:city:name_label", 
        text=f"{city_data.level} {city_data.name}{("!" if city_data.is_capital else "")}", 
        font=pg.font.SysFont("consolas", block_size.x // 6), 
        at=Position.DOWN, 
        color=Client.object.get_secondary_color(Client.object.order[city_owner]), 
        layer=6, 
        crop=0
    )
    city_name_label_background = create_game_object(
        parent=city, 
        tags="game_screen:world_section:world:city_layer:city:name_label_background", 
        at=Position.DOWN, 
        size=city_name_label.get_component(SurfaceComponent).size, 
        shape=Shape.RECT, 
        color=Client.object.get_main_color(Client.object.order[city_owner]), 
        layer=5, 
        crop=0
    )

def update_city_upgrades(city: GameObject):
    found_forge = any("game_screen:world_section:world:city_layer:city:forge_sprite" in child.tags for child in city.childs)
    found_walls = any("game_screen:world_section:world:city_layer:city:walls_sprite" in child.tags for child in city.childs)
    
    if not found_forge and city.get_component(CityComponent).city_data.forge:
        forge_sprite = create_game_object(
            parent=city, 
            tags="game_screen:world_section:world:city_layer:city:forge_sprite", 
            at=InGrid((1, 1), (0, 0)), 
            layer=1
        )
        forge_sprite.add_component(SpriteComponent(nickname="city_forge", size=block_size))
        
    if not found_walls and city.get_component(CityComponent).city_data.walls:
        walls_sprite = create_game_object(
            parent=city, 
            tags="game_screen:world_section:world:city_layer:city:walls_sprite", 
            at=InGrid((1, 1), (0, 0)), 
            layer=2
        )
        walls_sprite.add_component(SpriteComponent(nickname="city_walls", size=block_size))
        
def create_city_game_object(city_data: CityData):
    city_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:city_layer")
    for city in GameObject.get_group_by_tag("game_screen:world_section:world:city_layer:city"):
        if city.contains_component(CityComponent):
            if city.get_component(PositionComponent).pos == city_data.pos:
                if city_data.owner != city.get_component(CityComponent).city_data.owner:
                    if city_data.owner != -1:
                        if Client.object.myname == Client.object.order[city_data.owner]:
                            SoundComponent(nickname="city_conquer").play_once()
                    elif city.get_component(CityComponent).city_data.owner != -1:
                        if Client.object.myname == Client.object.order[city.get_component(CityComponent).city_data.owner]:
                            SoundComponent(nickname="city_lose").play_once()
                city.get_component(CityComponent).city_data = city_data
                update_city_name_label(city)
                update_city_upgrades(city)
                return
    
    city = create_game_object(city_layer, ["game_screen:world_section:world:city_layer:city"], at=InGrid(Client.object.world_size, city_data.pos), shape=Shape.RECT, layer=1)
    city.add_component(SelectComponent())
    city.add_component(CityComponent(city_data, city_data.pos))
    city_sprite = create_game_object(city, "game_screen:world_section:world:city_layer:city:sprite", size=block_size, layer=0)
    city_sprite.add_component(SpriteComponent(nickname="city", size=block_size))
    update_city_name_label(city)
    update_city_upgrades(city)

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
        create_line_game_object(
            parent=tech_win, 
            tags="TEST:line", 
            at=InGrid((8, 8), (number * 2 + width - 1, depth * 2 + 0.5)), 
            to=InGrid((8, 8), (number * 2 + width - 1, depth * 2 + 1)), 
            color=ColorComponent.WHITE, 
            width=5
        )
        if len(tech.childs) >= 2:
            create_line_game_object(
                parent=tech_win, tags="TEST:line", 
                at=InGrid((8, 8), (number * 2 + first_width - 1, depth * 2 + 1)), 
                to=InGrid((8, 8), (number * 2 + 2 * width - last_width - 1, depth * 2 + 1)), 
                color=ColorComponent.WHITE, 
                width=5
            )
    if tech.parent is not None:
        create_line_game_object(
            parent=tech_win, 
            tags="TEST:line", 
            at=InGrid((8, 8), (number * 2 + width - 1, depth * 2 - 0.5)), 
            to=InGrid((8, 8), (number * 2 + width - 1, depth * 2 - 1)), 
            color=ColorComponent.WHITE, 
            width=5
        )
    
    
    tech_node = create_game_object(tech_win, f"game_screen:techs_window:tech_node", at=InGrid((8, 8), (number * 2 + width - 1, depth * 2)), shape=Shape.RECT)
    tech_node.add_component(TechComponent(tech))
    tech_node.add_component(SelectComponent())
    tech_node.add_component(SpriteComponent(nickname=tech.name, size=block_size))

    return width

def create_tech_tree():
    tech_win = GameObject.get_game_object_by_tags("game_screen:techs_window")

    roots = []
    for tech in TechNode.values():
        if tech.parent is None:
            roots.append(tech)

    for i in range(len(roots)):
        create_tech_tree_node(tech_win, roots[i], i, 0)