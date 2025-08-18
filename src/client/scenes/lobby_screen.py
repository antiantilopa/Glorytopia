from engine_antiantilopa import *
from client.network.client import Client
from client.globals.settings import Settings
from client.network.lobby import respond, UpdateCodes
from client.widgets.fastgameobjectcreator import *
from client.widgets.sound import SoundComponent
from serializator.data_format import Format
from shared.asset_types import Nation
from . import game_screen
import threading
import pygame as pg

scroll_num = 0

def scroll(g_obj: GameObject, tr: list[int], *_):
        global scroll_num
        if len(tr) != 1:
            return
        dy = 1 if tr[0] == pg.K_UP else -1
        if scroll_num + dy < 0 or scroll_num + dy + 15 > len(Client.object.messages):
            return
        g_obj.disable()
        for child in g_obj.childs:
            child.get_component(Transform).move(Vector2d(0, g_obj.get_component(SurfaceComponent).size.y // 15 * dy))
        scroll_num += dy
        g_obj.enable()

def send_message(g_obj: GameObject, *_):
        text = g_obj.get_component(EntryComponent).text
        c = Client.object
        c.send(Format.event("LOBBY/MESSAGE", [text]))
        g_obj.get_component(EntryComponent).clear()

def send_ready(*_):
    c = Client.object
    c.send(Format.event("LOBBY/READY", [1 - c.readiness[c.myname]]))

def send_change_color(g, k, p, i):
    c = Client.object
    c.send(Format.event("LOBBY/COLOR_CHANGE", [i]))

def send_change_nation(g, k, p, i):
    c = Client.object
    c.send(Format.event("LOBBY/NATION_CHANGE", [i]))

def load(screen_size: Vector2d = Vector2d(1200, 800)):
    global scroll_num

    scene = create_game_object(tags="lobby_screen", size=screen_size)
    scene_size = screen_size
    
    chat_section = create_game_object(scene, "lobby_screen:chat_section", at=InGrid((12, 8), (6, 0), (6, 8)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)

    message_section = create_game_object(chat_section, "lobby_screen:chat_section:message_section", at=InGrid((1, 10), (0, 0), (1, 9)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)
    
    message_section.add_component(KeyBindComponent([pg.K_UP, pg.K_DOWN], 0, 1, scroll))
    
    entry_box = create_game_object(chat_section, "lobby_screen:chat_section:entry_box", at=InGrid((1, 10), (0, 9), (1, 1)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, margin=Vector2d(6, 6))
    
    entry_obj = create_game_object(entry_box, "lobby_screen:chat_section:entry_box:entry", at=InGrid((1, 1), (0, 0), (1, 1)), color=ColorComponent.RED, margin=Vector2d(2, 2))
    entry_obj.add_component(EntryComponent(active=True, font=pg.font.SysFont("consolas", scene_size.y // 40)))
    entry_obj.add_component(KeyBindComponent([pg.K_RETURN], 0, 1, send_message))

    ready_section = create_game_object(scene, "lobby_screen:ready_section", at=InGrid((12, 8), (0, 0), (6, 3)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)
    info_section = create_game_object(scene, "lobby_screen:info_section", at=InGrid((12, 8), (0, 3), (6, 5)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)

    ready_button = create_game_object(info_section, "lobby_screen:info_section:ready_button", Position.LEFT_UP, Vector2d(70, 70), ColorComponent.RED, Shape.RECT, margin=Vector2d(10, 10))
    ready_button.add_component(OnClickComponent([1, 0, 0], 0, 1, send_ready))

    ready_button_label = create_label(
        parent=ready_button, 
        tags="lobby_screen:info_section:ready_button:label", text="Ready", 
        font=pg.font.SysFont("consolas", 20), 
        color=ColorComponent.WHITE
    )

    color_change_box = create_list_game_object(
        parent=info_section,
        tags="lobby_screen:info_section:color_change_box",
        at=InGrid((6, 5), (0, 1), (6, 1)),
        color=ColorComponent.WHITE,
        shape=Shape.RECTBORDER,
        surface_margin=Vector2d(2, 2),
        width=2,
        axis=(1, 0),
    )

    for i, color in enumerate(Client.colors):
        color_change_button = create_game_object(color_change_box, "lobby_screen:info_section:color_change_box:button", InGrid((8, 1), (i, 0), (1, 1)), color=color[0], shape=Shape.RECT, margin=Vector2d(5, 5))
        color_change_button.add_component(OnClickComponent([1, 0, 0], 0, 1, send_change_color, i))
        color_change_button_label = create_label(
            parent=color_change_button, 
            tags=["lobby_screen:info_section:change_color_box:button:label", f"{i}"], 
            text="O", 
            font=pg.font.SysFont("consolas", screen_size.y // 12), 
            color=color[1]
        )
    
    nation_change_box = create_list_game_object(
        parent=info_section,
        tags="lobby_screen:info_section:nation_change_box",
        at=InGrid((6, 5), (0, 2), (6, 1)),
        color=ColorComponent.WHITE,
        shape=Shape.RECTBORDER,
        surface_margin=Vector2d(2, 2),
        width=2,
        axis=(1, 0)
    )
    
    for i, nation in enumerate(Nation.values()):
        nation_change_button = create_game_object(nation_change_box, "lobby_screen:info_section:nation_change_box:button", InGrid((8, 1), (i, 0), (1, 1)), color=(255, 255, 255), shape=Shape.RECT, margin=Vector2d(5, 5))
        nation_change_button.add_component(OnClickComponent([1, 0, 0], 0, 1, send_change_nation, nation.id))
        nation_change_button_icon = create_game_object(
            parent=nation_change_button, 
            tags=["lobby_screen:info_section:change_nation_box:button:icon", f"{i}"], 
            color=(0, 255, 0),
            size=Vector2d(64, 64)
        )
        nation_change_button_icon.add_component(SpriteComponent(nickname=nation.name, size=Vector2d(64, 64)))

    scene.disable()
    return scene

def start_game():
    scene = GameObject.get_group_by_tag("lobby_screen")[0]
    scene.disable()
    GameObject.get_game_object_by_tags("main_menu").get_component(SoundComponent).stop_all_channels()
    game_scene = game_screen.load(scene.get_component(SurfaceComponent).size)
    game_screen.init()
    game_screen.start()

def init():
    @Client.object.check_update(UpdateCodes.JOIN)
    def join():
        self = Client.object
        ready_section = GameObject.get_group_by_tag("lobby_screen:ready_section")[0]
        scene_size = GameObject.get_group_by_tag("lobby_screen")[0].get_component(SurfaceComponent).size
        num = len(self.names) - 1
        for i in range(len(GameObject.get_group_by_tag("lobby_screen:ready_section:name")), num + 1):
            n = create_game_object(ready_section, ["lobby_screen:ready_section:name", str(i)], at=InGrid((1, 6), (0, i)), color=ColorComponent.WHITE, width=2, shape=Shape.RECTBORDER, margin=Vector2d(10, 3))
            n.first_iteration()
        for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name"):
            if int(g.tags[1]) > num:
                g.need_blit_set_true()
                g.need_draw_set_true()
                g.destroy()
            else:
                for child in g.childs:
                    if "lobby_screen:ready_section:name:name_label" in child.tags:
                        child.destroy()
                        break
                l1 = create_label(
                    parent=g, 
                    tags="lobby_screen:ready_section:name:name_label", 
                    text=self.names[int(g.tags[1])], font=pg.font.SysFont("consolas", scene_size.y // 40), 
                    at=Position.LEFT, 
                    color=self.get_main_color(self.names[int(g.tags[1])]), 
                    margin=Vector2d(20, 3)
                )
                l2 = create_label(
                    parent=g, 
                    tags="lobby_screen:ready_section:name:ready_label", 
                    text="X", 
                    font=pg.font.SysFont("consolas", scene_size.y // 40), 
                    at=Position.RIGHT, 
                    color=self.get_main_color(self.names[int(g.tags[1])]), 
                    margin=Vector2d(20, 3)
                )
                l1.first_iteration()
                l2.first_iteration()
        for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name:ready_label"):
            g.get_component(LabelComponent).text = "X"
            g.need_draw_set_true()
            g.need_blit_set_true()

    @Client.object.check_update(UpdateCodes.DISCONNECT)
    def disconnect():
        self = Client.object
        num = len(self.names) - 1
        scene_size = GameObject.get_group_by_tag("lobby_screen")[0].get_component(SurfaceComponent).size
        for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name"):
            if int(g.tags[1]) > num:
                g.need_blit_set_true()
                g.need_draw_set_true()
                g.destroy()
            else:
                for child in g.childs:
                    if "lobby_screen:ready_section:name:name_label" in child.tags:
                        child.destroy()
                        break
                l1 = create_label(
                    parent=g, 
                    tags="lobby_screen:ready_section:name:name_label", 
                    text=self.names[int(g.tags[1])], 
                    font=pg.font.SysFont("consolas", scene_size.y // 40), 
                    at=Position.LEFT, 
                    color=self.get_main_color(self.names[int(g.tags[1])]), 
                    margin=Vector2d(20, 3)
                )
                l1.first_iteration()
        for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name:ready_label"):
            g.get_component(LabelComponent).text = "X"
            g.need_draw_set_true()
            g.need_blit_set_true()

    @Client.object.check_update(UpdateCodes.READY)
    def ready():
        self = Client.object
        for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name:ready_label"):
            g.get_component(LabelComponent).text = ("X", "O")[int(self.readiness[self.names[int(g.parent.tags[1])]])]
            g.need_draw_set_true()
            g.need_blit_set_true()

    @Client.object.check_update(UpdateCodes.INIT_NAMES)
    def init_names():
        self = Client.object
        ready_section = GameObject.get_group_by_tag("lobby_screen:ready_section")[0]
        scene_size = GameObject.get_group_by_tag("lobby_screen")[0].get_component(SurfaceComponent).size
        while len(ready_section.childs) > 0:
            ready_section.childs[0].destroy()
        for num in range(len(self.names)):
            n = create_game_object(ready_section, ["lobby_screen:ready_section:name", str(num)], at=InGrid((1, 6), (0, num)), color=ColorComponent.WHITE, width=2, shape=Shape.RECTBORDER, margin=Vector2d(10, 3))
            l1 = create_label(
                parent=n, 
                tags="lobby_screen:ready_section:name:name_label", 
                text=self.names[num], font=pg.font.SysFont("consolas", scene_size.y // 40), 
                at=Position.LEFT, 
                color=self.get_main_color(self.names[num]), 
                margin=Vector2d(20, 3)
            )
            l2 = create_label(
                parent=n, 
                tags="lobby_screen:ready_section:name:ready_label", 
                text="X", 
                font=pg.font.SysFont("consolas", scene_size.y // 40), 
                at=Position.RIGHT, 
                color=self.get_main_color(self.names[num]), 
                margin=Vector2d(20, 3)
            )
    
    @Client.object.check_update(UpdateCodes.INIT_COLORS)
    def init_colors():
        for label in GameObject.get_group_by_tag("lobby_screen:info_section:change_color_box:button:label"):
            label.get_component(LabelComponent).text = "X" if int(label.tags[1]) in Client.object.names_to_colors.values() else "O" 
            label.need_draw_set_true()
            label.need_blit_set_true()
        Client.object.send(Format.event("LOBBY/COLOR_CHANGE", [Settings.preffered_color.chosen]))

    @Client.object.check_update(UpdateCodes.MESSAGE)
    def message():
        self = Client.object
        message_section = GameObject.get_group_by_tag("lobby_screen:chat_section:message_section")[0]
        scene_size = GameObject.get_group_by_tag("lobby_screen")[0].get_component(SurfaceComponent).size
        message_section.disable()
        for child in message_section.childs:
            child.get_component(Transform).move(Vector2d(0, -(message_section.get_component(SurfaceComponent).size.y // 15)))
        for i in range(len(message_section.childs), len(self.messages)):
            n = create_game_object(message_section, "lobby_screen:chat_section:mesage_section:message_box", at=InGrid((1, 15), (0, 14)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, margin = Vector2d(3, 3))
            if self.messages[i][0] in self.names:
                color = self.get_main_color(self.messages[i][0])
            else:
                color = ColorComponent.WHITE
            l = create_label(
                parent=n, 
                tags="lobby_screen:chat_section:mesage_section:message_box:message_label", 
                at=Position.LEFT, 
                text=f"{self.messages[i][0]}: {self.messages[i][1]}", 
                font=pg.font.SysFont("consolas", scene_size.y // 40), 
                color=color, 
                margin=Vector2d(10, 2)
            )
        message_section.enable()

    @Client.object.check_update(UpdateCodes.COLOR_CHANGE)
    def color_change():
        self = Client.object
        scene_size = GameObject.get_group_by_tag("lobby_screen")[0].get_component(SurfaceComponent).size
        for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name"):
            for child in g.childs:
                if "lobby_screen:ready_section:name:name_label" in child.tags:
                    child.destroy()
                    break
            l1 = create_label(
                parent=g, 
                tags="lobby_screen:ready_section:name:name_label", 
                text=self.names[int(g.tags[1])], 
                font=pg.font.SysFont("consolas", scene_size.y // 40), 
                at=Position.LEFT, 
                color=self.get_main_color(self.names[int(g.tags[1])]), 
                margin=Vector2d(20, 3)
            )
            l2 = create_label(
                parent=g, 
                tags="lobby_screen:ready_section:name:ready_label", 
                text="O" if self.readiness[self.names[int(g.tags[1])]] else "X", 
                font=pg.font.SysFont("consolas", scene_size.y // 40), 
                at=Position.RIGHT, 
                color=self.get_main_color(self.names[int(g.tags[1])]), 
                margin=Vector2d(20, 3)
            )
            l1.first_iteration()
            l2.first_iteration()
        
        for label in GameObject.get_group_by_tag("lobby_screen:info_section:change_color_box:button:label"):
            label.get_component(LabelComponent).text = "X" if int(label.tags[1]) in Client.object.names_to_colors.values() else "O" 
            label.need_draw_set_true()
            label.need_blit_set_true()

    @Client.object.check_update(UpdateCodes.GAME_START)
    def game_start():
        threading.Thread(target=start_game).start()

    @Client.object.change_main_cycle
    def update(self: Client):
        while not self.changing_main_cycle:
            Client.object.check_updates()

def launch():
    GameObject.get_group_by_tag("lobby_screen")[0].enable()
    e = Engine(Vector2d(1200, 800))
    e.run()
    Client.object.sock.close()
    exit()

if __name__ == "__main__":
    load()
    launch()