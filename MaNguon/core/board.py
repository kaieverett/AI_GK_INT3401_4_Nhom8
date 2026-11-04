"""
File: core/board.py
Mô tả: Cài đặt bàn cờ Caro 9x9, quản lý luật chơi, kiểm tra điều kiện kết thúc ván
       và sinh danh sách nước đi ứng viên (Candidate Moves) giúp giảm hệ số phân nhánh.
"""

from typing import List, Optional, Tuple

# Quy ước hằng số biểu diễn trạng thái ô cờ
# [GHI CHÚ THIẾT KẾ]: Tại sao dùng 1 và -1 thay vì 1 và 2?
# Trả lời: Dùng 1 (X) và -1 (O) giúp đổi lượt người chơi cực nhanh chỉ bằng phép đảo dấu (-current_player),
# đồng thời rất thuận tiện cho hàm đánh giá đối xứng và lan truyền ngược trong MCTS.
EMPTY = 0
PLAYER_X = 1
PLAYER_O = -1

BOARD_SIZE = 9
WIN_LENGTH = 5

# 4 hướng kiểm tra thắng thua: Ngang, Dọc, Chéo chính (\), Chéo phụ (/)
DIRECTIONS = [
    (0, 1),   # Ngang (Horizontal)
    (1, 0),   # Dọc (Vertical)
    (1, 1),   # Chéo chính (Main Diagonal)
    (1, -1),  # Chéo phụ (Anti-Diagonal)
]


class Board:
    """
    Lớp biểu diễn trạng thái bàn cờ Caro kích thước 9x9.
    Luật chơi:
    - Hai người chơi X (1) và O (-1) lần lượt đánh vào ô trống (0).
    - Người chơi thắng khi tạo được ÍT NHẤT 05 quân liên tiếp (ngang, dọc, chéo).
    - Không áp dụng luật cấm nước đi (overline > 5 vẫn thắng) hoặc luật chặn hai đầu.
    - Hòa khi bàn cờ đầy (81 quân) mà chưa có ai thắng.
    """

    def __init__(self, size: int = BOARD_SIZE, win_length: int = WIN_LENGTH):
        self.size = size
        self.win_length = win_length
        # Ma trận 2 chiều lưu trạng thái bàn cờ
        self.grid: List[List[int]] = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.current_player: int = PLAYER_X
        self.move_history: List[Tuple[int, int]] = []
        self.winner: Optional[int] = None  # PLAYER_X (1), PLAYER_O (-1), 0 (Hòa), hoặc None (Chưa kết thúc)
        self.winning_line: List[Tuple[int, int]] = []

    def reset(self) -> None:
        """Khởi tạo lại bàn cờ về trạng thái rỗng ban đầu."""
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c] = EMPTY
        self.current_player = PLAYER_X
        self.move_history.clear()
        self.winner = None
        self.winning_line = []

    def clone(self) -> "Board":
        """
        Tạo bản sao độc lập của bàn cờ.
        [GHI CHÚ THIẾT KẾ]: Tại sao không dùng copy.deepcopy(self)?
        Trả lời: copy.deepcopy trong Python rất chậm (tốn nhiều thời gian khi MCTS mô phỏng hàng trăm lượt).
        Việc copy từng dòng [row[:] for row in self.grid] nhanh hơn gấp ~15 lần.
        """
        new_board = Board(self.size, self.win_length)
        new_board.grid = [row[:] for row in self.grid]
        new_board.current_player = self.current_player
        new_board.move_history = self.move_history[:]
        new_board.winner = self.winner
        new_board.winning_line = self.winning_line[:]
        return new_board

    def is_valid_move(self, row: int, col: int) -> bool:
        """Kiểm tra tọa độ (row, col) có nằm trong bàn cờ và đang trống hay không."""
        return (
            0 <= row < self.size
            and 0 <= col < self.size
            and self.grid[row][col] == EMPTY
        )

    def make_move(self, row: int, col: int, player: Optional[int] = None) -> bool:
        """
        Thực hiện đánh một quân cờ vào ô (row, col).
        Trả về True nếu nước đi hợp lệ, False nếu ô đã có quân hoặc ngoài bàn cờ.
        """
        if not self.is_valid_move(row, col) or self.winner is not None:
            return False

        p = player if player is not None else self.current_player
        self.grid[row][col] = p
        self.move_history.append((row, col))

        # Kiểm tra ngay xem nước đi vừa rồi có tạo thành >= 5 quân liên tiếp không
        if self._check_win_at(row, col, p):
            self.winner = p
        elif len(self.move_history) == self.size * self.size:
            self.winner = 0  # Hòa khi bàn cờ đầy

        # Đổi lượt người chơi kế tiếp
        self.current_player = -p
        return True

    def undo_move(self) -> Optional[Tuple[int, int]]:
        """
        Hoàn tác nước đi cuối cùng (Rất quan trọng cho đệ quy MiniMax để không phải copy bàn cờ).
        """
        if not self.move_history:
            return None
        row, col = self.move_history.pop()
        last_player = self.grid[row][col]
        self.grid[row][col] = EMPTY
        self.current_player = last_player
        self.winner = None
        self.winning_line = []
        return (row, col)

    def _check_win_at(self, row: int, col: int, player: int) -> bool:
        """
        [GHI CHÚ THIẾT KẾ]: Kiểm tra thắng thua cục bộ O(1) quanh nước đi vừa đánh (row, col).
        Tại sao chỉ kiểm tra quanh (row, col) mà không quét toàn bộ bàn cờ 9x9?
        Trả lời: Vì trước nước đi này ván cờ chưa kết thúc, nên nếu có chuỗi >= 5 quân mới xuất hiện
        thì chuỗi đó BẮT BUỘC phải đi qua ô (row, col) vừa đánh. Chỉ cần đếm dọc theo 4 hướng
        qua (row, col), giảm chi phí từ O(N^2) xuống O(1).
        """
        for dr, dc in DIRECTIONS:
            line = [(row, col)]
            # Đếm về phía dương (+dr, +dc)
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == player:
                line.append((r, c))
                r += dr
                c += dc

            # Đếm về phía âm (-dr, -dc)
            r, c = row - dr, col - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == player:
                line.insert(0, (r, c))
                r -= dr
                c -= dc

            # Luật chơi: Ít nhất 05 quân liên tiếp là thắng (không cấm >5, không xét chặn 2 đầu)
            if len(line) >= self.win_length:
                self.winning_line = line
                return True
        return False

    def check_full_board_winner(self) -> Optional[int]:
        """
        Quét toàn bộ bàn cờ để xác định người thắng (dùng khi giảng viên tự xếp thế cờ tùy chỉnh).
        """
        self.winner = None
        self.winning_line = []
        occupied_count = 0
        for r in range(self.size):
            for c in range(self.size):
                p = self.grid[r][c]
                if p != EMPTY:
                    occupied_count += 1
                    if self._check_win_at(r, c, p):
                        self.winner = p
                        return p
        if occupied_count == self.size * self.size:
            self.winner = 0
            return 0
        return None

    def is_game_over(self) -> bool:
        """Trả về True nếu ván cờ đã có kết quả (X thắng, O thắng, hoặc Hòa)."""
        return self.winner is not None

    def get_legal_moves(self) -> List[Tuple[int, int]]:
        """Trả về toàn bộ các ô trống hợp lệ trên bàn cờ."""
        return [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self.grid[r][c] == EMPTY
        ]

    def get_candidate_moves(self, radius: int = 1) -> List[Tuple[int, int]]:
        """
        [YÊU CẦU BÀI 1.2b & GHI CHÚ THIẾT KẾ]:
        Chiến lược giới hạn số nước đi ứng viên để tránh bùng nổ không gian tìm kiếm:
        - Nếu bàn cờ trống: đánh ngay vào tâm bàn cờ (4, 4).
        - Nếu đã có quân trên bàn cờ: chỉ xét các ô trống nằm trong bán kính Chebyshev <= radius
          (mặc định radius = 1 hoặc 2) xung quanh các quân cờ đã đánh.
        Ý nghĩa: Trong cờ Caro, đánh một quân cô lập ở góc xa không có giá trị tấn công hay phòng thủ.
        Giới hạn này thu hẹp nhánh tìm kiếm từ ~75 nước xuống chỉ còn 10-20 nước trọng tâm.
        """
        if not self.move_history:
            center = self.size // 2
            return [(center, center)]

        candidates = set()
        for r, c in self.move_history:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size and self.grid[nr][nc] == EMPTY:
                        candidates.add((nr, nc))

        # Dự phòng: nếu vì lý do nào đó tập ứng viên rỗng thì trả về mọi ô trống
        if not candidates:
            return self.get_legal_moves()

        # Sắp xếp ưu tiên các ô gần tâm bàn cờ hơn trước khi đánh giá sâu
        center = self.size // 2
        return sorted(
            list(candidates),
            key=lambda pos: abs(pos[0] - center) + abs(pos[1] - center),
        )

    def load_preset_state(self, preset_name: str) -> str:
        """
        Tải sẵn một số trạng thái cờ chuẩn phục vụ thực nghiệm cắt tỉa Alpha-Beta
        và phục vụ giảng viên kiểm tra trực tiếp khi vấn đáp.
        """
        self.reset()
        presets = {
            "khai_cuoc": {
                "desc": "Trạng thái 1: Khai cuộc (4 quân ở trung tâm)",
                "moves": [(4, 4), (4, 5), (3, 4), (3, 3)],
            },
            "trung_cuoc": {
                "desc": "Trạng thái 2: Trung cuộc giằng co (10 quân, nhiều hướng phát triển)",
                "moves": [
                    (4, 4), (4, 5),
                    (3, 4), (2, 4),
                    (5, 4), (6, 4),
                    (3, 5), (3, 3),
                    (4, 3), (5, 5),
                ],
            },
            "chan_chuoi_4": {
                "desc": "Trạng thái 3: Nguy cấp - Đối phương (X) đã có 4 quân liên tiếp bị chặn 1 đầu, O bắt buộc phải chặn tại (4, 6)",
                "moves": [
                    (4, 2), (4, 1),
                    (4, 3), (2, 2),
                    (4, 4), (2, 3),
                    (4, 5),  # X có 4 quân (4,2)..(4,5), đầu trái (4,1) đã bị O chặn -> O bắt buộc phải chặn đầu phải (4,6)!
                ],
            },
            "bay_doi_3_3": {
                "desc": "Trạng thái 4: Thế cờ phức tạp - Tạo nước đôi (Fork) đường ngang và đường chéo",
                "moves": [
                    (4, 4), (3, 4),
                    (4, 5), (3, 5),
                    (5, 3), (2, 6),
                    (3, 3), (6, 2),
                    (5, 5), (3, 6),
                ],
            },
        }
        info = presets.get(preset_name, presets["khai_cuoc"])
        for r, c in info["moves"]:
            self.make_move(r, c)
        return info["desc"]

    def to_ascii(self, last_move: Optional[Tuple[int, int]] = None) -> str:
        """Biểu diễn bàn cờ dạng chuỗi ASCII rõ đẹp cho chế độ CLI và ghi log."""
        lines = []
        header = "   " + " ".join(f"{c:2d}" for c in range(self.size))
        lines.append(header)
        lines.append("   " + "---" * self.size)
        for r in range(self.size):
            row_str = f"{r:2d}|"
            for c in range(self.size):
                val = self.grid[r][c]
                symbol = "."
                if val == PLAYER_X:
                    symbol = "X"
                elif val == PLAYER_O:
                    symbol = "O"
                if last_move and (r, c) == last_move:
                    row_str += f"[{symbol}]"
                else:
                    row_str += f" {symbol} "
            lines.append(row_str)
        return "\n".join(lines)

    @staticmethod
    def player_name(player: int) -> str:
        if player == PLAYER_X:
            return "X"
        if player == PLAYER_O:
            return "O"
        return "Hòa"
