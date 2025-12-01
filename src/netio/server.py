import socket
import threading
import time
from typing import Self

from .datatypes import PlayerData, ConnectionData, Address
from .serialization.routing import Writer, Reader, MessageType
from .serialization.serializer import Serializable, SpecialTypes, get_class_id
from . import router as Router
from .logger import serverLogger

class GameManager:
    conns: dict[Address, socket.socket]
    players: list[PlayerData]
    pdata_type: type[PlayerData]
    cdata_type: type[ConnectionData]
    
    _mapping: dict[Address, dict[int, bool]]
    _synchronized: list[Serializable]

    def __init__(
            self, 
            serializer: Writer, 
            router: "Router.ServerRouter",            
            player_data_type: type[PlayerData] = PlayerData, 
            connection_data_type: type[ConnectionData] = ConnectionData
            ):
        
        self.serializer = serializer
        self.router = router
        
        self.pdata_type = player_data_type
        self.cdata_type = connection_data_type
        self.conns = {}
        self.players = []

        self._synchronized = []
        self._mapping = {}

    def add_connection(self, conn: socket.socket, addr: Address):
        self.conns[addr] = conn
        self._mapping[addr] = {}

    def send_message(self, addr: Address, tp: MessageType, route: str, data: tuple):
        sock = self.conns[addr]
        serverLogger.debug("Server -> %s Route: %s", tp.name, route)
        self.serializer.encode(sock, (tp.value, route, data))

    def send_sync(self, addr: Address, data: tuple):
        self.send_message(addr, MessageType.SYNCHRONIZE, "", data)

    def send_del(self, addr: Address, data: tuple):
        self.send_message(addr, MessageType.DELETE, "", data)

    def send_create(self, addr: Address, data: tuple):
        self.send_message(addr, MessageType.CREATE, "", data)

    def create_object(self, obj: Serializable):
        assert not obj._primitive, "cannot create primitive object"
        for addr in self.conns.keys():
            data = obj.serialize()
            if obj.validate(self.get_player_data(addr)):
                self.send_message(addr, MessageType.CREATE, "", data)
                self._mapping[addr][obj._id] = True
                continue
            self._mapping[addr][obj._id] = False
        self._synchronized.append(obj)
        obj.is_created = True

    def delete_object(self, obj: Serializable):
        assert not obj._primitive, "cannot delete primitive object"
        for addr in self.conns.keys():
            if obj.validate(self.get_player_data(addr)):
                self.send_del(addr, (obj._id,))
            self._mapping[addr].pop(obj._id)
        self._synchronized.remove(obj)

    def handle_message(self, addr: Address, tp: int, route: str, data: tuple):
        match(tp):
            case MessageType.EVENT:
                serverLogger.event("Route: %s", route)
                self.router.fire_event(route, self.get_player_data(addr), data)
            case MessageType.REQUEST:
                resp = self.router.handle_request(route, self.get_player_data(addr), data)
                self.send_message(addr, MessageType.RESPONSE, route, resp)
            case MessageType.RESPONSE:
                self.router.handle_response(route, self.get_player_data(addr), data)
            case MessageType.CONNECT:
                connection_data = self.cdata_type.deserialize(data)
                if self.router._on_connect and not self.router._on_connect(connection_data):
                    self.disconnect_player(addr)
                    return
                player_data = self.pdata_type.create(addr, connection_data)
                serverLogger.info("New player connected: %s", player_data)
                self.players.append(player_data)
                self.create_object(player_data)
                self.synchronize()
                self.send_message(addr, MessageType.CONNECT, "", [player_data])
            case MessageType.ERROR:
                self.send_error(addr, "root", "Ты офигел?")
                serverLogger.error("client sent error: %s", data)

    def get_player_data(self, addr: Address):
        for i in self.players:
            if i.address == addr:
                return i
        raise KeyError("No player with address: ", addr)

    def send_error(self, addr: Address, route: str, details: str):
        sock = self.conns[addr]
        serverLogger.error("Client error. Route: %s Details: %s", route, details)
        self.serializer.encode(sock, (MessageType.ERROR.value, route, (details,)))
    
    def synchronize(self):
        for addr, con in self.conns.items():
            for obj in self._synchronized:
                udata = obj.serialize_updates()
                pr1, pr2 = obj.validate(self.get_player_data(addr)), self._mapping[addr].get(obj._id, False)

                if udata != SpecialTypes.NOTHING and pr1 and pr2:
                    serverLogger.debug("Object %s synchronized with %s", obj._id, addr)
                    self.send_sync(addr, udata)
                elif not pr1 and pr2:
                    serverLogger.debug("Object %s deleted from %s", obj._id, addr)
                    self.send_del(addr, (obj._id,))
                elif pr1 and not pr2:
                    serverLogger.debug("Object %s created for %s", obj._id, addr)
                    self.send_create(addr, obj.serialize())
                
                self._mapping[addr][obj._id] = pr1
                    
        for obj in self._synchronized:
            obj._clear_updates()
    
    def disconnect_player(self, addr: Address):
        conn = self.conns[addr]
        self.conns.pop(addr)
        self._mapping.pop(addr)
        player_data = [i for i in self.players if i.address == addr][0]
        self.players.remove(player_data)
        self.delete_object(player_data)
        conn.close()
        
    def close(self):
        for i in self.conns.values():
            i.close()          
              
class Host:
    sock: socket.socket

    def __init__(
            self, 
            host: str, 
            port: int, 
            router: "Router.ServerRouter" = None, 
            player_data_type: type[PlayerData] = PlayerData, 
            connection_data_type: type[ConnectionData] = ConnectionData,
            game_manager_type: type[GameManager] = GameManager):
        self.serializer = Writer()
        self.deserializer = Reader()
        if router is None:
            router = Router.ServerRouter()
        self.router = router
        router.host = self
        self.game_manager = game_manager_type(self.serializer, router, player_data_type, connection_data_type)

        self.sock = socket.socket()
        self.sock.settimeout(1)
        self.sock.bind((host, port))
        self.sock.listen()
        serverLogger.info("Listening on port: %s, ip: %s", port, host)

    def send_message(self, addr: Address, tp: MessageType, route: str, data: tuple):
        self.game_manager.send_message(addr, tp, route, data)

    def await_connection(self):
        while True:
            try:
                conn, addr = self.sock.accept()
            except socket.timeout:
                continue

            serverLogger.info("New socket connection, ip: %s, port: %s", *addr)
            conn.settimeout(1)
            self.game_manager.add_connection(conn, addr)
            t = threading.Thread(target=self.handle_connection, args=[addr])
            t.start()

    def create_object(self, obj: Serializable):
        serverLogger.debug("Requesting creating object... %s", obj._id)
        self.game_manager.create_object(obj)
    
    def delete_object(self, obj: Serializable):
        serverLogger.debug("Deleting object... %s", obj._id)
        self.game_manager.delete_object(obj)

    def synchronize(self):
        serverLogger.debug("Synchronizing objects...")
        self.game_manager.synchronize()

    def handle_connection(self, addr: tuple):
        try:
            while True:
                try:
                    tp, route, data = self.deserializer.get_message(self.game_manager.conns[addr])
                    serverLogger.debug("%s -> %s Route: %s", addr[0], tp.name, route)
                    self.game_manager.handle_message(addr, tp, route, data)
                except socket.timeout:
                    pass
        except ConnectionResetError:
            serverLogger.error(f"ConnectionResetError with {addr}")
            return
        except UnicodeDecodeError:
            serverLogger.error(f"UnicodeDecodeError with {addr}")
            return
        except Exception as e:
            raise e
        finally:
            try:
                if self.router._on_disconnect:
                    self.router._on_disconnect(self.game_manager.get_player_data(addr))
            finally:
                self.game_manager.disconnect_player(addr)

    def start(self):
        t = threading.Thread(target=self.await_connection)
        t.start()

    def close(self):
        self.game_manager.close()
        self.sock.close()