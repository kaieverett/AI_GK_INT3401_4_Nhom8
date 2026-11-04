#!/usr/bin/env python3
"""
File: main.py
Mô tả: Điểm khởi chạy chính (Entry Point) của chương trình Cờ Caro 9x9 - Trí Tuệ Nhân Tạo.
       Học phần: Trí tuệ nhân tạo | Mã lớp: INT3401 4 | Nhóm 8

Cách sử dụng (trên Windows dùng `python`, trên Linux/macOS dùng `python3`):
    python main.py             # Chạy giao diện đồ họa (Tkinter GUI - Mặc định)
    python main.py --cli       # Chạy giao diện dòng lệnh (CLI)
    python main.py --exp       # Chạy lại toàn bộ thực nghiệm và xuất bảng CSV/JSON
    python main.py --plot      # Vẽ lại toàn bộ 5 đồ thị PNG từ dữ liệu thực nghiệm
"""

import argparse
import os
import sys

# Đảm bảo luôn import đúng các package nội bộ dù chạy từ bất kỳ thư mục làm việc nào
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chương trình Cờ Caro 9x9 - MiniMax Alpha-Beta & MCTS UCT (Nhóm 8 - INT3401 4)"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Chạy chương trình ở chế độ dòng lệnh (Command Line Interface)",
    )
    parser.add_argument(
        "--exp",
        action="store_true",
        help="Chạy tự động toàn bộ bộ kịch bản thực nghiệm (20 ván/cấu hình) và xuất CSV/JSON",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Vẽ lại toàn bộ 5 đồ thị phân tích PNG (300 DPI) vào thư mục results/charts/",
    )
    args = parser.parse_args()

    if args.exp:
        from experiments.run_experiments import run_all_experiments
        run_all_experiments()
        return

    if args.plot:
        from experiments.plot_charts import generate_all_charts
        generate_all_charts()
        return

    if args.cli:
        from ui.cli import run_cli
        run_cli()
        return

    # Mặc định khởi chạy giao diện đồ họa (GUI), tự động chuyển sang CLI nếu máy không có màn hình (Headless)
    try:
        from ui.gui import run_gui
        run_gui()
    except Exception as exc:
        print(f"[!] Không thể khởi tạo giao diện đồ họa ({exc}). Chuyển sang giao diện dòng lệnh CLI...")
        from ui.cli import run_cli
        run_cli()


if __name__ == "__main__":
    main()
