import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://it_admin:it_chatbot_2026@localhost:5432/it_student_chatbot",
)
