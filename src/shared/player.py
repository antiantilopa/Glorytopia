from typing import Annotated
from netio import SerializeField, PlayerData
from shared.asset_types import Nation, TechNode
from netio import ConnectionData

class PlayerData_(PlayerData):
    id: Annotated[int, SerializeField()]
    nation: Annotated[Nation, SerializeField(by_id=True)]
    nickname: Annotated[str, SerializeField()]
    is_ready: Annotated[bool, SerializeField()]
    color: Annotated[int, SerializeField()]

    recovery_code: int

    @classmethod
    def create(cls, addr, conn_data: ConnectionData):
        obj = super().create(addr, conn_data)
        obj.id = -1

        obj.color = 0
        obj.recovery_code = None
        obj.is_ready = False
        obj.nickname = ""
        obj.nation = Nation.by_id(0)
        return obj