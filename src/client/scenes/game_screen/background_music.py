from client.globals.music import SoundManager
import random


class BackgroundMusic:
    current_music_ind: int = 0
    track_list: list[str] = ["track1", "track2", "track3", "track4"]

    @staticmethod
    def start():
        _next_track()

def _next_track():
    BackgroundMusic.current_music_ind = (BackgroundMusic.current_music_ind + 1)
    if not (0 <= BackgroundMusic.current_music_ind < len(BackgroundMusic.track_list)):
        BackgroundMusic.current_music_ind = 0
        random.shuffle(BackgroundMusic.track_list)
        print(f"shuffled track list: {BackgroundMusic.track_list}")
    SoundManager.new_music(BackgroundMusic.track_list[BackgroundMusic.current_music_ind], loop=False, on_end=_next_track)