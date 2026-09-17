"""Rules-first intent classifier (no LLM)."""
from app.services.intent_classifier import ChatIntent, IntentClassifier


classifier = IntentClassifier()


def test_tien_quyet_is_course_advice():
    result = classifier.classify("tiên quyết của INT2104 là gì?")
    assert result.intent == ChatIntent.COURSE_ADVICE
    assert result.course_codes == ["INT2104"]


def test_slide_int2104_is_material_qa():
    result = classifier.classify("slide INT2104 tuần 3 ở đâu?")
    assert result.intent == ChatIntent.MATERIAL_QA
    assert result.course_codes == ["INT2104"]


def test_de_cuong_with_d_stroke_is_material_qa():
    result = classifier.classify("Đề cương INT2104 gồm những nội dung gì?")
    assert result.intent == ChatIntent.MATERIAL_QA
    assert result.course_codes == ["INT2104"]


def test_xin_chao_is_greeting():
    result = classifier.classify("xin chào")
    assert result.intent == ChatIntent.GREETING


def test_em_chao_co_is_greeting():
    result = classifier.classify("em chào cô")
    assert result.intent == ChatIntent.GREETING


def test_unmatched_defaults_to_course_advice():
    result = classifier.classify("Python là gì")
    assert result.intent == ChatIntent.COURSE_ADVICE
    assert result.career_track is None
    assert result.course_codes == []


def test_tai_lieu_by_course_name_is_material_qa():
    result = classifier.classify(
        "Tìm cho t tài liệu của môn cấu trúc dữ liệu và giải thuật"
    )
    assert result.intent == ChatIntent.MATERIAL_QA


def test_tinh_hinh_hoc_tap_is_course_advice():
    result = classifier.classify("Cho t bt tình hình học tập của t hiện tại được chứ")
    assert result.intent == ChatIntent.COURSE_ADVICE


def test_web_track_question_is_course_advice():
    result = classifier.classify(
        "E muốn theo đường dev web thì học kì này lên học những môn nào"
    )
    assert result.intent == ChatIntent.COURSE_ADVICE
    assert result.career_track == "WEB"
