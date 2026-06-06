# Orbit Wars — Phân tích chiến lược

> Ghi chú chiến lược sống. Cập nhật dần khi test/đấu.
> flow-diff scoring, bắn đón liên tục, phòng thủ/regroup. Xem `docs/architecture.md`.
> → Hướng cải tiến giờ chuyển từ "viết từ đầu" sang **tune config + nâng heuristic**
> trong `orbit_lite` (mục 4 & các knob trong `ProducerLiteConfig`). Các phương án
> B/C/D dưới đây phần lớn ĐÃ có trong orbit_lite; giữ lại làm khung tư duy.
>
> **Hướng tune ưu tiên:** (1) đo thời gian/turn để biết trần `horizon`; (2) sweep
> `roi_threshold`, `max_waves_per_turn`, `horizon` qua self-play nhiều seed;
> (3) tinh chỉnh shortlist size 2P vs 4P; (4) cải thiện `score_candidates` /
> `cheap_enemy_pressure` nếu thấy điểm yếu trong replay.

## 1. Nguyên tắc thắng 

- Rating chỉ phụ thuộc **thắng/thua/hoà**, không phụ thuộc score gap → mục tiêu là **tối đa xác suất kết thúc dẫn đầu**, không cần thắng đậm. Tránh rủi ro cao khi đang dẫn.
- Thắng = nhiều ship nhất ở turn 500. Hai đòn bẩy: **production** (chiếm hành tinh production cao) và **bảo toàn ship** (không phí fleet vào combat thua).
- Production cộng dồn theo cấp số nhân theo thời gian → **chiếm sớm các hành tinh production cao** đáng giá hơn nhiều so với chiếm muộn. Một hành tinh production 5 chiếm ở turn 50 sinh ~2250 ship đến cuối game.

## 2. Các quyết định ảnh hưởng kết quả (theo mức ưu tiên)

1. **Chọn mục tiêu mở màn:** từ home, hành tinh production cao + garrison thấp + gần nhất là mục tiêu vàng. Tối đa hoá `production / (ships_needed + distance_cost)`.
2. **Đúng liều quân (ship economy):** gửi vừa đủ `garrison + 1 + production*ETA` (vì hành tinh trung lập KHÔNG sinh ship, nhưng hành tinh địch CÓ → phải tính production tích thêm trong thời gian bay). Gửi thừa = phí; gửi thiếu = mất trắng fleet.
3. **Intercept hành tinh quay & comet:** phải bắn đón (lead target), không bắn vào vị trí hiện tại. Đây là kỹ năng phân biệt bot tốt/dở.
4. **Phòng thủ:** phát hiện fleet địch đang tới, tính ETA, giữ đủ garrison hoặc tiếp viện kịp.
5. **Phân bổ toàn cục:** không dồn hết vào 1 mặt trận; cân bằng mở rộng vs thủ.

## 3. Toán học then chốt

### 3.1 Liều quân để chiếm

- Hành tinh **trung lập** (không sinh ship): cần `garrison + 1`.
- Hành tinh **địch** (sinh `prod`/turn): cần `garrison + prod * ETA + 1`, với `ETA = ceil(distance / fleet_speed)`.
- Vì `fleet_speed` phụ thuộc số ship → ETA và liều quân **phụ thuộc lẫn nhau**. Giải lặp: đoán ships → tính speed → tính ETA → tính lại ships needed → lặp tới hội tụ (2–3 vòng đủ).

### 3.2 Bắn đón hành tinh quay (lead intercept)

Hành tinh quay theo góc quanh tâm `(50,50)` với `angular_velocity ω`. Vị trí tại turn `t`:
```
θ(t) = θ0 + ω * t
pos(t) = center + R * (cos θ(t), sin θ(t))
```
Tìm `t` nhỏ nhất sao cho khoảng cách fleet bay được trong `t` turn ≥ khoảng cách tới `pos(t)`. Vì speed phụ thuộc ships, giải lặp hoặc quét `t` tăng dần (đơn giản, robust). Góc phóng = `atan2(pos(t).y - src.y, pos(t).x - src.x)`.

### 3.3 Tránh mặt trời

Đoạn thẳng src→target có thể cắt mặt trời (tâm 50,50 r=10). Kiểm tra khoảng cách điểm-đoạn tới tâm. Nếu cắt → fleet chết. Giải pháp: phóng theo **đường vòng** (chọn waypoint lệch sang một bên) hoặc bỏ mục tiêu đó. Cần hàm `segment_hits_sun(a, b)`.

## 4. Khung chiến lược đề xuất (ưu tiên cao → thấp)

### Phương án A — Greedy Expansion (baseline, làm trước)
- Mỗi turn, với mỗi hành tinh mình có ship dư, chọn mục tiêu tốt nhất theo `score = production / (ships_needed * distance)`.
- Gửi vừa đủ + buffer nhỏ. Né mặt trời.
- **Ưu:** đơn giản, ổn định, đánh bại random/sniper. **Nhược:** không phòng thủ, không bắn đón tốt, dễ bị bot mạnh phản công.

### Phương án B — Value-based Target Allocation
- Tính "giá trị" mỗi hành tinh = NPV production tới cuối game (`prod * (500 - turn)`).
- Bài toán phân bổ: gán fleet → mục tiêu tối đa hoá tổng giá trị chiếm được / chi phí. Greedy theo tỉ lệ value/cost, hoặc Hungarian nếu cần.
- Thêm **lead intercept** cho hành tinh quay + comet.
- **Ưu:** quyết định kinh tế tốt hơn hẳn A. **Nhược:** phức tạp hơn, cần tune.

### Phương án C — Threat-aware + Defense
- Mô phỏng các fleet địch đang bay: dự đoán hành tinh nào bị đe doạ và turn nào.
- Giữ garrison phòng thủ động; tiếp viện hành tinh sắp mất nếu cứu được, bỏ nếu không.
- Kết hợp B (tấn công) + C (thủ) = bot cạnh tranh top.
- **Ưu:** mạnh, ít mất hành tinh oan. **Nhược:** tốn tính toán, phải cẩn thận timeout 1s/turn.

### Phương án D — Lookahead / Simulation (nâng cao)
- Mô phỏng vài turn tới với forward model (đã biết đủ luật để viết). Đánh giá vài bộ action, chọn tốt nhất.
- Có thể giới hạn: chỉ simulate kết cục các cuộc combat đang diễn ra.
- **Ưu:** trần sức mạnh cao nhất. **Nhược:** rủi ro timeout, ROI giảm dần. Làm sau cùng nếu còn thời gian.

## 5. Khai thác mẹo cụ thể

- **Đối xứng:** ở game 2 người, vị trí/khởi đầu địch suy ra qua đối xứng chéo → dự đoán nước đi sớm.
- **Fleet lớn nhanh hơn:** gộp fleet khi cần tới đích nhanh (chặn/ cứu). Tách nhỏ khi chỉ cần chiếm nhiều mục tiêu yếu.
- **Production trước movement:** khi chiếm hành tinh địch, nó sinh thêm 1 lượt ship ngay turn đó → cộng vào liều quân.
- **Comet:** ship khởi đầu lệch thấp + production 1 → mục tiêu rẻ nhưng giá trị thấp & biến mất. Chỉ chiếm nếu tiện đường và còn ở lại đủ lâu. Đừng đầu tư nặng.
- **Combat 3 bên:** để 2 địch đánh nhau, vào nhặt xác (third-party) khi cả hai đã hao quân.
- **Endgame:** khi gần turn 500, dừng các fleet "đầu tư dài hạn" không kịp về điểm; giữ ship tại chỗ vì ship trong fleet vẫn tính điểm nhưng fleet bay ra biên/sun thì mất.

## 6. Rủi ro kỹ thuật

- **Timeout 1s/turn** + `remainingOverageTime`. Phải đo thời gian, có fallback nhanh nếu sắp hết giờ.
- **Edge cases:** không có mục tiêu, không đủ ship, mọi đường đều cắt sun, fleet đối thủ tie, hành tinh quay ra mép.
- **Số học liên đới ships↔speed↔ETA**: luôn cap vòng lặp để không treo.

## 7. Lộ trình triển khai

1. [ ] Baseline A chạy được, đánh bại `random` + sniper local. ← làm ngay
2. [ ] Thêm intercept hành tinh quay + né sun (đã có skeleton trong `src/bot/geometry.py`).
3. [ ] Nâng lên B (value allocation) + liều quân lặp.
4. [ ] Thêm C (phòng thủ threat-aware).
5. [ ] (tuỳ thời gian) D lookahead.
6. [ ] Harness self-play để so sánh phiên bản trước khi submit.

