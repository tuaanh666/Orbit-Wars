# Orbit Wars 

## Giới thiệu

Dự án này phát triển một tác tử trí tuệ nhân tạo (AI Agent) cho cuộc thi **Orbit Wars** trên Kaggle. Orbit Wars là một trò chơi chiến lược nhiều tác nhân (multi-agent strategy game) lấy cảm hứng từ Planet Wars, nơi người chơi điều khiển các hạm đội tàu vũ trụ để mở rộng lãnh thổ, khai thác tài nguyên và chinh phục các hành tinh trên bản đồ.

Mục tiêu của dự án là xây dựng một tác tử có khả năng đưa ra quyết định chiến lược hiệu quả trong môi trường động, nơi các hành tinh có thể quay quanh Mặt Trời, sao chổi xuất hiện theo chu kỳ và các hạm đội liên tục di chuyển, giao tranh.

---

## Mục tiêu dự án

* Xây dựng bot có khả năng cạnh tranh trên bảng xếp hạng Orbit Wars.
* Tối ưu chiến lược mở rộng lãnh thổ từ giai đoạn đầu trận.
* Dự đoán vị trí tương lai của các hành tinh quay và sao chổi.
* Quản lý tài nguyên và phân phối hạm đội hiệu quả.
* Cân bằng giữa tấn công, phòng thủ và phát triển kinh tế.
* Thích nghi với nhiều chiến thuật đối thủ khác nhau.

---

## Môi trường trò chơi

Trong Orbit Wars, mỗi người chơi bắt đầu với một hành tinh quê hương và phải mở rộng quyền kiểm soát bằng cách gửi các hạm đội đến:

* Hành tinh trung lập.
* Hành tinh của đối thủ.
* Sao chổi xuất hiện tạm thời.

Mỗi hành tinh sở hữu:

* Số lượng tàu hiện có.
* Tốc độ sản xuất tàu.
* Kích thước và vị trí trên bản đồ.

Trò chơi diễn ra tối đa 500 lượt. Người chiến thắng là người sở hữu tổng số tàu lớn nhất (bao gồm tàu trên hành tinh và tàu đang di chuyển).

---

## Các thành phần chính

### 1. Đánh giá kinh tế

Bot đánh giá giá trị của từng hành tinh dựa trên:

* Tốc độ sản xuất.
* Khoảng cách di chuyển.
* Chi phí chiếm đóng.
* Lợi nhuận dài hạn sau khi kiểm soát.

Mục tiêu là ưu tiên các hành tinh mang lại hiệu quả kinh tế cao nhất.

---

### 2. Dự đoán quỹ đạo

Một số hành tinh trong trò chơi quay quanh Mặt Trời với vận tốc góc cố định.

Bot sử dụng:

* Vị trí ban đầu của hành tinh.
* Vận tốc góc được cung cấp bởi môi trường.

để dự đoán vị trí của hành tinh trong tương lai và tính toán hướng phóng hạm đội chính xác.

---

### 3. Quản lý hạm đội

Bot thực hiện:

* Tính toán số tàu cần thiết để chiếm mục tiêu.
* Tránh gửi quá nhiều tàu gây lãng phí tài nguyên.
* Tận dụng cơ chế tàu lớn di chuyển nhanh hơn.
* Phối hợp nhiều đợt tấn công từ các hành tinh khác nhau.

---

### 4. Đánh giá mối đe dọa

Bot theo dõi:

* Các hạm đội đối phương đang tiến tới.
* Nguy cơ mất hành tinh trong tương lai.
* Các khu vực trọng yếu cần tăng viện.

Từ đó đưa ra các quyết định phòng thủ phù hợp.

---

### 5. Khai thác sao chổi

Sao chổi là các hành tinh tạm thời xuất hiện trên bản đồ.

Bot đánh giá:

* Thời gian tồn tại còn lại.
* Chi phí chiếm đóng.
* Lợi ích sản xuất mang lại.

Chỉ thực hiện chiếm đóng khi lợi ích kỳ vọng lớn hơn chi phí đầu tư.

---

## Kiến trúc hệ thống

```text
Quan sát trạng thái trò chơi
                │
                ▼
      Phân tích bản đồ
                │
                ▼
     Đánh giá kinh tế
                │
                ▼
      Phân tích rủi ro
                │
                ▼
      Chọn mục tiêu
                │
                ▼
      Lập kế hoạch đội tàu
                │
                ▼
        Sinh hành động
```

Bot liên tục cập nhật trạng thái môi trường và tạo ra danh sách hành động theo định dạng:

```python
[from_planet_id, direction_angle, num_ships]
```

---

## Công nghệ sử dụng

* Python
* Kaggle Environments
* NumPy
* Thuật toán tìm kiếm heuristic
* Mô phỏng tương lai (Forward Simulation)
* Chiến lược ra quyết định đa tác nhân

---

## Hướng phát triển

Các hướng nâng cấp trong tương lai bao gồm:

* Monte Carlo Tree Search (MCTS)
* Opponent Modeling
* Influence Maps
* Reinforcement Learning
* Deep Reinforcement Learning
* Evolutionary Algorithms
* Neural Network Value Function

---

## Kết quả kỳ vọng

Dự án hướng tới việc xây dựng một tác tử có khả năng:

* Mở rộng lãnh thổ hiệu quả.
* Duy trì lợi thế kinh tế lâu dài.
* Đối phó với nhiều loại đối thủ khác nhau.
* Đạt thứ hạng cao trên bảng xếp hạng Orbit Wars của Kaggle.
