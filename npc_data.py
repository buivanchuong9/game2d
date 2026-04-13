"""
npc_data.py — NPC pool, portrait system, and random NPC spawning for infinite map.
Matches story: "Last Roof: Escape City" - survivors in a zombie-infested city.
"""
import random

# ---------------------------------------------------------------------------
# NPC dialogue and lore pool
# ---------------------------------------------------------------------------

NPC_POOL = [
    {
        "name": "Phi công",
        "portrait_color": (255, 210, 60),
        "portrait_type": "pilot",
        "lines": [
            "Tôi đang cố hạ cánh gần tòa nhà phía bắc.",
            "Nếu cậu tìm thấy beacon, kích hoạt lên — tôi sẽ đến.",
        ],
        "reward": "radio",
        "hint": "Đi về phía bắc để tìm điểm di tản.",
        "sprite_path": "Sprites/Sprites_NPC/pilot.png",
    },
    {
        "name": "Bảo vệ Nam",
        "portrait_color": (60, 120, 255),
        "portrait_type": "guard",
        "lines": [
            "Phòng kỹ thuật còn có thẻ từ dự phòng bên trong tủ.",
            "Cẩn thận — loại zombie chạy nhanh đang tuần tra hành lang phía đông.",
        ],
        "reward": "map",
        "hint": "Thẻ từ ở khu kỹ thuật.",
        "sprite_path": "Sprites/Sprites_NPC/guard.png",
    },
    {
        "name": "Y tá Linh",
        "portrait_color": (60, 220, 100),
        "portrait_type": "medic",
        "lines": [
            "Tôi còn giữ được một ít thuốc. Cậu cần không?",
            "Kho chứa tầng 2 vẫn còn nhiều tiếp tế, nhưng bị zombie máu dày canh gác.",
        ],
        "reward": "medkit",
        "hint": "Kho thuốc ở tầng 2.",
        "sprite_path": "Sprites/Sprites_NPC/medic.png",
    },
    {
        "name": "Kỹ thuật viên Huy",
        "portrait_color": (255, 140, 30),
        "portrait_type": "engineer",
        "lines": [
            "Hệ thống điện dự phòng còn hoạt động nếu đặt đúng cầu chì.",
            "Cổng sân có thể mở từ bảng điều khiển trong kho.",
        ],
        "reward": "shortcut",
        "hint": "Cầu chì mở cổng sân.",
        "sprite_path": "Sprites/Sprites_NPC/engineer.png",
    },
    {
        "name": "Cô gái tên Vy",
        "portrait_color": (220, 100, 220),
        "portrait_type": "survivor_f",
        "lines": [
            "Tôi trốn ở đây được hai ngày rồi...",
            "Nghe nói phía tây có một đường ngầm còn nguyên vẹn.",
        ],
        "reward": None,
        "hint": "Đường ngầm phía tây.",
        "sprite_path": "Sprites/Sprites_NPC/survivor_f.png",
    },
    {
        "name": "Binh sĩ Khoa",
        "portrait_color": (130, 200, 80),
        "portrait_type": "soldier",
        "lines": [
            "Đơn vị tôi bị bao vây từ đêm qua. Mình tôi sống sót.",
            "Còn đạn trên xác đồng đội ở hành lang C.",
        ],
        "reward": "ammo",
        "hint": "Đạn ở hành lang C.",
        "sprite_path": "Sprites/Sprites_NPC/soldier.png",
    },
    {
        "name": "Bác sĩ Hòa",
        "portrait_color": (80, 220, 200),
        "portrait_type": "doctor",
        "lines": [
            "Virus này lây rất nhanh qua vết cắn. Đừng để bị thương.",
            "Tôi đang nghiên cứu mẫu máu — có thể có kháng thể.",
        ],
        "reward": "medkit",
        "hint": "Giữ HP cao, tránh bị cắn.",
        "sprite_path": "Sprites/Sprites_NPC/doctor.png",
    },
    {
        "name": "Ông già Phước",
        "portrait_color": (200, 180, 120),
        "portrait_type": "elder",
        "lines": [
            "Tôi từng làm bảo vệ tòa nhà này 20 năm.",
            "Có đường thoát hiểm bí mật ở tầng hầm — khóa là 4821.",
        ],
        "reward": "shortcut",
        "hint": "Mã cửa tầng hầm: 4821.",
        "sprite_path": "Sprites/Sprites_NPC/elder.png",
    },
    {
        "name": "Nhà báo Lan",
        "portrait_color": (255, 100, 100),
        "portrait_type": "journalist",
        "lines": [
            "Tôi đã ghi lại hết — dịch bắt đầu từ khu thí nghiệm phía đông thành phố.",
            "Nếu cậu thoát được, hãy nói với thế giới sự thật này.",
        ],
        "reward": None,
        "hint": "Nguồn gốc virus: khu thí nghiệm phía đông.",
        "sprite_path": "Sprites/Sprites_NPC/journalist.png",
    },
    {
        "name": "Trẻ em tên Bin",
        "portrait_color": (255, 220, 80),
        "portrait_type": "child",
        "lines": [
            "Bố tôi đâu rồi?... Nghe nói ông bị kẹt ở tầng 3.",
            "Tôi sợ lắm... Anh có thể ở lại không?",
        ],
        "reward": None,
        "hint": "Ai đó cần giúp đỡ ở tầng 3.",
        "sprite_path": "Sprites/Sprites_NPC/child.png",
    },
]

# ---------------------------------------------------------------------------
# Chunk-based NPC spawning
# ---------------------------------------------------------------------------

# Track which chunks already have NPCs
_spawned_chunks = {}


def get_random_npcs_for_chunk(chunk_x, chunk_y, tile_size=16, chunk_size=20):
    """
    Return a list of (npc_dict, world_tx, world_ty) for newly entered chunk.
    Each chunk gets 0-2 random NPCs from the pool.
    """
    key = (chunk_x, chunk_y)
    if key in _spawned_chunks:
        return _spawned_chunks[key]

    # Deterministic but varied based on chunk position
    rng = random.Random(chunk_x * 1000003 + chunk_y * 999983 + 7)
    count = rng.choices([0, 1, 2], weights=[55, 35, 10])[0]
    result = []
    for _ in range(count):
        npc_data = rng.choice(NPC_POOL).copy()
        # Random tile within chunk
        tx = chunk_x * chunk_size + rng.randint(2, chunk_size - 2)
        ty = chunk_y * chunk_size + rng.randint(2, chunk_size - 2)
        # Don't spawn too close to origin (story chapters are there)
        if abs(chunk_x) < 3 and abs(chunk_y) < 3:
            _spawned_chunks[key] = []
            return []
        result.append((npc_data, tx, ty))

    _spawned_chunks[key] = result
    return result


def reset_spawned_chunks():
    """Clear chunk cache (call on game reset)."""
    _spawned_chunks.clear()
