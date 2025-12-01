from engine_antiantilopa import *

from client.globals.music import SoundManager
from client.globals.window_size import WindowSize
from client.widgets.fastgameobjectcreator import *
from shared.util.position import Pos

from . import replay
from . import selector
from . import state

def update_money_label(money: int):
    money_label = GameObject.get_game_object_by_tags("replay_screen:info_section:money_label")
    money_label.get_component(LabelComponent).text = f"Money: {money}"
    money_label.need_draw_set_true()
    money_label.need_blit_set_true()

def update_now_playing_label(name: str):
    now_playing_label = GameObject.get_game_object_by_tags("replay_screen:info_section:now_playing_label")
    now_playing_label.destroy()
    info_section = GameObject.get_game_object_by_tags("replay_screen:info_section")
    now_playing_label = create_label_block(
        parent=info_section, 
        tags="replay_screen:info_section:now_playing_label", 
        text=f"Now playing:\n{name}", 
        font=pg.font.SysFont("consolas", WindowSize.value.inty() // 40), 
        at=InGrid((2, 8), (1, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )

def update_end_turn_button(is_my_turn: bool):
    pass

def click_end_turn_button():
    replay.Replay.next_frame()

def click_tech_open_button():
    if state.State.value == 0:
        open_techs_window()
        state.State.change_state(1)
    elif state.State.value == 1:
        close_techs_window()
        state.State.change_state(0)

def open_techs_window():
    tech_win = GameObject.get_game_object_by_tags("replay_screen:techs_window")
    world_sec = GameObject.get_game_object_by_tags("replay_screen:world_section")

    world_sec.disable()
    tech_win.enable()

def close_techs_window():
    tech_win = GameObject.get_game_object_by_tags("replay_screen:techs_window")
    world_sec = GameObject.get_game_object_by_tags("replay_screen:world_section")

    world_sec.enable()
    tech_win.disable()

def click_on_world(g_obj: GameObject, keys: tuple[bool, bool, bool], pos: Vector2d, *_):
    
    world_sec = GameObject.get_game_object_by_tags("replay_screen:world_section")
    world = GameObject.get_game_object_by_tags("replay_screen:world_section:world")

    if not Vector2d.is_in_box(pos + world.get_component(Transform).pos, -world_sec.get_component(SurfaceComponent).size // 2, world_sec.get_component(SurfaceComponent).size // 2):
        return
    coords = (pos + g_obj.get_component(SurfaceComponent).size // 2) // WindowSize.get_block_size()
    coords = Pos(coords.intx(), coords.inty())
    if coords.x < 0 or coords.y < 0 or coords.x >= replay.Replay.game_data.world_size.x or coords.y >= replay.Replay.game_data.world_size.y:
        return

    else:
        if keys[0]:  # Left click
            selector.select(coords)
            selector.selector_info_update()  
        elif keys[2]:  # Right click
            pass

def reset_ui(*_):
    print("reset ui NotImplementedYet!!!")
    # TODO