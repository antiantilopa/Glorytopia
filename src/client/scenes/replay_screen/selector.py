from typing import Callable
from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from client.widgets.select import SelectComponent
from client.globals.window_size import WindowSize
from shared import *
import pygame as pg

from shared.util.position import Pos

from . import components
# from . import game_classes
from . import ui
from . import replay

def select(coords: Pos):
    for unit in replay.Replay.units:
        if unit.udata.pos == coords:
            if unit.obj.get_component(SelectComponent).is_selected:
                unit.obj.get_component(SelectComponent).deselect()
                break
            else:
                unit.obj.get_component(SelectComponent).select()
                return
            
    for tile in replay.Replay.tiles:
        if tile.tdata.pos == coords:
            if tile.obj.get_component(SelectComponent).is_selected:
                tile.obj.get_component(SelectComponent).deselect()
                break
            else:
                tile.obj.get_component(SelectComponent).select()
                return

def selector_info_update():
    selector_info_section = GameObject.get_game_object_by_tags("replay_screen:info_section:selector_section:selector_info_section")
    selector_image_section = GameObject.get_game_object_by_tags("replay_screen:info_section:selector_section:selector_image_section")

    while len(selector_info_section.childs) != 0:
        selector_info_section.childs[0].destroy()

    while len(selector_image_section.childs) != 0:
        selector_image_section.childs[0].destroy()

    selector_image_section.need_draw = True
    selector_info_section.need_draw = True

    if SelectComponent.selected is None:
        return

    # default
    buttons = []
    text = ""
    
    if SelectComponent.selected.contains_component(components.TileComponent):
        text, buttons = _selected_tile()
    elif SelectComponent.selected.contains_component(components.UnitComponent):
        text, buttons = _selected_unit()
    elif SelectComponent.selected.contains_component(components.TechComponent):
        text, buttons = _selected_tech()
        
    create_selector_objects(selector_info_section, text, buttons)

def create_selector_objects(selector_info_section: GameObject, text: str, buttons: list[tuple[str, Callable]]):
    create_label_block(
        parent=selector_info_section, 
        tags="replay_screen:info_section:selector_section:selector_info_section:label_block", 
        text=text, 
        font=pg.font.SysFont("consolas", WindowSize.get_block_size().inty() // 5),  
        at=Position.LEFT_UP, 
        text_pos=Position.LEFT, 
        color=ColorComponent.RED
    )
    selector_info_buttons_section = create_list_game_object(selector_info_section, bound=1, at=InGrid((1, 5), (0, 2), (1, 3)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4), tags="replay_screen:info_section:selector_section:selector_info_section:buttons_section")

    for i in range(len(buttons)):
        button_sec = create_game_object(selector_info_buttons_section, at=InGrid((1, 5), (0, i), (1, 1)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4), tags="replay_screen:info_section:selector_section:selector_info_section:buttons_section:button_section")
        button = create_game_object(button_sec, at=InGrid((10, 1), (0, 0), (1, 1)), color=ColorComponent.GREEN, shape=Shape.RECT, tags="replay_screen:info_section:selector_section:selector_info_section:buttons_section:button_section:button")
        button.add_component(OnClickComponent((1, 0, 0), 0, 1, buttons[i][1], (buttons[i][2] if len(buttons[i]) > 2 else ())))
        create_label(
            parent=button_sec, 
            text=buttons[i][0], 
            font=pg.font.SysFont("consolas", WindowSize.get_block_size().inty() // 5), 
            at=InGrid((10, 1), (1, 0), (9, 1)), 
            margin=Vector2d(5, 0), 
            color=ColorComponent.RED, 
            tags="replay_screen:info_section:selector_section:selector_info_section:buttons_section:button_sec:label"
        )

def _selected_tile():
    selector_image_section = GameObject.get_game_object_by_tags("replay_screen:info_section:selector_section:selector_image_section")
    tile_data = SelectComponent.selected.get_component(components.TileComponent).tile_data

    img = create_game_object(selector_image_section, tags="replay_screen:info_section:selector_section:selector_image_section:tile_image", at=InGrid((1, 1), (0, 0)), layer=0)
    img.add_component(SpriteComponent(nickname=tile_data.ttype.name, size=WindowSize.get_block_size()))
    
    is_there_city = False
    city_data = None

    buttons = []
    text = ""

    if tile_data.resource is not None:
        r_img = create_game_object(
            parent=selector_image_section, 
            tags="replay_screen:info_section:selector_section:selector_image_section:resource_image", 
            at=InGrid((1, 1), (0, 0)), 
            layer=1
        )
        r_img.add_component(SpriteComponent(nickname=tile_data.resource.name, size=WindowSize.get_block_size()))
    if tile_data.building is not None:
        r_img = create_game_object(
            parent=selector_image_section, 
            tags="replay_screen:info_section:selector_section:selector_image_section:building_image", 
            at=InGrid((1, 1), (0, 0)), 
            layer=1
        )
        if tile_data.building.adjacent_bonus == None:
            r_img.add_component(SpriteComponent(nickname=tile_data.building.name, size=WindowSize.get_block_size()))
        else:
            r_img.add_component(SpriteComponent(nickname=tile_data.building.name, size=WindowSize.get_block_size(), frame=0, frames_number=8, frame_direction=Vector2d(0, 1)))
    if (tile_data.resource is None) and (tile_data.building is None):
        for city in replay.Replay.cities:
            if city.cdata.pos == tile_data.pos:
                r_img = create_game_object(
                    parent=selector_image_section, 
                    tags="replay_screen:info_section:selector_section:selector_image_section:city_image", 
                    at=InGrid((1, 1), (0, 0)), 
                    layer=1
                )
                r_img.add_component(SpriteComponent(nickname="city", size=WindowSize.get_block_size()))
                is_there_city = True
                city_data = city.cdata
                break
    
    if not is_there_city:
        text = "\n".join((
            f"type: {tile_data.ttype.name}", 
            f"owner: {replay.Replay.get_player_data_by_id(tile_data.owner).nickname if tile_data.owner != -1 else None}", 
            f"resorce: {tile_data.resource.name if tile_data.resource is not None else None}", 
            f"building: {tile_data.building.name if tile_data.building is not None else None}",
            f"pos: {tile_data.pos}", 
        ))

    else:
        text = "\n".join((
            f"city: {city_data.name}",
            f"owner: {replay.Replay.get_player_data_by_id(city_data.owner).nickname if city_data.owner != -1 else None}", 
            f"level: {city_data.level}",
            f"population: {city_data.population}/{city_data.level + 1}",
            f"fullness: {city_data.fullness}/{city_data.level + 1}",
            f"income: +{city_data.level + city_data.is_capital + city_data.forge}",
            f"pos: {city_data.pos}",
            f"Capital" if city_data.is_capital else ""
        ))
    return text, buttons

def _selected_unit():
    selector_image_section = GameObject.get_game_object_by_tags("replay_screen:info_section:selector_section:selector_image_section")
    unit_data = SelectComponent.selected.get_component(components.UnitComponent).unit_data
    buttons = []

    img = create_game_object(
        parent=selector_image_section, 
        tags="replay_screen:info_section:selector_section:selector_image_section:image", 
        at=InGrid((1, 1), (0, 0))
    )
    img.add_component(SpriteComponent(nickname=unit_data.utype.name, size=WindowSize.get_block_size()))


    if unit_data.attached_city_id == -1:
        attached_city_name = "(bug!)"
    else:
        attached_city_name = "None"
        for city in replay.Replay.cities:
            if city.cdata._id == unit_data.attached_city_id:
                attached_city_name = city.cdata.name
                break

    text = "\n".join((
        f"type: {unit_data.utype.name}",
        f"owner: {replay.Replay.get_player_data_by_id(unit_data.owner).nickname if unit_data.owner != -1 else None}", 
        f"health: {unit_data.health}",
        f"can_move?: {"no" if unit_data.moved else "yes"}",
        f"can_attack?: {"no" if unit_data.attacked else "yes"}",
        f"pos: {unit_data.pos}",
        f"attached_city: {attached_city_name}"
    ))
    return text, buttons

def _selected_tech():
    selector_image_section = GameObject.get_game_object_by_tags("replay_screen:info_section:selector_section:selector_image_section")
    buttons = []
    text = ""

    tech = SelectComponent.selected.get_component(components.TechComponent).tech

    img = create_game_object(selector_image_section, "replay_screen:info_section:selector_section:selector_image_section:image", at=InGrid((1, 1), (0, 0)))
    img.add_component(SpriteComponent(nickname=tech.name, size=WindowSize.get_block_size()))

    my_cities_count = 0
    for city in replay.Replay.cities:
        if city.cdata.owner != -1 and city.cdata.owner == replay.Replay.watch_as:
            my_cities_count += 1
    text = "\n".join((
        f"name: {tech.name}    " + (f"owned" if tech in replay.Replay.get_player_by_id(replay.Replay.watch_as).techs else "not owned"),
        f"cost: {tech.cost + tech.tier * my_cities_count}    " + f"tier: {tech.tier}",
        (f"buildings: {', '.join([b.name for b in tech.buildings])}\n" if len(tech.buildings) > 0 else "") +
        (f"units: {', '.join([u.name for u in tech.units])}\n" if len(tech.units) > 0 else "") +
        (f"resources: {', '.join([r.name for r in tech.harvestables])}\n" if len(tech.harvestables) > 0 else "") +
        (f"terrain: {', '.join([t.name for t in tech.accessable])}\n" if len(tech.accessable) > 0 else "") + 
        (f"defecnces: {', '.join([t.name for t in tech.defence])}\n" if len(tech.defence) > 0 else "") + 
        (f"terraforms: {', '.join([t.name for t in tech.terraforms])}\n" if len(tech.terraforms) > 0 else "") + 
        (f"achievements: {', '.join([a for a in tech.achievements])}\n" if len(tech.achievements) > 0 else "")
    ))

    return text, buttons