"""
File: agents/mcts_agent.py
Mô tả: Cài đặt thuật toán Monte Carlo Tree Search (MCTS) kết hợp công thức UCT (Bài 1.3).
       Tách biệt rõ ràng 4 giai đoạn:
       1. Selection (Lựa chọn)
       2. Expansion (Mở rộng)
       3. Simulation / Rollout (Mô phỏng ngẫu nhiên)
       4. Backpropagation (Lan truyền ngược)
"""

import math
import random
import time
from typing import Any, Dict, List, Optional, Tuple
from core.board import Board
from .base_agent import BaseAgent


class MCTSNode:
    """
    Lớp biểu diễn một nút (Node) trong cây tìm kiếm Monte Carlo (MCTS).

    [GHI CHÚ THIẾT KẾ - QUY ƯỚC GÓC NHÌN NGƯỜI CHƠI (Bài 1.3c)]:
    - `player_just_moved`: Người chơi vừa thực hiện nước đi `move` để tạo ra nút này.
    - `wins` (W_i): Tổng phần thưởng tích lũy tính theo góc nhìn của `player_just_moved`.
      + Thắng = +1.0
      + Hòa   = +0.5
      + Thua  = +0.0
    - Tại sao lưu `wins` theo góc nhìn của `player_just_moved`?
      Vì ở nút cha (Parent), người đang đến lượt phải chọn nước đi tiếp theo chính là
      `player_just_moved` của các nút con (Child)! Nhờ vậy, khi nút cha tính công thức UCT
      cho các nút con, tỉ số (W_i / N_i) chính là tỷ lệ thắng thuận chiều của người chơi tại nút cha,
      không bao giờ bị ngược dấu giữa X và O!
    """

    def __init__(
        self,
        move: Optional[Tuple[int, int]] = None,
        parent: Optional["MCTSNode"] = None,
        player_just_moved: int = -1,
        untried_moves: Optional[List[Tuple[int, int]]] = None,
    ):
        self.move = move
        self.parent = parent
        self.player_just_moved = player_just_moved
        self.children: List["MCTSNode"] = []
        self.wins: float = 0.0
        self.visits: int = 0
        self.untried_moves: List[Tuple[int, int]] = (
            untried_moves[:] if untried_moves is not None else []
        )

    def is_fully_expanded(self) -> bool:
        """Kiểm tra nút đã mở rộng hết tất cả các nước đi ứng viên hay chưa."""
        return len(self.untried_moves) == 0

    def is_leaf(self) -> bool:
        """Kiểm tra nút có phải là nút lá (chưa có nút con nào) hay không."""
        return len(self.children) == 0

    def get_uct_score(self, c: float) -> float:
        """
        [YÊU CẦU BÀI 1.3b]: Tính chỉ số UCT (Upper Confidence Bound 1 applied to Trees):
            UCT(i) = (W_i / N_i) + c * sqrt(ln(N_p) / N_i)
        Trong đó:
        - W_i (`self.wins`): Tổng phần thưởng của nút con i.
        - N_i (`self.visits`): Số lượt thăm nút con i.
        - N_p (`self.parent.visits`): Số lượt thăm nút cha.
        - c > 0: Hằng số điều khiển cân bằng Khai thác (Exploitation) - Khám phá (Exploration).

        [XỬ LÝ NÚT CHƯA TỪNG THĂM (N_i == 0)]:
        - Nếu `self.visits == 0`, trả về `float('inf')` (vô cùng lớn) để ưu tiên khám phá tuyệt đối
          và tuyệt đối không xảy ra lỗi chia cho 0 (ZeroDivisionError).
        """
        if self.visits == 0:
            return float("inf")

        parent_visits = self.parent.visits if self.parent and self.parent.visits > 0 else 1
        exploitation = self.wins / self.visits
        exploration = c * math.sqrt(math.log(parent_visits) / self.visits)
        return exploitation + exploration

    def select_best_child_uct(self, c: float) -> "MCTSNode":
        """Chọn nút con có chỉ số UCT lớn nhất."""
        return max(self.children, key=lambda child: child.get_uct_score(c))


class MCTSAgent(BaseAgent):
    """
    Tác nhân Monte Carlo Tree Search kết hợp UCT (Bài 1.3).

    Quy ước phần thưởng (Reward Convention - Bài 1.3c):
    - Thắng (Winner == player_just_moved): +1.0
    - Hòa   (Winner == 0)                : +0.5
    - Thua  (Winner == -player_just_moved): +0.0

    Quy tắc chọn nước đi cuối cùng (Bài 1.3d):
    - Mặc định chọn nút con có số lượt thăm `N` lớn nhất (`selection_policy="max_visits"` - Robust Child).
    - Lý giải tại sao chọn theo `N` lớn nhất thay vì `W/N` lớn nhất:
      Một nhánh có thể đạt tỷ lệ `W/N = 1/1 = 100%` chỉ vì may mắn thắng 1 lần mô phỏng ngẫu nhiên ở những lượt cuối
      (nhiễu phương sai lớn do mẫu quá nhỏ). Ngược lại, nút có `N` lớn nhất là nút đã được công thức UCT kiểm chứng
      và quay lại thăm nhiều lần nhất, đảm bảo cả tỷ lệ thắng cao lẫn độ tin cậy thống kê (Robustness).
    """

    REWARD_WIN = 1.0
    REWARD_DRAW = 0.5
    REWARD_LOSS = 0.0

    def __init__(
        self,
        iterations: int = 300,
        c: float = 1.4,
        candidate_radius: int = 2,
        selection_policy: str = "max_visits",
        seed: Optional[int] = None,
    ):
        super().__init__(name=f"MCTS(c={c}, iter={iterations})")
        self.iterations = max(1, iterations)
        self.c = float(c)
        self.candidate_radius = candidate_radius
        self.selection_policy = selection_policy  # "max_visits" (N) hoặc "max_win_rate" (W/N)
        self.rng = random.Random(seed)

    def _get_expandable_moves(self, board: Board) -> List[Tuple[int, int]]:
        """Lấy danh sách nước đi ứng viên để mở rộng cây tìm kiếm."""
        if self.candidate_radius is not None and self.candidate_radius > 0:
            moves = board.get_candidate_moves(radius=self.candidate_radius)
        else:
            moves = board.get_legal_moves()
        self.rng.shuffle(moves)
        return moves

    def get_move(self, board: Board) -> Tuple[int, int, Dict[str, Any]]:
        """
        Thực thi `self.iterations` chu trình 4 bước của MCTS và trả về nước đi tốt nhất.
        """
        start_time = time.perf_counter()
        root_moves = self._get_expandable_moves(board)
        if not root_moves:
            raise ValueError("Bàn cờ đã đầy, không còn nước đi hợp lệ.")

        if len(root_moves) == 1:
            chosen = root_moves[0]
            elapsed = time.perf_counter() - start_time
            stats = {
                "agent": self.name,
                "move": chosen,
                "iterations": self.iterations,
                "c": self.c,
                "time_sec": round(elapsed, 6),
                "nodes_visited": 1,
                "selected_visits": 1,
                "selected_win_rate": 0.5,
            }
            self.last_stats = stats
            return chosen[0], chosen[1], stats

        # Khởi tạo nút gốc (Root Node)
        root = MCTSNode(
            move=None,
            parent=None,
            player_just_moved=-board.current_player,
            untried_moves=root_moves,
        )

        total_nodes_created = 1

        # Vòng lặp chính của MCTS qua `iterations` lượt mô phỏng
        for _ in range(self.iterations):
            sim_board = board.clone()

            # GIAI ĐOẠN 1: SELECTION (Lựa chọn)
            node = self._select(root, sim_board)

            # GIAI ĐOẠN 2: EXPANSION (Mở rộng)
            if not sim_board.is_game_over() and not node.is_fully_expanded():
                node = self._expand(node, sim_board)
                total_nodes_created += 1

            # GIAI ĐOẠN 3: SIMULATION / ROLLOUT (Mô phỏng)
            winner = self._simulate(sim_board)

            # GIAI ĐOẠN 4: BACKPROPAGATION (Lan truyền ngược)
            self._backpropagate(node, winner)

        # Chọn nước đi cuối cùng sau khi kết thúc các iteration (Bài 1.3d)
        if self.selection_policy == "max_win_rate":
            best_child = max(
                root.children,
                key=lambda ch: (ch.wins / ch.visits) if ch.visits > 0 else -1.0,
            )
        else:
            # Mặc định: Chọn theo số lượt thăm N lớn nhất (nếu bằng nhau thì xét tiếp W/N)
            best_child = max(
                root.children,
                key=lambda ch: (ch.visits, (ch.wins / ch.visits) if ch.visits > 0 else 0.0),
            )

        chosen_move = best_child.move
        win_rate = (best_child.wins / best_child.visits) if best_child.visits > 0 else 0.0
        elapsed = time.perf_counter() - start_time

        stats = {
            "agent": self.name,
            "move": chosen_move,
            "iterations": self.iterations,
            "c": self.c,
            "time_sec": round(elapsed, 6),
            "nodes_visited": total_nodes_created,
            "selected_visits": best_child.visits,
            "selected_wins": round(best_child.wins, 2),
            "selected_win_rate": round(win_rate, 4),
            "score": round(win_rate * 100, 1),
        }
        self.last_stats = stats
        return chosen_move[0], chosen_move[1], stats

    # =========================================================================
    # BỐN GIAI ĐOẠN CỐT LÕI CỦA MCTS (Bài 1.3a)
    # =========================================================================

    def _select(self, node: MCTSNode, sim_board: Board) -> MCTSNode:
        """
        Giai đoạn 1 - Selection (Lựa chọn):
        Đi từ nút gốc xuống theo chỉ số UCT lớn nhất cho đến khi gặp một nút chưa mở rộng hết
        (còn `untried_moves`) hoặc trạng thái kết thúc ván cờ.
        """
        while not sim_board.is_game_over() and node.is_fully_expanded() and node.children:
            node = node.select_best_child_uct(self.c)
            sim_board.make_move(node.move[0], node.move[1])
        return node

    def _expand(self, node: MCTSNode, sim_board: Board) -> MCTSNode:
        """
        Giai đoạn 2 - Expansion (Mở rộng):
        Lấy một nước đi chưa thử từ `node.untried_moves`, tạo nút con mới,
        gắn vào cây tìm kiếm và cập nhật trạng thái `sim_board`.
        """
        move = node.untried_moves.pop()
        mover = sim_board.current_player
        sim_board.make_move(move[0], move[1], mover)

        child_untried = (
            [] if sim_board.is_game_over() else self._get_expandable_moves(sim_board)
        )
        child_node = MCTSNode(
            move=move,
            parent=node,
            player_just_moved=mover,
            untried_moves=child_untried,
        )
        node.children.append(child_node)
        return child_node

    def _simulate(self, sim_board: Board) -> int:
        """
        Giai đoạn 3 - Simulation / Rollout (Mô phỏng ngẫu nhiên):
        Từ trạng thái nút vừa mở rộng, hai bên thực hiện các nước đi ngẫu nhiên
        cho đến khi ván cờ kết thúc (Thắng / Thua / Hòa).
        Trả về người chiến thắng: PLAYER_X (1), PLAYER_O (-1), hoặc Hòa (0).
        """
        if sim_board.is_game_over():
            return sim_board.winner if sim_board.winner is not None else 0

        empty_cells = sim_board.get_legal_moves()
        self.rng.shuffle(empty_cells)

        for r, c in empty_cells:
            sim_board.make_move(r, c)
            if sim_board.is_game_over():
                break

        return sim_board.winner if sim_board.winner is not None else 0

    def _backpropagate(self, node: Optional[MCTSNode], winner: int) -> None:
        """
        Giai đoạn 4 - Backpropagation (Lan truyền ngược):
        Đi ngược từ nút vừa mở rộng lên tới nút gốc (Root), cập nhật:
        - Số lượt thăm `visits += 1`
        - Tổng phần thưởng `wins` theo góc nhìn của `node.player_just_moved`:
          + Thắng: +1.0
          + Hòa  : +0.5
          + Thua : +0.0
        """
        curr = node
        while curr is not None:
            curr.visits += 1
            if winner == 0:
                curr.wins += self.REWARD_DRAW
            elif winner == curr.player_just_moved:
                curr.wins += self.REWARD_WIN
            else:
                curr.wins += self.REWARD_LOSS
            curr = curr.parent
