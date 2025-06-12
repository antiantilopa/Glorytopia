from engine_antiantilopa import *
from client.respondings.client import Client
from client.respondings.lobby import respond, UpdateCodes
from client.widgets.fastgameobjectcreator import *
from client.widgets.game_objects_for_game_elements import *
from client.widgets.texture_load import load_textures
from serializator.data_format import Format
from shared import *
import pygame as pg

def load(screen_size: Vector2d = Vector2d(1200, 800)) -> GameObject:
    scene = create_game_object(tags="game_screen", size=screen_size)

    create_game_object(scene, "game_screen:world_section", at=InGrid((12, 8), (0, 0), (8, 8)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)

    info_section = create_game_object(scene, "game_screen:info_section", at=InGrid((12, 8), (8, 0), (4, 8)), shape=Shape.RECT)
    info_section.add_component(OnClickComponent([1, 0, 0], 0, 1, click))

    money_label = create_label(info_section,tags="game_screen:info_section:money_label", text=f"Money: {Client.object.money}", font=pg.font.SysFont("consolas", screen_size.y // 40), at=InGrid((1, 8), (0, 0), (1, 1)), color=ColorComponent.WHITE)

    load_textures()

    return scene



def click(g_obj: GameObject, keys: list[int], pos: Vector2d, *_):
    new = create_game_object(g_obj, "game_screen:info_section:click", at=pos, size=(20, 20), color=ColorComponent.RED, shape=Shape.CIRCLE, radius=10)
    new.add_component(SpriteComponent(size=Vector2d(20, 20), nickname="city"))
    print(f"> [!CLICK] {pos} {keys}")

def init():

    @Client.object.check_update(UpdateCodes.INIT_WORLD)
    def init_world():
        self = Client.object
        world_obj = GameObject.get_group_by_tag("game_screen:world_section")[0]
        world = create_game_object(world_obj, "game_screen:world_section:world", size=Vector2d.from_tuple(self.world_size) * 100, color=(80, 80, 80), shape=Shape.RECT)
        unit_layer = create_game_object(world, "game_screen:world_section:world:unit_layer", size=Vector2d.from_tuple(self.world_size) * 100, shape=Shape.RECT, layer=2)
        ui_lauer = create_game_object(world, "game_screen:world_section:world:ui_layer", size=Vector2d.from_tuple(self.world_size) * 100, shape=Shape.RECT, layer=3)
        ui_lauer.add_component(OnClickComponent([1, 0, 0], 0, 1, click))
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

    @Client.object.change_main_cycle
    def update(self: Client):
        if not self.game_started:
            raise RuntimeError("Game has not started yet!")
        
        while not self.changing_main_cycle:
            Client.object.check_updates()

            money_label = GameObject.get_group_by_tag("game_screen:info_section:money_label")[0]
            money_label.get_component(LabelComponent).text = f"Money: {self.money}"
            money_label.need_draw_set_true()
            money_label.need_blit_set_true()

if __name__ == "__main__":
    load()
