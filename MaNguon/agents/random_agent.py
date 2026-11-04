"""
File: agents/random_agent.py
Mô tả: Tác nhân chọn nước đi hợp lệ ngẫu nhiên (Random Baseline) theo yêu cầu Bài 1.4a(i).
"""

import random
import time
from typing import Any, Dict, Optional, Tuple
from core.board import Board
from .base_agent import BaseAgent


class RandomAgent(BaseAgent):
    """
    Tác nhân chọn một ô trống hợp lệ bất kỳ trên bàn cờ với xác suất đồng đều.
    Dùng làm mốc cơ sở (Baseline) để đánh giá hiệu quả của MiniMax và MCTS.
    """

    def __init__(self, seed: Optional[int] = None):
        super().__init__(name="Random")
        self.rng = random.Random(seed)

    def get_move(self, board: Board) -> Tuple[int, int, Dict[str, Any]]:
        start_time = time.perf_counter()
        legal_moves = board.get_legal_moves()
        if not legal_moves:
            raise ValueError("Bàn cờ đã đầy, không còn nước đi hợp lệ.")

        chosen_move = self.rng.choice(legal_moves)
        elapsed = time.perf_counter() - start_time

        stats = {
            "agent": self.name,
            "move": chosen_move,
            "time_sec": round(elapsed, 6),
            "nodes_visited": 1,
            "depth": 0,
            "score": 0.0,
        }
        self.last_stats = stats
        return chosen_move[0], chosen_move[1], stats
