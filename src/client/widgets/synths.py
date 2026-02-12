from typing import Callable
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

    half_tone = np.pow(2, 1/12)
    minimal_tone = -48
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
        with open(f"{name}.txt", "w") as f:
            for note in notes:
                f.write(f"{note.duration}/{note.tone}/{int(note.pause)}\n")
    
    @staticmethod
    def load_notes(name: str):
        notes = []
        with open(f"{name}.txt", "r") as f:
            for string in f.read().split("\n")[:-1]:
                dur = float(string.split("/")[0])
                tone = int(string.split("/")[1])
                pause = int(string.split("/")[2])
                notes.append(Note(dur, tone, pause))
        return notes
    
    def save_notes_new(notes: list["Note"], name: str):
        with open(f"{name}", "wb") as f:
            for note in notes:
                if note.pause == 1:
                    write = 255
                else:
                    write = note.tone - Note.minimal_tone
                if note.duration > 255 and note.pause:
                    for i in range(int(note.duration) // 255):
                        f.write(bytes((255, write)))
                    f.write(bytes((int(note.duration) % 255, write)))
                else:
                    f.write(bytes((int(note.duration), write)))
    
    @staticmethod
    def load_notes_new(name: str) -> list["Note"]:
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
    def get_hit_attack_arr(duration = 1.5):
        if ("get_hit_attack_arr", duration) in Synths.cache:
            return Synths.cache[("get_hit_attack_arr", duration)]
        rate = Synths.rate
        up = np.linspace(0, 1, round(0.01 * rate))
        down = np.linspace(1, 0.4, round(0.01 * rate))
        steep_down = np.linspace(0.4, 0, round((duration * rate) - round(0.01 * rate) - round(0.01 * rate)))
        Synths.cache[("get_hit_attack_arr", duration)] = np.append(np.append(up, down), steep_down)
        return Synths.cache[("get_hit_attack_arr", duration)]

    @staticmethod
    def get_sin_arr(freq, duration = 1.5, t0 = 0):
        if ("get_sin_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_sin_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(t0, t0 + duration, round(rate * duration), endpoint=False)
        arr = np.sin(2 * np.pi * freq * t)
        arr *= Synths.get_attack_arr(duration)
        Synths.cache[("get_sin_arr", freq, duration)] = arr
        return arr

    @staticmethod
    def get_pin_arr(freq, duration = 1.5, t0 = 0):
        if ("get_pin_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_pin_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(0, duration, round(rate * duration), endpoint=False)
        arr = np.sin(2 * np.pi * freq * t) / 2
        for i in range(2, 10):
            arr += np.sin(2 * np.pi * freq * t * 2 ** i) / (2 ** i)
        arr *= Synths.get_control_arr(duration)
        Synths.cache[("get_pin_arr", freq, duration)] = arr
        return arr
    
    @staticmethod
    def get_org_arr(freq, duration = 1.5, t0 = 0):
        if ("get_org_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_org_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(t0, t0 + duration, round(rate * duration), endpoint=False)
        arr = t*0
        for i in range(-5, 6):
            arr += np.sin(2 * np.pi * freq * t * 2 ** i) / (2 ** abs(i+1)) / 3
        arr += np.sin(2 * np.pi * freq * t * Note.half_tone**5 * 2**5) / 32
        arr += np.sin(2 * np.pi * freq * t * Note.half_tone**5 / 2**5) / 32
        arr += np.sin(2 * np.pi * freq * t * pow(2, 5/12)) / 32
        arr += np.sin(2 * np.pi * freq * t / pow(2, 7/12)) / 32
        arr *= Synths.get_control_arr(duration)
        Synths.cache[("get_org_arr", freq, duration)] = arr
        return arr
    
    @staticmethod
    def get_ovr_arr(freq, duration = 1.5, t0 = 0):
        if ("get_ovr_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_ovr_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(t0, t0 + duration, round(rate * duration), endpoint=False)
        arr = np.sin(2 * np.pi * freq * t) * 8
        for i in (1, 2, 3, 5, 6, 7, 8):
            arr += np.sin(2 * np.pi * freq * t * i) / (i) ** 2
        arr /= 16
        arr *= Synths.get_control_arr(duration)
        Synths.cache[("get_ovr_arr", freq, duration)] = arr
        return arr
    
    @staticmethod
    def get_wig_arr(freq, duration = 1.5, t0 = 0):
        if ("get_wig_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_wig_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(t0, t0 + duration, round(rate * duration), endpoint=False)
        b = 3
        a = 2
        arr = (2 ** b - 2 * a) * np.sin(2 * np.pi * freq * t) / (2 ** b)
        arr += a * np.sin(2 * np.pi * freq * t * 2 ** b) / (2 ** b)
        arr += a * np.sin(2 * np.pi * freq * t * 2 ** -b) / (2 ** b)
        arr *= Synths.get_control_arr(duration)
        Synths.cache[("get_wig_arr", freq, duration)] = arr
        return arr

    @staticmethod
    def get_pqr_arr(freq, duration = 1.5, t0 = 0):
        if ("get_pqr_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_pqr_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(t0, t0 + duration, round(rate * duration), endpoint=False)
        arr = np.fmod(np.floor(t * freq), 2) / 2
        for i in range(2, 4):
            arr += np.fmod(np.floor(t * freq * 2 ** i), 2) / (2 ** i)
        arr *= Synths.get_control_arr(duration)
        Synths.cache[("get_pqr_arr", freq, duration)] = arr
        return arr
    
    @staticmethod
    def get_str_arr(freq, duration = 1.5, t0 = 0):
        if ("get_str_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_str_arr", freq, duration)]
        k = 1.0001
        r = 0.3
        arr1 = Synths.get_tri_arr(freq, duration, t0) * (1 - 2 * r)
        arr2 = Synths.get_sqr_arr(freq * k, duration, t0) * r
        arr3 = Synths.get_sqr_arr(freq / k, duration, t0) * r
        arr = arr1 + arr2 + arr3
        Synths.cache[("get_str_arr", freq, duration)] = arr
        return arr

    @staticmethod
    def get_tri_arr(freq, duration = 1.5, t0 = 0):
        if ("get_tri_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_tri_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(t0, t0 + duration, round(rate * duration), endpoint=False)
        arr = np.fmod(t * freq / 2, 1)
        arr *= Synths.get_control_arr(duration)
        # arr /= 3
        Synths.cache[("get_tri_arr", freq, duration)] = arr
        return arr
    
    @staticmethod
    def get_sqr_arr(freq, duration = 1.5, t0 = 0):
        if ("get_sqr_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_sqr_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(t0, t0 + duration, round(rate * duration), endpoint=False)
        arr = np.fmod(np.floor(t * freq), 2)
        arr *= Synths.get_control_arr(duration)
        # arr /= 3
        Synths.cache[("get_sqr_arr", freq, duration)] = arr
        return arr
    
    @staticmethod
    def get_saw_arr(freq, duration = 1.5, t0 = 0):
        if ("get_saw_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_saw_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(t0, t0 + duration, round(rate * duration), endpoint=False)
        arr = np.fmod(t * freq, 2)
        arr = arr - 1
        arr = np.abs(arr)
        arr = arr * 2 - 1
        arr *= Synths.get_control_arr(duration)
        Synths.cache[("get_saw_arr", freq, duration)] = arr
        return arr
    

    @staticmethod
    def get_qin_arr(freq, duration = 1.5, t0 = 0):
        if ("get_qin_arr", freq, duration) in Synths.cache:
            return Synths.cache[("get_qin_arr", freq, duration)]
        rate = Synths.rate
        t = np.linspace(1, 1 + duration, round(rate * duration), endpoint=False)
        a = 2 / t
        a += t
        arr = np.sin(2 * np.pi * freq * a)
        arr *= Synths.get_control_arr(duration)
        Synths.cache[("get_qin_arr", freq, duration)] = arr
        return arr

    @staticmethod
    def get_nos_arr(freq, duration = 1.5, t0 = 0):
        if ("get_nos_arr", duration) in Synths.cache:
            return Synths.cache[("get_nos_arr", duration)]
        rate = Synths.rate
        arr = np.random.rand(round(rate * duration))
        arr *= Synths.get_attack_arr(duration)
        Synths.cache[("get_nos_arr", duration)] = arr
        return arr
    
    @staticmethod
    def get_hit_arr(freq, duration = 1.5, t0 = 0):
        if ("get_hit_arr", duration) in Synths.cache:
            return Synths.cache[("get_hit_arr", duration)]
        rate = Synths.rate
        arr = np.random.rand(round(rate * duration))
        arr *= Synths.get_hit_attack_arr(duration)
        Synths.cache[("get_hit_arr", duration)] = arr
        return arr

    @staticmethod
    def get_non_arr(freq, duration = 1.5, t0 = 0):
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
            # Set WAV file parameters
            wf.setnchannels(2)  # Number of channels (e.g., 1 for mono, 2 for stereo)
            wf.setsampwidth(2)  # Sample width in bytes (e.g., 2 for 16-bit)
            wf.setframerate(Synths.rate)  # Frame rate (frequency)

            # Write the raw audio data
            wf.writeframes(sound.get_raw())

    @staticmethod
    def get_party(notes: list[Note], wave: str = "sin"):
        sum_duration = sum([note.duration for note in notes])
        t = np.linspace(0, sum_duration * Synths.seconds_per_note, round(sum_duration * Synths.rate * Synths.seconds_per_note), endpoint=False)
        res = np.empty(sum([round(Synths.rate * note.duration * Synths.seconds_per_note) for note in notes]))
        i = 0
        for note in notes:
            if note.pause:
                arr = Synths.get_non_arr(freq=0, duration=note.duration * Synths.seconds_per_note)
            else:
                arr = wave_names[wave](note.freq, note.duration * Synths.seconds_per_note, (i) / Synths.rate)
                # arr = np.flip(arr)
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

wave_names: dict[str, Callable[[int, int, int], np.ndarray]] = {
        "sin": Synths.get_sin_arr,
        "pin": Synths.get_pin_arr,
        "pqr": Synths.get_pqr_arr,
        "tri": Synths.get_tri_arr,
        "saw": Synths.get_saw_arr, 
        "sqr": Synths.get_sqr_arr,
        "str": Synths.get_str_arr,
        "org": Synths.get_org_arr,
        "ovr": Synths.get_ovr_arr,
        "wig": Synths.get_wig_arr,
        "qin": Synths.get_qin_arr,
        "nos": Synths.get_nos_arr,
        "hit": Synths.get_hit_arr,
        "non": Synths.get_non_arr
    }
