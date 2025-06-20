from engine_antiantilopa import *
from client.respondings.client import Client
from client.respondings.lobby import respond, UpdateCodes
from client.widgets.fastgameobjectcreator import *
from client.widgets.game_objects_for_game_elements import *
from client.widgets.texture_load import load_textures
from client.widgets.select import SelectComponent
from serializator.data_format import Format
from shared import *
import pygame as pg


def load(screen_size: Vector2d = Vector2d(1200, 800)) -> GameObject:
    scene = create_game_object(tags="game_screen", size=screen_size)

    def deleteme(*_):
        try:
            exec(input())
        except Exception as e:
            print(f"error: {e}")

    create_game_object(scene, "game_screen:world_section", at=InGrid((12, 8), (0, 0), (8, 8)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)

    info_section = create_game_object(scene, "game_screen:info_section", at=InGrid((12, 8), (8, 0), (4, 8)), shape=Shape.RECT)

    money_label = create_label(info_section, tags="game_screen:info_section:money_label", text=f"Money: {Client.object.money}", font=pg.font.SysFont("consolas", screen_size.y // 40), at=InGrid((1, 8), (0, 0), (1, 1)), color=ColorComponent.WHITE)

    selector_section = create_game_object(info_section, at=InGrid((1, 8), (0, 1), (1, 5)), shape=Shape.RECTBORDER, color=ColorComponent.WHITE, width=2, margin=Vector2d(5, 0), tags="game_screen:info_section:selector_section")
    selector_image_section = create_game_object(selector_section, at=InGrid((4, 5), (0, 0), (1, 1)), surface_margin=Vector2d(7, 2), tags="game_screen:info_section:selector_section:selector_image_section")
    selector_info_section = create_game_object(selector_section, at=InGrid((4, 5), (0, 1), (4, 4)), surface_margin=Vector2d(7, 2), tags="game_screen:info_section:selector_section:selector_info_section")
    info_section.add_component(KeyBindComponent([pg.K_q], 0, 1, deleteme))
    
    end_turn_button = create_game_object(info_section, "game_screen:info_section:end_turn_button", at=InGrid((1, 8), (0, 7), (1, 1)), size=(100, 40), color=(50, 150, 50) if Client.object.names[0] == Client.object.myname else (30, 100, 30), shape=Shape.RECT)
    end_turn_label = create_label(end_turn_button, "game_screen:info_section:end_turn_label", text="End Turn", font=pg.font.SysFont("consolas", screen_size.y // 40), at=InGrid((1, 1), (0, 0), (1, 1)), color=ColorComponent.WHITE)
    end_turn_button.add_component(OnClickComponent([1, 0, 0], 0, 1, end_turn_click))

    load_textures()

    return scene

def reset_ui(*_):
    self = Client.object

    world = GameObject.get_game_object_by_tags("game_screen:world_section:world")
    while len(world.childs) != 0:
        world.childs[0].destroy()

    unit_layer = create_game_object(world, "game_screen:world_section:world:unit_layer", size=Vector2d.from_tuple(self.world_size) * 100, shape=Shape.RECT, layer=3)
    city_layer = create_game_object(world, "game_screen:world_section:world:city_layer", size=Vector2d.from_tuple(self.world_size) * 100, shape=Shape.RECT, layer=2)
    ui_lauer = create_game_object(world, "game_screen:world_section:world:ui_layer", size=Vector2d.from_tuple(self.world_size) * 100, shape=Shape.RECT, layer=4)
    ui_lauer.add_component(OnClickComponent([1, 0, 1], 0, 1, on_world_click))
    ui_lauer.add_component(KeyBindComponent([pg.K_r], 0, 1, reset_ui))

    for x in range(Client.object.world_size[0]):
        for y in range(Client.object.world_size[1]):
            if Client.object.world[y][x] is not None:
                create_tile_game_object((x, y))
     
    for city_data in Client.object.cities:
        create_city_game_object(city_data)
    
    for unit_data in Client.object.units:
        create_unit_game_object(unit_data)

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

    selector_image_section.disable()
    selector_info_section.disable()

    while len(selector_info_section.childs) != 0:
        selector_info_section.childs[0].destroy()
    while len(selector_image_section.childs) != 0:
        selector_image_section.childs[0].destroy()

    if SelectComponent.selected is None:
        pass
    elif SelectComponent.selected.contains_component(TileComponent):
        img = create_game_object(selector_image_section, tags="game_screen:info_section:selector_section:selector_image_section:tile_image", at=InGrid((1, 1), (0, 0)), layer=0)
        img.add_component(SpriteComponent(nickname=SelectComponent.selected.get_component(TileComponent).tile_data.ttype.name, size=Vector2d(100, 100)))
        is_there_city = False
        city_data = None
        if SelectComponent.selected.get_component(TileComponent).tile_data.resource is not None:
            r_img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:resource_image", at=InGrid((1, 1), (0, 0)), layer=1)
            r_img.add_component(SpriteComponent(nickname=SelectComponent.selected.get_component(TileComponent).tile_data.resource.name, size=Vector2d(100, 100)))
        elif  SelectComponent.selected.get_component(TileComponent).tile_data.building is not None:
            r_img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:building_image", at=InGrid((1, 1), (0, 0)), layer=1)
            r_img.add_component(SpriteComponent(nickname=SelectComponent.selected.get_component(TileComponent).tile_data.building.name, size=Vector2d(100, 100)))
        else:
            for city in Client.object.cities:
                if city.pos == SelectComponent.selected.get_component(TileComponent).pos:
                    r_img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:city_image", at=InGrid((1, 1), (0, 0)), layer=1)
                    r_img.add_component(SpriteComponent(nickname="city", size=Vector2d(100, 100)))
                    is_there_city = True
                    city_data = city
                    break
        if not is_there_city:
            tile_data = SelectComponent.selected.get_component(TileComponent).tile_data
            text = "\n".join((
                f"type: {tile_data.ttype.name}", 
                f"owner: {Client.object.names[tile_data.owner] if tile_data.owner != -1 else None}", 
                f"resorce: {tile_data.resource.name if tile_data.resource is not None else None}", 
                f"building: {tile_data.building.name if tile_data.building is not None else None}",
                f"pos: {tile_data.pos}", 
            ))
            create_label_block(selector_info_section, "game_screen:info_section:selector_section:selector_info_section:label_block", text, font=pg.font.SysFont("consolas", 20),  at=Position.LEFT_UP, text_pos=Position.LEFT, color=ColorComponent.RED)
        else:
            text = "\n".join((
                f"city: {city_data.name}",
                f"owner: {Client.object.names[city_data.owner] if city_data.owner != -1 else None}", 
                f"level: {city_data.level}",
                f"population: {city_data.population}/{city_data.level + 1}",
                f"fullness: {city_data.fullness}",
                f"income: +{city_data.level + city_data.is_capital + city_data.forge}",
                f"pos: {city_data.pos}",
                f"Capital" if city_data.is_capital else ""
            ))
            create_label_block(selector_info_section, "game_screen:info_section:selector_section:selector_info_section:label_block", text, font=pg.font.SysFont("consolas", 20),  at=Position.LEFT_UP, text_pos=Position.LEFT, color=ColorComponent.RED)

    elif SelectComponent.selected.contains_component(UnitComponent):
        unit_data = SelectComponent.selected.get_component(UnitComponent).unit_data

        img = create_game_object(selector_image_section, "game_screen:info_section:selector_section:selector_image_section:image", at=InGrid((1, 1), (0, 0)))
        img.add_component(SpriteComponent(nickname=unit_data.utype.name, size=Vector2d(100, 100)))
        
        text = "\n".join((
            f"type: {unit_data.utype.name}",
            f"owner: {Client.object.names[unit_data.owner] if unit_data.owner != -1 else None}", 
            f"health: {unit_data.health}",
            f"can_move?: {"no" if unit_data.moved else "yes"}",
            f"can_attack?: {"no" if unit_data.attacked else "yes"}",
            f"pos: {unit_data.pos}",
        ))
        create_label_block(selector_info_section, "game_screen:info_section:selector_section:selector_info_section:label_block", text, font=pg.font.SysFont("consolas", 20),  at=Position.LEFT_UP, text_pos=Position.LEFT, color=ColorComponent.RED)


    selector_image_section.enable()
    selector_info_section.enable()


def on_world_click(g_obj: GameObject, keys: tuple[bool, bool, bool], pos: Vector2d, *_):
    coords = (pos + g_obj.get_component(SurfaceComponent).size // 2) // 100

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
            SelectComponent.selected.get_component(SelectComponent).deselect()
            selector_info_update()

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
        world = create_game_object(world_obj, "game_screen:world_section:world", size=Vector2d.from_tuple(self.world_size) * 100, color=(80, 80, 80), shape=Shape.RECT)
        unit_layer = create_game_object(world, "game_screen:world_section:world:unit_layer", size=Vector2d.from_tuple(self.world_size) * 100, shape=Shape.RECT, layer=3)
        city_layer = create_game_object(world, "game_screen:world_section:world:city_layer", size=Vector2d.from_tuple(self.world_size) * 100, shape=Shape.RECT, layer=2)
        ui_lauer = create_game_object(world, "game_screen:world_section:world:ui_layer", size=Vector2d.from_tuple(self.world_size) * 100, shape=Shape.RECT, layer=4)
        ui_lauer.add_component(OnClickComponent([1, 0, 1], 0, 1, on_world_click))
        ui_lauer.add_component(KeyBindComponent([pg.K_r], 0, 1, reset_ui))
        def bind_keys(g_obj: GameObject, keys: list[int], *_):
            current_pos = g_obj.get_component(Transform).pos
                    
            world_width = self.world_size[0] * 100
            world_height = self.world_size[1] * 100
            
            view_width = 8 * (1200 / 12) 
            view_height = 8 * (800 / 8)
            
            max_x = (world_width - view_width) / 2
            max_y = (world_height - view_height) / 2
            
            if pg.K_w in keys and current_pos.y < max_y:
                g_obj.get_component(Transform).move(Vector2d(0, 20))
            if pg.K_a in keys and current_pos.x < max_x:
                g_obj.get_component(Transform).move(Vector2d(20, 0))
            if pg.K_s in keys and current_pos.y > -max_y:
                g_obj.get_component(Transform).move(Vector2d(0, -20))
            if pg.K_d in keys and current_pos.x > -max_x:
                g_obj.get_component(Transform).move(Vector2d(-20, 0))
        world.add_component(KeyBindComponent([pg.K_w, pg.K_a, pg.K_s, pg.K_d], 1, 1, bind_keys))

    @Client.object.check_update(UpdateCodes.UPDATE_TILE)
    def update_tile():
        self = Client.object
        world = GameObject.get_group_by_tag("game_screen:world_section:world")[0]
        world.disable()
        for pos in self.world_updates:
            create_tile_game_object(pos)
        self.world_updates.clear()
        world.enable()

    @Client.object.check_update(UpdateCodes.UPDATE_UNIT)
    def update_unit():
        self = Client.object
        for unit_change in self.units_updates:
            if len(unit_change[0]) == 0: 
                create_unit_game_object(unit_change[1])
            elif not isinstance(unit_change[1], UnitData):
                remove_unit_game_object(unit_change[0])
            else:
                move_unit_game_object(unit_change[0], unit_change[1])
        self.units_updates.clear()

    @Client.object.check_update(UpdateCodes.UPDATE_CITY)
    def update_city():
        self = Client.object
        for city in self.cities_updates:
            create_city_game_object(city)
        self.cities_updates.clear()

    @Client.object.check_update(UpdateCodes.UPDATE_MONEY)
    def update_money():
        self = Client.object
        money_label = GameObject.get_group_by_tag("game_screen:info_section:money_label")[0]
        money_label.get_component(LabelComponent).text = f"Money: {self.money}"
        money_label.need_draw_set_true()
        money_label.need_blit_set_true()

    @Client.object.check_update(UpdateCodes.END_TURN)
    def end_turn():
        self = Client.object
        if self.names[self.now_playing] == self.myname:
            end_turn_button = GameObject.get_group_by_tag("game_screen:info_section:end_turn_button")[0]
            end_turn_button.get_component(ColorComponent).color = (50, 150, 50)
            end_turn_button.need_draw_set_true()
            end_turn_button.need_blit_set_true()

    @Client.object.change_main_cycle
    def update(self: Client):
        if not self.game_started:
            raise RuntimeError("Game has not started yet!")
        
        while not self.changing_main_cycle:
            Client.object.check_updates()
            
if __name__ == "__main__":
    load()
