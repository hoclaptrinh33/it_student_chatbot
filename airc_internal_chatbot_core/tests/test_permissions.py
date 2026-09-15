"""Strict Core role→permission matrix tests (no FastAPI/Qdrant import)."""
from app.models.auth import User, UserRole, Permission, user_has_permission


def _user(role: UserRole) -> User:
    return User(
        id="u1",
        user_id="u1",
        email=f"{role.value}@airc.edu.vn",
        full_name="Test",
        role=role,
        is_active=True,
    )


def test_student_can_chat():
    assert user_has_permission(_user(UserRole.STUDENT), Permission.CHAT_USE)


def test_student_cannot_view_analytics():
    assert not user_has_permission(_user(UserRole.STUDENT), Permission.ANALYTICS_VIEW)


def test_teacher_can_view_analytics():
    assert user_has_permission(_user(UserRole.TEACHER), Permission.ANALYTICS_VIEW)


def test_teacher_cannot_manage_any_chatbot():
    assert not user_has_permission(_user(UserRole.TEACHER), Permission.CHATBOTS_MANAGE_ANY)


def test_admin_has_all_permissions():
    assert user_has_permission(_user(UserRole.ADMIN), Permission.SYSTEM_MANAGE)
    assert user_has_permission(_user(UserRole.ADMIN), Permission.CHAT_USE)
    assert user_has_permission(_user(UserRole.ADMIN), Permission.COURSES_MANAGE)
    assert user_has_permission(_user(UserRole.ADMIN), Permission.RECORDS_UPDATE)


def test_student_academic_permissions():
    student = _user(UserRole.STUDENT)
    assert user_has_permission(student, Permission.COURSES_VIEW)
    assert user_has_permission(student, Permission.RECORDS_VIEW_OWN)
    assert user_has_permission(student, Permission.MATERIALS_VIEW)
    assert not user_has_permission(student, Permission.COURSES_MANAGE)
    assert not user_has_permission(student, Permission.RECORDS_UPDATE)
    assert not user_has_permission(student, Permission.RECORDS_VIEW_ANY)
    assert not user_has_permission(student, Permission.MATERIALS_MANAGE)


def test_teacher_can_update_records_but_not_manage_courses():
    teacher = _user(UserRole.TEACHER)
    assert user_has_permission(teacher, Permission.COURSES_VIEW)
    assert user_has_permission(teacher, Permission.RECORDS_VIEW_ANY)
    assert user_has_permission(teacher, Permission.RECORDS_UPDATE)
    assert user_has_permission(teacher, Permission.MATERIALS_MANAGE)
    assert not user_has_permission(teacher, Permission.COURSES_MANAGE)
    assert not user_has_permission(teacher, Permission.RECORDS_VIEW_OWN)
