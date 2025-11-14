from engine_antiantilopa import *
from client.widgets.sound import SoundComponent

class SoundManager:
    volume = 1
    
    sounds: dict[str, SoundComponent] = {}

    @staticmethod
    def new_music(nickname="", loop = True):
        if nickname in SoundManager.sounds:
            if loop:
                return SoundManager.sounds[nickname].play_in_loop()
            else:
                return SoundManager.sounds[nickname].play_once()
        new_s = SoundComponent(nickname=nickname, volume=SoundManager.volume)
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
                raise KeyError(f"cannot find {nickname} sond or music")
            snd = SoundManager.sounds[nickname]
            snd.stop_all_channels()

    @staticmethod
    def set_volume(volume: float = 1):
        SoundManager.volume = volume
        for snd in SoundManager.sounds.values():
            snd.set_volume(volume)