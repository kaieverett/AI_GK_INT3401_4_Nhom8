"""
File: experiments/run_experiments.py
Mô tả: Tự động hóa toàn bộ quy trình thực nghiệm theo đúng yêu cầu Bài 1.2c, Bài 1.4 và Bài 2:
       1. Thực nghiệm cắt tỉa Alpha-Beta vs MiniMax không cắt tỉa trên 4 trạng thái cờ mẫu (d=2, d=3).
       2. Thực nghiệm đối sánh (Head-to-Head): Random, MiniMax+AlphaBeta, MCTS+UCT, MCTS+Heuristic.
       3. Thực nghiệm khảo sát tham số c thuộc {0.5, 1.0, 1.4, 2.0} với iteration = 300 cố định.
       4. Thực nghiệm khảo sát số iteration thuộc {100, 300, 500} với c = 1.4 cố định.
       5. Thực nghiệm Bài 2 Mở rộng (Hướng A): MCTS Heuristic Rollout vs MCTS Random Rollout.
       Mỗi cấu hình chạy tối thiểu 20 ván (10 cặp ván hoán đổi người đi trước X/O) từ bộ
       khai cuộc cân bằng cố định với hạt giống RANDOM_SEED = 2026 để đảm bảo tính tái lập 100%.
"""

import csv
import json
import os
import platform
import random
import sys
import time
from typing import Callable, Dict, List, Tuple

# Đảm bảo import được các module ở thư mục gốc MaNguon
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.board import Board, PLAYER_X, PLAYER_O
from agents import BaseAgent, RandomAgent, MiniMaxAgent, MCTSAgent, MCTSHeuristicAgent

RANDOM_SEED = 2026
RESULTS_DIR = os.path.join(ROOT_DIR, "results")

# 10 cặp khai cuộc 2 nước cân bằng ở vùng trung tâm (1 quân X, 1 quân O sát nhau)
# Giúp 10 cặp ván (20 ván hoán đổi tiên/hậu) giữa các thuật toán (kể cả thuật toán tất định như MiniMax)
# diễn ra đa dạng, khách quan, công bằng tuyệt đối và tái lập chính xác 100%.
BALANCED_OPENINGS: List[List[Tuple[int, int]]] = [
    [(4, 4), (4, 5)],
    [(4, 4), (3, 4)],
    [(4, 4), (3, 3)],
    [(4, 4), (5, 5)],
    [(4, 4), (3, 5)],
    [(4, 4), (5, 3)],
    [(3, 3), (4, 4)],
    [(3, 4), (4, 4)],
    [(4, 3), (4, 4)],
    [(5, 4), (4, 4)],
]


def get_system_info() -> Dict[str, str]:
    """Thu thập thông tin cấu hình phần cứng & môi trường thực thi (Bài 1.4e)."""
    cpu_model = platform.processor() or "x86_64 Processor"
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
            for line in f:
                if "model name" in line:
                    cpu_model = line.split(":", 1)[1].strip()
                    break
    except Exception:
        pass

    ram_gb = "N/A"
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                if "MemTotal" in line:
                    kb = int(line.split()[1])
                    ram_gb = f"{kb / (1024 * 1024):.1f} GB"
                    break
    except Exception:
        pass

    return {
        "os": f"{platform.system()} {platform.release()}",
        "python_version": platform.python_version(),
        "cpu": cpu_model,
        "cpu_cores": str(os.cpu_count() or 4),
        "ram": ram_gb,
        "random_seed": str(RANDOM_SEED),
    }


def play_single_match(
    agent_x: BaseAgent,
    agent_o: BaseAgent,
    opening_moves: List[Tuple[int, int]],
) -> Tuple[int, float, float, int]:
    """
    Chạy 1 ván đấu hoàn chỉnh giữa `agent_x` (cầm X đi trước) và `agent_o` (cầm O đi sau).
    Trả về:
        winner (1: X thắng, -1: O thắng, 0: Hòa),
        avg_time_x (thời gian suy luận trung bình mỗi nước của X),
        avg_time_o (thời gian suy luận trung bình mỗi nước của O),
        total_moves (tổng số nước đi của ván cờ)
    """
    board = Board()
    for r, c in opening_moves:
        board.make_move(r, c)

    times_x: List[float] = []
    times_o: List[float] = []

    while not board.is_game_over():
        curr = board.current_player
        if curr == PLAYER_X:
            r, c, stats = agent_x.get_move(board)
            times_x.append(stats.get("time_sec", 0.0))
        else:
            r, c, stats = agent_o.get_move(board)
            times_o.append(stats.get("time_sec", 0.0))
        board.make_move(r, c)

    avg_tx = sum(times_x) / len(times_x) if times_x else 0.0
    avg_to = sum(times_o) / len(times_o) if times_o else 0.0
    winner = board.winner if board.winner is not None else 0
    return winner, avg_tx, avg_to, len(board.move_history)


def evaluate_matchup(
    make_agent_a: Callable[[int], BaseAgent],
    make_agent_b: Callable[[int], BaseAgent],
    num_pairs: int = 10,
    label_a: str = "Agent A",
    label_b: str = "Agent B",
) -> Dict[str, object]:
    """
    Đánh giá 1 cặp đấu với `num_pairs` cặp ván (tổng cộng 2 * num_pairs = 20 ván),
    hoán đổi người đi trước (X) và đi sau (O) trên từng thế cờ khai cuộc để đảm bảo công bằng tuyệt đối.
    """
    wins_a = 0
    draws = 0
    losses_a = 0
    times_a: List[float] = []
    times_b: List[float] = []
    moves_list: List[int] = []

    for pair_idx in range(num_pairs):
        opening = BALANCED_OPENINGS[pair_idx % len(BALANCED_OPENINGS)]
        seed_1 = RANDOM_SEED + pair_idx * 17 + 1
        seed_2 = RANDOM_SEED + pair_idx * 17 + 2

        # Ván 1 của cặp: Agent A đi trước (X), Agent B đi sau (O)
        agent_a1 = make_agent_a(seed_1)
        agent_b1 = make_agent_b(seed_1 + 1000)
        w1, tx1, to1, m1 = play_single_match(agent_a1, agent_b1, opening)
        times_a.append(tx1)
        times_b.append(to1)
        moves_list.append(m1)
        if w1 == PLAYER_X:
            wins_a += 1
        elif w1 == PLAYER_O:
            losses_a += 1
        else:
            draws += 1

        # Ván 2 của cặp (Hoán đổi màu quân): Agent B đi trước (X), Agent A đi sau (O)
        agent_b2 = make_agent_b(seed_2 + 1000)
        agent_a2 = make_agent_a(seed_2)
        w2, tx2, to2, m2 = play_single_match(agent_b2, agent_a2, opening)
        times_b.append(tx2)
        times_a.append(to2)
        moves_list.append(m2)
        if w2 == PLAYER_O:
            wins_a += 1
        elif w2 == PLAYER_X:
            losses_a += 1
        else:
            draws += 1

    total_games = num_pairs * 2
    win_rate = (wins_a / total_games) * 100.0
    draw_rate = (draws / total_games) * 100.0
    loss_rate = (losses_a / total_games) * 100.0
    avg_time_a = sum(times_a) / len(times_a) if times_a else 0.0
    avg_time_b = sum(times_b) / len(times_b) if times_b else 0.0
    avg_moves = sum(moves_list) / len(moves_list) if moves_list else 0.0

    result = {
        "agent_a": label_a,
        "agent_b": label_b,
        "total_games": total_games,
        "wins": wins_a,
        "draws": draws,
        "losses": losses_a,
        "win_rate_pct": round(win_rate, 1),
        "draw_rate_pct": round(draw_rate, 1),
        "loss_rate_pct": round(loss_rate, 1),
        "avg_time_a_sec": round(avg_time_a, 4),
        "avg_time_b_sec": round(avg_time_b, 4),
        "avg_game_moves": round(avg_moves, 1),
    }
    print(
        f"  -> [{label_a} vs {label_b}] ({total_games} ván): "
        f"Thắng={wins_a}, Hòa={draws}, Thua={losses_a} | "
        f"WinRate={win_rate:.1f}% | Thời gian TB/nước={avg_time_a*1000:.2f}ms"
    )
    return result


def run_exp_alphabeta_pruning() -> List[Dict[str, object]]:
    """
    Thực nghiệm Bài 1.2c: Giải thích và chứng minh hiệu quả của cắt tỉa Alpha-Beta
    so với MiniMax không cắt tỉa trên 4 trạng thái bàn cờ thử nghiệm ở độ sâu d=2 và d=3.
    """
    print("\n[Thực nghiệm 1.2c] Đối sánh MiniMax KHÔNG cắt tỉa vs MiniMax CÓ cắt tỉa Alpha-Beta...")
    presets = ["khai_cuoc", "trung_cuoc", "chan_chuoi_4", "bay_doi_3_3"]
    rows: List[Dict[str, object]] = []

    for p_name in presets:
        for d in (2, 3):
            b1 = Board()
            desc = b1.load_preset_state(p_name)
            b2 = b1.clone()

            pure_mm = MiniMaxAgent(depth=d, use_alpha_beta=False, use_move_ordering=True)
            ab_mm = MiniMaxAgent(depth=d, use_alpha_beta=True, use_move_ordering=True)

            _, _, st_pure = pure_mm.get_move(b1)
            _, _, st_ab = ab_mm.get_move(b2)

            nodes_pure = st_pure["nodes_visited"]
            nodes_ab = st_ab["nodes_visited"]
            time_pure = st_pure["time_sec"]
            time_ab = st_ab["time_sec"]
            node_reduction = (1.0 - nodes_ab / max(1, nodes_pure)) * 100.0
            speedup = time_pure / max(1e-6, time_ab)

            row = {
                "preset": p_name,
                "description": desc,
                "depth": d,
                "chosen_move_pure": str(st_pure["move"]),
                "chosen_move_ab": str(st_ab["move"]),
                "same_optimal_move": st_pure["move"] == st_ab["move"],
                "nodes_pure": nodes_pure,
                "nodes_ab": nodes_ab,
                "pruned_branches": st_ab["pruned_branches"],
                "node_reduction_pct": round(node_reduction, 1),
                "time_pure_ms": round(time_pure * 1000, 2),
                "time_ab_ms": round(time_ab * 1000, 2),
                "speedup_factor": round(speedup, 2),
            }
            rows.append(row)
            print(
                f"  + {p_name} (d={d}): Nước chọn={st_ab['move']} | "
                f"Nút duyệt: {nodes_pure} -> {nodes_ab} (Giảm {node_reduction:.1f}%) | "
                f"Thời gian: {time_pure*1000:.2f}ms -> {time_ab*1000:.2f}ms ({speedup:.1f}x)"
            )

    csv_path = os.path.join(RESULTS_DIR, "exp4_alphabeta_pruning.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def run_all_experiments() -> Dict[str, object]:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    random.seed(RANDOM_SEED)
    sys_info = get_system_info()
    print("=" * 72)
    print("BẮT ĐẦU CHẠY THỰC NGHIỆM BÀI TẬP LỚN AI - LỚP INT3401 4 - NHÓM 8")
    print(f"Cấu hình máy: {sys_info['cpu']} ({sys_info['cpu_cores']} cores) | RAM: {sys_info['ram']} | Seed: {RANDOM_SEED}")
    print("=" * 72)

    # 1. Thực nghiệm cắt tỉa Alpha-Beta (Bài 1.2c)
    ab_rows = run_exp_alphabeta_pruning()

    # 2. Thực nghiệm đối sánh các thuật toán (Bài 1.4a & Bài 2)
    print("\n[Thực nghiệm 1.4a] Đối sánh giữa Random, MiniMax+AlphaBeta, MCTS+UCT và MCTS+Heuristic (20 ván/cặp)...")
    head_to_head_rows = [
        evaluate_matchup(
            lambda s: MiniMaxAgent(depth=2, use_alpha_beta=True),
            lambda s: RandomAgent(seed=s),
            num_pairs=10,
            label_a="MiniMax+AlphaBeta (d=2)",
            label_b="Random",
        ),
        evaluate_matchup(
            lambda s: MCTSAgent(iterations=300, c=1.4, seed=s),
            lambda s: RandomAgent(seed=s),
            num_pairs=10,
            label_a="MCTS+UCT Cơ sở (c=1.4, iter=300)",
            label_b="Random",
        ),
        evaluate_matchup(
            lambda s: MCTSAgent(iterations=300, c=1.4, seed=s),
            lambda s: MiniMaxAgent(depth=2, use_alpha_beta=True),
            num_pairs=10,
            label_a="MCTS+UCT Cơ sở (c=1.4, iter=300)",
            label_b="MiniMax+AlphaBeta (d=2)",
        ),
        evaluate_matchup(
            lambda s: MCTSHeuristicAgent(iterations=300, c=1.4, seed=s),
            lambda s: MCTSAgent(iterations=300, c=1.4, seed=s),
            num_pairs=10,
            label_a="MCTS+Heuristic [Bài 2] (c=1.4, iter=300)",
            label_b="MCTS+UCT Cơ sở (c=1.4, iter=300)",
        ),
        evaluate_matchup(
            lambda s: MCTSHeuristicAgent(iterations=300, c=1.4, seed=s),
            lambda s: MiniMaxAgent(depth=2, use_alpha_beta=True),
            num_pairs=10,
            label_a="MCTS+Heuristic [Bài 2] (c=1.4, iter=300)",
            label_b="MiniMax+AlphaBeta (d=2)",
        ),
    ]
    h2h_csv = os.path.join(RESULTS_DIR, "exp1_head_to_head.csv")
    with open(h2h_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(head_to_head_rows[0].keys()))
        writer.writeheader()
        writer.writerows(head_to_head_rows)

    # 3. Thực nghiệm khảo sát tham số c thuộc {0.5, 1.0, 1.4, 2.0} (Bài 1.4b)
    # Đối thủ cố định: MCTS chuẩn (c=1.0, iterations=150) để đo nhạy cảm của hệ số khám phá c
    print("\n[Thực nghiệm 1.4b] Khảo sát c thuộc {0.5, 1.0, 1.4, 2.0} với iteration = 300 cố định (20 ván/cấu hình)...")
    c_values = [0.5, 1.0, 1.4, 2.0]
    c_rows: List[Dict[str, object]] = []
    for c_val in c_values:
        res = evaluate_matchup(
            lambda s, cv=c_val: MCTSAgent(iterations=300, c=cv, seed=s),
            lambda s: MCTSAgent(iterations=150, c=1.0, seed=s),
            num_pairs=10,
            label_a=f"MCTS (c={c_val}, iter=300)",
            label_b="Đối thủ cố định (MCTS iter=150)",
        )
        res["c"] = c_val
        res["iterations"] = 300
        c_rows.append(res)

    c_csv = os.path.join(RESULTS_DIR, "exp2_c_sensitivity.csv")
    with open(c_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(c_rows[0].keys()))
        writer.writeheader()
        writer.writerows(c_rows)

    # 4. Thực nghiệm khảo sát số iteration thuộc {100, 300, 500} với c = 1.4 cố định (Bài 1.4c)
    print("\n[Thực nghiệm 1.4c] Khảo sát số iteration thuộc {100, 300, 500} với c = 1.4 cố định (20 ván/cấu hình)...")
    iter_values = [100, 300, 500]
    iter_rows: List[Dict[str, object]] = []
    for it_val in iter_values:
        res = evaluate_matchup(
            lambda s, iv=it_val: MCTSAgent(iterations=iv, c=1.4, seed=s),
            lambda s: MCTSAgent(iterations=150, c=1.0, seed=s),
            num_pairs=10,
            label_a=f"MCTS (c=1.4, iter={it_val})",
            label_b="Đối thủ cố định (MCTS iter=150)",
        )
        res["c"] = 1.4
        res["iterations"] = it_val
        iter_rows.append(res)

    iter_csv = os.path.join(RESULTS_DIR, "exp3_iter_sensitivity.csv")
    with open(iter_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(iter_rows[0].keys()))
        writer.writeheader()
        writer.writerows(iter_rows)

    # 5. Thực nghiệm Bài 2 Mở rộng (Hướng A): So sánh Heuristic Rollout vs Random Rollout theo số iteration
    print("\n[Thực nghiệm Bài 2 - Hướng A] Đối sánh MCTS Heuristic Rollout vs Random Rollout ở iter={100, 300, 500}...")
    bai2_rows: List[Dict[str, object]] = []
    for it_val in [100, 300, 500]:
        res = evaluate_matchup(
            lambda s, iv=it_val: MCTSHeuristicAgent(iterations=iv, c=1.4, seed=s),
            lambda s, iv=it_val: MCTSAgent(iterations=iv, c=1.4, seed=s),
            num_pairs=10,
            label_a=f"MCTS Heuristic Rollout (iter={it_val})",
            label_b=f"MCTS Random Rollout (iter={it_val})",
        )
        res["iterations"] = it_val
        bai2_rows.append(res)

    bai2_csv = os.path.join(RESULTS_DIR, "exp5_bai2_rollout.csv")
    with open(bai2_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(bai2_rows[0].keys()))
        writer.writeheader()
        writer.writerows(bai2_rows)

    summary = {
        "system_info": sys_info,
        "alphabeta_pruning": ab_rows,
        "head_to_head": head_to_head_rows,
        "c_sensitivity": c_rows,
        "iter_sensitivity": iter_rows,
        "bai2_heuristic_rollout": bai2_rows,
    }
    json_path = os.path.join(RESULTS_DIR, "experiment_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 72)
    print(f"HOÀN TẤT TOÀN BỘ THỰC NGHIỆM! Kết quả đã lưu tại: {RESULTS_DIR}")
    print("=" * 72)
    return summary


if __name__ == "__main__":
    run_all_experiments()
