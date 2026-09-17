-- =============================================================================
-- init_db.sql — Schema PostgreSQL 15 cho chatbot cố vấn học tập Khoa CNTT
-- Chạy tự động lần đầu qua /docker-entrypoint-initdb.d khi volume postgres trống.
--
-- Kết nối:
--   postgresql+asyncpg://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot
--
-- Tài khoản mẫu (mật khẩu Pass123, hash pbkdf2-sha256):
--   admin@eaut.edu.vn
--   gv01@eaut.edu.vn
--   sv01@eaut.edu.vn
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =============================================================================
-- 1. AUTH / RBAC
-- =============================================================================

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            VARCHAR(50)  NOT NULL DEFAULT 'student'
                    CHECK (role IN ('admin', 'teacher', 'student')),
    student_code    VARCHAR(20),
    department      VARCHAR(100) DEFAULT 'Khoa CNTT',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

CREATE UNIQUE INDEX ux_users_student_code
    ON users (student_code)
    WHERE student_code IS NOT NULL;

CREATE TABLE roles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(50)  NOT NULL UNIQUE,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    is_system   BOOLEAN NOT NULL DEFAULT FALSE,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ
);

CREATE TABLE permissions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(100) NOT NULL UNIQUE,
    name        VARCHAR(200) NOT NULL,
    resource    VARCHAR(50)  NOT NULL,
    action      VARCHAR(50)  NOT NULL,
    scope       VARCHAR(50),
    description TEXT,
    is_system   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_roles (
    user_id     UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    role_id     UUID NOT NULL REFERENCES roles (id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    assigned_by UUID REFERENCES users (id) ON DELETE SET NULL,
    expires_at  TIMESTAMPTZ,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE role_permissions (
    role_id       UUID NOT NULL REFERENCES roles (id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions (id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE password_reset_tokens (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at    TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- 2. ACADEMIC — môn học, tiên quyết, kết quả, tài liệu
-- =============================================================================

CREATE TABLE courses (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code    VARCHAR(20)  NOT NULL UNIQUE,
    course_name    VARCHAR(255) NOT NULL,
    credits        INTEGER      NOT NULL CHECK (credits > 0),
    theory_hours   INTEGER      NOT NULL DEFAULT 0 CHECK (theory_hours >= 0),
    practice_hours INTEGER      NOT NULL DEFAULT 0 CHECK (practice_hours >= 0),
    semester       INTEGER      CHECK (semester BETWEEN 1 AND 8),
    is_mandatory   BOOLEAN      NOT NULL DEFAULT TRUE,
    career_track   VARCHAR(50)  NOT NULL DEFAULT 'GENERAL'
                   CHECK (career_track IN (
                       'GENERAL', 'AI', 'WEB', 'SECURITY',
                       'DATA', 'NETWORK', 'SOFTWARE'
                   )),
    description    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ
);

CREATE TABLE course_prerequisites (
    course_id              UUID NOT NULL REFERENCES courses (id) ON DELETE CASCADE,
    prerequisite_course_id UUID NOT NULL REFERENCES courses (id) ON DELETE CASCADE,
    relation_type          VARCHAR(20) NOT NULL
                           CHECK (relation_type IN ('PREREQUISITE', 'PREVIOUS', 'CO_REQUISITE')),
    PRIMARY KEY (course_id, prerequisite_course_id, relation_type),
    CHECK (course_id <> prerequisite_course_id)
);

CREATE TABLE student_records (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    course_id      UUID NOT NULL REFERENCES courses (id) ON DELETE RESTRICT,
    status         VARCHAR(20) NOT NULL
                   CHECK (status IN ('PASSED', 'FAILED', 'IN_PROGRESS')),
    grade          NUMERIC(4, 2) CHECK (grade IS NULL OR (grade >= 0 AND grade <= 10)),
    semester_taken VARCHAR(20),
    attempt_count  INTEGER NOT NULL DEFAULT 1 CHECK (attempt_count >= 1),
    recorded_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, course_id)
);

CREATE TABLE learning_materials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id       UUID NOT NULL REFERENCES courses (id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    material_type   VARCHAR(20)  NOT NULL
                    CHECK (material_type IN ('SYLLABUS', 'SLIDE', 'TEXTBOOK', 'EXAM')),
    file_url        TEXT,
    qdrant_point_id VARCHAR(64),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- 3. CORE RAG — chatbot, dataset, session, message
-- =============================================================================

CREATE TABLE datasets (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name         VARCHAR(200) NOT NULL,
    description  TEXT,
    owner_id     UUID REFERENCES users (id) ON DELETE SET NULL,
    visibility   VARCHAR(20) NOT NULL DEFAULT 'private'
                 CHECK (visibility IN ('private', 'shared', 'public')),
    shared_with  TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    file_count   INTEGER NOT NULL DEFAULT 0,
    total_chunks INTEGER NOT NULL DEFAULT 0,
    status       VARCHAR(20) NOT NULL DEFAULT 'ready',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ
);

CREATE TABLE files (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name         VARCHAR(255) NOT NULL,
    path         TEXT,
    mime_type    VARCHAR(100),
    size         BIGINT NOT NULL DEFAULT 0,
    status       VARCHAR(20) NOT NULL DEFAULT 'Ready',
    owner_id     UUID REFERENCES users (id) ON DELETE SET NULL,
    uploaded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    error        TEXT
);

CREATE TABLE dataset_files (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id   UUID NOT NULL REFERENCES datasets (id) ON DELETE CASCADE,
    file_id      UUID NOT NULL REFERENCES files (id) ON DELETE CASCADE,
    status       VARCHAR(20) NOT NULL DEFAULT 'Pending',
    is_enabled   BOOLEAN NOT NULL DEFAULT TRUE,
    chunk_count  INTEGER NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    UNIQUE (dataset_id, file_id)
);

CREATE TABLE chunks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID NOT NULL REFERENCES datasets (id) ON DELETE CASCADE,
    dataset_file_id UUID REFERENCES dataset_files (id) ON DELETE CASCADE,
    file_id         UUID REFERENCES files (id) ON DELETE CASCADE,
    text            TEXT NOT NULL,
    chunk_index     INTEGER NOT NULL DEFAULT 0,
    qdrant_point_id VARCHAR(64),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    embedding_text  TEXT,
    context_enriched_text TEXT,
    heading_path    TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    is_parent       BOOLEAN NOT NULL DEFAULT FALSE,
    parent_chunk_id UUID REFERENCES chunks (id) ON DELETE SET NULL,
    domain          VARCHAR(50),
    language        VARCHAR(10) DEFAULT 'vi',
    section_type    VARCHAR(50),
    chunk_role      VARCHAR(50) DEFAULT 'standalone',
    is_table        BOOLEAN NOT NULL DEFAULT FALSE,
    table_caption   TEXT,
    table_header    TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    quality_flags   TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    page            INTEGER,
    extra           JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE TABLE chatbots (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(200) NOT NULL,
    description         TEXT,
    icon                VARCHAR(100),
    owner_id            UUID REFERENCES users (id) ON DELETE SET NULL,
    visibility          VARCHAR(20) NOT NULL DEFAULT 'public'
                        CHECK (visibility IN ('public', 'private')),
    allowed_roles       TEXT[] NOT NULL DEFAULT ARRAY['student', 'teacher', 'admin']::TEXT[],
    allowed_user_ids    UUID[] NOT NULL DEFAULT ARRAY[]::UUID[],
    allowed_departments TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    config              JSONB NOT NULL DEFAULT '{}'::JSONB,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ
);

CREATE TABLE chatbot_datasets (
    chatbot_id UUID NOT NULL REFERENCES chatbots (id) ON DELETE CASCADE,
    dataset_id UUID NOT NULL REFERENCES datasets (id) ON DELETE CASCADE,
    PRIMARY KEY (chatbot_id, dataset_id)
);

CREATE TABLE sessions (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       VARCHAR(255),
    user_id    UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    chatbot_id UUID REFERENCES chatbots (id) ON DELETE SET NULL,
    parent_id  UUID REFERENCES sessions (id) ON DELETE SET NULL,
    branch_message_index INTEGER,
    conversation_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE messages (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions (id) ON DELETE CASCADE,
    role       VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content    TEXT NOT NULL,
    sources    JSONB,
    extra      JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE message_feedback (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages (id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions (id) ON DELETE CASCADE,
    user_id    UUID REFERENCES users (id) ON DELETE SET NULL,
    rating     VARCHAR(10) NOT NULL CHECK (rating IN ('up', 'down')),
    comment    TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (message_id, user_id)
);

CREATE TABLE system_settings (
    id         VARCHAR(50) PRIMARY KEY DEFAULT 'singleton',
    config     JSONB NOT NULL DEFAULT '{}'::JSONB,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- 4. INDEXES
-- =============================================================================

CREATE INDEX ix_courses_career_track ON courses (career_track);
CREATE INDEX ix_courses_semester ON courses (semester);
CREATE INDEX ix_courses_mandatory ON courses (is_mandatory);

CREATE INDEX ix_prereq_prerequisite ON course_prerequisites (prerequisite_course_id);
CREATE INDEX ix_prereq_type ON course_prerequisites (relation_type);

CREATE INDEX ix_student_records_user ON student_records (user_id);
CREATE INDEX ix_student_records_course_status ON student_records (course_id, status);

CREATE INDEX ix_materials_course_type ON learning_materials (course_id, material_type);

CREATE INDEX ix_sessions_user ON sessions (user_id);
CREATE INDEX ix_sessions_chatbot ON sessions (chatbot_id);
CREATE INDEX ix_messages_session ON messages (session_id, created_at);
CREATE INDEX ix_dataset_files_dataset ON dataset_files (dataset_id);
CREATE INDEX ix_chunks_dataset ON chunks (dataset_id);
CREATE INDEX ix_chunks_parent ON chunks (parent_chunk_id);
CREATE INDEX ix_chunks_file ON chunks (dataset_file_id);
CREATE INDEX ix_chatbots_owner ON chatbots (owner_id);

ALTER TABLE learning_materials
    ADD COLUMN IF NOT EXISTS file_id UUID REFERENCES files (id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS dataset_id UUID REFERENCES datasets (id) ON DELETE SET NULL;

-- =============================================================================
-- 5. RULE ENGINE — recursive CTE + môn đủ điều kiện
-- =============================================================================

-- Đóng bao tiên quyết (mọi cấp). Dùng để giải thích "vì sao chưa được học môn X".
CREATE OR REPLACE VIEW v_course_prerequisite_closure AS
WITH RECURSIVE tree AS (
    SELECT
        c.id            AS course_id,
        c.course_code   AS course_code,
        c.course_name   AS course_name,
        p.prerequisite_course_id,
        pc.course_code  AS prerequisite_code,
        pc.course_name  AS prerequisite_name,
        p.relation_type,
        1               AS depth,
        ARRAY[c.id, p.prerequisite_course_id] AS path
    FROM courses c
    JOIN course_prerequisites p ON p.course_id = c.id
    JOIN courses pc ON pc.id = p.prerequisite_course_id
    UNION ALL
    SELECT
        t.course_id,
        t.course_code,
        t.course_name,
        p.prerequisite_course_id,
        pc.course_code,
        pc.course_name,
        p.relation_type,
        t.depth + 1,
        t.path || p.prerequisite_course_id
    FROM tree t
    JOIN course_prerequisites p ON p.course_id = t.prerequisite_course_id
    JOIN courses pc ON pc.id = p.prerequisite_course_id
    WHERE t.depth < 10
      AND NOT (p.prerequisite_course_id = ANY (t.path))
)
SELECT
    course_id,
    course_code,
    course_name,
    prerequisite_course_id,
    prerequisite_code,
    prerequisite_name,
    relation_type,
    depth
FROM tree;

-- Môn sinh viên được phép đăng ký: mọi PREREQUISITE đã PASSED,
-- chưa PASSED / IN_PROGRESS, PREVIOUS chỉ mang tính khuyến nghị.
CREATE OR REPLACE FUNCTION fn_student_eligible_courses(p_user_id UUID)
RETURNS TABLE (
    course_id            UUID,
    course_code          TEXT,
    course_name          TEXT,
    credits              INTEGER,
    semester             INTEGER,
    career_track         TEXT,
    is_mandatory         BOOLEAN,
    missing_prereq_codes TEXT[],
    recommended_previous TEXT[]
)
LANGUAGE sql
STABLE
AS $$
    WITH hard_prereq AS (
        SELECT
            cp.course_id,
            ARRAY_AGG(pc.course_code::TEXT ORDER BY pc.course_code)
                FILTER (
                    WHERE sr.status IS DISTINCT FROM 'PASSED'
                ) AS missing
        FROM course_prerequisites cp
        JOIN courses pc ON pc.id = cp.prerequisite_course_id
        LEFT JOIN student_records sr
            ON sr.course_id = cp.prerequisite_course_id
           AND sr.user_id = p_user_id
        WHERE cp.relation_type = 'PREREQUISITE'
        GROUP BY cp.course_id
    ),
    soft_prev AS (
        SELECT
            cp.course_id,
            ARRAY_AGG(pc.course_code::TEXT ORDER BY pc.course_code)
                FILTER (
                    WHERE sr.status IS DISTINCT FROM 'PASSED'
                ) AS recommended
        FROM course_prerequisites cp
        JOIN courses pc ON pc.id = cp.prerequisite_course_id
        LEFT JOIN student_records sr
            ON sr.course_id = cp.prerequisite_course_id
           AND sr.user_id = p_user_id
        WHERE cp.relation_type = 'PREVIOUS'
        GROUP BY cp.course_id
    )
    SELECT
        c.id,
        c.course_code,
        c.course_name,
        c.credits,
        c.semester,
        c.career_track,
        c.is_mandatory,
        COALESCE(hp.missing, ARRAY[]::TEXT[]),
        COALESCE(sp.recommended, ARRAY[]::TEXT[])
    FROM courses c
    LEFT JOIN student_records mine
        ON mine.course_id = c.id AND mine.user_id = p_user_id
    LEFT JOIN hard_prereq hp ON hp.course_id = c.id
    LEFT JOIN soft_prev sp ON sp.course_id = c.id
    WHERE (mine.status IS NULL OR mine.status = 'FAILED')
      AND COALESCE(hp.missing, ARRAY[]::TEXT[]) = ARRAY[]::TEXT[]
$$;

-- =============================================================================
-- 6. SEED — RBAC
-- =============================================================================

INSERT INTO roles (code, name, description, is_system, is_active) VALUES
    ('admin',   'Administrator', 'Quản trị viên hệ thống — toàn quyền', TRUE, TRUE),
    ('teacher', 'Teacher',       'Giảng viên — quản lý tài liệu và chatbot của mình', TRUE, TRUE),
    ('student', 'Student',       'Sinh viên — hỏi đáp, xem lộ trình và tài liệu được chia sẻ', TRUE, TRUE);

INSERT INTO permissions (code, name, resource, action, scope, is_system) VALUES
    ('users:view',            'Xem người dùng',          'users',    'view',   NULL,    TRUE),
    ('users:create',          'Tạo người dùng',          'users',    'create', NULL,    TRUE),
    ('users:update',          'Cập nhật người dùng',     'users',    'update', NULL,    TRUE),
    ('users:delete',          'Xóa người dùng',          'users',    'delete', NULL,    TRUE),
    ('datasets:view:all',     'Xem mọi dataset',         'datasets', 'view',   'all',   TRUE),
    ('datasets:view:shared',  'Xem dataset được chia sẻ','datasets', 'view',   'shared',TRUE),
    ('datasets:create',       'Tạo dataset',             'datasets', 'create', NULL,    TRUE),
    ('datasets:update:own',   'Sửa dataset của mình',    'datasets', 'update', 'own',   TRUE),
    ('datasets:update:any',   'Sửa mọi dataset',         'datasets', 'update', 'any',   TRUE),
    ('datasets:delete:own',   'Xóa dataset của mình',    'datasets', 'delete', 'own',   TRUE),
    ('datasets:delete:any',   'Xóa mọi dataset',         'datasets', 'delete', 'any',   TRUE),
    ('datasets:share',        'Chia sẻ dataset',         'datasets', 'share',  NULL,    TRUE),
    ('chatbots:create',       'Tạo chatbot',             'chatbots', 'create', NULL,    TRUE),
    ('chatbots:use',          'Sử dụng chatbot',         'chatbots', 'use',    NULL,    TRUE),
    ('chatbots:manage:own',   'Quản lý chatbot của mình','chatbots', 'manage', 'own',   TRUE),
    ('chatbots:manage:any',   'Quản lý mọi chatbot',     'chatbots', 'manage', 'any',   TRUE),
    ('chat:use',              'Chat',                    'chat',     'use',    NULL,    TRUE),
    ('chat:view:own',         'Xem lịch sử chat của mình','chat',    'view',   'own',   TRUE),
    ('chat:view:any',         'Xem mọi lịch sử chat',    'chat',     'view',   'any',   TRUE),
    ('analytics:view',        'Xem thống kê',            'analytics','view',   NULL,    TRUE),
    ('system:manage',         'Quản trị hệ thống',       'system',   'manage', NULL,    TRUE),
    ('courses:view',          'Xem môn học',             'courses',  'view',   NULL,    TRUE),
    ('courses:manage',        'Quản lý môn học',         'courses',  'manage', NULL,    TRUE),
    ('records:view:own',      'Xem bảng điểm của mình',  'records',  'view',   'own',   TRUE),
    ('records:view:any',      'Xem mọi bảng điểm',       'records',  'view',   'any',   TRUE),
    ('records:update',        'Cập nhật bảng điểm',      'records',  'update', NULL,    TRUE),
    ('materials:view',        'Xem tài liệu học tập',    'materials','view',   NULL,    TRUE),
    ('materials:manage',      'Quản lý tài liệu học tập','materials','manage', NULL,    TRUE);

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON (
    (r.code = 'admin')
    OR (r.code = 'teacher' AND p.code IN (
        'datasets:view:all', 'datasets:create', 'datasets:update:own',
        'datasets:delete:own', 'datasets:share',
        'chatbots:use', 'chatbots:manage:own',
        'chat:use', 'chat:view:own', 'analytics:view',
        'courses:view', 'records:view:any', 'records:update',
        'materials:view', 'materials:manage'
    ))
    OR (r.code = 'student' AND p.code IN (
        'datasets:view:shared', 'chatbots:use', 'chat:use', 'chat:view:own',
        'courses:view', 'records:view:own', 'materials:view'
    ))
);

-- Hash pbkdf2-sha256 của "Pass123" (tương thích passlib).
-- $pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0
INSERT INTO users (id, email, hashed_password, full_name, role, student_code, department, is_active)
VALUES
    (
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        'admin@eaut.edu.vn',
        '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0',
        'Quản trị viên Khoa CNTT',
        'admin',
        NULL,
        'Khoa CNTT',
        TRUE
    ),
    (
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        'gv01@eaut.edu.vn',
        '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0',
        'Nguyễn Văn An',
        'teacher',
        NULL,
        'Khoa CNTT',
        TRUE
    ),
    (
        'cccccccc-cccc-cccc-cccc-cccccccccccc',
        'sv01@eaut.edu.vn',
        '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0',
        'Lê Hải Đăng',
        'student',
        'SV001',
        'Khoa CNTT',
        TRUE
    );

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r ON r.code = u.role;

-- =============================================================================
-- 7. SEED — chương trình môn CNTT cơ sở
-- =============================================================================

INSERT INTO courses (
    course_code, course_name, credits, theory_hours, practice_hours,
    semester, is_mandatory, career_track, description
) VALUES
    -- Học kỳ 1
    ('INT1101', 'Nhập môn lập trình', 3, 30, 30, 1, TRUE, 'GENERAL',
     'Cú pháp, kiểu dữ liệu, cấu trúc điều khiển, hàm. Ngôn ngữ C/Python.'),
    ('INT1102', 'Toán rời rạc', 3, 45, 0, 1, TRUE, 'GENERAL',
     'Logic, tập hợp, quan hệ, tổ hợp, đồ thị — nền tảng cho thuật toán và CSDL.'),
    ('INT1103', 'Đại số tuyến tính', 3, 45, 0, 1, TRUE, 'GENERAL',
     'Ma trận, không gian vector, trị riêng — nền tảng cho AI và đồ họa.'),
    ('INT1104', 'Nhập môn Công nghệ thông tin', 2, 30, 0, 1, TRUE, 'GENERAL',
     'Tổng quan ngành CNTT, đạo đức nghề nghiệp, kỹ năng học tập đại học.'),

    -- Học kỳ 2
    ('INT1201', 'Cấu trúc dữ liệu và giải thuật', 4, 45, 30, 2, TRUE, 'GENERAL',
     'Danh sách, stack, queue, cây, đồ thị, sắp xếp, tìm kiếm, độ phức tạp.'),
    ('INT1202', 'Cơ sở dữ liệu', 3, 30, 30, 2, TRUE, 'DATA',
     'Mô hình quan hệ, SQL, chuẩn hóa, giao dịch, PostgreSQL.'),
    ('INT1203', 'Kiến trúc máy tính', 3, 45, 0, 2, TRUE, 'GENERAL',
     'CPU, bộ nhớ, I/O, assembly, đường ống lệnh.'),
    ('INT1204', 'Lập trình hướng đối tượng', 3, 30, 30, 2, TRUE, 'SOFTWARE',
     'Lớp, kế thừa, đa hình, SOLID. Java/C#.'),

    -- Học kỳ 3
    ('INT2101', 'Hệ điều hành', 3, 45, 0, 3, TRUE, 'GENERAL',
     'Tiến trình, luồng, đồng bộ, quản lý bộ nhớ, file system, Linux.'),
    ('INT2102', 'Mạng máy tính', 3, 30, 30, 3, TRUE, 'NETWORK',
     'Mô hình OSI/TCP-IP, định tuyến, chuyển mạch, ứng dụng mạng.'),
    ('INT2103', 'Phân tích và thiết kế hệ thống', 3, 30, 30, 3, TRUE, 'SOFTWARE',
     'Yêu cầu, UML, use case, kiến trúc phần mềm.'),
    ('INT2104', 'Lập trình Web', 3, 30, 30, 3, FALSE, 'WEB',
     'HTML/CSS/JS, HTTP, REST, backend cơ bản.'),

    -- Học kỳ 4
    ('INT2201', 'Công nghệ phần mềm', 3, 45, 0, 4, TRUE, 'SOFTWARE',
     'Quy trình phát triển, kiểm thử, CI/CD, quản lý dự án.'),
    ('INT2202', 'Trí tuệ nhân tạo', 3, 30, 30, 4, FALSE, 'AI',
     'Tìm kiếm, heuristic, tri thức, agent, giới thiệu học máy.'),
    ('INT2203', 'An toàn thông tin', 3, 30, 30, 4, FALSE, 'SECURITY',
     'Mã hóa, xác thực, tấn công phổ biến, chính sách an ninh.'),
    ('INT2204', 'Phát triển ứng dụng Web', 3, 30, 30, 4, FALSE, 'WEB',
     'Framework hiện đại, xác thực, CSDL, triển khai.'),

    -- Học kỳ 5
    ('INT3101', 'Học máy', 3, 30, 30, 5, FALSE, 'AI',
     'Hồi quy, phân lớp, clustering, đánh giá mô hình, scikit-learn.'),
    ('INT3102', 'Xử lý ngôn ngữ tự nhiên', 3, 30, 30, 5, FALSE, 'AI',
     'Tokenization, embedding, phân loại văn bản, transformer, RAG.'),
    ('INT3103', 'An ninh mạng', 3, 30, 30, 5, FALSE, 'SECURITY',
     'Tường lửa, IDS/IPS, pentest cơ bản, phản ứng sự cố.'),
    ('INT3104', 'Phát triển Web nâng cao', 3, 30, 30, 5, FALSE, 'WEB',
     'SPA, Next.js, API gateway, hiệu năng, bảo mật web.'),
    ('INT3105', 'Điện toán đám mây', 3, 30, 30, 5, FALSE, 'NETWORK',
     'IaaS/PaaS/SaaS, container, Kubernetes, DevOps.'),

    -- Học kỳ 6
    ('INT3201', 'Deep Learning', 3, 30, 30, 6, FALSE, 'AI',
     'MLP, CNN, RNN/Transformer, PyTorch, tinh chỉnh mô hình.'),
    ('INT3202', 'Đồ án chuyên ngành', 3, 0, 90, 6, TRUE, 'GENERAL',
     'Thực hiện đề tài theo định hướng AI / Web / Security.');

-- Quan hệ tiên quyết / học trước / song hành
INSERT INTO course_prerequisites (course_id, prerequisite_course_id, relation_type)
SELECT c.id, p.id, rel.relation_type
FROM (VALUES
    -- HK2
    ('INT1201', 'INT1101', 'PREREQUISITE'),
    ('INT1201', 'INT1102', 'PREVIOUS'),
    ('INT1202', 'INT1102', 'PREVIOUS'),
    ('INT1204', 'INT1101', 'PREREQUISITE'),
    -- HK3
    ('INT2101', 'INT1203', 'PREREQUISITE'),
    ('INT2102', 'INT1203', 'PREVIOUS'),
    ('INT2103', 'INT1202', 'PREREQUISITE'),
    ('INT2103', 'INT1204', 'PREVIOUS'),
    ('INT2104', 'INT1204', 'PREREQUISITE'),
    -- HK4
    ('INT2201', 'INT2103', 'PREREQUISITE'),
    ('INT2201', 'INT1204', 'PREREQUISITE'),
    ('INT2202', 'INT1201', 'PREREQUISITE'),
    ('INT2202', 'INT1103', 'PREVIOUS'),
    ('INT2203', 'INT2102', 'PREREQUISITE'),
    ('INT2204', 'INT2104', 'PREREQUISITE'),
    ('INT2204', 'INT1202', 'PREREQUISITE'),
    -- HK5
    ('INT3101', 'INT2202', 'PREREQUISITE'),
    ('INT3101', 'INT1103', 'PREREQUISITE'),
    ('INT3102', 'INT3101', 'PREREQUISITE'),
    ('INT3103', 'INT2203', 'PREREQUISITE'),
    ('INT3104', 'INT2204', 'PREREQUISITE'),
    ('INT3105', 'INT2102', 'PREREQUISITE'),
    ('INT3105', 'INT2101', 'PREVIOUS'),
    -- HK6
    ('INT3201', 'INT3101', 'PREREQUISITE'),
    ('INT3202', 'INT2201', 'PREREQUISITE')
) AS rel (course_code, prereq_code, relation_type)
JOIN courses c ON c.course_code = rel.course_code
JOIN courses p ON p.course_code = rel.prereq_code;

-- Sinh viên mẫu: đã qua HK1–HK2, trượt Kiến trúc MT, đang học HK3
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT
    'cccccccc-cccc-cccc-cccc-cccccccccccc'::UUID,
    c.id,
    rec.status,
    rec.grade,
    rec.semester_taken,
    rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED',      8.50, '2024-1', 1),
    ('INT1102', 'PASSED',      7.00, '2024-1', 1),
    ('INT1103', 'PASSED',      6.50, '2024-1', 1),
    ('INT1104', 'PASSED',      9.00, '2024-1', 1),
    ('INT1201', 'PASSED',      7.50, '2024-2', 1),
    ('INT1202', 'PASSED',      8.00, '2024-2', 1),
    ('INT1203', 'FAILED',      3.50, '2024-2', 1),
    ('INT1204', 'PASSED',      8.00, '2024-2', 1),
    ('INT2103', 'IN_PROGRESS', NULL, '2025-1', 1),
    ('INT2104', 'IN_PROGRESS', NULL, '2025-1', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code;

-- Tài liệu học tập mẫu (file_url / qdrant_point_id điền khi ingest)
INSERT INTO learning_materials (course_id, title, material_type, file_url)
SELECT c.id, m.title, m.material_type, m.file_url
FROM (VALUES
    ('INT1101', 'Đề cương chi tiết — Nhập môn lập trình',          'SYLLABUS', '/materials/INT1101/syllabus.pdf'),
    ('INT1101', 'Slide bài giảng tuần 1–8',                         'SLIDE',    '/materials/INT1101/slides.pdf'),
    ('INT1101', 'Giáo trình Nhập môn lập trình Python',             'TEXTBOOK', '/materials/INT1101/textbook.pdf'),
    ('INT1101', 'Ngân hàng đề thi kết thúc học phần',               'EXAM',     '/materials/INT1101/exam.pdf'),
    ('INT1201', 'Đề cương chi tiết — CTDL & GT',                    'SYLLABUS', '/materials/INT1201/syllabus.pdf'),
    ('INT1201', 'Slide cây, heap, đồ thị',                          'SLIDE',    '/materials/INT1201/slides.pdf'),
    ('INT1202', 'Đề cương chi tiết — Cơ sở dữ liệu',                'SYLLABUS', '/materials/INT1202/syllabus.pdf'),
    ('INT1202', 'Giáo trình SQL và mô hình quan hệ',                'TEXTBOOK', '/materials/INT1202/textbook.pdf'),
    ('INT2202', 'Đề cương chi tiết — Trí tuệ nhân tạo',             'SYLLABUS', '/materials/INT2202/syllabus.pdf'),
    ('INT3102', 'Đề cương chi tiết — Xử lý ngôn ngữ tự nhiên',      'SYLLABUS', '/materials/INT3102/syllabus.pdf'),
    ('INT3102', 'Slide Transformer, embedding, RAG',                'SLIDE',    '/materials/INT3102/slides.pdf')
) AS m (course_code, title, material_type, file_url)
JOIN courses c ON c.course_code = m.course_code;

-- Chatbot + dataset mặc định cho cố vấn học tập
INSERT INTO datasets (id, name, description, owner_id, visibility, status)
VALUES (
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    'Đề cương & Giáo trình Khoa CNTT',
    'Kho tài liệu đề cương, slide, giáo trình và ngân hàng đề phục vụ RAG.',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'shared',
    'ready'
);

INSERT INTO chatbots (id, name, description, owner_id, visibility, allowed_roles, config, is_active)
VALUES (
    'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
    'Cố vấn Học tập Khoa CNTT',
    'Trợ lý hỏi đáp ngôn ngữ tự nhiên: chọn môn, kiểm tra tiên quyết, gợi ý tài liệu học tập.',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'public',
    ARRAY['student', 'teacher', 'admin']::TEXT[],
    jsonb_build_object(
        'search_mode', 'hybrid',
        'top_k', 5,
        'temperature', 0.3,
        'no_context_behavior', 'reject',
        'system_prompt',
            'Cô là giảng viên cố vấn Khoa CNTT, nói chuyện tự nhiên với em bằng tiếng Việt. Không dùng từ máy PASSED/FAILED/PREREQUISITE/[AcademicFacts]. Tài liệu phải là link markdown /files/<file_id>/view.'
    ),
    TRUE
);

INSERT INTO chatbot_datasets (chatbot_id, dataset_id)
VALUES (
    'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
    'dddddddd-dddd-dddd-dddd-dddddddddddd'
);

INSERT INTO system_settings (id, config)
VALUES (
    'singleton',
    jsonb_build_object(
        'app_name', 'IT Student Chatbot',
        'persona', 'academic_advisor',
        'academic_facts_enabled', true
    )
);

-- =============================================================================
-- 8. Gợi ý kiểm tra nhanh (chạy tay sau khi container healthy)
-- =============================================================================
-- SELECT course_code, course_name, semester, career_track FROM courses ORDER BY semester, course_code;
-- SELECT course_code, prerequisite_code, relation_type, depth
--   FROM v_course_prerequisite_closure WHERE course_code = 'INT3201' ORDER BY depth;
-- SELECT course_code, course_name, missing_prereq_codes, recommended_previous
--   FROM fn_student_eligible_courses('cccccccc-cccc-cccc-cccc-cccccccccccc')
--   ORDER BY semester, course_code;
-- SELECT course_code FROM fn_student_eligible_courses('11111111-1111-1111-1111-111111111111'); -- INT2204
-- SELECT course_code FROM fn_student_eligible_courses('22222222-2222-2222-2222-222222222222'); -- INT3101
-- SELECT course_code FROM fn_student_eligible_courses('33333333-3333-3333-3333-333333333333'); -- HK2

-- =============================================================================
-- 9. SEED — persona demo SV_WEB / SV_AI / SV_NEW (PR6)
-- Same rows as migrations/005_seed_demo_personas.sql. Password Pass123.
-- Hash identical to sv01.
-- =============================================================================

INSERT INTO users (id, email, hashed_password, full_name, role, student_code, department, is_active)
VALUES
    (
        '11111111-1111-1111-1111-111111111111',
        'svweb@eaut.edu.vn',
        '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0',
        'Trần Minh Quân',
        'student',
        'SVWEB',
        'Khoa CNTT',
        TRUE
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        'svai@eaut.edu.vn',
        '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0',
        'Đặng Thu Hà',
        'student',
        'SVAI',
        'Khoa CNTT',
        TRUE
    ),
    (
        '33333333-3333-3333-3333-333333333333',
        'svnew@eaut.edu.vn',
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

-- =============================================================================
-- 10. SEED — Dữ liệu mẫu toàn diện CNTT (K21 - K24, môn học HK1-HK8, bảng điểm, tài liệu)
-- Đồng bộ từ migrations/006_seed_comprehensive_data.sql
-- =============================================================================

INSERT INTO courses (
    course_code, course_name, credits, theory_hours, practice_hours,
    semester, is_mandatory, career_track, description
) VALUES
    ('INT1105', 'Giải tích cho CNTT', 3, 45, 0, 1, TRUE, 'GENERAL',
     'Giới hạn, đạo hàm, vi phân, tích phân và chuỗi số — nền tảng toán học cho giải thuật và tính toán khoa học.'),
    ('INT1106', 'Xác suất thống kê ứng dụng', 3, 45, 0, 2, TRUE, 'GENERAL',
     'Biến ngẫu nhiên, phân phối xác suất, ước lượng tham số, kiểm định giả thuyết và hồi quy tuyến tính.'),
    ('INT2205', 'Khai phá dữ liệu', 3, 30, 30, 4, FALSE, 'DATA',
     'Tiền xử lý dữ liệu, khai phá tập phổ biến, luật kết hợp, phân loại, gom cụm dữ liệu quy mô lớn.'),
    ('INT2206', 'Kiểm thử và đảm bảo chất lượng phần mềm', 3, 30, 30, 4, FALSE, 'SOFTWARE',
     'Kỹ thuật kiểm thử hộp đen, hộp trắng, Unit Test, Test tự động với Selenium/Jest, quản trị lỗi và chuẩn chất lượng phần mềm.'),
    ('INT2207', 'Quản trị mạng và hệ thống', 3, 30, 30, 4, FALSE, 'NETWORK',
     'Cài đặt, cấu hình Linux/Windows Server, DNS, DHCP, Web Server, chính sách bảo mật máy chủ, backup và monitor.'),
    ('INT3106', 'Hệ quản trị cơ sở dữ liệu nâng cao', 3, 30, 30, 5, FALSE, 'DATA',
     'Tối ưu hóa câu truy vấn, cơ chế Index, Transaction isolation, cơ sở dữ liệu phân tán và NoSQL (MongoDB, Redis).'),
    ('INT3107', 'Kiến trúc và thiết kế phần mềm', 3, 30, 30, 5, FALSE, 'SOFTWARE',
     'Mẫu thiết kế Design Patterns, kiến trúc Microservices, Clean Architecture, Domain-Driven Design và Event-Driven.'),
    ('INT3108', 'Phát triển ứng dụng di động', 3, 30, 30, 5, FALSE, 'SOFTWARE',
     'Lập trình ứng dụng mobile đa nền tảng Flutter/React Native, giao tiếp REST API, quản lý State và cơ sở dữ liệu cục bộ.'),
    ('INT3203', 'Kỹ thuật dữ liệu lớn', 3, 30, 30, 6, FALSE, 'DATA',
     'Hệ sinh thái Apache Hadoop, HDFS, MapReduce, Apache Spark xử lý dữ liệu lớn trong bộ nhớ và Apache Kafka stream data.'),
    ('INT3204', 'An toàn mạng không dây và di động', 3, 30, 30, 6, FALSE, 'SECURITY',
     'Bảo mật sóng vô tuyến, WPA2/WPA3, phân tích gói tin không dây, bảo mật mạng 4G/5G và thiết bị IoT.'),
    ('INT3205', 'Thị giác máy tính', 3, 30, 30, 6, FALSE, 'AI',
     'Xử lý ảnh số, phát hiện cạnh, trích xuất đặc trưng, phân loại ảnh bằng CNN, nhận diện vật thể YOLO bằng OpenCV và PyTorch.'),
    ('INT3206', 'Phát triển phần mềm an toàn', 3, 30, 30, 6, FALSE, 'SECURITY',
     'Phòng chống OWASP Top 10, phân tích mã nguồn tĩnh (SAST), quy trình DevSecOps và kiểm thử bảo mật ứng dụng.'),
    ('INT4101', 'Thực tập tốt nghiệp doanh nghiệp', 3, 0, 90, 7, TRUE, 'GENERAL',
     'Thực tập trực tiếp tại các công ty/doanh nghiệp công nghệ trong 8-12 tuần, tham gia dự án thực tế và viết báo cáo tốt nghiệp.'),
    ('INT4102', 'Quản lý dự án CNTT', 3, 45, 0, 7, TRUE, 'SOFTWARE',
     'Mô hình phát triển Agile/Scrum, lập kế hoạch tiến độ, ước lượng chi phí, quản lý rủi ro dự án phần mềm.'),
    ('INT4103', 'Chuyên đề công nghệ mới và khởi nghiệp số', 3, 45, 0, 7, FALSE, 'GENERAL',
     'Tìm hiểu Generative AI, Blockchain, Web3, xây dựng sản phẩm tối thiểu (MVP) và kế hoạch khởi nghiệp công nghệ.'),
    ('INT4104', 'DevOps và Tự động hóa hạ tầng', 3, 30, 30, 7, FALSE, 'NETWORK',
     'Tự động hóa CI/CD với GitHub Actions, Quản lý hạ tầng bằng mã (IaC) Terraform/Ansible, giám sát hạ tầng Prometheus/Grafana.'),
    ('INT4105', 'Trực quan hóa dữ liệu và BI', 3, 30, 30, 7, FALSE, 'DATA',
     'Xây dựng báo cáo phân tích kinh doanh thông minh với PowerBI, Tableau, Data Mart, mô hình dữ liệu sao (Star Schema).'),
    ('INT4201', 'Khóa luận tốt nghiệp', 6, 0, 180, 8, FALSE, 'GENERAL',
     'Thực hiện đề tài nghiên cứu hoặc phát triển giải pháp hệ thống chuyên sâu dưới sự hướng dẫn của giảng viên và bảo vệ trước hội đồng khoa.'),
    ('INT4202', 'Chuyên đề tốt nghiệp 1 - AI & BigData ứng dụng', 3, 30, 30, 8, FALSE, 'AI',
     'Học phần thay thế khóa luận tốt nghiệp định hướng Trí tuệ nhân tạo và Phân tích dữ liệu lớn.'),
    ('INT4203', 'Chuyên đề tốt nghiệp 2 - Hệ thống phân tán và Cloud', 3, 30, 30, 8, FALSE, 'SOFTWARE',
     'Học phần thay thế khóa luận tốt nghiệp định hướng Hệ thống phân tán và Kỹ thuật phần mềm đám mây.')
ON CONFLICT (course_code) DO NOTHING;

INSERT INTO course_prerequisites (course_id, prerequisite_course_id, relation_type)
SELECT c.id, p.id, rel.relation_type
FROM (VALUES
    ('INT1106', 'INT1105', 'PREVIOUS'),
    ('INT2205', 'INT1202', 'PREREQUISITE'),
    ('INT2205', 'INT1201', 'PREVIOUS'),
    ('INT2206', 'INT1204', 'PREREQUISITE'),
    ('INT2207', 'INT2102', 'PREREQUISITE'),
    ('INT3106', 'INT1202', 'PREREQUISITE'),
    ('INT3107', 'INT2201', 'PREREQUISITE'),
    ('INT3108', 'INT1204', 'PREREQUISITE'),
    ('INT3108', 'INT2104', 'PREVIOUS'),
    ('INT3203', 'INT1202', 'PREREQUISITE'),
    ('INT3203', 'INT3105', 'PREREQUISITE'),
    ('INT3204', 'INT3103', 'PREREQUISITE'),
    ('INT3205', 'INT3101', 'PREREQUISITE'),
    ('INT3205', 'INT1103', 'PREVIOUS'),
    ('INT3206', 'INT2203', 'PREREQUISITE'),
    ('INT3206', 'INT2201', 'PREVIOUS'),
    ('INT4101', 'INT3202', 'PREREQUISITE'),
    ('INT4101', 'INT2201', 'PREVIOUS'),
    ('INT4102', 'INT2201', 'PREREQUISITE'),
    ('INT4104', 'INT3105', 'PREREQUISITE'),
    ('INT4105', 'INT2205', 'PREREQUISITE'),
    ('INT4201', 'INT4101', 'PREREQUISITE'),
    ('INT4201', 'INT3202', 'PREREQUISITE'),
    ('INT4202', 'INT4101', 'PREREQUISITE'),
    ('INT4202', 'INT3101', 'PREREQUISITE'),
    ('INT4203', 'INT4101', 'PREREQUISITE'),
    ('INT4203', 'INT3105', 'PREREQUISITE')
) AS rel (course_code, prereq_code, relation_type)
JOIN courses c ON c.course_code = rel.course_code
JOIN courses p ON p.course_code = rel.prereq_code
ON CONFLICT (course_id, prerequisite_course_id, relation_type) DO NOTHING;

INSERT INTO users (id, email, hashed_password, full_name, role, student_code, department, is_active)
VALUES
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2', 'gv_advisor@eaut.edu.vn', '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0', 'PGS.TS Trần Văn Hùng', 'teacher', NULL, 'Khoa CNTT', TRUE),
    ('44444444-2401-4444-4444-000000000001', 'sv24_top@eaut.edu.vn', '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0', 'Hoàng Minh Đức', 'student', '20240101', 'Khoa CNTT', TRUE),
    ('44444444-2402-4444-4444-000000000002', 'sv24_warn@eaut.edu.vn', '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0', 'Lê Quốc Tuấn', 'student', '20240102', 'Khoa CNTT', TRUE),
    ('44444444-2301-4444-4444-000000000003', 'sv23_soft@eaut.edu.vn', '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0', 'Đỗ Phương Linh', 'student', '20230201', 'Khoa CNTT', TRUE),
    ('44444444-2302-4444-4444-000000000004', 'sv23_net@eaut.edu.vn', '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0', 'Nguyễn Hải Nam', 'student', '20230202', 'Khoa CNTT', TRUE),
    ('44444444-2303-4444-4444-000000000005', 'sv23_avg@eaut.edu.vn', '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0', 'Phạm Ngọc Thảo', 'student', '20230203', 'Khoa CNTT', TRUE),
    ('44444444-2201-4444-4444-000000000006', 'sv22_data@eaut.edu.vn', '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0', 'Trần Gia Huy', 'student', '20220301', 'Khoa CNTT', TRUE),
    ('44444444-2202-4444-4444-000000000007', 'sv22_warn@eaut.edu.vn', '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0', 'Bùi Tiến Dũng', 'student', '20220302', 'Khoa CNTT', TRUE),
    ('44444444-2203-4444-4444-000000000008', 'sv22_web@eaut.edu.vn', '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0', 'Vũ Mai Phương', 'student', '20220303', 'Khoa CNTT', TRUE),
    ('44444444-2101-4444-4444-000000000009', 'sv21_top@eaut.edu.vn', '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0', 'Nguyễn Khắc Hưng', 'student', '20210401', 'Khoa CNTT', TRUE),
    ('44444444-2102-4444-4444-000000000010', 'sv21_delay@eaut.edu.vn', '$pbkdf2-sha256$29000$nXgoJqKtQ46tAr7HNP03Qw$FQzXG8NwWKQCHTLFv4EMddCslaua8NRy5wEJUCB0Je0', 'Chu Thanh Tùng', 'student', '20210402', 'Khoa CNTT', TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r ON r.code = u.role
WHERE u.id IN (
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2'::UUID,
    '44444444-2401-4444-4444-000000000001'::UUID,
    '44444444-2402-4444-4444-000000000002'::UUID,
    '44444444-2301-4444-4444-000000000003'::UUID,
    '44444444-2302-4444-4444-000000000004'::UUID,
    '44444444-2303-4444-4444-000000000005'::UUID,
    '44444444-2201-4444-4444-000000000006'::UUID,
    '44444444-2202-4444-4444-000000000007'::UUID,
    '44444444-2203-4444-4444-000000000008'::UUID,
    '44444444-2101-4444-4444-000000000009'::UUID,
    '44444444-2102-4444-4444-000000000010'::UUID
)
ON CONFLICT (user_id, role_id) DO NOTHING;

-- Bảng điểm K24 Tân SV xuất sắc
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT '44444444-2401-4444-4444-000000000001'::UUID, c.id, rec.status, rec.grade, rec.semester_taken, rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED',      9.50, '2024-1', 1),
    ('INT1102', 'PASSED',      9.00, '2024-1', 1),
    ('INT1103', 'PASSED',      9.00, '2024-1', 1),
    ('INT1104', 'PASSED',      9.50, '2024-1', 1),
    ('INT1105', 'PASSED',      8.50, '2024-1', 1),
    ('INT1201', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT1202', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT1203', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT1204', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT1106', 'IN_PROGRESS', NULL, '2024-2', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- Bảng điểm K24 Trượt môn nền tảng
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT '44444444-2402-4444-4444-000000000002'::UUID, c.id, rec.status, rec.grade, rec.semester_taken, rec.attempt_count
FROM (VALUES
    ('INT1101', 'FAILED',      3.00, '2024-1', 1),
    ('INT1102', 'FAILED',      3.50, '2024-1', 1),
    ('INT1103', 'PASSED',      5.50, '2024-1', 1),
    ('INT1104', 'PASSED',      6.00, '2024-1', 1),
    ('INT1105', 'FAILED',      3.50, '2024-1', 1),
    ('INT1203', 'IN_PROGRESS', NULL, '2024-2', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- Bảng điểm K23 Software
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT '44444444-2301-4444-4444-000000000003'::UUID, c.id, rec.status, rec.grade, rec.semester_taken, rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED',      9.00, '2023-1', 1),
    ('INT1102', 'PASSED',      8.00, '2023-1', 1),
    ('INT1103', 'PASSED',      7.50, '2023-1', 1),
    ('INT1104', 'PASSED',      8.50, '2023-1', 1),
    ('INT1105', 'PASSED',      8.00, '2023-1', 1),
    ('INT1201', 'PASSED',      8.50, '2023-2', 1),
    ('INT1202', 'PASSED',      8.00, '2023-2', 1),
    ('INT1203', 'PASSED',      7.50, '2023-2', 1),
    ('INT1204', 'PASSED',      9.00, '2023-2', 1),
    ('INT1106', 'PASSED',      8.00, '2023-2', 1),
    ('INT2101', 'PASSED',      8.00, '2024-1', 1),
    ('INT2102', 'PASSED',      8.00, '2024-1', 1),
    ('INT2103', 'PASSED',      8.50, '2024-1', 1),
    ('INT2104', 'PASSED',      8.50, '2024-1', 1),
    ('INT2201', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT2206', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT2204', 'IN_PROGRESS', NULL, '2024-2', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- Bảng điểm K23 Network/Security
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT '44444444-2302-4444-4444-000000000004'::UUID, c.id, rec.status, rec.grade, rec.semester_taken, rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED',      7.50, '2023-1', 1),
    ('INT1102', 'PASSED',      8.00, '2023-1', 1),
    ('INT1103', 'PASSED',      7.00, '2023-1', 1),
    ('INT1104', 'PASSED',      8.00, '2023-1', 1),
    ('INT1105', 'PASSED',      7.00, '2023-1', 1),
    ('INT1201', 'PASSED',      7.50, '2023-2', 1),
    ('INT1202', 'PASSED',      7.50, '2023-2', 1),
    ('INT1203', 'PASSED',      8.50, '2023-2', 1),
    ('INT1204', 'PASSED',      7.00, '2023-2', 1),
    ('INT1106', 'PASSED',      7.50, '2023-2', 1),
    ('INT2101', 'PASSED',      8.00, '2024-1', 1),
    ('INT2102', 'PASSED',      9.00, '2024-1', 1),
    ('INT2103', 'PASSED',      7.00, '2024-1', 1),
    ('INT2104', 'PASSED',      7.00, '2024-1', 1),
    ('INT2203', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT2207', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT2201', 'IN_PROGRESS', NULL, '2024-2', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- Bảng điểm K23 Trung bình khá
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT '44444444-2303-4444-4444-000000000005'::UUID, c.id, rec.status, rec.grade, rec.semester_taken, rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED',      6.00, '2023-1', 1),
    ('INT1102', 'PASSED',      5.50, '2023-1', 1),
    ('INT1103', 'PASSED',      6.00, '2023-1', 1),
    ('INT1104', 'PASSED',      7.00, '2023-1', 1),
    ('INT1105', 'PASSED',      5.50, '2023-1', 1),
    ('INT1201', 'PASSED',      6.00, '2023-2', 1),
    ('INT1202', 'PASSED',      6.50, '2023-2', 1),
    ('INT1203', 'PASSED',      5.50, '2023-2', 1),
    ('INT1204', 'PASSED',      6.50, '2023-2', 1),
    ('INT1106', 'PASSED',      6.00, '2023-2', 1),
    ('INT2101', 'PASSED',      6.00, '2024-1', 1),
    ('INT2102', 'PASSED',      6.50, '2024-1', 1),
    ('INT2103', 'PASSED',      6.00, '2024-1', 1),
    ('INT2104', 'PASSED',      6.50, '2024-1', 1),
    ('INT2201', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT2202', 'IN_PROGRESS', NULL, '2024-2', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- Bảng điểm K22 Data & AI
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT '44444444-2201-4444-4444-000000000006'::UUID, c.id, rec.status, rec.grade, rec.semester_taken, rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED',      8.50, '2022-1', 1),
    ('INT1102', 'PASSED',      8.00, '2022-1', 1),
    ('INT1103', 'PASSED',      9.00, '2022-1', 1),
    ('INT1104', 'PASSED',      8.50, '2022-1', 1),
    ('INT1105', 'PASSED',      8.50, '2022-1', 1),
    ('INT1201', 'PASSED',      8.50, '2022-2', 1),
    ('INT1202', 'PASSED',      9.00, '2022-2', 1),
    ('INT1203', 'PASSED',      7.50, '2022-2', 1),
    ('INT1204', 'PASSED',      8.00, '2022-2', 1),
    ('INT1106', 'PASSED',      9.00, '2022-2', 1),
    ('INT2101', 'PASSED',      8.00, '2023-1', 1),
    ('INT2102', 'PASSED',      8.00, '2023-1', 1),
    ('INT2103', 'PASSED',      8.00, '2023-1', 1),
    ('INT2104', 'PASSED',      8.00, '2023-1', 1),
    ('INT2201', 'PASSED',      8.00, '2023-2', 1),
    ('INT2202', 'PASSED',      9.00, '2023-2', 1),
    ('INT2203', 'PASSED',      8.00, '2023-2', 1),
    ('INT2205', 'PASSED',      9.00, '2023-2', 1),
    ('INT3101', 'PASSED',      9.00, '2024-1', 1),
    ('INT3102', 'PASSED',      8.50, '2024-1', 1),
    ('INT3105', 'PASSED',      8.50, '2024-1', 1),
    ('INT3106', 'PASSED',      9.00, '2024-1', 1),
    ('INT3201', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT3203', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT3205', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT3202', 'IN_PROGRESS', NULL, '2024-2', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- Bảng điểm K22 Cảnh báo học tập mức 2
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT '44444444-2202-4444-4444-000000000007'::UUID, c.id, rec.status, rec.grade, rec.semester_taken, rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED',      6.00, '2022-1', 1),
    ('INT1102', 'PASSED',      5.00, '2022-1', 1),
    ('INT1103', 'PASSED',      5.50, '2022-1', 1),
    ('INT1104', 'PASSED',      6.50, '2022-1', 1),
    ('INT1105', 'FAILED',      3.50, '2022-1', 1),
    ('INT1201', 'PASSED',      5.00, '2022-2', 1),
    ('INT1202', 'FAILED',      3.50, '2022-2', 1),
    ('INT1203', 'PASSED',      5.00, '2022-2', 1),
    ('INT1204', 'PASSED',      5.50, '2022-2', 1),
    ('INT1106', 'FAILED',      3.00, '2022-2', 1),
    ('INT2101', 'FAILED',      3.00, '2023-1', 1),
    ('INT2102', 'FAILED',      3.50, '2023-1', 1),
    ('INT2103', 'FAILED',      3.00, '2023-1', 1),
    ('INT2104', 'PASSED',      5.00, '2023-1', 1),
    ('INT2201', 'FAILED',      3.00, '2023-2', 1),
    ('INT2202', 'FAILED',      3.50, '2023-2', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- Bảng điểm K22 Web Fullstack & Cloud
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT '44444444-2203-4444-4444-000000000008'::UUID, c.id, rec.status, rec.grade, rec.semester_taken, rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED',      8.00, '2022-1', 1),
    ('INT1102', 'PASSED',      7.50, '2022-1', 1),
    ('INT1103', 'PASSED',      8.00, '2022-1', 1),
    ('INT1104', 'PASSED',      8.50, '2022-1', 1),
    ('INT1105', 'PASSED',      7.50, '2022-1', 1),
    ('INT1201', 'PASSED',      8.00, '2022-2', 1),
    ('INT1202', 'PASSED',      8.50, '2022-2', 1),
    ('INT1203', 'PASSED',      7.50, '2022-2', 1),
    ('INT1204', 'PASSED',      9.00, '2022-2', 1),
    ('INT1106', 'PASSED',      8.00, '2022-2', 1),
    ('INT2101', 'PASSED',      8.00, '2023-1', 1),
    ('INT2102', 'PASSED',      8.00, '2023-1', 1),
    ('INT2103', 'PASSED',      8.50, '2023-1', 1),
    ('INT2104', 'PASSED',      9.00, '2023-1', 1),
    ('INT2201', 'PASSED',      8.50, '2023-2', 1),
    ('INT2203', 'PASSED',      8.00, '2023-2', 1),
    ('INT2204', 'PASSED',      9.50, '2023-2', 1),
    ('INT3104', 'PASSED',      9.00, '2024-1', 1),
    ('INT3105', 'PASSED',      8.50, '2024-1', 1),
    ('INT3202', 'IN_PROGRESS', NULL, '2024-2', 1),
    ('INT4104', 'IN_PROGRESS', NULL, '2024-2', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- Bảng điểm K21 Năm 4 Xuất sắc
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT '44444444-2101-4444-4444-000000000009'::UUID, c.id, rec.status, rec.grade, rec.semester_taken, rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED',      9.00, '2021-1', 1),
    ('INT1102', 'PASSED',      8.50, '2021-1', 1),
    ('INT1103', 'PASSED',      9.00, '2021-1', 1),
    ('INT1104', 'PASSED',      9.50, '2021-1', 1),
    ('INT1105', 'PASSED',      8.50, '2021-1', 1),
    ('INT1201', 'PASSED',      9.00, '2021-2', 1),
    ('INT1202', 'PASSED',      9.00, '2021-2', 1),
    ('INT1203', 'PASSED',      8.00, '2021-2', 1),
    ('INT1204', 'PASSED',      9.50, '2021-2', 1),
    ('INT1106', 'PASSED',      8.50, '2021-2', 1),
    ('INT2101', 'PASSED',      8.50, '2022-1', 1),
    ('INT2102', 'PASSED',      8.50, '2022-1', 1),
    ('INT2103', 'PASSED',      9.00, '2022-1', 1),
    ('INT2104', 'PASSED',      9.00, '2022-1', 1),
    ('INT2201', 'PASSED',      9.00, '2022-2', 1),
    ('INT2202', 'PASSED',      8.50, '2022-2', 1),
    ('INT2203', 'PASSED',      8.50, '2022-2', 1),
    ('INT2204', 'PASSED',      9.00, '2022-2', 1),
    ('INT2206', 'PASSED',      9.00, '2022-2', 1),
    ('INT3101', 'PASSED',      8.50, '2023-1', 1),
    ('INT3104', 'PASSED',      9.00, '2023-1', 1),
    ('INT3105', 'PASSED',      9.00, '2023-1', 1),
    ('INT3107', 'PASSED',      9.00, '2023-1', 1),
    ('INT3201', 'PASSED',      8.50, '2023-2', 1),
    ('INT3202', 'PASSED',      9.50, '2023-2', 1),
    ('INT4101', 'PASSED',     10.00, '2024-1', 1),
    ('INT4102', 'PASSED',      9.00, '2024-1', 1),
    ('INT4103', 'PASSED',      9.00, '2024-1', 1),
    ('INT4104', 'PASSED',      9.00, '2024-1', 1),
    ('INT4201', 'IN_PROGRESS', NULL, '2024-2', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- Bảng điểm K21 Chậm tiến độ do nợ INT1203
INSERT INTO student_records (user_id, course_id, status, grade, semester_taken, attempt_count)
SELECT '44444444-2102-4444-4444-000000000010'::UUID, c.id, rec.status, rec.grade, rec.semester_taken, rec.attempt_count
FROM (VALUES
    ('INT1101', 'PASSED',      7.00, '2021-1', 1),
    ('INT1102', 'PASSED',      6.50, '2021-1', 1),
    ('INT1103', 'PASSED',      6.00, '2021-1', 1),
    ('INT1104', 'PASSED',      7.50, '2021-1', 1),
    ('INT1105', 'PASSED',      6.00, '2021-1', 1),
    ('INT1201', 'PASSED',      7.00, '2021-2', 1),
    ('INT1202', 'PASSED',      7.50, '2021-2', 1),
    ('INT1203', 'FAILED',      3.50, '2021-2', 1),
    ('INT1204', 'PASSED',      8.00, '2021-2', 1),
    ('INT1106', 'PASSED',      6.50, '2021-2', 1),
    ('INT2102', 'PASSED',      7.00, '2022-1', 1),
    ('INT2103', 'PASSED',      7.50, '2022-1', 1),
    ('INT2104', 'PASSED',      8.00, '2022-1', 1),
    ('INT2201', 'PASSED',      7.50, '2022-2', 1),
    ('INT2204', 'PASSED',      8.00, '2022-2', 1),
    ('INT2206', 'PASSED',      7.50, '2022-2', 1),
    ('INT3104', 'PASSED',      7.50, '2023-1', 1),
    ('INT3108', 'PASSED',      8.00, '2023-1', 1),
    ('INT3202', 'PASSED',      8.00, '2023-2', 1),
    ('INT4101', 'PASSED',      8.00, '2024-1', 1),
    ('INT4102', 'PASSED',      7.50, '2024-1', 1)
) AS rec (course_code, status, grade, semester_taken, attempt_count)
JOIN courses c ON c.course_code = rec.course_code
ON CONFLICT (user_id, course_id) DO NOTHING;

-- Tài liệu học tập cho các môn CNTT
INSERT INTO learning_materials (course_id, title, material_type, file_url)
SELECT c.id, m.title, m.material_type, m.file_url
FROM (VALUES
    ('INT1102', 'Đề cương chi tiết — Toán rời rạc', 'SYLLABUS', '/materials/INT1102/syllabus.pdf'),
    ('INT1102', 'Slide bài giảng Lý thuyết Đồ thị và Logic mệnh đề', 'SLIDE', '/materials/INT1102/slides.pdf'),
    ('INT1102', 'Giáo trình Toán rời rạc ứng dụng trong Tin học', 'TEXTBOOK', '/materials/INT1102/textbook.pdf'),
    ('INT1102', 'Đề thi trắc nghiệm & tự luận các năm', 'EXAM', '/materials/INT1102/exam.pdf'),
    ('INT1103', 'Đề cương chi tiết — Đại số tuyến tính', 'SYLLABUS', '/materials/INT1103/syllabus.pdf'),
    ('INT1103', 'Slide Không gian vector và Trị riêng, Vector riêng', 'SLIDE', '/materials/INT1103/slides.pdf'),
    ('INT1201', 'Giáo trình Cấu trúc dữ liệu và Giải thuật — ThS. Lê Hải Đăng', 'TEXTBOOK', '/materials/INT1201/textbook.pdf'),
    ('INT1201', 'Ngân hàng bài tập lớn & Đề thi kết thúc học phần', 'EXAM', '/materials/INT1201/exam.pdf'),
    ('INT1204', 'Đề cương chi tiết — Lập trình hướng đối tượng (Java/C#)', 'SYLLABUS', '/materials/INT1204/syllabus.pdf'),
    ('INT1204', 'Slide Nguyên lý SOLID và 4 tính chất OOP', 'SLIDE', '/materials/INT1204/slides.pdf'),
    ('INT1204', 'Giáo trình Lập trình Hướng đối tượng chuẩn Khoa CNTT', 'TEXTBOOK', '/materials/INT1204/textbook.pdf'),
    ('INT1204', 'Ngân hàng đề thi thực hành OOP Java', 'EXAM', '/materials/INT1204/exam.pdf'),
    ('INT2101', 'Đề cương chi tiết — Hệ điều hành', 'SYLLABUS', '/materials/INT2101/syllabus.pdf'),
    ('INT2101', 'Slide Quản lý tiến trình, luồng và đồng bộ hóa (Semaphore/Mutex)', 'SLIDE', '/materials/INT2101/slides.pdf'),
    ('INT2101', 'Giáo trình Hệ điều hành hiện đại (Operating Systems Concepts)', 'TEXTBOOK', '/materials/INT2101/textbook.pdf'),
    ('INT2102', 'Đề cương chi tiết — Mạng máy tính', 'SYLLABUS', '/materials/INT2102/syllabus.pdf'),
    ('INT2102', 'Slide Mô hình OSI, TCP/IP và Giao thức Định tuyến', 'SLIDE', '/materials/INT2102/slides.pdf'),
    ('INT2102', 'Giáo trình Mạng máy tính căn bản & nâng cao', 'TEXTBOOK', '/materials/INT2102/textbook.pdf'),
    ('INT2102', 'Tập bài tập phân tích gói tin với Wireshark', 'EXAM', '/materials/INT2102/exam.pdf'),
    ('INT2201', 'Đề cương chi tiết — Công nghệ phần mềm', 'SYLLABUS', '/materials/INT2201/syllabus.pdf'),
    ('INT2201', 'Slide Quy trình phát triển phần mềm Agile/Scrum và CI/CD', 'SLIDE', '/materials/INT2201/slides.pdf'),
    ('INT2201', 'Giáo trình Software Engineering — Pressman', 'TEXTBOOK', '/materials/INT2201/textbook.pdf'),
    ('INT2203', 'Đề cương chi tiết — An toàn thông tin', 'SYLLABUS', '/materials/INT2203/syllabus.pdf'),
    ('INT2203', 'Slide Mật mã học đối xứng, bất đối xứng và Chữ ký số', 'SLIDE', '/materials/INT2203/slides.pdf'),
    ('INT2203', 'Giáo trình An toàn & An ninh thông tin', 'TEXTBOOK', '/materials/INT2203/textbook.pdf'),
    ('INT2204', 'Đề cương chi tiết — Phát triển ứng dụng Web', 'SYLLABUS', '/materials/INT2204/syllabus.pdf'),
    ('INT2204', 'Slide Xây dựng RESTful API và Xác thực JWT/OAuth2', 'SLIDE', '/materials/INT2204/slides.pdf'),
    ('INT2204', 'Ngân hàng bài tập lớn phát triển Web Fullstack', 'EXAM', '/materials/INT2204/exam.pdf'),
    ('INT3101', 'Đề cương chi tiết — Học máy (Machine Learning)', 'SYLLABUS', '/materials/INT3101/syllabus.pdf'),
    ('INT3101', 'Slide Hồi quy tuyến tính, Logistic, SVM và Random Forest', 'SLIDE', '/materials/INT3101/slides.pdf'),
    ('INT3101', 'Giáo trình Machine Learning cơ bản — Vũ Hữu Tiệp', 'TEXTBOOK', '/materials/INT3101/textbook.pdf'),
    ('INT3104', 'Đề cương chi tiết — Phát triển Web nâng cao (SPA, Next.js)', 'SYLLABUS', '/materials/INT3104/syllabus.pdf'),
    ('INT3104', 'Slide Server-Side Rendering (SSR), Micro-frontend & Caching', 'SLIDE', '/materials/INT3104/slides.pdf'),
    ('INT3105', 'Đề cương chi tiết — Điện toán đám mây', 'SYLLABUS', '/materials/INT3105/syllabus.pdf'),
    ('INT3105', 'Slide Docker Containerization và Kubernetes Orchestration', 'SLIDE', '/materials/INT3105/slides.pdf'),
    ('INT3105', 'Tài liệu hướng dẫn thực hành AWS Cloud Practitioner', 'TEXTBOOK', '/materials/INT3105/textbook.pdf'),
    ('INT3201', 'Đề cương chi tiết — Deep Learning', 'SYLLABUS', '/materials/INT3201/syllabus.pdf'),
    ('INT3201', 'Slide Mạng nơ-ron tích chập (CNN) và Transformer Architecture', 'SLIDE', '/materials/INT3201/slides.pdf'),
    ('INT3201', 'Giáo trình Deep Learning — Ian Goodfellow', 'TEXTBOOK', '/materials/INT3201/textbook.pdf'),
    ('INT3202', 'Quy định và Hướng dẫn thực hiện Đồ án chuyên ngành CNTT', 'SYLLABUS', '/materials/INT3202/syllabus.pdf'),
    ('INT3202', 'Biểu mẫu đề cương, báo cáo tiến độ và tiêu chí chấm điểm', 'SLIDE', '/materials/INT3202/slides.pdf'),
    ('INT4101', 'Quy định thực tập tốt nghiệp và hướng dẫn liên hệ doanh nghiệp', 'SYLLABUS', '/materials/INT4101/syllabus.pdf'),
    ('INT4101', 'Mẫu nhật ký thực tập và phiếu đánh giá của doanh nghiệp', 'SLIDE', '/materials/INT4101/slides.pdf'),
    ('INT4201', 'Quy chế xét điều kiện làm Khóa luận tốt nghiệp và hướng dẫn bảo vệ', 'SYLLABUS', '/materials/INT4201/syllabus.pdf'),
    ('INT4201', 'Mẫu template LaTeX / Word chuẩn luận văn tốt nghiệp Khoa CNTT', 'TEXTBOOK', '/materials/INT4201/textbook.pdf')
) AS m (course_code, title, material_type, file_url)
JOIN courses c ON c.course_code = m.course_code
ON CONFLICT DO NOTHING;

