# TÀI LIỆU HỆ THỐNG SƠ ĐỒ KỸ THUẬT (MERMAID DIAGRAMS)

Hệ thống: **Cố vấn Học tập Khoa CNTT (IT Student Chatbot Advisor)**

## Sơ đồ thực thể liên kết (ERD) Cơ sở dữ liệu PostgreSQL 15

```mermaid
erDiagram
    USERS {
        uuid id PK
        string email UK
        string full_name
        string student_id UK
        string class_name
        string major
        boolean is_active
    }
    ROLES {
        uuid id PK
        string name UK
        string description
    }
    PERMISSIONS {
        uuid id PK
        string code UK
        string name
    }
    USER_ROLES {
        uuid user_id PK,FK
        uuid role_id PK,FK
    }
    ROLE_PERMISSIONS {
        uuid role_id PK,FK
        uuid permission_id PK,FK
    }
    COURSES {
        uuid id PK
        string course_code UK
        string name
        int credits
        int semester
        string course_type
        string career_track
    }
    COURSE_PREREQUISITES {
        uuid id PK
        uuid course_id FK
        uuid prerequisite_course_id FK
        string prereq_type
    }
    STUDENT_ACADEMIC_RECORDS {
        uuid id PK
        uuid student_id FK
        uuid course_id FK
        string score_letter
        numeric score_number
        string status
        string academic_year
    }
    LEARNING_MATERIALS {
        uuid id PK
        string title
        string course_code
        string material_type
        string author
        string file_path
    }
    CHATBOTS {
        uuid id PK
        string name
        text system_prompt
        string model_name
        boolean is_active
    }
    DATASETS {
        uuid id PK
        string name
        string collection_name
        int total_chunks
    }
    CHAT_SESSIONS {
        uuid id PK
        uuid user_id FK
        uuid chatbot_id FK
        string title
    }
    CHAT_MESSAGES {
        uuid id PK
        uuid session_id FK
        string sender_role
        text content
    }

    USERS ||--o{ USER_ROLES : "has_role"
    ROLES ||--o{ USER_ROLES : "assigned_to"
    ROLES ||--o{ ROLE_PERMISSIONS : "grants"
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : "defines"

    USERS ||--o{ STUDENT_ACADEMIC_RECORDS : "earns"
    COURSES ||--o{ STUDENT_ACADEMIC_RECORDS : "evaluated_in"

    COURSES ||--o{ COURSE_PREREQUISITES : "requires"
    COURSES ||--o{ COURSE_PREREQUISITES : "prerequisite_of"

    COURSES ||--o{ LEARNING_MATERIALS : "references"

    USERS ||--o{ CHAT_SESSIONS : "owns"
    CHATBOTS ||--o{ CHAT_SESSIONS : "serves"
    CHAT_SESSIONS ||--o{ CHAT_MESSAGES : "contains"
    CHATBOTS ||--o{ DATASETS : "links_knowledge"
```

---

## Sơ đồ khối kiến trúc hệ thống Microservices

```mermaid
flowchart TB
    subgraph CLIENT_TIER["1. TẦNG NGƯỜI DÙNG & THIẾT BỊ (PRESENTATION TIER)"]
        direction LR
        SV["Sinh viên Khoa CNTT<br/>(Tra cứu môn, tài liệu, Live Voice)"]
        GV["Giảng viên / Cố vấn học tập<br/>(Xem tiến độ lớp, quản lý tài liệu)"]
        AD["Quản trị viên (Admin)<br/>(Quản lý hệ thống, RBAC, CSDL)"]
        WEB["Ứng dụng Web Next.js 14 Responsive<br/>(Port :3000 - SSR, TailwindCSS, Audio Visualizer)"]
        SV --> WEB
        GV --> WEB
        AD --> WEB
    end

    subgraph API_TIER["2. TẦNG DỊCH VỤ MICROSERVICES (BACKEND APIS)"]
        direction TB
        subgraph AUTH_SVC["Auth Service (FastAPI - Port :8001)"]
            AUTH_API["REST Endpoints: /api/v1/auth<br/>(Login, Register, Refresh, Forgot Password)"]
            RBAC_ENG["RBAC Engine & JWT Token Signer<br/>(PBKDF2 Password Hasher)"]
            AUTH_API --> RBAC_ENG
        end

        subgraph CORE_SVC["Core Chatbot Service (FastAPI - Port :8000)"]
            CORE_API["API Gateway & Controllers<br/>(/chat, /academic, /materials, /voice)"]
            INTENT_CLF["Bộ phân loại ý định (Intent Classifier)<br/>COURSE_ADVICE | MATERIAL_QA | HYBRID"]
            RAG_ENG["Hybrid RAG & Facts Injection Engine<br/>(Semantic Cache, Context Assembler)"]
            VOICE_ENG["Live Voice Engine<br/>(STT Whisper / TTS Audio Streaming)"]
            CORE_API --> INTENT_CLF
            INTENT_CLF --> RAG_ENG
            CORE_API --> VOICE_ENG
        end
    end

    subgraph DATA_TIER["3. TẦNG LƯU TRỮ VÀ TÌM KIẾM DỮ LIỆU (DATA ENGINES)"]
        direction LR
        PG[("PostgreSQL 15 (Port :5432)<br/>- Users, Roles, RBAC<br/>- 23 Courses, DAG Prerequisites<br/>- Academic Records, Materials<br/>- Function: fn_student_eligible_courses")]
        QD[("Qdrant Vector DB (Port :6333)<br/>- Collection: it_materials<br/>- Vector Dense 768 dims (HNSW)<br/>- Semantic Payload Metadata")]
        RD[("Redis Memory Cache (Port :6379)<br/>- User Session Tokens<br/>- Per-user Semantic Cache")]
    end

    subgraph AI_TIER["4. TẦNG TRÍ TUỆ NHÂN TẠO & MÔ HÌNH NGÔN NGỮ (AI ENGINES)"]
        direction LR
        SBERT["Vietnamese-SBERT<br/>(Embedding 768 chiều tiếng Việt)"]
        RERANK["Cross-Encoder Reranker<br/>(Tái xếp hạng Top-5 chunks)"]
        LLM["Mô hình ngôn ngữ lớn (LLM)<br/>(Prompt Assembly, Fact Injection, Streaming)"]
    end

    WEB -->|"HTTP REST / JWT"| AUTH_API
    WEB -->|"HTTP REST / Server-Sent Events"| CORE_API

    AUTH_SVC -->|"SQLAlchemy ORM"| PG
    AUTH_SVC -->|"Cache Tokens"| RD

    CORE_SVC -->|"SQL Query & DAG Function"| PG
    CORE_SVC -->|"ANN Vector Search"| QD
    CORE_SVC -->|"Semantic Caching"| RD

    RAG_ENG -->|"Text Vectorization"| SBERT
    RAG_ENG -->|"Precision Reranking"| RERANK
    RAG_ENG -->|"Prompt + AcademicFacts"| LLM
```

---

## Sơ đồ luồng xử lý Hybrid RAG và Tiêm tri thức học vụ

```mermaid
flowchart TD
    START(["Sinh viên gửi câu hỏi tự nhiên<br/>Ví dụ: 'Kỳ tới em được học môn gì?'"]) --> AUTH{"Xác thực JWT Token &<br/>Trích xuất student_id"}
    
    AUTH -->|"Hợp lệ"| CACHE{"Kiểm tra Semantic Cache<br/>(User-isolated Cache Key)"}
    AUTH -->|"Không hợp lệ"| ERR["Trả mã lỗi 401 Unauthorized"]
    
    CACHE -->|"Hit (Khoảng cách Cosine nhỏ hơn 0.08)"| HIT_RESP["Trả câu trả lời từ Cache tức thì<br/>(Độ trễ dưới 100ms)"]
    CACHE -->|"Miss"| INTENT["Intent Classifier<br/>Phân tích ý định & Trích xuất thực thể"]

    INTENT --> BRANCH{"Loại ý định người dùng"}

    BRANCH -->|"COURSE_ADVICE<br/>(Tư vấn môn học)"| PATH_ACAD["1. Truy vấn Hàm SQL PostgreSQL 15<br/>fn_student_eligible_courses(student_id)<br/>Duyệt đồ thị DAG môn học tiên quyết"]
    BRANCH -->|"MATERIAL_QA<br/>(Hỏi đáp tài liệu)"| PATH_MAT["2. Nhúng câu hỏi bằng Vietnamese-SBERT<br/>Vector Search Qdrant Top-20<br/>Rerank Top-5 chunks chuẩn"]
    BRANCH -->|"HYBRID / GENERAL<br/>(Hỗn hợp)"| PATH_HYBRID["3. Thực thi song song cả 2 nhánh:<br/>Truy vấn SQL Facts + Vector Search"]

    PATH_ACAD --> FACTS["Đóng gói Tri thức học vụ xác thực<br/>AcademicFacts: Môn đủ điều kiện, Luật tiên quyết, Điểm GPA"]
    PATH_MAT --> CHUNKS["Trích xuất Đoạn văn bản tinh hoa<br/>RetrievedDocs: Giáo trình, Đề cương, Slide bài giảng"]
    PATH_HYBRID --> FACTS
    PATH_HYBRID --> CHUNKS

    FACTS --> PROMPT["Ghép Prompt chuẩn mực:<br/>System Instruction + AcademicFacts + RetrievedDocs + Lịch sử hội thoại"]
    CHUNKS --> PROMPT

    PROMPT --> LLM["Mô hình ngôn ngữ lớn (LLM)<br/>Sinh phản hồi tự nhiên theo phong cách cố vấn học tập<br/>(Quy tắc: Tuyệt đối không bịa đặt môn học, zero hallucination)"]

    LLM --> STREAM["Truyền luồng dữ liệu thời gian thực (SSE Streaming)<br/>Kèm thẻ tải tài liệu và trích dẫn nguồn"]
    STREAM --> SAVE["Lưu lịch sử vào PostgreSQL & Cập nhật Semantic Cache Redis"]
    SAVE --> END_NODE(["Sinh viên nhận câu trả lời hoàn chỉnh"])
```

---

## Sơ đồ Đồ thị có hướng không chu trình (DAG) tiên quyết môn học

```mermaid
flowchart TB
    subgraph K1["HỌC KỲ 1 (ĐẠI CƯƠNG)"]
        K1_GT1["Giải tích 1 (3 TC)"]
        K1_THDC["Tin học đại cương (3 TC)"]
        K1_DSTT["Đại số tuyến tính (3 TC)"]
        K1_ENG1["Tiếng Anh 1 (3 TC)"]
        K1_TRIET["Triết học Mác-Lênin (3 TC)"]
    end

    subgraph K2["HỌC KỲ 2 (CƠ SỞ)"]
        K2_GT2["Giải tích 2 (3 TC)"]
        K2_NMLT["Nhập môn lập trình (3 TC)"]
        K2_CTRR["Cấu trúc rời rạc (3 TC)"]
        K2_PHYS["Vật lý đại cương (3 TC)"]
        K2_ENG2["Tiếng Anh 2 (3 TC)"]
    end

    subgraph K3["HỌC KỲ 3 (LẬP TRÌNH)"]
        K3_KTLT["Kỹ thuật lập trình (3 TC)"]
        K3_XSTK["Xác suất thống kê (3 TC)"]
        K3_KTMT["Kiến trúc máy tính (3 TC)"]
    end

    subgraph K4["HỌC KỲ 4 (CỐT LÕI CNTT)"]
        K4_CTDL["Cấu trúc dữ liệu & GT (4 TC)"]
        K4_CSDL["Cơ sở dữ liệu (3 TC)"]
        K4_HDH["Hệ điều hành (3 TC)"]
        K4_MMT["Mạng máy tính (3 TC)"]
    end

    subgraph K5["HỌC KỲ 5 (CHUYÊN SÂU)"]
        K5_TTNT["Trí tuệ nhân tạo (3 TC)"]
        K5_WEB["Lập trình Web (3 TC)"]
        K5_PTTK["Phân tích thiết kế HT (3 TC)"]
        K5_ATTT["An toàn thông tin (3 TC)"]
    end

    subgraph K6["HỌC KỲ 6 (ỨNG DỤNG & ĐỒ ÁN)"]
        K6_HOCMAY["Học máy / Machine Learning (3 TC)"]
        K6_NLP["Xử lý ngôn ngữ tự nhiên (3 TC)"]
        K6_DOAN["Đồ án chuyên ngành CNTT (3 TC)"]
    end

    %% Mối quan hệ tiên quyết DAG
    K1_GT1 ==>|"Tiên quyết"| K2_GT2
    K1_THDC ==>|"Tiên quyết"| K2_NMLT
    K1_ENG1 ==>|"Tiên quyết"| K2_ENG2

    K2_GT2 ==>|"Tiên quyết"| K3_XSTK
    K2_NMLT ==>|"Tiên quyết"| K3_KTLT

    K3_KTLT ==>|"Tiên quyết"| K4_CTDL
    K2_CTRR ==>|"Tiên quyết"| K4_CTDL
    K3_KTLT ==>|"Tiên quyết"| K4_CSDL
    K3_KTMT ==>|"Tiên quyết"| K4_HDH

    K4_CTDL ==>|"Tiên quyết"| K5_TTNT
    K4_CSDL ==>|"Tiên quyết"| K5_WEB
    K4_CSDL ==>|"Tiên quyết"| K5_PTTK
    K4_MMT ==>|"Tiên quyết"| K5_ATTT

    K5_TTNT ==>|"Tiên quyết"| K6_HOCMAY
    K5_TTNT ==>|"Tiên quyết"| K6_NLP
    K5_PTTK ==>|"Tiên quyết"| K6_DOAN
    K5_WEB ==>|"Tiên quyết"| K6_DOAN
```

---

## Sơ đồ ca sử dụng hệ thống (Use Case Diagram)

```mermaid
flowchart TB
    subgraph ACTORS["CÁC TÁC NHÂN HỆ THỐNG (ACTORS)"]
        direction LR
        SV["🎓 Sinh viên (Student)"]
        GV["👨‍🏫 Giảng viên / Cố vấn (Teacher)"]
        AD["⚙️ Quản trị viên (Admin)"]
    end

    subgraph SYSTEM["HỆ THỐNG CỐ VẤN HỌC TẬP KHOA CNTT (AIRC CHATBOT)"]
        direction TB

        subgraph ROW1["PHÂN HỆ TRUY CẬP VÀ NGHIỆP VỤ SINH VIÊN"]
            direction LR
            subgraph G1["1. Xác thực & Hồ sơ"]
                direction TB
                UC1(["Đăng nhập / Đăng ký"])
                UC2(["Quên & Đặt lại mật khẩu"])
                UC3(["Xem & Cập nhật hồ sơ"])
            end
            subgraph G2["2. Trợ lý Cố vấn Học vụ Sinh viên"]
                direction TB
                UC4(["Hỏi đáp quy chế & Lộ trình đào tạo"])
                UC5(["Tra cứu môn học đủ điều kiện"])
                UC6(["Tra cứu điểm & Môn cần học lại"])
                UC7(["Tìm kiếm & Tải tài liệu PDF"])
                UC8(["Tương tác giọng nói Live Voice"])
            end
        end

        subgraph ROW2["PHÂN HỆ GIẢNG VIÊN VÀ QUẢN TRỊ VIÊN"]
            direction LR
            subgraph G3["3. Nghiệp vụ Giảng viên / Cố vấn"]
                direction TB
                UC9(["Xem tiến độ học tập sinh viên"])
                UC10(["Xem trực quan sơ đồ DAG tiên quyết"])
                UC11(["Quản lý & Đóng góp tài liệu"])
                UC12(["Hỏi đáp trợ lý chuyên môn AI"])
            end
            subgraph G4["4. Nghiệp vụ Quản trị Hệ thống (Admin)"]
                direction TB
                UC13(["Quản trị người dùng & Phân quyền RBAC"])
                UC14(["Quản lý 23 môn học & Cây tiên quyết"])
                UC15(["Nhập liệu & Cập nhật bảng điểm"])
                UC16(["Quản trị kho tri thức Vector Qdrant"])
                UC17(["Cấu hình tham số RAG Pipeline & LLM"])
            end
        end
    end

    ACTORS ~~~ SYSTEM
    ROW1 ~~~ ROW2

    %% Liên kết Sinh viên
    SV --> UC1
    SV --> UC2
    SV --> UC3
    SV --> UC4
    SV --> UC5
    SV --> UC6
    SV --> UC7
    SV --> UC8

    %% Liên kết Giảng viên
    GV --> UC1
    GV --> UC3
    GV --> UC9
    GV --> UC10
    GV --> UC11
    GV --> UC12

    %% Liên kết Quản trị viên
    AD --> UC1
    AD --> UC3
    AD --> UC13
    AD --> UC14
    AD --> UC15
    AD --> UC16
    AD --> UC17
```

---

## Sơ đồ tuần tự tương tác thời gian thực (Sequence Diagram)

```mermaid
sequenceDiagram
    autonumber
    actor SV as Sinh viên (Client)
    participant UI as Next.js Web App (:3000)
    participant API as Core Service FastAPI (:8000)
    participant PG as PostgreSQL 15 (:5432)
    participant QD as Qdrant Vector DB (:6333)
    participant LLM as Mô hình ngôn ngữ lớn (LLM)

    SV->>+UI: Nhập câu hỏi: "Kỳ tới em được học môn nào?"
    UI->>+API: POST /api/v1/chat/message (Kèm JWT Bearer Token)

    API->>API: Xác thực JWT & Trích xuất student_id = 20233301
    API->>API: Intent Classifier: Nhận diện ý định = COURSE_ADVICE

    critical Truy xuất tri thức học vụ chính xác
        API->>+PG: SELECT * FROM fn_student_eligible_courses('20233301')
        Note over PG: Duyệt đồ thị DAG môn tiên quyết &<br/>Lọc các môn đã qua (PASSED), tìm môn đủ điều kiện
        PG-->>-API: Danh sách 4 môn đủ điều kiện (Mã, Tên, Tín chỉ, Lý do)
    end

    opt Khi câu hỏi yêu cầu thêm tài liệu hoặc giáo trình
        API->>+QD: Vector Search Cosine(query_vector, collection='it_materials', top_k=5)
        QD-->>-API: Top 5 đoạn văn bản đề cương chi tiết (Syllabus Chunks)
    end

    API->>API: Đóng gói Prompt:<br/>System Prompt + AcademicFacts + Retrieved Chunks

    API->>+LLM: Gửi Prompt hoàn chỉnh tới LLM
    Note over LLM: Sinh câu trả lời tự nhiên theo vai trò cố vấn,<br/>cam kết chính xác theo AcademicFacts (Zero Hallucination)
    LLM-->>-API: Phản hồi từng phần (Streaming Tokens)

    API-->>-UI: SSE Event Stream (text tokens + source citations)
    UI-->>-SV: Hiển thị phản hồi tức thì trên giao diện Chatbot
    
    API->>PG: INSERT INTO chat_messages (session_id, sender_role, content)
```

---

