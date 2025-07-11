from engine_antiantilopa import *
from client.respondings.client import Client
from client.globals.settings import Settings
from client.respondings.lobby import respond, UpdateCodes
from client.widgets.fastgameobjectcreator import *
from client.widgets.game_objects_for_game_elements import *
from client.widgets.texture_load import load_textures
from client.widgets.select import SelectComponent
from serializator.data_format import Format
from shared import *
import pygame as pg
from copy import deepcopy

block_size = Vector2d(100, 100)

def load(screen_size: Vector2d = Vector2d(1200, 800)) -> GameObject:
    global block_size
    load_textures(Settings.texture_packs.order)

    scene = create_game_object(tags="game_screen", size=screen_size)

    block_size = screen_size // Vector2d(12, 8)
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

    money_label = create_label(info_section, tags="game_screen:info_section:money_label", text=f"Money: {Client.object.money}", font=pg.font.SysFont("consolas", screen_size.y // 40), at=InGrid((2, 8), (0, 0), (1, 1)), color=ColorComponent.WHITE)

    selector_section = create_game_object(info_section, at=InGrid((1, 8), (0, 1), (1, 5)), shape=Shape.RECTBORDER, color=ColorComponent.WHITE, width=2, margin=Vector2d(5, 0), tags="game_screen:info_section:selector_section")
    selector_image_section = create_game_object(selector_section, at=InGrid((4, 5), (0, 0), (1, 1)), surface_margin=Vector2d(7, 2), tags="game_screen:info_section:selector_section:selector_image_section")
    selector_info_section = create_game_object(selector_section, at=InGrid((4, 5), (0, 1), (4, 4)), surface_margin=Vector2d(7, 2), tags="game_screen:info_section:selector_section:selector_info_section")
    
    end_turn_button = create_game_object(info_section, "game_screen:info_section:end_turn_button", at=InGrid((1, 8), (0, 7), (1, 1)), color=(50, 150, 50) if Client.object.order[0] == Client.object.myname else (30, 100, 30), shape=Shape.RECT)
    end_turn_label = create_label(end_turn_button, "game_screen:info_section:end_turn_label", text="End Turn", font=pg.font.SysFont("consolas", screen_size.y // 40), at=InGrid((1, 1), (0, 0), (1, 1)), color=ColorComponent.WHITE)
    end_turn_button.add_component(OnClickComponent([1, 0, 0], 0, 1, end_turn_click))
    now_playing_label = create_label_block(info_section, "game_screen:info_section:now_playing_label", text=f"Now playing:\n{Client.object.order[Client.object.now_playing]}", font=pg.font.SysFont("consolas", screen_size.y // 40), at=InGrid((2, 8), (1, 0), (1, 1)), color=ColorComponent.WHITE)

    techs_button = create_game_object(info_section, "game_screen:info_section:techs_button", at=InGrid((1, 8), (0, 6), (1, 1)), color=(0, 150, 250), shape=Shape.RECT)
    techs_label = create_label(techs_button, "game_screen:info_section:end_turn_label", text="Technology", font=pg.font.SysFont("consolas", screen_size.y // 40), at=InGrid((1, 1), (0, 0), (1, 1)), color=ColorComponent.WHITE)
    techs_button.add_component(OnClickComponent([1, 0, 0], 0, 1, open_techs_window))


    return scene

def reset_ui(*_):
    self = Client.object

    world = GameObject.get_game_object_by_tags("game_screen:world_section:world")
    while len(world.childs) != 0:
        world.childs[0].destroy()

    unit_layer = create_game_object(world, "game_screen:world_section:world:unit_layer", size=Vector2d.from_tuple(self.world_size) * block_size, shape=Shape.RECT, layer=3)
    city_layer = create_game_object(world, "game_screen:world_section:world:city_layer", size=Vector2d.from_tuple(self.world_size) * block_size, shape=Shape.RECT, layer=2)
    ui_lauer = create_game_object(world, "game_screen:world_section:world:ui_layer", size=Vector2d.from_tuple(self.world_size) * block_size, shape=Shape.RECT, layer=4)
    ui_lauer.add_component(OnClickComponent([1, 0, 1], 0, 1, on_world_click))
    ui_lauer.add_component(KeyBindComponent([pg.K_r], 0, 1, reset_ui))

    for x in range(Client.object.world_size[0]):
        for y in range(Client.object.world_size[1]):
            if Client.object.world[y][x] is not None:
                create_tile_game_object((x, y))
     
    for city_data in Client.object.cities:
        create_city_game_object(city_data)
    
    i = 0
    while i < len(Client.object.units):
        if Client.object.units[i].health <= 0:
            Client.object.units.pop(i)
        else:
            i += 1

    for unit_data in Client.object.units:
        if unit_data.health > 0:
            create_unit_game_object(unit_data)
        else:
            print("WTF! Unit with health <= 0 found in Client.object.units. It should not be there.")

def selecting(coords: Vector2d):
    self = Client.object
    if self.world[coords.inty()][coords.intx()] is None:
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
            for city in Client.object.cities:
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
                f"owner: {Client.object.order[tile_data.owner] if tile_data.owner != -1 else None}", 
                f"resorce: {tile_data.resource.name if tile_data.resource is not None else None}", 
                f"building: {tile_data.building.name if tile_data.building is not None else None}",
                f"pos: {tile_data.pos}", 
            ))
            if tile_data.owner != -1 and Client.object.myname == Client.object.order[tile_data.owner]:
                if tile_data.resource is not None:
                    for tech in Client.object.techs:
                        if tile_data.resource in tech.harvestables:
                            buttons.append(("harvest:2", lambda *_: Client.object.send(Format.event("GAME/HARVEST", [tile_data.pos.as_tuple()]))))
                if tile_data.building is None:
                    for tech in Client.object.techs:
                        for btype in tech.buildings:
                            print(btype.required_resource)
                            print(tile_data.resource)
                            if (tile_data.ttype in btype.ttypes) and ((btype.required_resource is None) or (btype.required_resource == tile_data.resource)):
                                buttons.append((f"{btype.name}:{btype.cost}", lambda g, k, p, *args: Client.object.send(Format.event("GAME/BUILD", [tile_data.pos.as_tuple(), args[0]])), btype.id))
        else:
            text = "\n".join((
                f"city: {city_data.name}",
                f"owner: {Client.object.order[city_data.owner] if city_data.owner != -1 else None}", 
                f"level: {city_data.level}",
                f"population: {city_data.population}/{city_data.level + 1}",
                f"fullness: {city_data.fullness}/{city_data.level + 1}",
                f"income: +{city_data.level + city_data.is_capital + city_data.forge}",
                f"pos: {city_data.pos}",
                f"Capital" if city_data.is_capital else ""
            ))
            if city_data.owner != -1 and Client.object.myname == Client.object.order[city_data.owner]:
                found = 0
                for unit_data in Client.object.units:
                    if unit_data.pos == city_data.pos:
                        found = 1
                        break
                if city_data.fullness != city_data.level + 1 and not found:
                    for tech in Client.object.techs:
                        for utype in tech.units:
                            buttons.append((f"{utype.name}:{utype.cost}", lambda g, p, k, *args: Client.object.send(Format.event("GAME/CREATE_UNIT", [city_data.pos.as_tuple(), args[0]])), utype.id))
    elif SelectComponent.selected.contains_component(UnitComponent):
        unit_data = SelectComponent.selected.get_component(UnitComponent).unit_data

        img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:image", at=InGrid((1, 1), (0, 0)))
        img.add_component(SpriteComponent(nickname=unit_data.utype.name, size=block_size))
        
        text = "\n".join((
            f"type: {unit_data.utype.name}",
            f"owner: {Client.object.order[unit_data.owner] if unit_data.owner != -1 else None}", 
            f"health: {unit_data.health}",
            f"can_move?: {"no" if unit_data.moved else "yes"}",
            f"can_attack?: {"no" if unit_data.attacked else "yes"}",
            f"pos: {unit_data.pos}",
        ))
        if not (unit_data.moved or unit_data.attacked):
            city_found = False
            for city in Client.object.cities:
                if city.pos == unit_data.pos:
                    if city.owner == unit_data.owner:
                        break
                    else:
                        city_found = True
                        break
            if city_found:
                buttons.append(("Conquer city", lambda *_: Client.object.send(Format.event("GAME/CONQUER_CITY", [unit_data.pos.as_tuple()]))))
    elif SelectComponent.selected.contains_component(TechComponent):
        tech = SelectComponent.selected.get_component(TechComponent).tech

        img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:image", at=InGrid((1, 1), (0, 0)))
        img.add_component(SpriteComponent(nickname=tech.name, size=block_size))

        my_cities_count = 0
        for city in Client.object.cities:
            if city.owner != -1 and Client.object.myname == Client.object.order[city.owner]:
                my_cities_count += 1
        text = "\n".join((
            f"name: {tech.name}    " + (f"owned" if tech in Client.object.techs else "not owned"),
            f"cost: {tech.cost + tech.tier * my_cities_count}    " + f"tier: {tech.tier}",
            (f"buildings: {', '.join([b.name for b in tech.buildings])}\n" if len(tech.buildings) > 0 else "") +
            (f"units: {', '.join([u.name for u in tech.units])}\n" if len(tech.units) > 0 else "") +
            (f"resources: {', '.join([r.name for r in tech.harvestables])}\n" if len(tech.harvestables) > 0 else "") +
            (f"terrain: {', '.join([t.name for t in tech.accessable])}\n" if len(tech.accessable) > 0 else "") + 
            (f"defecnces: {', '.join([t.name for t in tech.defence])}\n" if len(tech.defence) > 0 else "") + 
            (f"achievements: {', '.join([a for a in tech.achievements])}\n" if len(tech.achievements) > 0 else "")
        ))
        if (tech.parent is not None) and (tech.parent in Client.object.techs) and (tech not in Client.object.techs):
            buttons.append((f"buy:{tech.cost + tech.tier * my_cities_count}", lambda *_: Client.object.send(Format.event("GAME/BUY_TECH", [tech.id]))))
    create_label_block(selector_info_section, "game_screen:info_section:selector_section:selector_info_section:label_block", text, font=pg.font.SysFont("consolas", block_size.y // 5),  at=Position.LEFT_UP, text_pos=Position.LEFT, color=ColorComponent.RED)
    selector_info_buttons_section = create_list_game_object(selector_info_section, bound=1, at=InGrid((1, 5), (0, 2), (1, 3)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4), tags="game_screen:info_section:selector_section:selector_info_section:buttons_section")

    for i in range(len(buttons)):
        button_sec = create_game_object(selector_info_buttons_section, at=InGrid((1, 5), (0, i), (1, 1)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4), tags="game_screen:info_section:selector_section:selector_info_section:buttons_section:button_section")
        button = create_game_object(button_sec, at=InGrid((10, 1), (0, 0), (1, 1)), color=ColorComponent.GREEN, shape=Shape.RECT, tags="game_screen:info_section:selector_section:selector_info_section:buttons_section:button_section:button")
        button.add_component(OnClickComponent((1, 0, 0), 0, 1, buttons[i][1], (buttons[i][2] if len(buttons[i]) > 2 else ())))
        create_label(button_sec, text=buttons[i][0], font=pg.font.SysFont("consolas", block_size.y // 5), at=InGrid((10, 1), (1, 0), (9, 1)), margin=Vector2d(5, 0), color=ColorComponent.RED, tags="game_screen:info_section:selector_section:selector_info_section:buttons_section:button_sec:label")

def on_world_click(g_obj: GameObject, keys: tuple[bool, bool, bool], pos: Vector2d, *_):
    
    world_sec = GameObject.get_game_object_by_tags("game_screen:world_section")
    world = GameObject.get_game_object_by_tags("game_screen:world_section:world")

    if not Vector2d.is_in_box(pos + world.get_component(Transform).pos, -world_sec.get_component(SurfaceComponent).size // 2, world_sec.get_component(SurfaceComponent).size // 2):
        return
    coords = (pos + g_obj.get_component(SurfaceComponent).size // 2) // block_size

    if coords.x < 0 or coords.y < 0 or coords.x >= Client.object.world_size[0] or coords.y >= Client.object.world_size[1]:
        return

    else:
        if keys[0]:  # Left click
            selecting(coords)
            selector_info_update()  
        elif keys[2]:  # Right click
            if SelectComponent.selected is None:
                return
            if not SelectComponent.selected.contains_component(UnitComponent):
                return
            Client.object.send(Format.event("GAME/MOVE_UNIT", [SelectComponent.selected.get_component(UnitComponent).unit_data.pos.as_tuple(), coords.as_tuple()]))

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

def end_turn_click(g_obj: GameObject, keys: list[int], pos: Vector2d, *_):
    Client.object.send(Format.event("GAME/END_TURN", ()))
    g_obj.get_component(ColorComponent).color = (30, 100, 30)
    g_obj.need_draw_set_true()
    g_obj.need_blit_set_true()
    
def init():

    @Client.object.check_update(UpdateCodes.INIT_WORLD)
    def init_world():
        self = Client.object
        world_obj = GameObject.get_group_by_tag("game_screen:world_section")[0]
        world_obj.disable()
        world = create_game_object(world_obj, "game_screen:world_section:world", size=Vector2d.from_tuple(self.world_size) * block_size, color=(80, 80, 80), shape=Shape.RECT)
        unit_layer = create_game_object(world, "game_screen:world_section:world:unit_layer", size=Vector2d.from_tuple(self.world_size) * block_size, shape=Shape.RECT, layer=3)
        city_layer = create_game_object(world, "game_screen:world_section:world:city_layer", size=Vector2d.from_tuple(self.world_size) * block_size, shape=Shape.RECT, layer=2)
        ui_lauer = create_game_object(world, "game_screen:world_section:world:ui_layer", size=Vector2d.from_tuple(self.world_size) * block_size, shape=Shape.RECT, layer=4)
        ui_lauer.add_component(OnClickComponent([1, 0, 1], 0, 1, on_world_click))
        ui_lauer.add_component(KeyBindComponent([pg.K_r], 0, 1, reset_ui))
        def bind_keys(g_obj: GameObject, keys: list[int], *_):
            world_obj = GameObject.get_game_object_by_tags("game_screen:world_section")
            current_pos = g_obj.get_component(Transform).pos
                    
            world_width = self.world_size[0] * block_size.x
            world_height = self.world_size[1] * block_size.y
            
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

    @Client.object.check_update(UpdateCodes.UPDATE_TILE)
    def update_tile():
        self = Client.object
        for pos in self.world_updates:
            create_tile_game_object(pos)
        self.world_updates.clear()
        selector_info_update()

    @Client.object.check_update(UpdateCodes.UPDATE_UNIT)
    def update_unit():
        self = Client.object
        for unit_change in self.units_updates:
            if len(unit_change[0]) == 0: 
                create_unit_game_object(unit_change[1])
            elif (not isinstance(unit_change[1], UnitData)) or unit_change[1].health <= 0:
                remove_unit_game_object(unit_change[0])
            else:
                move_unit_game_object(unit_change[0], unit_change[1])
        self.units_updates.clear()
        selector_info_update()

    @Client.object.check_update(UpdateCodes.UPDATE_CITY)
    def update_city():
        self = Client.object
        for city in self.cities_updates:
            create_city_game_object(city)
        self.cities_updates.clear()
        selector_info_update()

    @Client.object.check_update(UpdateCodes.UPDATE_MONEY)
    def update_money():
        self = Client.object
        money_label = GameObject.get_group_by_tag("game_screen:info_section:money_label")[0]
        money_label.get_component(LabelComponent).text = f"Money: {self.money}"
        money_label.need_draw_set_true()
        money_label.need_blit_set_true()

    @Client.object.check_update(UpdateCodes.UPDATE_TECH)
    def update_tech():
        selector_info_update()

    @Client.object.check_update(UpdateCodes.END_TURN)
    def end_turn():
        self = Client.object
        if self.order[self.now_playing] == self.myname:
            end_turn_button = GameObject.get_group_by_tag("game_screen:info_section:end_turn_button")[0]
            end_turn_button.get_component(ColorComponent).color = (50, 150, 50)
            end_turn_button.need_draw_set_true()
            end_turn_button.need_blit_set_true()

        now_playing_label = GameObject.get_game_object_by_tags("game_screen:info_section:now_playing_label")
        now_playing_label.destroy()
        screen_size = GameObject.get_game_object_by_tags("game_screen").get_component(SurfaceComponent).size
        info_section = GameObject.get_game_object_by_tags("game_screen:info_section")
        now_playing_label = create_label_block(info_section, "game_screen:info_section:now_playing_label", text=f"Now playing:\n{Client.object.order[Client.object.now_playing]}", font=pg.font.SysFont("consolas", screen_size.y // 40), at=InGrid((2, 8), (1, 0), (1, 1)), color=ColorComponent.WHITE)

    @Client.object.change_main_cycle
    def update(self: Client):
        if not self.game_started:
            raise RuntimeError("Game has not started yet!")
        
        while not self.changing_main_cycle:
            Client.object.check_updates()
            
def start():
    scene=GameObject.get_game_object_by_tags("game_screen")
    tech_win = GameObject.get_game_object_by_tags("game_screen:techs_window")

    scene.enable()
    tech_win.disable()

if __name__ == "__main__":
    load()
