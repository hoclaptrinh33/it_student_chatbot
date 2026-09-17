# Changelog

Chỉ ghi thay đổi và bug. Trạng thái: `Đã làm` · `Đã sửa` · `Chưa sửa`

---

## Chưa commit

### Thay đổi

| Mục | Trạng thái |
|-----|------------|
| Cố vấn nói giọng giáo viên (cô/em), không lộ [AcademicFacts]/PREREQUISITE; tên file tài liệu thành link `/files/<id>/view` mở tab mới | Đã sửa |
| Trị gốc: bot cố vấn không reject no_context khi academic facts bật; default intent COURSE_ADVICE; map tên môn từ catalog | Đã sửa |
| Câu “tình hình học tập” / bảng điểm xếp COURSE_ADVICE; HYBRID không reject khi đã có AcademicFacts dù dataset trống | Đã sửa |
| Chat `xin chào` / greeting không đi RAG; trả lời giới thiệu cố vấn thay vì NO CONTEXT | Đã sửa |
| HF_HOME Core/Worker `/tmp/hf_home` (volume `models_cache` mount đè, appuser không ghi được) | Đã sửa |
| Auth + Core cắt Mongo/Motor: SQLAlchemy 2.0 + asyncpg, `DATABASE_URL`, repository dict `id` UUID | Đã làm |
| `ChatbotRepository.get_by_id` JOIN `chatbot_datasets` hydrate `dataset_ids`; keyword search ILIKE token | Đã làm |
| Worker ingest mở `SessionLocal` Postgres, commit sau `process_dataset_file` | Đã làm |
| Delta RAG (`sessions` nhánh, `messages.extra`, cột parent-child `chunks`, `learning_materials.file_id`) trong `init_db.sql` + `migrations/002_align_rag_schema.sql` | Đã làm |
| Seed chatbot `eeeeeeee-…` giữ persona RAG chặt (`no_context_behavior=reject`) đến PR3 | Đã làm |
| Sửa dual-identity role, ingest commit ERROR, settings đọc cùng session | Đã sửa |
| Live Voice Mode: STT (Web Speech) + TTS (Edge-TTS), modal live trên dashboard và student chat | Đã làm |
| API `POST /api/v1/voice/tts` (voice allowlist, stream MP3, không log nội dung user) | Đã làm |
| Hiện nguồn (citation) dưới câu trả lời; click mở file gốc; lưu sources khi reload session | Đã làm |
| Streaming SSE `POST /api/v1/chat/ask/stream`; UI render token dần | Đã làm |
| Feedback 👍👎 (`POST /api/v1/chat/feedback`); dashboard lấy accuracy/latency thật | Đã làm |
| Share dataset chọn từng sinh viên; `all_students` dùng `shared_with: ["*"]` | Đã làm |
| Forgot/reset password (token SHA-256, SMTP optional, UI `/auth/forgot-password`) | Đã làm |
| Gán role user thật: `GET /users/{id}`, `PUT /rbac/users/{id}/roles` + UI admin | Đã làm |
| CORS Core/Auth: origin allowlist, không còn `*` + credentials | Đã làm |
| K8s: Cloudflared token qua Secret; kustomize secretGenerator; cert = `ragairc.neovort.shop` | Đã làm |
| Tắt `ignoreBuildErrors` trên Next.js | Đã làm |
| Gộp transcript chat (ChatTranscript + useChatBranches) | Đã làm |
| `search_mode` / `similarity_threshold` chạy thật (RRF hybrid) | Đã làm |
| Gợi ý câu hỏi, xuất Markdown, drawer kiểm chứng nguồn, góp ý khi 👎 | Đã làm |
| Jenkins Core thêm stage Test | Đã làm |
| API không preload embedding/rerank (PRELOAD_MODELS); worker mới preload | Đã làm |
| Academic API: CRUD môn học (admin), tiên quyết, transcript/eligible own vs any | Đã làm |
| Upsert điểm + CSV import (batch 100, dòng lỗi không abort trừ `strict=true`) | Đã làm |
| Sinh viên ghi điểm / xem bảng điểm người khác → 403; xóa môn có `student_records` → 409 | Đã làm |
| Quyền học vụ `courses:*` / `records:*` / `materials:*` đồng bộ SQL + Auth + Core | Đã làm |
| Hybrid chat: IntentClassifier rules-first (`COURSE_ADVICE` / `MATERIAL_QA` / `HYBRID`) | Đã làm |
| Inject `[AcademicFacts]` từ JWT `user_id` (Postgres), không tin utterance sinh viên | Đã làm |
| Persona cố vấn Khoa CNTT + block cấm bịa mã môn (admin `system_prompt` không gỡ được) | Đã làm |
| Cache P0: COURSE_ADVICE skip; HYBRID suffix có `user_id` TTL 15 phút; invalidate khi ghi điểm | Đã làm |
| Ingest: payload Qdrant thêm `course_id`, `course_code`, `material_type` | Đã làm |
| Nguồn metadata ingest: form upload/add-files → `learning_materials` theo `file_id` → parse tên file (`INT2104_slides.pdf`) | Đã làm |
| `VectorService.search` filter `course_id` + `create_payload_index` keyword khi ensure collection | Đã làm |
| Bind `POST /academic/materials` ghi `file_id` + `course_id` + `material_type` (+ `dataset_id`) | Đã làm |
| Form API `course_id`/`material_type` trên `POST /files/upload` và `POST /datasets/{id}/files` | Đã làm |
| UI dataset upload chọn môn + loại tài liệu (PR5) | Đã làm |
| Tab sinh viên: Chat / Môn đủ ĐK / Bảng điểm / Tài liệu | Đã làm |
| Trang `/dashboard/eligible-courses` (badge PREVIOUS mềm) và `/dashboard/transcript` (empty "chưa có bảng điểm") | Đã làm |
| Trang `/dashboard/materials` lọc theo môn + `material_type` | Đã làm |
| Admin CRUD môn + tiên quyết (`/admin/courses`); admin/GV nhập điểm + CSV (`/admin/grades`) | Đã làm |
| Branding Khoa CNTT: navy `#0F4C81` + teal `#0D9488`, `FitLogo`, title cố vấn | Đã làm |
| Seed persona demo SV_WEB / SV_AI / SV_NEW (`Pass123`) — `migrations/005_seed_demo_personas.sql` + `init_db.sql` | Đã làm |
| PDF mẫu INT1101 / INT1203 / INT2104 / INT2202 + script ingest bind dataset `dddddddd-…` | Đã làm |
| Checklist demo hội đồng `document/DEMO_CHECKLIST.md` | Đã làm |

### Bug

| Mục | Trạng thái |
|-----|------------|
| Tắt mic rồi bot nói xong vẫn tự bật nghe lại | Đã sửa |
| Pause lúc đang tải câu TTS tiếp theo vẫn phát tiếp | Đã sửa |
| VAD 1s chỉ gửi text final, mất từ interim cuối câu | Đã sửa |
| Đóng modal lúc `audioCtx.resume()` leak mic / AudioContext | Đã sửa |
| Dashboard mở Live khi chưa chọn chatbot; gửi fail thì live im lặng | Đã sửa |
| Hướng dẫn mic hardcode `localhost:3000` | Đã sửa |
| Lỗi STT `network` / `audio-capture` restart vòng, không báo UI | Đã sửa |
| Live modal re-render ~60fps vì `setMicAudioLevel` mỗi frame | Đã sửa |
| Enter từ overlay lọt xuống ô chat phía sau; không đóng bằng Escape | Đã sửa |
| Core `require_permission` chỉ log warning, không chặn 403 | Đã sửa |
| Dashboard `accuracy_rate=89%` và `avg_response_time=1.2s` hardcode | Đã sửa |
| Share “all students” không ghi student nào; UI chọn SV cụ thể chưa làm | Đã sửa |
| Forgot-password là endpoint giả; trang gán role user dùng mock | Đã sửa |
| TTS không prefetch câu sau → ngắt quãng giữa các câu | Chưa sửa |
| Chưa ghi trên UI là STT đi Google, TTS đi Microsoft | Chưa sửa |
| `ChatInput.onOpenLiveVoice` không được dùng (dead code) | Chưa sửa |
| CORS `allow_origins=["*"]` + credentials; token Cloudflared hardcode; cert lệch ingress | Đã sửa |
| `_search_dataset` query file N+1 | Đã sửa |
| Reformulation/compression mặc định bật (thêm 1–2 lần LLM) | Đã sửa |
| Dashboard stats không auth | Đã sửa |
| UI tiếng Việt không dấu (ChatInput, DatasetTable, form admin) | Đã sửa |
| `search_mode` / threshold chỉ nằm trên form, retrieval luôn vector+regex | Đã sửa |

---

## `feature/rag-processing-improvements`

### Thay đổi

| Mục | Trạng thái |
|-----|------------|
| Parse tài liệu bằng Docling (PDF/DOCX/HTML, OCR) | Đã làm |
| Chunking layout-aware, parent-child, gộp chunk ngắn, overlap thông minh | Đã làm |
| Document profiling, section parsing, enrich context bằng tóm tắt / header bảng | Đã làm |
| Nén lịch sử hội thoại (incremental buffer) và reformulation câu hỏi | Đã làm |
| Upload nhiều file song song | Đã làm |
| Admin UI tiếng Việt; hỗ trợ chọn LLM local / OpenAI-compatible | Đã làm |
| Chat render Markdown, LaTeX, sơ đồ Mermaid | Đã làm |

### Bug

| Mục | Trạng thái |
|-----|------------|
| Chữ Việt không dấu trên admin (users, roles, permissions, datasets) | Đã sửa |

---

## Trước đó

### Thay đổi

| Mục | Trạng thái |
|-----|------------|
| Auth/RBAC, chia sẻ dataset, lọc user theo role | Đã làm |
| UI bỏ mock role, nối API thật | Đã làm |
| Seed, docker-compose, cấu hình môi trường local/dev | Đã làm |
