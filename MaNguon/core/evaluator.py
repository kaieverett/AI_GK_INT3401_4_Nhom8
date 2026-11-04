"""
File: core/evaluator.py
Mô tả: Hàm đánh giá trạng thái bàn cờ (Heuristic Evaluation Function) cho thuật toán MiniMax
       và đánh giá nhanh nước đi cục bộ (Quick Move Scoring) cho Move Ordering & Heuristic Rollout.
"""

from typing import List, Tuple
from .board import Board, EMPTY, DIRECTIONS

# [GHI CHÚ THIẾT KẾ]: Bảng trọng số điểm của các mẫu hình chuỗi quân (Length, Open_Ends)
# Giải thích:
# - Chuỗi 5 quân (bất kể bị chặn hay không) = 100,000 điểm (Thắng tuyệt đối theo luật đề bài).
# - Chuỗi 4 mở 2 đầu (Live Four) = 10,000 điểm (Chắc chắn thắng ở lượt sau vì đối phương không thể chặn cả 2 đầu).
# - Chuỗi 4 mở 1 đầu (Dead Four) = 1,500 điểm (Bắt buộc đối phương phải chặn ngay lập tức).
# - Chuỗi 3 mở 2 đầu (Live Three) = 1,200 điểm (Đe dọa tạo Live Four ở lượt kế tiếp).
# - Chuỗi 3 mở 1 đầu (Dead Three) = 150 điểm.
# - Chuỗi 2 mở 2 đầu (Live Two) = 80 điểm.
# - Chuỗi 2 mở 1 đầu (Dead Two) = 15 điểm.
PATTERN_SCORES = {
    (5, 2): 100000,
    (5, 1): 100000,
    (5, 0): 100000,
    (4, 2): 10000,
    (4, 1): 1500,
    (4, 0): 0,      # Chuỗi 4 bị chặn kín cả 2 đầu không thể phát triển thành 5 ở vị trí đó
    (3, 2): 1200,
    (3, 1): 150,
    (3, 0): 0,
    (2, 2): 80,
    (2, 1): 15,
    (2, 0): 0,
    (1, 2): 5,
    (1, 1): 1,
    (1, 0): 0,
}


class Evaluator:
    """
    Lớp cung cấp hàm đánh giá trạng thái bàn cờ (Static Evaluation Function)
    và hàm chấm điểm ưu tiên cho từng nước đi ứng viên.
    """

    # [GHI CHÚ THIẾT KẾ]: Hệ số phòng thủ (DEFENSE_WEIGHT = 1.15)
    # Tại sao điểm của đối thủ lại nhân với 1.15?
    # Trả lời: Nếu cả mình và đối thủ đều có chuỗi 4 mở 1 đầu (hoặc chuỗi 3 mở 2 đầu) nhưng đang là lượt đối thủ
    # vừa tạo đe dọa, việc nhân hệ số 1.15 giúp AI ưu tiên chặn các mối đe dọa sát sườn của đối phương,
    # tránh việc mải tấn công chuỗi ngắn mà để đối phương tạo đủ 5 quân trước.
    DEFENSE_WEIGHT = 1.15

    @classmethod
    def evaluate_board(cls, board: Board, maximizing_player: int) -> float:
        """
        Đánh giá tổng thể trạng thái bàn cờ từ góc nhìn của `maximizing_player`.
        Công thức:
            Score(s) = Score_Player(maximizing_player) - DEFENSE_WEIGHT * Score_Player(-maximizing_player)
        """
        if board.winner is not None:
            if board.winner == maximizing_player:
                return 100000.0
            elif board.winner == -maximizing_player:
                return -100000.0
            else:
                return 0.0

        my_score = cls._evaluate_for_player(board, maximizing_player)
        opp_score = cls._evaluate_for_player(board, -maximizing_player)
        return float(my_score - cls.DEFENSE_WEIGHT * opp_score)

    @classmethod
    def _evaluate_for_player(cls, board: Board, player: int) -> int:
        """
        Quét toàn bộ 4 hướng trên bàn cờ để đếm các chuỗi quân liên tiếp của `player`
        và số đầu trống (0, 1, hoặc 2 đầu mở) của mỗi chuỗi.
        """
        total_score = 0
        size = board.size
        grid = board.grid
        center = size // 2

        for r in range(size):
            for c in range(size):
                if grid[r][c] != player:
                    continue

                # Điểm thưởng nhỏ khi chiếm khu vực trung tâm bàn cờ
                dist_to_center = max(abs(r - center), abs(c - center))
                total_score += max(0, 4 - dist_to_center)

                for dr, dc in DIRECTIONS:
                    # Để không đếm trùng một chuỗi nhiều lần:
                    # Chỉ bắt đầu đếm nếu ô ngay trước đó theo hướng (-dr, -dc) KHÔNG PHẢI là quân của cùng player
                    prev_r, prev_c = r - dr, c - dc
                    if 0 <= prev_r < size and 0 <= prev_c < size and grid[prev_r][prev_c] == player:
                        continue

                    # Đếm độ dài chuỗi liên tiếp theo hướng (+dr, +dc)
                    length = 0
                    curr_r, curr_c = r, c
                    while (
                        0 <= curr_r < size
                        and 0 <= curr_c < size
                        and grid[curr_r][curr_c] == player
                    ):
                        length += 1
                        curr_r += dr
                        curr_c += dc

                    # Nếu chuỗi >= 5 thì thắng tuyệt đối (kể cả bị chặn 2 đầu theo luật đề bài)
                    if length >= board.win_length:
                        return 100000

                    # Kiểm tra 2 đầu của chuỗi có trống (Open End) hay không
                    open_ends = 0
                    if 0 <= prev_r < size and 0 <= prev_c < size and grid[prev_r][prev_c] == EMPTY:
                        open_ends += 1
                    if 0 <= curr_r < size and 0 <= curr_c < size and grid[curr_r][curr_c] == EMPTY:
                        open_ends += 1

                    total_score += PATTERN_SCORES.get((length, open_ends), 0)

        return total_score

    @classmethod
    def score_move_quick(cls, board: Board, row: int, col: int, player: int) -> int:
        """
        Đánh giá nhanh mức độ quan trọng của một ô trống (row, col) trong thời gian O(1).
        Hàm này phục vụ 2 mục đích quan trọng:
        1. Sắp xếp thứ tự nước đi (Move Ordering) trong Alpha-Beta để cắt tỉa nhánh sớm nhất.
        2. Định hướng mô phỏng thông minh (Heuristic Rollout) trong Bài 2 Mở rộng.
        """
        size = board.size
        grid = board.grid
        center = size // 2
        # Điểm vị trí gần tâm bàn cờ
        positional_bonus = max(0, 4 - max(abs(row - center), abs(col - center)))

        attack_score = cls._point_pattern_score(grid, size, row, col, player)
        defend_score = cls._point_pattern_score(grid, size, row, col, -player)

        # Nếu nước đi giúp mình thắng ngay (>= 5 quân), ưu tiên tuyệt đối
        if attack_score >= 100000:
            return 1000000
        # Nếu nước đi chặn đối phương thắng ngay ở lượt sau, ưu tiên số 2
        if defend_score >= 100000:
            return 500000

        return attack_score + int(defend_score * 1.1) + positional_bonus

    @staticmethod
    def _point_pattern_score(
        grid: List[List[int]], size: int, row: int, col: int, player: int
    ) -> int:
        """
        Tính điểm giả định nếu đặt quân của `player` vào ô (row, col) theo 4 hướng.
        """
        score = 0
        for dr, dc in DIRECTIONS:
            count = 1
            open_ends = 0

            # Hướng dương (+dr, +dc)
            r, c = row + dr, col + dc
            while 0 <= r < size and 0 <= c < size and grid[r][c] == player:
                count += 1
                r += dr
                c += dc
            if 0 <= r < size and 0 <= c < size and grid[r][c] == EMPTY:
                open_ends += 1

            # Hướng âm (-dr, -dc)
            r, c = row - dr, col - dc
            while 0 <= r < size and 0 <= c < size and grid[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            if 0 <= r < size and 0 <= c < size and grid[r][c] == EMPTY:
                open_ends += 1

            if count >= 5:
                score += 100000
            else:
                score += PATTERN_SCORES.get((count, open_ends), 0)

        return score

    @classmethod
    def order_moves(
        cls,
        board: Board,
        moves: List[Tuple[int, int]],
        player: int,
        max_candidates: int = 16,
    ) -> List[Tuple[int, int]]:
        """
        Sắp xếp các nước đi ứng viên theo điểm giảm dần và giữ lại top `max_candidates` nước tốt nhất.
        Giúp cắt tỉa Alpha-Beta đạt hiệu suất cao nhất và tránh bùng nổ tổ hợp.
        """
        if len(moves) <= 1:
            return moves
        scored = [
            (cls.score_move_quick(board, r, c, player), (r, c))
            for r, c in moves
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        if max_candidates and len(scored) > max_candidates:
            scored = scored[:max_candidates]
        return [m for _, m in scored]
