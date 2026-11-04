"""
File: experiments/plot_charts.py
Mô tả: Đọc dữ liệu thực nghiệm từ `results/experiment_summary.json` và vẽ 05 đồ thị
       phân tích chất lượng cao (300 DPI) phục vụ Báo cáo và Slide thuyết trình:
       1. chart1_head_to_head.png         : Đối sánh Thắng - Hòa - Thua giữa các thuật toán (Bài 1.4a)
       2. chart2_c_sensitivity.png        : Khảo sát tham số c thuộc {0.5, 1.0, 1.4, 2.0} (Bài 1.4b)
       3. chart3_iter_winrate_time.png    : Khảo sát số iteration {100, 300, 500} với tỷ lệ thắng & thời gian (Bài 1.4c)
       4. chart4_alphabeta_nodes_time.png : Hiệu quả cắt tỉa Alpha-Beta vs MiniMax thuần (Bài 1.2c)
       5. chart5_bai2_heuristic_rollout.png: Cải tiến Heuristic Rollout vs Random Rollout (Bài 2 - Hướng A)
"""

import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT_DIR, "results")
CHARTS_DIR = os.path.join(RESULTS_DIR, "charts")


def save_fig_with_permissions(fig: plt.Figure, filename: str) -> str:
    os.makedirs(CHARTS_DIR, exist_ok=True)
    path = os.path.join(CHARTS_DIR, filename)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    try:
        os.chmod(path, 0o666)
    except Exception:
        pass
    print(f"  [OK] Đã xuất đồ thị: {path}")
    return path


def generate_all_charts() -> None:
    summary_path = os.path.join(RESULTS_DIR, "experiment_summary.json")
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"Không tìm thấy {summary_path}. Hãy chạy run_experiments.py trước.")

    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Liberation Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    # -------------------------------------------------------------------------
    # ĐỒ THỊ 1: Đối sánh Thắng / Hòa / Thua giữa các cặp thuật toán (Bài 1.4a)
    # -------------------------------------------------------------------------
    h2h = data["head_to_head"]
    labels = [
        "MiniMax(d=2)\nvs Random",
        "MCTS Cơ sở\nvs Random",
        "MCTS Cơ sở\nvs MiniMax(d=2)",
        "MCTS Heuristic [Bài 2]\nvs MCTS Cơ sở",
        "MCTS Heuristic [Bài 2]\nvs MiniMax(d=2)",
    ]
    win_rates = [row["win_rate_pct"] for row in h2h]
    draw_rates = [row["draw_rate_pct"] for row in h2h]
    loss_rates = [row["loss_rate_pct"] for row in h2h]

    x = np.arange(len(labels))
    width = 0.52

    fig, ax = plt.subplots(figsize=(10, 5.2))
    p1 = ax.bar(x, win_rates, width, label="Tỷ lệ Thắng (%)", color="#1a73e8")
    p2 = ax.bar(x, draw_rates, width, bottom=win_rates, label="Tỷ lệ Hòa (%)", color="#fbbc04")
    bottom_loss = [w + d for w, d in zip(win_rates, draw_rates)]
    p3 = ax.bar(x, loss_rates, width, bottom=bottom_loss, label="Tỷ lệ Thua (%)", color="#ea4335")

    ax.set_ylabel("Tỷ lệ phần trăm (%)", fontsize=11, fontweight="bold")
    ax.set_title("Đồ thị 1: Kết quả Đối sánh Trực tiếp giữa các Thuật toán (20 ván/cặp, hoán đổi tiên/hậu)", fontsize=12, fontweight="bold", pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylim(0, 115)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="upper right", frameon=True)

    for i, w in enumerate(win_rates):
        if w > 0:
            ax.text(i, w / 2, f"{w:.0f}%", ha="center", va="center", color="white", fontweight="bold", fontsize=10)
        if loss_rates[i] > 0:
            ax.text(i, bottom_loss[i] + loss_rates[i] / 2, f"{loss_rates[i]:.0f}%", ha="center", va="center", color="white", fontweight="bold", fontsize=10)

    save_fig_with_permissions(fig, "chart1_head_to_head.png")

    # -------------------------------------------------------------------------
    # ĐỒ THỊ 2: Khảo sát tham số c thuộc {0.5, 1.0, 1.4, 2.0} (Bài 1.4b)
    # -------------------------------------------------------------------------
    c_data = data["c_sensitivity"]
    c_vals = [str(row["c"]) for row in c_data]
    c_win = [row["win_rate_pct"] for row in c_data]
    c_draw = [row["draw_rate_pct"] for row in c_data]
    c_loss = [row["loss_rate_pct"] for row in c_data]

    fig, ax = plt.subplots(figsize=(8.8, 5.0))
    x_c = np.arange(len(c_vals))
    w_bar = 0.25

    b_win = ax.bar(x_c - w_bar, c_win, w_bar, label="Thắng (%)", color="#1e8e3e")
    b_draw = ax.bar(x_c, c_draw, w_bar, label="Hòa (%)", color="#f9ab00")
    b_loss = ax.bar(x_c + w_bar, c_loss, w_bar, label="Thua (%)", color="#d93025")

    ax.plot(x_c - w_bar, c_win, color="#0d652d", marker="o", linewidth=2, linestyle="--", label="Đường xu hướng Tỷ lệ thắng")

    ax.set_xlabel("Giá trị hằng số cân bằng Khai thác - Khám phá (c)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Tỷ lệ (%)", fontsize=11, fontweight="bold")
    ax.set_title("Đồ thị 2: Ảnh hưởng của tham số UCT c ∈ {0.5, 1.0, 1.4, 2.0} đến Tỷ lệ Thắng (iter = 300)", fontsize=12, fontweight="bold", pad=14)
    ax.set_xticks(x_c)
    ax.set_xticklabels([f"c = {v}" for v in c_vals], fontsize=10.5, fontweight="bold")
    ax.set_ylim(0, 105)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="upper right")

    for rect in b_win:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2.0, h + 1.5, f"{h:.0f}%", ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#1e8e3e")
    for rect in b_loss:
        h = rect.get_height()
        if h > 0:
            ax.text(rect.get_x() + rect.get_width() / 2.0, h + 1.5, f"{h:.0f}%", ha="center", va="bottom", fontsize=9.5, color="#d93025")

    save_fig_with_permissions(fig, "chart2_c_sensitivity.png")

    # -------------------------------------------------------------------------
    # ĐỒ THỊ 3: Khảo sát số iteration ∈ {100, 300, 500} (Bài 1.4c - 2 trục tung)
    # -------------------------------------------------------------------------
    it_data = data["iter_sensitivity"]
    it_vals = [str(row["iterations"]) for row in it_data]
    it_win = [row["win_rate_pct"] for row in it_data]
    it_time_ms = [row["avg_time_a_sec"] * 1000.0 for row in it_data]

    fig, ax1 = plt.subplots(figsize=(8.8, 5.0))
    x_it = np.arange(len(it_vals))

    bars = ax1.bar(x_it - 0.15, it_win, width=0.3, color="#1a73e8", alpha=0.88, label="Tỷ lệ thắng (%)")
    ax1.set_xlabel("Số lượt mô phỏng mỗi nước đi (Iterations)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Tỷ lệ Thắng (%)", color="#1a73e8", fontsize=11, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor="#1a73e8")
    ax1.set_ylim(0, 108)
    ax1.set_xticks(x_it)
    ax1.set_xticklabels([f"{v} iterations" for v in it_vals], fontsize=10.5, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    for rect in bars:
        h = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width() / 2.0, h + 1.8, f"{h:.1f}%", ha="center", va="bottom", color="#1a73e8", fontweight="bold", fontsize=10)

    ax2 = ax1.twinx()
    line = ax2.plot(x_it + 0.15, it_time_ms, color="#d93025", marker="s", markersize=8, linewidth=2.5, label="Thời gian xử lý TB/nước (ms)")
    ax2.set_ylabel("Thời gian suy luận TB / nước (ms)", color="#d93025", fontsize=11, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="#d93025")
    ax2.set_ylim(0, max(it_time_ms) * 1.30)

    for i, v in enumerate(it_time_ms):
        ax2.text(x_it[i] + 0.15, v + max(it_time_ms) * 0.04, f"{v:.1f} ms", ha="center", va="bottom", color="#d93025", fontweight="bold", fontsize=9.5)

    plt.title("Đồ thị 3: Quan hệ giữa Số Iteration {100, 300, 500}, Tỷ lệ Thắng và Thời gian Xử lý (c = 1.4)", fontsize=11.5, fontweight="bold", pad=14)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    save_fig_with_permissions(fig, "chart3_iter_winrate_time.png")

    # -------------------------------------------------------------------------
    # ĐỒ THỊ 4: Hiệu quả cắt tỉa Alpha-Beta vs MiniMax thuần (Bài 1.2c)
    # -------------------------------------------------------------------------
    ab_data = [row for row in data["alphabeta_pruning"] if row["depth"] == 3]
    preset_labels = ["Khai cuộc\n(d=3)", "Trung cuộc\n(d=3)", "Chặn chuỗi 4\n(d=3)", "Bẫy đôi 3-3\n(d=3)"]
    nodes_pure = [row["nodes_pure"] for row in ab_data]
    nodes_ab = [row["nodes_ab"] for row in ab_data]
    reductions = [row["node_reduction_pct"] for row in ab_data]

    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    x_ab = np.arange(len(preset_labels))
    w_ab = 0.34

    r1 = ax.bar(x_ab - w_ab / 2, nodes_pure, w_ab, label="MiniMax thuần (Không cắt tỉa)", color="#ea4335")
    r2 = ax.bar(x_ab + w_ab / 2, nodes_ab, w_ab, label="MiniMax + Cắt tỉa Alpha-Beta", color="#1e8e3e")

    ax.set_ylabel("Số nút đã duyệt (Nodes Visited)", fontsize=11, fontweight="bold")
    ax.set_title("Đồ thị 4: So sánh Số nút duyệt giữa MiniMax thuần và Cắt tỉa Alpha-Beta (Độ sâu d = 3)", fontsize=11.5, fontweight="bold", pad=14)
    ax.set_xticks(x_ab)
    ax.set_xticklabels(preset_labels, fontsize=10, fontweight="bold")
    ax.set_ylim(0, max(nodes_pure) * 1.32)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="upper right")

    for i, rect in enumerate(r1):
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2.0, h + 40, f"{h:,}", ha="center", va="bottom", fontsize=9.5, color="#ea4335", fontweight="bold")
    for i, rect in enumerate(r2):
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2.0, h + 40, f"{h:,}\n(-{reductions[i]:.1f}%)", ha="center", va="bottom", fontsize=9, color="#1e8e3e", fontweight="bold")

    save_fig_with_permissions(fig, "chart4_alphabeta_nodes_time.png")

    # -------------------------------------------------------------------------
    # ĐỒ THỊ 5: Bài 2 Mở rộng - MCTS Heuristic Rollout vs Random Rollout
    # -------------------------------------------------------------------------
    b2_data = data["bai2_heuristic_rollout"]
    b2_iters = [f"iter = {row['iterations']}" for row in b2_data]
    b2_win_heur = [row["win_rate_pct"] for row in b2_data]
    b2_win_rand = [row["loss_rate_pct"] for row in b2_data]

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    x_b2 = np.arange(len(b2_iters))
    w_b2 = 0.32

    b_h = ax.bar(x_b2 - w_b2 / 2, b2_win_heur, w_b2, label="MCTS + Heuristic Rollout (Bài 2 - Hướng A)", color="#1a73e8")
    b_r = ax.bar(x_b2 + w_b2 / 2, b2_win_rand, w_b2, label="MCTS + Random Rollout (Cơ sở - Bài 1)", color="#9aa0a6")

    ax.set_ylabel("Tỷ lệ Thắng đối đầu trực tiếp (%)", fontsize=11, fontweight="bold")
    ax.set_title("Đồ thị 5 (Bài 2 Mở rộng): Hiệu quả của Heuristic Rollout so với Random Rollout cơ sở", fontsize=11.5, fontweight="bold", pad=14)
    ax.set_xticks(x_b2)
    ax.set_xticklabels(b2_iters, fontsize=10.5, fontweight="bold")
    ax.set_ylim(0, 128)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="upper right")

    for rect in b_h:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2.0, h + 1.8, f"{h:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold", color="#1a73e8")
    for rect in b_r:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2.0, h + 1.8, f"{h:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold", color="#5f6368")

    save_fig_with_permissions(fig, "chart5_bai2_heuristic_rollout.png")


if __name__ == "__main__":
    generate_all_charts()
