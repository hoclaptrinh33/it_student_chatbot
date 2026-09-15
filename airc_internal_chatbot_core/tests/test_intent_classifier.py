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


def test_default_intent_is_hybrid():
    result = classifier.classify("em chào cô")
    assert result.intent == ChatIntent.HYBRID
    assert result.career_track is None
    assert result.course_codes == []


def test_web_track_question_is_course_advice():
    result = classifier.classify(
        "E muốn theo đường dev web thì học kì này lên học những môn nào"
    )
    assert result.intent == ChatIntent.COURSE_ADVICE
    assert result.career_track == "WEB"
