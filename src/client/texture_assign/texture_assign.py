




from typing import Callable
from netio.util.generic_type import GenericType
from shared.generic_object import GenericObject
from engine_antiantilopa import GameObject

class TextureAssignSystem:

    _assign_checker: dict[Callable[[GenericObject|GenericType], bool], Callable[[GenericObject|GenericType, GameObject, set[str]], None]] = {}
    _assign_spec: dict[str, Callable[[GenericObject|GenericType, GameObject, set[str]], None]] = {}
    _assign_default: dict[type, Callable[[GenericObject|GenericType, GameObject, set[str]], None]] = {}

    _update_checker: dict[Callable[[GenericObject|GenericType], bool], Callable[[GenericObject|GenericType, GameObject, set[str]], None]] = {}
    _update_spec: dict[str, Callable[[GenericObject|GenericType, GameObject, set[str]], None]] = {}
    _update_default: dict[type, Callable[[GenericObject|GenericType, GameObject, set[str]], None]] = {}

    @staticmethod
    def assign_texture(obj: GenericObject|GenericType, game_object: GameObject, flags: set[str] = set()):
        for checker, assigner in TextureAssignSystem._assign_checker.items():
            if checker(obj):
                return assigner(obj, game_object, flags)
        if isinstance(obj, GenericType) and obj.name in TextureAssignSystem._assign_spec:
            return TextureAssignSystem._assign_spec[obj.name](obj, game_object, flags)
        if type(obj) in TextureAssignSystem._assign_default:
            return TextureAssignSystem._assign_default[type(obj)](obj, game_object, flags)

        for t in TextureAssignSystem._assign_default:
            if isinstance(obj, t):
                return TextureAssignSystem._assign_default[t](obj, game_object, flags)
        
        raise Exception(f"Cannot assign texture for object {obj} of type {type(obj)}")
    
    @staticmethod
    def update_texture(obj: GenericObject|GenericType, game_object: GameObject, flags: set[str] = set()):
        for checker, assigner in TextureAssignSystem._update_checker.items():
            if checker(obj):
                return assigner(obj, game_object, flags)
        if isinstance(obj, GenericType) and obj.name in TextureAssignSystem._update_spec:
            return TextureAssignSystem._update_spec[obj.name](obj, game_object, flags)
        if type(obj) in TextureAssignSystem._update_default:
            return TextureAssignSystem._update_default[type(obj)](obj, game_object, flags)

        for t in TextureAssignSystem._update_default:
            if isinstance(obj, t):
                return TextureAssignSystem._update_default[t](obj, game_object, flags)
        
        raise Exception(f"Cannot update texture for object {obj} of type {type(obj)}")

    @staticmethod
    def register_assign_checker(checker: Callable[[GenericObject|GenericType], bool]):
        def wrapper(assigner: Callable[[GenericObject|GenericType, GameObject, set[str]], None]):
            TextureAssignSystem._assign_checker[checker] = assigner
        return wrapper
    
    @staticmethod
    def register_update_checker(checker: Callable[[GenericObject|GenericType], bool]):
        def wrapper(assigner: Callable[[GenericObject|GenericType, GameObject, set[str]], None]):
            TextureAssignSystem._update_checker[checker] = assigner
        return wrapper
    
    @staticmethod
    def register_assign_spec(name: str):
        def wrapper(assigner: Callable[[GenericObject|GenericType, GameObject, set[str]], None]):
            TextureAssignSystem._assign_spec[name] = assigner
        return wrapper
    
    @staticmethod
    def register_update_spec(name: str):
        def wrapper(assigner: Callable[[GenericObject|GenericType, GameObject, set[str]], None]):
            TextureAssignSystem._update_spec[name] = assigner
        return wrapper

    @staticmethod
    def register_assign_default(cls: type):
        def wrapper(assigner: Callable[[GenericObject|GenericType, GameObject, set[str]], None]):
            TextureAssignSystem._assign_default[cls] = assigner
        return wrapper

    @staticmethod
    def register_update_default(cls: type):
        def wrapper(assigner: Callable[[GenericObject|GenericType, GameObject, set[str]], None]):
            TextureAssignSystem._update_default[cls] = assigner
        return wrapper