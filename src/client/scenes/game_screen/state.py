from typing import Callable


class State:
    value: int = 0

    _on_state_end: dict[int: Callable] = {}
    _on_state_start: dict[int: Callable] = {}

    @staticmethod
    def change_state(new_state: int):
        State._on_state_end.get(State.value, lambda:0)()
        State._on_state_start.get(new_state, lambda:0)()

        State.value = new_state

    @staticmethod
    def set_on_state_end(state: int, func: Callable[[], None]):
        State._on_state_end[state] = func

    @staticmethod
    def set_on_state_start(state: int, func: Callable[[], None]):
        State._on_state_start[state] = func



