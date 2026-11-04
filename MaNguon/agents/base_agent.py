"""
File: agents/base_agent.py
Mô tả: Lớp cơ sở trừu tượng (Abstract Base Class) định nghĩa Hợp đồng Giao tiếp (API Contract)
       chung cho toàn bộ các tác nhân chơi cờ trong hệ thống.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
from core.board import Board


class BaseAgent(ABC):
    """
    Lớp cơ sở cho mọi tác nhân AI.
    Mọi Agent con bắt buộc cài đặt phương thức `get_move(board)` trả về:
        (row, col, stats_dict)
    """

    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        self.last_stats: Dict[str, Any] = {}

    @abstractmethod
    def get_move(self, board: Board) -> Tuple[int, int, Dict[str, Any]]:
        """
        Tính toán và trả về nước đi tiếp theo cho trạng thái `board` hiện tại.
        Returns:
            row (int): Chỉ số dòng (0..8)
            col (int): Chỉ số cột (0..8)
            stats (dict): Thống kê suy luận (thời gian, số nút đã duyệt, độ sâu, điểm số...)
        """
        pass
