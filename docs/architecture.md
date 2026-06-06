# Kiến trúc agent `orbit_lite` 

## Bản đồ thư mục 

```
main.py                      # Entry point Kaggle (def agent cuối cùng) + vòng lặp turn
orbit_lite/
├── __init__.py              # Khai báo package
├── constants.py             # Hằng số physics + capacity + tham số early-termination
├── geometry.py              # Hàm tensor thuần: fleet_speed, khoảng cách, va sun...
├── aiming.py                # orbit_phase_index: đổi step quan sát -> pha quỹ đạo engine
├── obs.py                   # parse_obs: 7-field tensor -> ParsedObs (trường có tên)
├── adapter.py               # obs dict <-> tensor; payload sparse -> move-list Kaggle
├── movement.py     (90 KB)  # ★ LÕI: dự đoán vị trí hành tinh/comet + chiếu garrison tương lai
├── movement_aiming.py       # Aim angle/ETA cho (source,target,size) dùng cache vị trí
├── intercept_aim.py         # Bắn đón liên tục (sub-turn) cho hành tinh quay + check va chạm
├── distance_cache.py        # Cache khoảng cách chéo-thời-gian cross_dist[k,s,t]
├── garrison_launch.py       # "What-if launch": chiếu dòng ship khi mình phóng (flow-diff)
├── movement_step.py         # Áp launch dự kiến vào movement, gộp/khử trùng lặp lệnh
└── planner_core.py (29 KB)  # Bộ não: chấm điểm net-ship-delta, shortlist, chọn greedy
```

## Luồng một turn (đọc `main.py`)

```
agent(obs)
 └─ single_obs_to_tensor(obs)              # adapter: dict -> dict tensor 7-field
     └─ ProducerLiteRuntime.tensor_action
         └─ run_turn(obs_tensors, config, player_count, memory)
             1. parse_obs                  # tensor -> ParsedObs (owner/ships/alive/owned...)
             2. ensure_planet_movement     # dựng/cập nhật PlanetMovement (cache cuộn qua turn)
             3. build_distance_cache       # cross_dist[k,s,t] tới horizon
             4. movement.garrison_status   # chiếu owner/ships mỗi planet qua horizon (nếu mình KHÔNG làm gì)
             5. plan_lite_waves            # ★ sinh + chấm + chọn các đợt phóng (+ regroup)
             6. disambiguate / infer / apply_private_planned_launches  # ghi lệnh vào movement
             7. entries_to_sparse_payload  # -> payload thưa
 └─ sparse_action_row_to_moves             # adapter: payload -> [[from_id, angle, ships], ...]
```

`memory.movement` được giữ qua các turn (rolling cache) → tiết kiệm tính toán; reset khi `step==0`.

## Vai trò từng module (phân tích)

### `constants.py` — hằng số
Physics khớp engine (BOARD 100, CENTER 50, SUN_RADIUS 10, MAX_SHIP_SPEED 6, ROT_RADIUS_LIMIT 50).
tham số **early-termination** (gọi thắng sớm khi 1 người áp đảo, hiệu chỉnh trên 535 replay).
Mã hoá owner tương đối: OWN/ENEMY/NEUTRAL/DEAD. Capacity `P_MAX=64`, `F_MAX=256` là trần slot.

### `geometry.py` — toán thuần tensor
`fleet_speed(ships)` các primitive khoảng cách điểm-đoạn,
kiểm tra cắt mặt trời.

### `obs.py` — parse quan sát
`parse_obs` biến 7-field tensor thành `ParsedObs` với trường có tên: `owner_abs`, `ships`,
`alive`, `owned`, `prod`, toạ độ, `player_id`, `P` (số planet)... Đây là góc nhìn tiện dụng mọi
module dùng.

### `adapter.py` — cầu nối định dạng
Hai chiều: `single_obs_to_tensor(obs_dict)` (dict Kaggle → tensor) và
`sparse_action_row_to_moves(payload)` (payload planner → list `[from_id, angle, ships]` Kaggle yêu cầu).
Xử lý cả comet (sự kiện spawn, path).

### `movement.py`  — dự đoán tương lai 
Trái tim "Producer". `PlanetMovement`:
- Dự đoán vị trí hành tinh quay & comet ở mọi step trong horizon (giải tích quỹ đạo, không mô phỏng từng bước).
- Theo dõi fleet đang bay (in-flight), ước lượng thời điểm tới.
- `garrison_status(max_horizon=H)` chiếu **owner & số ship của từng planet qua H turn** giả định
  mình không hành động — đây là đường cơ sở để so sánh giá trị mọi nước phóng.
- `alive_by_step`: planet nào còn sống ở mỗi step.

### `movement_aiming.py` + `intercept_aim.py` — nhắm & bắn đón
`intercept_aim` giải **thời điểm chạm liên tục** `t*` (nghiệm `v·t = dist(target_pos(t), src) − gap`)
với target trên quỹ đạo giải tích → nhắm tới `target_pos(t*)`, sub-turn chính xác, và **kiểm tra
đường bay không va sun / planet khác** (swept hit mask). Đây là điểm vượt trội so với baseline cũ
khi chỉ nhắm vị trí hiện tại.

### `distance_cache.py` — cache khoảng cách chéo-thời-gian
`cross_dist[k, s, t]` = khoảng cách từ planet `s` ở step 0 tới planet `t` ở step `k`
(quãng đường fleet phải bay nếu phóng bây giờ để chặn target lúc nó tới đó). Dùng lại khắp nơi.

### `garrison_launch.py` — flow-diff "what-if I launch"
`PlanetGarrisonStatus` là sổ cái owner/ships theo horizon. `sparse_launch_flow_delta` tính
**chênh lệch dòng ship** khi mình phóng một bộ lệnh: ai chiếm được gì, đổi chủ lúc nào → cơ sở để
chấm điểm "lợi ròng".

### `movement_step.py` — ghi lệnh vào trạng thái
Sau khi chọn lệnh: gộp (`concat`), khử trùng lặp (`disambiguate`), suy lệnh dự kiến và
`apply_private_planned_launches` cập nhật movement (để turn sau biết fleet của chính mình).

### `planner_core.py` ★ — bộ não quyết định (~29 KB)
- `build_target_shortlist`: chọn mục tiêu tấn công/phòng thủ theo độ gần + giá trị.
- `safe_drain`: số ship tối đa được rút khỏi 1 source mà vẫn an toàn theo garrison_status.
- `capture_floor`: ngưỡng quân tối thiểu để chiếm tại từng turn tới (defender tăng theo k).
- `reachable_mask`: lọc cứng candidate bay không kịp (strict-superset reachability).
- `score_candidates`: **chấm điểm net-ship-delta cạnh tranh** qua flow-diff (lõi quyết định).
- `_greedy_select`: chọn tham lam đợt tốt nhất mỗi target, tối đa `max_waves_per_turn`, lọc `roi_threshold`.
- `_plan_regroup`: dồn ship dư lên "gradient áp lực địch" (`cheap_enemy_pressure`) để củng cố tiền tuyến.

## Tham số chiến lược (`ProducerLiteConfig` trong `main.py`)

| Knob | 2P | 4P (CONFIG_4P) | Ý nghĩa |
|---|---|---|---|
| `horizon` | 18 | 13 | Cửa sổ dự đoán = ETA cap |
| `max_sources_per_lane` | 12 | 6 | Số source xét/turn |
| `max_offensive_targets` | 12 | 12 | Mục tiêu tấn công |
| `max_defensive_targets` | 4 | 2 | Mục tiêu phòng thủ |
| `max_waves_per_turn` | 6 | 6 | Số đợt phóng tối đa/turn |
| `roi_threshold` | 1.5 | 1.5 | Chỉ bắn nếu score > ngưỡng |
| `min_ships_to_launch` | 4 | 4 | Source phải có ≥ ngần này |
| `enable_regroup` | true | true | Dồn ship củng cố |

→ **Đây là nơi tune để cải thiện winrate** (xem `docs/strategy.md`).

## Điểm mạnh / điểm cần lưu ý

**Mạnh:** dự đoán tương lai + flow-diff chấm điểm lợi ròng (không chỉ greedy khoảng cách);
bắn đón liên tục chính xác; tách config 2P/4P; early-termination calibrated; rolling cache giảm tải.

**Lưu ý khi sửa:**
- Tốc độ: `P_MAX/F_MAX` và horizon ảnh hưởng trực tiếp thời gian/turn (giới hạn 1s). Đo trước khi tăng.
- Còn dấu vết engine batch (hằng số `B_DEFAULT`, `LIBRARY_K`) — không dùng ở runtime single-game, đừng nhầm.
- Toàn bộ là tensor; muốn đổi heuristic phải hiểu shape `[S]`, `[T]`, `[S,T]`, `[T,K]`.
- Phụ thuộc `torch`: phải có trong môi trường (Kaggle có sẵn).

```bash
python scripts/build_from_notebook.py
```
