import random, math


def noise(ind, map, mn, mx):
    for i in range(len(map) // ind + 1):
        for j in range(len(map[0]) // ind + 1):
            rand = random.randint(mn, mx)
            for a in range(ind):
                for b in range(ind):
                    if a + i * ind < len(map) and b + j * ind < len(map[0]):
                        map[a + i * ind][b + j * ind] += rand
                        
def pangea_noise(ind, map, mn, mx):
    for i in range(len(map) // ind + 1):
        for j in range(len(map[0]) // ind + 1):
            divergence = (((len(map) // 2 - ind * i) ** 2 + (len(map) // 2 - ind * j) ** 2) / (len(map) / 7) ** 2 or 1)
            rand = (random.random() * (mx - mn) + mn) / divergence
            for a in range(ind):
                for b in range(ind):
                    if (a + i * ind < len(map) - 1 and b + j * ind < len(map[0]) - 1) and (a + i * ind > 0 and b + j * ind > 0):
                        map[a + i * ind][b + j * ind] += rand

def antialiasing_map(mas: list) -> list:
    a = len(mas[0])
    b = len(mas)
    nmas=[[0] * a for _ in range(b)]
    for y in range(len(nmas)):
        for x in range(len(nmas)):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx != 0 or dy != 0:
                        nmas[y][x] += mas[(y + dy) % b][(x + dx) % a] / math.sqrt(dx ** 2 + dy ** 2)
            nmas[y][x] += mas[y][x] * 2
            nmas[y][x] /= 6 + 2 * math.sqrt(2)
    return nmas

def pangea(width: int, heigh: int) -> list:
    hydro_world = [[0] * width for i in range(heigh)]
    pangea_noise(1, hydro_world, 3, 6)

    for i in range(len(hydro_world)):
        for j in range(len(hydro_world[i])):
            cnt = 0
            for (idx, idxj) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if not((i + idx < len(hydro_world) and j + idxj < len(hydro_world[i])) and (i + idx >= 0 and j + idxj >= 0)):
                    continue
                    
                if (round(hydro_world[i + idx][j + idxj]) != 0):
                    cnt += 1
            if (cnt <= 0):
                hydro_world[i][j] = 0
    for i in range(heigh):
        for j in range(width):
            if hydro_world[i][j] < 0.3:
                hydro_world[i][j] = -1
            elif round(hydro_world[i][j]) == 0:
                hydro_world[i][j] = 0
            else:
                hydro_world[i][j] = 1

    terrain_mask = [[(hydro_world[i][j] > 0) * random.randint(0, 2) for j in range(width)] for i in range(heigh)]

    resource_mask = [[int((random.random() > ((width / 2 - j) ** 2 + (heigh / 2 - i) ** 2) / (width / 2) ** 2) and random.random() > 0.6) for j in range(width)] for i in range(heigh)]

    world = [[resource_mask[i][j] + 2 * (hydro_world[i][j] + terrain_mask[i][j]) + 2   for j in range(width)] for i in range(heigh)]

    return world

def print_map(world):
    alph = "_~.:-+o8^M"
    for i in world:
        for j in i:
           
            print(alph[j], end = " ")
        print()

if __name__ == "main":
    print_map(pangea(11, 11))