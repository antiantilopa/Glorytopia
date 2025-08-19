from engine_antiantilopa import *
from client.globals.settings import Settings
from replay_player.core.replay import Replay
from replay_player.widgets.fastgameobjectcreator import *
from replay_player.widgets.game_objects_for_game_elements import *
from replay_player.widgets.texture_load import load_textures
from replay_player.widgets.select import SelectComponent
from serializator.data_format import Format
from server.core.city import City
from server.core.player import Player
from server.core.tile import Tile
from server.core.unit import Unit
from server.core.updating_object import UpdatingObject
from server.core.world import World
from shared import *
import pygame as pg
from copy import deepcopy



block_size = Vector2d(100, 100)

def load(screen_size: Vector2d = Vector2d(1200, 800)) -> GameObject:
    if len(GameObject.get_group_by_tag("game_screen")) > 0:
        return GameObject.get_game_object_by_tags("game_screen")
    global block_size

    load_textures(Settings.texture_packs.order)

    scene = create_game_object(tags="game_screen", size=screen_size)

    block_size = screen_size // Vector2d(12, 8) // 2
    init_block_size_for_game_elements_creator(block_size)

    def deleteme(*_):
        try:
            exec(input())
        except Exception as e:
            print(f"error: {e}")

    scene.add_component(KeyBindComponent([pg.K_q], 0, 1, deleteme))

    create_game_object(scene, "game_screen:world_section", at=InGrid((12, 8), (0, 0), (8, 8)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)
    
    techs_window = create_list_game_object(scene, "game_screen:techs_window", at=InGrid((12, 8), (0, 0), (8, 8)), color=(0, 70, 150), shape=Shape.RECT, axis=(1, 1), speed=Vector2d(40, 40) * block_size // 100, bound=1, layer=0, x_axis_keys=[pg.K_a, pg.K_d], y_axis_keys=[pg.K_w, pg.K_s])
    techs_window.add_component(KeyBindComponent([pg.K_ESCAPE], 0, 1, close_techs_window))
    create_tech_tree()

    for child in techs_window.childs:
        if child.contains_component(TechComponent):
            child.add_component(OnClickComponent([1, 0, 0], 0, 1, on_tech_click))
    techs_window.disable()

    info_section = create_game_object(scene, "game_screen:info_section", at=InGrid((12, 8), (8, 0), (4, 8)), shape=Shape.RECT)

    money_label = create_label(
        parent=info_section, 
        tags="game_screen:info_section:money_label", 
        text=f"Money: {Replay.obj.game.players[Replay.obj.watch_as].money}", font=pg.font.SysFont("consolas", screen_size.y // 40), 
        at=InGrid((2, 8), (0, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )

    selector_section = create_game_object(info_section, at=InGrid((1, 8), (0, 1), (1, 5)), shape=Shape.RECTBORDER, color=ColorComponent.WHITE, width=2, margin=Vector2d(5, 0), tags="game_screen:info_section:selector_section")
    selector_image_section = create_game_object(selector_section, at=InGrid((4, 5), (0, 0), (1, 1)), surface_margin=Vector2d(7, 2), tags="game_screen:info_section:selector_section:selector_image_section")
    selector_info_section = create_game_object(selector_section, at=InGrid((4, 5), (0, 1), (4, 4)), surface_margin=Vector2d(7, 2), tags="game_screen:info_section:selector_section:selector_info_section")
    now_playing_label = create_label_block(
        parent=info_section, 
        tags="game_screen:info_section:now_playing_label", 
        text=f"Now playing:\n{Replay.obj.game.now_playing_player_index}", 
        font=pg.font.SysFont("consolas", screen_size.y // 40), 
        at=InGrid((2, 8), (1, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )

    next_frame_button = create_game_object(info_section, "game_screen:info_section:next_frame_button", at=InGrid((1, 8), (0, 7), (1, 1)), color=(50, 150, 50), shape=Shape.RECT)
    next_frame_label = create_label(
        parent=next_frame_button, 
        tags="game_screen:info_section:next_frame_label", 
        text="End Turn", 
        font=pg.font.SysFont("consolas", screen_size.y // 40), 
        at=InGrid((1, 1), (0, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )
    next_frame_button.add_component(OnClickComponent([1, 0, 0], 0, 1, next_frame_click))
    next_frame_button.add_component(KeyBindComponent([pg.K_SPACE], 1, 1, next_frame_click))


    techs_button = create_game_object(info_section, "game_screen:info_section:techs_button", at=InGrid((1, 8), (0, 6), (1, 1)), color=(0, 150, 250), shape=Shape.RECT)
    techs_label = create_label(
        parent=techs_button, 
        tags="game_screen:info_section:techs_label", 
        text="Technology", 
        font=pg.font.SysFont("consolas", screen_size.y // 40), 
        at=InGrid((1, 1), (0, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )
    techs_button.add_component(OnClickComponent([1, 0, 0], 0, 1, open_techs_window))
    init_world()

    units = []
    cities = []
    tiles = []
    for unit in Unit.units:
        unit.previous_pos = Vector2d(-1, -1)
        units.append(unit)
    for city in City.cities:
        cities.append(city)
    for row in World.object.world:
        for tile in row:
            tiles.append(tile)
    update_unit(units)
    update_city(cities)
    update_tile(tiles)
    update_player(Replay.obj.game.players[Replay.obj.watch_as])

    for unit in Unit.units:
        unit.previous_pos = unit.pos

    return scene

def next_frame_click(*_):
    Replay.obj.next_frame()
    units = []
    cities = []
    tiles = []
    for obj in UpdatingObject.updated_objs:
        if isinstance(obj, Unit):
            units.append(obj)
        elif isinstance(obj, City):
            cities.append(obj)
        elif isinstance(obj, Tile):
            tiles.append(obj)
        elif isinstance(obj, Player):
            continue
        else:
            raise Exception("!!! Updating object is neither unit, city, tile, nor player")
    update_unit(units)
    update_city(cities)
    update_tile(tiles)
    update_player(Replay.obj.game.players[Replay.obj.watch_as])
    while len(UpdatingObject.updated_objs) != 0:
        UpdatingObject.updated_objs[0].refresh_updated()

def selecting(coords: Vector2d):
    if Replay.obj.game.world[coords.inty()][coords.intx()] is None:
        return
    
    for uobj in GameObject.get_group_by_tag("game_screen:world_section:world:unit_layer:unit"):
        if uobj.get_component(PositionComponent).pos == coords:
            if uobj.get_component(SelectComponent).is_selected:
                uobj.get_component(SelectComponent).deselect()
                break
            else:
                uobj.get_component(SelectComponent).select()
                return
            
    for tile in GameObject.get_group_by_tag("game_screen:world_section:world:tile"):
        if tile.get_component(PositionComponent).pos == coords:
            if tile.get_component(SelectComponent).is_selected:
                tile.get_component(SelectComponent).deselect()
                break
            else:
                tile.get_component(SelectComponent).select()
                return
    
def selector_info_update():
    selector_info_section = GameObject.get_game_object_by_tags("game_screen:info_section:selector_section:selector_info_section")
    selector_image_section = GameObject.get_game_object_by_tags("game_screen:info_section:selector_section:selector_image_section")

    while len(selector_info_section.childs) != 0:
        selector_info_section.childs[0].destroy()

    while len(selector_image_section.childs) != 0:
        selector_image_section.childs[0].destroy()

    selector_image_section.need_draw = True
    selector_info_section.need_draw = True

    if SelectComponent.selected is None:
        return

    buttons = []
    text = ""
    
    if SelectComponent.selected.contains_component(TileComponent):
        img = create_game_object(selector_image_section, tags="game_screen:info_section:selector_section:selector_image_section:tile_image", at=InGrid((1, 1), (0, 0)), layer=0)
        img.add_component(SpriteComponent(nickname=SelectComponent.selected.get_component(TileComponent).tile_data.ttype.name, size=block_size))
        is_there_city = False
        city_data = None
        if SelectComponent.selected.get_component(TileComponent).tile_data.resource is not None:
            r_img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:resource_image", at=InGrid((1, 1), (0, 0)), layer=1)
            r_img.add_component(SpriteComponent(nickname=SelectComponent.selected.get_component(TileComponent).tile_data.resource.name, size=block_size))
        elif  SelectComponent.selected.get_component(TileComponent).tile_data.building is not None:
            r_img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:building_image", at=InGrid((1, 1), (0, 0)), layer=1)
            if SelectComponent.selected.get_component(TileComponent).tile_data.building.adjacent_bonus == None:
                r_img.add_component(SpriteComponent(nickname=SelectComponent.selected.get_component(TileComponent).tile_data.building.name, size=block_size))
            else:
                r_img.add_component(SpriteComponent(nickname=SelectComponent.selected.get_component(TileComponent).tile_data.building.name, size=block_size, frame=0, frames_number=8, frame_direction=Vector2d(0, 1)))
        else:
            for city in City.cities:
                if city.pos == SelectComponent.selected.get_component(TileComponent).pos:
                    r_img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:city_image", at=InGrid((1, 1), (0, 0)), layer=1)
                    r_img.add_component(SpriteComponent(nickname="city", size=block_size))
                    is_there_city = True
                    city_data = city
                    break
        if not is_there_city:
            tile_data = SelectComponent.selected.get_component(TileComponent).tile_data
            text = "\n".join((
                f"type: {tile_data.ttype.name}", 
                f"owner: {tile_data.owner if tile_data.owner != -1 else None}", 
                f"resorce: {tile_data.resource.name if tile_data.resource is not None else None}", 
                f"building: {tile_data.building.name if tile_data.building is not None else None}",
                f"pos: {tile_data.pos}", 
            ))
            if tile_data.owner != -1 and Replay.obj.watch_as == tile_data.owner:
                if tile_data.resource is not None:
                    for tech in Replay.obj.game.players[Replay.obj.watch_as].techs:
                        if tile_data.resource in tech.harvestables:
                            buttons.append(("harvest:2"))
                if tile_data.building is None:
                    for tech in Replay.obj.game.players[Replay.obj.watch_as].techs:
                        for btype in tech.buildings:
                            if (tile_data.ttype in btype.ttypes) and ((btype.required_resource is None) or (btype.required_resource == tile_data.resource)):
                                buttons.append((f"{btype.name}:{btype.cost}"))
                    for tech in Replay.obj.game.players[Replay.obj.watch_as].techs:
                        for terraform in tech.terraforms:
                            if (tile_data.ttype == terraform.from_ttype) and ((terraform.from_resource is None) or (terraform.from_resource == tile_data.resource)):
                                buttons.append((f"{terraform.name}:{terraform.cost}"))
        else:
            text = "\n".join((
                f"city: {city_data.name}",
                f"owner: {city_data.owner if city_data.owner != -1 else None}", 
                f"level: {city_data.level}",
                f"population: {city_data.population}/{city_data.level + 1}",
                f"fullness: {city_data.fullness}/{city_data.level + 1}",
                f"income: +{city_data.level + city_data.is_capital + city_data.forge}",
                f"pos: {city_data.pos}",
                f"Capital" if city_data.is_capital else ""
            ))
            if city_data.owner != -1 and Replay.obj.watch_as == city_data.owner:
                found = 0
                for unit_data in Unit.units:
                    if unit_data.pos == city_data.pos:
                        found = 1
                        break
                if city_data.fullness != city_data.level + 1 and not found:
                    for tech in Replay.obj.game.players[Replay.obj.watch_as].techs:
                        for utype in tech.units:
                            buttons.append((f"{utype.name}:{utype.cost}"))
    elif SelectComponent.selected.contains_component(UnitComponent):
        unit_data = SelectComponent.selected.get_component(UnitComponent).unit_data

        img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:image", at=InGrid((1, 1), (0, 0)))
        img.add_component(SpriteComponent(nickname=unit_data.utype.name, size=block_size))
        
        text = "\n".join((
            f"type: {unit_data.utype.name}",
            f"owner: {unit_data.owner if unit_data.owner != -1 else None}", 
            f"health: {unit_data.health}",
            f"can_move?: {"no" if unit_data.moved else "yes"}",
            f"can_attack?: {"no" if unit_data.attacked else "yes"}",
            f"pos: {unit_data.pos}",
            f"pos: {SelectComponent.selected.get_component(UnitComponent).pos}"
        ))
        if not (unit_data.moved or unit_data.attacked):
            city_found = False
            for city in City.cities:
                if city.pos == unit_data.pos:
                    if city.owner == unit_data.owner:
                        break
                    else:
                        city_found = True
                        break
            if city_found:
                buttons.append(("Conquer city"))
    elif SelectComponent.selected.contains_component(TechComponent):
        tech = SelectComponent.selected.get_component(TechComponent).tech

        img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:image", at=InGrid((1, 1), (0, 0)))
        img.add_component(SpriteComponent(nickname=tech.name, size=block_size))

        my_cities_count = 0
        for city in City.cities:
            if city.owner != -1 and Replay.obj.watch_as == city.owner:
                my_cities_count += 1
        text = "\n".join((
            f"name: {tech.name}    " + (f"owned" if tech in Replay.obj.game.players[Replay.obj.watch_as].techs else "not owned"),
            f"cost: {tech.cost + tech.tier * my_cities_count}    " + f"tier: {tech.tier}",
            (f"buildings: {', '.join([b.name for b in tech.buildings])}\n" if len(tech.buildings) > 0 else "") +
            (f"units: {', '.join([u.name for u in tech.units])}\n" if len(tech.units) > 0 else "") +
            (f"resources: {', '.join([r.name for r in tech.harvestables])}\n" if len(tech.harvestables) > 0 else "") +
            (f"terrain: {', '.join([t.name for t in tech.accessable])}\n" if len(tech.accessable) > 0 else "") + 
            (f"defecnces: {', '.join([t.name for t in tech.defence])}\n" if len(tech.defence) > 0 else "") + 
            (f"terraforms: {', '.join([t.name for t in tech.terraforms])}\n" if len(tech.terraforms) > 0 else "") + 
            (f"achievements: {', '.join([a for a in tech.achievements])}\n" if len(tech.achievements) > 0 else "")
        ))
        if (tech.parent is not None) and (tech.parent in Replay.obj.game.players[Replay.obj.watch_as].techs) and (tech not in Replay.obj.game.players[Replay.obj.watch_as].techs):
            buttons.append((f"buy:{tech.cost + tech.tier * my_cities_count}"))
    create_label_block(
        parent=selector_info_section, 
        tags="game_screen:info_section:selector_section:selector_info_section:label_block", 
        text=text, 
        font=pg.font.SysFont("consolas", block_size.y // 5),  
        at=Position.LEFT_UP, 
        text_pos=Position.LEFT, 
        color=ColorComponent.RED
    )
    selector_info_buttons_section = create_list_game_object(selector_info_section, bound=1, at=InGrid((1, 5), (0, 2), (1, 3)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4), tags="game_screen:info_section:selector_section:selector_info_section:buttons_section")

    for i in range(len(buttons)):
        button_sec = create_game_object(selector_info_buttons_section, at=InGrid((1, 5), (0, i), (1, 1)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4), tags="game_screen:info_section:selector_section:selector_info_section:buttons_section:button_section")
        button = create_game_object(button_sec, at=InGrid((10, 1), (0, 0), (1, 1)), color=ColorComponent.GREEN, shape=Shape.RECT, tags="game_screen:info_section:selector_section:selector_info_section:buttons_section:button_section:button")
        button.add_component(OnClickComponent((1, 0, 0), 0, 1, buttons[i][1], (buttons[i][2] if len(buttons[i]) > 2 else ())))
        create_label(
            parent=button_sec, 
            text=buttons[i][0], 
            font=pg.font.SysFont("consolas", block_size.y // 5), 
            at=InGrid((10, 1), (1, 0), (9, 1)), 
            margin=Vector2d(5, 0), 
            color=ColorComponent.RED, 
            tags="game_screen:info_section:selector_section:selector_info_section:buttons_section:button_sec:label"
        )

def on_world_click(g_obj: GameObject, keys: tuple[bool, bool, bool], pos: Vector2d, *_):
    
    world_sec = GameObject.get_game_object_by_tags("game_screen:world_section")
    world = GameObject.get_game_object_by_tags("game_screen:world_section:world")

    if not Vector2d.is_in_box(pos + world.get_component(Transform).pos, -world_sec.get_component(SurfaceComponent).size // 2, world_sec.get_component(SurfaceComponent).size // 2):
        return
    coords = (pos + g_obj.get_component(SurfaceComponent).size // 2) // block_size

    if coords.x < 0 or coords.y < 0 or coords.x >= World.object.size.x or coords.y >= World.object.size.x:
        return

    else:
        if keys[0]:  # Left click
            selecting(coords)
            selector_info_update()  

def on_tech_click(g_obj: GameObject, keys: tuple[bool, bool, bool], pos: Vector2d, *_):
    if not g_obj.contains_component(TechComponent):
        return
    if keys[0]:
        g_obj.get_component(SelectComponent).select()
        selector_info_update()

def open_techs_window(*_):
    tech_win = GameObject.get_game_object_by_tags("game_screen:techs_window")
    world_sec = GameObject.get_game_object_by_tags("game_screen:world_section")

    world_sec.disable()
    tech_win.enable()

def close_techs_window(*_):
    tech_win = GameObject.get_game_object_by_tags("game_screen:techs_window")
    world_sec = GameObject.get_game_object_by_tags("game_screen:world_section")

    world_sec.enable()
    tech_win.disable()
    
def init_world():
    world_size = World.object.size
    world_obj = GameObject.get_group_by_tag("game_screen:world_section")[0]
    world_obj.disable()
    world = create_game_object(world_obj, "game_screen:world_section:world", size=world_size * block_size, color=(80, 80, 80), shape=Shape.RECT)
    unit_layer = create_game_object(world, "game_screen:world_section:world:unit_layer", size=world_size * block_size, shape=Shape.RECT, layer=3)
    city_layer = create_game_object(world, "game_screen:world_section:world:city_layer", size=world_size * block_size, shape=Shape.RECT, layer=2)
    ui_lauer = create_game_object(world, "game_screen:world_section:world:ui_layer", size=world_size * block_size, shape=Shape.RECT, layer=4)
    ui_lauer.add_component(OnClickComponent([1, 0, 1], 0, 1, on_world_click))
    def bind_keys(g_obj: GameObject, keys: list[int], *_):
        world_obj = GameObject.get_game_object_by_tags("game_screen:world_section")
        current_pos = g_obj.get_component(Transform).pos
                
        world_width = world_size.x * block_size.x + block_size.x // 2
        world_height = world_size.y * block_size.y + block_size.y // 2
        
        view_width = world_obj.get_component(SurfaceComponent).size.x
        view_height = world_obj.get_component(SurfaceComponent).size.y
        
        max_x = (world_width - view_width) / 2
        max_y = (world_height - view_height) / 2
        
        if pg.K_w in keys and current_pos.y < max_y:
            g_obj.get_component(Transform).move(Vector2d(0, 40) * block_size // 100)
        if pg.K_a in keys and current_pos.x < max_x:
            g_obj.get_component(Transform).move(Vector2d(40, 0) * block_size // 100)
        if pg.K_s in keys and current_pos.y > -max_y:
            g_obj.get_component(Transform).move(Vector2d(0, -40) * block_size // 100)
        if pg.K_d in keys and current_pos.x > -max_x:
            g_obj.get_component(Transform).move(Vector2d(-40, 0) * block_size // 100)
    world.add_component(KeyBindComponent([pg.K_w, pg.K_a, pg.K_s, pg.K_d], 1, 1, bind_keys))
    world_obj.enable()

def update_tile(tiles: list[Tile]):
    while len(tiles) > 0:
        create_tile_game_object(tiles.pop(0).pos)
    selector_info_update()

def update_unit(units: list[Unit]):
    for unit in units:
        if unit.health <= 0:
            remove_unit_game_object(unit)
    for unit in units:
        if unit.health <= 0:
            continue
        if unit.previous_pos == Vector2d(-1, -1): 
            create_unit_game_object(unit)
        else:
            move_unit_game_object(unit.previous_pos.as_tuple(), unit)
    selector_info_update()

def update_city(cities: list[City]):
    if len(cities) == 0:
        return
    if len(GameObject.get_group_by_tag("game_screen:world_section:world:city_layer:city")) == 0:
        world = GameObject.get_game_object_by_tags("game_screen:world_section:world")
        world.get_component(Transform).set_pos(world.get_component(SurfaceComponent).size // 2 - cities[0].pos * block_size)
    for city in cities:
        create_city_game_object(city)
    selector_info_update()

def update_player(player: Player):
    money_label = GameObject.get_group_by_tag("game_screen:info_section:money_label")[0]
    money_label.get_component(LabelComponent).text = f"Money: {player.money}"
    money_label.need_draw_set_true()
    money_label.need_blit_set_true()
    update_fog_of_war()
    selector_info_update()

def end_turn():
    now_playing_label = GameObject.get_game_object_by_tags("game_screen:info_section:now_playing_label")
    now_playing_label.destroy()
    screen_size = GameObject.get_game_object_by_tags("game_screen").get_component(SurfaceComponent).size
    info_section = GameObject.get_game_object_by_tags("game_screen:info_section")
    now_playing_label = create_label_block(
        parent=info_section, 
        tags="game_screen:info_section:now_playing_label", 
        text=f"Now playing:\n{Replay.obj.game.now_playing_player_index}", 
        font=pg.font.SysFont("consolas", screen_size.y // 40), 
        at=InGrid((2, 8), (1, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )

def start():
    scene=GameObject.get_game_object_by_tags("game_screen")
    tech_win = GameObject.get_game_object_by_tags("game_screen:techs_window")

    scene.enable()
    tech_win.disable()

if __name__ == "__main__":
    load()
