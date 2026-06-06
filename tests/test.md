# Thư mục `tests/`

Chứa các script **kiểm tra bot chạy đúng trước khi nộp** 
Các file ở đây KHÔNG được đưa vào archive submit (chỉ nộp `main.py` + `orbit_lite/`).

## Các file

### `smoke_test.py` — kiểm tra nhanh nhất
Import `main.agent` rồi cho chạy đúng **1 turn** với một observation giả (1 hành tinh nhà của mình
+ 1 trung lập + 1 địch). Mục đích: phát hiện sớm lỗi import / crash mà không tốn công chạy cả ván.
Pass = agent load được và trả về list move đúng định dạng `[from_planet_id, angle, num_ships]`.

```bash
python tests/smoke_test.py
```

### `test_local.py` — đấu thật, đo winrate
Dùng `kaggle-environments` cho bot đánh nhiều ván với đối thủ (mặc định `random`) và in tỉ lệ thắng.

```bash
python tests/test_local.py --games 10 --opponent random
```

## Yêu cầu môi trường

- `smoke_test.py` cần **torch**.
- `test_local.py` cần thêm **kaggle-environments** (`pip install "kaggle-environments>=1.28.0"`).

Cài tất cả: `pip install -r requirements.txt`.

## Quy trình khuyến nghị trước khi submit

1. `python tests/smoke_test.py` → chắc chắn agent không crash.
2. `python tests/test_local.py --games 10` → xem winrate cơ bản vs random.
3. Nếu ổn, đóng gói và nộp (xem `scripts/submit.sh`).

> Lưu ý: các test này được tạo lúc dựng khung dự án, cần chạy trên máy có torch
