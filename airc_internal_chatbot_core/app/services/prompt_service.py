"""
Prompt Service - Xây dựng prompts cho RAG
Service này chịu trách nhiệm ghép nối câu hỏi, lịch sử chat và context thành một prompt hoàn chỉnh cho LLM.
"""
import re
from typing import List, Dict, Any, Optional

ADVISOR_BAN_HALLUCINATION = (
    "Em đang nói chuyện với cô — giảng viên cố vấn học tập Khoa CNTT.\n"
    "Giọng văn: tự nhiên như cô đang ngồi trao đổi với em, xưng “cô”, gọi người hỏi là “em”. "
    "Viết thành đoạn văn ngắn, có lúc một vài ý gạch đầu dòng khi thật sự cần. "
    "Không nói như báo cáo hệ thống, không mở đầu bằng “Dựa trên dữ liệu”, "
    "không chép nguyên khối bảng điểm.\n"
    "\n"
    "CẤM xuất hiện trong câu trả lời (kể cả trong ngoặc): "
    "[AcademicFacts], [Knowledge], PASSED, FAILED, IN_PROGRESS, PREREQUISITE, PREVIOUS, "
    "depth, career_track, empty_transcript, TC viết kèm tiếng Anh. "
    "Dùng tiếng Việt: đã đạt / chưa đạt (cần học lại) / đang học / "
    "môn tiên quyết bắt buộc / môn nên học trước.\n"
    "\n"
    "QUY TẮC ĐÚNG SỰ THẬT (cô đọc khối [AcademicFacts] thầm, không đọc tên khối):\n"
    "1. Mã môn, số tín chỉ, tiên quyết, đã đạt/chưa đạt/đang học — chỉ lấy từ [AcademicFacts]. Không bịa.\n"
    "2. Em nói đã qua một môn nhưng bảng điểm chưa ghi đã đạt → tin bảng điểm, giải thích nhẹ, không cãi.\n"
    "3. Đang học không được coi là đã đạt. Không khuyên đăng ký môn còn thiếu tiên quyết bắt buộc.\n"
    "4. Bảng điểm trống → nói chưa có bảng điểm, không suy ra em đã xong học kỳ nào.\n"
    "5. Không đoán học kỳ nếu khối ghi không xác định.\n"
    "6. Chỉ bàn môn liên quan câu hỏi. Không liệt kê hết môn bị chặn.\n"
    "7. Tài liệu: chỉ nói file có trong [Knowledge]. Mỗi file nhắc tới PHẢI là markdown link "
    "[tên dễ đọc](/files/<file_id>/view) với đúng file_id trong Knowledge. "
    "Không viết [tên.pdf] trơn, không bịa URL ngoài.\n"
    "8. Knowledge trống: không bịa slide/đề cương. Bảo em xem tab Tài liệu hoặc nhờ giảng viên upload.\n"
    "9. Câu không liên quan học tập Khoa CNTT: từ chối ngắn, vẫn giọng cô nói với em."
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
            
            file_ids_by_name = {}
            for r in results:
                fname = (r.get("file_name") or "").strip()
                fid = str(r.get("file_id") or "").strip()
                if fname and fid and fname not in file_ids_by_name:
                    file_ids_by_name[fname] = fid

            # Render chunks grouped by file
            for file_name, texts in chunks_by_file.items():
                file_id = file_ids_by_name.get(file_name) or ""
                lines.append(f"\n  [File: {file_name}]")
                if file_id:
                    lines.append(f"  file_id: {file_id}")
                    lines.append(f"  cite_markdown: [{file_name}](/files/{file_id}/view)")
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


def clean_internal_tokens(answer: str) -> str:
    """Loại bỏ các token nội bộ hệ thống nếu LLM vô tình lặp lại."""
    if not answer:
        return answer
    out = answer
    out = re.sub(r'\[AcademicFacts\]', 'dữ liệu học vụ', out, flags=re.IGNORECASE)
    out = re.sub(r'\[Knowledge\]', 'tài liệu học tập', out, flags=re.IGNORECASE)
    out = re.sub(r'\bAcademicFacts\b', 'dữ liệu học vụ', out, flags=re.IGNORECASE)
    return out


def linkify_material_citations(answer: str, grouped_results: Optional[List[Dict[str, Any]]] = None) -> str:
    """Turn bare PDF names into markdown links the UI can open in a new tab, strip hallucinatory links."""
    if not answer:
        return answer

    out = clean_internal_tokens(answer)

    mapping: Dict[str, tuple[str, str]] = {}
    valid_keys: set[str] = set()
    for group in grouped_results or []:
        for row in group.get("results") or []:
            file_id = str(row.get("file_id") or "").strip()
            file_name = (row.get("file_name") or "").strip()
            if file_id and file_name:
                mapping[file_name.lower()] = (file_name, file_id)
                valid_keys.add(file_id.lower())
                valid_keys.add(file_name.lower())

    # 1. Linkify valid files from knowledge
    for _, (file_name, file_id) in sorted(mapping.items(), key=lambda item: -len(item[0])):
        href = f"/files/{file_id}/view"
        md = f"[{file_name}]({href})"
        escaped = re.escape(file_name)
        out = re.sub(
            rf"\[{escaped}\]\((?!/files/{re.escape(file_id)}/view)[^)]*\)",
            md,
            out,
            flags=re.IGNORECASE,
        )
        out = re.sub(
            rf"(?<!\()\[{escaped}\](?!\()",
            md,
            out,
            flags=re.IGNORECASE,
        )
        out = re.sub(
            rf"(?<!\[)(?<!\]\(){escaped}(?!\))",
            md,
            out,
            flags=re.IGNORECASE,
        )

    # 2. Xóa bỏ các link markdown tới file ảo giác không có trong dữ liệu (tránh click vào lỗi 404)
    def strip_fake_file_link(match: re.Match) -> str:
        label = match.group(1).strip()
        url = match.group(2).strip()
        files_match = re.match(r'^/files/([^/]+)/view$', url, re.IGNORECASE)
        if files_match:
            fid = files_match.group(1).strip().lower()
            if fid not in valid_keys and label.lower() not in mapping:
                return f"**{label}**"
        return match.group(0)

    out = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', strip_fake_file_link, out)

    return out


# Singleton instance toàn cục
prompt_service = PromptService()
