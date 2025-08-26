import socket
import enum

from ..serialization.serializer import BaseReader, BaseWriter


class MessageType(enum.Enum):
    EVENT = 0
    RESPONSE = 1
    REQUEST = 2
    CONNECT = 3
    CREATE = 4
    SYNCHRONIZE = 5
    ERROR = 6
    DELETE = 7
    RELOAD = 8

class Reader(BaseReader):

    def get_message(self, conn: socket.socket) -> tuple[MessageType, str, tuple]:
        q, route, obj  = self.decode(conn)
        return MessageType(q), route, obj

class Writer(BaseWriter):

    def send_message(self, conn: socket.socket, message_type: MessageType, route: str, obj: tuple):
        self.encode(conn, (message_type.value, route, obj))