# Kiến trúc agent `orbit_lite`

## Bản đồ thư mục

```
main.py                      # Entry point Kaggle + vòng lặp turn
orbit_lite/
├── __init__.py              # Package declaration
├── constants.py             # Hằng số physics + cấu hình agent
├── geometry.py              # Hàm tensor thuần: tốc độ fleet, khoảng cách, va chạm mặt trời
├── obs.py                   # parse_obs: raw tensor -> ParsedObs trường có tên
├── adapter.py               # dict Kaggle <-> tensor; payload sparse -> move list
├── movement.py              # Dự đoán vị trí hành tinh/comet + garrison projection
├── movement_aiming.py       # Aim/hit helper dùng cache vị trí
├── intercept_aiming.py      # Bắn đón liên tục và kiểm tra first-contact thực tế
├── distance_cache.py        # Cache khoảng cách cross-time [k, s, t]
├── garrison_launch.py       # What-if launch flow diff + net-ship-delta
├── movement_step.py         # Gộp lệnh, khử trùng lặp, infer/apply planned launches
├── planner_core.py          # Bộ não: shortlist, score, greedy select, regroup
└── README.md                # Giải thích module cho người đọc

docs/
├── Architecture.md          # Tài liệu kiến trúc mới
└── rule.md                  # Luật chơi Orbit Wars
```

## Luồng một turn

```
agent(obs)
 └─ single_obs_to_tensor(obs_dict)
     └─ ProducerLiteRuntime.tensor_action
         └─ run_turn(obs_tensors, config, player_count, memory)
             1. parse_obs                  # raw tensor -> ParsedObs
             2. ensure_planet_movement     # dựng/cập nhật PlanetMovement cache
             3. build_distance_cache       # cross_dist[k,s,t] tới horizon
             4. movement.garrison_status   # chiếu owner/ships nếu không hành động
             5. plan_lite_waves            # sinh + chấm + chọn đợt phóng
             6. disambiguate / infer / apply_private_planned_launches
             7. entries_to_sparse_payload  # planner -> payload Kaggle
 └─ sparse_action_row_to_moves             # payload -> [[from_id, angle, ships], ...]
```

`memory.movement` được giữ qua các turn như rolling cache để tiết kiệm tính toán;
reset khi `step == 0`.

## Vai trò từng module

### `main.py` — điều phối chính

- Định nghĩa `ProducerLiteConfig` với tham số chiến lược.
- Khởi tạo hoặc cập nhật `PlanetMovement` qua `ensure_planet_movement`.
- Tạo `DistanceCache`, `garrison_status`, `alive_by_step`.
- Gọi `plan_lite_waves` để chọn lệnh.
- Dọn lệnh trùng, infer kế hoạch tương lai, cập nhật movement và xuất payload.

### `constants.py` — hằng số trò chơi và cấu hình

- Thông số thế giới: `BOARD_SIZE`, `CENTER`, `SUN_RADIUS`, `MAX_SHIP_SPEED`.
- Giới hạn tensor: `P_MAX`, `F_MAX`.
- Cấu hình agent: ngưỡng launch, horizon, regroup, early-termination.

### `geometry.py` — toán thuần tensor

- `fleet_speed(ships)` tính tốc độ di chuyển thực tế của fleet.
- Khoảng cách giữa điểm và đoạn, kiểm tra cắt mặt trời.
- Không chứa logic trạng thái game; chỉ phục vụ tính toán số học.

### `obs.py` — parse observation

- `parse_obs` biến raw tensor 7-field thành `ParsedObs` có trường tên.
- Tách ownership, alive, enemy/neutral, orbit parameters từ `initial_planets`.
- Cung cấp mặt nạ `owned`, `is_enemy`, `is_neutral` và thông tin orbit.

### `adapter.py` — cầu nối Kaggle ↔ nội bộ

- `single_obs_to_tensor`: chuyển observation dict Kaggle sang tensor chuẩn.
- `sparse_action_row_to_moves`: chuyển payload planner thành list move Kaggle.
- Xử lý cả comet, `player_count`, `next_fleet_id`, `episode_steps`.

### `movement.py` — dự đoán tương lai

- `PlanetMovement`: cache vị trí hành tinh/comet qua horizon.
- Dự đoán `x`, `y`, `alive_by_step`, `planet_prod`, `owner`, `ships`.
- `garrison_status(max_horizon=H)`: chiếu owner/ship mỗi planet nếu không hành động.
- Hỗ trợ fleet tracking để tương tác chính xác với các launch đã gửi.

### `distance_cache.py` — cache khoảng cách cross-time

- `DistanceCache.cross_dist[k, s, t] = dist(s@0, t@k)`.
- `build_distance_cache` xây dựng bảng cross-time dùng lại khắp planner.
- `min_distance_to_targets` lấy khoảng cách nhỏ nhất từ source tới target qua bước.

### `movement_aiming.py` — helper nhắm và hit

- Giải quyết vị trí launch/hit với offset bề mặt.
- Cung cấp `_swept_pair_hit_mask` để kiểm tra va chạm swept-pair.
- Dùng bởi `intercept_aiming` để sàng lọc đường bay hợp lệ.

### `intercept_aiming.py` — bắn đón liên tục

- `intercept_angle` giải nghiệm intercept time liên tục cho mục tiêu quay.
- Tìm góc launch và ETA với fixed-point iteration.
- Xác thực bằng first-contact engine-faithful: planet, sun, lẫn out-of-bounds.
- Trả `angle`, `eta`, `viable`.

### `garrison_launch.py` — what-if launch và flow diff

- `LaunchSet` định nghĩa candidate launches.
- Dự đoán sản lượng và tổn thất combat theo giả định lệnh được gửi.
- `GarrisonFlowDiff` tính net ship delta cho từng người chơi.
- Cơ chế này là cơ sở chấm điểm lợi ròng khi lựa chọn target.

### `movement_step.py` — ghi lệnh và cập nhật trạng thái

- `concat_launch_entries` gộp nhiều batch lệnh.
- `disambiguate_duplicate_launches` sửa các lệnh trùng (nhỏ epsilon vào góc).
- `ensure_planet_movement` tái sử dụng hoặc rebuild `PlanetMovement`.
- `infer_planned_launches_from_entries` suy ra `PlannedLaunches` từ final entries.
- `apply_private_planned_launches` cập nhật cache fleet arrivals cho turn sau.

### `planner_core.py` — bộ não quyết định

- `build_target_shortlist`: chọn target tấn công/phòng thủ tốt nhất.
- `safe_drain`: tính quân rút khỏi source mà vẫn an toàn.
- `capture_floor`: ngưỡng ship cần thiết để chiếm target tại step k.
- `reachable_mask`: loại bỏ cặp source/target không bay kịp.
- `score_candidates`: dùng `sparse_launch_flow_delta` để đánh net-ship-delta cạnh tranh.
- `_greedy_select`: pick đợt phóng tốt nhất, tối đa `max_waves_per_turn`.
- `_plan_regroup`: dồn quân thừa về các điểm áp lực kẻ địch.

## Tham số chiến lược chính

| Knob | 2P | 4P | Ý nghĩa |
|---|---|---|---|
| `horizon` | 18 | 13 | Dự đoán window, cap ETA |
| `max_sources_per_lane` | 12 | 6 | Số source xét mỗi turn |
| `max_offensive_targets` | 12 | 12 | Target tấn công |
| `max_defensive_targets` | 4 | 2 | Target phòng thủ |
| `max_waves_per_turn` | 6 | 6 | Số đợt phóng tối đa |
| `roi_threshold` | 1.5 | 1.5 | Chỉ phóng khi score > threshold |
| `min_ships_to_launch` | 4 | 4 | Ngưỡng source khả dụng |
| `enable_regroup` | true | true | Dồn ship củng cố |

## Điểm mạnh chính

- Dự đoán tương lai bằng cache hành tinh/comet và garrison projection.
- Bắn đón chính xác với first-contact verification.
- Chấm điểm launch bằng net-ship-delta cạnh tranh, không chỉ khoảng cách.
- Rolling cache lưu trạng thái `movement` qua turn.
- Tách rõ định dạng Kaggle và nội bộ tensor.

## Lưu ý khi mở rộng

- Tốc độ chạy phụ thuộc trực tiếp vào `P_MAX`, `F_MAX`, `horizon`.
- `PlanetMovement` và `DistanceCache` là hai cấu phần tối ưu hoá lớn nhất.
- `intercept_aiming` và `garrison_launch` là nơi thay đổi chiến lược cho hiệu quả.
- Nếu sửa `adapter.py`, phải giữ định dạng đầu vào/đầu ra đúng với Kaggle.
