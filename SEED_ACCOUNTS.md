# Danh Sách Tài Khoản Seed (Dữ Liệu Mẫu) — Hệ Thống Cố Vấn Học Tập Khoa CNTT

Tất cả tài khoản mẫu dưới đây đều đã được cấu hình sẵn trong cơ sở dữ liệu hệ thống (PostgreSQL). Dữ liệu được thiết kế mô phỏng chính xác môi trường đào tạo đại học thực tế ngành Công nghệ Thông tin (CNTT), bao gồm sinh viên từ **Năm 1 đến Năm 4** với nhiều trường hợp học tập khác nhau.

---

## 1. Thông Tin Đăng Nhập Chung

- **Mật khẩu dùng chung cho tất cả tài khoản**: `Pass123`
  *(Lưu ý: Chữ **P** viết hoa, đúng 7 ký tự).*
- **Định dạng Email trường**: `@eaut.edu.vn`

---

## 2. Bảng Tổng Hợp Tài Khoản Mẫu Theo Khóa & Vai Trò

### 🎓 A. Nhóm Quản Trị & Giảng Viên

| STT | Email                     | Mật khẩu  |     Vai trò     | Họ và tên               | Mã số | Mục đích kiểm thử                                                                               |
| :-: | :------------------------ | :---------- | :---------------: | :------------------------- | :-----: | :--------------------------------------------------------------------------------------------------- |
|  1  | `admin@eaut.edu.vn`      | `Pass123` |  **Admin**  | Quản trị viên Khoa CNTT |   —   | Toàn quyền quản trị hệ thống, quản lý người dùng, dataset, tài liệu, cấu hình chatbot |
|  2  | `gv01@eaut.edu.vn`       | `Pass123` | **Teacher** | Nguyễn Văn An            |   —   | Giảng viên, quản lý tài liệu môn học, xem bảng điểm sinh viên                            |
|  3  | `gv_advisor@eaut.edu.vn` | `Pass123` | **Teacher** | PGS.TS Trần Văn Hùng    |  GV002  | Cố vấn học tập Khoa CNTT, tra cứu và tư vấn lộ trình học tập cho sinh viên              |

---

### 🎒 B. Sinh Viên Khóa 2024 — Năm 1 (K24)

| STT | Email                    | Mật khẩu  |       Mã SV       | Họ và tên      | Tình trạng học tập & Mục đích test                                                                                                |
| :-: | :----------------------- | :---------- | :----------------: | :---------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
|  4  | `svnew@eaut.edu.vn`     | `Pass123` |  **SVNEW**  | Vũ Nhật Nam     | Mới hoàn thành HK1, chưa học OOP, hỏi tư vấn đăng ký môn HK2                                                                 |
|  5  | `sv24_top@eaut.edu.vn`  | `Pass123` | **20240101** | Hoàng Minh Đức | **Tân SV xuất sắc**: GPA 9.1, hoàn thành xuất sắc HK1, đang học HK2, hỏi đăng ký môn HK3 sớm                        |
|  6  | `sv24_warn@eaut.edu.vn` | `Pass123` | **20240102** | Lê Quốc Tuấn   | **Tân SV trượt môn nền tảng**: Trượt `INT1101` (3.0) & `INT1102` (3.5). Bị chặn `INT1201`, cần tư vấn học lại |

---

### 🎒 C. Sinh Viên Khóa 2023 — Năm 2 (K23)

| STT | Email                    | Mật khẩu  |       Mã SV       | Họ và tên       | Tình trạng học tập & Mục đích test                                                                                     |
| :-: | :----------------------- | :---------- | :----------------: | :----------------- | :---------------------------------------------------------------------------------------------------------------------------- |
|  7  | `sv01@eaut.edu.vn`      | `Pass123` |  **SV001**  | Lê Hải Đăng    | Trượt`INT1203` (KTMT), đang học Web `INT2104` & PTTK `INT2103`                                                      |
|  8  | `svweb@eaut.edu.vn`     | `Pass123` |  **SVWEB**  | Trần Minh Quân   | Đã qua`INT2104` (8.0) & `INT1202` (8.0), đủ tiên quyết học Web App `INT2204`                                     |
|  9  | `svai@eaut.edu.vn`      | `Pass123` |   **SVAI**   | Đặng Thu Hà     | Đã qua`INT2202` (AI - 8.5) & `INT1103` (ĐSTT - 8.5), chuẩn bị học Học máy `INT3101`                             |
| 10 | `sv23_soft@eaut.edu.vn` | `Pass123` | **20230201** | Đỗ Phương Linh | **Định hướng Software**: Đã qua OOP, CSDL, CTDL điểm giỏi (8.0-9.0), đang học CNPM                           |
| 11 | `sv23_net@eaut.edu.vn`  | `Pass123` | **20230202** | Nguyễn Hải Nam   | **Định hướng Mạng & Bảo mật**: Đã qua Mạng MT, KTMT, HĐH. Hỏi về môn An ninh mạng, Quản trị mạng      |
| 12 | `sv23_avg@eaut.edu.vn`  | `Pass123` | **20230203** | Phạm Ngọc Thảo  | **Học lực Trung bình**: GPA 6.1, không nợ môn, điểm 5.0 - 6.5. Hỏi cải thiện điểm và lộ trình vừa sức |

---

### 🎒 D. Sinh Viên Khóa 2022 — Năm 3 (K22)

| STT | Email                    | Mật khẩu  |       Mã SV       | Họ và tên     | Tình trạng học tập & Mục đích test                                                                                                   |
| :-: | :----------------------- | :---------- | :----------------: | :--------------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| 13 | `sv22_data@eaut.edu.vn` | `Pass123` | **20220301** | Trần Gia Huy    | **Định hướng Data & AI**: Tích lũy 85 TC, đã học Machine Learning, CSDL nâng cao, đang học Big Data & Deep Learning       |
| 14 | `sv22_warn@eaut.edu.vn` | `Pass123` | **20220302** | Bùi Tiến Dũng | **Cảnh báo học tập mức 2**: Nợ nhiều môn cơ sở (`INT1202`, `INT2101`, `INT2102`, `INT2103`), mới tích lũy ~30 TC |
| 15 | `sv22_web@eaut.edu.vn`  | `Pass123` | **20220303** | Vũ Mai Phương | **Web Fullstack & Cloud**: Đã học Lập trình Web, Web nâng cao, Cloud. Chuẩn bị làm Đồ án chuyên ngành                   |

---

### 🎒 E. Sinh Viên Khóa 2021 — Năm 4 (K21 - Năm cuối tốt nghiệp)

| STT | Email                     | Mật khẩu  |       Mã SV       | Họ và tên        | Tình trạng học tập & Mục đích test                                                                                             |
| :-: | :------------------------ | :---------- | :----------------: | :------------------ | :------------------------------------------------------------------------------------------------------------------------------------ |
| 16 | `sv21_top@eaut.edu.vn`   | `Pass123` | **20210401** | Nguyễn Khắc Hưng | **Sinh viên Xuất sắc chuẩn bị tốt nghiệp**: GPA 9.25, tích lũy 128 TC, đủ điều kiện làm Khóa luận tốt nghiệp |
| 17 | `sv21_delay@eaut.edu.vn` | `Pass123` | **20210402** | Chu Thanh Tùng     | **Sinh viên Trễ tiến độ**: Nợ môn Thực tập chuyên ngành & nợ chuẩn đầu ra chứng chỉ ngoại ngữ                |

---

## 3. Hướng Dẫn Kiểm Thử Nhanh

1. Mở trang đăng nhập: `http://localhost:3000/auth/login`
2. Nhập Email (Ví dụ: `admin@eaut.edu.vn` hoặc `sv01@eaut.edu.vn`)
3. Nhập Mật khẩu: `Pass123`
4. Bấm **Đăng nhập** để vào Dashboard tương ứng với vai trò.
