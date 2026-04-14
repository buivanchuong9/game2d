from __future__ import annotations

import os
from pathlib import Path

import pygame


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "Sprites" / "Sprites_Environment" / "props"
ITEM_DIR = ROOT / "Sprites" / "Sprites_Environment" / "items"


def _save(surface: pygame.Surface, name: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    pygame.image.save(surface, str(path))
    return path


def _save_item(surface: pygame.Surface, name: str):
    ITEM_DIR.mkdir(parents=True, exist_ok=True)
    path = ITEM_DIR / name
    pygame.image.save(surface, str(path))
    return path


def _new(w: int, h: int) -> pygame.Surface:
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _px_rect(surf: pygame.Surface, color, x, y, w, h):
    pygame.draw.rect(surf, color, pygame.Rect(int(x), int(y), int(w), int(h)))


def _outline(surf: pygame.Surface, rect: pygame.Rect, color=(15, 18, 24)):
    pygame.draw.rect(surf, color, rect, 1)


def roof_vent_32():
    s = _new(32, 32)
    body = pygame.Rect(4, 8, 24, 18)
    _px_rect(s, (80, 86, 96), *body)
    _outline(s, body)
    # grille
    for y in range(10, 24, 3):
        pygame.draw.line(s, (55, 60, 70), (6, y), (26, y))
    # highlight + rust
    pygame.draw.line(s, (130, 138, 150), (6, 10), (26, 10))
    _px_rect(s, (140, 80, 40), 6, 22, 4, 2)
    return s


def roof_ac_48():
    s = _new(48, 48)
    body = pygame.Rect(6, 14, 36, 26)
    _px_rect(s, (78, 84, 96), *body)
    _outline(s, body)
    fan = pygame.Rect(16, 20, 16, 16)
    _px_rect(s, (55, 58, 66), *fan)
    _outline(s, fan)
    pygame.draw.line(s, (90, 92, 100), (16, 28), (32, 28))
    pygame.draw.line(s, (90, 92, 100), (24, 20), (24, 36))
    # feet
    _px_rect(s, (40, 44, 52), 10, 40, 6, 3)
    _px_rect(s, (40, 44, 52), 32, 40, 6, 3)
    return s


def roof_water_tank_64():
    s = _new(64, 64)
    tank = pygame.Rect(14, 10, 36, 44)
    _px_rect(s, (70, 86, 110), *tank)
    _outline(s, tank)
    # bands
    for y in (18, 30, 42):
        pygame.draw.line(s, (40, 52, 70), (14, y), (50, y))
    # cap
    _px_rect(s, (50, 62, 82), 26, 6, 12, 6)
    _outline(s, pygame.Rect(26, 6, 12, 6))
    # ladder hint
    pygame.draw.line(s, (35, 40, 48), (12, 14), (12, 52))
    for y in range(18, 52, 6):
        pygame.draw.line(s, (35, 40, 48), (10, y), (14, y))
    return s


def roof_stairwell_64():
    s = _new(64, 64)
    base = pygame.Rect(10, 18, 44, 36)
    _px_rect(s, (92, 92, 98), *base)
    _outline(s, base)
    door = pygame.Rect(26, 28, 12, 20)
    _px_rect(s, (54, 58, 66), *door)
    _outline(s, door)
    # roof lip
    _px_rect(s, (70, 70, 76), 10, 16, 44, 4)
    _outline(s, pygame.Rect(10, 16, 44, 4))
    # warning stripe
    for x in range(12, 54, 6):
        _px_rect(s, (170, 140, 40), x, 52, 3, 2)
    return s


def roof_satdish_48():
    s = _new(48, 48)
    dish = pygame.Rect(10, 8, 28, 18)
    pygame.draw.ellipse(s, (86, 90, 100), dish)
    pygame.draw.ellipse(s, (15, 18, 24), dish, 1)
    pygame.draw.line(s, (55, 58, 66), (24, 18), (34, 10))
    # stand
    pygame.draw.line(s, (60, 64, 74), (24, 26), (24, 40))
    pygame.draw.line(s, (60, 64, 74), (18, 40), (30, 40))
    _px_rect(s, (40, 44, 52), 16, 40, 16, 4)
    return s


def office_desk_48():
    s = _new(48, 48)
    top = pygame.Rect(6, 18, 36, 10)
    _px_rect(s, (120, 92, 60), *top)
    _outline(s, top)
    # legs
    _px_rect(s, (90, 70, 46), 10, 28, 6, 14)
    _px_rect(s, (90, 70, 46), 32, 28, 6, 14)
    _outline(s, pygame.Rect(10, 28, 6, 14))
    _outline(s, pygame.Rect(32, 28, 6, 14))
    # papers
    _px_rect(s, (220, 220, 230), 28, 14, 10, 6)
    pygame.draw.line(s, (180, 180, 190), (28, 18), (38, 18))
    return s


def office_table_64():
    s = _new(64, 64)
    top = pygame.Rect(10, 22, 44, 12)
    _px_rect(s, (118, 88, 58), *top)
    _outline(s, top)
    # legs
    _px_rect(s, (88, 66, 44), 16, 34, 6, 20)
    _px_rect(s, (88, 66, 44), 42, 34, 6, 20)
    _outline(s, pygame.Rect(16, 34, 6, 20))
    _outline(s, pygame.Rect(42, 34, 6, 20))
    return s


def office_cabinet_48():
    s = _new(48, 48)
    cab = pygame.Rect(12, 10, 24, 32)
    _px_rect(s, (70, 78, 92), *cab)
    _outline(s, cab)
    # drawers
    for y in (14, 22, 30):
        pygame.draw.line(s, (50, 56, 66), (12, y), (36, y))
        _px_rect(s, (160, 160, 170), 30, y + 3, 3, 2)
    return s


def office_glasswall_64():
    s = _new(64, 64)
    frame = pygame.Rect(6, 10, 52, 44)
    _px_rect(s, (40, 44, 52), *frame)
    _outline(s, frame)
    glass = pygame.Rect(8, 12, 48, 40)
    _px_rect(s, (60, 120, 150, 70), *glass)
    pygame.draw.line(s, (160, 220, 240, 110), (10, 16), (52, 16))
    pygame.draw.line(s, (160, 220, 240, 110), (10, 20), (52, 20))
    # mullions
    pygame.draw.line(s, (30, 34, 42), (32, 12), (32, 52))
    pygame.draw.line(s, (30, 34, 42), (8, 32), (56, 32))
    return s


def medical_bed_64():
    s = _new(64, 64)
    frame = pygame.Rect(10, 20, 44, 22)
    _px_rect(s, (86, 92, 104), *frame)
    _outline(s, frame)
    mattress = pygame.Rect(12, 22, 40, 18)
    _px_rect(s, (200, 210, 220), *mattress)
    _outline(s, mattress, (160, 170, 182))
    pillow = pygame.Rect(14, 24, 12, 8)
    _px_rect(s, (230, 235, 240), *pillow)
    _outline(s, pillow, (180, 190, 200))
    # legs
    _px_rect(s, (55, 60, 70), 12, 42, 6, 10)
    _px_rect(s, (55, 60, 70), 46, 42, 6, 10)
    return s


def medical_cabinet_48():
    s = _new(48, 48)
    cab = pygame.Rect(10, 10, 28, 32)
    _px_rect(s, (82, 100, 112), *cab)
    _outline(s, cab)
    # doors + red cross
    pygame.draw.line(s, (55, 66, 74), (24, 10), (24, 42))
    _px_rect(s, (180, 40, 40), 21, 22, 6, 2)
    _px_rect(s, (180, 40, 40), 23, 20, 2, 6)
    return s


def medical_trolley_48():
    s = _new(48, 48)
    tray = pygame.Rect(10, 16, 28, 8)
    _px_rect(s, (90, 96, 106), *tray)
    _outline(s, tray)
    _px_rect(s, (70, 76, 86), 14, 24, 20, 10)
    _outline(s, pygame.Rect(14, 24, 20, 10))
    # wheels
    pygame.draw.circle(s, (25, 28, 34), (16, 36), 3)
    pygame.draw.circle(s, (25, 28, 34), (32, 36), 3)
    return s


def basement_generator_64():
    s = _new(64, 64)
    body = pygame.Rect(10, 16, 44, 30)
    _px_rect(s, (66, 74, 86), *body)
    _outline(s, body)
    # panel + lights
    panel = pygame.Rect(14, 22, 14, 18)
    _px_rect(s, (40, 44, 52), *panel)
    _outline(s, panel)
    _px_rect(s, (40, 200, 80), 16, 24, 3, 3)
    _px_rect(s, (220, 180, 40), 20, 24, 3, 3)
    # exhaust
    pygame.draw.circle(s, (40, 44, 52), (44, 30), 8)
    pygame.draw.circle(s, (90, 96, 108), (44, 30), 6)
    # base
    _px_rect(s, (40, 44, 52), 10, 46, 44, 6)
    return s


def basement_pipes_64():
    s = _new(64, 64)
    # main pipe
    _px_rect(s, (86, 86, 92), 8, 20, 48, 10)
    _outline(s, pygame.Rect(8, 20, 48, 10))
    # elbow
    _px_rect(s, (86, 86, 92), 44, 20, 10, 30)
    _outline(s, pygame.Rect(44, 20, 10, 30))
    # joints
    for x in (18, 32):
        _px_rect(s, (60, 60, 66), x, 20, 3, 10)
    for y in (30, 40):
        _px_rect(s, (60, 60, 66), 44, y, 10, 3)
    return s


def basement_crates_48():
    s = _new(48, 48)
    c1 = pygame.Rect(8, 22, 16, 16)
    c2 = pygame.Rect(22, 18, 18, 20)
    _px_rect(s, (120, 86, 50), *c1)
    _px_rect(s, (110, 80, 46), *c2)
    _outline(s, c1)
    _outline(s, c2)
    pygame.draw.line(s, (80, 58, 34), (8, 30), (24, 30))
    pygame.draw.line(s, (80, 58, 34), (22, 28), (40, 28))
    return s


def basement_panel_48():
    s = _new(48, 48)
    box = pygame.Rect(14, 10, 20, 28)
    _px_rect(s, (70, 76, 88), *box)
    _outline(s, box)
    _px_rect(s, (40, 44, 52), 18, 14, 12, 18)
    _outline(s, pygame.Rect(18, 14, 12, 18))
    _px_rect(s, (220, 180, 40), 18, 34, 4, 3)
    _px_rect(s, (40, 200, 80), 24, 34, 4, 3)
    _px_rect(s, (200, 60, 60), 30, 34, 4, 3)
    return s


def lab_freezer_64():
    s = _new(64, 64)
    unit = pygame.Rect(16, 8, 32, 48)
    _px_rect(s, (86, 110, 130), *unit)
    _outline(s, unit)
    # door seam
    pygame.draw.line(s, (55, 70, 86), (32, 8), (32, 56))
    # frosty highlight
    _px_rect(s, (200, 240, 255, 80), 18, 12, 10, 34)
    # handle
    _px_rect(s, (180, 180, 190), 26, 30, 2, 10)
    _px_rect(s, (180, 180, 190), 38, 30, 2, 10)
    return s


def lab_console_64():
    s = _new(64, 64)
    base = pygame.Rect(10, 22, 44, 28)
    _px_rect(s, (64, 70, 82), *base)
    _outline(s, base)
    screen = pygame.Rect(18, 26, 28, 14)
    _px_rect(s, (40, 180, 140), *screen)
    _outline(s, screen)
    # buttons
    for i, col in enumerate([(220, 180, 40), (200, 60, 60), (40, 200, 80)]):
        _px_rect(s, col, 18 + i * 8, 42, 5, 4)
    return s


def lab_bench_64():
    s = _new(64, 64)
    top = pygame.Rect(10, 22, 44, 10)
    _px_rect(s, (94, 96, 104), *top)
    _outline(s, top)
    # legs
    _px_rect(s, (60, 64, 74), 14, 32, 6, 20)
    _px_rect(s, (60, 64, 74), 44, 32, 6, 20)
    _outline(s, pygame.Rect(14, 32, 6, 20))
    _outline(s, pygame.Rect(44, 32, 6, 20))
    # beakers
    pygame.draw.circle(s, (120, 220, 255, 160), (26, 18), 4)
    pygame.draw.circle(s, (120, 255, 160, 160), (36, 18), 4)
    return s


def lab_tubes_48():
    s = _new(48, 48)
    rack = pygame.Rect(10, 26, 28, 10)
    _px_rect(s, (70, 76, 86), *rack)
    _outline(s, rack)
    for i in range(4):
        x = 14 + i * 6
        _px_rect(s, (140, 200, 220, 120), x, 14, 4, 14)
        pygame.draw.line(s, (180, 240, 255, 160), (x, 16), (x + 3, 16))
    return s


def gate_closed_64():
    s = _new(64, 64)
    frame = pygame.Rect(10, 8, 44, 48)
    _px_rect(s, (55, 60, 70), *frame)
    _outline(s, frame)
    # bars
    for x in range(16, 50, 6):
        pygame.draw.line(s, (25, 28, 34), (x, 12), (x, 54))
    # warning stripe
    for x in range(14, 54, 8):
        _px_rect(s, (220, 180, 40), x, 56, 4, 2)
    # lock light
    pygame.draw.circle(s, (200, 60, 60), (48, 14), 3)
    return s


def gate_open_64():
    s = _new(64, 64)
    frame = pygame.Rect(10, 8, 44, 48)
    _px_rect(s, (55, 60, 70), *frame)
    _outline(s, frame)
    # open split doors
    left = pygame.Rect(10, 8, 18, 48)
    right = pygame.Rect(36, 8, 18, 48)
    _px_rect(s, (70, 76, 86), *left)
    _px_rect(s, (70, 76, 86), *right)
    _outline(s, left)
    _outline(s, right)
    # green light
    pygame.draw.circle(s, (40, 200, 80), (48, 14), 3)
    return s


def item_keycard_24():
    s = _new(24, 24)
    card = pygame.Rect(3, 7, 18, 10)
    _px_rect(s, (70, 140, 255), *card)
    _outline(s, card)
    # chip
    _px_rect(s, (230, 210, 120), 6, 10, 5, 4)
    _outline(s, pygame.Rect(6, 10, 5, 4), (150, 130, 70))
    # notch
    pygame.draw.circle(s, (15, 18, 24), (19, 12), 2)
    return s


def item_fuse_24():
    s = _new(24, 24)
    body = pygame.Rect(6, 9, 12, 6)
    _px_rect(s, (210, 210, 220), *body)
    _outline(s, body, (40, 44, 54))
    _px_rect(s, (200, 160, 60), 8, 10, 8, 4)
    # caps
    _px_rect(s, (120, 120, 130), 4, 10, 2, 4)
    _px_rect(s, (120, 120, 130), 18, 10, 2, 4)
    return s


def item_codebook_24():
    s = _new(24, 24)
    book = pygame.Rect(6, 6, 12, 14)
    _px_rect(s, (180, 120, 60), *book)
    _outline(s, book)
    # pages
    _px_rect(s, (230, 230, 240), 17, 7, 2, 12)
    # label
    _px_rect(s, (60, 44, 30), 8, 10, 8, 2)
    return s


def item_antidote_24():
    s = _new(24, 24)
    vial = pygame.Rect(9, 6, 6, 14)
    _px_rect(s, (140, 220, 160, 170), *vial)
    _outline(s, vial)
    _px_rect(s, (230, 230, 240), 9, 6, 6, 3)
    _outline(s, pygame.Rect(9, 6, 6, 3), (120, 120, 130))
    # liquid line
    pygame.draw.line(s, (60, 200, 120), (10, 16), (13, 16))
    return s


def item_gate_switch_24():
    s = _new(24, 24)
    base = pygame.Rect(7, 8, 10, 12)
    _px_rect(s, (90, 92, 104), *base)
    _outline(s, base)
    # lever
    pygame.draw.line(s, (220, 180, 40), (12, 8), (16, 4))
    pygame.draw.circle(s, (220, 180, 40), (16, 4), 2)
    return s


def item_beacon_24():
    s = _new(24, 24)
    body = pygame.Rect(10, 8, 4, 12)
    _px_rect(s, (120, 120, 130), *body)
    _outline(s, body)
    pygame.draw.circle(s, (255, 220, 80), (12, 6), 4)
    pygame.draw.circle(s, (255, 220, 80, 120), (12, 6), 6, 1)
    return s


def item_exit_key_24():
    s = _new(24, 24)
    # simple key
    pygame.draw.circle(s, (255, 210, 60), (9, 12), 4)
    pygame.draw.circle(s, (15, 18, 24), (9, 12), 4, 1)
    pygame.draw.rect(s, (255, 210, 60), pygame.Rect(12, 11, 9, 2))
    pygame.draw.rect(s, (255, 210, 60), pygame.Rect(18, 9, 2, 2))
    pygame.draw.rect(s, (255, 210, 60), pygame.Rect(16, 13, 2, 2))
    return s


def item_money_24():
    s = _new(24, 24)
    # coin
    pygame.draw.circle(s, (255, 210, 60), (12, 12), 9)
    pygame.draw.circle(s, (15, 18, 24), (12, 12), 9, 1)
    pygame.draw.circle(s, (255, 240, 180), (9, 9), 3)
    # dollar sign (simple)
    pygame.draw.line(s, (40, 44, 52), (12, 6), (12, 18), 2)
    pygame.draw.line(s, (40, 44, 52), (9, 8), (15, 8), 2)
    pygame.draw.line(s, (40, 44, 52), (9, 16), (15, 16), 2)
    return s


def main():
    # Headless friendly init
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()

    outputs = [
        ("roof_vent_32.png", roof_vent_32()),
        ("roof_ac_48.png", roof_ac_48()),
        ("roof_water_tank_64.png", roof_water_tank_64()),
        ("roof_stairwell_64.png", roof_stairwell_64()),
        ("roof_satdish_48.png", roof_satdish_48()),
        ("office_desk_48.png", office_desk_48()),
        ("office_table_64.png", office_table_64()),
        ("office_cabinet_48.png", office_cabinet_48()),
        ("office_glasswall_64.png", office_glasswall_64()),
        ("medical_bed_64.png", medical_bed_64()),
        ("medical_cabinet_48.png", medical_cabinet_48()),
        ("medical_trolley_48.png", medical_trolley_48()),
        ("basement_generator_64.png", basement_generator_64()),
        ("basement_pipes_64.png", basement_pipes_64()),
        ("basement_crates_48.png", basement_crates_48()),
        ("basement_panel_48.png", basement_panel_48()),
        ("lab_freezer_64.png", lab_freezer_64()),
        ("lab_console_64.png", lab_console_64()),
        ("lab_bench_64.png", lab_bench_64()),
        ("lab_tubes_48.png", lab_tubes_48()),
        ("gate_closed_64.png", gate_closed_64()),
        ("gate_open_64.png", gate_open_64()),
    ]

    item_outputs = [
        ("keycard_24.png", item_keycard_24()),
        ("fuse_24.png", item_fuse_24()),
        ("codebook_24.png", item_codebook_24()),
        ("antidote_24.png", item_antidote_24()),
        ("gate_switch_24.png", item_gate_switch_24()),
        ("beacon_24.png", item_beacon_24()),
        ("exit_key_24.png", item_exit_key_24()),
        ("money_24.png", item_money_24()),
    ]

    print(f"Writing {len(outputs)} prop sprites to {OUT_DIR} ...")
    for name, surf in outputs:
        path = _save(surf, name)
        print(" -", path.relative_to(ROOT))

    print(f"Writing {len(item_outputs)} item icons to {ITEM_DIR} ...")
    for name, surf in item_outputs:
        path = _save_item(surf, name)
        print(" -", path.relative_to(ROOT))

    pygame.quit()


if __name__ == "__main__":
    main()

