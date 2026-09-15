-- PR3: enable AcademicFacts injection and restore advisor persona.
-- Fresh installs get the same values from init_db.sql.
-- Apply on an existing volume:
--   psql "postgresql://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot" -f migrations/004_enable_academic_facts.sql

UPDATE chatbots
SET config = jsonb_set(
    jsonb_set(config, '{system_prompt}',
      '"Bạn là Trợ lý Cố vấn Học tập & Tài liệu Khoa CNTT. Trả lời tiếng Việt, súc tích; liệt kê mã môn, tên môn và lý do. Chỉ dùng mã môn/tín chỉ/tiên quyết từ [AcademicFacts]."'::jsonb),
    '{no_context_behavior}', '"reject"'::jsonb
)
WHERE id = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee';

UPDATE system_settings
SET config = config || '{"academic_facts_enabled": true}'::jsonb
WHERE id = 'singleton';
