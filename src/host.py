from netio.serialization.serializer import Serializable
from server.core import *
from server.core.game_event import GameEvent
from server.network import game, lobby
from server.network.game_server import GameServer
from server.globals.backup import BackupSettings
import socket, time, random, os
from engine_antiantilopa import Vector2d
from shared.loader import load_mains, load_effects_and_abilities_full
from shared.asset_types import *
from pathlib import Path
from netio import Host, MessageType, ConnectionData
from shared.player import PlayerData_

import logging

load_mains()
load_effects_and_abilities_full()

# GameEvent.start_recording()
# TODO
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

preload_data = None
name = None
# if len(saves) == 0:
#     print("No saves found. Starting a new game.")
# else:
#     while True:
#         preload_folder_index = (input("preload? (leave empty to start a new game/write folder index to continue): "))
#         if preload_folder_index:
#             try:
#                 preload_folder_index = int(preload_folder_index)
#                 if os.path.exists(saves_path / saves[preload_folder_index]):
#                     innersaves = os.listdir(saves_path / saves[preload_folder_index])
#                     if len(innersaves) == 0:
#                         print("No saves found in this folder.")
#                         name = saves[preload_folder_index]
#                         break
#                     print("Available turns:")
#                     for i in range(len(innersaves)):
#                         print(f"{i}) {innersaves[i]}")
#                     preload_file_index = int(input("write file index to continue: "))
#                 with open(saves_path / saves[preload_folder_index] / innersaves[preload_file_index], "rb") as f:
#                     try:
#                         preload_data = Serializator.decode_full(f.read())
#                         name = saves[preload_folder_index]
#                         print("preloaded successfully")
#                         a = str(preload_data)
#                         tabs = 0
#                         break
#                     except Exception as e:
#                         print(f"error while preloading: {e}")
#                         raise e
#             except Exception as e:
#                 print(f"wrong file index: {e}")
#                 raise e
#         else:
#             break


host = GameServer('localhost', 8080, 5)
host.router.merge(lobby.router)
host.router.merge(game.router)
print(host.router._event_handlers.keys())
if preload_data is None:
    print("Starting a new game.")
    if name is None:
        name = input("Enter the game's name: ")
        # os.mkdir(saves_path / name)
else:
    host.game = Game.from_serializable(preload_data)

BackupSettings.save_folder_name = name

@host.router.on_connect()
def at_connect(conn_data: ConnectionData) -> bool:
    if len(host.game_manager.players) == host.max_players:
        return False
    logging.info(f"Connection with someone established")
    return True

@host.router.on_disconnect()
def at_disconnect(player_data: PlayerData_):
    logging.info(f"Connection with {player_data.nickname} has lost.")
    if host.game_started:
        for player in host.game_manager.players:
            host.game_manager.send_message(player.address, MessageType.EVENT, "PLAYER_DISCONNECT", (player_data.nickname,))
        logging.info(f"{player_data.nickname} has disconnected from the game.")
        recovery_code = random.randint(100000, 999999)
        player_data.recovery_code = recovery_code
        # TODO player data save
        logging.warning(f"Recovery code: {recovery_code}")
        logging.info("Awaiting for player to reconnect...")

host.start()

def start_game():
    if preload_data is None:
        host.game = Game(Vector2d(17, 17), len(host.game_manager.players))
        for player in host.game_manager.players:
            host.send_message(player.address, MessageType.EVENT, "GAME_START", (0,))
        host.game.start()
    else:
        for player in host.game_manager.players:
            host.send_message(player.address, MessageType.EVENT, "GAME_START", (0,))
    host.create_all_objects()

try:
    host.game_starting = False
    while True:
        if not host.game_started:
            if host.game_starting:
                print(f"Game starting in {timer}...")
                for pl in host.game_manager.players:
                    host.send_message(pl.address, MessageType.EVENT, "MESSAGE", (timer,))
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

