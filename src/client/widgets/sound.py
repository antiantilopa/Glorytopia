from engine_antiantilopa import *
import pygame as pg
import numpy as np
import os, json
from .synths import Synths, Note

class SoundComponent(Component):
    sound: pg.mixer.Sound
    channels: list[pg.mixer.Channel]
    volume: float
    tone_offset: float

    downloaded: dict[str, pg.mixer.Sound] = {}
    stop_event_type = pg.event.custom_type()
    names_to_funcs = {
        "sin": Synths.get_sin_party,
        "pin": Synths.get_pin_party,
        "tri": Synths.get_tri_party,
        "sqr": Synths.get_sqr_party,
        "pqr": Synths.get_pqr_party,
        "nos": Synths.get_nos_party,
        "hit": Synths.get_hit_party,
    }


    def __init__(self, path: str = "", nickname: str = "", volume: float = 1, tone_offset: int = 0):
        prenickname = ":"
        self.channels = []
        if path != "" and path in SoundComponent.downloaded:
            self.sound = SoundComponent.downloaded[path]
        elif nickname != "" and (prenickname + nickname) in SoundComponent.downloaded:
            self.sound = SoundComponent.downloaded[(prenickname + nickname)]
        else:
            if nickname != "":
                SoundComponent.downloaded[(prenickname + nickname)] = SoundComponent.load(path)
                self.sound = SoundComponent.downloaded[(prenickname + nickname)]
            else:
                SoundComponent.downloaded[path] = SoundComponent.load(path)
                self.sound = SoundComponent.downloaded[path]
        self.volume = volume
        self.set_volume(volume)
        self.tone_offset = tone_offset
    
    def set_volume(self, volume: int = 1):
        self.volume = volume
        for channel in self.channels:
            channel.set_volume(volume)

    @staticmethod
    def load(path):
        assert os.path.exists(path + "/config.json")
        config = json.load(open(path + "/config.json"))
        parties = []
        Synths.seconds_per_note = config["spn"]
        for party_conf in config["parties"]:
            notes = Note.load_notes(path + "/" + party_conf["name"])
            party = SoundComponent.names_to_funcs[party_conf["wave"]](notes)
            party *= party_conf["volume"]
            parties.append(party)
        arr = Synths.merge_parties(*parties)
        sound = np.asarray([32767 * arr, 32767 * arr]).T.astype(np.int16)
        sound = pg.sndarray.make_sound(sound.copy())
        return sound

    @staticmethod
    def get_by_nickname(nickname: str) -> pg.Surface:
        prenickname = ":"
        if (prenickname + nickname) in SoundComponent.downloaded:
            return SoundComponent.downloaded[(prenickname + nickname)]
        else:
            raise KeyError(f"Sound with nickname '{nickname}' not found.")
    
    @staticmethod
    def is_downloaded(nickname: str = None, path: str = None) -> bool:
        if nickname is None and path is None:
            raise ValueError("Either 'nickname' or 'path' must be provided.")
        if path is not None and nickname is not None:
            raise ValueError("Only one of 'nickname' or 'path' should be provided.")
        if path is not None:
            return path in SoundComponent.downloaded
        if nickname is not None:
            prenickname = ":"
            return (prenickname + nickname) in SoundComponent.downloaded
        
    def play_once(self) -> pg.mixer.Channel:
        channel = self.sound.play()
        channel.set_volume(self.volume)
        self.channels.append(channel)
        channel.set_endevent(SoundComponent.stop_event_type)
        return channel

    def play_in_loop(self) -> pg.mixer.Channel:
        channel = self.sound.play(loops=-1)
        channel.set_volume(self.volume)
        self.channels.append(channel)
        channel.set_endevent(SoundComponent.stop_event_type)
        return channel
    
    def stop_channel(self, channel: pg.mixer.Channel):
        if channel in self.channels:
            channel.stop()
            self.channels.remove(channel)
    
    def stop_all_channels(self):
        for channel in self.channels:
            channel.stop()
        self.channels = []
    
    def iteration(self):
        if self.game_object.active == 0:
            if len(self.channels) > 0:
                self.stop_all_channels()

        for event in pg.event.get(SoundComponent.stop_event_type, pump=False):
            i = 0
            while i < len(self.channels):
                if self.channels[i].get_busy() == 0:
                    self.channels.pop(i)
                else:
                    i += 1
            break
