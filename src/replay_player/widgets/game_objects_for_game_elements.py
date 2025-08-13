from engine_antiantilopa import *
from replay_player.core.replay import Replay
from server.core.world import World
from shared import *
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
    
    def __setattr__(self, name, value):
        return object.__setattr__(self, name, value)

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
        at=InGrid(World.object.size, Vector2d(*pos)), 
        shape=Shape.RECT, 
        layer = 0
    )

    new_tile.add_component(TileComponent(World.object.world[pos[1]][pos[0]], Vector2d(*pos)))
    new_tile.add_component(SelectComponent())
    new_tile_sprite = create_game_object(
        parent=new_tile, 
        tags="game_screen:world_section:world:tile:sprite", 
        at=InGrid((1, 1), (0, 0)), 
        layer=0
    )
    new_tile_sprite.add_component(SpriteComponent(nickname=World.object.world[pos[1]][pos[0]].ttype.name, size=block_size))
    if World.object.world[pos[1]][pos[0]].building is not None:
        building = create_game_object(
            parent=new_tile, 
            tags="game_screen:world_section:world:tile:building", 
            at=InGrid((1, 1), (0, 0)), 
            layer = 1
        )
        if World.object.world[pos[1]][pos[0]].building.adjacent_bonus == None:
            building.add_component(SpriteComponent(nickname=World.object.world[pos[1]][pos[0]].building.name, size=block_size))
        else:
            level = 0
            for d in VectorRange(Vector2d(-1, -1), Vector2d(2, 2)):
                if (Vector2d.from_tuple(pos) + d).is_in_box(Vector2d(0, 0), World.object.size - Vector2d(1, 1)):
                    if World.object.world[pos[1] + d.inty()][pos[0] + d.intx()].owner == World.object.world[pos[1]][pos[0]].owner:
                        if World.object.world[pos[1] + d.inty()][pos[0] + d.intx()].building == World.object.world[pos[1]][pos[0]].building.adjacent_bonus:
                            level += 1
            if level == 0:
                level = 1
            building.add_component(SpriteComponent(nickname=World.object.world[pos[1]][pos[0]].building.name, size=block_size, frame=level-1, frames_number=8, frame_direction=Vector2d(0, 1)))
    if World.object.world[pos[1]][pos[0]].resource is not None:
        resource = create_game_object(
            parent=new_tile, 
            tags="game_screen:world_section:world:tile:resource", 
            at=InGrid((1, 1), (0, 0)), 
            layer = 1
        )
        resource.add_component(SpriteComponent(nickname=World.object.world[pos[1]][pos[0]].resource.name, size=block_size))
    if World.object.world[pos[1]][pos[0]].owner != -1:
        update_tile_border(pos)
        for d in (Vector2d(-1, 0), Vector2d(1, 0), Vector2d(0, 1), Vector2d(0, -1)):
            if not (0 <= pos[0] + d.x < World.object.size.x and 0 <= pos[1] + d.y < World.object.size.y):
                continue
            if World.object.world[pos[1] + d.inty()][pos[0] + d.intx()] == None:
                continue
            if World.object.world[pos[1] + d.inty()][pos[0] + d.intx()].owner != -1:
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
    for d in (Vector2d(-1, 0), Vector2d(1, 0), Vector2d(0, 1), Vector2d(0, -1)):
        if not (0 <= pos[0] + d.x < World.object.size.x and 0 <= pos[1] + d.y < World.object.size.y):
            continue
        if (World.object.world[pos[1] + d.inty()][pos[0] + d.intx()] == None) or (World.object.world[pos[1] + d.inty()][pos[0] + d.intx()].owner != World.object.world[pos[1]][pos[0]].owner):
            create_line_game_object(
                parent=new_tile, 
                tags="game_screen:world_section:world:tile:border", 
                at=d.complex_multiply(Vector2d(1, 1)) * block_size // 2, 
                to=d.complex_multiply(Vector2d(1, -1)) * block_size // 2, 
                color=Replay.colors[World.object.world[pos[1]][pos[0]].owner][0], 
                width=2 * (block_size.x // 15)
            )

    new_tile.need_draw = True
    new_tile.need_blit_set_true()

def create_unit_game_object(unit_data: UnitData):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    unit = create_game_object(unit_layer, "game_screen:world_section:world:unit_layer:unit", at=InGrid(World.object.size, unit_data.pos.as_tuple()), shape=Shape.RECT, layer=2)
    unit.add_component(UnitComponent(unit_data, unit_data.pos))
    unit.add_component(SelectComponent())
    sprite = create_game_object(unit, at=InGrid((1, 1), (0, 0)), layer=2, tags="game_screen:world_section:world:unit_layer:unit:sprite")
    sprite.add_component(SpriteComponent(nickname=unit_data.utype.name, size=block_size))
    health = create_game_object(unit, at=Position.LEFT_UP, size=block_size // 3, shape=Shape.CIRCLE, layer=3, color=Replay.colors[unit_data.owner][0], radius=block_size.x // 6, tags="game_screen:world_section:world:unit_layer:unit:health")
    
    create_label(
        parent=health, 
        text=f"{unit_data.health}", 
        font=pg.font.SysFont("consolas", block_size.x // 4), 
        color=Replay.colors[unit_data.owner][1], 
        tags="game_screen:world_section:world:unit_layer:unit:health:number" 
    )

def remove_unit_game_object(unit_data: UnitData):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    unit_layer.need_draw = True
    for unit in unit_layer.childs:
        if (unit.get_component(UnitComponent).pos == unit_data.pos) and (unit.get_component(UnitComponent).unit_data.owner == unit_data.owner):
            unit.need_blit_set_true()
            unit.need_draw_set_true()
            unit.destroy()
            return
        elif (unit.get_component(UnitComponent).pos == unit_data.pos):
            print("SUPER WTF !!!! THERE ARE 2 UNITS ON THE SAME POSITION!!")
    print(f"WTF !!! TRIED TO REMOVE UNIT ON {unit_data.pos}")

def move_unit_game_object(pos: tuple[int, int], unit_data: UnitData):
    unit_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:unit_layer")
    for unit in unit_layer.childs:
        if unit.get_component(UnitComponent).pos == Vector2d(*pos):
            unit.get_component(UnitComponent).unit_data = unit_data
            unit.get_component(UnitComponent).pos = unit_data.pos
            unit.get_component(Transform).set_pos(InGrid(World.object.size, unit_data.pos).get_pos(unit_layer))
            for child in unit.childs:
                if "game_screen:world_section:world:unit_layer:unit:health" in child.tags:
                    child.childs[0].destroy()
                    create_label(
                        parent=child, 
                        text=f"{unit_data.health}", 
                        font=pg.font.SysFont("consolas", block_size.x // 4), 
                        color=Replay.colors[unit_data.owner][1], 
                        tags="game_screen:world_section:world:unit_layer:unit:health:number"
                    )
            return
    print(f"WTF !!! TRIED TO MOVE UNIT FROM {pos} to {unit_data.pos}")

def update_city_name_label(city: GameObject):
    city_data = city.get_component(CityComponent).city_data
    city_owner = city_data.owner
    if city_owner == -1:
        return

    i = 0
    while i < len(city.childs):
        if "game_screen:world_section:world:city_layer:city:name_label" in city.childs[i].tags:
            city.childs[i].destroy()
        elif "game_screen:world_section:world:city_layer:city:name_label_background" in city.childs[i].tags:
            city.childs[i].destroy()
        else:
            i += 1
            
    city_name_label = create_label(
        parent=city, 
        tags="game_screen:world_section:world:city_layer:city:name_label", 
        text=f"{city_data.level} {city_data.name}{("!" if city_data.is_capital else "")}", 
        font=pg.font.SysFont("consolas", block_size.x // 6), 
        at=Position.DOWN, 
        color=Replay.colors[city_owner][1], 
        layer=6, 
        crop=0
    )
    city_name_label_background = create_game_object(
        parent=city, 
        tags="game_screen:world_section:world:city_layer:city:name_label_background", 
        at=Position.DOWN, 
        size=city_name_label.get_component(SurfaceComponent).size, 
        shape=Shape.RECT, 
        color=Replay.colors[city_owner][0], 
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
            if city.get_component(CityComponent).pos == city_data.pos:
                city.get_component(CityComponent).city_data = city_data
                update_city_name_label(city)
                update_city_upgrades(city)
                return
    
    city = create_game_object(city_layer, ["game_screen:world_section:world:city_layer:city"], at=InGrid(World.object.size, city_data.pos), shape=Shape.RECT, layer=1)
    city.add_component(SelectComponent())
    city.add_component(CityComponent(city_data, city_data.pos))
    city_sprite = create_game_object(city, "game_screen:world_section:world:city_layer:city:sprite", size=block_size, layer=0)
    city_sprite.add_component(SpriteComponent(nickname="city", size=block_size))
    update_city_name_label(city)
    update_city_upgrades(city)

def update_fog_of_war():
    vision = Replay.obj.game.players[Replay.obj.watch_as].vision
    for v in VectorRange(Vector2d(0, 0), World.object.size):
        if vision[v.inty()][v.intx()] == 1:
            for fog_obj in GameObject.get_group_by_tag("FOG"):
                if fog_obj.get_component(PositionComponent).pos == v:
                    fog_obj.need_blit_set_true()
                    fog_obj.need_draw_set_true()
                    fog_obj.destroy()
                    break
        else:
            found = False
            for fog_obj in GameObject.get_group_by_tag("FOG"):
                if fog_obj.get_component(PositionComponent).pos == v:
                    found = True
                    break
            if not found:
                create_fog(v)

def create_fog(v):
    ui_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:ui_layer")

    fog = create_game_object(
        parent=ui_layer,
        tags="FOG",
        at=InGrid(World.object.size, v),
        shape=Shape.RECT,
        color=(128, 128, 128)
    )
    fog.add_component(PositionComponent(v))
    fog.get_component(SurfaceComponent).pg_surf.set_alpha(128)

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