# -*- coding: utf-8 -*-
"""
generate_diagrams.py
Tạo các sơ đồ kỹ thuật và kiến trúc chuẩn cho báo cáo BTL TTNT:
1. so_do_erd_database.png (Sơ đồ ERD thực thể liên kết PostgreSQL 15)
2. so_do_khoi_kien_truc.png (Sơ đồ khối kiến trúc hệ thống Microservices)
3. so_do_luong_rag_facts.png (Sơ đồ luồng xử lý RAG & Tiêm tri thức học vụ)
4. so_do_cay_tien_quyet_dag.png (Sơ đồ đồ thị DAG điều kiện tiên quyết học phần)
5. so_do_usecase_he_thong.png (Sơ đồ ca sử dụng Use Case Diagram)
6. so_do_tuan_tu_sequence.png (Sơ đồ tuần tự tương tác Sequence Diagram)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Cấu hình font chữ cho matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Times New Roman']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = "Report/image"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. SƠ ĐỒ ERD CƠ SỞ DỮ LIỆU POSTGRESQL 15
# -----------------------------------------------------------------------------
def draw_erd_diagram():
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Tiêu đề
    ax.text(8, 11.6, "SƠ ĐỒ THỰC THỂ LIÊN KẾT (ERD) — HỆ THỐNG CỐ VẤN HỌC TẬP KHOA CNTT", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#1A365D')
    ax.text(8, 11.25, "Cơ sở dữ liệu PostgreSQL 15: Phân hệ Xác thực (Auth), Học vụ (Academic) & Tri thức RAG", 
            ha='center', va='center', fontsize=11, fontstyle='italic', color='#4A5568')

    # Định nghĩa các bảng
    tables = [
        # (x, y, w, h, title, bg_header, fields)
        # AUTH
        (0.8, 7.8, 4.0, 2.8, "users", "#2B6CB0", [
            ("+ id : UUID (PK)", True),
            ("* email : VARCHAR(255) (UK)", False),
            ("* hashed_password : VARCHAR", False),
            ("* full_name : VARCHAR(255)", False),
            ("* role : 'admin'|'teacher'|'student'", False),
            ("  student_code : VARCHAR(20) (UK)", False),
            ("  department : VARCHAR(100)", False),
            ("  is_active : BOOLEAN", False),
            ("  created_at : TIMESTAMPTZ", False)
        ]),
        (0.8, 4.4, 4.0, 2.4, "roles & permissions", "#2B6CB0", [
            ("+ roles (id PK, code UK, name)", True),
            ("+ permissions (id PK, code UK, res)", True),
            ("+ user_roles (user_id FK, role_id FK)", True),
            ("+ role_permissions (role_id, perm_id)", True),
            ("  password_reset_tokens (id, user_id)", False),
            ("  is_system : BOOLEAN", False),
            ("  action, scope, description", False)
        ]),
        
        # ACADEMIC
        (6.0, 7.6, 4.3, 3.1, "courses", "#2C7A7B", [
            ("+ id : UUID (PK)", True),
            ("* course_code : VARCHAR(20) (UK)", False),
            ("* course_name : VARCHAR(255)", False),
            ("* credits : INTEGER CHECK > 0", False),
            ("  theory_hours : INTEGER", False),
            ("  practice_hours : INTEGER", False),
            ("  semester : INT CHECK 1..8", False),
            ("  is_mandatory : BOOLEAN", False),
            ("  career_track : 'AI'|'WEB'|'SEC'...", False),
            ("  description : TEXT", False)
        ]),
        (6.0, 4.2, 4.3, 2.6, "course_prerequisites (DAG)", "#2C7A7B", [
            ("+ id : UUID (PK)", True),
            ("* course_id : UUID (FK -> courses)", True),
            ("* prerequisite_id : UUID (FK -> courses)", True),
            ("* prereq_type : VARCHAR(20)", False),
            ("    'PREREQUISITE' (bắt buộc cứng)", False),
            ("    'PREVIOUS' (học trước)", False),
            ("    'COREQUISITE' (song hành)", False),
            ("  created_at : TIMESTAMPTZ", False)
        ]),
        (6.0, 0.8, 4.3, 2.8, "student_academic_records", "#2C7A7B", [
            ("+ id : UUID (PK)", True),
            ("* student_id : UUID (FK -> users)", True),
            ("* course_id : UUID (FK -> courses)", True),
            ("* semester : VARCHAR(20)", False),
            ("* academic_year : VARCHAR(20)", False),
            ("  score_10 : NUMERIC(4,2)", False),
            ("  score_4 : NUMERIC(3,2)", False),
            ("  score_letter : VARCHAR(2)", False),
            ("* status : 'PASSED'|'FAILED'|'IN_PROGRESS'", False)
        ]),

        # RAG & MATERIALS
        (11.2, 7.8, 4.2, 2.8, "learning_materials", "#744210", [
            ("+ id : UUID (PK)", True),
            ("* course_id : UUID (FK -> courses)", True),
            ("* title : VARCHAR(255)", False),
            ("* material_type : VARCHAR(50)", False),
            ("    'SYLLABUS' | 'TEXTBOOK'", False),
            ("    'LECTURE_SLIDE' | 'EXAM'", False),
            ("  file_id : UUID (FK -> files)", True),
            ("  download_url : TEXT", False),
            ("  is_active : BOOLEAN", False)
        ]),
        (11.2, 4.3, 4.2, 2.8, "chatbots & datasets", "#744210", [
            ("+ chatbots (id PK, name, model, prompt)", True),
            ("+ datasets (id PK, name, collection)", True),
            ("+ files (id PK, path, size, mime)", True),
            ("+ dataset_files (dataset_id, file_id)", True),
            ("  qdrant_collection : VARCHAR", False),
            ("  temperature, top_k, max_tokens", False),
            ("  total_chunks : INTEGER", False)
        ]),
        (11.2, 0.8, 4.2, 2.8, "chat_sessions & messages", "#744210", [
            ("+ chat_sessions (id PK, user_id, bot_id)", True),
            ("+ chat_messages (id PK, session_id)", True),
            ("  sender_type : 'user' | 'bot'", False),
            ("  message_text : TEXT", False),
            ("  citations : JSONB (source PDF, page)", False),
            ("  academic_facts_injected : JSONB", False),
            ("  latency_ms : INTEGER", False),
            ("  created_at : TIMESTAMPTZ", False)
        ])
    ]

    for x, y, w, h, title, hdr_col, fields in tables:
        # Box chính
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                      linewidth=1.2, edgecolor='#A0AEC0', facecolor='#FFFFFF')
        ax.add_patch(rect)
        # Header box
        hdr_rect = patches.FancyBboxPatch((x, y + h - 0.45), w, 0.45, boxstyle="round,pad=0.08,rounding_size=0.15",
                                           linewidth=1.2, edgecolor=hdr_col, facecolor=hdr_col)
        ax.add_patch(hdr_rect)
        ax.text(x + w/2, y + h - 0.22, title.upper(), ha='center', va='center', fontsize=10.5, fontweight='bold', color='white')
        
        # Fields
        cur_y = y + h - 0.68
        for fld, is_key in fields:
            f_col = '#C53030' if is_key else '#2D3748'
            f_wt = 'bold' if is_key else 'normal'
            ax.text(x + 0.15, cur_y, fld, ha='left', va='center', fontsize=8.2, fontweight=f_wt, color=f_col)
            cur_y -= 0.25

    # Vẽ đường nối quan hệ giữa các bảng
    def draw_rel(x1, y1, x2, y2, label=""):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.4", color="#4A5568", lw=1.3,
                                    connectionstyle="arc3,rad=0.05"))
        if label:
            ax.text((x1 + x2)/2, (y1 + y2)/2, label, ha='center', va='center', fontsize=7.5,
                    bbox=dict(boxstyle="round,pad=0.1", fc="#EDF2F7", ec="none", alpha=0.9))

    draw_rel(4.8, 8.8, 6.0, 2.2, "1 - n (student_records)")
    draw_rel(6.0, 8.5, 6.0, 5.5, "1 - n (prereq)")
    draw_rel(10.3, 8.5, 11.2, 8.5, "1 - n (materials)")
    draw_rel(10.3, 8.0, 10.3, 3.0, "courses 1 - n records")
    draw_rel(4.8, 8.2, 11.2, 2.2, "user 1 - n chat_sessions")
    draw_rel(13.3, 7.8, 13.3, 7.1, "materials 1 - 1 files")

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "so_do_erd_database.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 2. SƠ ĐỒ KHỐI KIẾN TRÚC HỆ THỐNG
# -----------------------------------------------------------------------------
def draw_architecture_diagram():
    fig, ax = plt.subplots(figsize=(15, 9), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(7.5, 8.6, "SƠ ĐỒ KHỐI KIẾN TRÚC HỆ THỐNG MICROSERVICES", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#1A365D')
    ax.text(7.5, 8.25, "Kiến trúc 3 phân tầng độc lập: Tầng Trình diễn (UI), Tầng Dịch vụ (Core/Auth) & Tầng Dữ liệu AI", 
            ha='center', va='center', fontsize=10.5, fontstyle='italic', color='#4A5568')

    # Layer 1: Frontend
    box_ui = patches.FancyBboxPatch((1.0, 6.4), 13.0, 1.4, boxstyle="round,pad=0.1",
                                    linewidth=1.5, edgecolor='#3182CE', facecolor='#EBF8FF')
    ax.add_patch(box_ui)
    ax.text(1.3, 7.5, "TẦNG TRÌNH DIỄN (FRONTEND CLIENT — NEXT.JS 14 APP ROUTER :3000)", fontsize=11, fontweight='bold', color='#2B6CB0')
    ui_sub = ["Chatbot Sinh viên (/dashboard/chat)", "Môn đủ điều kiện (/courses)", "Bảng điểm cá nhân (/grades)", 
              "Kho tài liệu PDF (/materials)", "Trợ lý giọng nói Live Voice", "Dashboard Giảng viên & Quản trị"]
    for i, s in enumerate(ui_sub):
        col_x = 1.3 + (i % 3) * 4.2
        row_y = 7.0 if i < 3 else 6.6
        ax.text(col_x, row_y, f"• {s}", fontsize=9, color='#2D3748')

    # Mũi tên UI -> API
    ax.annotate('', xy=(7.5, 5.7), xytext=(7.5, 6.4),
                arrowprops=dict(arrowstyle="<->,head_width=0.3,head_length=0.4", color="#4A5568", lw=1.8))
    ax.text(7.5, 6.05, "RESTful API / SSE Streaming (JWT Bearer Token)", ha='center', va='center', fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.15", fc="#FFF", ec="#CBD5E0"))

    # Layer 2: Microservices
    box_api1 = patches.FancyBboxPatch((1.0, 3.6), 6.2, 1.9, boxstyle="round,pad=0.1",
                                      linewidth=1.5, edgecolor='#805AD5', facecolor='#FAF5FF')
    ax.add_patch(box_api1)
    ax.text(1.2, 5.2, "it_auth Service (FastAPI — Port 8001)", fontsize=11, fontweight='bold', color='#6B46C1')
    ax.text(1.2, 4.8, "• JWT Access & Refresh Token Provider", fontsize=9, color='#2D3748')
    ax.text(1.2, 4.5, "• Mã hóa băm mật khẩu PBKDF2-SHA256", fontsize=9, color='#2D3748')
    ax.text(1.2, 4.2, "• Kiểm soát truy cập phân quyền đa vai trò RBAC", fontsize=9, color='#2D3748')
    ax.text(1.2, 3.9, "• Quản lý tài khoản (Admin, Teacher, Student)", fontsize=9, color='#2D3748')

    box_api2 = patches.FancyBboxPatch((7.8, 3.6), 6.2, 1.9, boxstyle="round,pad=0.1",
                                      linewidth=1.5, edgecolor='#319795', facecolor='#E6FFFA')
    ax.add_patch(box_api2)
    ax.text(8.0, 5.2, "it_core Service (FastAPI RAG Engine — Port 8000)", fontsize=11, fontweight='bold', color='#234E52')
    ax.text(8.0, 4.8, "• Intent Classifier (COURSE_ADVICE | MATERIAL | HYBRID)", fontsize=9, color='#2D3748')
    ax.text(8.0, 4.5, "• Academic Facts Injector (Điểm số & Cây tiên quyết)", fontsize=9, color='#2D3748')
    ax.text(8.0, 4.2, "• Per-user Semantic Caching (Cosine Distance <= 0.08)", fontsize=9, color='#2D3748')
    ax.text(8.0, 3.9, "• Vector Search, Cross-Encoder Rerank & LLM Streaming", fontsize=9, color='#2D3748')

    # Mũi tên Services -> Database
    ax.annotate('', xy=(4.1, 2.7), xytext=(4.1, 3.6),
                arrowprops=dict(arrowstyle="<->,head_width=0.3,head_length=0.4", color="#4A5568", lw=1.5))
    ax.annotate('', xy=(10.9, 2.7), xytext=(10.9, 3.6),
                arrowprops=dict(arrowstyle="<->,head_width=0.3,head_length=0.4", color="#4A5568", lw=1.5))

    # Layer 3: Database & AI
    db_boxes = [
        (1.0, 0.6, 4.0, 1.9, "PostgreSQL 15 (Port 5432)", "#2C5282", "#EBF8FF", [
            "Users, Roles, RBAC permissions",
            "23 Học phần chuẩn & 25 tiên quyết DAG",
            "Bảng điểm cá nhân sinh viên",
            "Hàm logic fn_student_eligible_courses"
        ]),
        (5.5, 0.6, 4.0, 1.9, "Qdrant Vector DB (Port 6333)", "#C53030", "#FFF5F5", [
            "Lập chỉ mục HNSW Graph tốc độ cao",
            "Dense Embeddings (Vietnamese-SBERT)",
            "Lọc Chunks theo metadata course_id",
            "Truy hồi độ tương đồng Cosine < 20ms"
        ]),
        (10.0, 0.6, 4.0, 1.9, "Redis Cache & LLM Service", "#D69E2E", "#FFFFF0", [
            "Semantic Cache phân lập theo User ID",
            "Hàng đợi Background Worker Ingest PDF",
            "Tái xếp hạng Cross-Encoder Reranker",
            "Dịch vụ LLM tạo sinh câu trả lời tự nhiên"
        ])
    ]

    for x, y, w, h, title, b_col, bg_col, items in db_boxes:
        b = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                   linewidth=1.5, edgecolor=b_col, facecolor=bg_col)
        ax.add_patch(b)
        ax.text(x + 0.15, y + h - 0.35, title, fontsize=10, fontweight='bold', color=b_col)
        for idx, itm in enumerate(items):
            ax.text(x + 0.15, y + h - 0.7 - idx * 0.28, f"✔ {itm}", fontsize=8.2, color='#2D3748')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "so_do_khoi_kien_truc.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 3. SƠ ĐỒ LUỒNG RAG VÀ TIÊM TRI THỨC HỌC VỤ
# -----------------------------------------------------------------------------
def draw_rag_facts_flow():
    fig, ax = plt.subplots(figsize=(15, 9), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(7.5, 8.6, "SƠ ĐỒ LUỒNG XỬ LÝ HYBRID RAG & TIÊM TRI THỨC HỌC VỤ", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#1A365D')
    ax.text(7.5, 8.25, "Quy trình kết hợp giữa Semantic Cache theo User, Lập luận DAG và Truy hồi Vector chống ảo giác", 
            ha='center', va='center', fontsize=10.5, fontstyle='italic', color='#4A5568')

    # Các khối quy trình
    steps = [
        (1.0, 6.2, 2.5, 1.2, "1. Câu hỏi sinh viên\n(User Query)", "#3182CE", "#EBF8FF"),
        (4.2, 6.2, 3.2, 1.2, "2. Kiểm tra Semantic Cache\n(Per-user Cosine Dist <= 0.08)", "#DD6B20", "#FFFAF0"),
        (8.2, 6.2, 2.8, 1.2, "3. Phân loại ý định\n(Intent Classifier)", "#805AD5", "#FAF5FF"),
        (11.8, 6.2, 2.5, 1.2, "4. Trả lời ngay\n(< 100ms Cache Hit)", "#38A169", "#F0FFF4"),
        
        # Nhánh Course & Facts
        (6.0, 3.8, 3.8, 1.4, "5A. Trích xuất [AcademicFacts]\n- Bảng điểm thực tế từ PostgreSQL\n- Duyệt DAG: fn_student_eligible_courses", "#2C7A7B", "#E6FFFA"),
        
        # Nhánh Material QA
        (10.5, 3.8, 3.8, 1.4, "5B. Truy hồi tài liệu (Qdrant)\n- Vectorize với Vietnamese-SBERT\n- Top-20 Cosine Search + Rerank Top-5", "#B7791F", "#FEFCBF"),
        
        # Đóng gói & LLM
        (7.0, 1.2, 6.5, 1.6, "6. Đóng gói Prompt chuyên gia & Gọi LLM\nPrompt = System Rules + [AcademicFacts] + [Knowledge Chunks] + Query\n--> Sinh phản hồi chính xác 100%, trích nguồn PDF & Stream về UI", "#2B6CB0", "#EBF8FF")
    ]

    for x, y, w, h, text, b_col, bg_col in steps:
        b = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                   linewidth=1.3, edgecolor=b_col, facecolor=bg_col)
        ax.add_patch(b)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=9.2, fontweight='bold', color=b_col)

    # Các mũi tên
    def arrow(x1, y1, x2, y2, label=""):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->,head_width=0.25,head_length=0.35", color="#4A5568", lw=1.5))
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + 0.18, label, ha='center', va='center', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.1", fc="#FFF", ec="#CBD5E0"))

    arrow(3.5, 6.8, 4.2, 6.8)
    arrow(7.4, 6.8, 8.2, 6.8, "Cache Miss")
    arrow(5.8, 6.2, 11.8, 6.8, "Cache Hit")
    arrow(9.6, 6.2, 7.9, 5.2, "COURSE_ADVICE")
    arrow(9.6, 6.2, 12.4, 5.2, "MATERIAL_QA")
    arrow(7.9, 3.8, 9.5, 2.8)
    arrow(12.4, 3.8, 11.0, 2.8)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "so_do_luong_rag_facts.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 4. SƠ ĐỒ ĐỒ THỊ DAG QUAN HỆ TIÊN QUYẾT
# -----------------------------------------------------------------------------
def draw_prerequisite_dag():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(8, 8.6, "ĐỒ THỊ CÓ HƯỚNG KHÔNG CHU TRÌNH (DAG) MÔN HỌC TIÊN QUYẾT KHOA CNTT", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#1A365D')
    ax.text(8, 8.25, "Mô hình phụ thuộc học phần từ Học kỳ 1 đến Học kỳ 6: Ràng buộc Tiên quyết (Prerequisite)", 
            ha='center', va='center', fontsize=10.5, fontstyle='italic', color='#4A5568')

    # Vẽ các cột học kỳ
    semesters = ["HỌC KỲ 1", "HỌC KỲ 2", "HỌC KỲ 3", "HỌC KỲ 4", "HỌC KỲ 5", "HỌC KỲ 6"]
    for i, sem in enumerate(semesters):
        sx = 1.0 + i * 2.4
        ax.text(sx + 0.9, 7.8, sem, ha='center', va='center', fontsize=10, fontweight='bold', color='#718096')
        ax.plot([sx + 0.9, sx + 0.9], [0.8, 7.5], color='#E2E8F0', linestyle='--', lw=1.2)

    # Tọa độ các môn học (x, y, code, name, color)
    courses = [
        # HK1
        (1.0, 6.2, "INT1101", "Tin học đại cương", "#3182CE"),
        (1.0, 4.4, "INT1102", "Giải tích", "#3182CE"),
        (1.0, 2.6, "INT1103", "Đại số tuyến tính", "#3182CE"),
        
        # HK2
        (3.4, 6.2, "INT1201", "Kỹ thuật lập trình C++", "#3182CE"),
        (3.4, 4.4, "INT1202", "Toán rời rạc", "#3182CE"),
        (3.4, 2.6, "INT1203", "Kiến trúc máy tính", "#3182CE"),
        (3.4, 1.0, "INT1204", "Mạng máy tính", "#3182CE"),
        
        # HK3
        (5.8, 6.2, "INT2102", "Cấu trúc DL & GT", "#2C7A7B"),
        (5.8, 4.4, "INT2103", "Cơ sở dữ liệu", "#2C7A7B"),
        (5.8, 2.6, "INT2101", "Hệ điều hành", "#2C7A7B"),
        (5.8, 1.0, "INT2104", "Lập trình Web", "#2C7A7B"),

        # HK4
        (8.2, 6.2, "INT2202", "Trí tuệ nhân tạo", "#D69E2E"),
        (8.2, 4.4, "INT2201", "Lập trình OOP Java", "#D69E2E"),
        (8.2, 2.6, "INT2204", "Công nghệ phần mềm", "#D69E2E"),

        # HK5
        (10.6, 6.2, "INT3101", "Học máy (Machine Learning)", "#DD6B20"),
        (10.6, 4.4, "INT3104", "Web nâng cao (React/Node)", "#DD6B20"),
        (10.6, 2.6, "INT3105", "An toàn thông tin", "#DD6B20"),

        # HK6
        (13.0, 6.8, "INT3201", "Học sâu & Thị giác", "#9B2C2C"),
        (13.0, 5.4, "INT3202", "Xử lý ngôn ngữ tự nhiên", "#9B2C2C"),
        (13.0, 3.6, "INT4101", "Cloud & DevOps", "#9B2C2C")
    ]

    c_pos = {}
    for x, y, code, name, col in courses:
        c_pos[code] = (x + 1.0, y + 0.4)
        b = patches.FancyBboxPatch((x, y), 2.0, 0.8, boxstyle="round,pad=0.08",
                                   linewidth=1.2, edgecolor=col, facecolor='#FFFFFF')
        ax.add_patch(b)
        ax.text(x + 1.0, y + 0.52, code, ha='center', va='center', fontsize=8.5, fontweight='bold', color=col)
        ax.text(x + 1.0, y + 0.24, name, ha='center', va='center', fontsize=6.8, color='#4A5568')

    # Các cạnh phụ thuộc tiên quyết (u -> v có nghĩa u là tiên quyết của v)
    edges = [
        ("INT1101", "INT1201"),
        ("INT1201", "INT2102"),
        ("INT2102", "INT2202"),
        ("INT2202", "INT3101"),
        ("INT3101", "INT3201"),
        ("INT3101", "INT3202"),
        ("INT1103", "INT2202"),
        ("INT1203", "INT2101"),
        ("INT1202", "INT2103"),
        ("INT2102", "INT2201"),
        ("INT2201", "INT2104"),
        ("INT2104", "INT3104"),
        ("INT2103", "INT2204"),
        ("INT2201", "INT2204"),
        ("INT1204", "INT3105"),
        ("INT2101", "INT4101"),
        ("INT3104", "INT4101")
    ]

    for u, v in edges:
        if u in c_pos and v in c_pos:
            x1, y1 = c_pos[u]
            x2, y2 = c_pos[v]
            ax.annotate('', xy=(x2 - 1.0, y2), xytext=(x1 + 1.0, y1),
                        arrowprops=dict(arrowstyle="->,head_width=0.2,head_length=0.3", color="#718096", lw=1.2))

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "so_do_cay_tien_quyet_dag.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 5. SƠ ĐỒ USE CASE HỆ THỐNG
# -----------------------------------------------------------------------------
def draw_usecase_diagram():
    fig, ax = plt.subplots(figsize=(15, 9), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(7.5, 8.6, "SƠ ĐỒ CA SỬ DỤNG (USE CASE DIAGRAM) — HỆ THỐNG CỐ VẤN HỌC TẬP", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#1A365D')
    ax.text(7.5, 8.25, "Phân quyền tương tác giữa 3 tác nhân: Sinh viên, Giảng viên / Cố vấn và Quản trị viên", 
            ha='center', va='center', fontsize=10.5, fontstyle='italic', color='#4A5568')

    # Khung ranh giới hệ thống (System Boundary)
    boundary = patches.Rectangle((3.8, 0.6), 7.6, 7.3, fill=False, edgecolor='#4A5568', linestyle='--', lw=1.5)
    ax.add_patch(boundary)
    ax.text(4.0, 7.65, "HỆ THỐNG CỐ VẤN HỌC TẬP KHOA CNTT", fontsize=11, fontweight='bold', color='#2B6CB0')

    # Actors
    def draw_actor(x, y, name, color):
        circle = patches.Circle((x, y + 0.4), 0.25, edgecolor=color, facecolor='#FFF', lw=1.5)
        ax.add_patch(circle)
        ax.plot([x, x], [y + 0.15, y - 0.3], color=color, lw=1.5)  # Body
        ax.plot([x - 0.3, x + 0.3], [y, y], color=color, lw=1.5)  # Arms
        ax.plot([x, x - 0.25], [y - 0.3, y - 0.65], color=color, lw=1.5)  # Left leg
        ax.plot([x, x + 0.25], [y - 0.3, y - 0.65], color=color, lw=1.5)  # Right leg
        ax.text(x, y - 0.9, name, ha='center', va='center', fontsize=9.5, fontweight='bold', color=color)

    draw_actor(1.8, 5.5, "Sinh viên\n(Student)", "#2B6CB0")
    draw_actor(1.8, 2.0, "Giảng viên\n(Teacher)", "#2C7A7B")
    draw_actor(13.2, 4.0, "Quản trị viên\n(Admin)", "#C53030")

    # Use Cases (Ellipses)
    usecases = [
        (7.6, 7.0, "Đăng nhập / Đổi mật khẩu", ["SV", "GV", "AD"]),
        (7.6, 6.1, "Chat hỏi đáp & Tư vấn môn học", ["SV"]),
        (7.6, 5.2, "Tra cứu môn đủ điều kiện học kỳ tới", ["SV", "GV"]),
        (7.6, 4.3, "Tra cứu bảng điểm cá nhân & GPA", ["SV"]),
        (7.6, 3.4, "Tìm kiếm & Tải tài liệu học tập PDF", ["SV", "GV"]),
        (7.6, 2.5, "Tương tác giọng nói Live Voice", ["SV"]),
        (7.6, 1.6, "Tra cứu bảng điểm sinh viên theo lớp", ["GV", "AD"]),
        (7.6, 0.9, "Quản lý CSDL, Môn học & RAG Pipeline", ["AD"])
    ]

    for x, y, uc_text, actors in usecases:
        ellipse = patches.Ellipse((x, y), 4.6, 0.65, edgecolor='#3182CE', facecolor='#F7FAFC', lw=1.2)
        ax.add_patch(ellipse)
        ax.text(x, y, uc_text, ha='center', va='center', fontsize=8.8, fontweight='bold', color='#2D3748')

        # Nối actor vào use case
        if "SV" in actors:
            ax.plot([2.3, x - 2.2], [5.5, y], color='#A0AEC0', lw=1.0)
        if "GV" in actors:
            ax.plot([2.3, x - 2.2], [2.0, y], color='#A0AEC0', lw=1.0)
        if "AD" in actors:
            ax.plot([12.7, x + 2.2], [4.0, y], color='#A0AEC0', lw=1.0)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "so_do_usecase_he_thong.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 6. SƠ ĐỒ TUẦN TỰ TƯƠNG TÁC (SEQUENCE DIAGRAM)
# -----------------------------------------------------------------------------
def draw_sequence_diagram():
    fig, ax = plt.subplots(figsize=(15, 9), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9)
    ax.axis('off')

    ax.text(7.5, 8.6, "SƠ ĐỒ TUẦN TỰ (SEQUENCE DIAGRAM) — LUỒNG HỎI ĐÁP HỌC VỤ", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#1A365D')
    ax.text(7.5, 8.25, "Trình tự tương tác giữa Sinh viên, Next.js UI, it_core API, PostgreSQL, Qdrant và LLM Service", 
            ha='center', va='center', fontsize=10.5, fontstyle='italic', color='#4A5568')

    participants = [
        (1.5, "Sinh viên\n(User)"),
        (4.0, "Frontend UI\n(Next.js :3000)"),
        (7.0, "Core Service\n(FastAPI :8000)"),
        (9.5, "PostgreSQL 15\n(Academic DB)"),
        (11.8, "Qdrant Vector DB\n(ANN Index)"),
        (14.0, "Dịch vụ LLM\n(LLM Service)")
    ]

    for x, name in participants:
        # Box header
        b = patches.FancyBboxPatch((x - 0.9, 7.3), 1.8, 0.7, boxstyle="round,pad=0.08",
                                   linewidth=1.2, edgecolor='#2B6CB0', facecolor='#EBF8FF')
        ax.add_patch(b)
        ax.text(x, 7.65, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2B6CB0')
        # Lifeline
        ax.plot([x, x], [0.8, 7.3], color='#CBD5E0', linestyle='--', lw=1.2)

    # Tương tác tuần tự
    messages = [
        (1.5, 4.0, 6.8, "1. Gửi câu hỏi học vụ ('Kỳ tới học môn gì?')"),
        (4.0, 7.0, 6.2, "2. POST /api/v1/chat (User Query + JWT Token)"),
        (7.0, 7.0, 5.6, "3. IntentClassifier -> COURSE_ADVICE"),
        (7.0, 9.5, 5.0, "4. fn_student_eligible_courses(student_id)"),
        (9.5, 7.0, 4.4, "5. Trả về: Môn PASSED, FAILED, Eligible"),
        (7.0, 11.8, 3.8, "6. Vector Search Top-20 đề cương & tài liệu PDF"),
        (11.8, 7.0, 3.2, "7. Trả về Top-5 chunks tài liệu sau Rerank"),
        (7.0, 14.0, 2.6, "8. Gửi Prompt = [AcademicFacts] + [Chunks] + Query"),
        (14.0, 7.0, 2.0, "9. Sinh câu trả lời tự nhiên (Streaming Response)"),
        (7.0, 4.0, 1.4, "10. Đẩy dữ liệu qua Server-Sent Events (SSE)"),
        (4.0, 1.5, 0.9, "11. Hiển thị tin nhắn, trích dẫn & nút tải PDF")
    ]

    for x1, x2, y, text in messages:
        if x1 == x2:
            # Self call
            ax.annotate('', xy=(x1, y - 0.2), xytext=(x1, y + 0.1),
                        arrowprops=dict(arrowstyle="->", color="#805AD5", lw=1.3,
                                        connectionstyle="arc3,rad=0.3"))
            ax.text(x1 + 0.15, y, text, fontsize=8, color='#805AD5', fontweight='bold')
        else:
            is_return = x1 > x2
            col = "#38A169" if is_return else "#2B6CB0"
            style = "--" if is_return else "-"
            ax.annotate('', xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->,head_width=0.2,head_length=0.3", color=col, linestyle=style, lw=1.3))
            ax.text((x1 + x2)/2, y + 0.14, text, ha='center', va='center', fontsize=7.8, color=col, fontweight='bold')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "so_do_tuan_tu_sequence.png")
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated:", path)

if __name__ == '__main__':
    print("Generating all technical architecture diagrams...")
    draw_erd_diagram()
    draw_architecture_diagram()
    draw_rag_facts_flow()
    draw_prerequisite_dag()
    draw_usecase_diagram()
    draw_sequence_diagram()
    print("All 6 diagrams generated successfully in Report/image/")
