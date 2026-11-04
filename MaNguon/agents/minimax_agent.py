"""
File: agents/minimax_agent.py
Mô tả: Cài đặt thuật toán MiniMax kết hợp cắt tỉa Alpha-Beta (Bài 1.2).
       Hỗ trợ bật/tắt cắt tỉa Alpha-Beta để thực nghiệm đối sánh trực tiếp với MiniMax thuần,
       tùy chỉnh độ sâu tìm kiếm d >= 2, giới hạn nước đi ứng viên và ghi nhật ký chi tiết.
"""

import math
import time
from typing import Any, Dict, List, Optional, Tuple
from core.board import Board
from core.evaluator import Evaluator
from .base_agent import BaseAgent


class MiniMaxAgent(BaseAgent):
    """
    Tác nhân sử dụng thuật toán Tìm kiếm Đối kháng MiniMax kết hợp cắt tỉa Alpha-Beta.

    Giải thích các thành phần cốt lõi (Phục vụ Vấn đáp Bài 1.2a):
    - Nút MAX (is_maximizing = True): Đại diện cho lượt đi của chính tác nhân AI hiện tại,
      luôn tìm cách CỰC ĐẠI HÓA giá trị hàm đánh giá (chọn nhánh có điểm cao nhất).
    - Nút MIN (is_maximizing = False): Đại diện cho lượt đi của đối thủ, giả định đối thủ chơi tối ưu
      nên sẽ luôn tìm cách CỰC TIỂU HÓA giá trị hàm đánh giá của AI (chọn nhánh có điểm thấp nhất).
    - Điều kiện kết thúc đệ quy (Terminal Conditions):
      (1) Ván cờ kết thúc (có người tạo được >= 5 quân liên tiếp hoặc bàn cờ đầy hòa), HOẶC
      (2) Đạt đến độ sâu giới hạn (depth == 0).
    - Hàm đánh giá trạng thái: Evaluator.evaluate_board(board, maximizing_player).
    """

    def __init__(
        self,
        depth: int = 2,
        use_alpha_beta: bool = True,
        candidate_radius: int = 1,
        max_candidates: int = 14,
        use_move_ordering: bool = True,
    ):
        mode_str = "AlphaBeta" if use_alpha_beta else "PureMiniMax"
        super().__init__(name=f"MiniMax({mode_str}, d={depth})")
        self.depth = max(1, depth)
        self.use_alpha_beta = use_alpha_beta
        self.candidate_radius = candidate_radius
        self.max_candidates = max_candidates
        self.use_move_ordering = use_move_ordering

        # Biến thống kê phục vụ ghi nhật ký (Bài 1.2c)
        self.nodes_visited: int = 0
        self.pruned_branches: int = 0
        self.maximizing_player: int = 1

    def get_move(self, board: Board) -> Tuple[int, int, Dict[str, Any]]:
        """
        Tìm nước đi tốt nhất cho người chơi hiện tại trên bàn cờ `board`.
        """
        start_time = time.perf_counter()
        self.nodes_visited = 0
        self.pruned_branches = 0
        self.maximizing_player = board.current_player

        # Sinh danh sách nước đi ứng viên trong bán kính lân cận
        candidates = board.get_candidate_moves(radius=self.candidate_radius)
        if not candidates:
            raise ValueError("Không còn nước đi hợp lệ trên bàn cờ.")

        # Nếu chỉ có duy nhất 1 nước ứng viên (ví dụ nước đầu tiên ở tâm bàn cờ 4,4)
        if len(candidates) == 1:
            chosen_move = candidates[0]
            elapsed = time.perf_counter() - start_time
            stats = {
                "agent": self.name,
                "move": chosen_move,
                "depth": self.depth,
                "time_sec": round(elapsed, 6),
                "nodes_visited": 1,
                "pruned_branches": 0,
                "score": 0.0,
                "use_alpha_beta": self.use_alpha_beta,
            }
            self.last_stats = stats
            return chosen_move[0], chosen_move[1], stats

        # Sắp xếp thứ tự nước đi ứng viên (Move Ordering) giúp cắt tỉa sớm nhất
        if self.use_move_ordering:
            candidates = Evaluator.order_moves(
                board, candidates, self.maximizing_player, self.max_candidates
            )
        elif self.max_candidates and len(candidates) > self.max_candidates:
            candidates = candidates[: self.max_candidates]

        best_score = -math.inf
        best_move = candidates[0]
        alpha = -math.inf
        beta = math.inf

        # Duyệt các nhánh con ở tầng gốc (Root - Nút MAX)
        for r, c in candidates:
            board.make_move(r, c)
            score = self._minimax(
                board=board,
                depth=self.depth - 1,
                alpha=alpha,
                beta=beta,
                is_maximizing=False,
            )
            board.undo_move()

            if score > best_score:
                best_score = score
                best_move = (r, c)

            if self.use_alpha_beta:
                alpha = max(alpha, best_score)

        elapsed = time.perf_counter() - start_time
        stats = {
            "agent": self.name,
            "move": best_move,
            "depth": self.depth,
            "time_sec": round(elapsed, 6),
            "nodes_visited": self.nodes_visited,
            "pruned_branches": self.pruned_branches,
            "score": round(best_score, 2),
            "use_alpha_beta": self.use_alpha_beta,
        }
        self.last_stats = stats
        return best_move[0], best_move[1], stats

    def _minimax(
        self,
        board: Board,
        depth: int,
        alpha: float,
        beta: float,
        is_maximizing: bool,
    ) -> float:
        """
        Hàm đệ quy MiniMax kết hợp cắt tỉa Alpha-Beta.
        - alpha: Giá trị tốt nhất (cao nhất) mà nút MAX đang được đảm bảo trên đường đi tới gốc.
        - beta : Giá trị tốt nhất (thấp nhất) mà nút MIN đang được đảm bảo trên đường đi tới gốc.
        """
        self.nodes_visited += 1

        # 1. Kiểm tra điều kiện dừng (Terminal State hoặc đạt giới hạn độ sâu d)
        if board.is_game_over():
            if board.winner == self.maximizing_player:
                # Cộng thêm depth để ưu tiên thắng càng sớm càng tốt (ít nước đi hơn)
                return 100000.0 + depth * 100.0
            elif board.winner == -self.maximizing_player:
                # Trừ thêm depth để nếu thua thì kéo dài ván cờ lâu nhất có thể
                return -100000.0 - depth * 100.0
            else:
                return 0.0  # Hòa

        if depth <= 0:
            return Evaluator.evaluate_board(board, self.maximizing_player)

        # 2. Sinh danh sách nước đi ứng viên cho trạng thái hiện tại
        candidates = board.get_candidate_moves(radius=self.candidate_radius)
        if self.use_move_ordering:
            candidates = Evaluator.order_moves(
                board, candidates, board.current_player, self.max_candidates
            )
        elif self.max_candidates and len(candidates) > self.max_candidates:
            candidates = candidates[: self.max_candidates]

        # 3. Nhánh của Nút MAX (Tối đa hóa điểm số)
        if is_maximizing:
            max_eval = -math.inf
            for r, c in candidates:
                board.make_move(r, c)
                eval_score = self._minimax(
                    board, depth - 1, alpha, beta, is_maximizing=False
                )
                board.undo_move()

                if eval_score > max_eval:
                    max_eval = eval_score

                # [GHI CHÚ THIẾT KẾ]: Cơ chế cắt tỉa Beta (Beta Cutoff) tại nút MAX
                if self.use_alpha_beta:
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        self.pruned_branches += 1
                        break  # Cắt tỉa: Nút MIN cha ở trên sẽ không bao giờ chọn nhánh này
            return max_eval

        # 4. Nhánh của Nút MIN (Tối thiểu hóa điểm số của MAX)
        else:
            min_eval = math.inf
            for r, c in candidates:
                board.make_move(r, c)
                eval_score = self._minimax(
                    board, depth - 1, alpha, beta, is_maximizing=True
                )
                board.undo_move()

                if eval_score < min_eval:
                    min_eval = eval_score

                # [GHI CHÚ THIẾT KẾ]: Cơ chế cắt tỉa Alpha (Alpha Cutoff) tại nút MIN
                if self.use_alpha_beta:
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        self.pruned_branches += 1
                        break  # Cắt tỉa: Nút MAX cha ở trên đã có lựa chọn >= alpha tốt hơn rồi
            return min_eval
