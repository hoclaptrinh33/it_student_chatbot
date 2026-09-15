-- Additive academic permissions for existing Postgres volumes.
-- Fresh installs get the same rows from init_db.sql.
-- Apply on an existing volume:
--   psql "postgresql://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot" -f migrations/003_academic_permissions.sql

INSERT INTO permissions (code, name, resource, action, scope, is_system) VALUES
    ('courses:view',          'Xem môn học',             'courses',  'view',   NULL,    TRUE),
    ('courses:manage',        'Quản lý môn học',         'courses',  'manage', NULL,    TRUE),
    ('records:view:own',      'Xem bảng điểm của mình',  'records',  'view',   'own',   TRUE),
    ('records:view:any',      'Xem mọi bảng điểm',       'records',  'view',   'any',   TRUE),
    ('records:update',        'Cập nhật bảng điểm',      'records',  'update', NULL,    TRUE),
    ('materials:view',        'Xem tài liệu học tập',    'materials','view',   NULL,    TRUE),
    ('materials:manage',      'Quản lý tài liệu học tập','materials','manage', NULL,    TRUE)
ON CONFLICT (code) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON (
    (r.code = 'admin' AND p.code IN (
        'courses:view', 'courses:manage',
        'records:view:own', 'records:view:any', 'records:update',
        'materials:view', 'materials:manage'
    ))
    OR (r.code = 'teacher' AND p.code IN (
        'courses:view', 'records:view:any', 'records:update',
        'materials:view', 'materials:manage'
    ))
    OR (r.code = 'student' AND p.code IN (
        'courses:view', 'records:view:own', 'materials:view'
    ))
)
ON CONFLICT DO NOTHING;
