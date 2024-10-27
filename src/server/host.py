import socket
import asyncio
from enum import Enum

from src.shared.net import PlayerConn

class GameStatus(Enum):
    IN_LOBBY = 0
    IN_GAME = 1
    
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
        print("Game started", data, flush=True)

    async def handle_connections(self):
        for i in range(self.player_count):
            conn, address = self.server.accept()

            cn = PlayerConn(conn)
            cn.load_name()
            self.player_conns.append(cn)
            print(f"Player {cn.name} connected")
            cn.on("start", lambda x: self.start(x))
            asyncio.ensure_future(cn.load())
        while True:
            await asyncio.sleep(1)

# async def main():
#     host = Host(1)
#     print("Server started", flush=True)
#     await host.handle_connections()


# loop = asyncio.get_event_loop()

# if __name__ == "__main__":
#     asyncio.run(main())

            
