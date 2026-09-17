# -*- coding: utf-8 -*-
"""
content_cover.py
Xây dựng Trang bìa, Bìa phụ, Phân công nhiệm vụ, Lời cảm ơn, Danh mục từ viết tắt, Danh mục bảng biểu và hình vẽ.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from make_full_report import (
    FONT_NAME, BLACK, set_run_font, add_p, add_heading_1, add_heading_2, 
    add_bullet, add_styled_table
)

def build_cover_and_preamble(doc):
    # TRANG BÌA CHÍNH
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_uni.paragraph_format.space_before = Pt(0)
    p_uni.paragraph_format.space_after = Pt(2)
    r = p_uni.add_run("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ ĐÔNG Á\nKHOA CÔNG NGHỆ THÔNG TIN")
    set_run_font(r, FONT_NAME, 14, bold=True, color=BLACK)
    
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_before = Pt(0)
    p_line.paragraph_format.space_after = Pt(40)
    r = p_line.add_run("--------------------***--------------------")
    set_run_font(r, FONT_NAME, 12, bold=True, color=BLACK)
    
    p_btl = doc.add_paragraph()
    p_btl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_btl.paragraph_format.space_before = Pt(20)
    p_btl.paragraph_format.space_after = Pt(12)
    r = p_btl.add_run("BÀI TẬP LỚN\nHỌC PHẦN: TRÍ TUỆ NHÂN TẠO")
    set_run_font(r, FONT_NAME, 16, bold=True, color=BLACK)
    
    p_de = doc.add_paragraph()
    p_de.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_de.paragraph_format.space_before = Pt(6)
    p_de.paragraph_format.space_after = Pt(16)
    r = p_de.add_run("MÃ ĐỀ TÀI: 32")
    set_run_font(r, FONT_NAME, 14, bold=True, color=BLACK)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(40)
    p_title.paragraph_format.line_spacing = 1.3
    r = p_title.add_run("ĐỀ TÀI:\nXÂY DỰNG CHƯƠNG TRÌNH HỎI ĐÁP BẰNG NGÔN NGỮ TỰ NHIÊN HỖ TRỢ CHỌN MÔN HỌC VÀ TÀI LIỆU HỌC TẬP CHO SINH VIÊN KHOA CNTT")
    set_run_font(r, FONT_NAME, 17, bold=True, color=BLACK)
    
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_meta.paragraph_format.left_indent = Inches(1.5)
    p_meta.paragraph_format.space_before = Pt(30)
    p_meta.paragraph_format.space_after = Pt(60)
    p_meta.paragraph_format.line_spacing = 1.3
    
    runs_meta = [
        ("Giảng viên hướng dẫn: ", True), ("ThS. Nguyễn Văn An\n", False),
        ("Lớp tín chỉ: ", True), ("TTNT.01.K14.08.LH.C01_LT\n", False),
        ("Nhóm thực hiện: ", True), ("Nhóm 15\n", False),
        ("Sinh viên đại diện: ", True), ("Lê Hải Đăng (MSV: 20233301)", False)
    ]
    for text, is_b in runs_meta:
        r = p_meta.add_run(text)
        set_run_font(r, FONT_NAME, 13, bold=is_b, color=BLACK)
        
    p_bot = doc.add_paragraph()
    p_bot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bot.paragraph_format.space_before = Pt(30)
    p_bot.paragraph_format.space_after = Pt(0)
    r = p_bot.add_run("BẮC NINH - NĂM 2026")
    set_run_font(r, FONT_NAME, 13, bold=True, color=BLACK)
    
    doc.add_page_break()
    
    # TRANG PHỤ BÌA & PHÂN CÔNG NHIỆM VỤ
    p_sub_title = doc.add_paragraph()
    p_sub_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub_title.paragraph_format.space_before = Pt(10)
    p_sub_title.paragraph_format.space_after = Pt(20)
    r = p_sub_title.add_run("DANH SÁCH THÀNH VIÊN VÀ BẢNG PHÂN CÔNG NHIỆM VỤ")
    set_run_font(r, FONT_NAME, 15, bold=True, color=BLACK)
    
    headers_members = ["STT", "Mã sinh viên", "Họ và tên", "Lớp", "Nhiệm vụ phân công", "Đánh giá"]
    rows_members = [
        ["1", "20233301", "Lê Hải Đăng", "DCCNTT14.9", "Nhóm trưởng, Thiết kế kiến trúc RAG, Backend FastAPI Core, CSDL Postgres, Tổng hợp báo cáo", "100% Hoàn thành xuất sắc"],
        ["2", "20233302", "Lê Minh Quân", "DCCNTT14.9", "Nghiên cứu mô hình Vector Embedding, Qdrant Vector DB, Xử lý Text Chunking PDF", "100% Hoàn thành xuất sắc"],
        ["3", "20233303", "Lê Xuân Đạt", "DCCNTT14.9", "Xây dựng dịch vụ Xác thực Auth Service (RBAC), Quản lý người dùng, Viết kịch bản test", "100% Hoàn thành xuất sắc"],
        ["4", "20233304", "Lê Thanh Tùng", "DCCNTT14.9", "Phát triển giao diện Frontend Next.js (Chatbot, Bảng điểm, Kho tài liệu, Live Voice)", "100% Hoàn thành xuất sắc"],
        ["5", "20233305", "Phạm Bảo Sơn", "DCCNTT14.9", "Thu thập dữ liệu khung môn học, đề cương syllabus PDF, Kiểm thử hệ thống và đo lường latency", "100% Hoàn thành xuất sắc"]
    ]
    add_styled_table(doc, headers_members, rows_members, [0.5, 1.1, 1.4, 1.0, 1.8, 1.2], "Bảng 0.1: Phân công nhiệm vụ và kết quả thực hiện của các thành viên Nhóm 15")
    
    doc.add_page_break()
    
    # LỜI CẢM ƠN
    add_heading_1(doc, "LỜI CẢM ƠN")
    add_p(doc, "Để hoàn thành tốt bài tập lớn học phần Trí tuệ nhân tạo với đề tài “Xây dựng chương trình hỏi đáp bằng ngôn ngữ tự nhiên hỗ trợ chọn môn học và tài liệu học tập cho sinh viên khoa CNTT”, nhóm sinh viên chúng em xin được bày tỏ lòng biết ơn sâu sắc và chân thành nhất tới các thầy, cô giáo trong Khoa Công nghệ Thông tin - Trường Đại học Công nghệ Đông Á.")
    add_p(doc, "Đặc biệt, nhóm chúng em xin gửi lời cảm ơn trân trọng tới ThS. Nguyễn Văn An, giảng viên trực tiếp phụ trách giảng dạy và hướng dẫn học phần Trí tuệ nhân tạo. Trong suốt thời gian thực hiện nghiên cứu, thầy đã tận tình truyền đạt những kiến thức chuyên môn quý báu về Tác tử thông minh, Không gian trạng thái, Thuật toán tìm kiếm, Lập luận xác suất Bayes, Học máy và các kiến trúc AI hiện đại. Thầy cũng đã đưa ra những định hướng khoa học, góp ý sâu sắc và tạo mọi điều kiện thuận lợi nhất để nhóm có thể hiện thực hóa thành công sản phẩm từ lý thuyết sang ứng dụng thực tiễn.")
    add_p(doc, "Mặc dù nhóm đã nỗ lực hết mình, chủ động nghiên cứu và áp dụng các công nghệ tiên tiến nhất như FastAPI, PostgreSQL 15, Qdrant Vector Database, Vietnamese-SBERT và Google Gemini LLM, song do phạm vi rộng của đề tài và giới hạn về mặt thời gian, bài báo cáo khó tránh khỏi những thiếu sót nhất định. Nhóm chúng em rất mong nhận được những nhận xét, đóng góp quý báu từ quý thầy cô và các bạn sinh viên để sản phẩm ngày càng hoàn thiện, có tính ứng dụng cao hơn nữa trong thực tiễn đào tạo của Nhà trường.")
    add_p(doc, "Chúng em xin chân thành cảm ơn!")
    
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.space_before = Pt(20)
    p_sign.paragraph_format.space_after = Pt(0)
    r = p_sign.add_run("Bắc Ninh, tháng 09 năm 2026\nĐại diện Nhóm thực hiện\n\n\nLê Hải Đăng")
    set_run_font(r, FONT_NAME, 13, bold=True, italic=True, color=BLACK)
    
    doc.add_page_break()
    
    # MỤC LỤC
    add_heading_1(doc, "MỤC LỤC TỔNG QUAN")
    toc_items = [
        ("PHẦN MỞ ĐẦU", "1"),
        ("1. Lý do chọn đề tài", "1"),
        ("2. Mục tiêu của đề tài", "2"),
        ("3. Đối tượng và phạm vi nghiên cứu", "3"),
        ("4. Phương pháp nghiên cứu", "3"),
        ("5. Cấu trúc báo cáo", "4"),
        ("CHƯƠNG 1: CƠ SỞ LÝ THUYẾT VÀ CÁC PHƯƠNG PHÁP TRÍ TUỆ NHÂN TẠO", "5"),
        ("1.1 Tổng quan về Trí tuệ nhân tạo và Tác tử thông minh trong Hệ thống Hỏi - Đáp", "5"),
        ("1.2 Không gian trạng thái và Các phương pháp tìm kiếm trong Quản lý Lộ trình Học tập", "9"),
        ("1.3 Lập luận xác suất và Xử lý thông tin không chắc chắn", "13"),
        ("1.4 Tổng quan Học máy và Xử lý ngôn ngữ tự nhiên trong Kiến trúc Chatbot RAG", "16"),
        ("1.5 Phương pháp đánh giá mô hình và hệ thống Hỏi - Đáp", "28"),
        ("1.6 Công cụ, Thư viện và Hạ tầng công nghệ phát triển hệ thống", "31"),
        ("CHƯƠNG 2: PHÂN TÍCH VÀ XÂY DỰNG CHƯƠNG TRÌNH", "33"),
        ("2.1 Phát biểu bài toán", "33"),
        ("2.2 Xác định yêu cầu, Input và Output của hệ thống", "35"),
        ("2.3 Thiết kế sơ đồ khối và kiến trúc hệ thống", "38"),
        ("2.4 Mô tả thuật toán và giải thuật xử lý cốt lõi", "42"),
        ("2.5 Mô tả dữ liệu (Dataset) và Cơ sở tri thức", "48"),
        ("2.6 Cài đặt hệ thống và Giao diện tương tác thực tế", "53"),
        ("CHƯƠNG 3: THỰC NGHIỆM VÀ ĐÁNH GIÁ", "67"),
        ("3.1 Môi trường thực nghiệm và triển khai", "67"),
        ("3.2 Kịch bản kiểm thử chương trình với các trường hợp thực tế", "68"),
        ("3.3 Đánh giá kết quả thực nghiệm", "73"),
        ("3.4 Đánh giá ưu điểm và hạn chế của hệ thống", "76"),
        ("PHẦN KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "78"),
        ("TÀI LIỆU THAM KHẢO", "80"),
        ("PHỤ LỤC: LIÊN KẾT MÃ NGUỒN GITHUB VÀ HƯỚNG DẪN DEMO", "82")
    ]
    for title, page in toc_items:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.space_before = Pt(1)
        p_toc.paragraph_format.space_after = Pt(2)
        p_toc.paragraph_format.line_spacing = 1.15
        is_bold = title.startswith("CHƯƠNG") or title.startswith("PHẦN") or title.startswith("TÀI")
        r_t = p_toc.add_run(title)
        set_run_font(r_t, FONT_NAME, 12, bold=is_bold, color=BLACK)
        
        # Dấu chấm tab dẫn trang
        dots_len = max(5, 75 - len(title))
        r_dots = p_toc.add_run(" " + "." * dots_len + " ")
        set_run_font(r_dots, FONT_NAME, 11, bold=False, color=BLACK)
        
        r_p = p_toc.add_run(page)
        set_run_font(r_p, FONT_NAME, 12, bold=is_bold, color=BLACK)
        
    doc.add_page_break()
    
    # DANH MỤC CÁC CHỮ VIẾT TẮT
    add_heading_1(doc, "DANH MỤC CÁC CHỮ VIẾT TẮT")
    abbr_headers = ["Ký hiệu viết tắt", "Thuật ngữ tiếng Anh", "Ý nghĩa tiếng Việt"]
    abbr_rows = [
        ["AI", "Artificial Intelligence", "Trí tuệ nhân tạo"],
        ["RAG", "Retrieval-Augmented Generation", "Tạo sinh tăng cường truy xuất"],
        ["LLM", "Large Language Model", "Mô hình ngôn ngữ lớn"],
        ["NLP", "Natural Language Processing", "Xử lý ngôn ngữ tự nhiên"],
        ["NLU", "Natural Language Understanding", "Hiểu ngôn ngữ tự nhiên"],
        ["ML", "Machine Learning", "Học máy"],
        ["BFS", "Breadth-First Search", "Thuật toán tìm kiếm theo chiều rộng"],
        ["DFS", "Depth-First Search", "Thuật toán tìm kiếm theo chiều sâu"],
        ["DAG", "Directed Acyclic Graph", "Đồ thị có hướng không chu trình"],
        ["RBAC", "Role-Based Access Control", "Kiểm soát truy cập dựa trên vai trò"],
        ["API", "Application Programming Interface", "Giao diện lập trình ứng dụng"],
        ["JWT", "JSON Web Token", "Mã thông báo định danh Web JSON"],
        ["SBERT", "Sentence-BERT", "Mô hình nhúng câu dựa trên kiến trúc BERT"],
        ["TF-IDF", "Term Frequency - Inverse Document Frequency", "Tần số xuất hiện từ - Nghịch đảo tần số tài liệu"],
        ["ANN", "Approximate Nearest Neighbor", "Thuật toán tìm kiếm lân cận gần đúng"],
        ["HNSW", "Hierarchical Navigable Small World", "Đồ thị thế giới nhỏ phân cấp điều hướng"],
        ["MRR", "Mean Reciprocal Rank", "Điểm trung bình nghịch đảo thứ hạng"],
        ["MSE", "Mean Squared Error", "Sai số toàn phương trung bình"],
        ["MAE", "Mean Absolute Error", "Sai số tuyệt đối trung bình"],
        ["ROC-AUC", "Receiver Operating Characteristic - Area Under Curve", "Diện tích dưới đường cong ROC"],
        ["MLOps", "Machine Learning Operations", "Vận hành và quản lý vòng đời học máy"]
    ]
    add_styled_table(doc, abbr_headers, abbr_rows, [1.2, 2.5, 2.7], "Bảng 0.2: Danh mục các thuật ngữ và chữ viết tắt trong báo cáo")
    
    doc.add_page_break()
