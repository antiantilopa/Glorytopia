from serializator.host import Address
from serializator.data_format import Format
from serializator.net import Serializator
from server.core import *
from server.core.game_event import GameEvent
from server.network import game, lobby
from server.network.server import Server, Connection
from server.globals.backup import BackupSettings
import socket, time, random, os
from engine_antiantilopa import Vector2d
from shared.loader import load_mains
from shared.asset_types import *
from pathlib import Path

load_mains()
GameEvent.start_recording()
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
                with open(saves_path / saves[preload_folder_index] / innersaves[preload_file_index], "rb") as f:
                    try:
                        preload_data = Serializator.decode_full(f.read())
                        name = saves[preload_folder_index]
                        print("preloaded successfully")
                        a = str(preload_data)
                        tabs = 0
                        break
                    except Exception as e:
                        print(f"error while preloading: {e}")
                        raise e
            except Exception as e:
                print(f"wrong file index: {e}")
                raise e
        else:
            break


host = Server()
host.password = "Ha-Ha-Ha Rana"
host.respond.merge(lobby.respond)
host.respond.merge(game.respond)

if preload_data is None:
    print("Starting a new game.")
    if name is None:
        name = input("Enter the game's name: ")
        os.mkdir(saves_path / name)
else:
    host.the_game = Game.from_serializable(preload_data)

BackupSettings.save_folder_name = name

@host.respond.connection()
def at_connect(self: Server, conn: socket.socket, addr: Address) -> bool:
    if len(Connection.conns) == self.player_number:
        self.send_to_conn(conn, Format.error("CONNECTION", ["this server is already full."]))
        conn.close()
        return False
    print(f"Connection with {addr} established")
    return True

@host.respond.disconnection()
def at_disconnect(self: Server, addr: Address):
    print(f"Connection with {addr} has lost.")
    if addr in [conn.addr for conn in Connection.conns]:
        if not self.game_started:
            for i in self.conns:
                self.send_to_addr(i, Format.event("DISCONNECT", [Connection.get_by_addr(addr).name]))
            removed_idx = Connection.get_by_addr(addr).idx
            Connection.conns.remove(Connection.get_by_addr(addr))
            Connection.IDX -= 1
            for conn in Connection.conns:
                if conn.idx > removed_idx:
                    conn.idx -= 1
                conn.ready = False
        else:
            for i in self.conns:
                self.send_to_addr(i, Format.event("GAME/DISCONNECT", [Connection.get_by_addr(addr).name]))
            print(f"{Connection.get_by_addr(addr).name} has disconnected from the game.")
            recovery_code = random.randint(100000, 999999)
            Connection.get_by_addr(addr).recovery_code = recovery_code
            print(f"recovery code: {recovery_code}")
            print("awaiting for player to reconnect...")
    
@host.respond.request("ORDER")
def req_order(self: Server, addr: Address, _: tuple):
    self.send_to_addr(addr, Format.info("ORDER", [conn.name for conn in Connection.conns]))

host.init_server(6)
host.start()

def start_game():
    if preload_data is None:
        host.the_game = Game(Vector2d(17, 17), len(Connection.conns))
        for conn in Connection.conns:
            conn.player = host.the_game.players[conn.idx]
            conn.player.set_nation(Nation.by_id(conn.nation))
            host.send_to_addr(conn.addr, Format.event("GAME/GAME_START", [0, conn.idx]))
        host.the_game.start()
    else:
        for conn in Connection.conns:
            conn.player = host.the_game.players[conn.idx]
            host.send_to_addr(conn.addr, Format.event("GAME/GAME_START", [0, conn.idx]))

try:
    while True:
        if not host.game_started:
            if host.game_starting:
                for conn in Connection.conns:
                    host.send_to_addr(conn.addr, Format.event("LOBBY/GAME_START", [timer]))
                    host.send_to_addr(conn.addr, Format.event("LOBBY/MESSAGE", ("GAME STARTS IN", f"{timer}...")))
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

