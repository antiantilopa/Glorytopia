from .state import State
from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from client.globals.settings import Settings

def state_1_start():
    scene = GameObject.get_game_object_by_tags("join_menu")
    label_obj = GameObject.get_game_object_by_tags("join_menu:main_label")
    entry_obj = GameObject.get_game_object_by_tags("join_menu:entry_box:entry")

    entry_obj.get_component(EntryComponent).clear()
    entry_obj.get_component(EntryComponent).text = Settings.pref_name.var
    label_obj.destroy()
    new_label_obj = create_label(
        parent=scene, 
        tags="join_menu:main_label", 
        text="Enter nickname:", 
        at=Position.CENTER, 
        color=ColorComponent.RED
    )
    new_label_obj.first_iteration()


def state_2_start():
    scene = GameObject.get_game_object_by_tags("join_menu")
    label_obj = GameObject.get_game_object_by_tags("join_menu:main_label")
    entry_obj = GameObject.get_game_object_by_tags("join_menu:entry_box:entry")

    entry_obj.get_component(EntryComponent).clear()
    label_obj.destroy()
    new_label_obj = create_label(
        parent=scene, 
        tags="join_menu:main_label", 
        text="Enter recovery code:", 
        at=Position.CENTER, 
        color=ColorComponent.RED
    )
    new_label_obj.first_iteration()


def main():
    State.set_on_state_start(1, state_1_start)
    State.set_on_state_start(2, state_2_start)