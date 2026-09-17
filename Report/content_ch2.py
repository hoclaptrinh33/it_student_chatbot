# -*- coding: utf-8 -*-
"""
content_ch2.py
Xây dựng CHƯƠNG 2: PHÂN TÍCH VÀ XÂY DỰNG CHƯƠNG TRÌNH
Bao gồm:
- Phát biểu bài toán, Yêu cầu chức năng & phi chức năng, Đặc tả Input/Output
- Hệ thống Sơ đồ kỹ thuật hoàn chỉnh:
  + Sơ đồ khối kiến trúc hệ thống Microservices (so_do_khoi_kien_truc.png)
  + Sơ đồ thực thể liên kết ERD PostgreSQL 15 (so_do_erd_database.png)
  + Sơ đồ luồng Hybrid RAG & Tiêm sự thật học vụ (so_do_luong_rag_facts.png)
  + Sơ đồ đồ thị DAG điều kiện tiên quyết môn học (so_do_cay_tien_quyet_dag.png)
  + Sơ đồ ca sử dụng Use Case Diagram (so_do_usecase_he_thong.png)
  + Sơ đồ tuần tự Sequence Diagram (so_do_tuan_tu_sequence.png)
- Mô tả 4 thuật toán then chốt kèm Code Snippets
- Mô tả Dataset (Khung 23 môn học, cây 25 tiên quyết, 18+ tệp PDF)
- Hệ thống 35 hình ảnh giao diện thực tế từ Report/image (Hình 2.7 - 2.41)
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from make_full_report import (
    FONT_NAME, BLACK, set_run_font, add_p, add_heading_1, add_heading_2, 
    add_heading_3, add_bullet, add_styled_table, add_figure, add_code_snippet
)

def build_chapter_2(doc):
    add_heading_1(doc, "CHƯƠNG 2: PHÂN TÍCH VÀ XÂY DỰNG CHƯƠNG TRÌNH")
    
    # 2.1 Phát biểu bài toán
    add_heading_2(doc, "2.1 Phát biểu bài toán")
    add_heading_3(doc, "2.1.1 Bối cảnh thực tế trong đào tạo đại học theo hệ thống tín chỉ")
    add_p(doc, "Trường Đại học Công nghệ Đông Á (EAUT), cụ thể là Khoa Công nghệ Thông tin, hiện đang đào tạo hàng nghìn sinh viên theo học chế tín chỉ. Điểm cốt lõi của học chế tín chỉ là trao quyền tự chủ tối đa cho sinh viên trong việc chủ động đăng ký kế hoạch học tập, lựa chọn số lượng học phần trong mỗi kỳ và quyết định lộ trình theo đuổi chuyên ngành.")
    add_p(doc, "Tuy nhiên, để đạt được chuẩn đầu ra kỹ sư/cử nhân CNTT, sinh viên phải hoàn thành một khối lượng kiến thức tối thiểu từ 130 đến 150 tín chỉ, trải rộng qua 8 học kỳ. Toàn bộ chương trình được liên kết với nhau bằng một mạng lưới ràng buộc logic phức tạp, đòi hỏi sinh viên phải nắm rất vững quy chế học vụ và cây môn học tiên quyết.")

    add_heading_3(doc, "2.1.2 Những rào cản sinh viên gặp phải khi chọn môn học và tìm kiếm tài liệu")
    add_p(doc, "Qua khảo sát thực tế sinh viên các khóa từ K12 đến K15 Khoa CNTT, nhóm nghiên cứu nhận thấy sinh viên đối mặt với 4 khó khăn nghiêm trọng sau:")
    add_bullet(doc, "Nguy cơ đăng ký sai môn do vướng môn tiên quyết", 
               "Nhiều sinh viên chưa hoàn thành môn học trước hoặc trượt môn cơ sở (ví dụ trượt INT1203 Kiến trúc máy tính) nhưng vẫn cố gắng đăng ký môn học nâng cao (INT2101 Hệ điều hành), dẫn đến việc bị hủy học phần giữa chừng hoặc đuối sức, gây chậm tiến độ tốt nghiệp.")
    add_bullet(doc, "Mơ hồ trong định hướng chuyên ngành", 
               "Sinh viên bước sang năm 2 và năm 3 thường không rõ định hướng Web, Trí tuệ nhân tạo, Mạng máy tính hay An toàn thông tin thì cần học các môn tự chọn cụ thể nào, thứ tự học ra sao để đáp ứng yêu cầu tuyển dụng thực tế.")
    add_bullet(doc, "Phân tán và khó tiếp cận tài liệu chuẩn", 
               "Sinh viên thường phải xin đề cương, slide bài giảng hoặc bài tập lớn từ các khóa trước qua mạng xã hội, dẫn đến tình trạng học theo tài liệu cũ, sai chuẩn kiến thức hoặc không đúng đề cương của học kỳ hiện tại.")
    add_bullet(doc, "Giảng viên cố vấn học tập quá tải", 
               "Mỗi đợt đăng ký tín chỉ đầu kỳ, mỗi thầy cô cố vấn phải giải đáp hàng trăm email, tin nhắn của sinh viên với các câu hỏi trùng lặp nhau, dẫn đến tình trạng phản hồi chậm trễ.")

    add_heading_3(doc, "2.1.3 Mục tiêu giải pháp: Hệ thống Cố vấn Học tập Thông minh Khoa CNTT")
    add_p(doc, "Để giải quyết dứt điểm các bài toán trên, đề tài tập trung xây dựng một Trợ lý Cố vấn Học tập AI thông minh với năng lực:")
    add_bullet(doc, "Hiểu ngôn ngữ tự nhiên tiếng Việt", "Tiếp nhận câu hỏi dạng tự do của sinh viên về quy chế, môn học, lộ trình và tài liệu.")
    add_bullet(doc, "Cá nhân hóa theo bảng điểm thực tế", "Nhận diện sinh viên qua mã JWT, tự động truy xuất bảng điểm cá nhân (môn đã đạt, môn trượt, môn đang học) để đưa ra câu trả lời riêng biệt, chính xác tuyệt đối.")
    add_bullet(doc, "Tự động truy xuất và gợi ý tài liệu PDF", "Tìm kiếm chính xác đoạn kiến trúc đề cương và đính kèm đường dẫn tải tài liệu học tập chính thống.")
    add_bullet(doc, "Hỗ trợ giọng nói trực tiếp (Live Voice)", "Cung cấp trải nghiệm tương tác tự nhiên, sinh động như đang trò chuyện trực tiếp với thầy cô cố vấn.")

    # 2.2 Xác định yêu cầu, Input, Output
    add_heading_2(doc, "2.2 Xác định yêu cầu, Input và Output của hệ thống")
    add_heading_3(doc, "2.2.1 Xác định yêu cầu chức năng (Functional Requirements)")
    add_p(doc, "Hệ thống đáp ứng đầy đủ các yêu cầu chức năng sau:")
    add_bullet(doc, "FR-01: Quản lý xác thực và phân quyền RBAC", "Đăng nhập, đăng ký sinh viên, quên mật khẩu, phân chia 3 vai trò Admin, Teacher, Student.")
    add_bullet(doc, "FR-02: Tư vấn môn đủ điều kiện học kỳ tới", "Kiểm tra tự động điều kiện tiên quyết và trả về danh sách các môn được phép học.")
    add_bullet(doc, "FR-03: Giải đáp thắc mắc môn học tiên quyết", "Giải thích chi tiết tại sao sinh viên chưa đủ điều kiện học môn X, cần học môn nào trước.")
    add_bullet(doc, "FR-04: Tư vấn lộ trình chuyên ngành", "Gợi ý danh sách môn học bắt buộc và tự chọn theo chuyên ngành mong muốn (Web, AI, Security).")
    add_bullet(doc, "FR-05: Tra cứu và tải tài liệu học tập (PDF)", "Truy hồi đề cương syllabus, slide bài giảng kèm trích dẫn nguồn (Citations) và nút tải file.")
    add_bullet(doc, "FR-06: Tra cứu bảng điểm và hồ sơ học vụ", "Xem điểm tổng kết thang 10, thang 4, điểm chữ, số tín chỉ tích lũy và GPA cá nhân.")
    add_bullet(doc, "FR-07: Trợ lý giọng nói trực tiếp (Live Voice Advisor)", "Giao tiếp hai chiều bằng giọng nói tiếng Việt qua Web Speech API và TTS.")
    add_bullet(doc, "FR-08: Phân hệ Quản trị & Giảng viên", "CRUD danh mục môn học, nhập bảng điểm, quản lý kho tài liệu, cấu hình tham số RAG pipeline.")

    add_heading_3(doc, "2.2.2 Xác định yêu cầu phi chức năng (Non-functional Requirements)")
    add_bullet(doc, "Hiệu năng và độ trễ phản hồi", "Phản hồi dưới 100ms cho các câu hỏi trùng lặp trong Semantic Cache; dưới 2.5s cho toàn bộ pipeline RAG phức tạp.")
    add_bullet(doc, "Độ chính xác và độ tin cậy", "Triệt tiêu 100% hiện tượng bịa mã môn học, số tín chỉ (Zero Hallucination) thông qua kỹ thuật tiêm tri thức học vụ.")
    add_bullet(doc, "Bảo mật và an toàn dữ liệu", "Phân lập bộ nhớ đệm theo sinh viên (Per-user cache key), mã hóa mật khẩu PBKDF2-SHA256, xác thực JWT Bearer Token.")
    add_bullet(doc, "Tính khả dụng và tương thích", "Giao diện Web Responsive hoạt động trơn tru trên cả máy tính để bàn (Desktop) và điện thoại di động (Mobile).")

    add_heading_3(doc, "2.2.3 Đặc tả chi tiết Input và Output theo từng luồng nghiệp vụ")
    headers_io = ["Nghiệp vụ / Tác vụ", "Input đầu vào", "Xử lý trung gian của hệ thống", "Output đầu ra"]
    rows_io = [
        ["Đăng nhập hệ thống", "Email trường (@eaut.edu.vn) và Mật khẩu.", "Kiểm tra băm mật khẩu, truy vấn vai trò người dùng trong PostgreSQL 15.", "Access token JWT, Refresh token, thông tin hồ sơ và chuyển hướng vai trò."],
        ["Hỏi môn đủ điều kiện", "Câu hỏi tự nhiên: 'Kỳ tới em được học những môn nào?'.", "Trích xuất student_id từ JWT, gọi hàm fn_student_eligible_courses, tiêm vào prompt LLM.", "Danh sách môn đủ điều kiện kèm số tín chỉ, lý do giải thích chi tiết."],
        ["Tra cứu tài liệu PDF", "Câu hỏi tự nhiên: 'Cho em xin đề cương môn Lập trình Web'.", "Intent Classifier (MATERIAL_QA), Dense Vector Search Qdrant, Rerank Top-5 chunks.", "Câu trả lời tóm tắt đề cương, nguồn trích dẫn và liên kết tải tài liệu PDF."],
        ["Tư vấn định hướng", "Câu hỏi: 'Em muốn theo hướng AI thì nên chọn môn gì?'.", "Truy vấn các môn có career_track = 'AI', duyệt cây tiên quyết, tổng hợp lộ trình.", "Kế hoạch môn học theo từng kỳ tối ưu cho định hướng Trí tuệ nhân tạo."],
        ["Giao tiếp giọng nói Live Voice", "Luồng âm thanh micro của sinh viên.", "Speech-to-Text chuyển thành văn bản, chạy Core RAG, Text-to-Speech sinh âm thanh.", "Giọng nói trợ lý AI phản hồi trực tiếp kèm sóng âm trực quan (Audio Visualizer)."]
    ]
    add_styled_table(doc, headers_io, rows_io, [1.5, 1.8, 1.8, 1.9], "Bảng 2.1: Đặc tả Input và Output chi tiết của các nghiệp vụ chính")

    # 2.3 Thiết kế sơ đồ khối và kiến trúc hệ thống
    add_heading_2(doc, "2.3 Thiết kế sơ đồ khối và kiến trúc hệ thống")
    
    img_dir = "Report/image"

    add_heading_3(doc, "2.3.1 Sơ đồ ca sử dụng hệ thống (Use Case Diagram)")
    add_p(doc, "Hệ thống phục vụ 3 nhóm tác nhân (Actors) chính với các quyền hạn nghiệp vụ phân cấp rõ ràng:")
    add_bullet(doc, "Sinh viên (Student)", "Đăng nhập, trò chuyện hỏi đáp học vụ, tra cứu môn đủ điều kiện, tra cứu bảng điểm cá nhân, tìm kiếm và tải tài liệu PDF, tương tác bằng giọng nói Live Voice.")
    add_bullet(doc, "Giảng viên / Cố vấn học tập (Teacher)", "Tra cứu tiến độ học tập và danh sách sinh viên theo lớp, xem cây điều kiện tiên quyết môn học, quản lý học liệu và tài liệu giảng dạy, trò chuyện với trợ lý AI chuyên môn.")
    add_bullet(doc, "Quản trị viên hệ thống (Admin)", "Quản lý người dùng, vai trò RBAC, quyền hạn, quản lý danh mục môn học toàn khóa, nhập điểm thi sinh viên, quản trị kho tri thức vector và cấu hình tham số RAG Pipeline.")
    
    add_figure(doc, os.path.join(img_dir, "so_do_usecase_he_thong.png"), 
               "Hình 2.1: Sơ đồ ca sử dụng (Use Case Diagram) tổng thể hệ thống Cố vấn Học tập Khoa CNTT", width_in=6.0)

    add_heading_3(doc, "2.3.2 Sơ đồ khối kiến trúc hệ thống Microservices")
    add_p(doc, "Hệ thống Cố vấn Học tập Khoa CNTT được thiết kế theo mô hình Microservices phân tán hiện đại, tách biệt hoàn toàn giữa các tầng giao diện (Frontend UI), xử lý nghiệp vụ xác thực (Auth Service), xử lý trí tuệ nhân tạo RAG (Core Service) và tầng lưu trữ dữ liệu chuyên dụng (PostgreSQL 15, Qdrant Vector DB, Redis Cache):")
    
    add_figure(doc, os.path.join(img_dir, "so_do_khoi_kien_truc.png"), 
               "Hình 2.2: Sơ đồ khối kiến trúc hệ thống Microservices (UI :3000, Auth :8001, Core :8000)", width_in=6.0)

    add_heading_3(doc, "2.3.3 Sơ đồ thực thể liên kết (ERD) Cơ sở dữ liệu PostgreSQL 15")
    add_p(doc, "Cơ sở dữ liệu trung tâm của hệ thống sử dụng PostgreSQL 15, bao gồm 3 phân hệ liên kết chặt chẽ qua các khóa ngoại (Foreign Keys) và ràng buộc toàn vẹn:")
    add_bullet(doc, "Phân hệ Xác thực & Phân quyền (Auth / RBAC)", "Bao gồm các bảng users, roles, permissions, user_roles, role_permissions và password_reset_tokens.")
    add_bullet(doc, "Phân hệ Học vụ & Tiên quyết (Academic)", "Bao gồm các bảng courses (23 học phần chuẩn), course_prerequisites (25 ràng buộc tiên quyết có hướng DAG) và student_academic_records (kết quả học tập sinh viên).")
    add_bullet(doc, "Phân hệ Tri thức RAG & Hội thoại (Materials & Chat)", "Bao gồm các bảng learning_materials, chatbots, datasets, files, dataset_files, chat_sessions và chat_messages.")

    add_figure(doc, os.path.join(img_dir, "so_do_erd_database.png"), 
               "Hình 2.3: Sơ đồ thực thể liên kết (Entity-Relationship Diagram - ERD) Cơ sở dữ liệu PostgreSQL 15", width_in=6.0)

    add_heading_3(doc, "2.3.4 Sơ đồ luồng xử lý Hybrid RAG và Tiêm sự thật học vụ")
    add_p(doc, "Để đảm bảo phản hồi tức thì và loại bỏ hoàn toàn hiện tượng ảo giác thông tin, hệ thống kết hợp giữa Semantic Cache theo User, Intent Classifier, hàm SQL fn_student_eligible_courses và Dense Vector Search:")

    add_figure(doc, os.path.join(img_dir, "so_do_luong_rag_facts.png"), 
               "Hình 2.4: Sơ đồ luồng xử lý Hybrid RAG kết hợp Tiêm tri thức học vụ [AcademicFacts] và Semantic Cache", width_in=6.0)

    add_heading_3(doc, "2.3.5 Sơ đồ tuần tự tương tác thời gian thực (Sequence Diagram)")
    add_p(doc, "Trình tự trao đổi thông điệp giữa các thành phần phần mềm khi sinh viên gửi yêu cầu hỏi đáp học vụ:")

    add_figure(doc, os.path.join(img_dir, "so_do_tuan_tu_sequence.png"), 
               "Hình 2.5: Sơ đồ tuần tự (Sequence Diagram) luồng tương tác giữa Client, Core API, PostgreSQL, Qdrant và LLM", width_in=6.0)

    add_heading_3(doc, "2.3.6 Sơ đồ đồ thị có hướng không chu trình (DAG) môn học tiên quyết")
    add_p(doc, "Đồ thị có hướng không chu trình (Directed Acyclic Graph - DAG) mô hình hóa cấu trúc phụ thuộc của 23 học phần Khoa CNTT từ Học kỳ 1 đến Học kỳ 6:")

    add_figure(doc, os.path.join(img_dir, "so_do_cay_tien_quyet_dag.png"), 
               "Hình 2.6: Đồ thị có hướng không chu trình (DAG) quan hệ tiên quyết giữa các môn học Khoa CNTT", width_in=6.0)

    # 2.4 Mô tả thuật toán
    add_heading_2(doc, "2.4 Mô tả thuật toán và giải thuật xử lý cốt lõi")
    
    add_heading_3(doc, "2.4.1 Thuật toán 1: Phân loại ý định người dùng (Intent Classifier)")
    add_p(doc, "Thuật toán sử dụng phân loại từ khóa kết hợp cấu trúc ngữ nghĩa để định tuyến chính xác câu hỏi của sinh viên vào đúng nhánh xử lý chuyên biệt:")
    
    code_intent = """class IntentClassifier:
    COURSE_KEYWORDS = ["môn", "học kỳ", "kỳ tới", "tiên quyết", "tín chỉ", "đăng ký", "qua môn", "học lại", "chuyên ngành"]
    MATERIAL_KEYWORDS = ["tài liệu", "giáo trình", "slide", "bài giảng", "đề cương", "syllabus", "đề thi", "tải", "download"]

    @classmethod
    def classify(cls, query: str) -> str:
        q = query.lower()
        has_course = any(k in q for k in cls.COURSE_KEYWORDS)
        has_material = any(k in q for k in cls.MATERIAL_KEYWORDS)
        if has_course and has_material:
            return "HYBRID"
        elif has_course:
            return "COURSE_ADVICE"
        elif has_material:
            return "MATERIAL_QA"
        return "GENERAL_CHAT"
"""
    add_code_snippet(doc, code_intent, "Đoạn mã 2.1: Thuật toán phân loại ý định người dùng (Intent Classifier)")

    add_heading_3(doc, "2.4.2 Thuật toán 2: Kiểm tra môn đủ điều kiện & Duyệt đồ thị tiên quyết (Prerequisite DAG)")
    add_p(doc, "Trong cơ sở dữ liệu PostgreSQL, các mối quan hệ tiên quyết giữa các môn học được mô hình hóa thành một Đồ thị có hướng không chu trình (DAG). Để xác định chính xác sinh viên có được phép học môn X hay không, hệ thống xây dựng hàm fn_student_eligible_courses:")
    
    code_sql_prereq = """CREATE OR REPLACE FUNCTION fn_student_eligible_courses(p_student_id UUID)
RETURNS TABLE (
    course_id UUID, course_code VARCHAR, course_name VARCHAR, credits INT, reason TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH passed_courses AS (
        SELECT sar.course_id FROM student_academic_records sar
        WHERE sar.student_id = p_student_id AND sar.status = 'PASSED'
    ),
    unmet_prereqs AS (
        SELECT cp.course_id, STRING_AGG(c_pre.course_code, ', ') as missing_codes
        FROM course_prerequisites cp
        JOIN courses c_pre ON cp.prerequisite_id = c_pre.id
        WHERE cp.prereq_type = 'PREREQUISITE'
          AND cp.prerequisite_id NOT IN (SELECT course_id FROM passed_courses)
        GROUP BY cp.course_id
    )
    SELECT c.id, c.course_code, c.course_name, c.credits,
           CASE 
               WHEN c.id IN (SELECT course_id FROM passed_courses) THEN 'Đã hoàn thành'
               WHEN up.missing_codes IS NOT NULL THEN 'Chưa đạt tiên quyết: ' || up.missing_codes
               ELSE 'Đủ điều kiện đăng ký'
           END
    FROM courses c
    LEFT JOIN unmet_prereqs up ON c.id = up.course_id;
END;
$$ LANGUAGE plpgsql;
"""
    add_code_snippet(doc, code_sql_prereq, "Đoạn mã 2.2: Hàm SQL kiểm tra môn đủ điều kiện trên đồ thị DAG tiên quyết")

    add_heading_3(doc, "2.4.3 Thuật toán 3: Tạo sinh tăng cường truy xuất kết hợp Tiêm tri thức học vụ")
    add_p(doc, "Để triệt tiêu hoàn toàn hiện tượng ảo giác thông tin (Hallucination), nhóm nghiên cứu phát triển kỹ thuật Tiêm tri thức học vụ ([AcademicFacts] Injection). Hệ thống ép mô hình LLM chỉ được phép căn cứ vào dữ liệu sự thật được cung cấp:")
    
    code_prompt = """def build_academic_prompt(query: str, facts: AcademicFacts, knowledge_chunks: list) -> str:
    facts_text = f\"\"\"
    [AcademicFacts - NGUỒN SỰ THẬT DUY NHẤT VỀ SINH VIÊN]
    - Sinh viên: {facts.student_name} (MSV: {facts.student_code})
    - Môn đã hoàn thành (PASSED): {', '.join(facts.passed_courses)}
    - Môn trượt cần học lại (FAILED): {', '.join(facts.failed_courses)}
    - Môn đủ điều kiện học kỳ tới: {', '.join(facts.eligible_courses)}
    \"\"\"
    system_rules = \"\"\"
    QUY TẮC CỐT LÕI:
    1. Tuyệt đối KHÔNG BỊA ĐẶT mã môn học hoặc điều kiện tiên quyết nằm ngoài [AcademicFacts].
    2. Nếu sinh viên có môn FAILED, phải ưu tiên nhắc nhở đăng ký học lại môn đó trước.
    3. Khi trả lời về tài liệu học tập, bắt buộc trích dẫn tên tệp tài liệu và cung cấp link tải.
    \"\"\"
    return f"{system_rules}\\n{facts_text}\\n[Knowledge]\\n{format_chunks(knowledge_chunks)}\\nCâu hỏi: {query}"
"""
    add_code_snippet(doc, code_prompt, "Đoạn mã 2.3: Kỹ thuật tiêm tri thức học vụ triệt tiêu ảo giác thông tin")

    add_heading_3(doc, "2.4.4 Thuật toán 4: Bộ nhớ đệm ngữ nghĩa phân lập theo sinh viên (Per-User Semantic Caching)")
    add_p(doc, "Nếu áp dụng Semantic Cache dùng chung cho toàn bộ hệ thống, câu trả lời tư vấn môn học kỳ tới của Sinh viên A (đã đỗ hết môn) có thể bị trả nhầm cho Sinh viên B (đang bị trượt 2 môn). Do đó, thuật toán Semantic Cache của hệ thống bắt buộc phải đính kèm user_id vào khóa định danh:")
    add_p(doc, "Cache_Key = Hash(user_id) + '_' + Hash(chatbot_id)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p(doc, "Khi người dùng gửi câu hỏi q, hệ thống tính khoảng cách Cosine giữa vector q và các câu hỏi trong vùng đệm của riêng người dùng đó. Nếu khoảng cách Cosine Distance <= 0.08 (tương đồng >= 92%), kết quả được trả về ngay lập tức, tiết kiệm 100% chi phí gọi dịch vụ LLM.")

    # 2.5 Mô tả dữ liệu
    add_heading_2(doc, "2.5 Mô tả dữ liệu (Dataset) và Cơ sở tri thức")
    add_heading_3(doc, "2.5.1 Cấu trúc cơ sở dữ liệu học vụ PostgreSQL")
    add_p(doc, "Hệ thống xây dựng và chuẩn hóa danh mục 23 học phần trọng tâm của Khoa Công nghệ Thông tin - Trường Đại học Công nghệ Đông Á từ học kỳ 1 đến học kỳ 6:")
    
    headers_courses = ["Mã môn", "Tên học phần", "Số TC", "LT/TH", "Học kỳ", "Chuyên ngành"]
    rows_courses = [
        ["INT1101", "Tin học đại cương", "3", "30/30", "HK1", "GENERAL"],
        ["INT1102", "Giải tích", "3", "45/0", "HK1", "GENERAL"],
        ["INT1103", "Đại số tuyến tính", "3", "45/0", "HK1", "GENERAL"],
        ["INT1104", "Vật lý đại cương", "3", "45/0", "HK1", "GENERAL"],
        ["INT1201", "Kỹ thuật lập trình C/C++", "3", "30/30", "HK2", "GENERAL"],
        ["INT1202", "Toán rời rạc", "3", "45/0", "HK2", "GENERAL"],
        ["INT1203", "Kiến trúc máy tính", "3", "45/0", "HK2", "GENERAL"],
        ["INT1204", "Mạng máy tính căn bản", "3", "30/30", "HK2", "GENERAL"],
        ["INT2101", "Hệ điều hành", "3", "30/30", "HK3", "GENERAL"],
        ["INT2102", "Cấu trúc dữ liệu và giải thuật", "3", "30/30", "HK3", "GENERAL"],
        ["INT2103", "Cơ sở dữ liệu", "3", "30/30", "HK3", "GENERAL"],
        ["INT2104", "Lập trình Web", "3", "30/30", "HK3", "WEB"],
        ["INT2201", "Lập trình hướng đối tượng (Java)", "3", "30/30", "HK4", "GENERAL"],
        ["INT2202", "Trí tuệ nhân tạo", "3", "30/30", "HK4", "AI"],
        ["INT2203", "Phân tích và thiết kế hệ thống", "3", "45/0", "HK4", "SOFTWARE"],
        ["INT2204", "Công nghệ phần mềm", "3", "30/30", "HK4", "SOFTWARE"],
        ["INT3101", "Học máy (Machine Learning)", "3", "30/30", "HK5", "AI"],
        ["INT3104", "Lập trình Web nâng cao (React/Node)", "3", "30/30", "HK5", "WEB"],
        ["INT3105", "An toàn thông tin", "3", "30/30", "HK5", "SECURITY"],
        ["INT3201", "Học sâu và thị giác máy tính", "3", "30/30", "HK6", "AI"],
        ["INT3202", "Xử lý ngôn ngữ tự nhiên", "3", "30/30", "HK6", "AI"],
        ["INT4101", "Điện toán đám mây và DevOps", "3", "30/30", "HK6", "CLOUD_DEVOPS"],
        ["INT4201", "Thực tập tốt nghiệp", "4", "0/120", "HK7", "GENERAL"]
    ]
    add_styled_table(doc, headers_courses, rows_courses, [1.0, 2.5, 0.6, 0.8, 0.8, 1.3], "Bảng 2.2: Khung danh mục 23 học phần đào tạo chuẩn Khoa CNTT")

    add_heading_3(doc, "2.5.2 Kho tài liệu học tập chính thống (Knowledge Base)")
    add_p(doc, "Kho tài liệu của hệ thống bao gồm 18+ tệp PDF đề cương chi tiết học phần (syllabus) và slide bài giảng chính thức của Khoa CNTT. Mỗi tài liệu được hệ thống tự động bóc tách nội dung, chia thành các đoạn văn bản (chunks) 1024 ký tự có gắn thẻ siêu dữ liệu (course_id, material_type: SYLLABUS, LECTURE_SLIDE, EXAM_SAMPLE) và vector hóa vào Qdrant.")

    # 2.6 Cài đặt hệ thống và Giao diện tương tác
    add_heading_2(doc, "2.6 Cài đặt hệ thống và Giao diện tương tác thực tế")
    add_heading_3(doc, "2.6.1 Giới thiệu cấu trúc mã nguồn dự án")
    add_p(doc, "Mã nguồn dự án được tổ chức khoa học theo mô hình Monorepo chứa 3 microservices chính:")
    add_bullet(doc, "airc_internal_chatbot_core", "Chứa toàn bộ logic RAG, router học vụ academic.py, prompt_service.py, chat_service.py, domain_splitter.py.")
    add_bullet(doc, "airc_internal_chatbot_auth", "Chứa logic xác thực người dùng auth.py, phân quyền RBAC, mã hóa mật khẩu và sinh mã token JWT.")
    add_bullet(doc, "airc_internal_chatbot_ui", "Chứa ứng dụng Frontend Next.js 14, các trang giao diện sinh viên (/dashboard/chat, /dashboard/courses, /dashboard/grades, /dashboard/materials), giao diện giảng viên (/dashboard/teacher) và quản trị (/admin).")

    add_heading_3(doc, "2.6.2 Hệ thống giao diện tương tác thực tế")
    add_p(doc, "Dưới đây là hình ảnh chụp thực tế toàn bộ các phân hệ của hệ thống Cố vấn Học tập Khoa CNTT:")

    # Nhóm 1: Xác thực
    add_heading_3(doc, "A. Phân hệ Xác thực & Quản lý tài khoản")
    add_figure(doc, os.path.join(img_dir, "01_dang_nhap.png"), "Hình 2.7: Giao diện đăng nhập hệ thống Cố vấn Học tập Khoa CNTT")
    add_figure(doc, os.path.join(img_dir, "01b_dang_nhap_mobile.png"), "Hình 2.8: Giao diện đăng nhập tương thích trên thiết bị di động (Mobile Responsive)", width_in=3.2)
    add_figure(doc, os.path.join(img_dir, "02_dang_ky.png"), "Hình 2.9: Giao diện đăng ký tài khoản sinh viên trực tuyến")
    add_figure(doc, os.path.join(img_dir, "03_quen_mat_khau.png"), "Hình 2.10: Giao diện khôi phục mật khẩu thông qua mã xác thực")

    # Nhóm 2: Sinh viên
    add_heading_3(doc, "B. Phân hệ Sinh viên")
    add_figure(doc, os.path.join(img_dir, "10_sv_chat_trang_chu.png"), "Hình 2.11: Trang chủ chat sinh viên với các gợi ý câu hỏi học vụ phổ biến")
    add_figure(doc, os.path.join(img_dir, "11_sv_chat_chao_hoi.png"), "Hình 2.12: Hội thoại tương tác chào hỏi và giới thiệu chức năng cố vấn học tập")
    add_figure(doc, os.path.join(img_dir, "12_sv_chat_tu_van_mon.png"), "Hình 2.13: Trợ lý AI phân tích bảng điểm và tư vấn lộ trình môn học theo định hướng Web")
    add_figure(doc, os.path.join(img_dir, "12b_sv_chat_nguon_tham_khao.png"), "Hình 2.14: Trả lời câu hỏi học tập có trích nguồn tài liệu và cung cấp link tải đề cương PDF")
    add_figure(doc, os.path.join(img_dir, "13_sv_mon_du_dieu_kien.png"), "Hình 2.15: Danh sách các môn học đủ điều kiện đăng ký kỳ tới của sinh viên")
    add_figure(doc, os.path.join(img_dir, "14_sv_bang_diem.png"), "Hình 2.16: Tra cứu bảng điểm học tập cá nhân (Đạt, Trượt, Đang học và GPA)")
    add_figure(doc, os.path.join(img_dir, "15_sv_tai_lieu.png"), "Hình 2.17: Kho tài liệu học tập chính thống theo từng học phần của Khoa CNTT")
    add_figure(doc, os.path.join(img_dir, "16_sv_ho_so.png"), "Hình 2.18: Hồ sơ sinh viên, thông tin lớp hành chính và tiến độ tích lũy tín chỉ")
    add_figure(doc, os.path.join(img_dir, "17_sv_chat_mobile.png"), "Hình 2.19: Trải nghiệm trò chuyện với trợ lý cố vấn AI trên giao diện điện thoại", width_in=3.2)
    add_figure(doc, os.path.join(img_dir, "18_sv_live_voice.png"), "Hình 2.20: Cố vấn tương tác giọng nói trực tiếp hai chiều (Live Voice Advisor)")

    # Nhóm 3: Giảng viên
    add_heading_3(doc, "C. Phân hệ Giảng viên / Cố vấn học tập")
    add_figure(doc, os.path.join(img_dir, "20_gv_bang_dieu_khien.png"), "Hình 2.21: Bảng điều khiển dành cho Giảng viên / Cố vấn học tập")
    add_figure(doc, os.path.join(img_dir, "21_gv_quan_ly_diem.png"), "Hình 2.22: Tra cứu kết quả học tập và môn đủ điều kiện của sinh viên theo lớp")
    add_figure(doc, os.path.join(img_dir, "22_gv_tai_lieu.png"), "Hình 2.23: Quản lý kho tài liệu bài giảng và học liệu chuyên môn")
    add_figure(doc, os.path.join(img_dir, "23_gv_mon_hoc.png"), "Hình 2.24: Quản lý danh mục môn học phụ trách và thông tin tín chỉ")
    add_figure(doc, os.path.join(img_dir, "23b_gv_tien_quyet.png"), "Hình 2.25: Sơ đồ trực quan cây điều kiện tiên quyết của học phần INT2204 Công nghệ phần mềm")
    add_figure(doc, os.path.join(img_dir, "24_gv_bo_du_lieu.png"), "Hình 2.26: Danh sách các bộ dữ liệu tri thức đào tạo (Knowledge Base)")
    add_figure(doc, os.path.join(img_dir, "25_gv_chi_tiet_bo_du_lieu.png"), "Hình 2.27: Chi tiết bộ dữ liệu tài liệu học tập đã được phân đoạn và nạp vào RAG")
    add_figure(doc, os.path.join(img_dir, "26_gv_tro_ly_ai.png"), "Hình 2.28: Trợ lý AI hỗ trợ giảng viên soạn thảo đề cương và giải đáp nghiệp vụ")

    # Nhóm 4: Quản trị viên
    add_heading_3(doc, "D. Phân hệ Quản trị viên hệ thống (Admin)")
    add_figure(doc, os.path.join(img_dir, "30_admin_bang_dieu_khien.png"), "Hình 2.29: Bảng điều khiển quản trị tổng quan toàn bộ hệ thống")
    add_figure(doc, os.path.join(img_dir, "31_admin_nguoi_dung.png"), "Hình 2.30: Quản lý người dùng đa vai trò (Admin, Teacher, Student)")
    add_figure(doc, os.path.join(img_dir, "32_admin_vai_tro.png"), "Hình 2.31: Quản trị vai trò người dùng trong hệ thống (RBAC)")
    add_figure(doc, os.path.join(img_dir, "33_admin_quyen_han.png"), "Hình 2.32: Danh sách và đặc tả các quyền hạn chi tiết trong hệ thống")
    add_figure(doc, os.path.join(img_dir, "34_admin_chatbots.png"), "Hình 2.33: Quản lý danh sách các Chatbot cố vấn chuyên đề")
    add_figure(doc, os.path.join(img_dir, "35_admin_cau_hinh_chatbot.png"), "Hình 2.34: Cấu hình tham số RAG Pipeline (Model LLM, Temperature, Chunk size)")
    add_figure(doc, os.path.join(img_dir, "35b_admin_tao_chatbot.png"), "Hình 2.35: Biểu mẫu tạo mới Chatbot cố vấn chuyên ngành")
    add_figure(doc, os.path.join(img_dir, "36_admin_mon_hoc.png"), "Hình 2.36: Quản lý danh mục học phần toàn khóa và cấu hình tiên quyết")
    add_figure(doc, os.path.join(img_dir, "37_admin_bang_diem.png"), "Hình 2.37: Giao diện cập nhật và nhập điểm thi sinh viên hàng kỳ")
    add_figure(doc, os.path.join(img_dir, "38_admin_bo_du_lieu.png"), "Hình 2.38: Quản trị kho tài liệu tri thức học tập toàn trường")
    add_figure(doc, os.path.join(img_dir, "38b_admin_chi_tiet_bo_du_lieu.png"), "Hình 2.39: Chi tiết các tệp PDF đã phân đoạn và lập chỉ mục vector")
    add_figure(doc, os.path.join(img_dir, "39_admin_cai_dat.png"), "Hình 2.40: Cài đặt dịch vụ LLM Provider mặc định")
    add_figure(doc, os.path.join(img_dir, "40_admin_tro_chuyen.png"), "Hình 2.41: Giao diện kiểm thử trò chuyện AI phía Quản trị viên")

    doc.add_page_break()
