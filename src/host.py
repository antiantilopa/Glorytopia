from serializator.host import Address
from serializator.data_format import Format
from server.core import *
from server.respondings import lobby, game
from server.respondings.server import Server
import socket, time, random
from engine_antiantilopa import Vector2d
from shared.loader import load_mains

load_mains()

# random.seed(0)

password = input("input password for admin: ")

host = Server()
host.password = password
host.respond.merge(lobby.respond)
host.respond.merge(game.respond)


@host.respond.connection()
def at_connect(self: Server, conn: socket.socket, addr: Address) -> bool:
    if len(self.addrs_to_names) == self.player_number:
        self.send_to_conn(conn, Format.error("CONNECTION", ["this server is already full."]))
        conn.close()
        return False
    print(f"Connection with {addr} established")
    return True

@host.respond.disconnection()
def at_disconnect(self: Server, addr: Address):
    print(f"Connection with {addr} has lost.")
    if addr in self.addrs_to_names:
        if not self.game_started:
            for i in self.conns:
                self.send_to_addr(i, Format.event("DISCONNECT", [self.addrs_to_names[addr]]))
            self.names_to_colors.pop(self.addrs_to_names[addr], None)
            self.names_to_addrs.pop(self.addrs_to_names[addr], None)
            self.addrs_to_names.pop(addr)
            self.readiness.pop(addr)
            self.order.remove(addr)
            for i in self.readiness:
                self.readiness[i] = False
        else:
            for i in self.conns:
                self.send_to_addr(i, Format.event("GAME/DISCONNECT", [self.addrs_to_names[addr]]))
            print(f"{self.addrs_to_names[addr]} has disconnected from the game.")
            recovery_code = random.randint(100000, 999999)
            self.recovery_codes[self.addrs_to_names[addr]] = recovery_code
            print(f"recovery code: {recovery_code}")
            print("awaiting for players to reconnect...")
    
@host.respond.request("ORDER")
def req_order(self: Server, addr: Address, _: tuple):
    self.send_to_addr(addr, Format.info("ORDER", [self.addrs_to_names[addr1] for addr1 in self.order]))

host.init_server(8)
host.start()

for r in host.respond.routes:
    print(r)

def start_game():
    host.the_game = Game(Vector2d(17, 17), len(host.addrs_to_names))
    for addr in host.order:
        host.players[addr] = host.the_game.players[host.order.index(addr)]
        host.send_to_addr(addr, Format.event("GAME/GAME_START", [0, host.order.index(addr)]))
    symbol_terrain = "_~=+^"
    for i in range(host.the_game.world.size.y):
        for j in range(host.the_game.world.size.x):
            print(symbol_terrain[host.the_game.world[i][j].ttype.id], end = " ")
        print()

try:
    while True:
        if not host.game_started:
            if host.game_starting:
                print(timer)
                for addr in host.addrs_to_names:
                    host.send_to_addr(addr, Format.event("LOBBY/GAME_START", [timer]))
                    host.send_to_addr(addr, Format.event("LOBBY/MESSAGE", ("GAME STARTS IN", f"{timer}...")))
                timer -= 1
                time.sleep(1)
                if timer == 0:
                    host.game_started = True
                    start_game()
            else:
                timer = 3
        elif host.game_started:
            a = input()
            try:
                exec(a)
            except Exception as e:
                print(f"error: {e}")
except Exception as e:
    print(f"ERROR OCCURED: {e}")
    print(e.with_traceback())

