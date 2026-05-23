from client.globals.music import SoundManager
import random


class BackgroundMusic:
    current_music_ind: int = 0
    track_list: list[str] = ["track1.1", "track2.1", "track3.1", "track4.1", "track1.2", "track2.2", "track3.2", "track4.2"]

    @staticmethod
    def start():
        _next_track()

def _next_track():
    BackgroundMusic.current_music_ind = (BackgroundMusic.current_music_ind + 1)
    if not (0 <= BackgroundMusic.current_music_ind < len(BackgroundMusic.track_list)):
        BackgroundMusic.current_music_ind = 0
        random.shuffle(BackgroundMusic.track_list)
        print(f"shuffled track list: {BackgroundMusic.track_list}")
    SoundManager.new_music(BackgroundMusic.track_list[BackgroundMusic.current_music_ind], loop=False, on_end=_next_track, is_music=True)