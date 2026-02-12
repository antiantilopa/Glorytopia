from engine_antiantilopa import *
from client.network.client import GameClient, GamePlayer
from client.widgets.fastgameobjectcreator import *
from client.globals.window_size import WindowSize
from netio.serialization.routing import MessageType
from shared import *
import pygame as pg

from shared.util.position import Pos

from . import tech_tree
from . import network
from . import game_classes
from . import ui
from . import fog_of_war
from . import background_music

network.main()

def init(now_playing_player_id: int, world_size: Pos):
    GameClient.object.game_started = 1
    GameClient.object.now_playing_player_id = now_playing_player_id
    game_classes.GameRules.set_world_size(world_size)

def load() -> GameObject:
    if len(GameObject.get_group_by_tag("game_screen")) > 0:
        return GameObject.get_game_object_by_tags("game_screen")
    
    scene = create_game_object(tags="game_screen", size=WindowSize.value)

    background_music.BackgroundMusic.start()

    def deleteme(*_):
        try:
            exec(input())
        except Exception as e:
            print(f"error: {e}")

    scene.add_component(KeyBindComponent([pg.K_q], 0, 1, deleteme))

    world_section = create_game_object(
        parent=scene, 
        tags="game_screen:world_section", 
        at=InGrid((12, 8), (0, 0), (8, 8)), 
        color=ColorComponent.WHITE, 
        shape=Shape.RECTBORDER, 
        width=2
    )
    
    techs_window = create_list_game_object(
        parent=scene, 
        tags="game_screen:techs_window", 
        at=InGrid((12, 8), (0, 0), (8, 8)), 
        color=(0, 70, 150), 
        shape=Shape.RECT, 
        axis=(1, 1), 
        speed=Vector2d(40, 40) * WindowSize.get_block_size() // 100, 
        bound=1, 
        layer=0, 
        x_axis_keys=[pg.K_a, pg.K_d], 
        y_axis_keys=[pg.K_w, pg.K_s]
    )

    tech_tree.create_tech_tree()

    techs_window.disable()

    info_section = create_game_object(
        parent=scene, 
        tags="game_screen:info_section", 
        at=InGrid((12, 8), (8, 0), (4, 8)), 
        shape=Shape.RECT
    )

    money_label = create_label(
        parent=info_section, 
        tags="game_screen:info_section:money_label", 
        text=f"Money: {GameClient.object.me.money}", font=pg.font.SysFont("consolas", WindowSize.value.inty() // 40), 
        at=InGrid((2, 8), (0, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )

    selector_section = create_game_object(
        parent=info_section, 
        tags="game_screen:info_section:selector_section",
        at=InGrid((1, 8), (0, 1), (1, 5)), 
        shape=Shape.RECTBORDER, 
        color=ColorComponent.WHITE, 
        width=2, 
        margin=Vector2d(5, 0), 
    )
    selector_image_section = create_game_object(
        parent=selector_section, 
        tags="game_screen:info_section:selector_section:selector_image_section",
        at=InGrid((4, 5), (0, 0), (1, 1)), 
        surface_margin=Vector2d(7, 2), 
    )
    selector_info_section = create_game_object(
        parent=selector_section, 
        tags="game_screen:info_section:selector_section:selector_info_section",
        at=InGrid((4, 5), (0, 1), (4, 4)), 
        surface_margin=Vector2d(7, 2), 
    )
    
    end_turn_button = create_game_object(
        parent=info_section, 
        tags="game_screen:info_section:end_turn_button", 
        at=InGrid((1, 8), (0, 7), (1, 1)), 
        color=(50, 150, 50) if GameClient.object.now_playing_player_id == GameClient.object.me.id else (30, 100, 30),
        shape=Shape.RECT
    )
    end_turn_label = create_label(
        parent=end_turn_button, 
        tags="game_screen:info_section:end_turn_label", 
        text="End Turn", 
        font=pg.font.SysFont("consolas", WindowSize.value.inty() // 40), 
        at=InGrid((1, 1), (0, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )
    end_turn_button.add_component(OnClickComponent([1, 0, 0], 0, 1, lambda*_: ui.click_end_turn_button()))
    now_playing_label = create_label_block(
        parent=info_section, 
        tags="game_screen:info_section:now_playing_label", 
        text=f"Now playing:\n{GamePlayer.by_id(GameClient.object.now_playing_player_id).nickname}",
        font=pg.font.SysFont("consolas", WindowSize.value.inty() // 40), 
        at=InGrid((2, 8), (1, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )

    techs_button = create_game_object(
        parent=info_section, 
        tags="game_screen:info_section:techs_button", 
        at=InGrid((1, 8), (0, 6), (1, 1)), 
        color=(0, 150, 250), 
        shape=Shape.RECT
    )
    techs_label = create_label(
        parent=techs_button, 
        tags="game_screen:info_section:end_turn_label", 
        text="Technology", 
        font=pg.font.SysFont("consolas", WindowSize.value.inty() // 40), 
        at=InGrid((1, 1), (0, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )
    techs_button.add_component(OnClickComponent([1, 0, 0], 0, 1, lambda*_: ui.click_tech_open_button()))
    techs_button.add_component(KeyBindComponent([pg.K_ESCAPE], 0, 1, lambda*_: ui.click_tech_open_button()))

    world_size = game_classes.GameRules.world_size_as_Vector2d()
    world = create_game_object(world_section, "game_screen:world_section:world", size=world_size * WindowSize.get_block_size(), color=(80, 80, 80), shape=Shape.RECT)
    unit_layer = create_game_object(world, "game_screen:world_section:world:unit_layer", size=world_size * WindowSize.get_block_size(), shape=Shape.RECT, layer=3)
    city_layer = create_game_object(world, "game_screen:world_section:world:city_layer", size=world_size * WindowSize.get_block_size(), shape=Shape.RECT, layer=2)
    fog_of_war_layer = create_game_object(world, "game_screen:world_section:world:fog_of_war_layer", size=world_size * WindowSize.get_block_size(), shape=Shape.RECT, layer=4)
    fog_of_war_layer.add_component(fog_of_war.FogOfWarComponent(game_classes.GameRules.world_size))
    ui_layer = create_game_object(world, "game_screen:world_section:world:ui_layer", size=world_size * WindowSize.get_block_size(), shape=Shape.RECT, layer=5)
    ui_layer.add_component(OnClickComponent([1, 0, 1], 0, 1, ui.click_on_world))
    ui_layer.add_component(KeyBindComponent([pg.K_r], 0, 1, ui.reset_ui))
    def move_camera(g_obj: GameObject, keys: list[int], *_):
        world_obj = GameObject.get_game_object_by_tags("game_screen:world_section")
        current_pos = g_obj.get_component(Transform).pos

        world_width = world_size.x * WindowSize.get_block_size().x + WindowSize.get_block_size().x // 2
        world_height = world_size.y * WindowSize.get_block_size().y + WindowSize.get_block_size().y // 2
        
        view_width = world_obj.get_component(SurfaceComponent).size.x
        view_height = world_obj.get_component(SurfaceComponent).size.y
        
        max_x = (world_width - view_width) / 2
        max_y = (world_height - view_height) / 2
        
        if pg.K_w in keys and current_pos.y < max_y:
            g_obj.get_component(Transform).move(Vector2d(0, 40) * WindowSize.get_block_size() // 100)
        if pg.K_a in keys and current_pos.x < max_x:
            g_obj.get_component(Transform).move(Vector2d(40, 0) * WindowSize.get_block_size() // 100)
        if pg.K_s in keys and current_pos.y > -max_y:
            g_obj.get_component(Transform).move(Vector2d(0, -40) * WindowSize.get_block_size() // 100)
        if pg.K_d in keys and current_pos.x > -max_x:
            g_obj.get_component(Transform).move(Vector2d(-40, 0) * WindowSize.get_block_size() // 100)
    world.add_component(KeyBindComponent([pg.K_w, pg.K_a, pg.K_s, pg.K_d], 1, 1, move_camera))

    return scene
    
def start():
    scene = GameObject.get_game_object_by_tags("game_screen")
    tech_win = GameObject.get_game_object_by_tags("game_screen:techs_window")

    scene.enable()
    tech_win.disable()

    GameClient.object.send_message(MessageType.REQUEST, "GAME/SYNCHRONIZE", None)

if __name__ == "__main__":
    load()
