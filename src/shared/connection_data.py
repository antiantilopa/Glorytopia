from netio import ConnectionData as CD, SerializeField
from typing import Annotated

class ConnectionData(CD):
    nickname: Annotated[str, SerializeField()]