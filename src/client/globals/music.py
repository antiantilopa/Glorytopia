from typing import Callable
from engine_antiantilopa import *
from client.widgets.sound import SoundComponent

class SoundManager:
    music_volume = 0.0
    sound_volume = 0.1

    sounds: dict[str, SoundComponent] = {}

    @staticmethod
    def new_music(nickname="", loop = True, on_end: Callable = lambda: None, is_music: bool = False):
        if nickname in SoundManager.sounds:
            if loop:
                return SoundManager.sounds[nickname].play_in_loop()
            else:
                return SoundManager.sounds[nickname].play_once()
        if is_music:
            volume = SoundManager.music_volume
        else:
            volume = SoundManager.sound_volume
        new_s = SoundComponent(nickname=nickname, volume=volume, on_end=on_end, is_music=is_music)
        SoundManager.sounds[nickname] = new_s
        if loop:
            return new_s.play_in_loop()
        else:
            return new_s.play_once()
        
    @staticmethod
    def stop_music(nickname=""):
        if nickname == "":
            for snd_name in SoundManager.sounds:
                SoundManager.sounds[snd_name].stop_all_channels()
        else:
            if nickname not in SoundManager.sounds:
                raise KeyError(f"cannot find {nickname} sound or music")
            snd = SoundManager.sounds[nickname]
            snd.stop_all_channels()

    @staticmethod
    def set_music_volume(volume: float = 1):
        SoundManager.music_volume = volume
        for snd in SoundManager.sounds.values():
            if snd.is_music:
                snd.set_volume(volume)

    @staticmethod
    def set_sound_volume(volume: float = 1):
        SoundManager.sound_volume = volume
        for snd in SoundManager.sounds.values():
            if not snd.is_music:
                snd.set_volume(volume)