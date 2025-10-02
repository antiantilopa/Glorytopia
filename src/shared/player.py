from typing import Annotated
from engine_antiantilopa import Vector2d
from netio import SerializeField, PlayerData as PD
from shared.asset_types import Nation, TechNode
from netio import ConnectionData

class PlayerData_(PD):
    id: Annotated[int, SerializeField()]
    nation: Annotated[Nation, SerializeField(by_id=True)]
    is_dead: Annotated[bool, SerializeField()]
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
        obj.nickname = None
        obj.nation = None
        obj.is_dead = True
        return obj