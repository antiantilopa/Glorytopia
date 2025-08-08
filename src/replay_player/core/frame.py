from server.core.updating_object import UpdatingObject


class Change:
    cls_id: int
    cls_serialized: list

    def __init__(self, cls_id: int, cls_serialized: list):
        self.cls_id = cls_id
        self.cls_serialized = cls_serialized
    
    @staticmethod
    def from_serializable(data: tuple[int, list]):
        return Change(data[0], data[1])

class Frame:
    player_id: int
    func: int
    args: list
    changes: list[Change]

    def __init__(self, player_id: int, func: int, args: list, changes: list):
        self.player_id = player_id
        self.func = func
        self.args = args
        self.changes = [Change.from_serializable(change_data) for change_data in changes]

    def from_serializable(data: tuple[int, int, list, list]) -> "Frame":
        f = Frame(0, 0, [], [])
        f.player_id = data[0]# not used now
        f.func = data[1] # also not used now
        f.args = data[2] # guess what? not used now
        f.changes = [Change.from_serializable(change_data) for change_data in data[3]]
