import os
import sys

# Thêm đường dẫn hiện tại để import main.py nếu cần (hoặc chỉ cần copy logic)
def ring_walls():
    blocked = set()
    for x in range(44):
        blocked.add((x, 0))
        blocked.add((x, 43))
    for y in range(44):
        blocked.add((0, y))
        blocked.add((43, y))
    return blocked

def add_rect_walls(blocked, x1, y1, x2, y2, doors=None):
    for x in range(x1, x2 + 1):
        blocked.add((x, y1))
        blocked.add((x, y2))
    for y in range(y1, y2 + 1):
        blocked.add((x1, y))
        blocked.add((x2, y))
    if doors:
        for d in doors:
            blocked.discard(d)

def corridor(blocked, x1, y1, x2, y2, width=3):
    if x1 == x2:
        x = x1
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for dx in range(-(width // 2), width // 2 + 1):
                blocked.discard((x + dx, y))
    elif y1 == y2:
        y = y1
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for dy in range(-(width // 2), width // 2 + 1):
                blocked.discard((x, y + dy))

def carve(blocked, x1, y1, x2, y2):
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            blocked.discard((x, y))

if __name__ == "__main__":
    basement_blocked = ring_walls()
    add_rect_walls(basement_blocked, 3, 3, 40, 40, doors=[(4, 35), (40, 35)])
    carve(basement_blocked, 2, 33, 8, 39)
    carve(basement_blocked, 8, 33, 14, 35)
    for x in range(6, 38):
        basement_blocked.add((x, 20))
        basement_blocked.add((x, 24))
    for pos in [(16, 20), (17, 20), (28, 24), (29, 24), (10, 24), (11, 24), (34, 20), (35, 20)]:
        basement_blocked.discard(pos)
    add_rect_walls(basement_blocked, 26, 4, 40, 18, doors=[(38, 18), (26, 10)])
    add_rect_walls(basement_blocked, 4, 26, 18, 40, doors=[(18, 33), (10, 26), (4, 35)])
    add_rect_walls(basement_blocked, 4, 4, 18, 18, doors=[(10, 18), (18, 10)])
    corridor(basement_blocked, 10, 18, 10, 26, width=7)
    corridor(basement_blocked, 18, 33, 26, 33, width=7)
    carve(basement_blocked, 3, 34, 12, 36)
    carve(basement_blocked, 3, 33, 6, 39)
    carve(basement_blocked, 6, 19, 37, 25)
    for pos in [(8, 30), (9, 30), (8, 31), (30, 10), (31, 10), (32, 10), (14, 10), (14, 11), (15, 11), (34, 16)]:
        basement_blocked.add(pos)
    with open("basement_map.txt", "w") as f:
        for y in range(44):
            line = ""
            for x in range(44):
                if (x, y) in basement_blocked:
                    line += "##"
                else:
                    line += ".."
            f.write(line + "\n")
