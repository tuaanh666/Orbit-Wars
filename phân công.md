# Kế hoạch phân công — Orbit Wars (nhóm 3 người · sprint 3 ngày)

> **Deadline nhóm: tối Thứ Ba 09/06/2026** (hôm nay 06/06 — còn 3 ngày).
> Chia theo **vai trò + vùng code sở hữu** để mỗi người commit phần của mình
> Thay `TV2`, `TV3` bằng tên thật.

## 1. ĐIỀU CẦN LÀM

1. **Chạy được** local (cài torch + kaggle-env) và **nộp thành công** (qua Validation Episode).
2. **Đo baseline** (bản tối ưu vs `CODE_BASE`) để có số liệu cho báo cáo.
3. **Tune nhẹ** vài config nếu kịp (không bắt buộc).
4. **Hoàn thiện tài liệu + báo cáo** giao nộp.

## 2. Vai trò & vùng sở hữu

| Người | Vai trò | Sở hữu chính (code) | Trách nhiệm 3 ngày |
|---|---|---|---|
| **Tuan Ank (TV1)** | Lead · Tích hợp & Submission | `main.py`, `planner_core.py`, `garrison_launch.py`, `movement_step.py`, `adapter.py`, `constants.py`, `scripts/`, `notebooks/` | Dựng git, gói & nộp Kaggle, tune config, merge PR, chốt bản nộp |
| **TV2** | Chiến thuật · Thuật toán | `movement.py`, `movement_aiming.py`, `intercept_aim.py`, `distance_cache.py`, `geometry.py`, `aiming.py`, `obs.py` | Hiểu + viết giải thích thuật toán dự đoán/bắn đón, kiểm tra không vượt timeout |
| **TV3** | QA · Thực nghiệm & Báo cáo | `tests/`, `CODE_BASE/`, `replays/`, `docs/` | Self-play đo winrate, phân tích replay, viết báo cáo nộp |

## 3. Phân công commit theo file (ai sửa file nào)

| File / thư mục | Commit chính | Review |
|---|---|---|
| `main.py`, `constants.py` (dùng chung) | TV1 | TV2/TV3 qua PR |
| `planner_core.py`, `garrison_launch.py`, `movement_step.py`, `adapter.py` | TV1 | TV3 |
| `movement.py`, `intercept_aim.py`, `movement_aiming.py` | TV2 | TV1 |
| `distance_cache.py`, `geometry.py`, `aiming.py`, `obs.py` | TV2 | — |
| `tests/`, `CODE_BASE/` | TV3 | — |
| `docs/` (mỗi người viết phần của mình) | TV3 tổng hợp | tác giả từng phần |
| `scripts/`, `notebooks/` | TV1 | — |

**Tránh xung đột:** `main.py` + `constants.py` chỉ TV1 commit thẳng; người khác đổi thì mở PR.
Mỗi người 1 branch riêng (`feat/<tên>-<việc>`), merge vào `main` qua PR có ≥1 review.

## 4. Lịch 3 ngày (06 → 09/06)

### Ngày 1 — Thứ 7 06/06: Dựng nền & chạy được
| Người | Việc | Commit |
|---|---|---|
| TV1 | `git init` + push repo, cài `requirements.txt`, chạy `tests/smoke_test.py` PASS, gói thử `submission.tar.gz` | repo + scripts |
| TV2 | Cài torch, đọc `movement.py` + `intercept_aim.py`, viết note ngắn cách dự đoán/bắn đón | `docs/` phần thuật toán |
| TV3 | Viết `scripts/compare.py` (self-play tối ưu vs `CODE_BASE`), chạy thử 5–10 ván | `scripts/compare.py` |

### Ngày 2 — Chủ nhật 07–08/06: Đo & tune nhẹ + nộp thử
| Người | Việc | Commit |
|---|---|---|
| TV1 | Nộp bản đầu lên Kaggle (qua Validation), thử 1–2 giá trị `horizon`/`roi_threshold`, ghi kết quả | `main.py` (config) |
| TV2 | Kiểm tra thời gian/turn (không vượt 1s), xác nhận an toàn timeout; góp ý heuristic nếu thấy | note `docs/` |
| TV3 | Chạy self-play nhiều seed, lập **bảng winrate** bản tối ưu vs baseline, soi 1–2 replay thua | `docs/` bảng số liệu |

### Ngày 3 — Thứ 2→tối Thứ 3 08–09/06: Chốt & báo cáo
| Người | Việc | Commit |
|---|---|---|
| TV1 | Chọn bản nộp cuối, gói `submission.tar.gz`, kiểm tra `smoke_test` PASS, tag commit | bản chốt |
| TV2 | Rà lại phần giải thích thuật toán trong `docs/architecture.md` + `orbit_lite/README.md` | `docs/` |
| TV3 | Viết **báo cáo tổng kết** (phương pháp, kiến trúc, bảng winrate, kết luận), kiểm tra repo sạch | `docs/bao-cao.md` |

> Tối 09/06: cả nhóm rà soát lần cuối — repo chạy được, README đầy đủ, báo cáo xong, đã nộp.

## 5. Quy ước Git nhanh
- Branch: `feat/<tên>-<việc>` · Commit: `<scope>: <mô tả>` (vd `movement: note dự đoán comet`).
- `main` luôn chạy được: trước khi merge chạy `python tests/smoke_test.py`.
- Chỉ TV1 nộp Kaggle; ghi commit hash vào mô tả submission. Tối đa 5 submission/ngày.

## 6. Rủi ro cần canh 
- **Phân công tài liệu:** mỗi người viết phần module mình phụ trách, TV3 ghép — tránh dồn 1 người.
