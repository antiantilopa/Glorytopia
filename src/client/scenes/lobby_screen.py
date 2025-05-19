from engine_antiantilopa import *
from client.respondings.client import Client
from client.respondings.lobby import respond, UpdateCodes
from client.widgets.fastgameobjectcreator import *
from serializator.data_format import Format
import pygame as pg

scene = GameObject("lobby_screen")

scene.add_component(Transform())
scene.add_component(SurfaceComponent(Vector2d(1200, 800)))
GameObject.root.add_child(scene)

chat_section = create_game_object(scene, "lobby_screen:chat_section", Position.RIGHT, (600, 800), ColorComponent.WHITE, Shape.RECTBORDER, 2)

message_section = create_game_object(chat_section, "lobby_screen:chat_section:message_section", Position.UP, (600, 730), ColorComponent.WHITE, Shape.RECTBORDER, 2)
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
message_section.add_component(KeyBindComponent([pg.K_UP, pg.K_DOWN], 0, 1, scroll))
entry_box = create_game_object(chat_section, "lobby_screen:chat_section:entry_box", Position.LEFT_DOWN, Vector2d(600, 70), ColorComponent.WHITE, Shape.RECTBORDER, 2, margin=Vector2d(6, 6))
entry_obj = create_game_object(entry_box, "lobby_screen:chat_section:entry_box:entry", Position.CENTER, Vector2d(600, 70), ColorComponent.RED, margin=Vector2d(2, 2))
entry_obj.add_component(EntryComponent(active=True, font=pg.font.SysFont("consolas", 20)))
def message(g_obj: GameObject, *_):
    text = g_obj.get_component(EntryComponent).text
    c = Client.object
    c.send(Format.event("LOBBY/MESSAGE", [text]))
    g_obj.get_component(EntryComponent).clear()

entry_obj.add_component(KeyBindComponent([pg.K_RETURN], 0, 1, message))

ready_section = create_game_object(scene, "lobby_screen:ready_section", Position.LEFT_UP, (600, 300), ColorComponent.WHITE, Shape.RECTBORDER, 2)

info_section = create_game_object(scene, "lobby_screen:info_section", Position.LEFT_DOWN, Vector2d(600, 500), ColorComponent.WHITE, Shape.RECTBORDER, 2)

ready_button = create_game_object(info_section, "lobby_screen:info_section:ready_button", Position.LEFT_UP, Vector2d(70, 70), ColorComponent.RED, Shape.RECT, margin=Vector2d(10, 10))

def ready(*_):
    c = Client.object
    c.send(Format.event("LOBBY/READY", [1 - c.readiness[c.myname]]))

ready_button.add_component(OnClickComponent([1, 0, 0], 0, 1, ready))

scene.disable()

def init():
    @Client.object.set_main_cycle
    def update(self: Client):
        while True:
            if self.updated == 0:
                continue
            if self.updated & 2 ** UpdateCodes.JOIN.value:
                num = len(self.names) - 1
                n = create_game_object(ready_section, ["lobby_screen:ready_section:name", str(num)], at=InGrid((1, 6), (0, num)), color=ColorComponent.WHITE, width=2, shape=Shape.RECTBORDER, margin=Vector2d(10, 3))
                l1 = create_label(n, tags="lobby_screen:ready_section:name:name_label", text = self.names[num], at=Position.LEFT, color=ColorComponent.GREEN if self.names[num] == Client.object.myname else ColorComponent.RED, margin=Vector2d(10, 3))
                l2 = create_label(n, tags="lobby_screen:ready_section:name:ready_label", at = Position.RIGHT, text="X", color=ColorComponent.RED, margin=Vector2d(10, 3))
                n.first_iteration()
                l1.first_iteration()
                l2.first_iteration()
                for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name:ready_label"):
                    g.get_component(LabelComponent).text = "X"
                    g.need_draw_set_true()
                    g.need_blit_set_true()
            if self.updated & 2 ** UpdateCodes.DISCONNECT.value:
                num = len(self.names) - 1
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
                        l1 = create_label(g, tags="lobby_screen:ready_section:name:name_label", text = self.names[int(g.tags[1])], at=Position.LEFT, color=ColorComponent.GREEN if self.names[num] == Client.object.myname else ColorComponent.RED, margin=Vector2d(10, 3))
                        l1.first_iteration()
                for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name:ready_label"):
                    g.get_component(LabelComponent).text = "X"
                    g.need_draw_set_true()
                    g.need_blit_set_true()
            if self.updated & 2 ** UpdateCodes.READY.value:
                for g in GameObject.get_group_by_tag("lobby_screen:ready_section:name:ready_label"):
                    g.get_component(LabelComponent).text = ("X", "O")[int(self.readiness[self.names[int(g.parent.tags[1])]])]
                    g.need_draw_set_true()
                    g.need_blit_set_true()
            if self.updated & 2 ** UpdateCodes.INIT_NAMES.value:
                for child in ready_section.childs:
                    child.destroy()
                for num in range(len(self.names)):
                    n = create_game_object(ready_section, ["lobby_screen:ready_section:name", str(num)], at=InGrid((1, 6), (0, num)), color=ColorComponent.WHITE, width=2, shape=Shape.RECTBORDER, margin=Vector2d(10, 3))
                    l1 = create_label(n, tags="lobby_screen:ready_section:name:name_label", text = self.names[num], at=Position.LEFT, color=ColorComponent.GREEN if self.names[num] == Client.object.myname else ColorComponent.RED, margin=Vector2d(10, 3))
                    l2 = create_label(n, tags="lobby_screen:ready_section:name:ready_label", at = Position.RIGHT, text="X", color=ColorComponent.RED, margin=Vector2d(10, 3))
            if self.updated & 2 ** UpdateCodes.MESSAGE.value:
                message_section.disable()
                for child in message_section.childs:
                    child.get_component(Transform).move(Vector2d(0, -(message_section.get_component(SurfaceComponent).size.y // 15)))
                for i in range(len(message_section.childs), len(self.messages)):
                    n = create_game_object(message_section, "lobby_screen:chat_section:mesage_section:message_box", at=InGrid((1, 15), (0, 14)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, margin = Vector2d(3, 3))
                    l = create_label(n, "lobby_screen:chat_section:mesage_section:message_box:message_label", at=Position.LEFT, text=f"{self.messages[i][0]}: {self.messages[i][1]}", font=pg.font.SysFont("consolas", 20), color=ColorComponent.RED, margin=Vector2d(10, 2))
                message_section.enable()
            print(bin(self.updated))
            self.updated = UpdateCodes.NOTHING.value

def launch():
    scene.enable()
    e = Engine(Vector2d(1200, 800))
    e.run()
    Client.object.sock.close()
    exit()

if __name__ == "__main__":
    launch()