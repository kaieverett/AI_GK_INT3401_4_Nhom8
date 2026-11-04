"""
File: ui/cli.py
Mô tả: Giao diện dòng lệnh (CLI) cho phép chơi cờ Caro 9x9:
       - Chế độ Người đấu với Máy (Human vs AI)
       - Chế độ Máy đấu với Máy (AI vs AI)
       - Chế độ Kiểm tra trạng thái cờ thử nghiệm (Alpha-Beta vs Pure MiniMax vs MCTS)
"""

import time
from typing import Optional, Tuple
from core.board import Board, PLAYER_X, PLAYER_O
from agents import BaseAgent, RandomAgent, MiniMaxAgent, MCTSAgent, MCTSHeuristicAgent


def create_agent_interactive(role_label: str) -> BaseAgent:
    """Menu chọn và cấu hình tham số cho tác nhân AI trên dòng lệnh."""
    print(f"\n--- Cấu hình tác nhân cho {role_label} ---")
    print("  1. MiniMax + Cắt tỉa Alpha-Beta (Bài 1.2)")
    print("  2. MiniMax thuần KHÔNG cắt tỉa (Để đối sánh hiệu quả cắt tỉa)")
    print("  3. MCTS + UCT cơ sở - Random Rollout (Bài 1.3)")
    print("  4. MCTS + UCT cải tiến - Heuristic Rollout (Bài 2 Mở rộng)")
    print("  5. Random Agent (Chọn nước ngẫu nhiên)")
    choice = input("Chọn loại AI [mặc định = 1]: ").strip() or "1"

    if choice in ("1", "2"):
        use_ab = choice == "1"
        d_str = input("  Nhập độ sâu tìm kiếm d (tối thiểu 2) [mặc định = 2]: ").strip()
        depth = int(d_str) if d_str.isdigit() and int(d_str) >= 1 else 2
        return MiniMaxAgent(depth=depth, use_alpha_beta=use_ab)
    elif choice in ("3", "4"):
        c_str = input("  Nhập hệ số khám phá c [mặc định = 1.4]: ").strip()
        try:
            c_val = float(c_str) if c_str else 1.4
        except ValueError:
            c_val = 1.4
        it_str = input("  Nhập số lượt mô phỏng iterations [mặc định = 300]: ").strip()
        iters = int(it_str) if it_str.isdigit() and int(it_str) >= 10 else 300
        if choice == "3":
            return MCTSAgent(iterations=iters, c=c_val)
        else:
            return MCTSHeuristicAgent(iterations=iters, c=c_val)
    else:
        return RandomAgent()


def format_stats_log(player: int, stats: dict) -> str:
    """Định dạng chuỗi nhật ký (log) theo đúng yêu cầu Bài 1.2c và 1.3d."""
    p_name = Board.player_name(player)
    move = stats.get("move", (-1, -1))
    time_s = stats.get("time_sec", 0.0)
    nodes = stats.get("nodes_visited", 0)
    agent_name = stats.get("agent", "AI")

    if "depth" in stats and "MiniMax" in agent_name:
        pruned = stats.get("pruned_branches", 0)
        score = stats.get("score", 0.0)
        return (
            f"[{p_name} - {agent_name}] Nước đi: {move} | Độ sâu d={stats['depth']} | "
            f"Thời gian: {time_s:.4f}s | Số nút duyệt: {nodes} | Nhánh cắt tỉa: {pruned} | Điểm: {score}"
        )
    elif "iterations" in stats:
        visits = stats.get("selected_visits", 0)
        win_rate = stats.get("selected_win_rate", 0.0) * 100
        return (
            f"[{p_name} - {agent_name}] Nước đi: {move} | c={stats['c']}, iter={stats['iterations']} | "
            f"Thời gian: {time_s:.4f}s | Tổng nút cây: {nodes} | Lượt thăm N lớn nhất: {visits} | Tỷ lệ W/N: {win_rate:.1f}%"
        )
    else:
        return f"[{p_name} - {agent_name}] Nước đi: {move} | Thời gian: {time_s:.4f}s | Số nút: {nodes}"


def play_cli_game(agent_x: Optional[BaseAgent], agent_o: Optional[BaseAgent], board: Optional[Board] = None) -> None:
    """Vòng lặp trận đấu trên giao diện dòng lệnh."""
    if board is None:
        board = Board()

    last_move: Optional[Tuple[int, int]] = board.move_history[-1] if board.move_history else None

    while not board.is_game_over():
        print("\n" + board.to_ascii(last_move))
        curr = board.current_player
        p_name = Board.player_name(curr)
        current_agent = agent_x if curr == PLAYER_X else agent_o

        if current_agent is None:
            # Lượt của người chơi
            while True:
                raw = input(f"\nLượt của bạn ({p_name}) - Nhập 'dòng cột' (ví dụ: 4 4) hoặc 'q' để thoát: ").strip()
                if raw.lower() in ("q", "quit", "exit"):
                    print("Đã thoát ván cờ.")
                    return
                parts = raw.replace(",", " ").split()
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    r, c = int(parts[0]), int(parts[1])
                    if board.make_move(r, c):
                        last_move = (r, c)
                        break
                print("  [!] Nước đi không hợp lệ hoặc ô đã có quân. Vui lòng nhập lại (0..8)!")
        else:
            # Lượt của AI
            r, c, stats = current_agent.get_move(board)
            board.make_move(r, c)
            last_move = (r, c)
            print("\n" + format_stats_log(curr, stats))
            if agent_x is not None and agent_o is not None:
                time.sleep(0.15)

    print("\n" + board.to_ascii(last_move))
    print("=" * 65)
    if board.winner == PLAYER_X:
        print(">>> KẾT QUẢ VÁN CỜ: NGƯỜI CHƠI X CHIẾN THẮNG! (Tạo được >= 5 quân liên tiếp)")
        print(f"    Chuỗi quân chiến thắng: {board.winning_line}")
    elif board.winner == PLAYER_O:
        print(">>> KẾT QUẢ VÁN CỜ: NGƯỜI CHƠI O CHIẾN THẮNG! (Tạo được >= 5 quân liên tiếp)")
        print(f"    Chuỗi quân chiến thắng: {board.winning_line}")
    else:
        print(">>> KẾT QUẢ VÁN CỜ: HÒA! (Bàn cờ 9x9 đã đầy)")
    print("=" * 65)


def run_cli() -> None:
    """Menu chính của giao diện dòng lệnh."""
    while True:
        print("\n" + "=" * 65)
        print("   CHƯƠNG TRÌNH CỜ CARO 9x9 - TRÍ TUỆ NHÂN TẠO (NHÓM 8 - INT3401 4)")
        print("=" * 65)
        print("  1. Người đấu với Máy (Human vs AI)")
        print("  2. Máy đấu với Máy (AI vs AI)")
        print("  3. Kiểm tra & Đối sánh trên các Trạng thái cờ mẫu (Preset States)")
        print("  0. Thoát chương trình")
        mode = input("Chọn chế độ [1/2/3/0]: ").strip()

        if mode == "0":
            break
        elif mode == "1":
            first = input("Bạn muốn cầm quân X đi trước không? [y/n, mặc định = y]: ").strip().lower()
            ai_agent = create_agent_interactive("Máy (AI)")
            if first in ("", "y", "yes"):
                play_cli_game(agent_x=None, agent_o=ai_agent)
            else:
                play_cli_game(agent_x=ai_agent, agent_o=None)
        elif mode == "2":
            agent_x = create_agent_interactive("Quân X (Đi trước)")
            agent_o = create_agent_interactive("Quân O (Đi sau)")
            play_cli_game(agent_x=agent_x, agent_o=agent_o)
        elif mode == "3":
            board = Board()
            print("\nChọn trạng thái bàn cờ mẫu:")
            print("  1. Khai cuộc (4 quân ở trung tâm)")
            print("  2. Trung cuộc giằng co (10 quân)")
            print("  3. Nguy cấp: Chặn chuỗi 4 quân của đối phương")
            print("  4. Bẫy đôi 3-3 (Fork)")
            p_choice = input("Chọn [1-4, mặc định = 3]: ").strip() or "3"
            mapping = {
                "1": "khai_cuoc",
                "2": "trung_cuoc",
                "3": "chan_chuoi_4",
                "4": "bay_doi_3_3",
            }
            desc = board.load_preset_state(mapping.get(p_choice, "chan_chuoi_4"))
            print(f"\nĐã tải: {desc}")
            print(board.to_ascii(board.move_history[-1] if board.move_history else None))
            print(f"Lượt hiện tại: Quân {Board.player_name(board.current_player)}")

            for d in (2, 3):
                ab_agent = MiniMaxAgent(depth=d, use_alpha_beta=True)
                pure_agent = MiniMaxAgent(depth=d, use_alpha_beta=False)
                _, _, st_ab = ab_agent.get_move(board.clone())
                _, _, st_pure = pure_agent.get_move(board.clone())
                print("\n--- Đối sánh ở độ sâu d =", d, "---")
                print("  +", format_stats_log(board.current_player, st_ab))
                print("  +", format_stats_log(board.current_player, st_pure))
                ratio = (
                    (1.0 - st_ab["nodes_visited"] / max(1, st_pure["nodes_visited"])) * 100
                )
                print(f"  => Hiệu quả cắt tỉa Alpha-Beta: Giảm {ratio:.1f}% số nút phải duyệt, chọn CÙNG nước đi {st_ab['move']}!")
