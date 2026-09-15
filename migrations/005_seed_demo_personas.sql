-- PR6: demo personas SV_WEB / SV_AI / SV_NEW (Pass123).
-- Fresh installs get the same rows from init_db.sql (append-only).
-- Apply on an existing volume:
--   docker cp migrations/005_seed_demo_personas.sql it_postgres:/tmp/005_seed_demo_personas.sql
--   docker exec it_postgres psql -U it_admin -d it_student_chatbot -f /tmp/005_seed_demo_personas.sql
-- Or:
--   psql "postgresql://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot" -f migrations/005_seed_demo_personas.sql
--
-- Hash identical to sv01 (pbkdf2-sha256 of Pass123):
-- $pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0

INSERT INTO users (id, email, hashed_password, full_name, role, student_code, department, is_active)
VALUES
    (
        '11111111-1111-1111-1111-111111111111',
        'svweb@fit.edu.vn',
        '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0',
        'Trần Minh Quân',
        'student',
        'SVWEB',
        'Khoa CNTT',
        TRUE
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        'svai@fit.edu.vn',
        '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0',
        'Đặng Thu Hà',
        'student',
        'SVAI',
        'Khoa CNTT',
        TRUE
    ),
    (
        '33333333-3333-3333-3333-333333333333',
        'svnew@fit.edu.vn',
        '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0',
        'Vũ Nhật Nam',
        'student',
        'SVNEW',
        'Khoa CNTT',
        TRUE
    )
ON CONFLICT (id) DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r ON r.code = u.role
WHERE u.id IN (
    '11111111-1111-1111-1111-111111111111'::UUID,
    '22222222-2222-2222-2222-222222222222'::UUID,
    '33333333-3333-3333-3333-333333333333'::UUID
)
ON CONFLICT (user_id, role_id) DO NOTHING;

-- SV_WEB: PASSED INT2104 + INT1202 + foundation HK1–HK2 → eligible INT2204
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT
    '11111111-1111-1111-1111-111111111111'::UUID,
    c.id,
    rec.status,
    rec.grade,
    rec.semester_taken,
    rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED', 8.00, '2024-1', 1),
    ('INT1102', 'PASSED', 7.50, '2024-1', 1),
    ('INT1103', 'PASSED', 7.00, '2024-1', 1),
    ('INT1104', 'PASSED', 8.50, '2024-1', 1),
    ('INT1201', 'PASSED', 7.50, '2024-2', 1),
    ('INT1202', 'PASSED', 8.00, '2024-2', 1),
    ('INT1203', 'PASSED', 7.00, '2024-2', 1),
    ('INT1204', 'PASSED', 8.50, '2024-2', 1),
    ('INT2104', 'PASSED', 8.00, '2024-2', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- SV_AI: PASSED INT1201 + INT2202 + INT1103 (nền tảng AI); chưa INT1204/INT2104
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT
    '22222222-2222-2222-2222-222222222222'::UUID,
    c.id,
    rec.status,
    rec.grade,
    rec.semester_taken,
    rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED', 8.00, '2024-1', 1),
    ('INT1102', 'PASSED', 7.00, '2024-1', 1),
    ('INT1103', 'PASSED', 8.50, '2024-1', 1),
    ('INT1104', 'PASSED', 8.00, '2024-1', 1),
    ('INT1201', 'PASSED', 8.00, '2024-2', 1),
    ('INT2202', 'PASSED', 8.50, '2024-2', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- SV_NEW: chỉ PASSED HK1 → eligible kiểu HK2, chưa INT2104
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT
    '33333333-3333-3333-3333-333333333333'::UUID,
    c.id,
    rec.status,
    rec.grade,
    rec.semester_taken,
    rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED', 8.00, '2024-1', 1),
    ('INT1102', 'PASSED', 7.50, '2024-1', 1),
    ('INT1103', 'PASSED', 7.00, '2024-1', 1),
    ('INT1104', 'PASSED', 8.50, '2024-1', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;
