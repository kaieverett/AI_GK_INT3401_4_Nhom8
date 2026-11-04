# HƯỚNG DẪN CÀI ĐẶT, CHẠY CHƯƠNG TRÌNH, CẤU HÌNH THUẬT TOÁN VÀ TÁI LẬP THỰC NGHIỆM

- **Học phần:** Trí tuệ nhân tạo (Năm học 2026 - 2027)
- **Mã lớp học phần:** INT3401 4
- **Nhóm thực hiện:** Nhóm 8 (04 thành viên)
- **Đề tài:** Xây dựng tác nhân chơi cờ Caro 9x9 với thuật toán **MiniMax kết hợp cắt tỉa Alpha-Beta**, **Monte Carlo Tree Search (MCTS) kết hợp UCT**, và **Bài 2 Mở rộng (Hướng A): MCTS kết hợp Heuristic Rollout**.

---

## 1. HƯỚNG DẪN CÀI ĐẶT MÔI TRƯỜNG

Chương trình được viết bằng ngôn ngữ **Python 3** (tương thích hoàn toàn với Python 3.8 trở lên trên Windows, macOS và Linux).

### 1.1. Yêu cầu chạy Trò chơi (GUI & CLI) và Chạy Thực nghiệm (`--exp`)
- **Không cần cài đặt thư viện bên thứ ba:** Toàn bộ lõi trò chơi, thuật toán AI (`MiniMax`, `Alpha-Beta`, `MCTS + UCT`, `MCTS Heuristic`), giao diện đồ họa (`tkinter`) và bộ chạy thực nghiệm (`csv`, `json`) đều sử dụng **100% thư viện chuẩn (Standard Library)** đi kèm sẵn khi cài Python.
- Kiểm tra phiên bản Python trên máy:
  - Trên **Windows (Command Prompt / PowerShell):**
    ```bash
    python --version
    ```
  - Trên **Linux / macOS (Terminal):**
    ```bash
    python3 --version
    ```

### 1.2. Cài đặt thư viện vẽ đồ thị (Tùy chọn - chỉ cần nếu muốn xuất lại file ảnh PNG)
- Toàn bộ 5 biểu đồ PNG (300 DPI) và 5 bảng dữ liệu CSV đã được chạy sẵn và lưu trong thư mục `results/`. Nếu giảng viên muốn chạy lại lệnh vẽ biểu đồ từ file CSV/JSON, cài đặt `matplotlib` và `numpy` bằng lệnh:
  ```bash
  pip install -r requirements.txt
  ```

---

## 2. HƯỚNG DẪN CHẠY CHƯƠNG TRÌNH

Mở Terminal (hoặc Command Prompt) tại thư mục `MaNguon/` và thực hiện các lệnh sau (trên Windows có thể gõ `python` thay cho `python3`):

### 2.1. Chạy Giao diện Đồ họa Trực quan (Tkinter GUI - Mặc định)
```bash
python3 main.py
# Hoặc trên Windows:
python main.py
```
- Giao diện hiển thị bàn cờ Caro 9x9 rõ nét, đánh dấu tọa độ dòng/cột `0..8`, tô sáng nước đi vừa đánh và tô xanh chuỗi 5 quân chiến thắng.
- Hỗ trợ đầy đủ chế độ **Người đấu với Máy**, **Máy đấu với Máy** và **Người đấu với Người**.

### 2.2. Chạy Giao diện Dòng lệnh (CLI)
```bash
python3 main.py --cli
# Hoặc trên Windows:
python main.py --cli
```
- Menu tương tác trực tiếp trên dòng lệnh gồm:
  - `Phím 1`: Người đấu với Máy (chọn cầm quân X đi trước hoặc quân O đi sau).
  - `Phím 2`: Máy đấu với Máy (chọn bất kỳ 2 thuật toán nào đối đầu nhau).
  - `Phím 3`: Kiểm tra và đối sánh trực tiếp giữa **MiniMax không cắt tỉa** và **MiniMax có cắt tỉa Alpha-Beta** trên 4 trạng thái bàn cờ mẫu ở độ sâu `d = 2` và `d = 3`.

---

## 3. HƯỚNG DẪN CẤU HÌNH THUẬT TOÁN & KIỂM TRA TRẠNG THÁI CỜ

### 3.1. Cấu hình trực tiếp trên Giao diện Đồ họa (GUI)
Ngay tại khung điều khiển bên phải của cửa sổ GUI, người dùng/giảng viên có thể thay đổi trực tiếp mà không cần khởi động lại chương trình:
1. **Chọn thuật toán cho Quân X (Đi trước) và Quân O (Đi sau):**
   - `Người chơi (Human)`
   - `MiniMax + Alpha-Beta (Bài 1.2)`
   - `MiniMax thuần - Không cắt tỉa` *(dùng để đối sánh số nút duyệt và thời gian với bản có cắt tỉa)*
   - `MCTS + UCT - Random Rollout (Bài 1.3)`
   - `MCTS + Heuristic Rollout (Bài 2 Mở rộng)`
   - `Random Agent (Ngẫu nhiên)`
2. **Thay đổi các siêu tham số (Hyperparameters):**
   - **Độ sâu MiniMax (`d`):** Chỉnh trực tiếp tại ô Spinbox (`d = 1, 2, 3, 4`, mặc định `d = 2`).
   - **Hệ số khám phá UCT (`c`):** Chọn hoặc nhập giá trị bất kỳ (`0.5, 1.0, 1.4, 2.0`, mặc định `c = 1.4`).
   - **Số lượt mô phỏng MCTS (`iter`):** Chọn hoặc nhập số lượt (`100, 300, 500, 800`, mặc định `300`).
   - **Quy tắc chọn nước đi cuối của MCTS:** Mặc định `max_visits (N)` (chọn nút con có số lượt thăm lớn nhất); có thể đổi sang `max_win_rate (W/N)` để kiểm nghiệm sự khác biệt.
3. **Kiểm tra trạng thái bàn cờ bất kỳ (Dành cho Giảng viên kiểm tra trực tiếp):**
   - **Tải thế cờ mẫu:** Chọn một trong 4 trạng thái (`khai_cuoc`, `trung_cuoc`, `chan_chuoi_4`, `bay_doi_3_3`) -> bấm **Tải thế cờ** -> bấm **AI Đi 1 Nước (Step)** để xem nước đi AI chọn và bảng thống kê chi tiết.
   - **Xếp thế cờ tự do (Sandbox Mode):** Tích vào ô *"Chế độ Xếp cờ tự do"*, dùng **Chuột trái** click lên bàn cờ để đặt quân X, **Chuột phải** để đặt quân O (hoặc xóa ô). Sau khi xếp xong thế cờ, bỏ tích và bấm **AI Đi 1 Nước (Step)**.

### 3.2. Cấu hình trong Mã nguồn (Nếu muốn chỉnh sâu hơn khi Vấn đáp)
- **Đổi kích thước bàn cờ hoặc số quân liên tiếp để thắng:** Mở tệp `core/board.py` (dòng 16-17: `BOARD_SIZE = 9`, `WIN_LENGTH = 5`).
- **Đổi bảng trọng số mẫu hình và hệ số phòng thủ của MiniMax:** Mở tệp `core/evaluator.py` (dòng 19 `PATTERN_SCORES` và dòng 47 `DEFENSE_WEIGHT = 1.15`).
- **Đổi quy ước phần thưởng Thắng / Hòa / Thua của MCTS:** Mở tệp `agents/mcts_agent.py` (dòng 94-96: `REWARD_WIN = 1.0`, `REWARD_DRAW = 0.5`, `REWARD_LOSS = 0.0`).

---

## 4. HƯỚNG DẪN TÁI LẬP THỰC NGHIỆM & DỮ LIỆU KẾT QUẢ

Toàn bộ thực nghiệm trong Báo cáo được cố định hạt giống ngẫu nhiên `RANDOM_SEED = 2026` trong tệp `experiments/run_experiments.py`. Mỗi cấu hình chạy đúng **20 ván (10 cặp ván hoán đổi người đi trước X và đi sau O)**.

### 4.1. Lệnh chạy lại toàn bộ thực nghiệm
```bash
python3 main.py --exp
# Hoặc chạy trực tiếp:
python3 experiments/run_experiments.py
```

### 4.2. Lệnh vẽ lại 05 biểu đồ PNG (300 DPI)
```bash
python3 main.py --plot
# Hoặc chạy trực tiếp:
python3 experiments/plot_charts.py
```

### 4.3. Danh mục Dữ liệu & Kết quả Thực nghiệm đính kèm (`results/`)
- `results/exp1_head_to_head.csv`: Bảng kết quả đối sánh trực tiếp giữa `Random`, `MiniMax + Alpha-Beta`, `MCTS + UCT Cơ sở` và `MCTS + Heuristic Rollout [Bài 2]`.
- `results/exp2_c_sensitivity.csv`: Bảng kết quả khảo sát tham số `c ∈ {0.5, 1.0, 1.4, 2.0}` với `iterations = 300` cố định.
- `results/exp3_iter_sensitivity.csv`: Bảng kết quả khảo sát số `iteration ∈ {100, 300, 500}` với `c = 1.4` cố định.
- `results/exp4_alphabeta_pruning.csv`: Bảng đối sánh số nút duyệt, số nhánh cắt tỉa và thời gian suy luận giữa MiniMax thuần và MiniMax Alpha-Beta trên 4 trạng thái thử nghiệm (`d = 2, 3`).
- `results/exp5_bai2_rollout.csv`: Bảng kết quả đối sánh Bài 2 Mở rộng (`Heuristic Rollout` vs `Random Rollout`).
- `results/experiment_summary.json`: Tệp JSON tổng hợp toàn bộ thông số cấu hình máy tính, hạt giống ngẫu nhiên và kết quả chi tiết.
- `results/charts/*.png`: Bộ 05 biểu đồ phân tích chất lượng cao (300 DPI) đã nhúng trong Báo cáo và Slide.

---

## 5. CẤU TRÚC TỔNG THỂ THƯ MỤC MÃ NGUỒN (`MaNguon/`)

```text
MaNguon/
├── main.py                               # Điểm khởi chạy chính (GUI / --cli / --exp / --plot)
├── README.md                             # Tài liệu hướng dẫn cài đặt, chạy, cấu hình và tái lập
├── requirements.txt                      # Danh sách thư viện tùy chọn khi vẽ lại đồ thị
├── core/
│   ├── __init__.py
│   ├── board.py                          # Quản lý bàn cờ 9x9, kiểm tra thắng >= 5 quân O(1), Candidate Moves
│   └── evaluator.py                      # Hàm đánh giá trạng thái (Heuristic Evaluation) & Move Ordering
├── agents/
│   ├── __init__.py
│   ├── base_agent.py                     # Giao diện tác nhân chuẩn (BaseAgent)
│   ├── random_agent.py                   # Tác nhân chọn nước hợp lệ ngẫu nhiên (Baseline)
│   ├── minimax_agent.py                  # MiniMax + Cắt tỉa Alpha-Beta (Bài 1.2)
│   ├── mcts_agent.py                     # MCTS + UCT chuẩn 4 giai đoạn với Random Rollout (Bài 1.3)
│   └── mcts_heuristic_agent.py           # MCTS + UCT cải tiến với Heuristic Rollout (Bài 2 - Hướng A)
├── ui/
│   ├── __init__.py
│   ├── gui.py                            # Giao diện đồ họa Tkinter trực quan
│   └── cli.py                            # Giao diện dòng lệnh tương tác
├── experiments/
│   ├── __init__.py
│   ├── run_experiments.py                # Kịch bản tự động chạy thực nghiệm đối sánh (SEED = 2026)
│   ├── plot_charts.py                    # Kịch bản xuất 05 biểu đồ PNG (300 DPI)
│   └── build_report_and_slides.py        # Kịch bản tự động biên dịch Báo cáo PDF và Slide PDF/PPTX
└── results/                              # Dữ liệu CSV, JSON và biểu đồ thực nghiệm
```
