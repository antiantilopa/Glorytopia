from .net import Serializator
from .data_format import Format, REQUEST, INFO, EVENT, ERROR

import socket, threading
from typing import Any, Callable

Address = tuple[str, int]

def default_main_cycle():
        try:
            while True:
                pass
        except KeyboardInterrupt:
            exit()

class Client:
    sock: socket.socket
    respond: "__Respond"

    main_cycle: Callable[[None], None]

    class __Respond:
        routes: dict[Address, Callable[["Client", Any], Any]]
        at_connect: Callable[["Client"], Any]
        at_disconnect: Callable[["Client"], Any]

        def __init__(self):
            self.routes = {}
            self.at_connect = lambda client: None
            self.at_disconnect = lambda client: None

        def request(self, route: str|None = None):
            if route is not None:
                def decor(func):
                    self.routes[(REQUEST, route)] = func
                    return func
                return decor
            else:
                def decor(func):
                    self.routes[REQUEST] = func
                    return func
                return decor

        def info(self, route: str|None = None):
            if route is not None:
                def decor(func):
                    self.routes[(INFO, route)] = func
                    return func
                return decor
            else:
                def decor(func):
                    self.routes[INFO] = func
                    return func
                return decor
        
        def event(self, route: str|None = None):
            if route is not None:
                def decor(func):
                    self.routes[(EVENT, route)] = func
                    return func
                return decor
            else:
                def decor(func):
                    self.routes[EVENT] = func
                    return func
                return decor

        def error(self, route: str|None = None):
            if route is not None:
                def decor(func):
                    self.routes[(ERROR, route)] = func
                    return func
                return decor
            else:
                def decor(func):
                    self.routes[ERROR] = func
                    return func
                return decor
        
        def connection(self):
            def decor(func):
                self.at_connect = func
                return func
            return decor
        
        def disconnection(self):
            def decor(func):
                self.at_disconnect = func
                return func
            return decor

    def __init__(self):
        self.respond = Client.__Respond()
        self.main_cycle = default_main_cycle

    def init(self):
        pass

    def routing_respond(self, message: Any):
        route = tuple((message[0], message[1]))
        default_route = message[0]
        if route in self.respond.routes:
            self.respond.routes[route](self, message[2])
        elif default_route in self.respond.routes:
            self.respond.routes[default_route](self, message[2])

    def set_main_cycle(self, func: Callable):
        self.main_cycle = func
        return func

    def send(self, message: Any):
        self.sock.send(Serializator.encode(message))

    def recv(self) -> Any:
        return Serializator.decode_with_batching(self.sock)

    def init_client(self, IPaddr: tuple[str, int] = socket.gethostbyname(socket.gethostname())):
        self.sock = socket.socket()
        self.sock.connect(IPaddr)
        self.respond.at_connect(self)
        self.init()

    def await_message(self):
        try:
            while True:
                message = Serializator.decode_with_batching(self.sock)
                self.routing_respond(message)
        except:
            self.respond.at_disconnect(self)

    def start(self):
        t = threading.Thread(target=self.await_message)
        t.start()
        self.main_cycle()
