import random

def noise(ind, map, mn, mx):
    for i in range(len(map) // ind + 1):
        for j in range(len(map[0]) // ind + 1):
            rand = random.randint(mn, mx)
            for a in range(ind):
                for b in range(ind):
                    if a + i * ind < len(map) and b + j * ind < len(map[0]):
                        map[a + i * ind][b + j * ind] += rand

def neighbornx(mas: list, a, b, lenght) -> list:
    nmas=[[0] * a for i in range(b)]
    for y in range(len(nmas)):
        for x in range(len(nmas)):
            if mas[y][x] >= lenght // 2:
                mas[y][x] += 10
            else:
                mas[y][x] -= 10
            y1 = y - 1; x1 = x - 1
            y0 = y + 1; x0 = x + 1
            if y >= len(nmas) - 1: y0 = 0
            if x >= len(nmas) - 1: x0 = 0
            nmas[y][x] += mas[y1][x]
            nmas[y][x] += mas[y][x1]
            nmas[y][x] += mas[y0][x]
            nmas[y][x] += mas[y][x0]
            nmas[y][x] += mas[y][x]
            nmas[y][x] //= 5
    return nmas
