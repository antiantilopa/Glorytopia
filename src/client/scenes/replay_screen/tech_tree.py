from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from client.widgets.select import SelectComponent
from client.globals.window_size import WindowSize
from shared import *

from . import components
from . import selector

def create_tech_tree_node(tech_win: GameObject, tech: TechNode, number: int, depth: int):
    width = 0
    if len(tech.childs) == 0:
        width = 1
    else:
        first_width = 0
        last_width = 0
        for i in range(len(tech.childs)):
            if i == 0:
                first_width = create_tech_tree_node(tech_win, tech.childs[i], number + width, depth + 1)
                width += first_width
            elif i == len(tech.childs) - 1:
                last_width = create_tech_tree_node(tech_win, tech.childs[i], number + width, depth + 1)
                width += last_width
            else:
                width += create_tech_tree_node(tech_win, tech.childs[i], number + width, depth + 1)
        create_line_game_object(
            parent=tech_win, 
            tags="TEST:line", 
            at=InGrid((8, 8), (number * 2 + width - 1, depth * 2 + 0.5)), 
            to=InGrid((8, 8), (number * 2 + width - 1, depth * 2 + 1)), 
            color=ColorComponent.WHITE, 
            width=5
        )
        if len(tech.childs) >= 2:
            create_line_game_object(
                parent=tech_win, tags="TEST:line", 
                at=InGrid((8, 8), (number * 2 + first_width - 1, depth * 2 + 1)), 
                to=InGrid((8, 8), (number * 2 + 2 * width - last_width - 1, depth * 2 + 1)), 
                color=ColorComponent.WHITE, 
                width=5
            )
    if tech.parent is not None:
        create_line_game_object(
            parent=tech_win, 
            tags="TEST:line", 
            at=InGrid((8, 8), (number * 2 + width - 1, depth * 2 - 0.5)), 
            to=InGrid((8, 8), (number * 2 + width - 1, depth * 2 - 1)), 
            color=ColorComponent.WHITE, 
            width=5
        )
    
    
    tech_node = create_game_object(tech_win, f"replay_screen:techs_window:tech_node", at=InGrid((8, 8), (number * 2 + width - 1, depth * 2)), shape=Shape.RECT)
    tech_node.add_component(components.TechComponent(tech))
    tech_node.add_component(SelectComponent())
    tech_node.add_component(SpriteComponent(nickname=tech.name, size=WindowSize.get_block_size()))

    return width

def create_tech_tree():
    tech_win = GameObject.get_game_object_by_tags("replay_screen:techs_window")

    roots: list[TechNode] = []
    for tech in TechNode.values():
        if tech.parent is None:
            roots.append(tech)

    width = 0
    for i in range(len(roots)):
        width += create_tech_tree_node(tech_win, roots[i], width, 0)
    
    for child in tech_win.childs:
        if child.contains_component(components.TechComponent):
            child.add_component(OnClickComponent([1, 0, 0], 0, 1, on_tech_click))

def on_tech_click(g_obj: GameObject, keys: tuple[bool, bool, bool], pos: Vector2d, *_):
    if not g_obj.contains_component(components.TechComponent):
        return
    if keys[0]:
        g_obj.get_component(SelectComponent).select()
        selector.selector_info_update()