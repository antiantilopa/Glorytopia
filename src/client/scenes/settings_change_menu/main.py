from engine_antiantilopa import *
import pygame as pg
from client.globals.window_size import WindowSize
from client.widgets.fastgameobjectcreator import *
from client.widgets.select import SelectComponent
from client.globals.settings import Settings, ChosenVar, InputVar, OrderVar

from . import launchers
from .components import *
from .selector import selector_info_update

def load() -> GameObject:

    if len(GameObject.get_group_by_tag("settings_screen")) > 0:
        return GameObject.get_game_object_by_tags("settings_screen")

    scene = create_game_object(tags="settings_screen", size=WindowSize.value)
    scene.add_component(KeyBindComponent([pg.K_ESCAPE], 0, 1, lambda*_: launchers.launch_join_menu()))

    overview = create_game_object(scene, "settings_screen:overview", at=InGrid((12, 8), (0, 0), (8, 8)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)

    edit_section = create_game_object(scene, "settings_screen:edit_sec", at=InGrid((12, 8), (8, 0), (4, 8)), shape=Shape.RECT)

    selector_section = create_game_object(edit_section, at=InGrid((1, 8), (0, 1), (1, 5)), shape=Shape.RECTBORDER, color=ColorComponent.WHITE, width=2, margin=Vector2d(5, 0), tags="settings_screen:edit_sec:selector_section")
    selector_info_section = create_game_object(selector_section, at=InGrid((4, 5), (0, 1), (4, 4)), surface_margin=Vector2d(7, 2), tags="settings_screen:edit_sec:selector_section:selector_info_section")

    save_button = create_game_object(edit_section, "settings_screen:edit_sec:save_button", at=InGrid((1, 8), (0, 7), (1, 1)), color=(50, 150, 50), shape=Shape.RECT)
    save_label = create_label(
        parent=save_button, 
        tags="settings_screen:edit_sec:save_label", 
        text="Save to file", 
        font=pg.font.SysFont("consolas", WindowSize.value.y // 40), 
        at=InGrid((1, 1), (0, 0), (1, 1)), 
        color=ColorComponent.WHITE
    )
    save_button.add_component(OnClickComponent([1, 0, 0], 0, 1, lambda *_: save_click() or launchers.launch_join_menu()))


    entry_box = create_game_object(edit_section, "settings_screen:edit_sec:entry_box", at=InGrid((1, 8), (0, 6), (1, 1)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4))
    entry_obj = create_game_object(entry_box, "settings_screen:edit_sec:entry_box:entry", at=InGrid((1, 1), (0, 0)), color=ColorComponent.RED, surface_margin=Vector2d(4, 4))
    entry_obj.add_component(EntryComponent(font=pg.font.SysFont("consolas", WindowSize.get_block_size().inty() // 4), active=1))

    main_body = create_game_object(overview, "settings_screen:overview:main_body", size=WindowSize.value)
    ui_lauer = create_game_object(main_body, "settings_screen:overview:main_body:ui_layer", size=WindowSize.value, shape=Shape.RECT, layer=4)
    ui_lauer.add_component(OnClickComponent([1, 0, 1], 0, 1, click))
    main_body.enable()

    i = 0
    for setting_variable_name in Settings.__dict__:
        if setting_variable_name.startswith("_") or setting_variable_name.endswith("_"):
            continue
        box = create_game_object(main_body, "settings_screen:overview:main_body:setting_variable_box", InGrid((12, 8), (0, i), (6, 1)), shape=Shape.RECT)
        variable = Settings.__dict__[setting_variable_name]
        if isinstance(variable, ChosenVar):
            box.add_component(ChooseComponent(variable.variants, variable.chosen, setting_variable_name))
        if isinstance(variable, InputVar):
            box.add_component(InputComponent(variable.var, setting_variable_name))
        if isinstance(variable, OrderVar):
            box.add_component(OrderComponent(variable.order, setting_variable_name))
        box.add_component(SelectComponent())
        
        create_game_object(box, "settings_screen:overview:main_body:setting_variable_box:border", InGrid((1, 1), (0, 0)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4))
        create_label(
            parent=box, 
            tags="settings_screen:overview:main_body:setting_variable_box:label", 
            text=setting_variable_name, 
            font=pg.font.SysFont("consolas", WindowSize.get_block_size().inty() // 5), 
            color=ColorComponent.RED
        )
        i += 1
    return scene

def click_select(pos: Vector2d):
    main_body = GameObject.get_game_object_by_tags("settings_screen:overview:main_body")
    for obj in main_body.childs:
        if obj.contains_component(SelectComponent):
            rel_pos = pos - obj.get_component(Transform).pos
            if obj.get_component(ShapeComponent).collide_formula(rel_pos):
                obj.get_component(SelectComponent).select()

def click(g_obj: GameObject, keys: tuple[bool, bool, bool], pos: Vector2d, *_):
    
    overview = GameObject.get_game_object_by_tags("settings_screen:overview")
    main_boby = GameObject.get_game_object_by_tags("settings_screen:overview:main_body")

    if not Vector2d.is_in_box(pos + main_boby.get_component(Transform).pos, -overview.get_component(SurfaceComponent).size // 2, overview.get_component(SurfaceComponent).size // 2):
        return
    coords = pos

    click_select(coords)
    selector_info_update()  


def save_click(*_):
    boxes = GameObject.get_group_by_tag("settings_screen:overview:main_body:setting_variable_box")
    for box in boxes:
        name = box.get_component(SettingVariableComponent).name
        variable = Settings.__dict__[name]
        if isinstance(variable, ChosenVar):
            variable.chosen = box.get_component(ChooseComponent).chosen
        if isinstance(variable, InputVar):
            variable.var = box.get_component(InputComponent).var
        if isinstance(variable, OrderVar):
            variable.order = box.get_component(OrderComponent).order

    Settings.save_to_file_()


def launch():
    load()
    scene = GameObject.get_game_object_by_tags("settings_change_menu")

    e = Engine(WindowSize.value)
    scene.enable()
    e.run()

if __name__ == "__main__":
    launch()