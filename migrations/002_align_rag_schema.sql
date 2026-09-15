-- Additive RAG column delta for existing Postgres volumes.
-- Fresh installs get the same columns from init_db.sql.
-- Apply on an existing volume:
--   psql "postgresql://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot" -f migrations/002_align_rag_schema.sql

ALTER TABLE sessions
    ADD COLUMN IF NOT EXISTS parent_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS branch_message_index INTEGER,
    ADD COLUMN IF NOT EXISTS conversation_summary TEXT,
    ADD COLUMN IF NOT EXISTS chatbot_id UUID REFERENCES chatbots(id) ON DELETE SET NULL;

ALTER TABLE messages
    ADD COLUMN IF NOT EXISTS extra JSONB NOT NULL DEFAULT '{}'::JSONB;

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

ALTER TABLE learning_materials
    ADD COLUMN IF NOT EXISTS file_id UUID REFERENCES files(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS dataset_id UUID REFERENCES datasets(id) ON DELETE SET NULL;

-- Keep seed chatbot RAG-only until academic facts exist.
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
