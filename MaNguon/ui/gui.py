"""
File: ui/gui.py
Mô tả: Giao diện đồ họa (GUI) sử dụng thư viện chuẩn Tkinter của Python.
       Hỗ trợ đầy đủ yêu cầu Demo & Vấn đáp trực tiếp (Mục IV.3 & VI):
       - Chế độ Người vs Máy, Máy vs Máy, Người vs Người.
       - Thay đổi trực tiếp tham số độ sâu d, hằng số khám phá c, số lượt mô phỏng iterations.
       - Chế độ "Xếp thế cờ tùy chỉnh" & "Tải thế cờ mẫu" để giảng viên kiểm tra tình huống bất kỳ.
       - Hiển thị thống kê trực tiếp và nhật ký suy luận từng nước đi.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple
from core.board import Board, EMPTY, PLAYER_X, PLAYER_O, BOARD_SIZE
from agents import BaseAgent, RandomAgent, MiniMaxAgent, MCTSAgent, MCTSHeuristicAgent


AGENT_OPTIONS = [
    "Người chơi (Human)",
    "MiniMax + Alpha-Beta (Bài 1.2)",
    "MiniMax thuần - Không cắt tỉa",
    "MCTS + UCT - Random Rollout (Bài 1.3)",
    "MCTS + Heuristic Rollout (Bài 2 Mở rộng)",
    "Random Agent (Ngẫu nhiên)",
]


class CaroGUI:
    """Lớp giao diện đồ họa chính cho trò chơi Caro 9x9."""

    CELL_SIZE = 56
    MARGIN = 40
    CANVAS_SIZE = MARGIN * 2 + CELL_SIZE * BOARD_SIZE

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Cờ Caro 9x9 - Trí Tuệ Nhân Tạo | Lớp INT3401 4 - Nhóm 8")
        self.root.resizable(False, False)

        self.board = Board()
        self.last_move: Optional[Tuple[int, int]] = None
        self.auto_play_running: bool = False
        self.after_id: Optional[str] = None
        self.edit_mode: tk.BooleanVar = tk.BooleanVar(value=False)

        self._build_ui()
        self._draw_board()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Khung bên trái: Bàn cờ 9x9
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, padx=(0, 12))

        self.status_label = ttk.Label(
            left_frame,
            text="Lượt hiện tại: Quân X (Đi trước)",
            font=("DejaVu Sans", 12, "bold"),
            foreground="#1a5fb4",
        )
        self.status_label.pack(pady=(0, 6))

        self.canvas = tk.Canvas(
            left_frame,
            width=self.CANVAS_SIZE,
            height=self.CANVAS_SIZE,
            bg="#f8ecd4",
            highlightthickness=2,
            highlightbackground="#8b5a2b",
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)

        # Khung bên phải: Bảng điều khiển & Nhật ký
        right_frame = ttk.Frame(main_frame, width=440)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 1. Chọn tác nhân X và O
        agent_box = ttk.LabelFrame(right_frame, text="1. Cấu hình Người chơi / Thuật toán AI", padding=8)
        agent_box.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(agent_box, text="Quân X (Đi trước):").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.var_agent_x = tk.StringVar(value=AGENT_OPTIONS[0])
        cb_x = ttk.Combobox(agent_box, textvariable=self.var_agent_x, values=AGENT_OPTIONS, state="readonly", width=34)
        cb_x.grid(row=0, column=1, padx=5, pady=3)
        cb_x.bind("<<ComboboxSelected>>", lambda _: self._trigger_ai_if_needed())

        ttk.Label(agent_box, text="Quân O (Đi sau):").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.var_agent_o = tk.StringVar(value=AGENT_OPTIONS[1])
        cb_o = ttk.Combobox(agent_box, textvariable=self.var_agent_o, values=AGENT_OPTIONS, state="readonly", width=34)
        cb_o.grid(row=1, column=1, padx=5, pady=3)
        cb_o.bind("<<ComboboxSelected>>", lambda _: self._trigger_ai_if_needed())

        # 2. Tham số thuật toán (d, c, iterations)
        param_box = ttk.LabelFrame(right_frame, text="2. Tham số Thuật toán (Thay đổi trực tiếp)", padding=8)
        param_box.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(param_box, text="Độ sâu MiniMax (d):").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.var_depth = tk.IntVar(value=2)
        sp_depth = ttk.Spinbox(param_box, from_=1, to=4, textvariable=self.var_depth, width=8)
        sp_depth.grid(row=0, column=1, sticky=tk.W, padx=5, pady=3)

        ttk.Label(param_box, text="Hệ số UCT (c):").grid(row=0, column=2, sticky=tk.W, padx=(10, 0), pady=3)
        self.var_c = tk.DoubleVar(value=1.4)
        cb_c = ttk.Combobox(param_box, textvariable=self.var_c, values=[0.5, 1.0, 1.4, 2.0], width=8)
        cb_c.grid(row=0, column=3, sticky=tk.W, padx=5, pady=3)

        ttk.Label(param_box, text="Số lượt MCTS (iter):").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.var_iter = tk.IntVar(value=300)
        cb_iter = ttk.Combobox(param_box, textvariable=self.var_iter, values=[100, 300, 500, 800], width=8)
        cb_iter.grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)

        ttk.Label(param_box, text="Quy tắc chọn MCTS:").grid(row=1, column=2, sticky=tk.W, padx=(10, 0), pady=3)
        self.var_mcts_policy = tk.StringVar(value="max_visits (N)")
        cb_pol = ttk.Combobox(
            param_box,
            textvariable=self.var_mcts_policy,
            values=["max_visits (N)", "max_win_rate (W/N)"],
            state="readonly",
            width=16,
        )
        cb_pol.grid(row=1, column=3, sticky=tk.W, padx=5, pady=3)

        # 3. Điều khiển trận đấu & Kiểm tra thế cờ
        ctrl_box = ttk.LabelFrame(right_frame, text="3. Điều khiển & Kiểm tra Trạng thái Cờ", padding=8)
        ctrl_box.pack(fill=tk.X, pady=(0, 8))

        btn_row1 = ttk.Frame(ctrl_box)
        btn_row1.pack(fill=tk.X, pady=2)
        ttk.Button(btn_row1, text="Ván mới (Reset)", command=self.new_game).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(btn_row1, text="AI Đi 1 Nước (Step)", command=self.step_ai_once).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(btn_row1, text="Hoàn tác (Undo)", command=self.undo_last_move).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        btn_row2 = ttk.Frame(ctrl_box)
        btn_row2.pack(fill=tk.X, pady=4)
        ttk.Label(btn_row2, text="Thế cờ mẫu:").pack(side=tk.LEFT, padx=2)
        self.var_preset = tk.StringVar(value="chan_chuoi_4")
        cb_preset = ttk.Combobox(
            btn_row2,
            textvariable=self.var_preset,
            values=["khai_cuoc", "trung_cuoc", "chan_chuoi_4", "bay_doi_3_3"],
            state="readonly",
            width=16,
        )
        cb_preset.pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row2, text="Tải thế cờ", command=self.load_selected_preset).pack(side=tk.LEFT, padx=2)

        chk_edit = ttk.Checkbutton(
            ctrl_box,
            text="Chế độ Xếp cờ tự do (Chuột trái: đặt X | Chuột phải: đặt O/Xóa)",
            variable=self.edit_mode,
        )
        chk_edit.pack(anchor=tk.W, pady=2)

        # 4. Bảng thống kê nước đi gần nhất
        stat_box = ttk.LabelFrame(right_frame, text="4. Thống kê Suy luận Nước đi Gần nhất", padding=8)
        stat_box.pack(fill=tk.X, pady=(0, 8))
        self.lbl_stat_summary = ttk.Label(
            stat_box,
            text="Chưa có nước đi của AI.",
            font=("DejaVu Sans Mono", 9),
            justify=tk.LEFT,
        )
        self.lbl_stat_summary.pack(anchor=tk.W)

        # 5. Nhật ký chi tiết (Log Box)
        log_box = ttk.LabelFrame(right_frame, text="5. Nhật ký Suy luận (Move & Pruning Log)", padding=6)
        log_box.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_box, height=12, width=52, font=("DejaVu Sans Mono", 9), state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_box, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_agent(self, selection_str: str) -> Optional[BaseAgent]:
        """Khởi tạo đối tượng Agent theo lựa chọn và tham số hiện hành trên GUI."""
        if selection_str == AGENT_OPTIONS[0]:
            return None  # Người chơi

        try:
            d = max(1, int(self.var_depth.get()))
        except Exception:
            d = 2
        try:
            c_val = max(0.05, float(self.var_c.get()))
        except Exception:
            c_val = 1.4
        try:
            iters = max(10, int(self.var_iter.get()))
        except Exception:
            iters = 300

        pol = (
            "max_win_rate"
            if "max_win_rate" in self.var_mcts_policy.get()
            else "max_visits"
        )

        if selection_str == AGENT_OPTIONS[1]:
            return MiniMaxAgent(depth=d, use_alpha_beta=True)
        elif selection_str == AGENT_OPTIONS[2]:
            return MiniMaxAgent(depth=d, use_alpha_beta=False)
        elif selection_str == AGENT_OPTIONS[3]:
            return MCTSAgent(iterations=iters, c=c_val, selection_policy=pol)
        elif selection_str == AGENT_OPTIONS[4]:
            return MCTSHeuristicAgent(iterations=iters, c=c_val, selection_policy=pol)
        else:
            return RandomAgent()

    def _log(self, message: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _draw_board(self) -> None:
        self.canvas.delete("all")
        m = self.MARGIN
        cs = self.CELL_SIZE
        n = BOARD_SIZE

        # Vẽ các ô lưới và chỉ số tọa độ 0..8
        for i in range(n):
            # Nhãn tọa độ
            x_center = m + i * cs + cs // 2
            y_center = m + i * cs + cs // 2
            self.canvas.create_text(x_center, m // 2, text=str(i), font=("DejaVu Sans", 10, "bold"), fill="#5c4033")
            self.canvas.create_text(m // 2, y_center, text=str(i), font=("DejaVu Sans", 10, "bold"), fill="#5c4033")

        for r in range(n):
            for c in range(n):
                x1 = m + c * cs
                y1 = m + r * cs
                x2 = x1 + cs
                y2 = y1 + cs

                bg_color = "#f8ecd4"
                if (r, c) in self.board.winning_line:
                    bg_color = "#b7f7c1"  # Tô xanh lá chuỗi 5 quân chiến thắng
                elif self.last_move == (r, c):
                    bg_color = "#ffe4a0"  # Tô vàng nhạt nước đi vừa đánh

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline="#8b5a2b", width=1.5)

                val = self.board.grid[r][c]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                if val == PLAYER_X:
                    # Vẽ quân X màu xanh đậm/đỏ
                    pad = 14
                    self.canvas.create_line(x1 + pad, y1 + pad, x2 - pad, y2 - pad, fill="#d93025", width=4, capstyle=tk.ROUND)
                    self.canvas.create_line(x1 + pad, y2 - pad, x2 - pad, y1 + pad, fill="#d93025", width=4, capstyle=tk.ROUND)
                elif val == PLAYER_O:
                    pad = 12
                    self.canvas.create_oval(x1 + pad, y1 + pad, x2 - pad, y2 - pad, outline="#1a73e8", width=4)

        # Cập nhật thanh trạng thái
        if self.board.is_game_over():
            if self.board.winner == PLAYER_X:
                self.status_label.config(text="KẾT QUẢ: NGƯỜI CHƠI X THẮNG (>= 5 quân)!", foreground="#d93025")
            elif self.board.winner == PLAYER_O:
                self.status_label.config(text="KẾT QUẢ: NGƯỜI CHƠI O THẮNG (>= 5 quân)!", foreground="#1a73e8")
            else:
                self.status_label.config(text="KẾT QUẢ: VÁN CỜ HÒA (Bàn cờ đầy)!", foreground="#5f6368")
        else:
            p = self.board.current_player
            p_str = "X (Đỏ)" if p == PLAYER_X else "O (Xanh)"
            color = "#d93025" if p == PLAYER_X else "#1a73e8"
            self.status_label.config(text=f"Lượt hiện tại: Quân {p_str} | Tổng số nước đã đi: {len(self.board.move_history)}", foreground=color)

    def _pixel_to_cell(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        c = (x - self.MARGIN) // self.CELL_SIZE
        r = (y - self.MARGIN) // self.CELL_SIZE
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            return int(r), int(c)
        return None

    def _on_left_click(self, event: tk.Event) -> None:
        cell = self._pixel_to_cell(event.x, event.y)
        if cell is None:
            return
        r, c = cell

        # Nếu đang ở chế độ Xếp thế cờ tự do (Sandbox Mode cho giảng viên)
        if self.edit_mode.get():
            self.board.grid[r][c] = PLAYER_X if self.board.grid[r][c] != PLAYER_X else EMPTY
            if (r, c) not in self.board.move_history and self.board.grid[r][c] != EMPTY:
                self.board.move_history.append((r, c))
            self._recompute_custom_board()
            return

        if self.board.is_game_over():
            return

        # Kiểm tra xem lượt hiện tại có phải là Người chơi hay không
        curr_sel = self.var_agent_x.get() if self.board.current_player == PLAYER_X else self.var_agent_o.get()
        if curr_sel != AGENT_OPTIONS[0]:
            return  # Đang là lượt của Máy

        if self.board.make_move(r, c):
            self.last_move = (r, c)
            p_moved = -self.board.current_player
            self._log(f"[Người chơi {Board.player_name(p_moved)}] Đánh ô ({r}, {c})")
            self._draw_board()
            self._trigger_ai_if_needed()

    def _on_right_click(self, event: tk.Event) -> None:
        """Chuột phải trong chế độ Xếp thế cờ: Đặt quân O hoặc xóa ô."""
        if not self.edit_mode.get():
            return
        cell = self._pixel_to_cell(event.x, event.y)
        if cell is None:
            return
        r, c = cell
        self.board.grid[r][c] = PLAYER_O if self.board.grid[r][c] != PLAYER_O else EMPTY
        if (r, c) not in self.board.move_history and self.board.grid[r][c] != EMPTY:
            self.board.move_history.append((r, c))
        self._recompute_custom_board()

    def _recompute_custom_board(self) -> None:
        """Cập nhật lại lượt đi và trạng thái thắng/thua khi xếp cờ tự do."""
        x_count = sum(row.count(PLAYER_X) for row in self.board.grid)
        o_count = sum(row.count(PLAYER_O) for row in self.board.grid)
        self.board.current_player = PLAYER_X if x_count <= o_count else PLAYER_O
        self.board.check_full_board_winner()
        self._draw_board()

    def _trigger_ai_if_needed(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        if self.edit_mode.get() or self.board.is_game_over():
            return

        curr_sel = self.var_agent_x.get() if self.board.current_player == PLAYER_X else self.var_agent_o.get()
        if curr_sel != AGENT_OPTIONS[0]:
            self.after_id = self.root.after(120, self._execute_ai_turn)

    def _execute_ai_turn(self) -> None:
        self.after_id = None
        if self.board.is_game_over():
            return

        curr_player = self.board.current_player
        curr_sel = self.var_agent_x.get() if curr_player == PLAYER_X else self.var_agent_o.get()
        agent = self._build_agent(curr_sel)
        if agent is None:
            return

        self.root.config(cursor="watch")
        self.root.update_idletasks()
        r, c, stats = agent.get_move(self.board)
        self.root.config(cursor="")

        self.board.make_move(r, c)
        self.last_move = (r, c)
        self._update_stats_panel(curr_player, stats)
        self._draw_board()

        if not self.board.is_game_over():
            self._trigger_ai_if_needed()

    def step_ai_once(self) -> None:
        """Ép AI đi ngay 1 nước cho trạng thái bàn cờ hiện tại (phục vụ giảng viên kiểm tra)."""
        if self.board.is_game_over():
            messagebox.showinfo("Thông báo", "Ván cờ đã kết thúc. Hãy bấm Ván mới hoặc Hoàn tác.")
            return
        self.edit_mode.set(False)
        curr_player = self.board.current_player
        curr_sel = self.var_agent_x.get() if curr_player == PLAYER_X else self.var_agent_o.get()
        agent = self._build_agent(curr_sel)
        if agent is None:
            # Nếu đang để là Người chơi nhưng bấm "AI Đi 1 Nước", mặc định gọi MiniMax Alpha-Beta
            agent = MiniMaxAgent(depth=max(1, int(self.var_depth.get())), use_alpha_beta=True)

        r, c, stats = agent.get_move(self.board)
        self.board.make_move(r, c)
        self.last_move = (r, c)
        self._update_stats_panel(curr_player, stats)
        self._draw_board()

    def _update_stats_panel(self, player: int, stats: dict) -> None:
        p_str = Board.player_name(player)
        agent_name = stats.get("agent", "AI")
        move = stats.get("move", (-1, -1))
        t_sec = stats.get("time_sec", 0.0)
        nodes = stats.get("nodes_visited", 0)

        if "pruned_branches" in stats:
            pruned = stats.get("pruned_branches", 0)
            depth = stats.get("depth", 2)
            score = stats.get("score", 0.0)
            summary = (
                f"Người chơi : Quân {p_str} ({agent_name})\n"
                f"Nước chọn  : Dòng {move[0]}, Cột {move[1]} | Độ sâu d = {depth}\n"
                f"Thời gian  : {t_sec * 1000:.2f} ms ({t_sec:.4f} s)\n"
                f"Số nút duyệt: {nodes:,} nút | Nhánh cắt tỉa: {pruned:,}\n"
                f"Điểm lượng giá: {score}"
            )
            log_line = (
                f"[{p_str}] {agent_name}: chọn {move} | d={depth} | "
                f"{t_sec*1000:.1f}ms | nút={nodes} | cắt={pruned} | điểm={score}"
            )
        elif "iterations" in stats:
            visits = stats.get("selected_visits", 0)
            wr = stats.get("selected_win_rate", 0.0) * 100
            c_val = stats.get("c", 1.4)
            iters = stats.get("iterations", 300)
            summary = (
                f"Người chơi : Quân {p_str} ({agent_name})\n"
                f"Nước chọn  : Dòng {move[0]}, Cột {move[1]} | c={c_val}, iter={iters}\n"
                f"Thời gian  : {t_sec * 1000:.2f} ms ({t_sec:.4f} s)\n"
                f"Số nút cây : {nodes:,} nút | Lượt thăm N lớn nhất: {visits}\n"
                f"Tỷ lệ thắng nhánh (W/N): {wr:.1f}%"
            )
            log_line = (
                f"[{p_str}] {agent_name}: chọn {move} | {t_sec*1000:.1f}ms | "
                f"N={visits}/{iters} | W/N={wr:.1f}%"
            )
        else:
            summary = (
                f"Người chơi : Quân {p_str} ({agent_name})\n"
                f"Nước chọn  : Dòng {move[0]}, Cột {move[1]}\n"
                f"Thời gian  : {t_sec * 1000:.2f} ms"
            )
            log_line = f"[{p_str}] {agent_name}: chọn {move} | {t_sec*1000:.2f}ms"

        self.lbl_stat_summary.config(text=summary)
        self._log(log_line)

    def new_game(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.board.reset()
        self.last_move = None
        self.edit_mode.set(False)
        self._log("-" * 52)
        self._log("Bắt đầu ván cờ mới trên bàn cờ 9x9.")
        self._draw_board()
        self._trigger_ai_if_needed()

    def undo_last_move(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        undone = self.board.undo_move()
        if undone:
            self.last_move = self.board.move_history[-1] if self.board.move_history else None
            self._log(f"[Hoàn tác] Đã rút lại nước đi tại {undone}")
            self._draw_board()

    def load_selected_preset(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        preset = self.var_preset.get()
        desc = self.board.load_preset_state(preset)
        self.last_move = self.board.move_history[-1] if self.board.move_history else None
        self._log("-" * 52)
        self._log(f"[Tải thế cờ mẫu] {desc}")
        self._draw_board()


def run_gui() -> None:
    root = tk.Tk()
    CaroGUI(root)
    root.mainloop()
