from netio.serialization.serializer import Serializable
from server.backup import loader
from server.core import *
from server.network import game, lobby
from server.network.game_server import GamePlayer, GameServer
from server.globals.backup import BackupSettings
import socket, time, random, os
from engine_antiantilopa import Vector2d
from shared.loader import load_mains, load_effects_and_abilities_full
from shared.asset_types import *
from pathlib import Path
from netio import Host, MessageType, ConnectionData
from server.recorder.replay_recorder import ReplayRecorder
import logging

load_mains()
load_effects_and_abilities_full()

saves_path = BackupSettings.saves_path

if os.path.exists(saves_path):
    saves = os.listdir(saves_path)
    if len(saves) > 0:
        print("Available saves:")
        for i in range(len(saves)):
            print(f"{i}) {saves[i]}")
else:
    os.mkdir(saves_path)
    saves = []


new_game = True
player_datas = []

name = f"save_{int(time.time())}"
inner_save = "turn0-0.save"
if len(saves) == 0:
    print("No saves found. Starting a new game.")
else:
    while True:
        preload_folder_index = (input("preload? (leave empty to start a new game/write folder index to continue): "))
        if preload_folder_index:
            try:
                preload_folder_index = int(preload_folder_index)
                if os.path.exists(saves_path / saves[preload_folder_index]):
                    innersaves = os.listdir(saves_path / saves[preload_folder_index])
                    if len(innersaves) == 0:
                        print("No saves found in this folder.")
                        name = saves[preload_folder_index]
                        break
                    print("Available turns:")
                    for i in range(len(innersaves)):
                        print(f"{i}) {innersaves[i]}")
                    preload_file_index = int(input("write file index to continue: "))
                if os.path.exists(saves_path / saves[preload_folder_index] / innersaves[preload_file_index]):
                    try:
                        new_game = False
                        name = saves[preload_folder_index]
                        inner_save = innersaves[preload_file_index]
                        print("found successfully")
                        save_path = Path(saves_path / name / inner_save)
                        player_datas = loader.load(save_path)
                        break
                    except Exception as e:
                        print(f"error while finding file: {e}")
                        raise e
            except Exception as e:
                print(f"wrong file index: {e}")
                raise e
        else:
            break

host = GameServer('localhost', 8080, 5)
host.router.merge(lobby.router)
host.router.merge(game.router)
print(host.router._event_handlers.keys())

BackupSettings.save_folder_name = name

@host.router.on_connect()
def at_connect(conn_data: ConnectionData) -> bool:
    if len(host.game_manager.players) == host.max_players:
        return False
    if not new_game:
        if len(host.game_manager.players) == len(player_datas):
            return False
    logging.info(f"Connection with someone established")
    return True

@host.router.on_disconnect()
def at_disconnect(player_data: GamePlayer):
    if not player_data.joined:
        return
    
    GamePlayer.joined_players.remove(player_data)
    logging.info(f"Connection with {player_data.nickname} has lost.")
    if not host.game_started:
        for pdata in GamePlayer.joined_players:
            host.send_message(pdata.address, MessageType.EVENT, "LOBBY/DISCONNECT", player_data.nickname)
    if host.game_started:
        for pdata in GamePlayer.joined_players:
            host.send_message(pdata.address, MessageType.EVENT, "GAME/DISCONNECT", player_data.nickname)
        logging.info(f"{player_data.nickname} has disconnected from the game.")
        recovery_code = random.randint(100000, 999999)
        player_data.recovery_code = recovery_code
        save_obj = GamePlayer.new_copy_from(player_data)
        GamePlayer.need_reconnect.append(save_obj)
        logging.warning(f"Name: {player_data.nickname}, Recovery code: {recovery_code}")

host.start()

def start_game():
    if new_game:
        host.game = Game(Vector2d(17, 17), len(host.game_manager.players))
        i = 0
        for pdata in GamePlayer.joined_players:
            pdata.id = i
            Player.by_id(i).set_pdata(pdata)
            i += 1
        host.game.start()
    
        host.synchronize()
        for player in GamePlayer.joined_players:
            host.send_message(player.address, MessageType.EVENT, "LOBBY/GAME_START", (0, host.game.world.size))
    else:
        host.game = Game.obj
        for pdata in GamePlayer.joined_players:
            for loaded_pdata in player_datas:
                if pdata.nickname == loaded_pdata.nickname:
                    pdata.id = loaded_pdata.id
                    pdata.color = loaded_pdata.color
                    pdata.nation = loaded_pdata.nation
                    Player.by_id(pdata.id).set_pdata(pdata)
                    break
        host.game.start()
    
        host.synchronize()
        for player in GamePlayer.joined_players:
            host.send_message(player.address, MessageType.EVENT, "LOBBY/GAME_START", (0, host.game.world.size))

    host.create_all_objects()
    host.synchronize()
    ReplayRecorder.start_recording()

try:
    host.game_starting = False
    while True:
        if not host.game_started:
            if host.game_starting:
                print(f"Game starting in {timer}...")
                for pl in host.game_manager.players:
                    host.send_message(pl.address, MessageType.EVENT, "LOBBY/MESSAGE", ("SERVER", str(timer)))
                timer -= 1
                time.sleep(1)
                if timer == 0:
                    host.game_started = True
                    start_game()
            else:
                timer = 3
        elif host.game_started:
            try:
                a = input()
                exec(a)
            except Exception as e:
                print(f"error: {e}")
except Exception as e:
    print(f"ERROR OCCURED: {e}")
    print(e.with_traceback())

