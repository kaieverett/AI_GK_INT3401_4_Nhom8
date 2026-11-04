# Bài Tập Lớn Giữa Kỳ: Cờ Caro 9×9 AI (MiniMax Alpha-Beta & MCTS UCT)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Course: AI](https://img.shields.io/badge/Course-INT3401_4-orange.svg)](https://uet.vnu.edu.vn/)

Dự án Bài tập lớn - Kiểm tra giữa kỳ môn **Trí tuệ nhân tạo (Học kỳ I, Năm học 2026 - 2027)**  
- **Mã lớp học phần:** INT3401 4  
- **Nhóm thực hiện:** Nhóm 8 (04 thành viên)  
- **Chủ đề:** Xây dựng tác nhân chơi cờ Caro trên bàn cờ 9×9 sử dụng thuật toán **MiniMax kết hợp cắt tỉa Alpha-Beta**, **Monte Carlo Tree Search (MCTS) kết hợp UCT**, và **Bài 2 Mở rộng (Hướng A): MCTS với Epsilon-Greedy Heuristic Rollout**.

---

## 📌 Mục lục
- [1. Giới thiệu Bài toán](#1-giới-thiệu-bài-toán)
- [2. Cấu trúc Thư mục](#2-cấu-trúc-thư-mục)
- [3. Các Thuật toán Cốt lõi](#3-các-thuật-toán-cốt-lõi)
- [4. Cài đặt & Hướng dẫn Chạy](#4-cài-đặt--hướng-dẫn-chạy)
- [5. Kết quả Thực nghiệm](#5-kết-quả-thực-nghiệm)
- [6. Bảng Phân công Nhóm](#6-bảng-phân-công-nhóm)

---

## 1. Giới thiệu Bài toán

Trò chơi cờ Caro trên bàn cờ kích thước **9 × 9** (81 ô):
- **Người chơi:** Quân **X** (đi trước, biểu diễn `+1`) và Quân **O** (đi sau, biểu diễn `-1`).
- **Luật thắng:** Người chơi tạo được **ít nhất 05 quân liên tiếp** (ngang, dọc, chéo chính, chéo phụ) sẽ thắng ngay lập tức. Không áp dụng luật cấm quá 5 quân (overline) và không xét luật chặn 2 đầu.
- **Hòa:** Khi bàn cờ đầy 81 ô mà không có người chiến thắng.
- **Tối ưu hóa:** Kiểm tra thắng cục bộ $O(1)$ quanh nước đi vừa đánh; Lọc nước đi ứng viên lân cận (Candidate Moves) theo bán kính Chebyshev để tránh bùng nổ không gian trạng thái.

---

## 2. Cấu trúc Thư mục

```text
.
├── BaoCao/
│   └── BaoCao_BTL_AI_INT3401_4_Nhom8.pdf     # Báo cáo kỹ thuật 19 trang chuẩn A4
├── Slide/
│   ├── Slide_BTL_AI_INT3401_4_Nhom8.pdf      # Slide trình chiếu 16:9 PDF
│   └── Slide_BTL_AI_INT3401_4_Nhom8.pptx     # Slide trình chiếu PPTX
├── MaNguon/
│   ├── main.py                               # Điểm khởi chạy chính (GUI / CLI / Thực nghiệm)
│   ├── README.md                             # Hướng dẫn chi tiết mã nguồn
│   ├── requirements.txt                      # Thư viện tùy chọn (vẽ biểu đồ)
│   ├── core/
│   │   ├── board.py                          # Lõi bàn cờ 9x9, kiểm tra thắng O(1), Candidate Moves
│   │   └── evaluator.py                      # Hàm đánh giá mẫu hình chuỗi quân & Move Ordering
│   ├── agents/
│   │   ├── base_agent.py                     # Lớp cơ sở trừu tượng BaseAgent
│   │   ├── random_agent.py                   # Tác nhân ngẫu nhiên (Baseline)
│   │   ├── minimax_agent.py                  # MiniMax + Cắt tỉa Alpha-Beta (Bài 1.2)
│   │   ├── mcts_agent.py                     # MCTS + UCT 4 giai đoạn chuẩn (Bài 1.3)
│   │   └── mcts_heuristic_agent.py           # MCTS + Heuristic Rollout (Bài 2 Mở rộng - Hướng A)
│   ├── ui/
│   │   ├── gui.py                            # Giao diện đồ họa Tkinter tương tác
│   │   └── cli.py                            # Giao diện dòng lệnh CLI
│   ├── experiments/
│   │   ├── run_experiments.py                # Kịch bản chạy thực nghiệm đối sánh (SEED = 2026)
│   │   ├── plot_charts.py                    # Script vẽ 5 biểu đồ PNG (300 DPI)
│   │   └── build_report_and_slides.py        # Pipeline xuất Báo cáo PDF và Slide
│   └── results/                              # 5 bảng CSV, 1 JSON và 5 biểu đồ PNG
└── README.md
```

---

## 3. Các Thuật toán Cốt lõi

1. **MiniMax kết hợp Cắt tỉa Alpha-Beta (`agents/minimax_agent.py`):**
   - Hỗ trợ tùy chỉnh độ sâu $d \ge 1$.
   - Tích hợp **Move Ordering** xếp các nước đi tiềm năng lên đầu giúp điều kiện $\beta \le \alpha$ kích hoạt sớm nhất.
   - Giảm **88.8% - 97.9%** số nút phải duyệt ở độ sâu $d = 3$ so với MiniMax thuần.

2. **Monte Carlo Tree Search + UCT (`agents/mcts_agent.py`):**
   - Đầy đủ 4 giai đoạn: **Selection**, **Expansion**, **Simulation**, **Backpropagation**.
   - Công thức UCT: $\text{UCT}(i) = \frac{W_i}{N_i} + c \sqrt{\frac{\ln N_p}{N_i}}$.
   - Xử lý nút chưa thăm ($N_i = 0$) ưu tiên khám phá, không chia cho 0.
   - Nhất quán góc nhìn người chơi qua `player_just_moved`; chọn nước đi cuối theo số lượt thăm $N$ lớn nhất (Robust Child).

3. **Bài 2 Mở rộng - Epsilon-Greedy Heuristic Rollout (`agents/mcts_heuristic_agent.py`):**
   - Thay thế Rollout ngẫu nhiên bằng mô phỏng có tri thức chiến thuật: bắt buộc đánh ngay nước tạo 5 quân hoặc chặn chuỗi 4 của đối phương.
   - Áp dụng chính sách $\epsilon$-greedy ($\epsilon = 0.80$) cân bằng giữa định hướng chiến thuật và đa dạng thống kê.
   - Đạt tỷ lệ thắng **100% (20/20 ván)** trước MCTS Random Rollout cơ sở.

---

## 4. Cài đặt & Hướng dẫn Chạy

Chương trình được thiết kế chạy trực tiếp bằng thư viện chuẩn của **Python 3** (không cần cài thêm package bên ngoài khi chạy trò chơi).

```bash
# 1. Chạy Giao diện Đồ họa (GUI - Khuyên dùng)
cd MaNguon
python3 main.py

# 2. Chạy Giao diện Dòng lệnh (CLI)
python3 main.py --cli

# 3. Tái lập lại toàn bộ Thực nghiệm (20 ván/cấu hình, SEED = 2026)
python3 main.py --exp

# 4. Xuất lại 5 biểu đồ phân tích (Cần pip install -r requirements.txt)
python3 main.py --plot
```

---

## 5. Kết quả Thực nghiệm

Toàn bộ thực nghiệm được chạy tự động với `RANDOM_SEED = 2026`, mỗi cấu hình đánh đúng **20 ván (10 cặp ván hoán đổi người đi trước X / đi sau O)** từ 10 khai cuộc trung tâm cân bằng:

| Tác nhân A | Tác nhân B | Thắng - Hòa - Thua (A) | Tỷ lệ Thắng (A) | Thời gian TB / nước |
| :--- | :--- | :---: | :---: | :---: |
| **MiniMax + Alpha-Beta (d=2)** | Random | 20 - 0 - 0 | **100.0%** | 1.7 ms |
| **MCTS Cơ sở (c=1.4, iter=300)** | Random | 20 - 0 - 0 | **100.0%** | 39.2 ms |
| **MCTS Cơ sở (c=1.4, iter=300)** | MiniMax + Alpha-Beta (d=2) | 0 - 0 - 20 | 0.0% | 33.9 ms |
| **MCTS Heuristic [Bài 2] (iter=300)** | MCTS Cơ sở (iter=300) | 20 - 0 - 0 | **100.0%** | 306.7 ms |
| **MCTS Heuristic [Bài 2] (iter=300)** | MiniMax + Alpha-Beta (d=2) | 1 - 2 - 17 | 5.0% (3 ván bất bại) | 372.9 ms |

---

## 6. Bảng Phân công Nhóm

| Thành viên | Nhiệm vụ chính | Đóng góp |
| :--- | :--- | :---: |
| **Thành viên 1** (Trưởng nhóm) | Lõi bàn cờ 9x9, Luật chơi, Hàm lượng giá & MiniMax Alpha-Beta (Bài 1.1, 1.2) | 25% |
| **Thành viên 2** | Thuật toán MCTS + UCT 4 giai đoạn (Bài 1.3) & Heuristic Rollout (Bài 2 - Hướng A) | 25% |
| **Thành viên 3** | Thiết kế thực nghiệm đối sánh, Khảo sát $c$ & $iteration$, Vẽ đồ thị & Phân tích (Bài 1.4) | 25% |
| **Thành viên 4** | Giao diện đồ họa (Tkinter GUI), Giao diện CLI, Chế độ kiểm thử, Slide & Demo | 25% |
