from __future__ import annotations

import os
from pathlib import Path
import pygame


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "Sprites" / "Sprites_Weapon" / "armory"


def _new(w: int, h: int) -> pygame.Surface:
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _rect(s: pygame.Surface, color, x, y, w, h):
    pygame.draw.rect(s, color, pygame.Rect(int(x), int(y), int(w), int(h)))


def _outline(s: pygame.Surface, x, y, w, h, col=(15, 18, 24)):
    pygame.draw.rect(s, col, pygame.Rect(int(x), int(y), int(w), int(h)), 1)


def make_gun(style: str, seed: int) -> pygame.Surface:
    # 32x32 top-down side-ish pixel icon
    s = _new(32, 32)
    base = (70 + (seed * 3) % 60, 70 + (seed * 7) % 60, 80 + (seed * 11) % 60)
    accent = (220, 180, 40) if "flame" not in style else (255, 120, 60)
    glow = (80, 220, 120) if "poison" in style else (140, 220, 255) if "taesar" in style else (255, 240, 180)

    # body
    _rect(s, base, 6, 14, 18, 6)
    _outline(s, 6, 14, 18, 6)
    # grip
    _rect(s, (base[0] - 15, base[1] - 15, base[2] - 15), 10, 20, 6, 8)
    _outline(s, 10, 20, 6, 8)

    if style == "pistol":
        _rect(s, base, 22, 15, 6, 4)
        _outline(s, 22, 15, 6, 4)
        _rect(s, accent, 8, 15, 3, 2)
    elif style == "rifle":
        _rect(s, base, 22, 15, 8, 4)
        _outline(s, 22, 15, 8, 4)
        _rect(s, (50, 52, 62), 4, 15, 3, 4)  # stock
        _outline(s, 4, 15, 3, 4)
        _rect(s, accent, 18, 13, 4, 2)  # sight
    elif style == "smg":
        _rect(s, base, 22, 15, 6, 4)
        _outline(s, 22, 15, 6, 4)
        _rect(s, (50, 52, 62), 4, 16, 4, 3)
        _outline(s, 4, 16, 4, 3)
        _rect(s, accent, 16, 13, 3, 2)
    elif style == "shotgun":
        _rect(s, base, 22, 14, 10, 4)
        _outline(s, 22, 14, 10, 4)
        _rect(s, (120, 92, 60), 4, 14, 6, 4)  # wood stock
        _outline(s, 4, 14, 6, 4)
        _rect(s, accent, 14, 13, 4, 2)
    elif style == "sniper":
        _rect(s, base, 22, 15, 10, 3)
        _outline(s, 22, 15, 10, 3)
        _rect(s, (50, 52, 62), 4, 15, 4, 3)
        _outline(s, 4, 15, 4, 3)
        _rect(s, accent, 16, 12, 10, 3)  # scope
        _outline(s, 16, 12, 10, 3)
    elif style == "minigun":
        _rect(s, base, 6, 13, 16, 8)
        _outline(s, 6, 13, 16, 8)
        for i in range(3):
            _rect(s, (40, 44, 54), 22, 13 + i * 2, 9, 1)
        _rect(s, accent, 8, 12, 10, 2)
    elif style == "flamethrower":
        _rect(s, base, 6, 14, 16, 6)
        _outline(s, 6, 14, 16, 6)
        _rect(s, (60, 64, 74), 22, 14, 8, 6)
        _outline(s, 22, 14, 8, 6)
        pygame.draw.circle(s, glow, (28, 17), 3)
    elif style == "grenade_launcher":
        _rect(s, base, 6, 14, 14, 6)
        _outline(s, 6, 14, 14, 6)
        _rect(s, (60, 64, 74), 20, 14, 10, 6)
        _outline(s, 20, 14, 10, 6)
        pygame.draw.circle(s, accent, (26, 17), 2)
    elif style == "poison_gun":
        _rect(s, base, 6, 14, 16, 6)
        _outline(s, 6, 14, 16, 6)
        pygame.draw.circle(s, (80, 220, 120), (24, 17), 3)
        pygame.draw.circle(s, (80, 220, 120, 120), (24, 17), 5, 1)
    elif style == "taesar_gun":
        _rect(s, base, 6, 14, 16, 6)
        _outline(s, 6, 14, 16, 6)
        pygame.draw.line(s, (140, 220, 255), (22, 14), (30, 20), 2)
        pygame.draw.line(s, (140, 220, 255), (22, 20), (30, 14), 2)

    # small highlight
    _rect(s, (220, 220, 235, 150), 8, 15, 6, 1)
    return s


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    styles = [
        "pistol",
        "rifle",
        "smg",
        "shotgun",
        "sniper",
        "minigun",
        "flamethrower",
        "grenade_launcher",
        "poison_gun",
        "taesar_gun",
    ]

    # 50 weapons total: 5 variants per style
    count = 0
    for style in styles:
        for v in range(1, 6):
            seed = (hash(style) & 0xFFFF) + v * 97
            img = make_gun(style, seed)
            fname = f"{style}_{v:02}.png"
            pygame.image.save(img, str(OUT_DIR / fname))
            count += 1
            print("Wrote", (OUT_DIR / fname).relative_to(ROOT))

    pygame.quit()
    print("Total weapons:", count)


if __name__ == "__main__":
    main()

