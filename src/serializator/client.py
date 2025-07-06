from .net import Serializator
from .data_format import Format, REQUEST, INFO, EVENT, ERROR

import socket, threading
from typing import Any, Callable

Address = tuple[str, int]
Route = tuple[str, str]


def default_main_cycle(_):
    try:
        while not Client.object.changing_main_cycle:
            pass
    except KeyboardInterrupt:
        exit()

class Respond:
    default: str
    routes: dict[Address, Callable[["Client", Any], Any]]
    at_connect: Callable[["Client"], Any]
    at_disconnect: Callable[["Client"], Any]

    def __init__(self, default: str = ""):
        self.routes = {}
        self.default = default
        self.at_connect = lambda client: None
        self.at_disconnect = lambda client: None

    def request(self, route: str|None = None):
        if route is None:
            route = ""
        if self.default != "":
            route = self.default + "/" + route
        def decor(func):
            self.routes[(REQUEST, route)] = func
            return func
        return decor

    def info(self, route: str|None = None):
        if route is None:
            route = ""
        if self.default != "":
            route = self.default + "/" + route
        def decor(func):
            self.routes[(INFO, route)] = func
            return func
        return decor
    
    def event(self, route: str|None = None):
        if route is None:
            route = ""
        if self.default != "":
            route = self.default + "/" + route
        def decor(func):
            self.routes[(EVENT, route)] = func
            return func
        return decor

    def error(self, route: str|None = None):
        if route is None:
            route = ""
        if self.default != "":
            route = self.default + "/" + route
        def decor(func):
            self.routes[(ERROR, route)] = func
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

    def merge(self, other: "Respond"):
        for route, func in other.routes.items():
            if route not in self.routes:
                self.routes[route] = func
            else:
                raise ValueError(f"Route {route} already exists in the current Respond object.")

class Client:
    sock: socket.socket
    respond: "Respond"
    object: "Client" = None

    main_cycle: Callable[[None], None]
    main_cycle_thread: threading.Thread
    changing_main_cycle: bool

    def __init__(self):
        self.sock = None
        self.respond = Respond()
        self.main_cycle = default_main_cycle
        self.main_cycle_thread = None
        self.changing_main_cycle = False
        Client.object = self

    def init(self):
        pass

    def routing_respond(self, message: Any):
        route = tuple((message[0], message[1]))
        default_route = message[0]
        if route in self.respond.routes:
            self.respond.routes[route](self, message[2])
        elif default_route in self.respond.routes:
            self.respond.routes[default_route](self, message[2])
        else:
            print(f"cant find route {message[0]}/{message[1]}")

    def set_main_cycle(self, func: Callable[["Client"], None]):
        self.main_cycle = func
        return func

    def send(self, message: Any):
        self.sock.send(Serializator.encode(message))

    def recv(self) -> Any:
        return Serializator.decode_with_batching(self.sock)

    def init_client(self, IPaddr: tuple[str, int] = socket.gethostbyname(socket.gethostname())):
        self.sock = socket.socket()
        self.sock.connect(IPaddr)
        print("connected)")
        self.respond.at_connect(self)
        self.init()

    def await_message(self):
        try:
            while True:
                message = Serializator.decode_with_batching(self.sock)
                self.routing_respond(message)
        except Exception as e:
            print(f"error occured: {e}")
            self.respond.at_disconnect(self)
            raise e

    def start(self):
        t = threading.Thread(target=self.await_message)
        t.start()
        t = threading.Thread(target=self.main_cycle, args=[self])
        self.main_cycle_thread = t
        t.start()
    
    def change_main_cycle(self, func: Callable[["Client"], None]):
        self.changing_main_cycle = True
        self.main_cycle = func
        if self.main_cycle_thread is not None:
            if threading.current_thread() != self.main_cycle_thread:
                if self.main_cycle_thread.is_alive():
                    self.main_cycle_thread.join()
        old_main_cycle_thread = self.main_cycle_thread
        self.changing_main_cycle = False
        self.main_cycle_thread = threading.Thread(target=self.main_cycle, args=[self])
        self.main_cycle_thread.start()
        if old_main_cycle_thread is not None:
            if threading.current_thread() == self.main_cycle_thread:
                exit()
        return func