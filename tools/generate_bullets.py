from __future__ import annotations

import os
from pathlib import Path
import pygame


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "Sprites" / "Sprites_Effect" / "Bullets"


def _new(w: int, h: int) -> pygame.Surface:
    return pygame.Surface((w, h), pygame.SRCALPHA)


def make_bullet(idx: int) -> pygame.Surface:
    s = _new(32, 32)
    # palette cycle
    colors = [
        (255, 230, 120),
        (120, 220, 255),
        (255, 120, 120),
        (160, 255, 160),
        (220, 160, 255),
        (255, 180, 60),
    ]
    c = colors[idx % len(colors)]
    core = (max(0, c[0] - 40), max(0, c[1] - 40), max(0, c[2] - 40))
    # trail
    pygame.draw.line(s, (*c, 110), (6, 16), (18, 16), 4)
    pygame.draw.circle(s, (*c, 200), (20, 16), 6)
    pygame.draw.circle(s, (*core, 240), (20, 16), 3)
    pygame.draw.circle(s, (255, 255, 255, 220), (18, 14), 2)
    return s


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(1, 30):
        surf = make_bullet(i)
        path = OUT_DIR / f"{i:02}.png"
        pygame.image.save(surf, str(path))
        print("Wrote", path.relative_to(ROOT))
    pygame.quit()


if __name__ == "__main__":
    main()

