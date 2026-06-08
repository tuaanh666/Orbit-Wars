#!/usr/bin/env bash
# Bundle main.py + orbit_lite/ rồi submit lên Kaggle.
# Dùng: bash scripts/submit.sh "mô tả phiên bản"
set -e
cd "$(dirname "$0")/.."

MSG="${1:-orbit-lite producer agent}"
COMP="orbit-wars"

echo "Đóng gói submission.tar.gz (main.py + orbit_lite, main.py ở top level)..."
# Loại __pycache__ để gói gọn
find orbit_lite -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
tar -czf submission.tar.gz main.py orbit_lite

echo "Nội dung archive:"
tar -tzf submission.tar.gz | head -20

echo "Submit lên $COMP ..."
kaggle competitions submit "$COMP" -f submission.tar.gz -m "$MSG"

echo "Xong. Kiểm tra: kaggle competitions submissions $COMP"
