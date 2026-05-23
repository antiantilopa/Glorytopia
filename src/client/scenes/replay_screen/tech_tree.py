from engine_antiantilopa import *
from client.texture_assign.texture_assign import TextureAssignSystem
from client.widgets.fastgameobjectcreator import *
from client.widgets.select import SelectComponent
from client.globals.window_size import WindowSize
from shared import *

from . import components
from . import selector
from . import replay
from . import game_classes

def create_tech_tree_node(tech_win: GameObject, tech: TechNode, number: int, depth: int):
    lines = []
    up_lines = []
    width = 0
    if len(tech.childs) == 0:
        width = 1
    else:
        first_width = 0
        last_width = 0
        for i in range(len(tech.childs)):
            if i == 0:
                first_width, new_lines = create_tech_tree_node(tech_win, tech.childs[i], number + width, depth + 1)
                width += first_width
            elif i == len(tech.childs) - 1:
                last_width, new_lines = create_tech_tree_node(tech_win, tech.childs[i], number + width, depth + 1)
                width += last_width
            else:
                new_width, new_lines = create_tech_tree_node(tech_win, tech.childs[i], number + width, depth + 1)
                width += new_width
            lines.extend(new_lines)
        line = create_line_game_object(
            parent=tech_win, 
            tags="TEST:line", 
            at=InGrid((8, 8), (number * 2 + width - 1, depth * 2 + 0.5)), 
            to=InGrid((8, 8), (number * 2 + width - 1, depth * 2 + 1)), 
            color=ColorComponent.WHITE, 
            width=5
        )
        lines.append(line)
        if len(tech.childs) >= 2:
            line = create_line_game_object(
                parent=tech_win, tags="TEST:line", 
                at=InGrid((8, 8), (number * 2 + first_width - 1, depth * 2 + 1)), 
                to=InGrid((8, 8), (number * 2 + 2 * width - last_width - 1, depth * 2 + 1)), 
                color=ColorComponent.WHITE, 
                width=5
            )
            lines.append(line)
    if tech.parent is not None:
        line = create_line_game_object(
            parent=tech_win, 
            tags="TEST:line", 
            at=InGrid((8, 8), (number * 2 + width - 1, depth * 2 - 0.5)), 
            to=InGrid((8, 8), (number * 2 + width - 1, depth * 2 - 1)), 
            color=ColorComponent.WHITE, 
            width=5
        )
        up_lines.append(line)
    
    tech_obj = create_game_object(
        parent=tech_win, 
        tags=f"replay_screen:techs_window:tech_node", 
        at=InGrid((8, 8), (number * 2 + width - 1, depth * 2)), 
        shape=Shape.RECT, 
        size_margin=Vector2d(-5, -5)
    )
    tech_obj.add_component(components.TechComponent(tech))
    tech_obj.add_component(SelectComponent())
    tech_obj.get_component(components.TechComponent).lines = lines
    game_classes.TechNodeObj.technodeobjs[tech.name] = tech_obj
    color_ind = 0
    if tech in replay.Replay.get_player_by_id(replay.Replay.watch_as).techs:
        color_ind = 2
    elif tech.parent is not None:
        if tech.parent in replay.Replay.get_player_by_id(replay.Replay.watch_as).techs:
            color_ind = 1
    TextureAssignSystem.assign_texture(tech, tech_obj, args=(color_ind, lines))
    return width, up_lines

def create_tech_tree():
    tech_win = GameObject.get_game_object_by_tags("replay_screen:techs_window")

    roots: list[TechNode] = []
    for tech in TechNode.values():
        if tech.parent is None:
            roots.append(tech)

    width = 0
    for i in range(len(roots)):
        new_width, _ = create_tech_tree_node(tech_win, roots[i], width, 0)
        width += new_width
    
    for child in tech_win.childs:
        if child.contains_component(components.TechComponent):
            child.add_component(OnClickComponent([1, 0, 0], 0, 1, on_tech_click))

def update_tech_tree():
    for tech in TechNode.values():
        tech_obj = game_classes.TechNodeObj.get_obj_by_technode(tech)
        color_ind = 0
        if tech in replay.Replay.get_player_by_id(replay.Replay.watch_as).techs:
            color_ind = 2
        elif tech.parent is not None:
            if tech.parent in replay.Replay.get_player_by_id(replay.Replay.watch_as).techs:
                color_ind = 1
        TextureAssignSystem.update_texture(tech, tech_obj, args=(color_ind, tech_obj.get_component(components.TechComponent).lines))

def on_tech_click(g_obj: GameObject, keys: tuple[bool, bool, bool], pos: Vector2d, *_):
    if not g_obj.contains_component(components.TechComponent):
        return
    if not keys[0]:
        return
    if g_obj.parent.get_component(ShapeComponent).does_collide(g_obj.parent.get_component(Transform).pos + pos):
        g_obj.get_component(SelectComponent).select()
        selector.selector_info_update()