## Cách thêm âm thanh vào game

Bạn chỉ cần đặt file âm thanh **đúng tên** vào đúng thư mục dưới `Sounds/` là game tự load và dùng.

### Thư mục
- Bạn chỉ cần **1 thư mục duy nhất**: `Sounds/`
- Thả tất cả file âm thanh vào **thẳng `Sounds/`** (không cần chia folder).

Game sẽ tự load đệ quy tất cả file `.wav/.mp3/.ogg` trong `Sounds/**`.

### Tên file SFX cần có (tiếng Việt không dấu)
Bạn có thể dùng **.mp3 hoặc .wav hoặc .ogg**. Game sẽ tự dò theo thứ tự và có **tên dự phòng** (tên cũ cũng chạy).

Khuyến nghị: dùng `.mp3`.

#### Vũ khí (mỗi loại 1 file `.mp3`)
- `ban_sung_truong.(mp3|wav|ogg)`: bắn súng trường (rifle/AK/basic gun)
- `ban_tieu_lien.(mp3|wav|ogg)`: bắn SMG
- `ban_shotgun.(mp3|wav|ogg)`: bắn shotgun
- `ban_tia.(mp3|wav|ogg)`: bắn sniper
- `ban_b40.(mp3|wav|ogg)`: bắn rocket/RPG
- `chem.(mp3|wav|ogg)`: chém (katana/melee)

#### Thay đạn (mỗi loại 1 file `.mp3`)
- `thay_dan_sung_truong.(mp3|wav|ogg)`
- `thay_dan_tieu_lien.(mp3|wav|ogg)`
- `thay_dan_shotgun.(mp3|wav|ogg)`
- `thay_dan_tia.(mp3|wav|ogg)`
- `thay_dan_b40.(mp3|wav|ogg)`

#### Combat/UI
- `zombie_trung_dan.(mp3|wav|ogg)`
- `zombie_chet.(mp3|wav|ogg)`
- `nhan_vat_trung_don.(mp3|wav|ogg)`
- `mo_cong.(mp3|wav|ogg)`
- `roi_vat_pham.(mp3|wav|ogg)`
- `hoan_thanh_nhiem_vu.(mp3|wav|ogg)`

### Tên file nhạc nền
Đặt thẳng trong `Sounds/`:

- `nhac_nen_chinh.mp3` (hoặc `.wav/.ogg`)

Nếu chưa có `Sounds/nhac_nen_chinh.mp3` thì game sẽ fallback sang `Sounds/Game_loop_music.mp3`.

