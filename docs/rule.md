# Orbit Wars — Luật chơi đầy đ

## Tổng quan

- Bàn cờ **100×100 không gian liên tục**, gốc toạ độ ở góc trên-trái.
- **Mặt trời** ở tâm `(50, 50)`, bán kính `10`. Fleet bay cắt qua mặt trời sẽ bị huỷ.
- Mỗi người chơi bắt đầu với **1 hành tinh nhà** (home planet, 10 ships).
- Mục tiêu: kiểm soát bản đồ, kết thúc với **tổng số ship nhiều nhất** (trên hành tinh + trong fleet).
- Game kéo dài **500 turn**.

## Tính đối xứng

Mọi hành tinh và comet được đặt với **đối xứng gương 4 chiều** quanh tâm:
`(x, y)`, `(100-x, y)`, `(x, 100-y)`, `(100-x, 100-y)`.
→ Công bằng bất kể vị trí xuất phát. Có thể khai thác: vị trí đối thủ suy ra được qua đối xứng.

## Hành tinh (Planet)

Biểu diễn: `[id, owner, x, y, radius, ships, production]`

- `owner`: Player ID (0-3), hoặc `-1` nếu trung lập (neutral).
- `radius = 1 + ln(production)` — production cao thì hành tinh to hơn.
- `production`: số nguyên 1–5. Mỗi turn hành tinh sở hữu sinh ra `production` ships.
- `ships`: garrison hiện tại. Khởi đầu 5–99 (lệch về giá trị thấp).

### Loại hành tinh

- **Orbiting (quay):** `orbital_radius + planet_radius < 50` → quay quanh mặt trời với vận tốc góc cố định **0.025–0.05 rad/turn** (random mỗi game). Dùng `initial_planets` + `angular_velocity` để dự đoán vị trí.
- **Static (tĩnh):** xa tâm hơn, không quay.

Bản đồ có **20–40 hành tinh** (5–10 nhóm đối xứng × 4). Ít nhất 3 nhóm tĩnh, ít nhất 1 nhóm quay.

### Home planet

Một nhóm đối xứng được chọn làm điểm xuất phát. Game 2 người: 2 hành tinh đối xứng chéo (Q1 và Q4). Game 4 người: mỗi người 1 hành tinh trong nhóm. Home bắt đầu với **10 ships**.

## Fleet

Biểu diễn: `[id, owner, x, y, angle, from_planet_id, ships]`

- `angle`: hướng bay (radian).
- `ships`: số ship trong fleet (KHÔNG đổi khi đang bay).

### Tốc độ fleet (quan trọng cho intercept)

```
speed = 1.0 + (maxSpeed - 1.0) * (log(ships) / log(1000)) ^ 1.5
```

- 1 ship → 1.0 unit/turn.
- Fleet lớn bay nhanh hơn, tiệm cận max **6.0**.
- ~500 ship → ~5; ~1000 ship → đạt max.

→ **Hệ quả chiến thuật:** gửi fleet lớn rẻ hơn về thời gian (nhanh hơn). Tách nhỏ fleet làm chậm tổng thể.

### Di chuyển

Fleet bay thẳng theo `angle` với tốc độ tính ở trên mỗi turn. Bị xoá nếu:
- Ra ngoài biên (rời 100×100).
- Cắt mặt trời (đoạn đường tới gần mặt trời ≤ bán kính).
- Va hành tinh (đoạn đường tới gần hành tinh ≤ bán kính) → kích hoạt combat.

Va chạm là **liên tục** — kiểm tra cả đoạn từ vị trí cũ → mới, không chỉ điểm cuối.

### Phóng fleet (Launch)

Mỗi turn agent trả về list moves: `[from_planet_id, direction_angle, num_ships]`.
- Chỉ phóng từ hành tinh mình sở hữu.
- Không phóng nhiều hơn số ship hiện có.
- Fleet spawn ngay ngoài bán kính hành tinh theo hướng cho.
- Có thể phóng nhiều lệnh từ cùng/khác hành tinh trong 1 turn.

## Comet (sao chổi)

Vật thể tạm thời bay qua bàn cờ trên quỹ đạo elip quanh mặt trời. Spawn theo **nhóm 4** (mỗi quadrant 1) tại step **50, 150, 250, 350, 450**.

- Bán kính: 1.0 (cố định).
- Production: 1 ship/turn khi sở hữu.
- Ship khởi đầu: random lệch thấp (min của 4 lần roll 1–99). Cả 4 comet cùng nhóm chung số ship khởi đầu.
- Tốc độ: `cometSpeed` (default 4.0).
- Nhận diện: `comet_planet_ids` trong observation. Comet cũng nằm trong mảng `planets` và theo mọi luật hành tinh thường.
- Khi comet rời bàn cờ → bị xoá cùng ship đang đóng. Comet bị xoá **trước** bước launch → không phóng được từ comet sắp rời.
- Field `comets`: `paths` (toàn quỹ đạo) + `path_index` (vị trí hiện tại) → dự đoán vị trí tương lai.

## Thứ tự xử lý mỗi turn

1. **Comet expiration** — xoá comet đã rời bàn.
2. **Comet spawning** — spawn nhóm comet mới tại step quy định.
3. **Fleet launch** — xử lý action người chơi, tạo fleet mới.
4. **Production** — mọi hành tinh sở hữu (gồm comet) sinh ship.
5. **Fleet movement** — di chuyển fleet, check out-of-bounds / sun / planet collision. Fleet va hành tinh → xếp hàng combat.
6. **Planet rotation & comet movement** — hành tinh quay, comet tiến. Fleet bị hành tinh/comet đang di chuyển "quét trúng" → vào combat.
7. **Combat resolution** — giải quyết mọi combat.

> Lưu ý: production xảy ra **trước** movement → ship mới có ngay trong turn phóng.

## Combat

Khi ≥1 fleet va hành tinh (bay vào hoặc bị quét):

1. Gom các fleet đến theo owner. Ship cùng owner cộng dồn.
2. **Lực tấn công lớn nhất đánh lực lớn nhì. Phần chênh lệch sống sót.**
3. Nếu có quân tấn công sống sót:
   - Cùng owner với hành tinh → cộng vào garrison.
   - Khác owner → đánh garrison. Nếu vượt garrison → đổi chủ, garrison mới = phần dư.
4. Hai lực tấn công bằng nhau → **tất cả bị huỷ** (không ai sống).

> Hệ quả: tấn công hành tinh trung lập garrison G cần **G+1** ship để chiếm. Nhưng nếu nhiều bên cùng đánh, phải tính cả lực bên thứ ba.

## Kết thúc & tính điểm

Game kết thúc khi:
- Đủ 500 turn, HOẶC
- Elimination: chỉ còn ≤1 người chơi có hành tinh hoặc fleet.

**Final score = tổng ship trên hành tinh sở hữu + tổng ship trong fleet sở hữu.** Cao nhất thắng.

> Score chênh lệch KHÔNG ảnh hưởng skill rating — chỉ thắng/thua/hoà. → Tối ưu xác suất thắng, không cần thắng đậm.

## Observation Reference

| Field | Type | Mô tả |
|---|---|---|
| `planets` | `[[id, owner, x, y, radius, ships, production], ...]` | Mọi hành tinh gồm comet |
| `fleets` | `[[id, owner, x, y, angle, from_planet_id, ships], ...]` | Fleet đang hoạt động |
| `player` | int | Player ID của bạn (0-3) |
| `angular_velocity` | float | Vận tốc quay hành tinh (rad/turn) |
| `initial_planets` | như planets | Vị trí hành tinh lúc bắt đầu |
| `comets` | `[{planet_ids, paths, path_index}, ...]` | Dữ liệu nhóm comet |
| `comet_planet_ids` | `[int, ...]` | ID hành tinh là comet |
| `remainingOverageTime` | float | Ngân sách overage time còn lại (giây) |

## Action Format

```
[[from_planet_id, direction_angle, num_ships], ...]
```
- `direction_angle`: radian (0 = phải, pi/2 = xuống).
- Trả `[]` để không làm gì.

## Configuration (default)

| Param | Default | Mô tả |
|---|---|---|
| `episodeSteps` | 500 | Số turn tối đa |
| `actTimeout` | 1 | Giây mỗi turn |
| `shipSpeed` | 6.0 | Tốc độ fleet tối đa |
| `sunRadius` | 10.0 | Bán kính mặt trời |
| `boardSize` | 100.0 | Kích thước bàn |
| `cometSpeed` | 4.0 | Tốc độ comet |

## Helper import

```python
from kaggle_environments.envs.orbit_wars.orbit_wars import (
    Planet, Fleet, CENTER, ROTATION_RADIUS_LIMIT
)
```
