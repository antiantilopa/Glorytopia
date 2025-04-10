import random, math


def noise(ind, mp: list[list[int]], min_value: int, max_value: int):
    for i in range(len(mp) // ind + 1):
        for j in range(len(mp[0]) // ind + 1):
            rand = random.randint(min_value, max_value)
            for a in range(ind):
                for b in range(ind):
                    if a + i * ind < len(mp) and b + j * ind < len(mp[0]):
                        mp[a + i * ind][b + j * ind] += rand
                        
def pangea_noise(ind, mp: list[list[int]], min_value: int, max_value: int):
    for i in range(len(mp) // ind + 1):
        for j in range(len(mp[0]) // ind + 1):
            divergence = (((len(mp) // 2 - ind * i) ** 2 + (len(mp) // 2 - ind * j) ** 2) / (len(mp) / 7) ** 2 or 1)
            rand = (random.random() * (max_value - min_value) + min_value) / divergence
            for a in range(ind):
                for b in range(ind):
                    if (a + i * ind < len(mp) - 1 and b + j * ind < len(mp[0]) - 1) and (a + i * ind > 0 and b + j * ind > 0):
                        mp[a + i * ind][b + j * ind] += rand

def antialiasing_map(mas: list) -> list:
    a = len(mas[0])
    b = len(mas)
    nmas = [[0] * a for _ in range(b)]
    for y in range(len(nmas)):
        for x in range(len(nmas)):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx != 0 or dy != 0:
                        nmas[y][x] += mas[(y + dy) % b][(x + dx) % a] / math.sqrt(dx ** 2 + dy ** 2)
            nmas[y][x] += mas[y][x] * 2
            nmas[y][x] /= 6 + 2 * math.sqrt(2)
    return nmas

def pangea(width: int, height: int) -> list:
    hydro_world = [[0] * width for i in range(height)]
    pangea_noise(1, hydro_world, 3, 6)
    for i in range(len(hydro_world)):
        for j in range(len(hydro_world[i])):
            cnt = 0
            for (idx, idxj) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if not((i + idx < len(hydro_world) and j + idxj < len(hydro_world[i])) and (i + idx >= 0 and j + idxj >= 0)):
                    continue
                    
                if round(hydro_world[i + idx][j + idxj]) != 0:
                    cnt += 1
            if cnt <= 0:
                hydro_world[i][j] = 0
    for i in range(height):
        for j in range(width):
            if hydro_world[i][j] < 0.3:
                hydro_world[i][j] = -1
            elif round(hydro_world[i][j]) == 0:
                hydro_world[i][j] = 0
            else:
                hydro_world[i][j] = 1

    plain_chance = 0.48
    forest_chance = 0.38
    mountain_chance = 0.14
    terrain_mask = [[(hydro_world[i][j] > 0) for j in range(width)] for i in range(height)]
    for i in range(height):
        for j in range(width):
            if terrain_mask[i][j] == 0: continue
            r = random.random()
            if r > plain_chance + forest_chance:
                terrain_mask[i][j] = 2
            elif r > plain_chance:
                terrain_mask[i][j] = 1
            else:
                terrain_mask[i][j] = 0

    world = [[(hydro_world[i][j] + terrain_mask[i][j]) + 1   for j in range(width)] for i in range(height)]

    return world

def print_map(world: list[list[int]]):
    alph = "_.-o^"
    for i in world:
        for j in i:
            print(alph[j], end = " ")
        print()

if __name__ == "__main__":
    print_map(pangea(31, 31))