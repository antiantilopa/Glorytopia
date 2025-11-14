from engine_antiantilopa import *
from client.globals.music import SoundManager

from client.network.client import GameClient
from client.scenes.game_screen import main
from netio.serialization.routing import MessageType
from shared.util.position import Pos

def launch_game_screen(now_playing_player_id: int, world_size: Pos):
    GameClient.object.me.money = 0
    GameClient.object.me.techs = []
    GameClient.object.send_message(MessageType.REQUEST, "GAME/MONEY", None)
    GameClient.object.send_message(MessageType.REQUEST, "GAME/TECHS", None)
    scene = GameObject.get_game_object_by_tags("lobby_screen")
    scene.destroy()
    SoundManager.stop_music()
    main.init(now_playing_player_id, world_size)
    main.load()
    main.start()