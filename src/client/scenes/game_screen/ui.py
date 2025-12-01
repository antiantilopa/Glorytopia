from engine_antiantilopa import *

from client.globals.music import SoundManager
from client.globals.window_size import WindowSize
from client.network.client import GameClient
from client.widgets.fastgameobjectcreator import *
from client.widgets.select import SelectComponent
from netio.serialization.routing import MessageType
from shared.util.position import Pos

from . import game_classes
from . import selector
from . import components
from . import state

def update_money_label(money: int):
    money_label = GameObject.get_game_object_by_tags("game_screen:info_section:money_label")
    money_label.get_component(LabelComponent).text = f"Money: {money}"
    money_label.need_draw_set_true()
    money_label.need_blit_set_true()

def update_now_playing_label(name: str):
    now_playing_label = GameObject.get_game_object_by_tags("game_screen:info_section:now_playing_label")
    now_playing_label.destroy()
    info_section = GameObject.get_game_object_by_tags("game_screen:info_section")
    now_playing_label = create_label_block(
        parent=info_section, 
        tags="game_screen:info_section:now_playing_label", 
        text=f"Now playing:\n{name}", 
        font=pg.font.SysFont("consolas", WindowSize.value.inty() // 40), 
        at=InGrid((2, 8), (1, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )

def update_end_turn_button(is_my_turn: bool):
    end_turn_button = GameObject.get_game_object_by_tags("game_screen:info_section:end_turn_button")
    if is_my_turn:
        end_turn_button.get_component(ColorComponent).color = (50, 150, 50)
        SoundManager.new_music("start_turn", loop=False)
    else:
        end_turn_button.get_component(ColorComponent).color = (30, 100, 30)
    end_turn_button.need_draw_set_true()
    end_turn_button.need_blit_set_true()

def click_end_turn_button():
    GameClient.object.send_message(MessageType.EVENT, "GAME/END_TURN", None)

def click_tech_open_button():
    if state.State.value == 0:
        open_techs_window()
        state.State.change_state(1)
    elif state.State.value == 1:
        close_techs_window()
        state.State.change_state(0)

def open_techs_window():
    tech_win = GameObject.get_game_object_by_tags("game_screen:techs_window")
    world_sec = GameObject.get_game_object_by_tags("game_screen:world_section")

    world_sec.disable()
    tech_win.enable()

def close_techs_window():
    tech_win = GameObject.get_game_object_by_tags("game_screen:techs_window")
    world_sec = GameObject.get_game_object_by_tags("game_screen:world_section")

    world_sec.enable()
    tech_win.disable()

def click_harvest(pos: Pos):
    GameClient.object.send_message(MessageType.EVENT, "GAME/HARVEST", pos)

def click_build(pos: Pos, btype_id: int):
    GameClient.object.send_message(MessageType.EVENT, "GAME/BUILD", (pos, btype_id))

def click_terraform(pos: Pos, terraform_id: int):
    GameClient.object.send_message(MessageType.EVENT, "GAME/TERRAFORM", (pos, terraform_id))

def click_create_unit(pos: Pos, unit_id: int):
    GameClient.object.send_message(MessageType.EVENT, "GAME/CREATE_UNIT", (pos, unit_id))

def click_conquer_city(pos: Pos):
    GameClient.object.send_message(MessageType.EVENT, "GAME/CONQUER_CITY", pos)

def click_buy_tech(tech_id: int):
    GameClient.object.send_message(MessageType.EVENT, "GAME/BUY_TECH", tech_id)

def click_on_world(g_obj: GameObject, keys: tuple[bool, bool, bool], pos: Vector2d, *_):
    
    world_sec = GameObject.get_game_object_by_tags("game_screen:world_section")
    world = GameObject.get_game_object_by_tags("game_screen:world_section:world")

    if not Vector2d.is_in_box(pos + world.get_component(Transform).pos, -world_sec.get_component(SurfaceComponent).size // 2, world_sec.get_component(SurfaceComponent).size // 2):
        return
    coords = (pos + g_obj.get_component(SurfaceComponent).size // 2) // WindowSize.get_block_size()
    coords = Pos(coords.intx(), coords.inty())
    if coords.x < 0 or coords.y < 0 or coords.x >= game_classes.GameRules.world_size.x or coords.y >= game_classes.GameRules.world_size.y:
        return

    else:
        if keys[0]:  # Left click
            selector.select(coords)
            selector.selector_info_update()  
        elif keys[2]:  # Right click
            if SelectComponent.selected is None:
                return
            if not SelectComponent.selected.contains_component(components.UnitComponent):
                return
            unit = SelectComponent.selected.get_component(components.UnitComponent).unit_data
            GameClient.object.send_message(MessageType.EVENT, "GAME/MOVE_UNIT", (unit.pos, coords))

def reset_ui(*_):
    print("reset ui NotImplementedYet!!!")
    # TODO