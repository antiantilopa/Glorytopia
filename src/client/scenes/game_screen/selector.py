from typing import Callable
from engine_antiantilopa import *
from client.network.client import GameClient, GamePlayer
from client.widgets.fastgameobjectcreator import *
from client.widgets.select import SelectComponent
from client.globals.window_size import WindowSize
from shared import *
import pygame as pg

from shared.util.position import Pos

from . import components
from . import game_classes
from . import ui

def select(coords: Pos):
    if game_classes.GameRules.get_tile(coords) is None:
        return
    
    for unit in game_classes.Unit.units:
        if unit.pos == coords:
            if unit.obj.get_component(SelectComponent).is_selected:
                unit.obj.get_component(SelectComponent).deselect()
                break
            else:
                unit.obj.get_component(SelectComponent).select()
                return
            
    for tile in game_classes.Tile.tiles:
        if tile.pos == coords:
            if tile.obj.get_component(SelectComponent).is_selected:
                tile.obj.get_component(SelectComponent).deselect()
                break
            else:
                tile.obj.get_component(SelectComponent).select()
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
        tags="game_screen:info_section:selector_section:selector_info_section:label_block", 
        text=text, 
        font=pg.font.SysFont("consolas", WindowSize.get_block_size().inty() // 5),  
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
            font=pg.font.SysFont("consolas", WindowSize.get_block_size().inty() // 5), 
            at=InGrid((10, 1), (1, 0), (9, 1)), 
            margin=Vector2d(5, 0), 
            color=ColorComponent.RED, 
            tags="game_screen:info_section:selector_section:selector_info_section:buttons_section:button_sec:label"
        )

def _selected_tile():
    selector_image_section = GameObject.get_game_object_by_tags("game_screen:info_section:selector_section:selector_image_section")
    tile_data = SelectComponent.selected.get_component(components.TileComponent).tile_data

    img = create_game_object(selector_image_section, tags="game_screen:info_section:selector_section:selector_image_section:tile_image", at=InGrid((1, 1), (0, 0)), layer=0)
    img.add_component(SpriteComponent(nickname=tile_data.ttype.name, size=WindowSize.get_block_size()))
    
    is_there_city = False
    city_data = None

    buttons = []
    text = ""

    if tile_data.resource is not None:
        r_img = create_game_object(
            parent=selector_image_section, 
            tags="game_screen:info_section:selector_section:selector_image_section:resource_image", 
            at=InGrid((1, 1), (0, 0)), 
            layer=1
        )
        r_img.add_component(SpriteComponent(nickname=tile_data.resource.name, size=WindowSize.get_block_size()))
    if tile_data.building is not None:
        r_img = create_game_object(
            parent=selector_image_section, 
            tags="game_screen:info_section:selector_section:selector_image_section:building_image", 
            at=InGrid((1, 1), (0, 0)), 
            layer=1
        )
        if tile_data.building.adjacent_bonus == None:
            r_img.add_component(SpriteComponent(nickname=tile_data.building.name, size=WindowSize.get_block_size()))
        else:
            r_img.add_component(SpriteComponent(nickname=tile_data.building.name, size=WindowSize.get_block_size(), frame=0, frames_number=8, frame_direction=Vector2d(0, 1)))
    if (tile_data.resource is None) and (tile_data.building is None):
        for city in game_classes.City.cities:
            if city.pos == tile_data.pos:
                r_img = create_game_object(
                    parent=selector_image_section, 
                    tags="game_screen:info_section:selector_section:selector_image_section:city_image", 
                    at=InGrid((1, 1), (0, 0)), 
                    layer=1
                )
                r_img.add_component(SpriteComponent(nickname="city", size=WindowSize.get_block_size()))
                is_there_city = True
                city_data = city
                break
    
    if not is_there_city:
        text = "\n".join((
            f"type: {tile_data.ttype.name}", 
            f"owner: {GamePlayer.by_id(tile_data.owner).nickname if tile_data.owner != -1 else None}", 
            f"resorce: {tile_data.resource.name if tile_data.resource is not None else None}", 
            f"building: {tile_data.building.name if tile_data.building is not None else None}",
            f"pos: {tile_data.pos}", 
        ))
        if tile_data.owner == GameClient.object.me.id:
            if tile_data.resource is not None:
                for tech in GameClient.object.me.techs:
                    if tile_data.resource in tech.harvestables:
                        buttons.append(("harvest:2", lambda*_: ui.click_harvest(tile_data.pos)))
            if tile_data.building is None:
                for tech in GameClient.object.me.techs:
                    for btype in tech.buildings:
                        if (tile_data.ttype in btype.ttypes) and ((btype.required_resource is None) or (btype.required_resource == tile_data.resource)):
                            buttons.append((f"{btype.name}:{btype.cost}", lambda g, k, p, *args: ui.click_build(tile_data.pos, args[0]), btype.id))
                for tech in GameClient.object.me.techs:
                    for terraform in tech.terraforms:
                        if (tile_data.ttype == terraform.from_ttype) and ((terraform.from_resource is None) or (terraform.from_resource == tile_data.resource)):
                            buttons.append((f"{terraform.name}:{terraform.cost}", lambda g, k, p, *args: ui.click_terraform(tile_data.pos, args[0]), terraform.id))
    else:
        text = "\n".join((
            f"city: {city_data.name}",
            f"owner: {GamePlayer.by_id(city_data.owner).nickname if city_data.owner != -1 else None}", 
            f"level: {city_data.level}",
            f"population: {city_data.population}/{city_data.level + 1}",
            f"fullness: {city_data.fullness}/{city_data.level + 1}",
            f"income: +{city_data.level + city_data.is_capital + city_data.forge}",
            f"pos: {city_data.pos}",
            f"Capital" if city_data.is_capital else ""
        ))
        if city_data.owner == GameClient.object.me.id:
            found = 0
            for unit in game_classes.Unit.units:
                if unit.pos == city_data.pos:
                    found = 1
                    break
            if city_data.fullness != city_data.level + 1 and not found:
                for tech in GameClient.object.me.techs:
                    for utype in tech.units:
                        buttons.append((f"{utype.name}:{utype.cost}", lambda g, p, k, *args: ui.click_create_unit(tile_data.pos, args[0]), utype.id))
    return text, buttons

def _selected_unit():
    selector_image_section = GameObject.get_game_object_by_tags("game_screen:info_section:selector_section:selector_image_section")
    unit_data = SelectComponent.selected.get_component(components.UnitComponent).unit_data
    buttons = []

    img = create_game_object(
        parent=selector_image_section, 
        tags="game_screen:info_section:selector_section:selector_image_section:image", 
        at=InGrid((1, 1), (0, 0))
    )
    img.add_component(SpriteComponent(nickname=unit_data.utype.name, size=WindowSize.get_block_size()))
    
    text = "\n".join((
        f"type: {unit_data.utype.name}",
        f"owner: {GamePlayer.by_id(unit_data.owner).nickname if unit_data.owner != -1 else None}", 
        f"health: {unit_data.health}",
        f"can_move?: {"no" if unit_data.moved else "yes"}",
        f"can_attack?: {"no" if unit_data.attacked else "yes"}",
        f"pos: {unit_data.pos}",
    ))
    if not (unit_data.moved or unit_data.attacked):
        city_found = False
        for city in game_classes.City.cities:
            if city.pos == unit_data.pos:
                if city.owner == unit_data.owner:
                    break
                else:
                    city_found = True
                    break
        if city_found:
            buttons.append(("Conquer city", lambda *_: ui.click_conquer_city(unit_data.pos)))

    return text, buttons

def _selected_tech():
    selector_image_section = GameObject.get_game_object_by_tags("game_screen:info_section:selector_section:selector_image_section")
    buttons = []
    text = ""

    tech = SelectComponent.selected.get_component(components.TechComponent).tech

    img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:image", at=InGrid((1, 1), (0, 0)))
    img.add_component(SpriteComponent(nickname=tech.name, size=WindowSize.get_block_size()))

    my_cities_count = 0
    for city in game_classes.City.cities:
        if city.owner != -1 and city.owner == GameClient.object.me.id:
            my_cities_count += 1
    text = "\n".join((
        f"name: {tech.name}    " + (f"owned" if tech in GameClient.object.me.techs else "not owned"),
        f"cost: {tech.cost + tech.tier * my_cities_count}    " + f"tier: {tech.tier}",
        (f"buildings: {', '.join([b.name for b in tech.buildings])}\n" if len(tech.buildings) > 0 else "") +
        (f"units: {', '.join([u.name for u in tech.units])}\n" if len(tech.units) > 0 else "") +
        (f"resources: {', '.join([r.name for r in tech.harvestables])}\n" if len(tech.harvestables) > 0 else "") +
        (f"terrain: {', '.join([t.name for t in tech.accessable])}\n" if len(tech.accessable) > 0 else "") + 
        (f"defecnces: {', '.join([t.name for t in tech.defence])}\n" if len(tech.defence) > 0 else "") + 
        (f"terraforms: {', '.join([t.name for t in tech.terraforms])}\n" if len(tech.terraforms) > 0 else "") + 
        (f"achievements: {', '.join([a for a in tech.achievements])}\n" if len(tech.achievements) > 0 else "")
    ))
    if (tech.parent is not None) and (tech.parent in GameClient.object.me.techs) and (tech not in GameClient.object.me.techs):
        buttons.append((f"buy:{tech.cost + tech.tier * my_cities_count}", lambda *_: ui.click_buy_tech(tech.id)))

    return text, buttons