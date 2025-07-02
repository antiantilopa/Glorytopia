from .net import Serializator
from .data_format import Format, INFO, REQUEST, EVENT, ERROR

import ipaddress
import socket, threading, time
from typing import Any, Callable

def validate_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

Address = tuple[str, int]
Route = tuple[str, str]

class Respond:
    default: str
    routes: dict[Route, Callable[["Host", Address, Any], Any]]
    at_connect: Callable[["Host", socket.socket, Address], bool]
    at_disconnect: Callable[["Host", Address], Any]

    def __init__(self, default: str = ""):
        self.default = default
        self.routes = {}

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



class Host:
    conns: dict[Address, socket.socket]
    sock: socket.socket
    player_number: int
    alive: bool
    respond: "Respond"

    def __init__(self):
        self.alive = True
        self.conns = {}
        self.respond = Respond()
        with open("logs.txt", "w") as f:
            f.write("LOGGING START\n")

    def routing_respond(self, addr: Address, message: Any):
        with open("logs.txt", "a") as f:
            f.write(f"RECV: {addr} -> {message[0]}/{message[1]}:{message[2]}\n")
        route = tuple((message[0], message[1]))
        default_route = (message[0], "")
        if route in self.respond.routes:
            self.respond.routes[route](self, addr, message[2])
        elif default_route in self.respond.routes:
            self.respond.routes[default_route](self, addr, message[2])
        else:
            self.send_to_addr(addr, Format.error("ROUTING", [f"route {message[0]}/{message[1]} was not found"]))
            print(f"Route {addr[0]}:{message[0]}/{message[1]} was not found in Respond routes.")

    def send_to_addr(self, addr: Address, message: Any):
        with open("logs.txt", "a") as f:
            f.write(f"SEND: {addr} <- {message[0]}/{message[1]}:{message[2]}\n")
        self.conns[addr].send(Serializator.encode(message))
    
    def send_to_conn(self, conn: socket.socket, message: Any):
        with open("logs.txt", "a") as f:
            f.write(f"SEND: ?(send_to_conn used) <- {message[0]}/{message[1]}:{message[2]}\n")
        conn.send(Serializator.encode(message))

    def recv_from_addr(self, addr: Address) -> Any:
        return Serializator.decode_with_batching(self.conns[addr])
    
    def recv_from_conn(self, conn: socket.socket) -> Any:
        return Serializator.decode_with_batching(conn)

    def init_server(self, player_number: int = 1):
        self.player_number = player_number
        hostname = socket.gethostname()
        IPaddr = socket.gethostbyname_ex(hostname)[2]
        if len(IPaddr) == 1:
            IPaddr = IPaddr[0]
            print(IPaddr)
        else:
            for i in range(len(IPaddr)):
                print(f"{i}) {IPaddr[i]}")
            IPaddr = IPaddr[int(input("choose index of needed Ipv4: "))]
        if not validate_ip(IPaddr):
            print(f"IP address {IPaddr} is not valid.")
            IPaddr = input("Enter a valid IP address: ")
        
        try:
            self.sock = socket.socket()
            self.sock.settimeout(1)
            self.sock.bind((IPaddr, 9090))
            self.sock.listen(player_number)
        except socket.error as e:
            print(f"Socket error: {e}")
            return []

    def await_connection(self):
        while True:
            try:
                conn, addr = self.sock.accept()
            except socket.timeout:
                if self.alive:
                    continue
                else:
                    exit()
            check = self.respond.at_connect(self, conn, addr)
            if check:
                conn.settimeout(1)
                self.conns[addr] = conn
                t = threading.Thread(target=self.await_message, args=[addr])
                t.start()

    def await_message(self, addr: Address):
        while True:
            if not self.alive:
                return
            try:
                message = Serializator.decode_with_batching(self.conns[addr])
                self.routing_respond(addr, message)
            except socket.timeout:
                if self.alive:
                    continue
                else:
                    return
            except ConnectionResetError:
                self.conns[addr].close()
                self.conns.pop(addr)
                self.respond.at_disconnect(self, addr)
                return
            except UnicodeDecodeError:
                print(f"UnicodeDecodeError with {addr}")
                self.conns[addr].close()
                self.conns.pop(addr)
                self.respond.at_disconnect(self, addr)
                return
            except Exception as e:
                print(f"error occured with {addr}")
                # SHOULD BE DELETED WHEN DEBUGGING IS DONE
                self.conns[addr].close()
                self.conns.pop(addr)
                self.respond.at_disconnect(self, addr)
                raise e

    def start(self):
        t = threading.Thread(target=self.await_connection)
        t.start()
    
    def close_threads(self):
        self.alive = False
        time.sleep(1)
    
    def close_connections(self):
        for conn in self.conns.values():
            conn.close()