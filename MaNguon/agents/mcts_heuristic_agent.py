"""
File: agents/mcts_heuristic_agent.py
Mô tả: Cài đặt Bài 2 - Phần mở rộng, khuyến khích (Hướng A):
       "Thay rollout ngẫu nhiên bằng rollout có heuristic (ưu tiên tạo/chặn chuỗi quân)
        và đánh giá mức cải thiện so với rollout cơ sở."
"""

from typing import List, Optional, Tuple
from core.board import Board
from core.evaluator import Evaluator
from .mcts_agent import MCTSAgent


class MCTSHeuristicAgent(MCTSAgent):
    """
    Tác nhân MCTS nâng cao sử dụng Heuristic Rollout (Bài 2 - Hướng A).

    [GHI CHÚ THIẾT KẾ - BÀI 2 KHUYẾN KHÍCH (+1.0 ĐIỂM)]:
    1. Tại sao Rollout ngẫu nhiên của MCTS cơ sở lại yếu trên cờ Caro 9x9?
       - Trên bàn cờ 9x9 (81 ô), nếu hai bên đánh ngẫu nhiên hoàn toàn, các quân cờ bị rải rác
         khắp bàn cờ và bỏ qua các nước thắng trực tiếp (chuỗi 4 mở) hoặc không chặn chuỗi 4
         của đối phương. Điều này làm kết quả mô phỏng bị nhiễu nặng (High Variance / Tactical Blindness).
    2. Cơ chế Heuristic Rollout (Epsilon-Greedy Tactical Rollout) cải tiến như thế nào?
       - Cải tiến 1 (Tập trung không gian): Chỉ chọn các nước đi ứng viên trong bán kính lân cận
         xung quanh các quân cờ đã đánh thay vì đánh bừa ra góc bàn cờ.
       - Cải tiến 2 (Phát hiện chuỗi chiến thuật): Chấm điểm nhanh `Evaluator.score_move_quick`
         cho tập ứng viên. Nếu phát hiện nước đi tạo 5 quân (thắng ngay) hoặc chặn chuỗi 4 của đối phương,
         bắt buộc thực hiện ngay lập tức.
       - Cải tiến 3 (Epsilon-Greedy Rollout, epsilon = 0.80): Với xác suất 80% chọn nước đi tạo/chặn
         chuỗi tốt nhất, 20% chọn ngẫu nhiên trong nhóm ứng viên hàng đầu để vẫn giữ được tính ngẫu nhiên
         thống kê đặc trưng của Monte Carlo.
    """

    def __init__(
        self,
        iterations: int = 300,
        c: float = 1.4,
        candidate_radius: int = 1,
        max_rollout_depth: int = 24,
        epsilon: float = 0.80,
        selection_policy: str = "max_visits",
        seed: Optional[int] = None,
    ):
        super().__init__(
            iterations=iterations,
            c=c,
            candidate_radius=candidate_radius,
            selection_policy=selection_policy,
            seed=seed,
        )
        self.name = f"MCTS_Heuristic(c={c}, iter={iterations})"
        self.max_rollout_depth = max_rollout_depth
        self.epsilon = epsilon

    def _get_expandable_moves(self, board: Board) -> List[Tuple[int, int]]:
        """
        Sắp xếp các nước chưa mở rộng theo điểm Heuristic tăng dần
        (vì `_expand` dùng `.pop()` lấy phần tử cuối danh sách, nên nước có điểm cao nhất
        nằm ở cuối sẽ được mở rộng đầu tiên!).
        """
        moves = board.get_candidate_moves(radius=self.candidate_radius)
        scored = [
            (Evaluator.score_move_quick(board, r, c, board.current_player), (r, c))
            for r, c in moves
        ]
        # Giữ tối đa 12 nước ứng viên tốt nhất để cây MCTS tập trung đào sâu
        scored.sort(key=lambda x: x[0])
        if len(scored) > 12:
            scored = scored[-12:]
        return [m for _, m in scored]

    def _simulate(self, sim_board: Board) -> int:
        """
        Giai đoạn 3 cải tiến - Heuristic Rollout (Mô phỏng có định hướng tạo/chặn chuỗi quân).
        """
        if sim_board.is_game_over():
            return sim_board.winner if sim_board.winner is not None else 0

        steps = 0
        while not sim_board.is_game_over() and steps < self.max_rollout_depth:
            candidates = sim_board.get_candidate_moves(radius=1)
            if not candidates:
                break

            # Nếu số ứng viên nhiều hơn 8, lấy ngẫu nhiên 8 ứng viên quanh khu vực giao tranh
            # kết hợp các ô sát nước đi cuối cùng để đảm bảo tốc độ mô phỏng nhanh
            if len(candidates) > 8:
                last_r, last_c = sim_board.move_history[-1]
                local_urgent = [
                    (r, c)
                    for r, c in candidates
                    if abs(r - last_r) <= 1 and abs(c - last_c) <= 1
                ]
                others = [
                    m for m in candidates if m not in local_urgent
                ]
                sample_k = max(0, 8 - len(local_urgent))
                sampled_others = (
                    self.rng.sample(others, sample_k) if len(others) > sample_k else others
                )
                pool = local_urgent + sampled_others
            else:
                pool = candidates

            curr_player = sim_board.current_player
            best_move = pool[0]
            best_score = -1

            for r, c in pool:
                sc = Evaluator.score_move_quick(sim_board, r, c, curr_player)
                if sc > best_score:
                    best_score = sc
                    best_move = (r, c)

            # Nếu là nước thắng ngay hoặc chặn chuỗi 4 nguy hiểm (>= 1500 điểm), đánh ngay!
            if best_score >= 1500 or self.rng.random() < self.epsilon:
                chosen = best_move
            else:
                chosen = self.rng.choice(pool)

            sim_board.make_move(chosen[0], chosen[1])
            steps += 1

        if sim_board.winner is not None:
            return sim_board.winner

        # Nếu hết độ sâu rollout mà chưa ai thắng, dùng hàm đánh giá nhanh để xác định bên ưu thế
        eval_x = Evaluator.evaluate_board(sim_board, 1)
        if eval_x > 800:
            return 1
        elif eval_x < -800:
            return -1
        return 0
