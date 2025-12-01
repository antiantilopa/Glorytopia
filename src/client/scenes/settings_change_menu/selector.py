from typing import Callable
from engine_antiantilopa import *
import pygame as pg
from client.globals.window_size import WindowSize
from client.widgets.fastgameobjectcreator import *
from client.widgets.select import SelectComponent

from .components import *

def selector_info_update():
    selector_info_section = GameObject.get_game_object_by_tags("settings_screen:edit_sec:selector_section:selector_info_section")

    while len(selector_info_section.childs) != 0:
        selector_info_section.childs[0].destroy()
    selector_info_section.need_draw = True

    if SelectComponent.selected is None:
        return

    # default
    buttons = []
    text = ""
    
    if SelectComponent.selected.contains_component(ChooseComponent):
        text, buttons = _selected_choose()
    elif SelectComponent.selected.contains_component(InputComponent):
        text, buttons = _selected_input()
    elif SelectComponent.selected.contains_component(OrderComponent):
        text, buttons = _selected_order()
        
    create_selector_objects(selector_info_section, text, buttons)

def create_selector_objects(selector_info_section: GameObject, text: str, buttons: list[tuple[str, Callable]]):
    create_label_block(
        parent=selector_info_section, 
        tags="settings_screen:edit_sec:selector_section:selector_info_section:label_block", 
        text=text, 
        font=pg.font.SysFont("consolas", WindowSize.get_block_size().inty() // 5),  
        at=Position.LEFT_UP, 
        text_pos=Position.LEFT, 
        color=ColorComponent.RED
    )
    selector_info_buttons_section = create_list_game_object(selector_info_section, bound=1, at=InGrid((1, 5), (0, 2), (1, 3)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4), tags="settings_screen:edit_sec:selector_section:selector_info_section:buttons_section")

    for i in range(len(buttons)):
        button_sec = create_game_object(selector_info_buttons_section, at=InGrid((1, 5), (0, i), (1, 1)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, surface_margin=Vector2d(4, 4), tags="settings_screen:edit_sec:selector_section:selector_info_section:buttons_section:button_section")
        button = create_game_object(button_sec, at=InGrid((10, 1), (0, 0), (1, 1)), color=ColorComponent.GREEN, shape=Shape.RECT, tags="settings_screen:edit_sec:selector_section:selector_info_section:buttons_section:button_section:button")
        button.add_component(OnClickComponent((1, 0, 0), 0, 0, buttons[i][1], (buttons[i][2] if len(buttons[i]) > 2 else ())))
        create_label(
            parent=button_sec, 
            text=buttons[i][0], 
            font=pg.font.SysFont("consolas", WindowSize.get_block_size().inty() // 5), 
            at=InGrid((10, 1), (1, 0), (9, 1)), 
            margin=Vector2d(5, 0), 
            color=ColorComponent.RED, 
            tags="settings_screen:edit_sec:selector_section:selector_info_section:buttons_section:button_sec:label"
        )

def _selected_choose() -> tuple[str, list[tuple[str, Callable]]]:
    choose_component = SelectComponent.selected.get_component(ChooseComponent)
    variants = choose_component.variants
    chosen = choose_component.chosen
    name = choose_component.name
    text = "\n".join((
        f"chose one of given variants for",
        f"{name}",
        f"now chosen:",
        f"{variants[chosen]}"
    ))
    def choose(i):
        def func(*_):
            choose_component.chosen = i
            selector_info_update()
        return func
    buttons = []
    for i in range(len(variants)):
        buttons.append((str(variants[i]), choose(i)))

    return text, buttons

def _selected_input() -> tuple[str, list[tuple[str, Callable]]]:
    input_component = SelectComponent.selected.get_component(InputComponent)
    name = input_component.name
    var = input_component.var

    text = "\n".join((
        f"use input below to write",
        f"needed value for {name}",
        f"now saved is:", 
        f"{var}"
    ))

    def func(*_):
        entry_object = GameObject.get_game_object_by_tags("settings_screen:edit_sec:entry_box:entry")
        input_component.var = entry_object.get_component(EntryComponent).text
        selector_info_update()

    buttons = []
    buttons.append(("Save from entry", func))
    return text, buttons

def _selected_order() -> tuple[str, list[tuple[str, Callable]]]:
    order_component = SelectComponent.selected.get_component(OrderComponent)
    name = order_component.name
    order = order_component.order

    text = "\n".join((
        f"use button below to change the order of {name}",
        f"order now is:",
        *map(str, order)
    ))
    def change_order(i):
        def func(*_):
            f = order_component.order[i]
            s = order_component.order[i + 1]
            order_component.order[i] = s
            order_component.order[i + 1] = f
            selector_info_update()
        return func
    
    buttons = []
    for i in range(len(order) - 1):
        buttons.append(((f"{i} <-> {i + 1}"), change_order(i)))
    
    return text, buttons