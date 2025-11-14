from engine_antiantilopa import *
from client.network.client import GamePlayer
from client.widgets.fastgameobjectcreator import *
from client.globals.window_size import WindowSize
import pygame as pg

def update_all_section():
    ready_section = GameObject.get_game_object_by_tags("lobby_screen:ready_section")
    num = len(GamePlayer.joined_players) - 1

    for i in range(len(GameObject.get_group_by_tag("lobby_screen:ready_section:name")), num + 1):
        n = create_game_object(
            parent=ready_section, 
            tags=["lobby_screen:ready_section:name", str(i)], 
            at=InGrid((1, 6), (0, i)), 
            color=ColorComponent.WHITE, 
            width=2, 
            shape=Shape.RECTBORDER, 
            margin=Vector2d(10, 3)
        )
        n.first_iteration()

    for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name"):
        if int(g.tags[1]) > num:
            g.destroy()
        else:
            for child in g.childs:
                if "lobby_screen:ready_section:name:name_label" in child.tags:
                    child.destroy()
                    break
            l1 = create_label(
                parent=g, 
                tags="lobby_screen:ready_section:name:name_label", 
                text=GamePlayer.joined_players[int(g.tags[1])].nickname, font=pg.font.SysFont("consolas", WindowSize.value.inty() // 40), 
                at=Position.LEFT, 
                color=GamePlayer.joined_players[int(g.tags[1])].get_main_color(), 
                margin=Vector2d(20, 3)
            )
            l2 = create_label(
                parent=g, 
                tags="lobby_screen:ready_section:name:ready_label", 
                text="X", 
                font=pg.font.SysFont("consolas", WindowSize.value.inty() // 40), 
                at=Position.RIGHT, 
                color=GamePlayer.joined_players[int(g.tags[1])].get_main_color(), 
                margin=Vector2d(20, 3)
            )
            l1.first_iteration()
            l2.first_iteration()
    for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name:ready_label"):
        g.get_component(LabelComponent).text = "X"
        g.need_draw_set_true()
        g.need_blit_set_true()

def update_ready():
    for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name:ready_label"):
        g.get_component(LabelComponent).text = ("X", "O")[int(GamePlayer.joined_players[int(g.parent.tags[1])].is_ready)]
        g.need_draw_set_true()
        g.need_blit_set_true()