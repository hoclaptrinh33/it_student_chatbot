# Thiết kế: Chatbot Cố vấn Học tập Khoa CNTT

| Trường | Giá trị |
|--------|---------|
| **Tiêu đề** | Chuyển đổi AIRC Internal Chatbot thành Chatbot Cố vấn Học tập & Tài liệu Khoa CNTT |
| **Tác giả** | Grok / team đồ án |
| **Ngày** | 2026-09-15 |
| **Trạng thái** | Draft |
| **Phạm vi** | Domain pivot monorepo hiện có — không phải hệ thống greenfield |
| **Mục tiêu luận văn** | "Xây dựng chương trình hỏi đáp bằng ngôn ngữ tự nhiên hỗ trợ chọn môn học và tài liệu học tập cho sinh viên khoa CNTT" |

---

## Overview

Hệ thống hiện tại là **AIRC Internal Chatbot**: monorepo 3 microservice (Auth FastAPI + Core RAG FastAPI + Next.js UI) trả lời câu hỏi nội bộ bằng RAG (Qdrant + Gemini). `user_context` trên đường chat chỉ có `{id, role}` để RBAC chatbot — **không** nạp bảng điểm, tiên quyết, hay lộ trình. Docker Compose và `init_db.sql` đã chuyển hạ tầng sang PostgreSQL 15 với schema học vụ đầy đủ, nhưng **Python Auth/Core vẫn Motor/MongoDB**, nên `docker compose up` các service ứng dụng sẽ fail.

Tài liệu này là nguồn sự thật triển khai để pivot domain: giữ 3 service, JWT/RBAC, ingest, Qdrant, Redis, Gemini, SSE, citations; thay Mongo → Postgres; thêm rule engine học vụ; hybrid retrieval (`COURSE_ADVICE` / `MATERIAL_QA` / `HYBRID`); inject `[AcademicFacts]` mỗi request từ JWT `user_id`; đổi persona + UI sinh viên thành cố vấn Khoa CNTT. Dữ liệu sinh viên là **mẫu** (seed + CRUD/CSV), không nối SIS/LMS/SSO.

---

## Background & Motivation

### Hiện trạng đã xác minh trên repo

| Lớp | Đường dẫn | Thực tế 2026-09-15 |
|-----|-----------|-------------------|
| Infra Docker | `docker-compose.yml`, `docker-compose.local.yml` | **DONE.** `postgres:15-alpine`, prefix `it_*`, `DATABASE_URL=postgresql+asyncpg://it_admin:it_chatbot_2026@postgres:5432/it_student_chatbot` |
| Schema + seed | `init_db.sql` (mount `/docker-entrypoint-initdb.d/01_init_db.sql`) | **DONE.** 20 bảng, 23 môn, 25 cạnh tiên quyết, `v_course_prerequisite_closure`, `fn_student_eligible_courses(uuid)`, user mẫu, chatbot `Cố vấn Học tập Khoa CNTT` |
| GitNexus | `.gitnexus/` (gitignored) | **DONE.** repo `it_student_chatbot`, 294 files, 4154 nodes, 7682 edges, 303 flows |
| Auth DB | `airc_internal_chatbot_auth/app/core/database.py` | **CHƯA.** Motor `AsyncIOMotorClient`, `settings.mongodb_url` / `mongodb_db_name` |
| Core DB | `airc_internal_chatbot_core/app/core/database.py` | **CHƯA.** Motor singleton `mongodb`, `connect_to_mongo()` trong `app/main.py` lifespan và `app/jobs/ingest.py` |
| Chat path | `app/api/v1/chat.py` `ask_question` → `ChatService.ask_question` | Embed → semantic cache (key = question + `chatbot_id`) → retrieve Qdrant → rerank → `PromptService.build_prompt` → Gemini. `user_context` chỉ `{id, role}` |
| Prompt | `airc_internal_chatbot_core/app/services/prompt_service.py` | Persona "Chatbot RAG nội bộ của AIRC"; chỉ tin `[Knowledge]`; cấm kiến thức ngoài tài liệu |
| UI | `airc_internal_chatbot_ui` | Student redirect `/dashboard/chat` (`src/app/dashboard/page.tsx` dòng 62–69). Branding AIRC đỏ `#D32F2F`, `logo_airc.jpg`, `AIRCLogo` |
| K8s | `k8s-infrastructure/mongodb/` | Vẫn Mongo — **non-goal** trừ khi cần |

### Pain points (đồ án)

1. **Sai domain**: bot AIRC không biết tiên quyết, tín chỉ, PASSED/FAILED/IN_PROGRESS.
2. **LLM hay bịa mã môn**: prompt hiện tại không có `[AcademicFacts]` và không cấm bịa `course_code`.
3. **Cache xuyên user (P0)**: `SemanticCacheService` suffix chỉ `_bot_{chatbot_id}` (`chat_service.py` dòng 134–137, 512–519). Mọi câu có `[AcademicFacts]` trong đáp án (kể cả MATERIAL_QA) của SV_A có thể trả về SV_B.
4. **Stack không boot**: compose đã trỏ Postgres; Python vẫn `mongodb_url` bắt buộc (`core/app/core/config.py`).
5. **Schema RAG trong `init_db.sql` thiếu cột** so với model Mongo hiện tại (parent-child chunks, `conversation_summary`, branch session). PR1 phải vá delta này — không được giả sử 20 bảng đã đủ cho RAG.

### Dữ liệu học vụ đã seed (cite `init_db.sql`)

Tài khoản (mật khẩu `Pass123`, hash pbkdf2-sha256 — khớp `AuthService.pwd_context = CryptContext(schemes=["pbkdf2_sha256"])`):

| Email | Role | Tên | UUID |
|-------|------|-----|------|
| `admin@fit.edu.vn` | admin | Quản trị viên Khoa CNTT | `aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa` |
| `gv01@fit.edu.vn` | teacher | Nguyễn Văn An | `bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb` |
| `sv01@fit.edu.vn` | student | Lê Hải Đăng, `student_code=SV001` | `cccccccc-cccc-cccc-cccc-cccccccccccc` |

Bảng điểm SV001:

- **PASSED:** INT1101, INT1102, INT1103, INT1104, INT1201, INT1202, INT1204
- **FAILED:** INT1203 Kiến trúc máy tính (3.50, `2024-2`)
- **IN_PROGRESS:** INT2103, INT2104 (Lập trình Web), `semester_taken=2025-1`

`fn_student_eligible_courses('cccccccc-cccc-cccc-cccc-cccccccccccc')` đã verify:

- Được: INT1203 (học lại), INT2102 (PREVIOUS mềm INT1203), INT2202
- Chặn: INT2101 vì INT1203 chưa PASSED
- Loại: INT2103/INT2104 vì IN_PROGRESS

Môn HK1–HK6, `career_track ∈ {GENERAL, AI, WEB, SECURITY, DATA, NETWORK, SOFTWARE}`. Quan hệ: `PREREQUISITE` (cứng), `PREVIOUS` (mềm), `CO_REQUISITE`.

Chatbot mặc định: `eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee` — "Cố vấn Học tập Khoa CNTT". Dataset: `dddddddd-dddd-dddd-dddd-dddddddddddd`.

---

## Goals & Non-Goals

### Goals (P0 trừ khi ghi chú)

1. Auth + Core chạy trên Postgres (asyncpg + SQLAlchemy 2.0 asyncio). API `id` vẫn `string` (UUID). Stack `docker compose up` boot được.
2. Domain học vụ trên Core: Course / Prerequisite / StudentRecord / LearningMaterial + REST.
3. Hybrid `ask_question`: `IntentClassifier` → `COURSE_ADVICE` | `MATERIAL_QA` | `HYBRID`. Mỗi request inject `[AcademicFacts]` từ Postgres theo JWT `user_id`.
4. Persona "Trợ lý Cố vấn Học tập & Tài liệu Khoa CNTT". Cấm bịa mã môn / tín chỉ / tiên quyết.
5. Semantic cache: **mọi path inject `[AcademicFacts]` phải skip cache hoặc suffix có `user_id`** (COURSE_ADVICE / MATERIAL_QA / HYBRID). Invalidate khi ghi điểm.
6. Ingest: payload Qdrant + `learning_materials` gắn `course_id`, `material_type`.
7. UI sinh viên: chat cố vấn, môn đủ điều kiện, tài liệu theo môn, bảng điểm cá nhân. Admin/GV: CRUD môn, nhập điểm/CSV, bind upload vào môn.
8. Branding Khoa CNTT — **P2** so với học vụ P0.
9. 3–4 persona demo (cùng câu hỏi → đáp án khác).

### Non-Goals

- Đổi tên folder `airc_*` (optional sau).
- Connector SIS/LMS/SSO thật.
- Sinh viên tự khai báo điểm trong chat ("em đã qua OOP") — **cấm**; JWT → `student_records` là nguồn sự thật.
- K8s mongo→postgres, trừ khi demo production bắt buộc.
- Live Voice / Mermaid như yêu cầu luận văn (giữ code hiện có, không là acceptance).
- Parallelize migration Postgres với hybrid chat — **cấm**. Thứ tự 6 bước dưới đây là bắt buộc.
- Migrate dữ liệu Mongo production cũ sang Postgres (pivot local; volume Postgres đã seed; Mongo dump bỏ).

### Thứ tự triển khai đã chốt

1. Postgres Auth+Core để stack boot
2. Academic APIs + eligible-courses
3. Hybrid `ask_question` + persona + cache theo user
4. Ingest `course_id` metadata
5. Student UI + branding
6. Extra personas + PDF demo

---

## Proposed Design

### 1. Kiến trúc sau pivot (giữ 3 service)

```mermaid
flowchart LR
  subgraph UI["it_ui Next.js :3000"]
    Chat["/dashboard/chat"]
    Elig["/dashboard/eligible-courses"]
    Trans["/dashboard/transcript"]
    Mats["/dashboard/materials"]
    AdminC["/admin/courses + grades"]
  end

  subgraph Auth["it_auth FastAPI :8001"]
    JWT["JWT + RBAC"]
    Users["users / roles / permissions"]
  end

  subgraph Core["it_core FastAPI :8000"]
    Ask["POST /api/v1/chat/ask"]
    Intent["IntentClassifier"]
    Facts["AcademicFactsService"]
    RAG["ChatService retrieve+rerank"]
    Prompt["PromptService"]
    LLM["Gemini"]
  end

  subgraph Worker["it_worker RQ"]
    Ingest["process_dataset_file_job"]
  end

  PG[("it_postgres\nit_student_chatbot")]
  QD[("it_qdrant")]
  RD[("it_redis")]

  UI --> Auth
  UI --> Core
  Core -->|POST /api/auth/verify| Auth
  Ask --> Intent
  Intent --> Facts
  Intent --> RAG
  Facts --> PG
  RAG --> QD
  RAG --> PG
  Facts --> Prompt
  RAG --> Prompt
  Prompt --> LLM
  Ingest --> PG
  Ingest --> QD
  Auth --> PG
  Core --> RD
  Worker --> RD
```

**Quyết định hạ tầng:** Auth và Core **dùng chung một database Postgres** `it_student_chatbot` (đã thể hiện trong `init_db.sql` + cùng `DATABASE_URL` trên compose). Đây là thay đổi so với 2 Mongo DB tách (`airc_auth_db`, `airc_chatbot`). FK `datasets.owner_id → users(id)` chỉ hợp lệ khi share schema.

- Auth **chỉ** đọc/ghi: `users`, `roles`, `permissions`, `user_roles`, `role_permissions`, `password_reset_tokens`.
- Core đọc/ghi: RAG + học vụ; **đọc** `users` khi cần `student_code` / `full_name` cho facts (không ghi password).

Pool đề xuất: mỗi process `pool_size=5`, `max_overflow=10` (API 1 worker + worker RQ). Thesis load < 20 concurrent.

### 2. Hybrid retrieval (trái tim sản phẩm)

```
Câu hỏi + JWT user_id
  ├─ COURSE_ADVICE / tiên quyết / trượt / lộ trình → Rule engine PostgreSQL 100%
  ├─ MATERIAL_QA (môn học gì, slide, đề) → RAG Qdrant filtered by course_id
  └─ HYBRID → SQL facts + RAG docs → LLM diễn giải, cấm bịa mã môn/tín chỉ/tiên quyết
```

LLM **không nhớ** sinh viên. Mọi request phải inject `[AcademicFacts]` từ Postgres cho user đã xác thực.

Luồng `ask_question` mới:

```mermaid
sequenceDiagram
  participant UI
  participant ChatAPI as chat.py ask_question
  participant CS as ChatService
  participant IC as IntentClassifier
  participant AF as AcademicFactsService
  participant PG as Postgres
  participant Cache as SemanticCache
  participant QD as Qdrant
  participant PS as PromptService
  participant LLM as Gemini

  UI->>ChatAPI: POST /api/v1/chat/ask JWT
  ChatAPI->>CS: user_context {id, role}
  CS->>IC: classify(question, history)
  IC-->>CS: {intent, career_track, course_codes}
  CS->>AF: build(user_id, question, track, codes)
  AF->>PG: student_records + fn_student_eligible_courses + courses
  AF-->>CS: AcademicFacts
  Note over CS: embed ONLY if intent in {MATERIAL_QA, HYBRID}
  alt COURSE_ADVICE
    CS->>PS: facts only, knowledge empty
    Note over Cache: SKIP cache; SKIP embed/Qdrant
  else MATERIAL_QA
    opt cache key bot+user+course
      CS->>Cache: get(suffix=_bot_X_user_U_course_Y)
    end
    CS->>QD: search filter course_id
    CS->>PS: facts + knowledge
  else HYBRID
    CS->>QD: search filter course_id if detected
    CS->>PS: facts + knowledge
    Note over Cache: suffix MUST include user_id
  end
  PS->>LLM: prompt
  LLM-->>UI: SSE tokens + citations
```

### 3. IntentClassifier

File mới: `airc_internal_chatbot_core/app/services/intent_classifier.py`

Chiến lược: **rules trước**, LLM classify chỉ khi ambiguous **và** `not settings.chat_fast_path`.

```python
from enum import Enum
import re

class ChatIntent(str, Enum):
    COURSE_ADVICE = "COURSE_ADVICE"
    MATERIAL_QA = "MATERIAL_QA"
    HYBRID = "HYBRID"

COURSE_PATTERNS = [
    r"ti[eê]n quy[eê]t", r"học\s*lại", r"trượt", r"đăng\s*ký",
    r"lộ\s*trình", r"tín\s*chỉ", r"học\s*k[iỳ]", r"nên\s*học",
    r"được\s*học", r"đủ điều kiện", r"môn nào", r"học môn",
    r"định hướng", r"dev web", r"hướng\s*(web|ai|security|data|mạng)",
    r"career", r"chuyên ngành",
]
MATERIAL_PATTERNS = [
    r"slide", r"đề cương", r"giáo trình", r"đề thi", r"tài liệu",
    r"bài giảng", r"syllabus", r"nội dung môn", r"học gì trong",
    r"chapter", r"chương",
]
TRACK_HINTS = {
    "WEB": [r"\bweb\b", r"frontend", r"backend", r"dev web", r"full\s*stack"],
    "AI": [r"\bai\b", r"học máy", r"machine learning", r"deep learning", r"nlp"],
    "SECURITY": [r"an toàn", r"an ninh", r"security", r"pentest"],
    "DATA": [r"dữ liệu", r"database", r"sql", r"data"],
    "NETWORK": [r"mạng máy tính", r"mạng", r"cloud", r"kubernetes"],
    "SOFTWARE": [r"phần mềm", r"oop", r"công nghệ phần mềm"],
}

@dataclass
class ClassifiedIntent:
    intent: ChatIntent
    career_track: str | None          # WEB/AI/... từ TRACK_HINTS
    course_codes: list[str]           # regex INT\\d{4}

class IntentClassifier:
    def classify(self, question: str, history: list | None = None) -> ClassifiedIntent:
        q = question.lower()
        course = any(re.search(p, q, re.I) for p in COURSE_PATTERNS)
        material = any(re.search(p, q, re.I) for p in MATERIAL_PATTERNS)
        if course and material:
            intent = ChatIntent.HYBRID
        elif course:
            intent = ChatIntent.COURSE_ADVICE
        elif material:
            intent = ChatIntent.MATERIAL_QA
        else:
            intent = ChatIntent.HYBRID  # default an toàn: luôn có facts
        return ClassifiedIntent(
            intent=intent,
            career_track=self._detect_track(q),
            course_codes=re.findall(r"INT\\d{4}", question, flags=re.I),
        )

    def _detect_track(self, q: str) -> str | None:
        for track, patterns in TRACK_HINTS.items():
            if any(re.search(p, q, re.I) for p in patterns):
                return track
        return None
```

Default **HYBRID** khi không khớp pattern nào (không default MATERIAL_QA) vì câu "em nên học gì" phải có facts.

Câu demo *"E muốn theo đường dev web thì học kì này lên học những môn nào"* khớp `COURSE_PATTERNS` (`học kì`, `môn nào`, `dev web`) và **không** khớp `MATERIAL_PATTERNS` → **`COURSE_ADVICE` + `career_track=WEB`**. Không gọi Qdrant. INT2204 bị chặn vẫn nằm trong `[AcademicFacts].blocked_sample` nhờ track WEB. Golden test đúng chuỗi này cho SV001 (PR3) và 4 persona (PR6).

LLM classify **không** ghi đè intent khi rules đã khớp. Optional LLM (chỉ khi `not chat_fast_path` **và** `career_track is None` **và** `course_codes == []` **và** intent đã là default HYBRID) chỉ để gợi `course_codes` / `career_track` — không đổi `intent`.

### 4. AcademicFactsService — nguồn sự thật theo JWT

File mới: `airc_internal_chatbot_core/app/services/academic_facts_service.py`

**Không tin** câu sinh viên ("em đã qua OOP"). `user_id` lấy từ JWT (`chat.py` `_user_ctx` → `current_user.user_id`), trừ khi admin/teacher gửi `as_user_id` (xem §7). Query Postgres. Core **cấm** `SELECT hashed_password`:

```sql
SELECT id, student_code, full_name, role FROM users WHERE id = :user_id
```

```python
@dataclass
class AcademicFacts:
    student_id: str
    student_code: str | None
    full_name: str
    current_semester: str | None
    current_semester_source: str  # IN_PROGRESS | INFERRED_NEXT | UNKNOWN
    empty_transcript: bool
    records: list[dict]           # course_code, name, credits, status, grade, semester_taken, attempt_count
    eligible_courses: list[dict]  # fn_student_eligible_courses + credits + relation_type arrays
    blocked_sample: list[dict]    # môn track bị chặn: course_code, name, credits, missing_prereq_codes, relation_type
    career_track_filter: str | None
    mentioned_course_codes: list[str]
    in_progress: list[dict]
    retake: list[dict]            # FAILED
```

**Suy học kỳ hiện tại (chốt mặc định):**

1. Nếu có `student_records.status = IN_PROGRESS` → lấy `semester_taken` mới nhất theo thứ tự lexicographic `YYYY-N` (ví dụ `2025-1`). `source=IN_PROGRESS`.
2. Else nếu có PASSED/FAILED → parse `semester_taken` max, tăng học kỳ: `2024-2` → `2025-1`, `2025-1` → `2025-2`. `source=INFERRED_NEXT`.
3. Else `current_semester=None`, `source=UNKNOWN`. Prompt: "không suy đoán học kỳ".

Không thêm cột `users.current_semester` trong MVP.

**Empty transcript:** `empty_transcript=True` → bot trả lời cố định: bảng điểm chưa có, không bịa PASSED, không gọi eligible như thể đã học HK1.

**Track filter:** nếu `IntentClassifier` bắt được WEB/AI/... thì `courses` lấy thêm môn `career_track = hint OR GENERAL` và đánh dấu eligible/blocked.

Gọi SQL:

```sql
SELECT c.course_code, c.course_name, c.credits, sr.status, sr.grade,
       sr.semester_taken, sr.attempt_count
FROM student_records sr
JOIN courses c ON c.id = sr.course_id
WHERE sr.user_id = :user_id
ORDER BY semester_taken, course_code;

SELECT * FROM fn_student_eligible_courses(:user_id)
ORDER BY semester, course_code;
```

Với câu hỏi có mã môn (regex `INT\d{4}`), bổ sung closure:

```sql
SELECT prerequisite_code, relation_type, depth
FROM v_course_prerequisite_closure
WHERE course_code = :code
ORDER BY depth;
```

### 5. PromptService — persona mới

Sửa `PromptService.build_prompt` thêm kwarg `academic_facts: Optional[dict] = None`.

Khi `academic_facts` có mặt (mọi request student của chatbot cố vấn):

1. Default instruction đổi thành persona dưới đây (vẫn cho `chatbots.config.system_prompt` override **nhưng** runtime **luôn prepend** block cấm bịa — không tin system_prompt admin xóa rule).
2. Chèn `[AcademicFacts]` **trước** `[Knowledge]`.
3. Nếu `empty_transcript`: instruction "không suy ra môn đã học".
4. `COURSE_ADVICE`: `[Knowledge]` được phép trống; **không** reject no-context; `no_context_behavior` không được cắt flow trước LLM.
5. `MATERIAL_QA`/`HYBRID`: cite file như hiện tại (`Theo tài liệu [TÊN_FILE]`). Facts vẫn có để khỏi mâu thuẫn điểm.

Default instruction (thay block AIRC dòng 52–62):

```
Bạn là Trợ lý Cố vấn Học tập & Tài liệu Khoa CNTT.
QUY TẮC BẮT BUỘC:
1. Mã môn, số tín chỉ, tiên quyết, trạng thái PASSED/FAILED/IN_PROGRESS
   CHỈ được lấy từ [AcademicFacts]. CẤM bịa hoặc dùng kiến thức chung.
2. Nếu sinh viên nói đã qua một môn nhưng [AcademicFacts] không có PASSED
   → tin bảng điểm, giải thích nhẹ nhàng, không tranh cãi.
3. Tài liệu (slide/đề cương/giáo trình/đề) lấy từ [Knowledge] và PHẢI cite file.
4. [AcademicFacts].empty_transcript = true → nói bảng điểm chưa được nhập,
   không gợi ý như thể sinh viên đã hoàn thành HK bất kỳ.
5. current_semester_source = UNKNOWN → không đoán học kỳ.
6. Phân biệt PREREQUISITE (bắt buộc PASSED) và PREVIOUS (khuyến nghị).
7. Trả lời tiếng Việt, súc tích, liệt kê mã môn + tên + lý do.
```

Render facts dạng text cố định (không JSON thô) để LLM khó bỏ sót:

```
[AcademicFacts]
Sinh viên: Lê Hải Đăng (SV001)
Học kỳ hiện tại: 2025-1 (nguồn: IN_PROGRESS)
Đang học: INT2103 Phân tích và thiết kế hệ thống (3 TC); INT2104 Lập trình Web (3 TC)
Đã PASSED: INT1101 Nhập môn lập trình (3 TC); INT1102 Toán rời rạc (3 TC); INT1103 Đại số tuyến tính (3 TC); INT1104 Nhập môn CNTT (2 TC); INT1201 CTDL & GT (4 TC); INT1202 Cơ sở dữ liệu (3 TC); INT1204 OOP (3 TC)
FAILED cần học lại: INT1203 Kiến trúc máy tính (3 TC, 3.50, 2024-2)
Môn đủ điều kiện: INT1203 (3 TC, học lại); INT2102 Mạng máy tính (3 TC, PREVIOUS chưa đạt: INT1203); INT2202 Trí tuệ nhân tạo (3 TC)
Lọc định hướng: WEB
Môn WEB bị chặn: INT2204 Phát triển ứng dụng Web (3 TC, PREREQUISITE thiếu PASSED: INT2104)
Môn cứng bị chặn (ngoài WEB): INT2101 Hệ điều hành (3 TC, PREREQUISITE thiếu PASSED: INT1203)
```

### 6. Cache — chống lộ đáp án xuyên user (P0)

Hiện tại (`chat_service.py`):

```python
cache_key_suffix = f"_bot_{chatbot_id}" if chatbot_id else ""
```

**Quy tắc P0:** path nào đưa `[AcademicFacts]` vào prompt (cả ba intent, vì MATERIAL_QA cũng inject facts để khỏi mâu thuẫn điểm) thì **skip cache** hoặc suffix **phải** chứa `user_id`. `SemanticCacheService` lưu **chuỗi đáp án cuối**, không lưu prompt — cache MATERIAL_QA không có user sẽ leak bảng điểm SV001 cho SV_NEW.

Chốt:

| Intent | Hành vi cache |
|--------|----------------|
| `COURSE_ADVICE` | **SKIP** get/set. SQL rẻ; điểm đổi thường xuyên; không embed. |
| `HYBRID` | Key = `question_embed + suffix=_bot_{chatbot_id}_user_{user_id}`. |
| `MATERIAL_QA` | Key = `question_embed + suffix=_bot_{chatbot_id}_user_{user_id}_course_{course_id_or_none}`. **Bắt buộc `user_id`.** |

TTL: singleton hiện tại dùng `ttl_seconds` **cả instance** (`cache_service.py`); `set()` không nhận TTL từng entry. HYBRID/MATERIAL_QA muốn 15 phút vs 1 giờ thì **mỗi entry lưu `expires_at`** (so sánh lúc `get`) **hoặc** hai instance `SemanticCacheService(ttl_seconds=...)`. Không thêm arg TTL trên `get`/`set` rồi giả sử nó hoạt động. Test 2 JWT độc lập với TTL.

Khi Admin/GV ghi `student_records` (CRUD hoặc CSV): gọi `semantic_cache_service.clear()` (MVP in-memory singleton; đủ cho `--workers 1`). Ghi log `cache_invalidated_reason=grade_write`.

Compose đang `SEMANTIC_CACHE_ENABLED=false` — **vẫn phải sửa key** vì bật lại là P0 leak.

Defense in depth: facts **luôn** build trước cache get; COURSE_ADVICE không cache. Assert ERROR nếu cache hit mà suffix không chứa `user_` khi `academic_facts` đã inject.

### 7. Sửa `ChatService.ask_question`

File: `airc_internal_chatbot_core/app/services/chat_service.py`

Điểm móc (không viết lại RAG từ đầu). **Thứ tự bắt buộc** (skip embed trên COURSE_ADVICE — hôm nay dòng 128 là embed-then-cache):

0. Feature flag `academic_facts_enabled` (system_settings / env, default **false** đến PR3). Nếu false: giữ luồng RAG hiện tại, **bỏ qua** classifier/facts, **không** dùng advisor `system_prompt` (xem §8.11).
1. Sau validation: `classified = intent_classifier.classify(...)` → `intent`, `career_track`, `course_codes`.
2. Resolve subject: `facts_user_id = current_user.user_id`. Nếu role teacher/admin **và** request có `as_user_id` **và** `records:view:any` → `facts_user_id = as_user_id`. Student gửi `as_user_id` → **403**. Hội đồng demo chat **bằng account SV00x**; `as_user_id` chỉ để GV/admin thử.
3. `facts = await academic_facts_service.build(facts_user_id, classified)` — luôn inject cho cả ba intent.
4. **Embed / cache get chỉ khi** `intent in {MATERIAL_QA, HYBRID}`. COURSE_ADVICE: không `_try_embed_question`, không Qdrant, không cache.
5. Cache get/set: suffix luôn `_bot_{chatbot_id}_user_{facts_user_id}` (+ `_course_` nếu MATERIAL_QA).
6. `COURSE_ADVICE`: skip `_search_dataset` / rerank; `grouped_results=[]`; **không** early-return no-context (nhánh dòng 392–435 hiện reject khi 0 chunks).
7. `MATERIAL_QA`/`HYBRID`: `_search_dataset` thêm `course_id` filter khi `classified.course_codes` có đúng 1 mã; không thì retrieval dataset chatbot như cũ.
8. `prompt_service.build_prompt(..., academic_facts=facts.to_prompt_dict(), system_prompt=...)` + prepend cấm bịa.
9. Response thêm `debug.intent`, `debug.career_track`, `debug.current_semester`, `debug.empty_transcript`.

`ChatService.__init__` thêm deps: `academic_facts_service`, `intent_classifier` (hoặc import singleton). `get_chat_service` trong `app/api/dependencies.py` wire session Postgres.

Gợi ý fallback `GET /api/v1/chat/suggestions` đổi sang:

- "Học kì này em đủ điều kiện môn nào?"
- "Em trượt môn nào, cần học lại ra sao?"
- "Theo hướng Web thì môn tiếp theo là gì?"
- "Slide / đề cương môn INT2104 ở đâu?"

### 8. Mongo → Postgres (PR1) — chi tiết implement

#### 8.1 Settings

Auth `app/core/settings.py`: thay `mongodb_url` / `mongodb_db_name` bằng:

```python
database_url: str = "postgresql+asyncpg://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot"
app_name: str = "IT Faculty Auth Service"
```

Core `app/core/config.py`: tương tự; `app_name: str = "IT Faculty Advisor Core"`. **Xóa** field `mongodb_url` / `mongodb_db_name`. Nếu env còn `MONGODB_URL` / `MONGODB_DB_NAME` → **fail-fast** lúc import settings (raise `RuntimeError`), không dual-write.

Cập nhật **cả** `airc_internal_chatbot_auth/.env.example` và `airc_internal_chatbot_core/.env.example` (hiện `MONGODB_URL=mongodb://localhost:27017`). Local `uvicorn` đọc `.env`; compose inject `DATABASE_URL` — PR1 phải đổi `.env.example` kẻo `mongodb_url: str` required giữ Motor.

Compose đã set `DATABASE_URL` — pydantic-settings map `database_url`.

#### 8.2 Engine / session

Viết lại `app/core/database.py` (cả hai service), cùng pattern:

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.settings import settings  # hoặc config

engine = create_async_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def connect_to_db():
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

async def close_db():
    await engine.dispose()

async def get_session() -> AsyncSession:
    """Một AsyncSession / request FastAPI. Commit khi handler thành công; rollback khi exception.
    SQLAlchemy 2.0 `async with SessionLocal()` CHỈ đóng session — KHÔNG auto-commit.
    Mongo insert_one ghi ngay; session.add() sẽ biến mất nếu không commit.
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

Hợp đồng session (PR1, P0):

- **Một** `AsyncSession` per HTTP request, inject qua `Depends(get_session)`. Mọi repo (`get_dataset_repo`, `get_chat_service`, `UserRepository`, …) nhận **cùng** session đó — không `SessionLocal()` thêm, không engine thứ hai.
- **Cấm** `session.commit()` trong từng method repository (trừ worker, dưới đây). FastAPI dependency là ranh giới transaction.
- Worker ingest: mở **một** session cho cả job, `commit` sau `process_dataset_file` thành công, `rollback` trong `except`. Đây là job boundary duy nhất được `commit()` tay.
- Password reset / session messages / chatbot write đi qua cùng `get_session` → commit khi endpoint return 2xx.

Lifespan `main.py`: `connect_to_mongo` → `connect_to_db`. Health: `SELECT 1`.

Giữ alias tạm `connect_to_mongo = connect_to_db` **không** — rename dứt, grep sạch Motor.

#### 8.3 ORM vs dict API

Giữ **repository trả `dict` với `id: str`** để `ChatService` / JWT ít đổi. SQLAlchemy 2.0 mapped class nội bộ; `serialize_row` convert `UUID → str`, `Decimal → float`, `datetime.isoformat` khi cần.

```python
class BaseRepository:
    def __init__(self, session: AsyncSession, model: type):
        self.session = session
        self.model = model

    @staticmethod
    def parse_id(id_str: str) -> Optional[UUID]:
        try:
            return UUID(str(id_str))
        except (ValueError, TypeError):
            return None  # không còn ObjectId — chuỗi 24-hex Mongo là INVALID

    @staticmethod
    def serialize_row(row) -> Optional[dict]:
        ...
```

**P0:** mọi `to_object_id` / `{"_id": oid}` phải thành `id = UUID`. Seed chatbot `eeeeeeee-...` hiện **không** load được vì `ChatbotRepository.get_by_id` đòi ObjectId.

**Cấm `Base.metadata.create_all` và Alembic autogen.** Auth `models/orm.py` và Core `models/orm.py` map chồng `users` (và bảng RBAC) trên **một** Postgres. Schema sự thật = `init_db.sql` + `migrations/00x_*.sql` (CHECK, VIEW, `fn_student_eligible_courses`). ORM chỉ mapping đọc/ghi. Auth **cấm** INSERT bảng Core (`datasets`, `sessions`, `courses`, …).

#### 8.4 Chatbot.dataset_ids

Mongo nhúng `dataset_ids: [str]` trên document. Postgres: bảng `chatbot_datasets`.

`ChatbotRepository.get_by_id` **bắt buộc** JOIN và gán `doc["dataset_ids"] = [...]`. `ChatService` dòng 215 `if "dataset_ids" in chatbot` — thiếu field = bỏ context lock (lỗ hổng). Write path: xóa/insert `chatbot_datasets`, không `$set` array.

#### 8.5 Keyword search

`ChunkRepository.search_by_text` hiện tokenize, bỏ stopword, **AND-regex từng từ**, rồi OR-fallback nếu AND rỗng (`chunk_repository.py` 222–256). Port hành vi đó, **không** `ILIKE` cả câu hỏi:

```sql
-- AND-of-tokens (MVP, bound params, không pg_trgm)
SELECT * FROM chunks
WHERE dataset_file_id = ANY(:ids)
  AND text ILIKE :w1 AND text ILIKE :w2  -- ... mỗi keyword còn lại
LIMIT :limit
-- nếu 0 hàng: OR-fallback từng token len>=3 như Mongo
```

Keyword = split + strip punct + drop stopword giống `_KEYWORD_STOPWORDS`. `pg_trgm` để sau.

#### 8.6 Worker ingest

`app/jobs/ingest.py` hiện `connect_to_mongo()` + `mongodb.client[settings.mongodb_db_name]`. Đổi: mở `SessionLocal`, truyền session vào repos, `commit` sau `process_dataset_file`. `worker.py` không đụng Mongo.

#### 8.7 Password reset

`PasswordResetService` dùng `self.collection = db[COLLECTION]` + `ObjectId`. Viết lại INSERT/UPDATE `password_reset_tokens` (bảng đã có trong `init_db.sql`).

#### 8.8 Dependencies / requirements

Auth + Core `requirements.txt`:

- Thêm: `sqlalchemy[asyncio]>=2.0.36`, `asyncpg>=0.30.0`
- Xóa runtime: `motor`, `pymongo` (tests/migrate Mongo cũ có thể để script nhưng không import từ app)

#### 8.9 File mới / sửa — Auth

| File | Hành động |
|------|-----------|
| `airc_internal_chatbot_auth/app/core/database.py` | Viết lại engine Postgres |
| `airc_internal_chatbot_auth/app/core/settings.py` | `database_url` |
| `airc_internal_chatbot_auth/app/core/__init__.py` | export `connect_to_db` |
| `airc_internal_chatbot_auth/app/models/orm.py` | **TẠO** mapped `User`, `Role`, `Permission`, `UserRole`, `RolePermission`, `PasswordResetToken` |
| `airc_internal_chatbot_auth/app/models/user.py` | `UserCreate` thêm optional `student_code`; `UserResponse` thêm `student_code`, `department` |
| `airc_internal_chatbot_auth/app/repositories/base_repository.py` | Viết lại UUID |
| `airc_internal_chatbot_auth/app/repositories/user_repository.py` | `get_by_id` UUID; `create_user` nhận `student_code` |
| `airc_internal_chatbot_auth/app/repositories/rbac_repository.py` | 4 collection Motor → SQL |
| `airc_internal_chatbot_auth/app/services/auth_service.py` | **SỬA** — bỏ `bson.ObjectId`; dual-write role (xem dưới) |
| `airc_internal_chatbot_auth/app/services/password_reset_service.py` | Bỏ bson |
| `airc_internal_chatbot_auth/app/main.py` | lifespan Postgres |
| `airc_internal_chatbot_auth/app/api/dependencies.py` | `get_session` (commit/rollback) |
| `airc_internal_chatbot_auth/requirements.txt` | asyncpg/sqlalchemy |
| `airc_internal_chatbot_auth/.env.example` | `DATABASE_URL`; xóa `MONGODB_*` |

Giữ nguyên: `jwt_service.py` (`sub` = user_id string), **hash pbkdf2** trong `AuthService`, router `/api/auth/*`, `/api/auth/verify` trả `{id, email, full_name, role}` — **thêm `student_code`** optional. **Không** giữ nguyên thân `auth_service.py`: `login` → `_get_user_role` đang `from bson import ObjectId` + `db.user_roles.find_one({"user_id": ObjectId(user_id)})` (dòng 157–163). `register` ghi `users.role` nhưng **không** insert `user_roles`; `create_user_admin` thì có. Sau UUID, để nguyên file = login seed fail hoặc mọi user fallback `student`.

**Quy tắc dual identity (users.role + user_roles) — bắt buộc PR1:**

- Mọi INSERT/UPDATE `users.role` (register, admin create, RBAC assign, seed) **phải upsert** `user_roles` (join `roles.code`). SQL `init_db.sql` có cả hai.
- `login` / `_get_user_role` / `get_user_by_id`: JOIN `user_roles` → `roles.code`; nếu trống fallback `users.role`; nếu cả hai trống → `'student'` + log warning.
- JWT `role` claim = kết quả trên. Core **không** đọc SQL `permissions` lúc authorize — dùng `ROLE_PERMISSIONS` hardcoded sau `/api/auth/verify`.
- Cấm import `bson` trong Auth sau PR1.

#### 8.10 File mới / sửa — Core (migration)

| File | Hành động |
|------|-----------|
| `airc_internal_chatbot_core/app/core/database.py` | Viết lại |
| `airc_internal_chatbot_core/app/core/config.py` | `database_url` |
| `airc_internal_chatbot_core/app/models/orm.py` | **TẠO** mapped mọi bảng Core + academic |
| `airc_internal_chatbot_core/app/repositories/base_repository.py` | UUID |
| `airc_internal_chatbot_core/app/repositories/{dataset,file,dataset_file,chunk,session,chatbot,system_settings}_repository.py` | SQL; session extras; chatbot JOIN datasets |
| `airc_internal_chatbot_core/app/jobs/ingest.py` | Session Postgres |
| `airc_internal_chatbot_core/app/db/seed_standard_chatbot.py` | Trỏ seed SQL / no-op (đã seed `init_db.sql`) |
| `airc_internal_chatbot_core/app/main.py` | lifespan |
| `airc_internal_chatbot_core/app/api/dependencies.py` | `AsyncSession` **cùng** `get_session` cho mọi repo/service |
| `airc_internal_chatbot_core/app/repositories/session_repository.py` | Feedback → bảng `message_feedback`; `sources` cột; `latency_ms`/`cached`/`no_context` → `extra` |
| `airc_internal_chatbot_core/requirements.txt` | asyncpg/sqlalchemy |
| `airc_internal_chatbot_core/.env.example` | `DATABASE_URL`; xóa `MONGODB_*` |
| `migrations/002_align_rag_schema.sql` | **TẠO** — xem Data Model; gồm reset `system_prompt` RAG chặt |

`debug_db.py` / `migrate/seed_chatbot_dataset.py`: cập nhật hoặc đánh dấu deprecated.

#### 8.11 PR1 không bật advisor prompt (tránh bịa mã môn)

Seed `init_db.sql` chatbot `eeeeeeee-…` đã có `system_prompt` cố vấn + `no_context_behavior = fallback_llm`. `PromptService` **thay** default AIRC khi `system_prompt` set (dòng 47–49) và **chưa** prepend cấm bịa (PR3). Sau PR1, chat sẽ chạy persona cố vấn **không** `[AcademicFacts]` + fallback LLM → bịa INT**** — tệ hơn RAG chặt hiện tại.

PR1 `002` **bắt buộc**:

```sql
UPDATE chatbots
SET config = jsonb_set(
    jsonb_set(config, '{system_prompt}',
      '"Bạn là Chatbot RAG nội bộ. CHỈ trả lời dựa trên [Knowledge]. CẤM bịa mã môn, tín chỉ, tiên quyết."'::jsonb),
    '{no_context_behavior}', '"reject"'::jsonb
)
WHERE id = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee';

UPDATE system_settings
SET config = config || '{"academic_facts_enabled": false}'::jsonb
WHERE id = 'singleton';
```

`ChatService` (PR1): nếu `academic_facts_enabled` false → không classify, không facts, không advisor copy. PR3 lật flag + restore persona seed + prepend rules.

### 9. Domain học vụ (PR2)

File **mới** Core:

```
airc_internal_chatbot_core/app/repositories/course_repository.py
airc_internal_chatbot_core/app/repositories/prerequisite_repository.py
airc_internal_chatbot_core/app/repositories/student_record_repository.py
airc_internal_chatbot_core/app/repositories/learning_material_repository.py
airc_internal_chatbot_core/app/services/course_service.py
airc_internal_chatbot_core/app/services/prerequisite_service.py
airc_internal_chatbot_core/app/services/student_record_service.py
airc_internal_chatbot_core/app/services/learning_material_service.py
airc_internal_chatbot_core/app/api/v1/courses.py
airc_internal_chatbot_core/app/api/v1/academic.py
airc_internal_chatbot_core/app/models/academic_schemas.py
```

`PrerequisiteService`: wrap `v_course_prerequisite_closure` + giải thích "vì sao chưa học được X".

`StudentRecordService.upsert`: unique `(user_id, course_id)`; tăng `attempt_count` khi FAILED → đăng ký lại; **cấm** student role gọi write.

CSV import (Admin/Teacher): cột `student_code,course_code,status,grade,semester_taken`. Map `student_code → users.id`. Transaction từng batch 100 dòng; dòng lỗi trả `row, reason` không abort cả file trừ khi `?strict=true`.

### 10. Ingest metadata (PR4)

Hiện payload Qdrant (`processing_service.py` dòng 227–238):

```python
{"chunk_id", "dataset_file_id", "dataset_id", "is_child", "parent_chunk_id",
 "chunk_role", "domain", "language", "is_table"}
```

Thêm: `course_id`, `course_code`, `material_type`.

Nguồn metadata:

1. Upload teacher/admin gửi `course_id` + `material_type` (form field).
2. Lookup `learning_materials` theo `file_id` sau khi bind.
3. Parse mã môn từ tên file (`INT2104_slides.pdf`) — fallback, log warning.

`VectorService.search` thêm filter optional:

```python
rest.FieldCondition(key="course_id", match=rest.MatchValue(value=course_id))
```

Cần `create_payload_index` cho `course_id` (keyword) khi ensure collection.

`learning_materials.file_id` / `dataset_id` (cột mới) liên kết file RAG với môn.

Re-ingest tài liệu cũ: job admin "reindex dataset" — ngoài MVP nếu chưa có file thật; PR6 mới có PDF.

### 11. UI sinh viên + Admin (PR5)

Giữ Next.js 15, Ant Design, Zustand, `coreClient` / `authClient`.

**Student** (`role === 'student'` vẫn redirect `/dashboard/chat` từ `src/app/dashboard/page.tsx` — giữ):

| Route mới | Mục đích |
|-----------|----------|
| `/dashboard/chat` | Copy cố vấn; gợi ý câu học vụ; citations |
| `/dashboard/eligible-courses` | GET eligible; badge PREVIOUS mềm |
| `/dashboard/transcript` | Bảng điểm; empty state "chưa có bảng điểm" |
| `/dashboard/materials` | Filter theo môn + `material_type` |

Sửa `StudentNav.tsx`: thêm tab Chat / Môn đủ ĐK / Bảng điểm / Tài liệu; đổi text `AIRC` → `Khoa CNTT`.

**Admin / Teacher:**

| Route | Role | Mục đích |
|-------|------|----------|
| `/admin/courses` | admin | CRUD `courses` + cạnh `course_prerequisites` |
| `/admin/grades` | admin, teacher | Nhập điểm 1 SV + CSV |
| Dataset upload | teacher+ | Form bind `course_id` + `material_type` |

`Sidebar.tsx` `getMenuItems`: admin thêm "Môn học", "Bảng điểm"; teacher thêm "Nhập điểm".

**Branding P2** (cùng PR5 sau academic pages):

| Hiện tại | Đích |
|----------|------|
| `themeConfig.ts` `colorPrimary: '#D32F2F'` | Navy `#0F4C81` + teal `#0D9488` (đề xuất; xem Open Questions) |
| `AIRCLogo.tsx`, `logo_airc.jpg` | `FitLogo.tsx` + `public/logo_fit.png` (placeholder nếu chưa có file khoa) |
| `layout.tsx` title `AIRC Internal Chatbot` | `Cố vấn Học tập Khoa CNTT` |
| Login title dòng 85 | cùng copy |
| Chat empty state `ChatMessages.tsx`, `StudentChat.tsx` | persona cố vấn |

Không xóa `logo_airc.jpg` cho đến khi có asset thay.

Frontend services mới:

```
airc_internal_chatbot_ui/src/services/academicService.ts
airc_internal_chatbot_ui/src/services/courseService.ts
```

### 12. Persona demo (PR6)

Cùng câu: *"E muốn theo đường dev web thì học kì này lên học những môn nào"*

| Persona | Email / code | UUID (cố định) | Tình trạng | Kỳ vọng bot |
|---------|--------------|----------------|------------|-------------|
| SV001 (seed) | `sv01@fit.edu.vn` / SV001 | `cccccccc-...cccc` | Trượt INT1203; IN_PROGRESS INT2103+INT2104 | Giữ INT2104; **không** INT2204; học lại INT1203; INT2101 bị chặn |
| SV_WEB | `svweb@fit.edu.vn` / SVWEB | `11111111-1111-1111-1111-111111111111` | PASSED INT2104 + INT1202 + nền tảng | Eligible INT2204 (và môn WEB tiếp) |
| SV_AI | `svai@fit.edu.vn` / SVAI | `22222222-2222-2222-2222-222222222222` | PASSED INT1201+INT2202 (+ INT1103) | INT3101; **không** đẩy lộ trình Web |
| SV_NEW | `svnew@fit.edu.vn` / SVNEW | `33333333-3333-3333-3333-333333333333` | Chỉ PASSED HK1 | Eligible kiểu HK2 (INT1201, INT1204, …); chưa Web |

Seed: `migrations/003_seed_demo_personas.sql` (mật khẩu cùng `Pass123`). PDF demo: 1 syllabus + 1 slide cho INT2104, INT1203, INT2202, INT1101 — ingest dataset `dddddddd-...` bind `course_id`.

### 13. Worked example — câu Web track, SV001

Câu: **"E muốn theo đường dev web thì học kì này lên học những môn nào"**

```mermaid
sequenceDiagram
  autonumber
  participant SV as SV001 JWT
  participant API as POST /api/v1/chat/ask
  participant IC as IntentClassifier
  participant AF as AcademicFactsService
  participant PG as fn_student_eligible_courses
  participant RAG as Qdrant optional
  participant LLM as Gemini

  SV->>API: Bearer sub=cccccccc-...cccc
  API->>IC: classify
  IC-->>API: HYBRID (môn nào + hướng web)
  API->>AF: user_id=cccccccc-... track=WEB
  AF->>PG: records + eligible + WEB courses
  PG-->>AF: eligible INT1203, INT2102, INT2202
  Note over AF: IN_PROGRESS 2025-1: INT2103, INT2104<br/>FAILED INT1203<br/>INT2204 blocked (INT2104 not PASSED)<br/>INT2101 blocked (INT1203 not PASSED)
  API->>RAG: optional materials career_track=WEB
  API->>LLM: [AcademicFacts] + [Knowledge] + [Question]
  LLM-->>SV: (1) tiếp tục INT2104, INT2103<br/>(2) học lại INT1203<br/>(3) chưa đăng ký INT2204<br/>(4) INT2102 khuyến nghị mềm<br/>(5) không bịa tín chỉ
```

Đáp án tối thiểu (acceptance):

1. Học kỳ hiện tại **2025-1**, đang học INT2104 Lập trình Web và INT2103 — **giữ**, không bảo bỏ.
2. INT2204 Phát triển ứng dụng Web **chưa** đăng ký được vì PREREQUISITE INT2104 chưa PASSED.
3. Phải **học lại INT1203** (FAILED 3.50).
4. INT2101 Hệ điều hành bị chặn (cứng INT1203) — nêu nếu giải thích nền tảng, không nhầm là môn Web.
5. Eligible: INT1203, INT2102 (PREVIOUS mềm INT1203), INT2202 (AI — không phải Web; có thể nêu "không thuộc hướng Web").
6. Mọi mã môn xuất hiện trong câu trả lời phải có trong `[AcademicFacts]`.

Cùng câu, SV_WEB: được INT2204. SV_AI: INT3101, không INT2204 nếu chưa INT2104. SV_NEW: môn HK2, không INT2104.

### 14. Latency / tải (định lượng)

| Đường | Mục tiêu p95 (local CPU) | Ghi chú |
|-------|--------------------------|---------|
| `COURSE_ADVICE` | ≤ 800ms + LLM | 2 query SQL; skip embed/Qdrant nếu không cache |
| `MATERIAL_QA` | ≈ RAG hiện tại 2–5s | thêm 1 filter Qdrant |
| `HYBRID` | ≤ 6s | SQL song song embed/retrieve |
| Eligible API | ≤ 100ms | function SQL đã verify |

Tải đồ án: < 20 user, 1 replica. Semantic cache in-memory đủ.

---

## API / Interface Changes

Base Core: `http://localhost:8000/api/v1`. Auth không đổi prefix `/api/auth`.

### Giữ nguyên

- `POST /api/v1/chat/ask`, `POST /api/v1/chat/ask/stream` (SSE)
- `POST /api/v1/chat/feedback`
- Datasets / files / sessions / chatbots / stats / voice / settings
- `POST /api/auth/login|register|verify|forgot-password|reset-password`
- JWT claims: `sub`, `email`, `role` (`jwt_service.py`)

`ChatResponse` thêm field optional (không breaking):

```python
class ChatResponse(BaseModel):
    # existing...
    intent: Optional[str] = None
    empty_transcript: bool = False
```

### API mới — Courses

```
GET    /api/v1/courses                  # student+: list, filter semester, career_track, q
GET    /api/v1/courses/{id}             # UUID hoặc ?code=INT2104
GET    /api/v1/courses/{id}/prerequisites   # hard + soft + closure
POST   /api/v1/courses                  # admin
PATCH  /api/v1/courses/{id}             # admin
DELETE /api/v1/courses/{id}             # admin, 409 nếu student_records tham chiếu
POST   /api/v1/courses/{id}/prerequisites   # admin {prerequisite_course_id, relation_type}
DELETE /api/v1/courses/{id}/prerequisites/{prereq_id}
```

### API mới — Academic (sinh viên: own; admin/gv: any)

```
GET  /api/v1/academic/me/transcript
GET  /api/v1/academic/me/eligible-courses
GET  /api/v1/academic/me/facts          # debug/admin: payload AcademicFacts

GET  /api/v1/academic/students/{user_id}/transcript     # records:view:any
GET  /api/v1/academic/students/{user_id}/eligible-courses

PUT  /api/v1/academic/records           # upsert 1 dòng
POST /api/v1/academic/records/import    # multipart CSV
DELETE /api/v1/academic/records/{id}
```

`PUT /records` body:

```json
{
  "user_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
  "course_code": "INT1203",
  "status": "FAILED",
  "grade": 3.5,
  "semester_taken": "2024-2",
  "attempt_count": 1
}
```

Student gọi write → **403**. Student gọi transcript user khác → **403**.

### API mới — Materials

```
GET  /api/v1/academic/materials?course_id=&material_type=
POST /api/v1/academic/materials          # bind file_id đã upload + course_id + type
PATCH /api/v1/academic/materials/{id}
```

Upload file vẫn `POST /api/v1/files` + add to dataset; bước bind tạo `learning_materials`.

### Permissions mới (migration SQL + enum Python)

Đồng bộ 3 nơi: `init_db`/`003` SQL, `auth/app/models/user.py` `Permission` + `ROLE_PERMISSIONS`, `core/app/models/auth.py`.

| code | student | teacher | admin |
|------|---------|---------|-------|
| `courses:view` | ✓ | ✓ | ✓ |
| `courses:manage` | | | ✓ |
| `records:view:own` | ✓ | | ✓ |
| `records:view:any` | | ✓ | ✓ |
| `records:update` | | ✓ | ✓ |
| `materials:view` | ✓ | ✓ | ✓ |
| `materials:manage` | | ✓ | ✓ |

Teacher **không** `courses:manage` (tránh sửa chương trình); chỉ nhập điểm + tài liệu.

---

## Data Model Changes

Nguồn sự thật schema: `init_db.sql`. **Không recreate** volume nếu đã có 20 bảng — dùng file SQL additive.

### Đã có (không thiết kế lại)

`users` (kèm `student_code`, `department`), RBAC, `courses`, `course_prerequisites`, `student_records` (UNIQUE user+course), `learning_materials`, `datasets`, `files`, `dataset_files`, `chunks` (tối thiểu), `chatbots`, `chatbot_datasets`, `sessions`, `messages` (`sources JSONB`), `message_feedback`, `system_settings`, view + function eligible.

### Delta bắt buộc PR1 — `migrations/002_align_rag_schema.sql`

`init_db.sql` **thiếu** field Mongo mà RAG đang dùng. Nếu không vá, parent-child, nén history, branch chat sẽ gãy.

```sql
-- sessions: ChatService đọc conversation_summary; UI branch chat
ALTER TABLE sessions
    ADD COLUMN IF NOT EXISTS parent_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS branch_message_index INTEGER,
    ADD COLUMN IF NOT EXISTS conversation_summary TEXT,
    ADD COLUMN IF NOT EXISTS chatbot_id UUID REFERENCES chatbots(id) ON DELETE SET NULL;
-- chatbot_id đã có trong CREATE gốc — IF NOT EXISTS an toàn khi chạy lại

-- messages: extra latency/cached/no_context
ALTER TABLE messages
    ADD COLUMN IF NOT EXISTS extra JSONB NOT NULL DEFAULT '{}'::JSONB;

-- chunks: parent-child + profiler (processing_service / chunk_repository)
ALTER TABLE chunks
    ADD COLUMN IF NOT EXISTS embedding_text TEXT,
    ADD COLUMN IF NOT EXISTS context_enriched_text TEXT,
    ADD COLUMN IF NOT EXISTS heading_path TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    ADD COLUMN IF NOT EXISTS is_parent BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS parent_chunk_id UUID REFERENCES chunks(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS domain VARCHAR(50),
    ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'vi',
    ADD COLUMN IF NOT EXISTS section_type VARCHAR(50),
    ADD COLUMN IF NOT EXISTS chunk_role VARCHAR(50) DEFAULT 'standalone',
    ADD COLUMN IF NOT EXISTS is_table BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS table_caption TEXT,
    ADD COLUMN IF NOT EXISTS table_header TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    ADD COLUMN IF NOT EXISTS quality_flags TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    ADD COLUMN IF NOT EXISTS page INTEGER,
    ADD COLUMN IF NOT EXISTS extra JSONB NOT NULL DEFAULT '{}'::JSONB;

CREATE INDEX IF NOT EXISTS ix_chunks_parent ON chunks (parent_chunk_id);
CREATE INDEX IF NOT EXISTS ix_chunks_file ON chunks (dataset_file_id);

-- bind tài liệu ↔ file ingest
ALTER TABLE learning_materials
    ADD COLUMN IF NOT EXISTS file_id UUID REFERENCES files(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS dataset_id UUID REFERENCES datasets(id) ON DELETE SET NULL;

-- permissions học vụ (INSERT … ON CONFLICT DO NOTHING)
```

Áp dụng: script `migrations/apply.py` (asyncpg) chạy lúc Core startup nếu `APPLY_SQL_MIGRATIONS=true`, **hoặc** document "psql -f" trong README. Thesis: volume local có thể `docker compose down -v` rồi để `init_db.sql` + concat delta vào cuối file. **Ưu tiên:** gộp delta vào `init_db.sql` **và** giữ file `002` cho volume đã tạo. Không dùng Alembic trong MVP.

### Mapping Mongo collection → Postgres

| Mongo (cũ) | Postgres | Ghi chú serialize |
|------------|----------|-------------------|
| `users._id` ObjectId | `users.id` UUID | `id` API = `str(uuid)` |
| `chatbots.dataset_ids[]` | `chatbot_datasets` | hydrate array khi đọc |
| `sessions` + `messages` | cùng tên | `user_id` UUID FK |
| `chunks.parent_chunk_id` | cột mới | `get_parent_chunks_by_ids` |
| `password_reset_tokens` | cùng tên | `token_hash` VARCHAR(64) |

Không migrate document Mongo. Cutover sạch.

### Chiến lược dữ liệu sinh viên (đã chốt)

- Đồ án dùng **sample**: seed + Admin/Teacher CRUD/CSV.
- Schema SIS-shaped: connector tương lai chỉ fill `users` + `student_records`.
- Không tin chat. Không SIS/SSO.

---

## Alternatives Considered

### A. Giữ Mongo, thêm Postgres chỉ cho học vụ

- **Ưu:** ít đụng `BaseRepository`, ingest.
- **Nhược:** 2 source of truth, 2 ID types (ObjectId + UUID), compose đã bỏ Mongo, FK `owner_id` không enforce, vận hành đồ án phức tạp.
- **Loại.** Postgres-only.

### B. Pure RAG (nhồi đề cương + bảng điểm vào Qdrant)

- **Ưu:** ít code chat.
- **Nhược:** LLM bịa INT2204; không recursive CTE; cache xuyên user; điểm đổi phải re-embed.
- **Loại.** Hybrid: SQL 100% cho rule, RAG cho tài liệu.

### C. Agent tool-calling (LLM tự gọi SQL)

- **Ưu:** linh hoạt.
- **Nhược:** latency, tool hallucination, khó chấm luận văn, Gemini tool không ổn định trên stack hiện tại.
- **Loại cho MVP.** Classifier rules + luôn inject facts. Tool-calling = tương lai.

### D. Dual-write Mongo+Postgres / feature flag driver

- **Ưu:** rollback dễ.
- **Nhược:** không có data Mongo local cần giữ; flag làm PR1 phình.
- **Loại.** Hard cutover.

---

## Security & Privacy Considerations

| Threat | Severity | Mitigation |
|--------|----------|------------|
| Cache trả lời SV_B cho SV_A | **P0** | Skip cache COURSE_ADVICE; HYBRID suffix `user_id`; invalidate khi ghi điểm |
| LLM bịa mã môn / tín chỉ | **P0** | `[AcademicFacts]` bắt buộc; prompt cấm; test regression danh sách mã |
| Sinh viên claim "đã qua OOP" | P0 product | Bỏ qua utterance; chỉ `student_records` |
| Student đọc/ghi điểm người khác | P0 | JWT `sub` vs path `user_id`; 403; không trust body `user_id` của student |
| ObjectId parser nuốt UUID seed | **P0** | Bỏ bson; UUID parse fail → 404 |
| Context lock dataset | P1 (đã có) | Giữ override `dataset_ids` từ chatbot |
| CSV import leo quyền | P1 | Teacher/Admin only; không tạo user mới qua CSV (trừ admin flag) |
| Prompt injection "bỏ AcademicFacts" | P1 | Runtime prepend rule; facts ở block riêng |
| SSE leak token | P2 | Giữ auth `CHAT_USE`; không log nội dung câu hỏi full (đã có preview 50 ký tự) |

Authn: Core vẫn `POST {AUTH}/api/auth/verify` (`dependencies.py` `verify_token_with_auth_service`). Không nhúng secret JWT decode ở Core (tránh lệch). `user_id` facts = `current_user.user_id` đã verify.

Dữ liệu điểm là PII học vụ (mẫu): không log grade trong INFO; log `user_id` + `course_code` + status đủ debug.

---

## Observability

Log logger hiện có (`[CHAT]`, `[CACHE]`, `[VECTOR]`, `[PROCESS]`):

- `[CHAT] intent=HYBRID user=… empty_transcript=false semester=2025-1 track=WEB`
- `[FACTS] eligible=3 blocked_web=1 elapsed_ms=`
- `[CACHE] SKIP intent=COURSE_ADVICE` / `HIT suffix=_bot_e_user_c`
- `[GRADES] upsert user=… course=INT1203 status=PASSED cache_cleared=true`

`debug` JSON trong `ChatResponse` (UI `RAGDebugPanel.tsx` đã có): thêm `intent`, `facts_ms`, `empty_transcript`, `cache_suffix`.

Metrics (log-count đủ đồ án; không bắt Prometheus):

- `chat_intent_total{intent}`
- `academic_empty_transcript_total`
- `cache_cross_user_blocked` (nếu suffix thiếu user trên HYBRID — assert error)

Alert dev: ERROR nếu HYBRID cache hit mà suffix không chứa `user_`.

---

## Rollout Plan

Local thesis, không feature flag phức tạp.

1. **PR1 merge** → `docker compose up --build`: `it_auth` `/health`, login `sv01@fit.edu.vn` / `Pass123`, Core `/health`, chat RAG cũ vẫn trả lời (chưa facts).
2. **PR2** → curl eligible SV001 khớp INT1203/INT2102/INT2202.
3. **PR3** → 4 persona (khi có) / ít nhất SV001 worked example; cache test 2 user.
4. **PR4** → filter slide theo môn.
5. **PR5** → UI student + admin grades.
6. **PR6** → PDF + 4 account demo hội đồng.

Rollback PR1: checkout image cũ **không** chạy vì compose không còn Mongo. Rollback = revert PR + không down `-v` (data Postgres giữ). Không dual-run.

K8s: non-goal. Nếu buộc: thay `k8s-infrastructure/mongodb` bằng StatefulSet Postgres, đổi ConfigMap `DATABASE_URL` — ticket riêng.

CHANGELOG.md: **append-only**. Mỗi PR thêm mục `### Thay đổi` tiếng Việt, không sửa lịch sử AIRC.

---

## Risks

| Risk | Sev | Mitigation |
|------|-----|------------|
| Cache cross-user leak | **P0** | Skip COURSE_ADVICE; HYBRID key + user_id; test 2 JWT cùng câu |
| LLM hallucinate course codes | **P0** | Facts block + forbid; pytest so khớp mã với facts; temperature chatbot seed 0.3 |
| Empty transcript bịa điểm | **P1** | Flag + câu trả lời cố định |
| ObjectId vs UUID | **P0** | `parse_id` UUID only; integration test seed chatbot `eeeeeeee-…` |
| `init_db.sql` thiếu cột RAG | **P0** | `002_align_rag_schema.sql` trong PR1; parent-child test |
| `dataset_ids` không hydrate | **P0** | JOIN bắt buộc; test context lock |
| Keyword search ILIKE chậm | P2 | Dataset đồ án nhỏ; pg_trgm sau |
| Grade UNIQUE 1 dòng / môn | P2 | `attempt_count` + overwrite status; không lưu lịch sử lần thi (đủ luận văn) |
| Ingest chưa có `course_id` → MATERIAL_QA loãng | P2 | PR4; trước đó HYBRID vẫn đúng facts |
| Shared DB lock giữa Auth & Core | P3 | Pool nhỏ; không transaction dài trên Auth |

---

## Open Questions

Chỉ việc **chưa** chốt. Sample data, no SIS, hybrid, Postgres, personas, cấm self-report điểm, thứ tự 6 bước — **đã chốt**, không lặp.

1. **Màu brand Khoa CNTT:** đề xuất navy `#0F4C81` + teal `#0D9488` (tránh đỏ AIRC). Cần logo khoa thật hay placeholder chữ "CNTT"?
2. **Phạm vi nhập điểm của teacher:** đề xuất teacher sửa **mọi** `student_records` (đồ án 1 GV). Thu hẹp theo môn giảng dạy = bảng `course_instructors` — ngoài MVP.
3. **Keyword search:** ILIKE MVP. Có cần `pg_trgm` trước demo hội đồng không? (Khuyến nghị: không.)

Học kỳ hiện tại: **đã chốt mặc định** infer IN_PROGRESS else max passed+1 — không mở lại trừ khi product owner muốn cột profile.

---

## Key Decisions

| Quyết định | Lý do |
|------------|--------|
| **Postgres không Mongo** | Rule tiên quyết cần JOIN/CTE/CHECK; compose + `init_db.sql` đã Postgres; 2 DB ID-type là nợ. |
| **Một schema chia sẻ Auth+Core** | FK `owner_id`/`user_id` → `users`; `init_db.sql` đã gộp. Auth không ghi bảng Core. |
| **Sample data, không SIS** | Phạm vi luận văn; schema SIS-shaped để nối sau. |
| **Hybrid, không pure RAG, không tool-calling** | Mã môn/tín chỉ/tiên quyết phải 100% SQL; RAG chỉ tài liệu; tool-calling thêm latency/hallucination. |
| **JWT `sub` = identity học vụ** | `user_context.id` đã có trên `chat.py`; không tin body hay utterance. |
| **Cấm sinh viên tự khai điểm** | Tránh prompt injection bảng điểm; Admin/GV/CSV là write path duy nhất. |
| **Cache COURSE_ADVICE skip; HYBRID + user_id** | Cùng câu khác người; leak P0. MATERIAL_QA không dính điểm. |
| **PREREQUISITE cứng / PREVIOUS mềm** | `fn_student_eligible_courses` đã implement; prompt phải giải thích đúng. |
| **Cấm LLM bịa mã môn** | Acceptance luận văn; facts block + test. |
| **Default intent HYBRID** | An toàn hơn MATERIAL_QA khi classifier miss. |
| **Học kỳ = infer IN_PROGRESS else next** | Không thêm cột user; model cấm đoán khi UNKNOWN. |
| **Không song song PR1 với hybrid chat** | Python còn Motor thì academic API/chat không chạy. |
| **Không rename `airc_*` folders** | Giảm diff; branding UI đủ. |
| **Hard cutover, không dual-write** | Không có Mongo local cần giữ. |
| **API `id` luôn string UUID** | UI/Zustand không đổi kiểu. |
| **Gộp delta RAG vào PR1** | `chunks`/`sessions` SQL hiện thiếu field production. |
| **4 persona demo** | Cùng câu khác đáp án — tiêu chí hội đồng. |
| **Branding P2** | Học vụ P0; theme đổi sau khi chat đúng. |
| **CHANGELOG append-only** | Quy ước repo. |

---

## References

- `init_db.sql` — schema + seed + `fn_student_eligible_courses`
- `docker-compose.yml`, `docker-compose.local.yml` — prefix `it_*`, Postgres DONE
- `airc_internal_chatbot_core/app/services/chat_service.py` — `ask_question`
- `airc_internal_chatbot_core/app/services/prompt_service.py` — persona AIRC
- `airc_internal_chatbot_core/app/api/v1/chat.py` — `_user_ctx` `{id, role}`
- `airc_internal_chatbot_core/app/services/cache_service.py` — suffix chatbot only
- `airc_internal_chatbot_core/app/services/processing_service.py` — Qdrant payload
- `airc_internal_chatbot_core/app/services/vector_service.py` — filter `dataset_file_id`
- `airc_internal_chatbot_core/app/jobs/ingest.py`, `worker.py`
- `airc_internal_chatbot_auth/app/core/database.py`, `.../repositories/base_repository.py`
- `airc_internal_chatbot_auth/app/services/jwt_service.py`, `auth_service.py` (pbkdf2)
- `airc_internal_chatbot_ui/src/app/dashboard/page.tsx` — student → `/dashboard/chat`
- `airc_internal_chatbot_ui/src/components/Layout/Sidebar.tsx`
- `airc_internal_chatbot_ui/src/theme/themeConfig.ts`, `components/Common/AIRCLogo.tsx`
- `CHANGELOG.md` — append-only
- `document/core/README.md` — API cũ (Mongo) — cập nhật sau PR1
- GitNexus index `it_student_chatbot`

---

## PR Plan

Mỗi PR độc lập review/merge được theo thứ tự 6 bước. **Không** gộp PR1 với hybrid. Docker Compose Postgres **không** thuộc PR1 (DONE).

### PR1 — Auth+Core Mongo → Postgres (stack boot)

- **Title:** `feat(db): migrate Auth and Core from Motor/MongoDB to Postgres UUID`
- **Depends:** không (infra Docker đã xong)
- **Files / components:**
  - Auth: `app/core/database.py`, `settings.py`, `models/orm.py` (new), `repositories/*`, `services/password_reset_service.py`, `main.py`, `api/dependencies.py`, `requirements.txt`
  - Core: cùng nhóm `database.py`, `config.py`, `models/orm.py` (new), mọi `app/repositories/*`, `jobs/ingest.py`, `main.py`, `api/dependencies.py`, `requirements.txt`, `db/seed_standard_chatbot.py`
  - `migrations/002_align_rag_schema.sql` (+ gộp delta vào `init_db.sql`)
  - Tests: login seed `sv01@fit.edu.vn`, `GET` chatbot `eeeeeeee-…`, session create/list, ingest 1 file nhỏ (nếu fixture có)
- **Mô tả:** SQLAlchemy 2.0 + asyncpg; repository dict + `id: str`; hydrate `dataset_ids`; bỏ `bson`/`to_object_id`; worker dùng session Postgres. **Chưa** hybrid, **chưa** AcademicFacts. Chat RAG cũ phải chạy trên UUID.

### PR2 — Academic APIs + eligible-courses

- **Title:** `feat(academic): courses, records, eligible-courses APIs`
- **Depends:** PR1
- **Files:** `app/repositories/course_repository.py`, `prerequisite_repository.py`, `student_record_repository.py`, `learning_material_repository.py` (list/bind stub), `app/services/course_service.py`, `prerequisite_service.py`, `student_record_service.py`, `app/api/v1/courses.py`, `academic.py`, `models/academic_schemas.py`, `app/main.py` include router, `models/auth.py` + Auth `user.py` permissions, SQL insert permissions, tests eligible SV001 = `{INT1203, INT2102, INT2202}`
- **Mô tả:** CRUD môn (admin), transcript/eligible (own vs any), upsert điểm + CSV, 403 student write. Chưa đổi `ask_question`.

### PR3 — Hybrid ask_question + persona + cache per-user

- **Title:** `feat(chat): hybrid academic advisor with facts injection and per-user cache`
- **Depends:** PR2
- **Files:** `intent_classifier.py`, `academic_facts_service.py`, `chat_service.py`, `prompt_service.py`, `cache_service.py` (optional TTL arg), `api/v1/chat.py` (suggestions + response fields), `api/dependencies.py`, tests: SV001 web-track worked example; 2 user cùng câu khác answer / không cache-leak; empty transcript; utterance "em đã qua INT1203" vẫn FAILED
- **Mô tả:** Classifier rules; skip RAG trên COURSE_ADVICE; prepend cấm bịa; COURSE_ADVICE skip cache; HYBRID suffix user_id; invalidate cache khi `StudentRecordService` ghi.

### PR4 — Ingest course_id + material_type

- **Title:** `feat(ingest): attach course_id and material_type to chunks and Qdrant payload`
- **Depends:** PR2 (materials table); có thể song song muộn PR3 nhưng merge sau PR3 để chat filter dùng được
- **Files:** `processing_service.py`, `vector_service.py` (filter + payload index), `jobs/ingest.py`, `learning_material_service.py`, `api/v1/files.py` hoặc datasets add-file form fields, `api/v1/academic.py` POST materials, UI dataset upload (minimal)
- **Mô tả:** Payload Qdrant thêm `course_id`, `course_code`, `material_type`; search filter; bind `learning_materials.file_id`.

### PR5 — Student UI + Admin grades/courses + branding P2

- **Title:** `feat(ui): advisor chat, eligible courses, transcript, grade entry, FIT branding`
- **Depends:** PR2 (pages REST), PR3 (chat copy), PR4 (materials page tốt nhất; có thể materials empty)
- **Files:**
  - New: `src/app/dashboard/eligible-courses/page.tsx`, `transcript/page.tsx`, `materials/page.tsx`, `src/app/admin/courses/page.tsx`, `src/app/admin/grades/page.tsx`, `src/services/academicService.ts`, `courseService.ts`
  - Edit: `StudentNav.tsx`, `StudentChat.tsx`, `Sidebar.tsx`, `dashboard/page.tsx` (welcome copy admin), `chat/page.tsx`, `themeConfig.ts`, `AIRCLogo.tsx` → `FitLogo.tsx`, `layout.tsx`, `auth/login/page.tsx` (+ forgot/register/reset), `ChatMessages.tsx`
- **Mô tả:** Tab sinh viên; bảng eligible/transcript; admin CRUD môn + CSV điểm; bind upload; branding Khoa CNTT. Live Voice không phải acceptance.

### PR6 — Extra personas + PDF demo

- **Title:** `chore(demo): SV_WEB/SV_AI/SV_NEW personas and sample course PDFs`
- **Depends:** PR3, PR5 (để hội đồng click); PDF ingest cần PR4
- **Files:** `migrations/003_seed_demo_personas.sql`, `document/demo_materials/` (PDF), script ingest bind INT1101/INT1203/INT2104/INT2202, checklist demo README ngắn trong `document/` (không rewrite CHANGELOG history)
- **Mô tả:** 4 account `Pass123`; cùng câu Web track khác đáp án; tài liệu RAG cite được file thật.

### Ngoài scope / follow-up (không PR luận văn)

- Rename thư mục `airc_*`
- K8s Postgres
- SIS connector
- Alembic
- `pg_trgm` / tool-calling agent
---
