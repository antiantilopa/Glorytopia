from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
import pygame as pg
from client.widgets.select import SelectComponent
from client.globals.settings import Settings, ChosenVar, InputVar, OrderVar
from typing import Any

class SettingVariableComponent(Component):
    name: str
    value: Any

    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value
        Component.__init__(self)

class ChooseComponent(SettingVariableComponent):
    variants: list
    chosen: int

    def __init__(self, variants: list, chosen: int, name: str):
        self.variants = variants
        self.chosen = chosen 
        SettingVariableComponent.__init__(self, name, chosen)

class OrderComponent(SettingVariableComponent):
    order: list

    def __init__(self, order: list, name: str):
        self.order = order
        SettingVariableComponent.__init__(self, name, order)

class InputComponent(SettingVariableComponent):
    var: str

    def __init__(self, var: str, name: str):
        self.var = var
        SettingVariableComponent.__init__(self, name, var)

block_size = Vector2d(100, 100)

def load(screen_size: Vector2d = Vector2d(1200, 800)) -> GameObject:
    global block_size
    block_size = screen_size // Vector2d(12, 8)

    scene = create_game_object(tags="settings_screen", size=screen_size)

    overview = create_game_object(scene, "settings_screen:overview", at=InGrid((12, 8), (0, 0), (8, 8)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)

    edit_section = create_game_object(scene, "settings_screen:edit_sec", at=InGrid((12, 8), (8, 0), (4, 8)), shape=Shape.RECT)

    selector_section = create_game_object(edit_section, at=InGrid((1, 8), (0, 1), (1, 5)), shape=Shape.RECTBORDER, color=ColorComponent.WHITE, width=2, margin=Vector2d(5, 0), tags="settings_screen:edit_sec:selector_section")
    selector_info_section = create_game_object(selector_section, at=InGrid((4, 5), (0, 1), (4, 4)), surface_margin=Vector2d(7, 2), tags="settings_screen:edit_sec:selector_section:selector_info_section")
    
    save_button = create_game_object(edit_section, "settings_screen:edit_sec:save_button", at=InGrid((1, 8), (0, 7), (1, 1)), color=(50, 150, 50), shape=Shape.RECT)
    save_label = create_label(save_button, "settings_screen:edit_sec:save_label", text="Save to file", font=pg.font.SysFont("consolas", screen_size.y // 40), at=InGrid((1, 1), (0, 0), (1, 1)), color=ColorComponent.WHITE)
    save_button.add_component(OnClickComponent([1, 0, 0], 0, 1, save_click))


    entry_box = create_game_object(edit_section, "settings_screen:edit_sec:entry_box", at=InGrid((1, 8), (0, 6), (1, 1)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4))
    entry_obj = create_game_object(entry_box, "settings_screen:edit_sec:entry_box:entry", at=InGrid((1, 1), (0, 0)), color=ColorComponent.RED, surface_margin=Vector2d(4, 4))
    entry_obj.add_component(EntryComponent(font=pg.font.SysFont("consolas", block_size.y // 4), active=1))
    # techs_label = create_label(techs_button, "game_screen:info_section:end_turn_label", text="Technology", font=pg.font.SysFont("consolas", screen_size.y // 40), at=InGrid((1, 1), (0, 0), (1, 1)), color=ColorComponent.WHITE)
    # techs_button.add_component(OnClickComponent([1, 0, 0], 0, 1, open_techs_window))

    main_body = create_game_object(overview, "settings_screen:overview:main_body", size=screen_size)
    ui_lauer = create_game_object(main_body, "settings_screen:overview:main_body:ui_layer", size=screen_size, shape=Shape.RECT, layer=4)
    ui_lauer.add_component(OnClickComponent([1, 0, 1], 0, 1, on_world_click))
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
        create_label(box, "settings_screen:overview:main_body:setting_variable_box:label", setting_variable_name, pg.font.SysFont("consolas", block_size.y // 5), color=ColorComponent.RED)
        i += 1
    return scene

def selecting(pos: Vector2d):
    main_body = GameObject.get_game_object_by_tags("settings_screen:overview:main_body")
    for obj in main_body.childs:
        if obj.contains_component(SelectComponent):
            rel_pos = pos - obj.get_component(Transform).pos
            if obj.get_component(ShapeComponent).collide_formula(rel_pos):
                obj.get_component(SelectComponent).select()
    
def selector_info_update():
    selector_info_section = GameObject.get_game_object_by_tags("settings_screen:edit_sec:selector_section:selector_info_section")

    while len(selector_info_section.childs) != 0:
        selector_info_section.childs[0].destroy()
    selector_info_section.need_draw = True

    if SelectComponent.selected is None:
        return

    buttons = []
    text = ""
    
    if SelectComponent.selected.contains_component(ChooseComponent):
        variants = SelectComponent.selected.get_component(ChooseComponent).variants
        chosen = SelectComponent.selected.get_component(ChooseComponent).chosen
        name = SelectComponent.selected.get_component(ChooseComponent).name
        text = "\n".join((
            f"chose one of given variants for",
            f"{name}",
            f"now chosen:",
            f"{variants[chosen]}"
        ))
        def choose(i):
            def func(*_):
                SelectComponent.selected.get_component(ChooseComponent).chosen = i
                selector_info_update()
            return func
    
        for i in range(len(variants)):
            buttons.append((str(variants[i]), choose(i)))

    elif SelectComponent.selected.contains_component(InputComponent):
        name = SelectComponent.selected.get_component(InputComponent).name
        var = SelectComponent.selected.get_component(InputComponent).var

        text = "\n".join((
            f"use input below to write",
            f"needed value for {name}",
            f"now saved is:", 
            f"{var}"
        ))
        def set_var():
            def func(*_):
                entry_object = GameObject.get_game_object_by_tags("settings_screen:edit_sec:entry_box:entry")
                SelectComponent.selected.get_component(InputComponent).var = entry_object.get_component(EntryComponent).text
                selector_info_update()
            return func
        buttons.append(("Save from entry", set_var()))
    elif SelectComponent.selected.contains_component(OrderComponent):
        name = SelectComponent.selected.get_component(OrderComponent).name
        order = SelectComponent.selected.get_component(OrderComponent).order

        text = "\n".join((
            f"use button below to change the order of {name}",
            f"order now is:",
            *map(str, order)
        ))
        def change_order(i):
            def func(*_):
                f = SelectComponent.selected.get_component(OrderComponent).order[i]
                s = SelectComponent.selected.get_component(OrderComponent).order[i + 1]
                SelectComponent.selected.get_component(OrderComponent).order[i] = s
                SelectComponent.selected.get_component(OrderComponent).order[i + 1] = f
                selector_info_update()
            return func
        
        for i in range(len(order) - 1):
            buttons.append(((f"{i} <-> {i + 1}"), change_order(i)))
        
    create_label_block(selector_info_section, "settings_screen:edit_sec:selector_section:selector_info_section:label_block", text, font=pg.font.SysFont("consolas", block_size.y // 5),  at=Position.LEFT_UP, text_pos=Position.LEFT, color=ColorComponent.RED)
    selector_info_buttons_section = create_list_game_object(selector_info_section, bound=1, at=InGrid((1, 5), (0, 2), (1, 3)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4), tags="settings_screen:edit_sec:selector_section:selector_info_section:buttons_section")

    for i in range(len(buttons)):
        button_sec = create_game_object(selector_info_buttons_section, at=InGrid((1, 5), (0, i), (1, 1)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4), tags="settings_screen:edit_sec:selector_section:selector_info_section:buttons_section:button_section")
        button = create_game_object(button_sec, at=InGrid((10, 1), (0, 0), (1, 1)), color=ColorComponent.GREEN, shape=Shape.RECT, tags="settings_screen:edit_sec:selector_section:selector_info_section:buttons_section:button_section:button")
        button.add_component(OnClickComponent((1, 0, 0), 0, 0, buttons[i][1], (buttons[i][2] if len(buttons[i]) > 2 else ())))
        create_label(button_sec, text=buttons[i][0], font=pg.font.SysFont("consolas", block_size.y // 5), at=InGrid((10, 1), (1, 0), (9, 1)), margin=Vector2d(5, 0), color=ColorComponent.RED, tags="settings_screen:edit_sec:selector_section:selector_info_section:buttons_section:button_sec:label")

def on_world_click(g_obj: GameObject, keys: tuple[bool, bool, bool], pos: Vector2d, *_):
    
    overview = GameObject.get_game_object_by_tags("settings_screen:overview")
    main_boby = GameObject.get_game_object_by_tags("settings_screen:overview:main_body")

    if not Vector2d.is_in_box(pos + main_boby.get_component(Transform).pos, -overview.get_component(SurfaceComponent).size // 2, overview.get_component(SurfaceComponent).size // 2):
        return
    coords = pos

    selecting(coords)
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

def launch(screen_size: Vector2d = Vector2d(1200, 800)):
    load(screen_size)
    scene = GameObject.get_game_object_by_tags("settings_change_menu")

    e = Engine(screen_size)
    scene.enable()
    e.run()

if __name__ == "__main__":
    launch()