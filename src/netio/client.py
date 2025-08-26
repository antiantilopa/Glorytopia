import socket
import threading

from .serialization.serializer import Serializable
from .datatypes import ConnectionData, PlayerData
from .serialization.routing import Writer, Reader, MessageType
from .router import ClientRouter
from .logger import clientLogger


class Client:
    
    _objects: list[Serializable]

    def __init__(
            self, 
            host: str, 
            port: int, 
            router: ClientRouter = ClientRouter(), 
            pdata_type: type[PlayerData] = PlayerData
            ):
        self.address = (host, port)
        self.router = router
        self.router.client = self
        
        self.pdata_type = pdata_type
        self._objects = []
        self.deserializer = Reader()
        self.serializer = Writer()

        self.sock = self.init_connection(ConnectionData().serialize())

    def init_connection(self, connection_data: tuple) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.address)
        self.serializer.send_message(sock, MessageType.CONNECT, "", connection_data)
        clientLogger.info("Connected to the server.")
        return sock
    
    def send_message(self, tp: MessageType, route: str, data: tuple):
        clientLogger.debug("%s -> Route: %s", tp.name, route)
        self.serializer.encode(self.sock, (tp.value, route, data))

    def await_message(self):
        try:
            while True:
                tp, route, data = self.deserializer.get_message(self.sock)
                match(tp):
                    case MessageType.EVENT:
                        clientLogger.event("Route: %s", route)
                        self.router.fire_event(route, data)
                    case MessageType.RESPONSE:
                        self.router.handle_response(route, data)
                    case MessageType.REQUEST:
                        self.router.handle_request(route, data)
                    case MessageType.CONNECT:
                        raise ValueError("WTF?")
                    case MessageType.CREATE:
                        clientLogger.info("Creating new object with id: %s", data[1])
                        obj = Serializable.deserialize(data)
                        self._objects.append(obj)
                        obj.client_on_create()
                    case MessageType.SYNCHRONIZE:
                        obj = [i for i in self._objects if i._id == data[1]]
                        if len(obj) == 0:
                            clientLogger.error("Object not found. ID: %s", data[1])
                            continue
                        obj = obj[0]
                        obj.deserialize_updates(data)
                        clientLogger.info("Synchronized. Object ID: %s", data[1])
                    case MessageType.DELETE:
                        obj = [i for i in self._objects if i._id == data[0]]
                        if len(obj) == 0:
                            clientLogger.error("Object not found. ID: %s", data[0])
                            continue
                        obj = obj[0]
                        self._objects.remove(obj)
                        obj.client_on_destroy()
                        clientLogger.info("Deleted. Object ID: %s", data[0])
                    case MessageType.ERROR:
                        clientLogger.error("Server returned error. Route: %s, Details: %s", route, data[0])
        except Exception as e:
            print(f"Error occured: {e}")
            raise e

    def start(self):
        t = threading.Thread(target=self.await_message)
        t.start()

    def close(self):
        self.sock.close()
