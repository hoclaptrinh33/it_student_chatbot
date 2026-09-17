# Hệ Thống Hỏi Đáp Ngôn Ngữ Tự Nhiên Hỗ Trợ Chọn Môn Học và Tài Liệu Học Tập Cho Sinh Viên Khoa CNTT

### IT Student Academic Advisor & Learning Materials Chatbot

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.0+-black?logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC2626)](https://qdrant.tech/)
[![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

> **Học phần**: Trí tuệ nhân tạo (Artificial Intelligence)
> **Trường**: Đại học Công nghệ Đông Á (EAU) — **Khoa**: Công nghệ Thông tin
> **Nhóm thực hiện**: Nhóm 15
> **Báo cáo đồ án chính thức**: [`Report/BTL_TTNT_NHOM_15.docx`](Report/BTL_TTNT_NHOM_15.docx)

---

## 📌 1. Giới Thiệu Dự Án

Trong đào tạo đại học theo học chế tín chỉ, sinh viên ngành Công nghệ Thông tin (CNTT) thường gặp nhiều khó khăn trong việc:

1. **Nắm bắt chuỗi môn học tiên quyết**: Đồ thị phụ thuộc môn học (Prerequisites) phức tạp, nếu trượt hoặc học sai thứ tự sẽ bị nghẽn tiến độ tốt nghiệp.
2. **Lựa chọn định hướng chuyên ngành**: Lúng túng giữa các nhánh nghề nghiệp (Kỹ thuật phần mềm / Web, Trí tuệ nhân tạo / Khoa học dữ liệu, An toàn thông tin / Mạng máy tính).
3. **Tìm kiếm tài liệu học tập chính thống**: Tài liệu bài giảng, đề cương chi tiết (syllabus), đề thi tham khảo bị phân tán.
4. **Quá tải cố vấn học tập**: Giảng viên không thể phản hồi tức thì 24/7 mọi thắc mắc của hàng nghìn sinh viên.

**Giải pháp**: Hệ thống **Cố vấn học tập AI** ứng dụng kiến trúc **Tạo sinh tăng cường truy xuất (Retrieval-Augmented Generation - RAG)** kết hợp **Lập luận trên Đồ thị tiên quyết (Prerequisite DAG)** và **Bộ nhớ đệm ngữ nghĩa theo người dùng (Per-user Semantic Caching)**.

---

## ✨ 2. Các Tính Năng Nổi Bật

- 🎓 **Tư vấn môn đủ điều kiện thời gian thực**: Tự động đối chiếu bảng điểm cá nhân của sinh viên với cây tiên quyết (Prerequisite Closure) để chỉ ra các môn được phép học, môn bị chặn do thiếu môn tiên quyết hoặc môn cần học lại.
- 📚 **Tra cứu & Gợi ý tài liệu học tập (PDF)**: Truy xuất chính xác giáo trình, slide bài giảng, đề cương chi tiết từ kho tri thức vector Qdrant, kèm trích nguồn và nút tải tài liệu trực tiếp.
- 🎯 **Triệt tiêu ảo giác (Zero Hallucination)**: Kỹ thuật tiêm sự thật học vụ (`[AcademicFacts]` Injection) lấy trực tiếp từ CSDL PostgreSQL, cam kết không bịa mã môn học, số tín chỉ hay quy chế đào tạo.
- ⚡ **Bộ nhớ đệm ngữ nghĩa phân lập (Per-user Semantic Cache)**: Phản hồi dưới **100ms** cho các câu hỏi tương đồng ngữ nghĩa, đồng thời phân tách theo `user_id` để tuyệt đối bảo mật dữ liệu điểm số giữa các sinh viên.
- 🎙️ **Trợ lý giọng nói tương tác trực tiếp (Live Voice Advisor)**: Hỗ trợ sinh viên giao tiếp 2 chiều bằng giọng nói tiếng Việt với AI qua Web Audio / Speech Synthesis.
- 👥 **Hệ thống phân quyền đa vai trò (RBAC)**:
  - **Sinh viên**: Chatbot cố vấn, xem môn đủ điều kiện, tra cứu bảng điểm cá nhân, kho tài liệu học tập, cập nhật hồ sơ.
  - **Giảng viên**: Dashboard thống kê, tra cứu bảng điểm và môn đủ điều kiện của sinh viên, xem cây điều kiện tiên quyết trực quan, quản lý tài liệu và kho tri thức.
  - **Quản trị viên**: Quản lý người dùng, vai trò, quyền hạn, quản lý danh mục môn học, nhập bảng điểm, cấu hình tham số RAG Pipeline và LLM provider.

---

## 🏗️ 3. Kiến Trúc Hệ Thống

Hệ thống được xây dựng theo mô hình **Microservices**:

```
                              ┌───────────────────────────────────┐
                              │  Client Browser (Next.js 14 UI)   │
                              │       http://localhost:3000       │
                              └─────────────────┬─────────────────┘
                                                │ RESTful API / SSE
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
  ┌─────────────────────────────┐                               ┌─────────────────────────────┐
  │      it_auth Service        │                               │       it_core Service       │
  │     FastAPI (Port 8001)     │                               │     FastAPI (Port 8000)     │
  │  - JWT Authentication       │                               │  - Hybrid RAG Engine        │
  │  - RBAC (Admin/Teacher/SV)  │                               │  - Academic Facts Injection │
  │  - User Management          │                               │  - Prerequisite DAG Engine  │
  └──────────────┬──────────────┘                               │  - Per-user Semantic Cache  │
                 │                                              │  - Background Ingest Worker │
                 │                                              └──────────────┬──────────────┘
                 │                                                             │
                 ▼                                                             ▼
  ┌─────────────────────────────┐                               ┌─────────────────────────────┐
  │   PostgreSQL 15 Database    │                               │     Qdrant Vector DB        │
  │  - Users, Roles, Perms      │                               │  - 768-dim Vector Index     │
  │  - Courses (23 học phần)    │                               │  - Vietnamese-SBERT Embed   │
  │  - Prerequisite DAG (25)    │                               │  - Chunk Metadata Filtering │
  │  - Student Academic Records │                               └──────────────┬──────────────┘
  │  - Learning Materials (PDF) │                                              │
  └─────────────────────────────┘                               ┌──────────────┴──────────────┐
                                                                │     Redis Cache & Queue     │
                                                                │  - Semantic Cache Key Store │
                                                                │  - Document Ingest Jobs     │
                                                                └─────────────────────────────┘
```

---

## 📊 4. Dữ Liệu Học Vụ Mẫu (Seed Data)

Hệ thống đã nạp sẵn khung chương trình đào tạo chuẩn của Khoa CNTT:

- **23 môn học**: Từ học kỳ 1 đến học kỳ 6, bao gồm Đại cương, Cơ sở ngành và Chuyên ngành (Web, AI, Mạng máy tính, An toàn thông tin).
- **25 quan hệ tiên quyết**: Ràng buộc cứng (`PREREQUISITE`), ràng buộc học trước (`PREVIOUS`), ràng buộc song hành (`CO_REQUISITE`).
- **18+ tài liệu PDF**: Giáo trình, slide và đề cương chi tiết học phần đã chunk và vector hóa vào Qdrant.

### Tài khoản kiểm thử mẫu:

| Email                 | Vai trò         | Họ và tên / Mô tả                                     | Mật khẩu  |
| :-------------------- | :--------------- | :--------------------------------------------------------- | :---------- |
| `admin@eau.edu.vn`  | Quản trị viên | Quản trị viên Khoa CNTT                                 | `Pass123` |
| `gv01@eau.edu.vn`   | Giảng viên     | ThS. Nguyễn Văn An (Cố vấn học tập)                  | `Pass123` |
| `sv01@eau.edu.vn`   | Sinh viên       | Lê Hải Đăng (SV năm 2 - có môn rớt cần học lại) | `Pass123` |
| `sv_web@eau.edu.vn` | Sinh viên       | Trần Thị Mai (SV định hướng Lập trình Web)         | `Pass123` |
| `sv_ai@eau.edu.vn`  | Sinh viên       | Phạm Văn Bình (SV định hướng Trí tuệ nhân tạo)  | `Pass123` |
| `sv_new@eau.edu.vn` | Sinh viên       | Hoàng Gia Bảo (SV năm nhất mới nhập học)            | `Pass123` |

---

## 🚀 5. Hướng Dẫn Cài Đặt & Chạy Hệ Thống

### Yêu cầu tiên quyết:

- Docker và Docker Compose (hoặc Podman)
- Node.js 18+ và Python 3.11+ (nếu chạy không qua Docker)
- API Key Google Gemini (`GEMINI_API_KEY`)

### Bước 1: Sao chép dự án và cấu hình môi trường

```bash
git clone https://github.com/hoclaptrinh33/it_student_chatbot.git
cd it_student_chatbot

# Tạo file .env từ file mẫu
cp airc_internal_chatbot_core/.env.example airc_internal_chatbot_core/.env
# Điền khóa GEMINI_API_KEY của bạn vào file .env
```

### Bước 2: Khởi chạy toàn bộ hệ thống bằng Docker Compose

```bash
docker compose -f docker-compose.local.yml up -d --build
```

Hệ thống sẽ tự động khởi động các dịch vụ:

- **Frontend Web UI**: `http://localhost:3000`
- **Core Backend API**: `http://localhost:8000` (Tài liệu Swagger: `http://localhost:8000/docs`)
- **Auth Backend API**: `http://localhost:8001` (Tài liệu Swagger: `http://localhost:8001/docs`)
- **PostgreSQL 15**: `localhost:5432` (Database: `it_student_chatbot`)
- **Qdrant Vector DB**: `http://localhost:6333/dashboard`
- **Redis Cache**: `localhost:6379`

### Bước 3: Đăng nhập và trải nghiệm

1. Truy cập `http://localhost:3000`
2. Đăng nhập với tài khoản sinh viên `sv01@eau.edu.vn` / mật khẩu `Pass123`.
3. Thử đặt các câu hỏi:
   - *'Kỳ tới em được đăng ký những môn học nào?'*
   - *'Em muốn theo hướng Lập trình Web thì nên chọn môn gì?'*
   - *'Môn Lập trình Web có những điều kiện tiên quyết nào và cho em xin tài liệu học tập?'*
   - *'Em bị trượt môn Kiến trúc máy tính thì có đăng ký được Hệ điều hành không?'*

---

## 📸 6. Hình Ảnh Giao Diện Hệ Thống

Toàn bộ ảnh chụp thực tế từ hệ thống được lưu tại thư mục [`Report/image`](Report/image/):

- **Đăng nhập & Xác thực**: `01_dang_nhap.png`, `01b_dang_nhap_mobile.png`, `02_dang_ky.png`
- **Sinh viên**:
  - Tư vấn lộ trình môn học: `12_sv_chat_tu_van_mon.png`
  - Trích xuất nguồn tài liệu PDF: `12b_sv_chat_nguon_tham_khao.png`
  - Danh sách môn đủ điều kiện: `13_sv_mon_du_dieu_kien.png`
  - Bảng điểm cá nhân: `14_sv_bang_diem.png`
  - Trợ lý giọng nói Live Voice: `18_sv_live_voice.png`
- **Giảng viên**:
  - Tra cứu bảng điểm sinh viên: `21_gv_quan_ly_diem.png`
  - Sơ đồ điều kiện tiên quyết môn học: `23b_gv_tien_quyet.png`
- **Quản trị viên**:
  - Quản lý người dùng & vai trò: `31_admin_nguoi_dung.png`
  - Cấu hình RAG Pipeline: `35_admin_cau_hinh_chatbot.png`

---

## 📄 7. Báo Cáo Học Thuật

Chi tiết cơ sở lý thuyết Trí tuệ nhân tạo, thiết kế giải thuật, mô hình toán học và đánh giá thực nghiệm được trình bày đầy đủ trong tài liệu:
👉 **[`Report/BTL_TTNT_NHOM_15.docx`](Report/BTL_TTNT_NHOM_15.docx)**

---

## 👥 8. Thành Viên Thực Hiện (Nhóm 15)

1. **Lê Hải Đăng** (Nhóm trưởng) — MSV: 20233288 — Lớp: DCCNTT14.9
2. **Lê Minh Quân** — MSV: 20233302 — Lớp: DCCNTT14.9
3. **Lê Xuân Đạt** — MSV: 20233303 — Lớp: DCCNTT14.9
4. **Lê Thanh Tùng** — MSV: 20233304 — Lớp: DCCNTT14.9
5. **Phạm Bảo Sơn** — MSV: 20233305 — Lớp: DCCNTT14.9

---

*Bắc Ninh, Năm 2026 — Khoa Công nghệ Thông tin, Trường Đại học Công nghệ Đông Á.*
