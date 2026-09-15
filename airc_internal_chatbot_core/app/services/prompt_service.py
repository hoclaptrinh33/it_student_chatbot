"""
Prompt Service - Xây dựng prompts cho RAG
Service này chịu trách nhiệm ghép nối câu hỏi, lịch sử chat và context thành một prompt hoàn chỉnh cho LLM.
"""
from typing import List, Dict, Any, Optional

ADVISOR_BAN_HALLUCINATION = (
    "Bạn là Trợ lý Cố vấn Học tập & Tài liệu Khoa CNTT.\n"
    "QUY TẮC BẮT BUỘC:\n"
    "1. Mã môn, số tín chỉ, tiên quyết, trạng thái PASSED/FAILED/IN_PROGRESS\n"
    "   CHỈ được lấy từ [AcademicFacts]. CẤM bịa hoặc dùng kiến thức chung.\n"
    "2. Nếu sinh viên nói đã qua một môn nhưng [AcademicFacts] không có PASSED\n"
    "   → tin bảng điểm, giải thích nhẹ nhàng, không tranh cãi.\n"
    "3. Tài liệu (slide/đề cương/giáo trình/đề) lấy từ [Knowledge] và PHẢI cite file.\n"
    "4. [AcademicFacts].empty_transcript = true → nói bảng điểm chưa được nhập,\n"
    "   không gợi ý như thể sinh viên đã hoàn thành HK bất kỳ.\n"
    "5. current_semester_source = UNKNOWN → không đoán học kỳ.\n"
    "6. Phân biệt PREREQUISITE (bắt buộc PASSED) và PREVIOUS (khuyến nghị).\n"
    "7. Trả lời tiếng Việt, súc tích, liệt kê mã môn + tên + lý do."
)


def render_academic_facts(academic_facts: Dict[str, Any]) -> str:
    """Fixed-text AcademicFacts block. Never dump raw JSON."""
    from app.services.academic_facts_service import AcademicFacts

    if isinstance(academic_facts, AcademicFacts):
        return academic_facts.render_text()
    facts = AcademicFacts(
        student_id=str(academic_facts.get("student_id") or ""),
        student_code=academic_facts.get("student_code"),
        full_name=academic_facts.get("full_name") or "",
        current_semester=academic_facts.get("current_semester"),
        current_semester_source=academic_facts.get("current_semester_source") or "UNKNOWN",
        empty_transcript=bool(academic_facts.get("empty_transcript")),
        records=list(academic_facts.get("records") or []),
        eligible_courses=list(academic_facts.get("eligible_courses") or []),
        blocked_sample=list(academic_facts.get("blocked_sample") or []),
        career_track_filter=academic_facts.get("career_track_filter"),
        mentioned_course_codes=list(academic_facts.get("mentioned_course_codes") or []),
        mentioned_prereqs=list(academic_facts.get("mentioned_prereqs") or []),
        in_progress=list(academic_facts.get("in_progress") or []),
        retake=list(academic_facts.get("retake") or []),
    )
    for row in facts.records:
        row.setdefault("course_name", row.get("name"))
    for row in facts.eligible_courses:
        row.setdefault("course_name", row.get("name"))
    for row in facts.blocked_sample:
        row.setdefault("course_name", row.get("name"))
    for row in facts.in_progress:
        row.setdefault("course_name", row.get("name"))
    for row in facts.retake:
        row.setdefault("course_name", row.get("name"))
    return facts.render_text()


class PromptService:
    """Service xây dựng và format prompts"""
    
    def build_prompt(
        self,
        question: str,
        grouped_results: List[Dict[str, Any]],
        history: Optional[List[Dict]] = None,
        max_chunk_chars: int = 1200,
        system_prompt: Optional[str] = None,
        conversation_summary: Optional[str] = None,
        academic_facts: Optional[dict] = None,
    ) -> str:
        """
        Xây dựng RAG prompt từ context đã retrieve được
        
        Args:
            question: Câu hỏi của người dùng
            grouped_results: Kết quả tìm kiếm (đã gom nhóm theo dataset)
            history: Lịch sử chat rút gọn (nếu có)
            max_chunk_chars: Số ký tự tối đa cho mỗi chunk (để tránh context quá dài)
            system_prompt: Prompt hệ thống tùy chỉnh (override default)
            conversation_summary: Tóm tắt ngữ cảnh cuộc hội thoại trước đó (nếu có)
        
        Returns:
            str: Prompt hoàn chỉnh để gửi cho LLM
        """
        # Lấy danh sách tên các dataset có trong kết quả
        dataset_names = [
            g.get("dataset_name")
            for g in grouped_results
            if g.get("dataset_name")
        ]
        
        lines: List[str] = []
        
        # Phần 1: System Instruction
        lines.append("Prompt Instruction:")
        lines.append("[Instruction]")

        if academic_facts is not None:
            # Runtime always prepends the ban-hallucination block; admin system_prompt cannot remove it.
            lines.append(ADVISOR_BAN_HALLUCINATION)
            if academic_facts.get("empty_transcript"):
                lines.append(
                    "\nempty_transcript=true: bảng điểm chưa có. Không suy ra môn đã học, "
                    "không bịa PASSED, không gợi ý như đã xong học kỳ nào."
                )
            if academic_facts.get("current_semester_source") == "UNKNOWN":
                lines.append("current_semester_source=UNKNOWN: không đoán học kỳ hiện tại.")
            if system_prompt:
                lines.append("\n" + system_prompt)
            lines.append(
                f"\nDatasets hiện có: {', '.join(dataset_names) if dataset_names else '(Chưa có)'}"
            )
        elif system_prompt:
             # Use custom system prompt
             lines.append(system_prompt)
        else:
            # Default System Prompt - STRICT RAG MODE
            lines.append(
                "Bạn là Chatbot RAG (Retrieval-Augmented Generation) nội bộ của AIRC. "
                "NHIỆM VỤ: Trả lời câu hỏi DỰA TRÊN TÀI LIỆU được cung cấp trong phần [Knowledge]."
            )
            lines.append(
                "\n🔒 QUY TẮC BẮT BUỘC:\n"
                "1. CHỈ sử dụng thông tin từ phần [Knowledge] bên dưới\n"
                "2. LUÔN cite nguồn: 'Theo tài liệu [TÊN_FILE]: ...'\n"
                "3. NẾU [Knowledge] = '(Không tìm thấy...)' → Trả lời: 'Xin lỗi, tôi không tìm thấy thông tin về [chủ đề] trong tài liệu. Vui lòng kiểm tra lại dataset hoặc upload tài liệu liên quan.'\n"
                "4. KHÔNG được bịa đặt thông tin hoặc dùng kiến thức chung nếu không có trong [Knowledge]"
            )
            lines.append(
                f"\nDatasets hiện có: {', '.join(dataset_names) if dataset_names else '(Chưa có)'}"
            )
        
        # Phần 2: Chat History & Summary (Context ngữ cảnh hội thoại)
        if conversation_summary or history:
            lines.append("\n[History]")
            if conversation_summary:
                lines.append(f"Tóm tắt cuộc hội thoại trước đó: {conversation_summary}\n")
            if history:
                for msg in history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    # Format: User: ... / Assistant: ...
                    role_label = "Assistant" if role == "assistant" else "User"
                    lines.append(f"{role_label}: {content}")
            lines.append("")
        
        if academic_facts is not None:
            lines.append("")
            lines.append(render_academic_facts(academic_facts))
            lines.append("")

        # Phần 3: Knowledge Context (Thông tin tìm được từ Vector DB)
        lines.append("[Knowledge]")
        
        has_any = False
        
        for group in grouped_results:
            dataset_name = group.get("dataset_name")
            results = group.get("results") or []
            files = group.get("files", [])
            
            # Render if we have results OR files (metadata only query)
            if not dataset_name or (not results and not files):
                continue
            
            has_any = True
            lines.append(f"Dataset: {dataset_name}")
            
            # List available files in this dataset
            files = group.get("files", [])
            if files:
                lines.append(f"Files: {', '.join(files)}")
            
            lines.append(f"Relevant Content:")
            
            # Group chunks by file_name for better organization
            from collections import defaultdict
            chunks_by_file = defaultdict(list)
            
            for r in results:
                text = (r.get("text") or "").strip()
                if not text:
                    continue
                    
                # Cắt ngắn chunk nếu quá dài
                if len(text) > max_chunk_chars:
                    text = text[: max_chunk_chars - 1] + "…"
                
                # CRITICAL: Add file_name to each chunk
                file_name = r.get("file_name", "Unknown File")
                chunks_by_file[file_name].append(text)
            
            # Render chunks grouped by file
            for file_name, texts in chunks_by_file.items():
                lines.append(f"\n  [File: {file_name}]")
                for text in texts:
                    lines.append(f"  - {text}")
        
        if not has_any:
            if academic_facts is not None:
                lines.append("(Không có tài liệu RAG — trả lời dựa trên [AcademicFacts]. Knowledge được phép trống.)")
            else:
                lines.append("\n⚠️ CẢNH BÁO: Không tìm thấy thông tin liên quan trong tài liệu.")
                lines.append("Nguyên nhân có thể: Dataset trống, file chưa được xử lý, hoặc câu hỏi không liên quan.")
                lines.append("Hãy thông báo người dùng kiểm tra lại dataset/tài liệu.\n")
        
        # Phần 4: Câu hỏi hiện tại
        lines.append("[Question]")
        lines.append(question.strip())
        
        return "\n".join(lines)

    def build_reformulation_prompt(self, history: List[Dict[str, str]], question: str) -> str:
        """Xây dựng prompt viết lại câu hỏi dựa trên lịch sử"""
        history_lines = []
        for msg in history:
            role = "Assistant" if msg.get("role") == "assistant" else "User"
            history_lines.append(f"{role}: {msg.get('content')}")
        
        history_str = "\n".join(history_lines)
        
        return f"""Nhiệm vụ của bạn là phân tích lịch sử hội thoại và câu hỏi mới nhất dưới đây, sau đó viết lại câu hỏi mới nhất thành một CÂU HỎI ĐỘC LẬP (standalone query) chứa đầy đủ ngữ cảnh để có thể tìm kiếm dữ liệu chính xác mà không cần đọc lại lịch sử.

[Lịch sử hội thoại]
{history_str}

[Câu hỏi mới nhất]
{question}

YÊU CẦU:
1. Chỉ trả về CÂU HỎI ĐỘC LẬP duy nhất, KHÔNG thêm bất kỳ lời giải thích, dẫn dắt hay ký tự thừa nào khác.
2. Nếu câu hỏi mới nhất đã đầy đủ ý nghĩa và độc lập, hãy giữ nguyên câu hỏi gốc.
3. Giữ nguyên ngôn ngữ gốc của câu hỏi (Tiếng Việt).
"""

    def build_compression_prompt(self, old_summary: Optional[str], messages_to_compress: List[Dict[str, str]]) -> str:
        """Xây dựng prompt nén lịch sử cuộc trò chuyện"""
        new_chats = []
        for msg in messages_to_compress:
            role = "Assistant" if msg.get("role") == "assistant" else "User"
            new_chats.append(f"{role}: {msg.get('content')}")
            
        new_chats_str = "\n".join(new_chats)
        old_summary_str = old_summary if old_summary else "(Chưa có tóm tắt trước đó)"
        
        return f"""Nhiệm vụ của bạn là tóm tắt và cập nhật ngữ cảnh cuộc hội thoại dưới đây thành một đoạn tóm tắt cực kỳ ngắn gọn (dưới 150 từ). Đoạn tóm tắt này giúp mô hình AI ghi nhớ các thông tin cốt lõi đã trao đổi trước đó.

[Tóm tắt ngữ cảnh cũ]
{old_summary_str}

[Các lượt trò chuyện mới cần nén thêm]
{new_chats_str}

YÊU CẦU:
1. Chỉ trả về đoạn tóm tắt cập nhật mới nhất bằng tiếng Việt, KHÔNG giải thích gì thêm.
2. Tập trung vào các thực thể, câu hỏi chính, câu trả lời đã chốt hoặc các quyết định kỹ thuật quan trọng.
3. Viết súc tích, ngắn gọn, lược bỏ các lời chào hỏi xã giao.
"""


# Singleton instance toàn cục
prompt_service = PromptService()
