from typing import Any, Callable
from netio.util.generic_type import GenericType
from shared.generic_object import GenericObject
from engine_antiantilopa import GameObject

ACTION_RESULT = list[tuple[str, Callable]]
ACTION_FUNC_TYPE = Callable[[GenericObject|GenericType, Any], ACTION_RESULT]

class ActionSystem:
    
    _action_checker: list[ACTION_FUNC_TYPE] = []
    _action_spec: dict[str, list[ACTION_FUNC_TYPE]] = {}
    _action_default: dict[type, list[ACTION_FUNC_TYPE]] = {}

    @staticmethod
    def assign_action(obj: GenericObject|GenericType, args: Any = None) -> ACTION_RESULT:
        result: ACTION_RESULT = []
        for action in ActionSystem._action_checker:
            acts = action(obj, args)
            if acts is not None:
                result.extend(acts)
        if isinstance(obj, GenericType) and obj.name in ActionSystem._action_spec:
            for action_func in ActionSystem._action_spec[obj.name]:
                acts = action_func(obj, args)
                if acts is not None:
                    result.extend(acts)
        if type(obj) in ActionSystem._action_default:
            for action_func in ActionSystem._action_default[type(obj)]:
                acts = action_func(obj, args)
                if acts is not None:
                    result.extend(acts)

        for t in ActionSystem._action_default:
            if isinstance(obj, t):
                for action_func in ActionSystem._action_default[t]:
                    acts = action_func(obj, args)
                    if acts is not None:
                        result.extend(acts)
        return result
    
    @staticmethod
    def register_action_checker():
        def wrapper(action: ACTION_FUNC_TYPE):
            ActionSystem._action_checker.append(action)
        return wrapper
    
    @staticmethod
    def register_action_spec(name: str):
        if name not in ActionSystem._action_spec:
            ActionSystem._action_spec[name] = []
        def wrapper(action: ACTION_FUNC_TYPE):
            ActionSystem._action_spec[name].append(action)
        return wrapper
    
    @staticmethod
    def register_action_default(cls: type):
        if cls not in ActionSystem._action_default:
            ActionSystem._action_default[cls] = []
        def wrapper(action: ACTION_FUNC_TYPE):
            ActionSystem._action_default[cls].append(action)
        return wrapper
    

        
        