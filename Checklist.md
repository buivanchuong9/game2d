Danh sách cải tiến game 2D (Pygame)
1. Ưu tiên cao
Cải thiện cơ chế bắn của nhân vật
→ Thêm chế độ ngắm có thể chuyển đổi (chuột / auto aim / lock-on)
Thay cách vào shop bằng phím
→ Tạo NPC bán hàng (tương tác để mở shop)
Thêm giao diện trạng thái game
→ Nút thoát game (menu tạm dừng)
→ Màn hình Game Over (chơi lại / thoát)
Cân bằng lại vũ khí
→ Điều chỉnh damage, tốc độ bắn, độ tản
→ Fix vũ khí yếu (ví dụ shotgun quá yếu)
Cải tiến hệ thống chỉ dẫn
→ Bỏ chỉ dẫn tới item gần nhất
→ Thêm chỉ dẫn theo mục tiêu (objective)
→ Nhấn phím để hiển thị hướng tới mục tiêu

Chuẩn hóa hệ thống đạn
→ Dùng sprite từ:

Sprites_Effect/Bullets/All_Fire_Bullet_Pixel_16x16_00.png
Sprites_Effect/Bullets/All_Fire_Bullet_Pixel_16x16_05.png

→ Mỗi vũ khí dùng 1 loại đạn riêng
→ Cắt sprite theo grid 16x16
→ Mapping: weapon -> bullet_sprite

Fix va chạm quái
→ Quái không được đi xuyên tường
→ Áp dụng collision giống player (tile/block)
Cải thiện vùng tương tác (interaction)
→ Không cần đứng đúng 1 ô
→ Tạo interaction radius (vd: bán kính 32–64px)
→ Nhấn E khi ở gần là tương tác được

Hệ thống pet (ảnh + skill)
→ Sprite pet nằm ở:

Sprites/Sprites_Pet/

→ Cắt lại sprite pet đúng frame (animation)

→ Skill pet dùng sprite từ:

Sprites_Effect/Pet_Power.png
Sprites_Effect/Pet_SuperPowers.png

→ Ảnh chứa nhiều skill → cần cắt sprite sheet thành từng frame riêng

2. Ưu tiên trung bình
Cải thiện lời thoại NPC
→ Tự nhiên hơn, ít lặp, theo ngữ cảnh
Cải thiện tutorial
→ Hướng dẫn từng bước rõ ràng
→ Hiển thị control + mục tiêu dần dần
3. Tùy chọn
Thay nhạc nền (BGM)
→ Phù hợp không khí game hơn
→ Có thể chia trạng thái (combat / bình thường)