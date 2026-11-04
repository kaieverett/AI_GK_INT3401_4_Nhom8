"""
Module core: Quản lý trạng thái bàn cờ Caro 9x9 và hàm lượng giá (Heuristic Evaluation).
Học phần: Trí tuệ nhân tạo - Mã lớp: INT3401 4 - Nhóm 8
"""

from .board import Board, EMPTY, PLAYER_X, PLAYER_O, BOARD_SIZE, WIN_LENGTH
from .evaluator import Evaluator

__all__ = [
    "Board",
    "Evaluator",
    "EMPTY",
    "PLAYER_X",
    "PLAYER_O",
    "BOARD_SIZE",
    "WIN_LENGTH",
]
