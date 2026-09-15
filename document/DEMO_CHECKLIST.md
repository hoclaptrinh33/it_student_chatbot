# Checklist demo hội đồng — 4 persona + PDF môn học

Mật khẩu chung: **`Pass123`**. Chatbot: `eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee`. Dataset RAG: `dddddddd-dddd-dddd-dddd-dddddddddddd`.

Volume Postgres cũ (không chạy lại `init_db.sql`):

```bash
docker cp migrations/005_seed_demo_personas.sql it_postgres:/tmp/005_seed_demo_personas.sql
docker exec it_postgres psql -U it_admin -d it_student_chatbot -f /tmp/005_seed_demo_personas.sql
```

Volume mới: các INSERT đã nằm cuối `init_db.sql`.

## Tài khoản

| Persona | Email | MSSV | UUID | Tình trạng |
|---------|-------|------|------|------------|
| SV001 | `sv01@fit.edu.vn` | SV001 | `cccccccc-cccc-cccc-cccc-cccccccccccc` | FAILED INT1203; IN_PROGRESS INT2103 + INT2104 |
| SV_WEB | `svweb@fit.edu.vn` | SVWEB | `11111111-1111-1111-1111-111111111111` | PASSED INT2104 + INT1202 + nền tảng HK1–HK2 |
| SV_AI | `svai@fit.edu.vn` | SVAI | `22222222-2222-2222-2222-222222222222` | PASSED INT1201 + INT2202 + INT1103 |
| SV_NEW | `svnew@fit.edu.vn` | SVNEW | `33333333-3333-3333-3333-333333333333` | Chỉ PASSED HK1 |

## Câu hỏi (cùng một câu, bốn lần login)

> E muốn theo đường dev web thì học kì này lên học những môn nào

Intent kỳ vọng: `COURSE_ADVICE`, `career_track=WEB`.

## Đáp án kỳ vọng

| Persona | Bot nên nói | Bot không nên |
|---------|-------------|----------------|
| **SV001** | Giữ INT2104 (đang học). Học lại INT1203. INT2204 chưa đăng ký được (INT2104 chưa PASSED). INT2101 bị chặn vì INT1203. | Bảo bỏ INT2104; bảo đăng ký INT2204 |
| **SV_WEB** | Eligible **INT2204** Phát triển ứng dụng Web (đã PASSED INT2104 + INT1202) | Nói chưa đủ tiên quyết INT2204 |
| **SV_AI** | Gợi ý **INT3101** Học máy (đã PASSED INT2202 + INT1103). Không đẩy lộ trình Web | Đẩy INT2204 / INT2104 khi chưa qua INT1204/INT2104 |
| **SV_NEW** | Môn kiểu HK2: INT1201, INT1204, INT1202, INT1203 | Gợi ý INT2104 (cần INT1204) |

Mọi mã môn trong câu trả lời phải có trong `[AcademicFacts]`.

## PDF mẫu

Thư mục `document/demo_materials/` — mỗi môn 1 syllabus + 1 slide:

- INT1101, INT1203, INT2104, INT2202

Tạo lại PDF (không cần thư viện):

```bash
python document/demo_materials/generate_pdfs.py
```

Ingest + bind vào dataset mặc định (cần Auth, Core, worker đang chạy):

```bash
python document/demo_materials/ingest_demo_materials.py
```

Nếu stack chưa lên, script in curl tương đương. Upload: `POST /api/v1/files/upload`. Bind + ingest: `POST /api/v1/datasets/dddddddd-dddd-dddd-dddd-dddddddddddd/files` với `course_id` + `material_type`.

Sau ingest, hỏi tài liệu (login GV/SV): *Đề cương INT2104 gồm những nội dung gì?* — bot cite file PDF.
