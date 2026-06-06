# Thư mục `scripts/`

Chứa các script tiện ích để **chạy, đóng gói và nộp bot** 
Các file ở đây KHÔNG đưa vào archive submit.

## Các file

### `submit.sh` — đóng gói & nộp lên Kaggle
Gom `main.py` + thư mục `orbit_lite/` thành `submission.tar.gz` (loại `__pycache__`, main.py ở
top level) rồi gọi `kaggle competitions submit`.

### `run_local.sh` — kiểm tra nhanh trước khi nộp
Chạy `tests/smoke_test.py` (import + 1 turn) rồi `tests/test_local.py` (đấu vs random, in winrate).

```bash
bash scripts/run_local.sh 5     # 5 ván vs random
```

Yêu cầu: torch + kaggle-environments (xem `requirements.txt`).


## Lưu ý

- File `.sh` viết cho bash. Trên Windows chạy qua Git Bash / WSL, hoặc gõ tay các lệnh bên trong.
- So sánh bản tối ưu vs `CODE_BASE/`: xem hướng dẫn trong `CODE_BASE/README.md`
  (chưa có sẵn script — có thể thêm `scripts/compare.py` ).
