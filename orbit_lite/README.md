# `orbit_lite` — mỗi file nghĩa là gì 

Package này là "bộ não" của bot. Mỗi file lo một việc. Dưới đây giải thích từng file theo **3 lớp**:
ý nghĩa trong trò chơi, ví dụ đời thật để dễ hình dung, và vai trò kỹ thuật.

`main.py` (ở thư mục gốc) là **tổng chỉ huy** — mỗi turn nó gọi lần lượt các module này để ra quyết
định. Ví đời thật: một vị tướng ngồi trong phòng tác chiến, dùng từng bộ phận tham mưu bên dưới.

---

## `constants.py` — Bộ luật vũ trụ
- **Trong game:** các con số bất biến của thế giới — bàn 100×100, mặt trời ở giữa bán kính 10, tốc
  độ fleet tối đa 6, ngưỡng "thắng sớm khi áp đảo".
- **Đời thật:** quyển luật của trọng tài + thông số sân bóng. Ai cũng chơi trên cùng kích thước sân,
  cùng giới hạn tốc độ.
- **Kỹ thuật:** hằng số dùng chung, phải khớp đúng engine nếu không tính toán sẽ lệch.

## `geometry.py` — Thước đo & đồng hồ bấm giờ
- **Trong game:** tính khoảng cách giữa hai điểm và **tốc độ một hạm đội** (fleet to bay nhanh hơn),
  kiểm tra đường bay có đâm mặt trời không.
- **Đời thật:** cây thước + đồng hồ bấm giờ. "Đi từ nhà tới trường 2km, đi bộ mất bao lâu?"
- **Kỹ thuật:** hàm tensor thuần, không dính trạng thái game → tái dùng khắp nơi.

## `aiming.py` — Đọc mặt đồng hồ
- **Trong game:** các hành tinh phía trong **quay quanh mặt trời như kim đồng hồ**. File này đổi số
  thứ tự turn thành "kim đang chỉ góc nào" để biết hành tinh đang ở đâu trên vòng quay.
- **Đời thật:** nhìn đồng hồ kim để biết bây giờ là mấy giờ, từ đó suy ra kim phút sẽ ở đâu lát nữa.
- **Kỹ thuật:** đổi `step` quan sát → chỉ số pha quỹ đạo của engine.

## `obs.py` — Trinh sát đọc bản đồ
- **Trong game:** nhận "ảnh chụp" thô của chiến trường và dán nhãn rõ ràng: đâu là **quân ta**, đâu là
  **quân địch**, đâu là **đất trống**, mỗi nơi bao nhiêu tàu, sản xuất bao nhiêu.
- **Đời thật:** lính trinh sát nhìn ảnh vệ tinh rồi chú thích lên bản đồ cho chỉ huy dễ đọc.
- **Kỹ thuật:** `parse_obs` biến 7-field tensor thô thành `ParsedObs` có trường tên.

## `adapter.py` — Thông dịch viên
- **Trong game:** dịch hai chiều giữa "ngôn ngữ Kaggle" (dict observation, list lệnh) và "ngôn ngữ
  nội bộ" (tensor). Nhận đề bài vào, và viết câu trả lời (lệnh phóng tàu) ra đúng khuôn Kaggle hiểu.
- **Đời thật:** phiên dịch viên giữa hai bên không cùng tiếng nói, kiêm người đánh máy biên bản.
- **Kỹ thuật:** `single_obs_to_tensor` (vào) và `sparse_action_row_to_moves` (ra); xử lý cả comet.

## `movement.py` ★ — Nhà tiên tri (file lớn nhất)
- **Trong game:** **dự đoán tương lai**. Hành tinh quay sẽ trôi tới đâu, comet bay hướng nào, và
  "**nếu mình ngồi yên không làm gì** thì vài turn tới ai chiếm được gì, mỗi nơi còn bao nhiêu tàu".
  Đây là bức tranh nền để so sánh: làm việc X có tốt hơn ngồi yên không.
- **Đời thật:** kỳ thủ cờ tướng tính trước nhiều nước, hoặc nhà khí tượng dự báo "không can thiệp thì
  10 phút nữa trời thế nào".
- **Kỹ thuật:** lớp `PlanetMovement`, hàm `garrison_status(H)` chiếu owner/ships qua horizon;
  `alive_by_step`. Dự đoán bằng **giải tích quỹ đạo**, không mô phỏng từng bước → nhanh.

## `movement_aiming.py` — Pháo thủ ngắm sơ bộ
- **Trong game:** với một cặp (xuất phát, mục tiêu, cỡ hạm đội) cụ thể, tính cần bắn **góc nào, mất
  mấy turn**, và loại bỏ phát nào có đường bay bị mặt trời/hành tinh khác chắn.
- **Đời thật:** pháo thủ ngắm thô về phía mục tiêu rồi gạch bỏ những phát bị quả đồi che mất.
- **Kỹ thuật:** module nhỏ, dùng vị trí planet đã cache; hỗ trợ cho `intercept_aim`.

## `intercept_aim.py` — Thợ săn bắn đón
- **Trong game:** mục tiêu đang **di chuyển** (hành tinh quay), nên phải bắn vào chỗ nó **sẽ tới**,
  không phải chỗ nó đang đứng. File này giải chính xác thời điểm chạm dưới mức 1 turn rồi nhắm đón.
- **Đời thật:** thủ môn đoán đường sút, hay thợ săn ngắm trước đầu con vịt đang bay. Bắn vào "hiện
  tại" thì luôn trượt.
- **Kỹ thuật:** `intercept_angle` giải nghiệm `v·t = dist(target_pos(t), src) − gap`; có kiểm tra
  va chạm đường bay. Đây là điểm mạnh so với bot chỉ nhắm vị trí hiện tại.

## `distance_cache.py` — Bảng tra khoảng cách
- **Trong game:** dựng sẵn bảng "từ hành tinh A bây giờ, bay tới chỗ hành tinh B sẽ ở turn k thì xa
  bao nhiêu", để khỏi tính đi tính lại mỗi lần cân nhắc.
- **Đời thật:** bảng khoảng cách giữa các thành phố dán sẵn trên tường — tra một phát ra ngay.
- **Kỹ thuật:** `cross_dist[k, s, t]`; `build_distance_cache`, `min_distance_to_targets`.

## `garrison_launch.py` — Chơi thử nước cờ trong đầu
- **Trong game:** mô phỏng "**nếu tôi gửi nhóm lệnh phóng này** thì dòng tàu thay đổi ra sao — chiếm
  được gì, nơi nào đổi chủ, lúc nào". Cho biết **lợi/hại ròng** trước khi thực sự bấm nút.
- **Đời thật:** bảng tính what-if trước khi đầu tư, hay đánh thử nước cờ trong đầu rồi mới đặt quân.
- **Kỹ thuật:** `sparse_launch_flow_delta` trên `PlanetGarrisonStatus`; `GarrisonFlowDiff`, `LaunchSet`.

## `movement_step.py` — Thư ký ghi lệnh hành quân
- **Trong game:** sau khi đã chọn, **ghi các lệnh phóng vào kế hoạch**, gộp/dọn lệnh trùng, và cập
  nhật bức tranh tương lai để turn sau bot nhớ chính hạm đội mình vừa gửi.
- **Đời thật:** thư ký phòng tác chiến chép lệnh vào nhật ký, gộp các lệnh trùng cho gọn.
- **Kỹ thuật:** `concat_launch_entries`, `disambiguate_duplicate_launches`,
  `infer_planned_launches_from_entries`, `apply_private_planned_launches`, `ensure_planet_movement`.

## `planner_core.py` ★ — Bộ chỉ huy ra quyết định
- **Trong game:** trái tim chiến thuật. Chọn **đánh đâu** (mục tiêu), **lấy quân từ đâu** mà vẫn an
  toàn, **cần tối thiểu bao nhiêu tàu** để chiếm, loại nước bay không kịp, **chấm điểm lợi ròng** từng
  nước, rồi chọn các đợt tốt nhất; quân thừa thì **dồn về tuyến đang bị ép** để củng cố.
- **Đời thật:** vị tướng kiêm giám đốc đầu tư — cân nhắc "nước này lời bao nhiêu, có đáng không" rồi
  mới hạ lệnh; không rải quân bừa.
- **Kỹ thuật:** `build_target_shortlist`, `safe_drain`, `capture_floor`, `reachable_mask`,
  `score_candidates` (chấm net-ship-delta qua flow-diff), `_greedy_select`, `_plan_regroup`.

---

## Tóm tắt một câu mỗi file

| File | Một câu |
|---|---|
| `constants.py` | Bộ luật & thông số sân chơi |
| `geometry.py` | Thước đo khoảng cách + tốc độ hạm đội |
| `aiming.py` | Đọc "kim đồng hồ" của hành tinh quay |
| `obs.py` | Trinh sát dán nhãn bản đồ |
| `adapter.py` | Thông dịch giữa Kaggle ↔ nội bộ |
| `movement.py` ★ | Nhà tiên tri: dự đoán tương lai nếu ngồi yên |
| `movement_aiming.py` | Ngắm sơ bộ, loại phát bị chắn |
| `intercept_aim.py` | Bắn đón mục tiêu đang bay |
| `distance_cache.py` | Bảng tra khoảng cách dựng sẵn |
| `garrison_launch.py` | Chơi thử nước cờ: nếu gửi quân thì sao |
| `movement_step.py` | Thư ký ghi & dọn lệnh hành quân |
| `planner_core.py` ★ | Bộ chỉ huy: chọn đánh đâu, bao nhiêu, đáng không |

> Bản phân tích kỹ thuật sâu hơn (shape tensor, luồng một turn): xem [`../docs/architecture.md`](../docs/architecture.md).
> Các nút điều chỉnh hành vi để tăng winrate nằm ở `ProducerLiteConfig` trong `../main.py`.
