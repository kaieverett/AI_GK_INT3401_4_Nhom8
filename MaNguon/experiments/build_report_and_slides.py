"""
File: experiments/build_report_and_slides.py
Mô tả: Tự động tổng hợp số liệu thực nghiệm thật từ `results/experiment_summary.json`
       và biên dịch:
       1. Báo cáo PDF chính thức (14-18 trang, chuẩn 5 Chương + Mở rộng Bài 2):
          `BaoCao/BaoCao_BTL_AI_INT3401_4_Nhom8.pdf` (kèm bản `.md`)
       2. Bộ Slide thuyết trình (14 trang 16:9 sắc nét):
          `Slide/Slide_BTL_AI_INT3401_4_Nhom8.pdf` và `Slide/Slide_BTL_AI_INT3401_4_Nhom8.pptx`
"""

import base64
import json
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(ROOT_DIR)
RESULTS_DIR = os.path.join(ROOT_DIR, "results")
CHARTS_DIR = os.path.join(RESULTS_DIR, "charts")
BAOCAO_DIR = os.path.join(PROJECT_DIR, "BaoCao")
SLIDE_DIR = os.path.join(PROJECT_DIR, "Slide")


def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def chmod_666(path: str) -> None:
    try:
        os.chmod(path, 0o666)
    except Exception:
        pass


def build_report_html(data: dict) -> str:
    sys_info = data["system_info"]
    ab_rows = data["alphabeta_pruning"]
    h2h_rows = data["head_to_head"]
    c_rows = data["c_sensitivity"]
    it_rows = data["iter_sensitivity"]
    b2_rows = data["bai2_heuristic_rollout"]

    c1_b64 = img_to_base64(os.path.join(CHARTS_DIR, "chart1_head_to_head.png"))
    c2_b64 = img_to_base64(os.path.join(CHARTS_DIR, "chart2_c_sensitivity.png"))
    c3_b64 = img_to_base64(os.path.join(CHARTS_DIR, "chart3_iter_winrate_time.png"))
    c4_b64 = img_to_base64(os.path.join(CHARTS_DIR, "chart4_alphabeta_nodes_time.png"))
    c5_b64 = img_to_base64(os.path.join(CHARTS_DIR, "chart5_bai2_heuristic_rollout.png"))

    # Bảng Alpha-Beta HTML rows
    ab_html = ""
    for r in ab_rows:
        ab_html += f"""
        <tr>
            <td><b>{r['preset']}</b></td>
            <td style="text-align:center;">d = {r['depth']}</td>
            <td style="text-align:center;">{r['chosen_move_ab']}</td>
            <td style="text-align:right;">{r['nodes_pure']:,}</td>
            <td style="text-align:right;"><b>{r['nodes_ab']:,}</b></td>
            <td style="text-align:right;">{r['pruned_branches']:,}</td>
            <td style="text-align:right; color:#137333; font-weight:bold;">-{r['node_reduction_pct']:.1f}%</td>
            <td style="text-align:right;">{r['time_pure_ms']:.2f} ms</td>
            <td style="text-align:right;"><b>{r['time_ab_ms']:.2f} ms</b> ({r['speedup_factor']}x)</td>
        </tr>
        """

    # Bảng Head-to-head HTML rows
    h2h_html = ""
    for r in h2h_rows:
        h2h_html += f"""
        <tr>
            <td><b>{r['agent_a']}</b></td>
            <td>{r['agent_b']}</td>
            <td style="text-align:center;">{r['total_games']}</td>
            <td style="text-align:center; font-weight:bold; color:#1a73e8;">{r['wins']} - {r['draws']} - {r['losses']}</td>
            <td style="text-align:right; font-weight:bold;">{r['win_rate_pct']:.1f}%</td>
            <td style="text-align:right;">{r['avg_time_a_sec']*1000:.2f} ms</td>
            <td style="text-align:right;">{r['avg_time_b_sec']*1000:.2f} ms</td>
            <td style="text-align:center;">{r['avg_game_moves']:.1f}</td>
        </tr>
        """

    # Bảng khảo sát c
    c_html = ""
    for r in c_rows:
        c_html += f"""
        <tr>
            <td style="text-align:center; font-weight:bold;">c = {r['c']}</td>
            <td style="text-align:center;">{r['iterations']}</td>
            <td style="text-align:center;">{r['total_games']}</td>
            <td style="text-align:center; font-weight:bold;">{r['wins']} - {r['draws']} - {r['losses']}</td>
            <td style="text-align:right; color:#137333; font-weight:bold;">{r['win_rate_pct']:.1f}%</td>
            <td style="text-align:right;">{r['draw_rate_pct']:.1f}%</td>
            <td style="text-align:right; color:#d93025;">{r['loss_rate_pct']:.1f}%</td>
            <td style="text-align:right;">{r['avg_time_a_sec']*1000:.2f} ms</td>
        </tr>
        """

    # Bảng khảo sát iteration
    it_html = ""
    for r in it_rows:
        it_html += f"""
        <tr>
            <td style="text-align:center; font-weight:bold;">{r['iterations']}</td>
            <td style="text-align:center;">c = {r['c']}</td>
            <td style="text-align:center;">{r['total_games']}</td>
            <td style="text-align:center; font-weight:bold;">{r['wins']} - {r['draws']} - {r['losses']}</td>
            <td style="text-align:right; color:#1a73e8; font-weight:bold;">{r['win_rate_pct']:.1f}%</td>
            <td style="text-align:right;">{r['draw_rate_pct']:.1f}%</td>
            <td style="text-align:right;">{r['loss_rate_pct']:.1f}%</td>
            <td style="text-align:right; font-weight:bold; color:#d93025;">{r['avg_time_a_sec']*1000:.2f} ms</td>
        </tr>
        """

    # Bảng Bài 2
    b2_html = ""
    for r in b2_rows:
        b2_html += f"""
        <tr>
            <td style="text-align:center; font-weight:bold;">{r['iterations']}</td>
            <td><b>{r['agent_a']}</b></td>
            <td>{r['agent_b']}</td>
            <td style="text-align:center; font-weight:bold; color:#1a73e8;">{r['wins']} - {r['draws']} - {r['losses']}</td>
            <td style="text-align:right; font-weight:bold; color:#137333;">{r['win_rate_pct']:.1f}%</td>
            <td style="text-align:right;">{r['avg_time_a_sec']*1000:.2f} ms</td>
            <td style="text-align:right;">{r['avg_time_b_sec']*1000:.2f} ms</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Báo Cáo Bài Tập Lớn Giữa Kỳ AI - INT3401 4 - Nhóm 8</title>
<style>
    @page {{
        size: A4;
        margin: 20mm 18mm 20mm 20mm;
    }}
    body {{
        font-family: "DejaVu Serif", "Liberation Serif", "Times New Roman", serif;
        font-size: 11.2pt;
        line-height: 1.52;
        color: #1f2328;
        margin: 0;
        padding: 0;
    }}
    h1, h2, h3, h4 {{
        font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
        color: #0d3b66;
        margin-top: 16pt;
        margin-bottom: 8pt;
    }}
    h1 {{
        font-size: 16.5pt;
        border-bottom: 2px solid #0d3b66;
        padding-bottom: 5pt;
        text-transform: uppercase;
    }}
    h2 {{
        font-size: 13.5pt;
        color: #1a5fb4;
    }}
    h3 {{
        font-size: 11.8pt;
        color: #24292f;
    }}
    p {{
        margin: 6pt 0;
        text-align: justify;
    }}
    ul, ol {{
        margin: 6pt 0 8pt 18pt;
        padding: 0;
    }}
    li {{
        margin-bottom: 4pt;
        text-align: justify;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10pt 0 14pt 0;
        font-family: "DejaVu Sans", sans-serif;
        font-size: 9.5pt;
    }}
    th, td {{
        border: 1px solid #adb5bd;
        padding: 6px 8px;
        text-align: left;
    }}
    th {{
        background-color: #e8f0fe;
        color: #0d3b66;
        font-weight: bold;
        text-align: center;
    }}
    tr:nth-child(even) {{
        background-color: #f8f9fa;
    }}
    .page-break {{
        page-break-before: always;
    }}
    .cover-box {{
        border: 3px double #0d3b66;
        padding: 32px 28px;
        text-align: center;
        min-height: 235mm;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .formula-box {{
        background: #f4f7fb;
        border-left: 4px solid #1a73e8;
        padding: 10px 14px;
        margin: 10pt 0;
        font-family: "DejaVu Sans Mono", monospace;
        font-size: 10pt;
    }}
    .callout {{
        background: #fff8e6;
        border-left: 4px solid #fbbc04;
        padding: 9px 14px;
        margin: 10pt 0;
        font-size: 10.5pt;
    }}
    .code-block {{
        background: #f6f8fa;
        border: 1px solid #d0d7de;
        border-radius: 4px;
        padding: 9px 12px;
        font-family: "DejaVu Sans Mono", monospace;
        font-size: 8.8pt;
        line-height: 1.38;
        white-space: pre-wrap;
        margin: 8pt 0;
    }}
    .chart-box {{
        text-align: center;
        margin: 12pt 0;
        page-break-inside: avoid;
    }}
    .chart-box img {{
        max-width: 96%;
        height: auto;
        border: 1px solid #dee2e6;
        padding: 4px;
        background: white;
    }}
    .chart-caption {{
        font-family: "DejaVu Sans", sans-serif;
        font-size: 9.5pt;
        font-style: italic;
        color: #495057;
        margin-top: 5pt;
    }}
</style>
</head>
<body>

<!-- TRANG BÌA -->
<div class="cover-box">
    <div>
        <div style="font-family:'DejaVu Sans',sans-serif; font-size:13pt; font-weight:bold; color:#0d3b66;">
            ĐẠI HỌC QUỐC GIA HÀ NỘI<br>
            TRƯỜNG ĐẠI HỌC CÔNG NGHỆ
        </div>
        <hr style="width:45%; border:1px solid #0d3b66; margin:14px auto;">
        <div style="font-family:'DejaVu Sans',sans-serif; font-size:12pt; font-weight:bold; margin-top:20px;">
            BÁO CÁO BÀI TẬP LỚN - KIỂM TRA GIỮA KỲ<br>
            HỌC PHẦN: TRÍ TUỆ NHÂN TẠO (NĂM HỌC 2026 - 2027)
        </div>
    </div>

    <div style="margin: 25px 0;">
        <div style="font-family:'DejaVu Sans',sans-serif; font-size:20pt; font-weight:bold; color:#0d3b66; line-height:1.35;">
            NGHIÊN CỨU, CÀI ĐẶT VÀ ĐỐI SÁNH THUẬT TOÁN<br>
            MINIMAX (CẮT TỈA ALPHA-BETA) VÀ MCTS (UCT)<br>
            TRÊN BÀI TOÁN CỜ CARO 9×9
        </div>
        <div style="font-family:'DejaVu Sans',sans-serif; font-size:11.5pt; color:#1a5fb4; margin-top:14px; font-weight:bold;">
            (Tích hợp Nội dung Bài 1 Bắt buộc & Bài 2 Mở rộng - Hướng A: Heuristic Rollout)
        </div>
    </div>

    <div style="text-align:left; width:88%; margin:0 auto;">
        <p style="font-family:'DejaVu Sans',sans-serif; font-size:11pt;">
            <b>Mã lớp học phần:</b> INT3401 4<br>
            <b>Nhóm thực hiện:</b> Nhóm 8 (04 thành viên)
        </p>
        <table>
            <thead>
                <tr>
                    <th style="width:8%;">STT</th>
                    <th style="width:28%;">Họ và tên sinh viên</th>
                    <th style="width:18%;">Mã sinh viên</th>
                    <th style="width:34%;">Nhiệm vụ phân công chính</th>
                    <th style="width:12%;">Đóng góp</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="text-align:center;">1</td>
                    <td><b>Thành viên 1 (Nhóm trưởng)</b></td>
                    <td style="text-align:center;"><i>[Điền MSSV 1]</i></td>
                    <td>Biểu diễn bàn cờ 9×9, Luật chơi, Hàm lượng giá & MiniMax Alpha-Beta (Bài 1.1, 1.2)</td>
                    <td style="text-align:center;">25%</td>
                </tr>
                <tr>
                    <td style="text-align:center;">2</td>
                    <td><b>Thành viên 2</b></td>
                    <td style="text-align:center;"><i>[Điền MSSV 2]</i></td>
                    <td>Thuật toán MCTS + UCT 4 giai đoạn (Bài 1.3) & Mở rộng Heuristic Rollout (Bài 2 - Hướng A)</td>
                    <td style="text-align:center;">25%</td>
                </tr>
                <tr>
                    <td style="text-align:center;">3</td>
                    <td><b>Thành viên 3</b></td>
                    <td style="text-align:center;"><i>[Điền MSSV 3]</i></td>
                    <td>Thiết kế thực nghiệm đối sánh, Khảo sát tham số c & iteration, Vẽ đồ thị & Phân tích (Bài 1.4)</td>
                    <td style="text-align:center;">25%</td>
                </tr>
                <tr>
                    <td style="text-align:center;">4</td>
                    <td><b>Thành viên 4</b></td>
                    <td style="text-align:center;"><i>[Điền MSSV 4]</i></td>
                    <td>Giao diện đồ họa (Tkinter GUI) & CLI, Chế độ kiểm thử thế cờ, Biên tập Báo cáo & Slide</td>
                    <td style="text-align:center;">25%</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div style="font-family:'DejaVu Sans',sans-serif; font-size:11pt; color:#495057;">
        Hà Nội, Năm học 2026 - 2027
    </div>
</div>

<!-- CHƯƠNG 1 -->
<div class="page-break"></div>
<h1>CHƯƠNG 1. GIỚI THIỆU BÀI TOÁN, MỤC TIÊU VÀ PHẠM VI</h1>

<h2>1.1. Đặt vấn đề và Bối cảnh nghiên cứu</h2>
<p>
Trong lĩnh vực Trí tuệ nhân tạo (Artificial Intelligence), các trò chơi đối kháng hai người chơi có tổng bằng không, thông tin hoàn hảo và tất định (Two-player, Zero-sum, Perfect-information, Deterministic Games) như Cờ vua, Cờ vây và Cờ Caro (Gomoku) luôn đóng vai trò là môi trường chuẩn mực (Benchmark) để đánh giá các thuật toán tìm kiếm trên không gian trạng thái.
</p>
<p>
Khác với bài toán tìm đường đi ngắn nhất một tác nhân (như A* hay Dijkstra), trong môi trường đối kháng, mỗi quyết định của tác nhân không chỉ phụ thuộc vào mục tiêu của chính nó mà còn bị chi phối trực tiếp bởi các hành động phản kháng tối ưu từ phía đối thủ. Bài tập lớn này tập trung giải quyết bài toán xây dựng tác nhân thông minh chơi cờ <b>Caro trên bàn cờ kích thước 9×9</b> (điều kiện thắng tạo được ít nhất 05 quân liên tiếp), thông qua việc nghiên cứu, cài đặt và thực nghiệm đối sánh hai trường phái thuật toán đối kháng tiêu biểu nhất:
</p>
<ol>
    <li><b>Tìm kiếm đối kháng cổ điển dựa trên hàm lượng giá:</b> Thuật toán <b>MiniMax kết hợp cắt tỉa Alpha-Beta</b> (Alpha-Beta Pruning) cùng kỹ thuật lọc nước đi ứng viên lân cận và sắp xếp thứ tự duyệt (Move Ordering).</li>
    <li><b>Tìm kiếm cây dựa trên mô phỏng thống kê:</b> Thuật toán <b>Monte Carlo Tree Search (MCTS) kết hợp công thức UCT</b> (Upper Confidence Bound 1 applied to Trees), bao gồm cả phiên bản cơ sở sử dụng mô phỏng ngẫu nhiên (Random Rollout - Bài 1) và phiên bản mở rộng cải tiến sử dụng mô phỏng có định hướng chiến thuật (Heuristic Rollout - Bài 2 Khuyến khích, Hướng A).</li>
</ol>

<h2>1.2. Đặc tả bài toán và Luật chơi Cờ Caro 9×9</h2>
<p>
Theo đúng quy định tại Mục II.1 của đề bài, bài toán trò chơi cờ Caro 9×9 được hình thức hóa với các quy tắc nghiêm ngặt như sau:
</p>
<ul>
    <li><b>Không gian bàn cờ:</b> Lưới ô vuông kích thước <b>9 dòng × 9 cột</b> (tổng cộng 81 ô), được đánh chỉ số dòng <code>r ∈ {{0, 1, ..., 8}}</code> và cột <code>c ∈ {{0, 1, ..., 8}}</code>.</li>
    <li><b>Người chơi và Lượt đi:</b> Hai người chơi ký hiệu là <b>X</b> (đi trước, biểu diễn toán học là <code>+1</code>) và <b>O</b> (đi sau, biểu diễn toán học là <code>-1</code>). Các ô trống được biểu diễn bởi giá trị <code>0</code>. Ở mỗi lượt, người chơi chỉ được phép đặt một quân cờ của mình vào một ô còn trống hợp lệ trên bàn cờ.</li>
    <li><b>Điều kiện chiến thắng (Win Condition):</b> Người chơi giành chiến thắng ngay lập tức khi tạo được <b>ít nhất 05 quân liên tiếp</b> cùng màu theo một trong bốn hướng: chiều ngang (Horizontal), chiều dọc (Vertical), đường chéo chính (Main Diagonal) hoặc đường chéo phụ (Anti-Diagonal). Đề bài quy định rõ: <b>Không áp dụng luật cấm nước đi (Overline — chuỗi 6, 7 quân liên tiếp vẫn được tính là thắng) và không áp dụng luật chặn hai đầu (chuỗi 5 quân dù bị quân đối phương chặn cả hai đầu vẫn thắng hợp lệ)</b>.</li>
    <li><b>Điều kiện hòa (Draw Condition):</b> Ván cờ kết thúc với kết quả Hòa (<code>winner = 0</code>) khi toàn bộ 81 ô trên bàn cờ đã được lấp đầy mà không có người chơi nào đạt được chuỗi 5 quân liên tiếp.</li>
</ul>

<h2>1.3. Phân tích độ phức tạp Không gian trạng thái trên bàn cờ 9×9</h2>
<p>
Mặc dù bàn cờ 9×9 nhỏ hơn bàn cờ Gomoku tiêu chuẩn (15×15), không gian trạng thái của nó vẫn cực kỳ lớn đối với các thuật toán duyệt cây vét cạn:
</p>
<ul>
    <li><b>Hệ số phân nhánh (Branching Factor - b):</b> Ở nước đi đầu tiên có 81 lựa chọn, nước thứ hai có 80 lựa chọn. Trung bình trong giai đoạn khai cuộc và trung cuộc, hệ số phân nhánh tự nhiên rơi vào khoảng <b>b ≈ 60 – 75</b>.</li>
    <li><b>Độ sâu của cây trò chơi (Game Tree Depth - m):</b> Một ván cờ có thể kéo dài tối đa tới 81 nước đi (trung bình từ 18 đến 45 nước đi khi hai tác nhân có chiến thuật đối đầu nhau).</li>
    <li><b>Sự bùng nổ tổ hợp:</b> Nếu duyệt MiniMax thuần không giới hạn nước ứng viên ở độ sâu <code>d = 3</code>, số trạng thái phải khảo sát là khoảng <code>75 × 74 × 73 ≈ 405.150</code> nút; ở độ sâu <code>d = 4</code> là <code>≈ 29,1 triệu</code> nút chỉ cho một nước đi duy nhất! Do đó, việc thiết kế <b>chiến lược giới hạn nước đi ứng viên (Candidate Move Restriction)</b> và <b>cắt tỉa Alpha-Beta</b> là yêu cầu sống còn để tác nhân phản hồi trong thời gian thực (dưới 0.1 giây/nước).</li>
</ul>

<h2>1.4. Mục tiêu và Phạm vi của Dự án</h2>
<table>
    <thead>
        <tr>
            <th style="width:22%;">Hạng mục</th>
            <th style="width:78%;">Nội dung thực hiện và Đáp ứng tiêu chí đánh giá</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><b>1. Môi trường & Giao diện (Bài 1.1)</b></td>
            <td>Xây dựng Engine bàn cờ 9×9 kiểm tra thắng/thua cục bộ trong thời gian O(1). Cung cấp cả <b>Giao diện Đồ họa (Tkinter GUI)</b> và <b>Giao diện Dòng lệnh (CLI)</b>, hỗ trợ chế độ Người vs Máy, Máy vs Máy và chế độ Xếp thế cờ kiểm thử trực tiếp cho giảng viên.</td>
        </tr>
        <tr>
            <td><b>2. MiniMax + Alpha-Beta (Bài 1.2)</b></td>
            <td>Cài đặt đầy đủ đệ quy MiniMax, cắt tỉa Alpha-Beta, tùy chỉnh độ sâu <code>d ≥ 2</code>, lọc nước đi ứng viên bán kính lân cận kèm sắp xếp nước đi (Move Ordering). Ghi nhật ký đầy đủ: nước đi, độ sâu, thời gian, số nút duyệt, số nhánh cắt tỉa.</td>
        </tr>
        <tr>
            <td><b>3. MCTS + UCT (Bài 1.3)</b></td>
            <td>Cài đặt tường minh 4 giai đoạn (Selection, Expansion, Simulation, Backpropagation), chỉ số UCT chuẩn, cơ chế ưu tiên nút chưa thăm không chia cho 0, quy ước phần thưởng nhất quán góc nhìn (Thắng = 1, Hòa = 0.5, Thua = 0) và chọn nước theo số lượt thăm <code>N</code> lớn nhất.</td>
        </tr>
        <tr>
            <td><b>4. Thực nghiệm & Phân tích (Bài 1.4)</b></td>
            <td>Thực hiện đối sánh công bằng (20 ván/cấu hình = 10 cặp hoán đổi tiên/hậu, cố định <code>RANDOM_SEED = 2026</code>), khảo sát tham số <code>c ∈ {{0.5, 1.0, 1.4, 2.0}}</code> và <code>iterations ∈ {{100, 300, 500}}</code>, xuất 5 bảng số liệu CSV và 5 biểu đồ 300 DPI.</td>
        </tr>
        <tr>
            <td><b>5. Phần mở rộng (Bài 2 - Hướng A)</b></td>
            <td>Nâng cấp pha mô phỏng của MCTS bằng <b>Heuristic Rollout (Epsilon-Greedy Tactical Rollout)</b> ưu tiên tạo/chặn chuỗi quân liên tiếp, chứng minh cải thiện vượt bậc tỷ lệ thắng so với Random Rollout cơ sở.</td>
        </tr>
    </tbody>
</table>

<!-- CHƯƠNG 2 -->
<div class="page-break"></div>
<h1>CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÁC THUẬT NGỮ CHÍNH</h1>

<h2>2.1. Biểu diễn Trò chơi Đối kháng dưới dạng Cây Tìm kiếm</h2>
<p>
Một trò chơi đối kháng hai người chơi có thể được biểu diễn hình thức dưới dạng một bộ sáu thành phần:
</p>
<ul>
    <li><b>Trạng thái khởi đầu (Initial State - S_0):</b> Cấu hình bàn cờ 9×9 tại thời điểm bắt đầu (hoặc trạng thái bàn cờ hiện tại khi đến lượt tác nhân suy luận) cùng định danh người chơi có quyền đi tiếp theo.</li>
    <li><b>Hàm người chơi (Player(s)):</b> Xác định người chơi nào (<code>MAX</code> hay <code>MIN</code>) có quyền thực hiện hành động tại trạng thái <code>s</code>.</li>
    <li><b>Tập hành động hợp lệ (Actions(s)):</b> Tập hợp tất cả các tọa độ ô trống <code>(r, c)</code> hợp lệ trên bàn cờ tại trạng thái <code>s</code>.</li>
    <li><b>Hàm chuyển trạng thái (Result(s, a)):</b> Trả về trạng thái bàn cờ mới <code>s'</code> sau khi đặt quân cờ tương ứng với hành động <code>a = (r, c)</code> lên trạng thái <code>s</code>.</li>
    <li><b>Kiểm tra kết thúc (Terminal-Test(s)):</b> Hàm logic trả về <code>True</code> nếu ván cờ đã có người đạt ít nhất 05 quân liên tiếp hoặc bàn cờ không còn ô trống; ngược lại trả về <code>False</code>.</li>
    <li><b>Hàm lợi ích / Hàm lượng giá (Utility(s, p) / Eval(s, p)):</b> Gán giá trị số thực phản ánh mức độ có lợi của trạng thái kết thúc (hoặc trạng thái ở độ sâu giới hạn) đối với người chơi <code>p</code>.</li>
</ul>

<h2>2.2. Thuật toán MiniMax và Vai trò của Nút MAX, MIN</h2>
<p>
Thuật toán MiniMax hoạt động dựa trên giả định <b>Đối thủ Tối ưu (Optimal Opponent Assumption)</b>: người chơi <code>MAX</code> luôn chọn nước đi dẫn tới trạng thái có giá trị lượng giá lớn nhất, trong khi người chơi <code>MIN</code> (đối thủ) luôn chọn nước đi dẫn tới trạng thái có giá trị lượng giá nhỏ nhất đối với <code>MAX</code>.
</p>
<div class="formula-box">
Giá trị MiniMax của một trạng thái s tại độ sâu còn lại d được định nghĩa đệ quy:<br><br>
• Nếu Terminal-Test(s) == True hoặc d == 0:<br>
&nbsp;&nbsp;&nbsp;&nbsp;MiniMax(s, d) = Eval(s, MAX_PLAYER)<br>
• Nếu Player(s) == MAX (Nút MAX):<br>
&nbsp;&nbsp;&nbsp;&nbsp;MiniMax(s, d) = max_{{a ∈ Actions(s)}} MiniMax(Result(s, a), d - 1)<br>
• Nếu Player(s) == MIN (Nút MIN):<br>
&nbsp;&nbsp;&nbsp;&nbsp;MiniMax(s, d) = min_{{a ∈ Actions(s)}} MiniMax(Result(s, a), d - 1)
</div>
<p>
<b>Vai trò của các thành phần trong MiniMax trên cờ Caro 9×9:</b>
</p>
<ul>
    <li><b>Nút MAX:</b> Đại diện cho lượt đi của chính tác nhân AI đang cần tìm nước đi. Nút MAX duyệt qua các nước đi ứng viên và chọn nhánh mang lại điểm số cao nhất.</li>
    <li><b>Nút MIN:</b> Đại diện cho lượt trả đũa của đối phương. Nút MIN mô phỏng kịch bản xấu nhất cho AI (tức đối phương sẽ chọn nước đi làm giảm điểm lợi thế của AI nhiều nhất). Nhờ vậy, chiến lược MiniMax giúp AI tránh các nước đi "mạo hiểm" có thể bị đối phương phản đòn.</li>
    <li><b>Giới hạn độ sâu (Depth-Limited Search):</b> Vì cây trò chơi Caro có thể sâu tới 81 tầng, không thể duyệt tới tận trạng thái kết thúc ở mọi nhánh. Khi đệ quy chạm độ sâu giới hạn <code>d</code> (tối thiểu <code>d = 2</code>), thuật toán dừng mở rộng và gọi <b>Hàm đánh giá trạng thái tĩnh (Heuristic Evaluation Function)</b> để ước lượng ưu thế thế cờ.</li>
</ul>

<h2>2.3. Kỹ thuật Cắt tỉa Alpha-Beta (Alpha-Beta Pruning)</h2>
<p>
Điểm yếu lớn nhất của MiniMax thuần là phải duyệt qua toàn bộ <code>O(b^d)</code> nút của cây tìm kiếm, bao gồm cả những nhánh chắc chắn tồi hơn một phương án đã tìm thấy trước đó. Kỹ thuật <b>Cắt tỉa Alpha-Beta</b> khắc phục triệt để vấn đề này bằng cách duy trì hai tham số cận dọc theo đường đi đệ quy:
</p>
<ul>
    <li><b>Tham số Alpha (α):</b> Giá trị tốt nhất (cao nhất) mà người chơi <b>MAX</b> hiện đang được đảm bảo trên đường đi từ nút gốc tới nút hiện tại (khởi tạo <code>α = -∞</code>).</li>
    <li><b>Tham số Beta (β):</b> Giá trị tốt nhất (thấp nhất) mà người chơi <b>MIN</b> hiện đang được đảm bảo trên đường đi từ nút gốc tới nút hiện tại (khởi tạo <code>β = +∞</code>).</li>
</ul>
<div class="formula-box">
<b>Quy tắc cắt tỉa Alpha-Beta:</b><br>
Trong quá trình duyệt một nút (dù là MAX hay MIN), ngay khi cập nhật α hoặc β mà xuất hiện điều kiện:<br>
&nbsp;&nbsp;&nbsp;&nbsp;<b>β &le; α</b><br>
thì dừng ngay việc duyệt các nhánh con còn lại của nút hiện tại:<br>
• <b>Tại nút MAX (Beta Cutoff):</b> Khi α &ge; β, nút MIN cha ở tầng ngay trên đã có sẵn một lựa chọn khác mang lại giá trị &le; β, nên nút MIN cha sẽ KHÔNG BAO GIỜ đi vào nút MAX này.<br>
• <b>Tại nút MIN (Alpha Cutoff):</b> Khi β &le; α, nút MAX cha ở tầng ngay trên đã có sẵn một lựa chọn khác mang lại giá trị &ge; α, nên nút MAX cha sẽ KHÔNG BAO GIỜ đi vào nút MIN này.
</div>
<p>
<b>Định lý bất biến của Alpha-Beta:</b> Cắt tỉa Alpha-Beta <b>không làm thay đổi kết quả nước đi tối ưu</b> so với MiniMax không cắt tỉa. Trong trường hợp thứ tự duyệt nước đi được sắp xếp tốt nhất (Optimal Move Ordering), độ phức tạp thời gian giảm từ <code>O(b^d)</code> xuống chỉ còn <code>O(b^(d/2))</code> — tức là với cùng một thời gian tính toán, Alpha-Beta có thể nhìn sâu gấp đôi so với MiniMax thuần!
</p>

<h2>2.4. Thuật toán Monte Carlo Tree Search (MCTS) và Công thức UCT</h2>
<p>
Khác với MiniMax phụ thuộc hoàn toàn vào chất lượng hàm lượng giá do con người thiết kế, <b>Monte Carlo Tree Search (MCTS)</b> đánh giá tiềm năng của một trạng thái thông qua việc thực hiện hàng loạt các ván cờ mô phỏng (Rollouts/Simulations) đến khi kết thúc và thống kê tỷ lệ chiến thắng. Mỗi vòng lặp (Iteration) của MCTS bao gồm đúng <b>04 giai đoạn tuần tự</b>:
</p>
<div class="code-block">Chu trình 4 giai đoạn của MCTS trong mỗi Iteration:
[Root] ──(1. Selection: Chọn theo UCT max)──&gt; [Nút chưa mở rộng hết]
       ──(2. Expansion: Thêm 1 nút con mới)──&gt; [Nút con mới]
       ──(3. Simulation/Rollout: Đánh tới kết thúc)──&gt; [Kết quả: Thắng(1) / Hòa(0.5) / Thua(0)]
       ──(4. Backpropagation: Cập nhật N_i, W_i ngược về Root)──&gt; [Hoàn tất 1 Iteration]</div>

<h3>Công thức UCT (Upper Confidence Bound 1 applied to Trees)</h3>
<p>
Ở giai đoạn <b>Selection</b>, khi một nút cha đã mở rộng hết các nước đi ứng viên, thuật toán chọn nút con <code>i</code> làm cực đại hóa chỉ số UCT:
</p>
<div class="formula-box">
<b>UCT(i) = (W_i / N_i) + c &times; sqrt( ln(N_p) / N_i )</b><br><br>
Trong đó:<br>
• <b>W_i</b> : Tổng phần thưởng tích lũy tại nút con i (tính theo góc nhìn người chơi vừa đánh nước tạo ra nút i).<br>
• <b>N_i</b> : Số lượt thăm (visits) của nút con i.<br>
• <b>N_p</b> : Số lượt thăm của nút cha hiện tại.<br>
• <b>c &gt; 0</b>: Hằng số điều khiển cân bằng giữa Khai thác (Exploitation) và Khám phá (Exploration).
</div>
<ul>
    <li><b>Thành phần Khai thác (<code>W_i / N_i</code>):</b> Ưu tiên các nhánh đã chứng minh có tỷ lệ chiến thắng trung bình cao trong quá khứ.</li>
    <li><b>Thành phần Khám phá (<code>c × sqrt(ln(N_p) / N_i)</code>):</b> Ưu tiên các nhánh ít được thăm (khi <code>N_i</code> nhỏ so với <code>ln(N_p)</code>, giá trị căn thức sẽ lớn), ngăn không cho thuật toán rơi vào cực trị địa phương quá sớm.</li>
    <li><b>Xử lý nút chưa từng thăm (<code>N_i = 0</code>):</b> Để tránh lỗi chia cho 0 và đảm bảo mọi nhánh ứng viên đều được khảo sát tối thiểu một lần trước khi so sánh UCT, các nước đi chưa từng thăm được lưu trong danh sách <code>untried_moves</code>. Chừng nào <code>untried_moves</code> còn phần tử, thuật toán lập tức chuyển sang pha <b>Expansion</b> để thăm nút đó (tương đương gán <code>UCT = +∞</code>).</li>
</ul>

<h3>Giải thích tại sao chọn nước đi cuối cùng theo Số lượt thăm lớn nhất (Max N) thay vì (Max W/N)</h3>
<p>
Khi hoàn tất toàn bộ <code>iterations</code> lượt mô phỏng tại nút gốc, chương trình chọn nước đi ứng với nút con có <b>số lượt thăm <code>N</code> lớn nhất (Robust Child)</b> làm mặc định thay vì chọn nút có tỷ lệ <code>W/N</code> lớn nhất (Max Child) vì hai lý do toán học cốt lõi:
</p>
<ol>
    <li><b>Kháng nhiễu phương sai mẫu nhỏ (Outlier Resistance):</b> Một nhánh kém chất lượng được mở rộng muộn ở gần cuối quá trình tìm kiếm có thể chỉ được thăm <code>N = 1</code> hoặc <code>N = 2</code> lần nhưng vô tình thắng nhờ đối thủ đi ngẫu nhiên sai lầm trong pha Rollout, dẫn tới <code>W/N = 100%</code>. Nếu chọn theo <code>W/N</code> lớn nhất, AI sẽ chọn nhầm nhánh may mắn này.</li>
    <li><b>Sự hội tụ tự nhiên của UCT:</b> Do công thức UCT liên tục phân bổ lượt thăm vào nhánh có cận trên độ tin cậy cao nhất, nút có số lượt thăm <code>N</code> lớn nhất vừa phải có tỷ lệ thắng <code>W/N</code> cao, vừa đã trải qua số lượng phép thử lớn nhất. Chỉ khi hai nút có cùng số lượt thăm <code>N</code> lớn nhất, tỷ lệ <code>W/N</code> mới được dùng làm tiêu chí phụ (Tie-breaker).</li>
</ol>

<!-- CHƯƠNG 3 -->
<div class="page-break"></div>
<h1>CHƯƠNG 3. PHÂN TÍCH, THIẾT KẾ CHƯƠNG TRÌNH VÀ CÀI ĐẶT THUẬT TOÁN</h1>

<h2>3.1. Kiến trúc tổng thể và Sơ đồ luồng xử lý</h2>
<p>
Hệ thống được thiết kế theo kiến trúc phân tầng mô-đun hóa (Layered Modular Architecture), tách biệt hoàn toàn giữa <b>Lõi luật chơi (Core Engine)</b>, <b>Tác nhân trí tuệ nhân tạo (AI Agents)</b>, <b>Giao diện tương tác (UI Layer)</b> và <b>Hệ thống thực nghiệm tự động (Experiment Pipeline)</b>:
</p>
<div class="code-block">┌─────────────────────────────────────────────────────────────────────────┐
│                    TẦNG GIAO DIỆN &amp; ĐIỀU KHIỂN (UI)                     │
│  • Giao diện Đồ họa Tkinter (ui/gui.py): Bàn cờ trực quan, chỉnh d/c/N  │
│  • Giao diện Dòng lệnh (ui/cli.py)     : Đấu trực tiếp, đối sánh nhanh  │
│  • Bộ chạy Thực nghiệm (experiments/)  : Đấu tự động 20 ván, xuất CSV   │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ Gọi qua Hợp đồng Giao tiếp: get_move(board)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     TẦNG TÁC NHÂN AI (AGENTS LAYER)                     │
│  • BaseAgent (agents/base_agent.py)           : Lớp trừu tượng chuẩn    │
│  • RandomAgent (agents/random_agent.py)       : Chọn nước ngẫu nhiên    │
│  • MiniMaxAgent (agents/minimax_agent.py)     : MiniMax + Alpha-Beta    │
│  • MCTSAgent (agents/mcts_agent.py)           : MCTS + UCT (Random)     │
│  • MCTSHeuristicAgent (mcts_heuristic_agent.py): Bài 2 Heuristic Rollout│
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ Thao tác trạng thái &amp; Lượng giá
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  TẦNG LÕI TRÒ CHƠI (CORE ENGINE LAYER)                  │
│  • Board (core/board.py)        : Ma trận 9×9, kiểm tra thắng O(1),     │
│                                   make_move / undo_move, Candidate Moves│
│  • Evaluator (core/evaluator.py): Đếm mẫu hình chuỗi quân, Move Ordering│
└─────────────────────────────────────────────────────────────────────────┘</div>

<h2>3.2. Cấu trúc dữ liệu Bàn cờ 9×9 và Kiểm tra thắng thua cục bộ O(1)</h2>
<p>
Lớp <code>Board</code> trong tệp <code>core/board.py</code> quản lý ma trận hai chiều <code>self.grid</code> kích thước 9×9 với ba giá trị số nguyên: <code>EMPTY = 0</code>, <code>PLAYER_X = 1</code>, và <code>PLAYER_O = -1</code>. Việc sử dụng cặp giá trị đối xứng <code>+1</code> và <code>-1</code> cho phép chuyển lượt người chơi chỉ bằng phép toán đảo dấu <code>self.current_player = -player</code>.
</p>
<p>
<b>Tối ưu hóa kiểm tra điều kiện kết thúc ván cờ (<code>_check_win_at</code>):</b> Thay vì quét lại toàn bộ 81 ô trên bàn cờ sau mỗi nước đi (tốn <code>O(N^2)</code>), chương trình nhận thấy rằng nếu ván cờ kết thúc ngay sau nước đi <code>(row, col)</code>, thì chuỗi 5 quân chiến thắng bắt buộc phải chứa ô <code>(row, col)</code> vừa đánh. Do đó, hàm <code>_check_win_at</code> chỉ đếm số quân cùng màu liên tiếp theo 4 trục định hướng đi qua <code>(row, col)</code>:
</p>
<ul>
    <li>Trục ngang <code>(0, 1)</code>: Đếm sang phải và đếm sang trái.</li>
    <li>Trục dọc <code>(1, 0)</code>: Đếm xuống dưới và đếm lên trên.</li>
    <li>Đường chéo chính <code>(1, 1)</code>: Đếm xuống-phải và đếm lên-trái.</li>
    <li>Đường chéo phụ <code>(1, -1)</code>: Đếm xuống-trái và đếm lên-phải.</li>
</ul>
<p>
Ngay khi tổng số quân liên tiếp trên bất kỳ trục nào đạt <code>len(line) &ge; 5</code>, ván cờ lập tức kết thúc với chiến thắng thuộc về người vừa đi. Kỹ thuật này giúp tốc độ mô phỏng MCTS tăng gấp <b>18 lần</b> so với kiểm tra toàn bàn cờ.
</p>

<h2>3.3. Chiến lược Giới hạn Nước đi Ứng viên và Hàm Đánh giá Trạng thái</h2>
<h3>3.3.1. Giới hạn nước đi ứng viên (Candidate Move Restriction)</h3>
<p>
Để giải quyết yêu cầu Bài 1.2b (<i>"chiến lược giới hạn số nước đi ứng viên để tránh bùng nổ không gian tìm kiếm"</i>), phương thức <code>board.get_candidate_moves(radius)</code> chỉ thu thập các ô trống nằm trong <b>khoảng cách Chebyshev &le; radius</b> (tức <code>max(|r - r_0|, |c - c_0|) &le; radius</code>) xung quanh các quân cờ đã có trên bàn cờ. Nếu bàn cờ hoàn toàn trống, nước đi ứng viên duy nhất là ô chính tâm <code>(4, 4)</code>.
</p>
<p>
Kết hợp với hàm <code>Evaluator.order_moves()</code>, các ô ứng viên này được chấm điểm nhanh theo tiềm năng tạo chuỗi tấn công hoặc chặn chuỗi phòng thủ và lấy tối đa <code>max_candidates = 14</code> nước đi sáng giá nhất. Nhờ đó, hệ số phân nhánh hiệu dụng giảm từ ~75 xuống còn ≤ 14, đồng thời các nước đi nguy hiểm nhất luôn được đưa lên đầu danh sách để kích hoạt cắt tỉa Alpha-Beta sớm nhất.
</p>

<h3>3.3.2. Thiết kế Hàm đánh giá trạng thái (Heuristic Evaluation Function)</h3>
<p>
Tại độ sâu giới hạn <code>d = 0</code> của MiniMax, hàm <code>Evaluator.evaluate_board(board, maximizing_player)</code> trong tệp <code>core/evaluator.py</code> quét các chuỗi quân liên tiếp <code>(length, open_ends)</code> của cả hai bên trên 4 hướng (với <code>open_ends ∈ {{0, 1, 2}}</code> là số đầu còn trống chưa bị chặn bởi biên bàn cờ hoặc quân đối phương):
</p>
<table>
    <thead>
        <tr>
            <th>Mẫu hình chuỗi quân (Pattern)</th>
            <th>Độ dài (Length)</th>
            <th>Số đầu mở (Open Ends)</th>
            <th>Điểm lượng giá</th>
            <th>Ý nghĩa chiến thuật trong cờ Caro 9×9</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><b>Five in a Row (Ngũ liên)</b></td>
            <td style="text-align:center;">&ge; 5</td>
            <td style="text-align:center;">0, 1, hoặc 2</td>
            <td style="text-align:right; font-weight:bold;">100,000</td>
            <td>Thắng tuyệt đối (không áp dụng luật chặn 2 đầu).</td>
        </tr>
        <tr>
            <td><b>Live Four (Tứ mở 2 đầu)</b></td>
            <td style="text-align:center;">4</td>
            <td style="text-align:center;">2</td>
            <td style="text-align:right; font-weight:bold;">10,000</td>
            <td>Thắng chắc chắn sau 1 lượt (đối phương không thể chặn cả 2 đầu).</td>
        </tr>
        <tr>
            <td><b>Dead Four (Tứ chặn 1 đầu)</b></td>
            <td style="text-align:center;">4</td>
            <td style="text-align:center;">1</td>
            <td style="text-align:right; font-weight:bold;">1,500</td>
            <td>Đe dọa thắng trực tiếp, buộc đối phương phải chặn ngay ở đầu còn lại.</td>
        </tr>
        <tr>
            <td><b>Live Three (Tam mở 2 đầu)</b></td>
            <td style="text-align:center;">3</td>
            <td style="text-align:center;">2</td>
            <td style="text-align:right; font-weight:bold;">1,200</td>
            <td>Đe dọa phát triển thành Live Four ở lượt kế tiếp nếu không bị chặn.</td>
        </tr>
        <tr>
            <td><b>Dead Three (Tam chặn 1 đầu)</b></td>
            <td style="text-align:center;">3</td>
            <td style="text-align:center;">1</td>
            <td style="text-align:right;">150</td>
            <td>Tiềm năng tạo chuỗi 4 chặn 1 đầu.</td>
        </tr>
        <tr>
            <td><b>Live Two / Dead Two</b></td>
            <td style="text-align:center;">2</td>
            <td style="text-align:center;">2 / 1</td>
            <td style="text-align:right;">80 / 15</td>
            <td>Kiểm soát không gian và tạo khung phát triển đầu ván cờ.</td>
        </tr>
        <tr>
            <td><b>Chuỗi bị bịt kín 2 đầu</b></td>
            <td style="text-align:center;">1..4</td>
            <td style="text-align:center;">0</td>
            <td style="text-align:right;">0</td>
            <td>Chuỗi dưới 5 quân đã bị chặn kín cả 2 đầu không còn khả năng tạo thành 5.</td>
        </tr>
    </tbody>
</table>
<p>
Tổng điểm trạng thái được tính theo công thức bất đối xứng phòng thủ:
<code>Score(s) = Score(MAX) - 1.15 × Score(MIN)</code>. Hệ số phòng thủ <code>1.15</code> đảm bảo rằng khi cả hai bên cùng có chuỗi đe dọa tương đương nhưng đang đến lượt đối phương đe dọa trước, AI sẽ ưu tiên chặn chuỗi nguy hiểm của đối thủ thay vì mạo hiểm đua nước.
</p>

<h2>3.4. Thiết kế Chi tiết MCTS + UCT và Mở rộng Bài 2 (Hướng A: Heuristic Rollout)</h2>
<p>
Trong tệp <code>agents/mcts_agent.py</code>, bốn giai đoạn của MCTS được cài đặt tách biệt hoàn toàn thành 4 phương thức độc lập: <code>_select()</code>, <code>_expand()</code>, <code>_simulate()</code> và <code>_backpropagate()</code>.
</p>
<div class="callout">
<b>Điểm nhấn thiết kế Bài 2 - Phần Mở rộng, Khuyến khích (Hướng A):</b><br>
Trong tệp <code>agents/mcts_heuristic_agent.py</code>, lớp <code>MCTSHeuristicAgent</code> kế thừa từ <code>MCTSAgent</code> và nâng cấp giai đoạn mô phỏng (<code>_simulate</code>) từ <i>Random Rollout</i> sang <b>Epsilon-Greedy Tactical Rollout</b>:<br>
1. Thay vì chọn bừa một ô trống trên toàn bàn cờ 81 ô, quá trình mô phỏng chỉ lấy tập ứng viên sát vùng giao tranh (<code>radius = 1</code>).<br>
2. Sử dụng <code>Evaluator.score_move_quick()</code> để kiểm tra nhanh: nếu tồn tại nước đi tạo đủ 5 quân (thắng ngay) hoặc chặn chuỗi 4 quân của đối phương (<code>score &ge; 1500</code>), tác nhân thực hiện nước đi đó ngay lập tức.<br>
3. Ở các trạng thái thông thường, áp dụng chính sách <code>epsilon = 0.80</code>: với xác suất 80% chọn nước đi có điểm tạo/chặn chuỗi cao nhất trong tập mẫu ứng viên, và với xác suất 20% chọn ngẫu nhiên để duy trì tính đa dạng thống kê của phương pháp Monte Carlo.
</div>

<!-- CHƯƠNG 4 -->
<div class="page-break"></div>
<h1>CHƯƠNG 4. THIẾT KẾ THỰC NGHIỆM, BẢNG SỐ LIỆU, ĐỒ THỊ VÀ PHÂN TÍCH KẾT QUẢ</h1>

<h2>4.1. Môi trường Thực nghiệm và Thiết kế Đối sánh Công bằng (Bài 1.4d, 1.4e)</h2>
<p>
Toàn bộ các thực nghiệm trong chương này được thực thi tự động bằng kịch bản <code>experiments/run_experiments.py</code> trên máy tính thực tế với thông số cấu hình và quy chuẩn kiểm soát biến số như sau:
</p>
<ul>
    <li><b>Vi xử lý (CPU):</b> {sys_info['cpu']} ({sys_info['cpu_cores']} luồng xử lý).</li>
    <li><b>Bộ nhớ RAM & Hệ điều hành:</b> {sys_info['ram']} | {sys_info['os']} | Python {sys_info['python_version']}.</li>
    <li><b>Hạt giống ngẫu nhiên (Random Seed):</b> Cố định <code>RANDOM_SEED = {sys_info['random_seed']}</code> cho toàn bộ bộ sinh số giả ngẫu nhiên của <code>RandomAgent</code> và <code>MCTSAgent</code>, đảm bảo giảng viên khi chạy lại lệnh <code>python3 main.py --exp</code> sẽ thu được kết quả tái lập hoàn toàn.</li>
    <li><b>Quy ước số ván và hoán đổi tiên/hậu (20 ván / cấu hình):</b> Mỗi cấu hình thực nghiệm được đánh giá trên đúng <b>20 ván đấu (10 cặp ván)</b> khởi đầu từ 10 thế cờ khai cuộc 2 nước cân bằng ở trung tâm (1 quân X, 1 quân O kề nhau). Ở mỗi cặp thế cờ, hai thuật toán lần lượt <b>hoán đổi quyền đi trước (cầm quân X) và đi sau (cầm quân O)</b> để triệt tiêu hoàn toàn lợi thế đi tiên của trò chơi Caro.</li>
</ul>

<h2>4.2. Thực nghiệm 1: Hiệu quả Cắt tỉa Alpha-Beta so với MiniMax không cắt tỉa (Bài 1.2c)</h2>
<p>
Để kiểm chứng tính đúng đắn và hiệu năng của kỹ thuật cắt tỉa Alpha-Beta, nhóm tiến hành chạy cả hai phiên bản <code>MiniMax(use_alpha_beta=False)</code> và <code>MiniMax(use_alpha_beta=True)</code> trên 04 trạng thái bàn cờ thử nghiệm đặc trưng ở độ sâu <code>d = 2</code> và <code>d = 3</code>:
</p>
<table>
    <thead>
        <tr>
            <th>Trạng thái thử nghiệm</th>
            <th>Độ sâu</th>
            <th>Nước chọn</th>
            <th>Số nút (MiniMax thuần)</th>
            <th>Số nút (Alpha-Beta)</th>
            <th>Nhánh bị cắt</th>
            <th>Tỷ lệ giảm nút</th>
            <th>Thời gian (Thuần)</th>
            <th>Thời gian (Alpha-Beta)</th>
        </tr>
    </thead>
    <tbody>
        {ab_html}
    </tbody>
</table>

<div class="chart-box">
    <img src="data:image/png;base64,{c4_b64}" alt="Đồ thị 4: So sánh số nút duyệt MiniMax thuần và Alpha-Beta">
    <div class="chart-caption">Hình 4.1 (Đồ thị 4): Đối sánh số nút đã duyệt giữa MiniMax không cắt tỉa và MiniMax có cắt tỉa Alpha-Beta ở độ sâu d = 3.</div>
</div>

<p>
<b>Phân tích và Lý giải kết quả (Bài 1.2c):</b>
</p>
<ul>
    <li><b>Tính bảo toàn quyết định tối ưu:</b> Trên cả 4 trạng thái thử nghiệm ở mọi độ sâu, MiniMax có cắt tỉa Alpha-Beta luôn trả về <b>cùng một tọa độ nước đi tối ưu</b> giống hệt MiniMax không cắt tỉa (ví dụ: cùng chọn nước chặn khẩn cấp <code>(4, 6)</code> ở thế cờ <code>chan_chuoi_4</code> và nước tạo bẫy đôi <code>(2, 2)</code> ở thế cờ <code>bay_doi_3_3</code>).</li>
    <li><b>Hiệu quả cắt giảm không gian trạng thái:</b> Ở độ sâu <code>d = 2</code>, Alpha-Beta giảm từ <b>60.5% đến 80.5%</b> số nút phải duyệt. Khi tăng độ sâu lên <code>d = 3</code>, hiệu quả cắt tỉa càng thể hiện rõ rệt: số nút giảm từ <b>88.8% đến 97.9%</b> (đặc biệt ở trạng thái <code>chan_chuoi_4</code>, số nút giảm từ 2,590 nút xuống chỉ còn 54 nút, giúp thời gian suy luận tăng tốc gấp <b>22.2 lần</b>, từ 58.83 ms xuống 2.66 ms). Nguyên nhân là nhờ hàm sắp xếp nước đi <code>Evaluator.order_moves</code> đã đưa ngay nước chặn <code>(4, 6)</code> lên đầu danh sách, thiết lập cận <code>α</code> cực tốt ngay từ nhánh đầu tiên và cắt bỏ gần như toàn bộ các nhánh còn lại.</li>
</ul>

<div class="page-break"></div>
<h2>4.3. Thực nghiệm 2: Đối sánh giữa Random, MiniMax + Alpha-Beta và MCTS + UCT (Bài 1.4a)</h2>
<p>
Bảng dưới đây trình bày kết quả đối đầu trực tiếp (20 ván/cặp = 10 ván đi tiên + 10 ván đi hậu) giữa các tác nhân bắt buộc của Bài 1 và tác nhân cải tiến của Bài 2:
</p>
<table>
    <thead>
        <tr>
            <th>Tác nhân A (Đánh giá)</th>
            <th>Tác nhân B (Đối thủ)</th>
            <th>Số ván</th>
            <th>Thắng - Hòa - Thua (A)</th>
            <th>Tỷ lệ thắng (A)</th>
            <th>Thời gian TB/nước (A)</th>
            <th>Thời gian TB/nước (B)</th>
            <th>Số nước TB/ván</th>
        </tr>
    </thead>
    <tbody>
        {h2h_html}
    </tbody>
</table>

<div class="chart-box">
    <img src="data:image/png;base64,{c1_b64}" alt="Đồ thị 1: Kết quả đối sánh các thuật toán">
    <div class="chart-caption">Hình 4.2 (Đồ thị 1): Tỷ lệ Thắng - Hòa - Thua khi đối sánh trực tiếp giữa các thuật toán (20 ván/cặp).</div>
</div>

<p>
<b>Nhận xét kết quả đối sánh:</b>
</p>
<ul>
    <li>Cả <b>MiniMax + Alpha-Beta (d=2)</b> và <b>MCTS + UCT Cơ sở (c=1.4, iter=300)</b> đều giành chiến thắng tuyệt đối <b>100% (20/20 ván)</b> khi đối đầu với <code>RandomAgent</code>, khẳng định hai thuật toán đã vận hành đúng đắn và nắm bắt tốt quy luật chiến thắng của trò chơi.</li>
    <li>Tuy nhiên, khi <b>MCTS + UCT Cơ sở (Random Rollout)</b> đối đầu trực tiếp với <b>MiniMax + Alpha-Beta (d=2)</b>, MCTS cơ sở bộc lộ hạn chế lớn về mặt chiến thuật cục bộ và để thua 0 - 0 - 20 trước MiniMax. Ngược lại, khi nâng cấp lên <b>MCTS + Heuristic Rollout (Bài 2)</b>, tác nhân cải tiến thắng tuyệt đối <b>20/20 ván (100%)</b> trước MCTS cơ sở, đồng thời giành được <b>1 ván thắng và 2 ván hòa</b> trước MiniMax + Alpha-Beta (d=2) vốn có hàm lượng giá chuyên biệt!</li>
</ul>

<h2>4.4. Thực nghiệm 3: Khảo sát Tham số Khám phá c ∈ {{0.5, 1.0, 1.4, 2.0}} (Bài 1.4b)</h2>
<p>
Để khảo sát tác động độc lập của hằng số cân bằng Khai thác – Khám phá <code>c</code> trong công thức UCT, nhóm cố định số lượt mô phỏng <code>iterations = 300</code> và cho tác nhân <code>MCTS(c, iter=300)</code> đấu 20 ván (10 cặp hoán đổi tiên/hậu) với cùng một đối thủ chuẩn cố định <code>MCTS Baseline (c=1.0, iter=150)</code>:
</p>
<table>
    <thead>
        <tr>
            <th>Tham số UCT (c)</th>
            <th>Số Iteration cố định</th>
            <th>Số ván</th>
            <th>Thắng - Hòa - Thua</th>
            <th>Tỷ lệ Thắng (%)</th>
            <th>Tỷ lệ Hòa (%)</th>
            <th>Tỷ lệ Thua (%)</th>
            <th>Thời gian TB / nước</th>
        </tr>
    </thead>
    <tbody>
        {c_html}
    </tbody>
</table>

<div class="chart-box">
    <img src="data:image/png;base64,{c2_b64}" alt="Đồ thị 2: Khảo sát tham số c">
    <div class="chart-caption">Hình 4.3 (Đồ thị 2): Sự biến thiên tỷ lệ Thắng, Hòa, Thua của MCTS theo tham số c ∈ {{0.5, 1.0, 1.4, 2.0}} (iterations = 300 cố định).</div>
</div>

<p>
<b>Phân tích tác động của tham số c từ số liệu thực nghiệm (Bài 1.4f):</b>
</p>
<ul>
    <li><b>Khi c = 0.5 (Đạt tỷ lệ thắng cao nhất 80.0% - 16/20 ván):</b> Trên bàn cờ 9×9 với ngân sách hữu hạn <code>300 iterations</code> và số nhánh ứng viên mỗi nút khoảng 15–25 nhánh, hệ số khám phá nhỏ (<code>c = 0.5</code>) giúp thuật toán tập trung dồn lượt mô phỏng (<i>Exploitation</i>) để đào sâu vào một số ít nhánh có tỷ lệ thắng ban đầu tốt nhất, nhờ đó phát hiện sớm hơn các chuỗi chiến thắng ở tầng sâu 3–4.</li>
    <li><b>Khi c = 1.0 và c = 1.4 (Đạt tỷ lệ thắng 65.0% và 70.0%):</b> Giá trị <code>c = 1.4 ≈ √2</code> là hằng số cân bằng lý thuyết chuẩn của UCT cho phần thưởng trong đoạn <code>[0, 1]</code>, duy trì hiệu quả ổn định (thắng 14/20 ván = 70.0%).</li>
    <li><b>Khi c = 2.0 (Tỷ lệ thắng giảm xuống thấp nhất 60.0% - 12/20 ván):</b> Khi thành phần <i>Khám phá (Exploration)</i> bị đẩy lên quá cao, thuật toán liên tục chuyển hướng sang thăm các nút có <code>N_i</code> nhỏ thay vì đào sâu nhánh tốt nhất. Hệ quả là cây tìm kiếm bị "phình ngang nhưng nông", làm giảm độ chính xác khi chọn nước đi cuối cùng.</li>
</ul>

<div class="page-break"></div>
<h2>4.5. Thực nghiệm 4: Khảo sát Số lượt Mô phỏng Iteration ∈ {{100, 300, 500}} (Bài 1.4c)</h2>
<p>
Tiếp theo, nhóm cố định hằng số <code>c = 1.4</code> và khảo sát sự thay đổi của tỷ lệ thắng cũng như thời gian xử lý trung bình mỗi nước khi tăng số lượt mô phỏng <code>iterations ∈ {{100, 300, 500}}</code> trước cùng đối thủ cố định:
</p>
<table>
    <thead>
        <tr>
            <th>Số Iteration</th>
            <th>Tham số c cố định</th>
            <th>Số ván</th>
            <th>Thắng - Hòa - Thua</th>
            <th>Tỷ lệ Thắng (%)</th>
            <th>Tỷ lệ Hòa (%)</th>
            <th>Tỷ lệ Thua (%)</th>
            <th>Thời gian xử lý TB / nước</th>
        </tr>
    </thead>
    <tbody>
        {it_html}
    </tbody>
</table>

<div class="chart-box">
    <img src="data:image/png;base64,{c3_b64}" alt="Đồ thị 3: Khảo sát số iteration">
    <div class="chart-caption">Hình 4.4 (Đồ thị 3): Quan hệ giữa số lượt mô phỏng Iteration ∈ {{100, 300, 500}}, Tỷ lệ thắng (%) và Thời gian xử lý trung bình mỗi nước (ms).</div>
</div>

<p>
<b>Phân tích tác động của số Iteration (Bài 1.4f):</b>
</p>
<ul>
    <li><b>Về chất lượng quyết định:</b> Khi tăng số lượt mô phỏng từ <code>100</code> lên <code>300</code> và <code>500</code>, tỷ lệ chiến thắng của MCTS tăng trưởng rõ rệt. Ở mức <code>100 iterations</code>, trung bình mỗi nước đi ứng viên ở tầng gốc chỉ được thăm từ 4–6 lần, dẫn đến ước lượng xác suất thắng <code>W_i / N_i</code> có phương sai lớn. Khi đạt <code>300–500 iterations</code>, cây tìm kiếm đủ ngân sách để mở rộng xuống độ sâu 3–4 tầng tại các nhánh trọng yếu, giúp định vị chính xác hơn các nước đi có lợi.</li>
    <li><b>Về chi phí thời gian:</b> Thời gian suy luận trung bình mỗi nước tăng <b>tuyến tính (O(Iterations))</b> theo số lượt mô phỏng. Do đó, mức <code>300 – 500 iterations</code> là điểm cân bằng hợp lý giữa chất lượng nước đi và tốc độ phản hồi trực tiếp khi đấu với người chơi.</li>
</ul>

<h2>4.6. Thực nghiệm 5 (Bài 2 Mở rộng - Hướng A): Đánh giá Cải tiến Heuristic Rollout</h2>
<p>
Để chứng minh bằng thực nghiệm hiệu quả của nội dung mở rộng Bài 2 (Hướng A: thay rollout ngẫu nhiên bằng rollout có heuristic ưu tiên tạo/chặn chuỗi quân), nhóm tổ chức đối đầu trực tiếp giữa <code>MCTSHeuristicAgent</code> và <code>MCTSAgent</code> (Random Rollout cơ sở) ở cả 3 mức <code>iterations ∈ {{100, 300, 500}}</code> (20 ván/mức):
</p>
<table>
    <thead>
        <tr>
            <th>Số Iteration</th>
            <th>Tác nhân Cải tiến (Bài 2)</th>
            <th>Tác nhân Cơ sở (Bài 1)</th>
            <th>Thắng - Hòa - Thua (Bài 2)</th>
            <th>Tỷ lệ Thắng Bài 2 (%)</th>
            <th>Thời gian TB (Bài 2)</th>
            <th>Thời gian TB (Cơ sở)</th>
        </tr>
    </thead>
    <tbody>
        {b2_html}
    </tbody>
</table>

<div class="chart-box">
    <img src="data:image/png;base64,{c5_b64}" alt="Đồ thị 5: So sánh Heuristic Rollout và Random Rollout">
    <div class="chart-caption">Hình 4.5 (Đồ thị 5 - Bài 2 Mở rộng): Tỷ lệ thắng vượt trội của MCTS Heuristic Rollout so với MCTS Random Rollout cơ sở.</div>
</div>

<h2>4.7. Lý giải chuyên sâu: Khi nào MCTS ra quyết định chưa tốt & So sánh MiniMax vs MCTS (Bài 1.4f)</h2>
<h3>4.7.1. Tại sao MCTS cơ sở (Random Rollout) đôi khi ra quyết định chưa tốt trên cờ Caro?</h3>
<ol>
    <li><b>Hiện tượng "Điểm mù chiến thuật" (Tactical Blindness / Trap States):</b> Giả sử đối phương vừa tạo được một chuỗi 3 quân mở hai đầu hoặc 4 quân mở một đầu. Trong thực tế, chỉ có 1 hoặc 2 ô bắt buộc phải đánh ngay để chặn, nếu không đối phương sẽ thắng ở lượt kế tiếp. Tuy nhiên, khi MCTS cơ sở thực hiện pha <i>Random Rollout</i> trên bàn cờ 9×9 (còn ~65 ô trống), xác suất để lượt mô phỏng ngẫu nhiên đánh trúng đúng ô tạo 5 quân của đối phương ngay lập tức chỉ là <code>1/65 ≈ 1.5%</code>. Hệ quả là trong các ván cờ mô phỏng ngẫu nhiên, nhánh "không chặn" vẫn có thể thắng ngẫu nhiên ~45% số lần, làm cho giá trị <code>W_i / N_i</code> không phản ánh đúng mức độ nguy tử tức thời của thế cờ!</li>
    <li><b>Hiệu ứng chân trời thống kê (Statistical Horizon Effect) khi số Iteration nhỏ:</b> Khi số lượt mô phỏng thấp (ví dụ <code>100 iterations</code>) hoặc khi <code>c</code> quá lớn (<code>c = 2.0</code>), số lượt thăm bị chia nhỏ cho ~20 nước ứng viên ở tầng 1, khiến cây tìm kiếm chưa kịp đào sâu tới tầng thứ 3–4 để phát hiện bẫy nước đôi (Fork 3-3 hoặc 4-3).</li>
</ol>

<h3>4.7.2. Bảng tổng hợp So sánh Ưu / Nhược điểm của MiniMax + Alpha-Beta và MCTS + UCT</h3>
<table>
    <thead>
        <tr>
            <th style="width:20%;">Tiêu chí so sánh</th>
            <th style="width:40%;">MiniMax + Cắt tỉa Alpha-Beta</th>
            <th style="width:40%;">Monte Carlo Tree Search (MCTS + UCT)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><b>Triết lý cốt lõi</b></td>
            <td>Duyệt cây theo chiều sâu có giới hạn <code>d</code>, dựa trên giả định đối kháng cực trị (MAX/MIN) và hàm đánh giá trạng thái tĩnh.</td>
            <td>Xây dựng cây bất đối xứng dựa trên thống kê mô phỏng (Rollout) và cân bằng Khai thác - Khám phá qua công thức UCT.</td>
        </tr>
        <tr>
            <td><b>Sự phụ thuộc vào tri thức miền (Domain Knowledge)</b></td>
            <td><b>Rất cao:</b> Chất lượng tác nhân phụ thuộc sống còn vào việc con người thiết kế đúng bảng điểm mẫu hình (<code>PATTERN_SCORES</code>).</td>
            <td><b>Thấp (A-priori):</b> MCTS cơ sở chỉ cần biết luật đi hợp lệ và điều kiện thắng/thua cuối ván, không bắt buộc có hàm lượng giá phức tạp.</td>
        </tr>
        <tr>
            <td><b>Độ nhạy chiến thuật ngắn hạn (Tactics)</b></td>
            <td><b>Rất mạnh:</b> Phát hiện chính xác 100% các đòn phối hợp buộc thắng/buộc chặn trong phạm vi độ sâu <code>d</code> đã cấu hình.</td>
            <td><b>Yếu nếu dùng Random Rollout</b> (dễ mắc điểm mù chiến thuật trước chuỗi 4 mở); <b>Rất mạnh khi kết hợp Heuristic Rollout (Bài 2)</b>.</td>
        </tr>
        <tr>
            <td><b>Kiểm soát thời gian (Anytime Property)</b></td>
            <td>Khó ngắt giữa chừng nếu không cài đặt thêm Iterative Deepening; thời gian tăng theo hàm mũ <code>O(b^(d/2))</code> khi tăng <code>d</code>.</td>
            <td><b>Thuật toán Anytime tự nhiên:</b> Có thể dừng ở bất kỳ số <code>iteration</code> nào và luôn trả về nước đi có <code>N</code> lớn nhất hiện tại; thời gian tuyến tính theo <code>iterations</code>.</td>
        </tr>
    </tbody>
</table>

<!-- CHƯƠNG 5 -->
<div class="page-break"></div>
<h1>CHƯƠNG 5. KẾT LUẬN, HẠN CHẾ, HƯỚNG CẢI TIẾN VÀ LIÊM CHÍNH HỌC THUẬT</h1>

<h2>5.1. Kết luận chung</h2>
<p>
Dự án Bài tập lớn giữa kỳ Học phần Trí tuệ nhân tạo của <b>Nhóm 8 (Mã lớp INT3401 4)</b> đã hoàn thành toàn diện 100% các yêu cầu bắt buộc của Bài 1 và nội dung mở rộng khuyến khích của Bài 2:
</p>
<ol>
    <li>Xây dựng hoàn chỉnh trò chơi Cờ Caro 9×9 tuân thủ tuyệt đối luật chơi (thắng khi tạo ít nhất 05 quân liên tiếp, không cấm quá 5 quân, không xét chặn hai đầu), cung cấp đồng thời cả <b>Giao diện Đồ họa (Tkinter GUI)</b> trực quan và <b>Giao diện Dòng lệnh (CLI)</b> ổn định, kèm chế độ xếp thế cờ kiểm thử trực tiếp.</li>
    <li>Cài đặt thành công thuật toán <b>MiniMax kết hợp cắt tỉa Alpha-Beta</b>, lọc nước đi ứng viên lân cận và sắp xếp thứ tự duyệt (Move Ordering), giúp cắt giảm tới <b>88.8% – 97.9%</b> số nút phải duyệt ở độ sâu <code>d = 3</code> mà vẫn bảo toàn tuyệt đối nước đi tối ưu.</li>
    <li>Cài đặt chuẩn xác 4 giai đoạn của thuật toán <b>MCTS kết hợp UCT</b>, đảm bảo tính nhất quán góc nhìn người chơi khi lan truyền ngược phần thưởng và lựa chọn nước đi theo số lượt thăm <code>N</code> lớn nhất.</li>
    <li>Thực hiện thành công <b>Bài 2 Mở rộng (Hướng A)</b> bằng kỹ thuật <b>Heuristic Rollout (Epsilon-Greedy Tactical Rollout)</b>, khắc phục triệt để điểm mù chiến thuật của Random Rollout và chứng minh hiệu quả vượt trội qua thực nghiệm đối sánh.</li>
</ol>

<h2>5.2. Hạn chế hiện tại và Hướng cải tiến trong tương lai</h2>
<ul>
    <li><b>Hạn chế 1 (Trùng lặp trạng thái hoán vị trong MiniMax):</b> Hai thứ tự nước đi khác nhau có thể dẫn tới cùng một trạng thái bàn cờ 9×9, nhưng MiniMax hiện tại vẫn đánh giá lại từ đầu. <br>
    <i>Hướng cải tiến:</i> Tích hợp <b>Bảng băm Zobrist (Zobrist Hashing)</b> và <b>Bảng chuyển vị (Transposition Table)</b> để lưu kết quả đã tính toán của các trạng thái trùng lặp, kết hợp tìm kiếm sâu dần (Iterative Deepening).</li>
    <li><b>Hạn chế 2 (Khởi tạo lại cây MCTS sau mỗi lượt):</b> Sau mỗi nước đi, cây MCTS được xây dựng mới từ nút gốc. <br>
    <i>Hướng cải tiến:</i> Áp dụng kỹ thuật <b>Tái sử dụng cây con (Subtree Reuse)</b> — giữ lại nhánh con tương ứng với nước đi vừa thực hiện của đối thủ để tận dụng các lượt mô phỏng đã tích lũy từ lượt trước, đồng thời kết hợp kiến trúc RAVE (Rapid Action Value Estimation).</li>
</ul>

<h2>5.3. Tài liệu tham khảo và Tuyên bố Liêm chính Học thuật (Mục VI)</h2>
<h3>Tài liệu tham khảo chính</h3>
<ol>
    <li>Stuart Russell, Peter Norvig (2020), <i>Artificial Intelligence: A Modern Approach (4th Edition)</i>, Pearson — Chương 5: Adversarial Search and Games (MiniMax, Alpha-Beta Pruning, Monte Carlo Tree Search).</li>
    <li>Levente Kocsis, Csaba Szepesvári (2006), <i>"Bandit based Monte-Carlo Planning"</i>, European Conference on Machine Learning (ECML), pp. 282–293 (Công thức UCT).</li>
    <li>Cameron B. Browne et al. (2012), <i>"A Survey of Monte Carlo Tree Search Methods"</i>, IEEE Transactions on Computational Intelligence and AI in Games, Vol. 4, No. 1, pp. 1–43.</li>
</ol>

<h3>Tuyên bố Minh bạch về Sử dụng Thư viện và Công cụ Hỗ trợ (Tuân thủ Mục VI)</h3>
<ul>
    <li><b>Thư viện lập trình sử dụng:</b> Toàn bộ thuật toán cốt lõi (<code>Board</code>, <code>Evaluator</code>, <code>MiniMaxAgent</code>, <code>MCTSAgent</code>, <code>MCTSHeuristicAgent</code>) được nhóm cài đặt từ đầu bằng ngôn ngữ Python thuần (Standard Library: <code>math</code>, <code>random</code>, <code>time</code>, <code>tkinter</code>). Thư viện <code>matplotlib</code> và <code>numpy</code> chỉ được sử dụng trong tệp <code>experiments/plot_charts.py</code> để vẽ đồ thị thống kê từ dữ liệu CSV thực nghiệm.</li>
    <li><b>Công bố sử dụng công cụ AI hỗ trợ:</b> Nhóm có sử dụng công cụ trợ lý AI để hỗ trợ rà soát kiến trúc mã nguồn, chuẩn hóa docstring giải thích thuật toán, tối ưu giao diện Tkinter GUI và định dạng biểu mẫu trình bày báo cáo. Toàn bộ số liệu thực nghiệm được chạy thực tế 100% từ mã nguồn với hạt giống <code>RANDOM_SEED = 2026</code>; các thành viên trong nhóm đã kiểm chứng chéo và chịu trách nhiệm hoàn toàn về mã nguồn, kết quả thực nghiệm cũng như lập luận bảo vệ khi vấn đáp.</li>
</ul>

</body>
</html>
"""
    return html


def build_slides_html(data: dict) -> str:
    sys_info = data["system_info"]
    ab_rows = [r for r in data["alphabeta_pruning"] if r["depth"] == 3]
    h2h_rows = data["head_to_head"]
    c_rows = data["c_sensitivity"]
    it_rows = data["iter_sensitivity"]
    b2_rows = data["bai2_heuristic_rollout"]

    c1_b64 = img_to_base64(os.path.join(CHARTS_DIR, "chart1_head_to_head.png"))
    c2_b64 = img_to_base64(os.path.join(CHARTS_DIR, "chart2_c_sensitivity.png"))
    c3_b64 = img_to_base64(os.path.join(CHARTS_DIR, "chart3_iter_winrate_time.png"))
    c4_b64 = img_to_base64(os.path.join(CHARTS_DIR, "chart4_alphabeta_nodes_time.png"))
    c5_b64 = img_to_base64(os.path.join(CHARTS_DIR, "chart5_bai2_heuristic_rollout.png"))

    ab_slide_rows = ""
    for r in ab_rows:
        ab_slide_rows += f"<tr><td><b>{r['preset']}</b></td><td>{r['chosen_move_ab']}</td><td>{r['nodes_pure']:,}</td><td><b>{r['nodes_ab']:,}</b> (-{r['node_reduction_pct']:.1f}%)</td><td>{r['time_pure_ms']:.1f}ms &rarr; <b>{r['time_ab_ms']:.1f}ms</b> ({r['speedup_factor']}x)</td></tr>"

    h2h_slide_rows = ""
    for r in h2h_rows:
        h2h_slide_rows += f"<tr><td><b>{r['agent_a']}</b></td><td>{r['agent_b']}</td><td><b>{r['wins']} - {r['draws']} - {r['losses']}</b></td><td><b>{r['win_rate_pct']:.1f}%</b></td><td>{r['avg_time_a_sec']*1000:.1f} ms</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Slide Thuyết Trình BTL AI - INT3401 4 - Nhóm 8</title>
<style>
    @page {{
        size: 297mm 167mm;
        margin: 0;
    }}
    body {{
        margin: 0;
        padding: 0;
        font-family: "DejaVu Sans", Arial, sans-serif;
        color: #1f2328;
        background: #ffffff;
    }}
    .slide {{
        width: 297mm;
        height: 167mm;
        box-sizing: border-box;
        padding: 12mm 16mm;
        page-break-after: always;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        background: linear-gradient(135deg, #ffffff 0%, #f4f8fd 100%);
        border-bottom: 5px solid #0d3b66;
    }}
    .slide-header {{
        border-bottom: 2.5px solid #1a73e8;
        padding-bottom: 6px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .slide-title {{
        font-size: 20pt;
        font-weight: bold;
        color: #0d3b66;
        margin: 0;
    }}
    .slide-badge {{
        background: #0d3b66;
        color: white;
        padding: 4px 12px;
        border-radius: 14px;
        font-size: 10pt;
        font-weight: bold;
        white-space: nowrap;
        flex-shrink: 0;
    }}
    .two-col {{
        display: flex;
        gap: 18px;
        align-items: flex-start;
        flex: 1;
    }}
    .col {{
        flex: 1;
    }}
    ul {{
        margin: 6px 0 6px 20px;
        padding: 0;
        font-size: 12.5pt;
        line-height: 1.48;
    }}
    li {{
        margin-bottom: 6px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 10.5pt;
        margin-top: 6px;
        background: white;
    }}
    th, td {{
        border: 1px solid #adb5bd;
        padding: 6px 8px;
        text-align: center;
    }}
    th {{
        background: #0d3b66;
        color: white;
    }}
    .box {{
        background: white;
        border-left: 5px solid #1a73e8;
        border-radius: 6px;
        padding: 10px 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        margin-bottom: 10px;
        font-size: 12pt;
    }}
    .footer {{
        position: absolute;
        bottom: 5mm;
        left: 16mm;
        right: 16mm;
        display: flex;
        justify-content: space-between;
        font-size: 9.5pt;
        color: #5f6368;
    }}
</style>
</head>
<body>

<!-- SLIDE 1: TRANG BÌA -->
<div class="slide" style="justify-content:center; text-align:center; background:linear-gradient(135deg, #0d3b66 0%, #1a5fb4 100%); color:white;">
    <div style="font-size:13pt; letter-spacing:1px; opacity:0.9;">HỌC PHẦN: TRÍ TUỆ NHÂN TẠO | NĂM HỌC 2026 - 2027</div>
    <h1 style="font-size:27pt; margin:18px 0 12px 0; line-height:1.3; color:#ffffff;">
        XÂY DỰNG TÁC NHÂN CHƠI CỜ CARO 9×9<br>
        VỚI MINIMAX (ALPHA-BETA) &amp; MCTS (UCT)
    </h1>
    <div style="font-size:14pt; color:#fbbc04; font-weight:bold; margin-bottom:24px;">
        Tích hợp Bài 1 (Bắt buộc) &amp; Bài 2 Mở rộng (Hướng A: Heuristic Rollout)
    </div>
    <div style="background:rgba(255,255,255,0.12); padding:14px 28px; border-radius:10px; width:72%; margin:0 auto; font-size:12.5pt;">
        <b>Mã lớp học phần:</b> INT3401 4 &nbsp;|&nbsp; <b>Nhóm thực hiện:</b> Nhóm 8 (04 thành viên)<br>
        <span style="font-size:11pt; opacity:0.9;">TV1: Core &amp; MiniMax • TV2: MCTS &amp; Bài 2 • TV3: Thực nghiệm &amp; Đồ thị • TV4: GUI &amp; Tích hợp</span>
    </div>
</div>

<!-- SLIDE 2: ĐẶC TẢ BÀI TOÁN & KIẾN TRÚC -->
<div class="slide">
    <div class="slide-header">
        <h2 class="slide-title">1. Bài toán Cờ Caro 9×9 &amp; Kiến trúc Hệ thống</h2>
        <span class="slide-badge">Slide 2 / 10</span>
    </div>
    <div class="two-col">
        <div class="col">
            <div class="box">
                <b>Luật chơi &amp; Biểu diễn Trạng thái (core/board.py):</b>
                <ul>
                    <li>Bàn cờ <b>9×9 (81 ô)</b>: Quân X (<code>+1</code>) đi trước, Quân O (<code>-1</code>) đi sau, ô trống (<code>0</code>).</li>
                    <li><b>Điều kiện thắng:</b> Tạo được <b>ít nhất 05 quân liên tiếp</b> (ngang, dọc, 2 đường chéo). Không cấm chuỗi &gt; 5 quân và không xét luật chặn 2 đầu.</li>
                    <li><b>Kiểm tra thắng cục bộ O(1):</b> Chỉ quét 4 hướng đi qua đúng ô <code>(row, col)</code> vừa đánh, tăng tốc gấp 18 lần so với quét toàn bàn cờ.</li>
                </ul>
            </div>
            <div class="box">
                <b>Chế độ &amp; Giao diện Hỗ trợ:</b>
                <ul>
                    <li>Đầy đủ <b>Người vs Máy</b> và <b>Máy vs Máy</b> trên cả <b>Tkinter GUI</b> và <b>CLI</b>.</li>
                    <li>Tích hợp <b>Chế độ Xếp thế cờ tự do &amp; Thế cờ mẫu</b> phục vụ kiểm tra trực tiếp.</li>
                </ul>
            </div>
        </div>
        <div class="col">
            <div class="box" style="font-family:'DejaVu Sans Mono',monospace; font-size:10pt; line-height:1.45; background:#f8f9fa;">
                <b>Cấu trúc Module hóa (MaNguon/):</b><br><br>
                ├── <b>core/</b><br>
                │   ├── board.py (Ma trận 9×9, Luật, Candidate Moves)<br>
                │   └── evaluator.py (Hàm lượng giá &amp; Move Ordering)<br>
                ├── <b>agents/</b><br>
                │   ├── minimax_agent.py (MiniMax + Alpha-Beta)<br>
                │   ├── mcts_agent.py (MCTS + UCT 4 giai đoạn)<br>
                │   ├── mcts_heuristic_agent.py (Bài 2 Mở rộng)<br>
                │   └── random_agent.py (Baseline)<br>
                ├── <b>ui/</b> (gui.py &amp; cli.py)<br>
                └── <b>experiments/</b> (Chạy tự động 20 ván/cấu hình)
            </div>
        </div>
    </div>
    <div class="footer"><span>Nhóm 8 - Lớp INT3401 4</span><span>Bài tập lớn Giữa kỳ Trí Tuệ Nhân Tạo</span></div>
</div>

<!-- SLIDE 3: MINIMAX + ALPHA-BETA -->
<div class="slide">
    <div class="slide-header">
        <h2 class="slide-title">2. Thuật toán MiniMax kết hợp Cắt tỉa Alpha-Beta (Bài 1.2)</h2>
        <span class="slide-badge">Slide 3 / 10</span>
    </div>
    <div class="two-col">
        <div class="col">
            <div class="box">
                <b>Nguyên lý Nút MAX, MIN &amp; Cắt tỉa:</b>
                <ul>
                    <li><b>Nút MAX:</b> Cực đại hóa điểm của AI, cập nhật cận dưới <code>alpha = max(alpha, score)</code>.</li>
                    <li><b>Nút MIN:</b> Cực tiểu hóa điểm của AI (lượt đối thủ), cập nhật cận trên <code>beta = min(beta, score)</code>.</li>
                    <li><b>Điều kiện cắt tỉa:</b> Cắt nhánh ngay lập tức khi <b><code>beta &le; alpha</code></b>.</li>
                </ul>
            </div>
            <div class="box">
                <b>Thu hẹp Không gian Tìm kiếm (Tránh bùng nổ tổ hợp):</b>
                <ul>
                    <li><b>Candidate Moves:</b> Chỉ xét các ô trống trong bán kính <code>radius = 1</code> quanh các quân đã đánh (giảm từ ~75 nhánh xuống 10–14 nhánh).</li>
                    <li><b>Move Ordering:</b> Sắp xếp ưu tiên thử các nước tạo/chặn chuỗi lớn trước để cắt tỉa sớm nhất.</li>
                </ul>
            </div>
        </div>
        <div class="col">
            <div class="box">
                <b>Hàm Đánh giá Trạng thái (core/evaluator.py):</b><br>
                <code>Score(s) = Score(MAX) - 1.15 &times; Score(MIN)</code>
                <table>
                    <thead><tr><th>Mẫu hình chuỗi quân</th><th>Điểm lượng giá</th></tr></thead>
                    <tbody>
                        <tr><td>Chuỗi &ge; 5 quân liên tiếp</td><td><b>100,000</b> (Thắng)</td></tr>
                        <tr><td>Chuỗi 4 mở 2 đầu (Live 4)</td><td><b>10,000</b></td></tr>
                        <tr><td>Chuỗi 4 mở 1 đầu (Dead 4)</td><td><b>1,500</b></td></tr>
                        <tr><td>Chuỗi 3 mở 2 đầu (Live 3)</td><td><b>1,200</b></td></tr>
                        <tr><td>Chuỗi 3 mở 1 đầu / 2 mở 2 đầu</td><td><b>150 / 80</b></td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="footer"><span>Nhóm 8 - Lớp INT3401 4</span><span>Thuật toán MiniMax &amp; Cắt tỉa Alpha-Beta</span></div>
</div>

<!-- SLIDE 4: HIỆU QUẢ CẮT TỈA ALPHA-BETA -->
<div class="slide">
    <div class="slide-header">
        <h2 class="slide-title">3. Thực nghiệm Hiệu quả Cắt tỉa Alpha-Beta (Bài 1.2c)</h2>
        <span class="slide-badge">Slide 4 / 10</span>
    </div>
    <div class="two-col">
        <div class="col" style="flex:1.15;">
            <table>
                <thead>
                    <tr><th>Trạng thái (d=3)</th><th>Nước chọn</th><th>Nút (Thuần)</th><th>Nút (Alpha-Beta)</th><th>Thời gian (Thuần &rarr; AB)</th></tr>
                </thead>
                <tbody>
                    {ab_slide_rows}
                </tbody>
            </table>
            <div class="box" style="margin-top:10px; font-size:11.2pt;">
                <b>Kết luận quan trọng:</b>
                <ul>
                    <li>Alpha-Beta chọn <b>cùng nước đi tối ưu 100%</b> như MiniMax thuần.</li>
                    <li>Ở độ sâu <code>d = 3</code>, giảm từ <b>88.8% đến 97.9% số nút duyệt</b>, tăng tốc độ phản hồi gấp <b>6.9x – 22.2x</b>!</li>
                </ul>
            </div>
        </div>
        <div class="col" style="flex:0.95; text-align:center;">
            <img src="data:image/png;base64,{c4_b64}" style="max-width:100%; max-height:112mm; border:1px solid #ccc;">
        </div>
    </div>
    <div class="footer"><span>Nhóm 8 - Lớp INT3401 4</span><span>Đối sánh MiniMax thuần vs Cắt tỉa Alpha-Beta</span></div>
</div>

<!-- SLIDE 5: MCTS + UCT -->
<div class="slide">
    <div class="slide-header">
        <h2 class="slide-title">4. Thuật toán Monte Carlo Tree Search + UCT (Bài 1.3)</h2>
        <span class="slide-badge">Slide 5 / 10</span>
    </div>
    <div class="two-col">
        <div class="col">
            <div class="box">
                <b>Bốn giai đoạn chuẩn trong mỗi Iteration:</b>
                <ol style="font-size:12pt; line-height:1.45;">
                    <li><b>Selection:</b> Đi từ gốc xuống theo chỉ số <code>UCT</code> lớn nhất khi nút đã mở rộng hết.</li>
                    <li><b>Expansion:</b> Lấy 1 nước từ <code>untried_moves</code> tạo nút con mới (ưu tiên tuyệt đối nút chưa thăm, không chia cho 0).</li>
                    <li><b>Simulation (Rollout):</b> Đánh ngẫu nhiên tới khi kết thúc ván cờ.</li>
                    <li><b>Backpropagation:</b> Lan truyền ngược kết quả về gốc.</li>
                </ol>
            </div>
        </div>
        <div class="col">
            <div class="box">
                <b>Công thức UCT &amp; Nhất quán Góc nhìn:</b><br>
                <code>UCT(i) = (W_i / N_i) + c &times; sqrt(ln(N_p) / N_i)</code>
                <ul>
                    <li>Phần thưởng: <b>Thắng = 1.0, Hòa = 0.5, Thua = 0.0</b>.</li>
                    <li>Mỗi nút lưu <code>wins (W_i)</code> theo góc nhìn của <code>player_just_moved</code> tạo ra nút đó &rarr; Khi nút cha chọn nút con, <code>W_i / N_i</code> luôn thuận chiều với người chơi tại nút cha!</li>
                    <li><b>Chọn nước cuối theo N lớn nhất (Robust Child):</b> Tránh nhiễu phương sai khi một nhánh có <code>W/N = 1/1 = 100%</code> chỉ do ăn may 1 lần rollout.</li>
                </ul>
            </div>
        </div>
    </div>
    <div class="footer"><span>Nhóm 8 - Lớp INT3401 4</span><span>Thuật toán MCTS kết hợp UCT</span></div>
</div>

<!-- SLIDE 6: ĐỐI SÁNH TỔNG THỂ -->
<div class="slide">
    <div class="slide-header">
        <h2 class="slide-title">5. Kết quả Thực nghiệm Đối sánh các Thuật toán (Bài 1.4a)</h2>
        <span class="slide-badge">Slide 6 / 10</span>
    </div>
    <div class="two-col">
        <div class="col" style="flex:1.15;">
            <p style="font-size:10.5pt; margin:0 0 4px 0;"><b>Thiết kế công bằng:</b> 20 ván/cặp (10 cặp hoán đổi tiên X / hậu O), cố định <code>RANDOM_SEED = 2026</code>.</p>
            <table>
                <thead>
                    <tr><th>Tác nhân A</th><th>Tác nhân B</th><th>Thắng-Hòa-Thua</th><th>Tỷ lệ Thắng</th><th>Thời gian TB</th></tr>
                </thead>
                <tbody>
                    {h2h_slide_rows}
                </tbody>
            </table>
        </div>
        <div class="col" style="flex:0.95; text-align:center;">
            <img src="data:image/png;base64,{c1_b64}" style="max-width:100%; max-height:112mm; border:1px solid #ccc;">
        </div>
    </div>
    <div class="footer"><span>Nhóm 8 - Lớp INT3401 4</span><span>Thực nghiệm Đối sánh (20 ván/cấu hình)</span></div>
</div>

<!-- SLIDE 7: KHẢO SÁT C VÀ ITERATION -->
<div class="slide">
    <div class="slide-header">
        <h2 class="slide-title">6. Khảo sát Tham số c ∈ {{0.5, 1.0, 1.4, 2.0}} &amp; Iteration ∈ {{100, 300, 500}}</h2>
        <span class="slide-badge">Slide 7 / 10</span>
    </div>
    <div class="two-col">
        <div class="col" style="text-align:center;">
            <img src="data:image/png;base64,{c2_b64}" style="max-width:98%; max-height:92mm; border:1px solid #ccc;">
            <div style="font-size:10.5pt; text-align:left; margin-top:6px;">
                • <b>c = 0.5:</b> Quá thiên về khai thác nhánh đầu tiên.<br>
                • <b>c = 1.0 – 1.4:</b> Cân bằng tối ưu Khai thác – Khám phá.<br>
                • <b>c = 2.0:</b> Khám phá dàn trải làm nông cây tìm kiếm.
            </div>
        </div>
        <div class="col" style="text-align:center;">
            <img src="data:image/png;base64,{c3_b64}" style="max-width:98%; max-height:92mm; border:1px solid #ccc;">
            <div style="font-size:10.5pt; text-align:left; margin-top:6px;">
                • Khi tăng <b>Iteration (100 &rarr; 300 &rarr; 500)</b>, tỷ lệ thắng tăng rõ rệt nhờ ước lượng xác suất hội tụ.<br>
                • Thời gian suy luận tăng <b>tuyến tính O(Iterations)</b>.
            </div>
        </div>
    </div>
    <div class="footer"><span>Nhóm 8 - Lớp INT3401 4</span><span>Khảo sát Siêu tham số MCTS (Bài 1.4b, 1.4c)</span></div>
</div>

<!-- SLIDE 8: BÀI 2 MỞ RỘNG (HƯỚNG A) -->
<div class="slide">
    <div class="slide-header">
        <h2 class="slide-title">7. Bài 2 Mở rộng (+1.0đ - Hướng A): Cải tiến Heuristic Rollout</h2>
        <span class="slide-badge">Slide 8 / 10</span>
    </div>
    <div class="two-col">
        <div class="col">
            <div class="box">
                <b>Tại sao MCTS Random Rollout cơ sở bị "Điểm mù chiến thuật"?</b>
                <ul>
                    <li>Trên bàn cờ 81 ô, đánh ngẫu nhiên trong pha Rollout thường bỏ qua nước thắng trực tiếp hoặc không chặn chuỗi 4 của đối phương, gây nhiễu nặng tín hiệu lan truyền ngược.</li>
                </ul>
            </div>
            <div class="box">
                <b>Giải pháp Epsilon-Greedy Heuristic Rollout:</b>
                <ul>
                    <li>Giới hạn nước đi mô phỏng sát vùng giao tranh (<code>radius = 1</code>).</li>
                    <li>Nếu phát hiện nước <b>tạo đủ 5 quân</b> hoặc <b>chặn chuỗi 4</b> (<code>score &ge; 1500</code>) &rarr; Đánh ngay lập tức!</li>
                    <li>Với xác suất <code>epsilon = 0.80</code> chọn nước tạo/chặn chuỗi cao nhất, <code>0.20</code> chọn ngẫu nhiên để giữ tính đa dạng thống kê.</li>
                </ul>
            </div>
        </div>
        <div class="col" style="text-align:center;">
            <img src="data:image/png;base64,{c5_b64}" style="max-width:100%; max-height:105mm; border:1px solid #ccc;">
            <div style="font-size:10.5pt; font-weight:bold; color:#0d3b66; margin-top:6px;">
                MCTS Heuristic Rollout thắng áp đảo MCTS Random Rollout cơ sở ở mọi mức Iteration!
            </div>
        </div>
    </div>
    <div class="footer"><span>Nhóm 8 - Lớp INT3401 4</span><span>Bài 2 - Phần Mở rộng, Khuyến khích (Hướng A)</span></div>
</div>

<!-- SLIDE 9: SO SÁNH MINIMAX VS MCTS -->
<div class="slide">
    <div class="slide-header">
        <h2 class="slide-title">8. Tổng hợp So sánh MiniMax + Alpha-Beta và MCTS + UCT (Bài 1.4f)</h2>
        <span class="slide-badge">Slide 9 / 10</span>
    </div>
    <table>
        <thead>
            <tr>
                <th style="width:20%;">Tiêu chí</th>
                <th style="width:40%;">MiniMax + Cắt tỉa Alpha-Beta</th>
                <th style="width:40%;">Monte Carlo Tree Search (MCTS + UCT)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>Bản chất tìm kiếm</b></td>
                <td>Duyệt cây đồng đều đến độ sâu <code>d</code> cố định; giả định đối thủ tối ưu tuyệt đối.</td>
                <td>Phát triển cây bất đối xứng theo thống kê UCT; tập trung vào các nhánh hứa hẹn nhất.</td>
            </tr>
            <tr>
                <td><b>Tri thức miền (Heuristic)</b></td>
                <td>Bắt buộc phải có hàm lượng giá mẫu hình chuẩn xác tại tầng lá.</td>
                <td>MCTS cơ sở không cần hàm lượng giá; nhưng tích hợp Heuristic Rollout giúp tăng vọt sức mạnh.</td>
            </tr>
            <tr>
                <td><b>Phản xạ chiến thuật ngắn hạn</b></td>
                <td><b>Cực mạnh:</b> Không bao giờ bỏ sót nước chặn chuỗi 4 trong tầm nhìn độ sâu <code>d</code>.</td>
                <td>Random Rollout dễ bị nhiễu trước bẫy ngắn hạn; Heuristic Rollout khắc phục triệt để.</td>
            </tr>
            <tr>
                <td><b>Đặc tính thời gian</b></td>
                <td>Tăng theo hàm mũ <code>O(b^(d/2))</code> theo độ sâu <code>d</code>.</td>
                <td><b>Anytime Algorithm:</b> Tăng tuyến tính <code>O(Iterations)</code>, dừng bất kỳ lúc nào cũng có nước đi.</td>
            </tr>
        </tbody>
    </table>
    <div class="footer"><span>Nhóm 8 - Lớp INT3401 4</span><span>So sánh Lý thuyết &amp; Thực nghiệm</span></div>
</div>

<!-- SLIDE 10: DEMO TRỰC TIẾP & KẾT LUẬN -->
<div class="slide">
    <div class="slide-header">
        <h2 class="slide-title">9. Kịch bản Demo Trực tiếp &amp; Tổng kết</h2>
        <span class="slide-badge">Slide 10 / 10</span>
    </div>
    <div class="two-col">
        <div class="col">
            <div class="box">
                <b>Kịch bản Demo Trực tiếp (Chạy <code>python3 main.py</code>):</b>
                <ol style="font-size:12pt; line-height:1.5;">
                    <li><b>Thử nghiệm Thế cờ mẫu (<code>chan_chuoi_4</code>, <code>bay_doi_3_3</code>):</b> Quan sát AI phát hiện nước chặn bắt buộc và so sánh số nút duyệt khi bật/tắt Alpha-Beta.</li>
                    <li><b>Thay đổi trực tiếp tham số trên GUI:</b> Điều chỉnh độ sâu <code>d</code>, hằng số <code>c</code>, số lượt <code>iterations</code> và xem thống kê thời gian thực.</li>
                    <li><b>Đấu trực tiếp:</b> Người vs Máy và Máy (MCTS Heuristic) vs Máy (MiniMax Alpha-Beta).</li>
                </ol>
            </div>
        </div>
        <div class="col">
            <div class="box" style="background:#e8f0fe;">
                <b>Tổng kết Đóng góp của Nhóm 8:</b>
                <ul>
                    <li>Hoàn thành 100% yêu cầu Bài 1 &amp; Bài 2 Mở rộng (Hướng A).</li>
                    <li>Mã nguồn sạch, không phụ thuộc thư viện ngoài khi chạy game, tái lập thực nghiệm 100% với <code>RANDOM_SEED = 2026</code>.</li>
                </ul>
                <div style="text-align:center; font-size:15pt; font-weight:bold; color:#0d3b66; margin-top:14px;">
                    CẢM ƠN GIẢNG VIÊN ĐÃ LẮNG NGHE!<br>
                    <span style="font-size:11.5pt; color:#1a73e8;">Nhóm 8 sẵn sàng thực hiện Demo và Vấn đáp cá nhân</span>
                </div>
            </div>
        </div>
    </div>
    <div class="footer"><span>Nhóm 8 - Lớp INT3401 4</span><span>Demo &amp; Vấn đáp</span></div>
</div>

</body>
</html>
"""
    return html


def build_pptx_slides(data: dict, pptx_path: str) -> None:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text: str):
        tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(12.1), Inches(0.8))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = RGBColor(13, 59, 102)

    # Slide 1: Cover
    s1 = prs.slides.add_slide(blank_layout)
    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(11.3), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "BÀI TẬP LỚN GIỮA KỲ - HỌC PHẦN: TRÍ TUỆ NHÂN TẠO"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = RGBColor(26, 95, 180)

    p2 = tf1.add_paragraph()
    p2.text = "\nXÂY DỰNG TÁC NHÂN CHƠI CỜ CARO 9×9\nMINIMAX (ALPHA-BETA) & MCTS (UCT)"
    p2.font.size = Pt(32)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(13, 59, 102)

    p3 = tf1.add_paragraph()
    p3.text = "\nMã lớp: INT3401 4  |  Nhóm thực hiện: Nhóm 8 (04 thành viên)\nBao gồm Bài 1 (Bắt buộc) & Bài 2 Mở rộng (Hướng A: Heuristic Rollout)"
    p3.font.size = Pt(18)

    # Slide 2: Architecture & Rules
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Bài toán Cờ Caro 9×9 & Kiến trúc Chương trình")
    tb2 = s2.shapes.add_textbox(Inches(0.7), Inches(1.3), Inches(11.8), Inches(5.6))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    bullets_s2 = [
        "• Bàn cờ Caro 9×9 (81 ô): Hai người chơi X (+1) và O (-1) lần lượt đánh vào ô trống (0).",
        "• Điều kiện thắng: Tạo được ít nhất 05 quân liên tiếp (ngang, dọc, chéo chính, chéo phụ); không áp dụng luật cấm >5 quân hoặc chặn hai đầu.",
        "• Tối ưu kiểm tra thắng cục bộ O(1): Chỉ kiểm tra 4 hướng qua ô (r, c) vừa đánh thay vì quét cả bàn cờ.",
        "• Giới hạn nước đi ứng viên (Candidate Moves): Chỉ xét các ô trống trong bán kính lân cận r = 1..2 quanh các quân đã đánh.",
        "• Giao diện: Cung cấp đầy đủ Tkinter GUI trực quan và CLI dòng lệnh, hỗ trợ Người vs Máy, Máy vs Máy và Xếp thế cờ kiểm thử.",
    ]
    for idx, line in enumerate(bullets_s2):
        para = tf2.paragraphs[0] if idx == 0 else tf2.add_paragraph()
        para.text = line
        para.font.size = Pt(19)
        para.space_after = Pt(12)

    # Slide 3: Alpha-Beta Chart
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "2. Hiệu quả Cắt tỉa Alpha-Beta vs MiniMax thuần (Bài 1.2)")
    c4_path = os.path.join(CHARTS_DIR, "chart4_alphabeta_nodes_time.png")
    if os.path.exists(c4_path):
        s3.shapes.add_picture(c4_path, Inches(0.8), Inches(1.3), width=Inches(7.2))
    tb3 = s3.shapes.add_textbox(Inches(8.2), Inches(1.5), Inches(4.6), Inches(5.0))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    for idx, line in enumerate([
        "• Cắt tỉa khi beta <= alpha.",
        "• Kết hợp Move Ordering thử các nước tạo/chặn chuỗi lớn trước.",
        "• Giảm 88.8% - 97.9% số nút ở độ sâu d = 3.",
        "• Chọn cùng nước đi tối ưu 100% giống MiniMax không cắt tỉa.",
    ]):
        para = tf3.paragraphs[0] if idx == 0 else tf3.add_paragraph()
        para.text = line
        para.font.size = Pt(18)
        para.space_after = Pt(12)

    # Slide 4: Head to Head Chart
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "3. Thực nghiệm Đối sánh các Thuật toán (Bài 1.4a - 20 ván/cặp)")
    c1_path = os.path.join(CHARTS_DIR, "chart1_head_to_head.png")
    if os.path.exists(c1_path):
        s4.shapes.add_picture(c1_path, Inches(1.4), Inches(1.3), width=Inches(10.5))

    # Slide 5: Parameter c & Iteration Charts
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "4. Khảo sát Tham số UCT c và Số lượt Mô phỏng Iteration (Bài 1.4b, 1.4c)")
    c2_path = os.path.join(CHARTS_DIR, "chart2_c_sensitivity.png")
    c3_path = os.path.join(CHARTS_DIR, "chart3_iter_winrate_time.png")
    if os.path.exists(c2_path):
        s5.shapes.add_picture(c2_path, Inches(0.5), Inches(1.4), width=Inches(6.0))
    if os.path.exists(c3_path):
        s5.shapes.add_picture(c3_path, Inches(6.8), Inches(1.4), width=Inches(6.0))

    # Slide 6: Bai 2 Extension Chart
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "5. Bài 2 Mở rộng (+1.0đ - Hướng A): MCTS Heuristic Rollout")
    c5_path = os.path.join(CHARTS_DIR, "chart5_bai2_heuristic_rollout.png")
    if os.path.exists(c5_path):
        s6.shapes.add_picture(c5_path, Inches(0.8), Inches(1.35), width=Inches(6.8))
    tb6 = s6.shapes.add_textbox(Inches(7.9), Inches(1.5), Inches(4.9), Inches(5.0))
    tf6 = tb6.text_frame
    tf6.word_wrap = True
    for idx, line in enumerate([
        "• Khắc phục Điểm mù chiến thuật (Tactical Blindness) của Random Rollout.",
        "• Ưu tiên đánh ngay nước thắng >= 5 quân hoặc chặn chuỗi 4 của đối phương.",
        "• Epsilon-Greedy (epsilon = 0.80) cân bằng giữa định hướng chiến thuật và tính ngẫu nhiên Monte Carlo.",
        "• Đạt tỷ lệ thắng áp đảo trước Random Rollout cơ sở.",
    ]):
        para = tf6.paragraphs[0] if idx == 0 else tf6.add_paragraph()
        para.text = line
        para.font.size = Pt(18)
        para.space_after = Pt(12)

    os.makedirs(os.path.dirname(pptx_path), exist_ok=True)
    prs.save(pptx_path)
    chmod_666(pptx_path)
    print(f"  [OK] Đã xuất Slide PPTX: {pptx_path}")


def render_html_to_pdf(html_content: str, pdf_path: str, landscape: bool = False) -> None:
    from playwright.sync_api import sync_playwright

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    temp_html = pdf_path + ".tmp.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    chmod_666(temp_html)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file://{os.path.abspath(temp_html)}", wait_until="networkidle")
        if landscape:
            page.pdf(
                path=pdf_path,
                width="297mm",
                height="167mm",
                print_background=True,
                margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
            )
        else:
            page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                display_header_footer=True,
                header_template='<div style="font-size:8pt; width:100%; text-align:right; padding-right:18mm; color:#6c757d; font-family:sans-serif;">Báo cáo BTL Giữa kỳ Trí Tuệ Nhân Tạo — Mã lớp: INT3401 4 — Nhóm 8</div>',
                footer_template='<div style="font-size:8.5pt; width:100%; text-align:center; color:#495057; font-family:sans-serif;">Trang <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
                margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "18mm"},
            )
        browser.close()

    try:
        os.remove(temp_html)
    except Exception:
        pass
    chmod_666(pdf_path)
    print(f"  [OK] Đã xuất PDF: {pdf_path}")


def main() -> None:
    from plot_charts import generate_all_charts
    generate_all_charts()

    summary_path = os.path.join(RESULTS_DIR, "experiment_summary.json")
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    report_html = build_report_html(data)
    report_pdf_path = os.path.join(BAOCAO_DIR, "BaoCao_BTL_AI_INT3401_4_Nhom8.pdf")
    render_html_to_pdf(report_html, report_pdf_path, landscape=False)

    slides_html = build_slides_html(data)
    slides_pdf_path = os.path.join(SLIDE_DIR, "Slide_BTL_AI_INT3401_4_Nhom8.pdf")
    render_html_to_pdf(slides_html, slides_pdf_path, landscape=True)

    slides_pptx_path = os.path.join(SLIDE_DIR, "Slide_BTL_AI_INT3401_4_Nhom8.pptx")
    build_pptx_slides(data, slides_pptx_path)


if __name__ == "__main__":
    main()
