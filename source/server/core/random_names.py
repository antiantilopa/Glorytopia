import random

consonants = ["q", "w", "r", "t", "p", "s", "d", "f", "g", 
                "h", "j", "k", "l", "z", "x", "c", "v", "b", "n", "m", "y"]
vowels = ["e", "u", "i", "o", "a"]

consonants_1 = ["q", "r", "t", "p", "d", "g", "k", "l", "z", "x", "c", "v", "b", "n", "m"]
consonants_2 = ["w", "s", "f", "h", "j", "y"]


def random_funny_name():
    name = ""

    syllables = ["te", "tu", "ti", "to", "ta", "ra", 
                 "ru", "re", "ri", "ro", "pe", "po", 
                 "pu", "pi", "pa", "de", "du", "di",
                 "do", "da", "ke", "ku", "ki", "ko",
                 "ka", "qe", "qu", "qi", "qo", "qa",
                 "ge", "gu", "gi", "go", "ga", "ze",
                 "zu", "zi", "zo", "za", "le", "lu",
                 "li", "lo", "la", "ce", "cu", "ci",
                 "ca", "ve", "vu", "vi", "vo", "va",
                 "me", "mu", "mi", "mo", "ma", "he",
                 "sha", "she", "sho", "cha", "che", "cho",
                 "shu", "shi", "chu", "chi",
                 "ne", "nu", "ni", "no", "na"]
    
    for i in range(random.randint(2, 3)):
        syllable = random.choice(syllables)
        name += syllable
        
        match(syllable):
            case "po":
                name += "pa"
            case "mu":
                name += "mu"
            case "mi":
                name += "memamomu"
            case "zi":
                name += "ga"
            case "ka":
                name += "shka"
            case "he":
                name += "hehe"
            case "ni":
                name += "ger"
            case "ci":
                name += "ty"

    return name

def random_sonorous_name():
    name = ""

    tchs = [1, 1, 1]
    for i in range(random.randint(4, 8)):
        chances = random.random() * tchs[0], random.random() * tchs[1], random.random() * tchs[2]
        idx = 0
        for i in range(3):
            if (chances[i] > chances[idx]):
                idx = i

        name += random.choice((consonants_2, vowels, consonants_1)[idx])
        
        match (idx):
            case 0:
                tchs[0] *= 0
                tchs[2] *= 0.7
            case 1:
                tchs[1] *= 0.5
            case 2:
                tchs[0] *= 0.7
                tchs[2] *= 0

        for i in range(3): 
            if (i != idx): 
                tchs[i] = 1

    return name

def random_normal_name():
    name = ""

    a = 0
    for i in range(random.randint(4, 8)):
        is_vowel = round(i % 2)
        name += random.choice((consonants, vowels)[is_vowel])

    return name

def random_name_with_double():
    name = ""

    a = 0
    for i in range(random.randint(3, 5)):
        is_vowel = round(i % 2)
        name += random.choice((consonants, vowels)[is_vowel])

        dbl = round(random.random() * 0.6)
        if dbl:
            name += random.choice((consonants, vowels)[is_vowel])

    return name

for i in range(7):
    print(random_funny_name())