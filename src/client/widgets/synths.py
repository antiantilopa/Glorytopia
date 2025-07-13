import pygame
import numpy as np
import time
import wave

pygame.init()
pygame.mixer.init(channels=2)

class Note:
    duration: float
    tone: int
    pause: bool

    minimal_tone = -48
    half_tone = np.pow(2, 1/12)
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    colors = (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)
    def __init__(self, duration: float, tone: int, pause: bool = False):
        self.duration = duration
        self.tone = tone
        self.pause = pause
        self.freq = 440 * (Note.half_tone ** tone)
    
    def __repr__(self):
        return f"{Note.names[(self.tone + 9) % 12]}\t{4 + (self.tone + 9) // 12}\t{self.duration}"

    def get_color(self):
        return Note.colors[(self.tone + 9) % 12]
    
    @staticmethod
    def save_notes(notes: list["Note"], name: str):
        with open(f"{name}", "wb") as f:
            for note in notes:
                if note.pause == 1:
                    write = 255
                else:
                    write = note.tone - Note.minimal_tone
                f.write(bytes(note.duration, write))
    
    @staticmethod
    def load_notes(name: str):
        notes = []
        with open(f"{name}", "rb") as f:
            raw = f.read()
            assert len(raw) % 2 == 0
            for i in range(len(raw) // 2):
                dur = int(raw[2 * i])
                tone = int(raw[2 * i + 1] + Note.minimal_tone)
                pause = (raw[2 * i + 1] == 255)
                notes.append(Note(dur, tone, pause))
        return notes


class Synths:
    rate: int = 44100
    seconds_per_note: float = 0.4
    cache = {}

    def __init__(self, rate: int = 44100):
        Synths.rate = rate
    
    @staticmethod
    def get_control_arr(duration = 1.5):
        if ("get_control_arr", duration) in Synths.cache:
            return Synths.cache[("get_control_arr", duration)]
        rate = Synths.rate
        up = np.linspace(0, 1, round(0.01 * rate))
        straight = np.full(round((duration * rate) - 2 * round(0.01 * rate)), 1)
        down = np.linspace(1, 0, round((0.01) * rate))
        Synths.cache[("get_control_arr", duration)] = np.append(np.append(up, straight), down)
        return Synths.cache[("get_control_arr", duration)]

    @staticmethod
    def get_attack_arr(duration = 1.5):
        if ("get_attack_arr", duration) in Synths.cache:
            return Synths.cache[("get_attack_arr", duration)]
        rate = Synths.rate
        up = np.linspace(0, 1, round(0.01 * rate))
        down = np.linspace(1, 0, round((duration * rate) - round(0.01 * rate)))
        Synths.cache[("get_attack_arr", duration)] = np.append(up, down)
        return Synths.cache[("get_attack_arr", duration)]

    @staticmethod
    def get_sin_arr(freq, duration = 1.5):
        if ("get_sin_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_sin_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(0, duration, round(rate * duration), endpoint=False)
        arr = np.sin(2 * np.pi * freq * t)
        arr *= Synths.get_control_arr(duration)
        Synths.cache[("get_sin_arr", freq, duration)] = arr
        return arr

    @staticmethod
    def get_tri_arr(freq, duration = 1.5):
        if ("get_tri_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_tri_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(0, duration, round(rate * duration), endpoint=False)
        arr = np.fmod(t * freq / 2, 1)
        arr *= Synths.get_control_arr(duration)
        # arr /= 3
        Synths.cache[("get_tri_arr", freq, duration)] = arr
        return arr
    
    @staticmethod
    def get_sqr_arr(freq, duration = 1.5):
        if ("get_sqr_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_sqr_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(0, duration, round(rate * duration), endpoint=False)
        arr = np.fmod(np.floor(t * freq), 2)
        arr *= Synths.get_control_arr(duration)
        # arr /= 3
        Synths.cache[("get_sqr_arr", freq, duration)] = arr
        return arr

    @staticmethod
    def get_nos_arr(duration = 1.5):
        if ("get_nos_arr", duration) in Synths.cache:
            return Synths.cache[("get_nos_arr", duration)]
        rate = Synths.rate
        arr = np.random.rand(round(rate * duration))
        arr *= Synths.get_attack_arr(duration)
        Synths.cache[("get_nos_arr", duration)] = arr
        return arr

    @staticmethod
    def get_non_arr(duration = 1.5):
        rate = Synths.rate
        arr = np.zeros(round(duration * rate))
        return arr

    @staticmethod
    def play_arr(arr, delay: bool = True, loops = 0) -> pygame.mixer.Channel:
        sound = np.asarray([32767 * arr, 32767 * arr]).T.astype(np.int16)
        sound = pygame.sndarray.make_sound(sound.copy())
        sound_channel = sound.play(loops=loops)
        if delay:
            pygame.time.delay(len(arr) * 1000 // Synths.rate)
        return sound_channel
    
    @staticmethod
    def save_to_wav(arr, output_filename = "output_sound.wav"):
        sound = np.asarray([32767 * arr, 32767 * arr]).T.astype(np.int16)
        sound = pygame.sndarray.make_sound(sound.copy())
        
        with wave.open(output_filename, 'wb') as wf:
            print("at least was here")
            # Set WAV file parameters
            wf.setnchannels(2)  # Number of channels (e.g., 1 for mono, 2 for stereo)
            wf.setsampwidth(2)  # Sample width in bytes (e.g., 2 for 16-bit)
            wf.setframerate(Synths.rate)  # Frame rate (frequency)

            # Write the raw audio data
            wf.writeframes(sound.get_raw())

    @staticmethod
    def get_sin_party(notes: list[Note]):
        res = np.empty(sum([round(Synths.rate * note.duration * Synths.seconds_per_note) for note in notes]))
        i = 0
        for note in notes:
            if note.pause:
                arr = Synths.get_non_arr(note.duration * Synths.seconds_per_note)
            else:
                arr = Synths.get_sin_arr(note.freq, note.duration * Synths.seconds_per_note)
            res[i : i + round(Synths.rate * note.duration * Synths.seconds_per_note)] = arr
            i += round(Synths.rate * note.duration * Synths.seconds_per_note)
        return res

    @staticmethod
    def get_tri_party(notes: list[Note]):
        res = np.empty(sum([round(Synths.rate * note.duration * Synths.seconds_per_note) for note in notes]))
        i = 0
        for note in notes:
            if note.pause:
                arr = Synths.get_non_arr(note.duration * Synths.seconds_per_note)
            else:
                arr = Synths.get_tri_arr(note.freq, note.duration * Synths.seconds_per_note)
            res[i : i + round(Synths.rate * note.duration * Synths.seconds_per_note)] = arr
            i += round(Synths.rate * note.duration * Synths.seconds_per_note)
        return res
    
    @staticmethod
    def get_sqr_party(notes: list[Note]):
        res = np.empty(sum([round(Synths.rate * note.duration * Synths.seconds_per_note) for note in notes]))
        i = 0
        for note in notes:
            if note.pause:
                arr = Synths.get_non_arr(note.duration * Synths.seconds_per_note)
            else:
                arr = Synths.get_sqr_arr(note.freq, note.duration * Synths.seconds_per_note)
            res[i : i + round(Synths.rate * note.duration * Synths.seconds_per_note)] = arr
            i += round(Synths.rate * note.duration * Synths.seconds_per_note)
        return res
    
    @staticmethod
    def get_nos_party(notes: list[Note]):
        res = np.empty(sum([round(Synths.rate * note.duration * Synths.seconds_per_note) for note in notes]))
        i = 0
        for note in notes:
            if note.pause:
                arr = Synths.get_non_arr(note.duration * Synths.seconds_per_note)
            else:
                arr = Synths.get_nos_arr(note.duration * Synths.seconds_per_note) * note.tone
            res[i : i + round(Synths.rate * note.duration * Synths.seconds_per_note)] = arr
            i += round(Synths.rate * note.duration * Synths.seconds_per_note)
        return res

    @staticmethod
    def merge_parties(*parties: list):
        max_len = 0
        for party in parties:
            if len(party) > max_len:
                max_len = len(party)
        
        res = np.zeros(max_len)
        for party in parties:
            res += np.append(party, np.zeros(max_len - len(party)))
        
        res /= len(parties)

        return res
