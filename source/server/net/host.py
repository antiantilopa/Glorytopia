import socket
import asyncio
from enum import Enum
from typing import Callable


SEPARATOR = 0x00

class GameStatus(Enum):
    IN_LOBBY = 0
    IN_GAME = 1

class PlayerConn:
    conn: socket.socket
    name: str
    _listeners: dict[str, list[Callable]]

    def __init__(self, conn, name) -> None:
        self.conn = conn
        self.name = name
        self._listeners = {}

    def on(self, event: str, listener: Callable):
        self._listeners[event].append(listener)

    def emit(self, event: str, data: bytes):
        self.conn.send(event.encode())
        self.conn.send(SEPARATOR)
        self.conn.send(data)

    async def load(self):
        while True:
            bts = self.conn.recv(1024)
            idx = 0
            for i in bts:
                if i == SEPARATOR:
                    idx = i
                    break
            name = bts[:idx].decode()
            data = bts[idx+1:]

            self._listeners[name](data)
    
class Host:
    server: socket.socket
    status: GameStatus
    player_conns: list[PlayerConn]

    def __init__(self, player_count) -> None:
        self.server = socket.socket()
        self.status = GameStatus.IN_LOBBY
        self.player_count = player_count
        self.player_conns = []
        self.server.bind(('localhost', 9090))
        self.server.listen(player_count)
    
    def start(self, data):
        print("Game started")

    async def handle_connections(self):
        for i in range(self.player_count):
            conn, address = self.server.accept()

            # Initial data
            name = conn.recv(1024).decode()
            cn = PlayerConn(conn, name)
            self.player_conns.append(cn)
            print(f"Player {name} connected")
            cn.on("start", lambda x: self.start)


async def task():
    sock = socket.socket()
    sock.connect(('localhost', 9090))
    sock.send("Player1".encode())
    
    h = PlayerConn(sock, "Player1")
    h.emit("start", b"aa")

async def hd():
    host = Host(1)
    print("Server started", flush=True)
    await host.handle_connections()

loop = asyncio.get_event_loop()

async def main():
    f1 = loop.create_task(hd())
    f2 = loop.create_task(task())
    await asyncio.wait([f1, f2])

if __name__ == "__main__":
    asyncio.run(main())

            
