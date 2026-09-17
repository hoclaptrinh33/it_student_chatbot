# -*- coding: utf-8 -*-
"""
content_intro_ch1.py
Xây dựng PHẦN MỞ ĐẦU và CHƯƠNG 1: CƠ SỞ LÝ THUYẾT VÀ CÁC PHƯƠNG PHÁP TRÍ TUỆ NHÂN TẠO.
Tích hợp toàn diện tài liệu Báo Cáo Tổng Quan Học Máy vào Mục 1.4.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from make_full_report import (
    FONT_NAME, BLACK, set_run_font, add_p, add_heading_1, add_heading_2, 
    add_heading_3, add_bullet, add_styled_table
)

def build_introduction_and_chapter_1(doc):
    # =========================================================================
    # PHẦN MỞ ĐẦU
    # =========================================================================
    add_heading_1(doc, "PHẦN MỞ ĐẦU")
    
    add_heading_2(doc, "1. Lý do chọn đề tài")
    add_p(doc, "Trong bối cảnh chuyển đổi số giáo dục đại học và việc áp dụng triệt để phương thức đào tạo theo hệ thống tín chỉ, sinh viên ngành Công nghệ Thông tin (CNTT) được trao quyền chủ động rất lớn trong việc tự xây dựng kế hoạch và lộ trình học tập cá nhân. Tuy nhiên, tính linh hoạt của hệ thống tín chỉ cũng đặt ra không ít rào cản và thách thức lớn đối với sinh viên, đặc biệt là sinh viên năm nhất và năm hai mới bước vào môi trường đại học:")
    add_bullet(doc, "Khối lượng môn học đồ sộ và mạng lưới quan hệ tiên quyết phức tạp", 
               "Chương trình đào tạo ngành CNTT bao gồm hơn 50 học phần với các điều kiện ràng buộc chặt chẽ về môn học tiên quyết (Prerequisite), môn học trước (Previous) và môn học song hành (Co-requisite). Sinh viên nếu không nắm vững lộ trình rất dễ đăng ký sai thứ tự, dẫn đến tình trạng bị chậm tiến độ tốt nghiệp hoặc không đủ điều kiện theo học các học phần chuyên ngành chuyên sâu.")
    add_bullet(doc, "Khó khăn trong định hướng chuyên ngành", 
               "Ngành CNTT bao gồm nhiều nhánh nghề nghiệp đa dạng như Kỹ thuật phần mềm (Software Engineering), Trí tuệ nhân tạo & Khoa học dữ liệu (AI & Data Science), An toàn thông tin & Mạng máy tính (Cyber Security & Networking), Hệ thống thông tin... Sinh viên thường lúng túng không biết nên chọn các môn học tự chọn nào để phục vụ tốt nhất cho định hướng nghề nghiệp tương lai.")
    add_bullet(doc, "Phân tán và thiếu hụt tài liệu học tập chuẩn hóa", 
               "Nguồn tài liệu học tập (giáo trình chính thức, tài liệu bài giảng, đề cương chi tiết học phần, ngân hàng đề thi tham khảo) phân tán rải rác trên nhiều kênh khác nhau, khiến sinh viên mất nhiều thời gian tìm kiếm và dễ tiếp cận phải tài liệu không chính thống hoặc đã lỗi thời.")
    add_bullet(doc, "Quá tải công tác cố vấn học tập", 
               "Vào mỗi đợt đăng ký học phần đầu kỳ, số lượng câu hỏi và thắc mắc từ hàng nghìn sinh viên gửi về giảng viên cố vấn học tập và văn phòng khoa là rất lớn. Giảng viên không thể phản hồi tức thì 24/7 mọi thắc mắc của từng sinh viên.")
    add_p(doc, "Sự phát triển mạnh mẽ của Trí tuệ nhân tạo (Artificial Intelligence - AI), đặc biệt là kiến trúc Tạo sinh tăng cường truy xuất (Retrieval-Augmented Generation - RAG), Tìm kiếm trong Không gian trạng thái, Lập luận xác suất và Học máy (Machine Learning), đã mở ra cơ hội xây dựng các giải pháp trợ lý học tập ảo thông minh. Một hệ thống hỏi đáp tự động có khả năng tiếp nhận câu hỏi bằng tiếng Việt tự nhiên của sinh viên, hiểu chính xác ngữ nghĩa và thực thể học tập, trích xuất tức thì các điều khoản quy chế và tài liệu chuẩn từ cơ sở tri thức, sau đó sinh câu trả lời chính xác, đáng tin cậy chỉ trong vài giây.")
    add_p(doc, "Xuất phát từ những yêu cầu thực tiễn và tính cấp thiết nêu trên, nhóm tác giả đã lựa chọn nghiên cứu đề tài: “Xây dựng chương trình hỏi đáp bằng ngôn ngữ tự nhiên hỗ trợ chọn môn học và tài liệu học tập cho sinh viên khoa CNTT” (Mã đề tài: 32). Đề tài kết hợp nhuần nhuyễn giữa các kiến thức nền tảng trong chương trình đào tạo Trí tuệ nhân tạo (Biểu diễn không gian trạng thái, Thuật toán tìm kiếm mù BFS/DFS, Tìm kiếm Heuristic A*, Lập luận xác suất Bayes, Mô hình nhúng vector, Cosine Similarity và Kiến trúc RAG), tạo nên một ứng dụng có giá trị thực tiễn cao phục vụ trực tiếp cho sinh viên và giảng viên khoa CNTT.")

    add_heading_2(doc, "2. Mục tiêu của đề tài")
    add_p(doc, "Mục tiêu tổng quát của đề tài là nghiên cứu, thiết kế và phát triển hoàn chỉnh một hệ thống hỏi đáp thông minh (IT Student Academic Advisor Chatbot) theo kiến trúc RAG hiện đại kết hợp tiêm tri thức học vụ để hỗ trợ sinh viên khoa CNTT trong việc tra cứu lộ trình học tập, giải đáp môn học tiên quyết, tư vấn chọn môn theo định hướng chuyên ngành và gợi ý tải tài liệu học tập chính thống.")
    add_p(doc, "Các mục tiêu cụ thể bao gồm:")
    add_bullet(doc, "Hệ thống hóa toàn diện cơ sở lý thuyết Trí tuệ nhân tạo", "Không gian trạng thái, các chiến lược tìm kiếm mù (BFS, DFS), tìm kiếm có kinh nghiệm (A*, Best-First), lập luận xác suất Bayes, mạng Bayes, học máy phân loại và kiến trúc RAG hiện đại.")
    add_bullet(doc, "Khảo sát và chuẩn hóa Cơ sở tri thức (Knowledge Base)", "Xây dựng CSDL học vụ 23 môn học chuẩn, 25 quan hệ tiên quyết, bảng điểm cá nhân hóa và kho dữ liệu tài liệu học tập gồm 18+ tệp PDF (giáo trình chuẩn, slide bài giảng, đề cương chi tiết syllabus).")
    add_bullet(doc, "Xây dựng quy trình xử lý và phân đoạn văn bản tiếng Việt", "Vietnamese Text Chunking tối ưu theo các dấu phân tách ngữ nghĩa, bảo toàn trọn vẹn ngữ cảnh của từng điều khoản quy chế và nội dung bài giảng.")
    add_bullet(doc, "Ứng dụng mô hình nhúng ngôn ngữ sâu", "Dense Vector Embedding với Vietnamese-SBERT và Cơ sở dữ liệu vector Qdrant để thực hiện tìm kiếm ngữ nghĩa theo độ đo Cosine Similarity đạt tốc độ mili-giây.")
    add_bullet(doc, "Triệt tiêu ảo giác thông tin (Zero Hallucination)", "Tích hợp kỹ thuật Tiêm tri thức học vụ ([AcademicFacts] Injection), Tái xếp hạng Cross-Encoder và Mô hình ngôn ngữ lớn (Google Gemini LLM) để sinh câu trả lời tiếng Việt chính xác 100% dựa trên quy chế và điểm số thực tế.")
    add_bullet(doc, "Thiết kế và triển khai hệ thống Microservices hoàn chỉnh", "Xây dựng Frontend Web Chatbot Next.js thân thiện, hỗ trợ tra cứu môn đủ điều kiện, bảng điểm, kho tài liệu và trợ lý tương tác giọng nói trực tiếp (Live Voice).")

    add_heading_2(doc, "3. Đối tượng và phạm vi nghiên cứu")
    add_p(doc, "Đối tượng nghiên cứu: Khung chương trình đào tạo cử nhân/kỹ sư Công nghệ Thông tin; cấu trúc phụ thuộc và ràng buộc tiên quyết giữa các học phần; cơ sở dữ liệu tài liệu học tập (giáo trình, bài giảng, đề cương chi tiết); các truy vấn và câu hỏi bằng ngôn ngữ tự nhiên tiếng Việt của sinh viên liên quan đến học tập và đăng ký tín chỉ.")
    add_p(doc, "Phạm vi nội dung: Tập trung vào bài toán Hiểu ngôn ngữ tự nhiên (NLU) hướng miền giáo dục đại học, kết hợp Tìm kiếm trong không gian trạng thái (State Space Search), Lập luận xác suất (Probabilistic Reasoning), Tìm kiếm vector tương đồng (Vector Search) và Tạo sinh tăng cường truy xuất (RAG Pipeline).")
    add_p(doc, "Phạm vi áp dụng: Ứng dụng được thiết kế phục vụ trực tiếp cho sinh viên các khóa thuộc Khoa Công nghệ Thông tin - Trường Đại học Công nghệ Đông Á và có khả năng tùy biến mở rộng cho các khoa/ngành khác.")

    add_heading_2(doc, "4. Phương pháp nghiên cứu")
    add_p(doc, "Đề tài áp dụng phương pháp nghiên cứu kết hợp chặt chẽ giữa nghiên cứu lý thuyết nền tảng và phát triển thực nghiệm ứng dụng:")
    add_bullet(doc, "Cơ sở lý thuyết", "Hệ thống hóa các cơ sở lý thuyết chuẩn mực của môn học Trí tuệ nhân tạo, bao gồm lý thuyết tác tử thông minh, không gian trạng thái và thuật toán tìm kiếm, lập luận xác suất Bayes, các phương pháp học máy phân loại và kiến trúc RAG.")
    add_bullet(doc, "Xử lý dữ liệu", "Thu thập dữ liệu từ sổ tay sinh viên, khung chương trình đào tạo, tài liệu bài giảng CNTT; áp dụng kỹ thuật tiền xử lý văn bản tiếng Việt và phân đoạn văn bản đệ quy có độ chồng lấp.")
    add_bullet(doc, "Triển khai mô hình AI", "Vector hóa văn bản với mô hình Vietnamese Sentence-BERT, lập chỉ mục trong Qdrant Vector DB, kết hợp Cross-Encoder Reranker và Google Gemini LLM.")
    add_bullet(doc, "Phát triển hệ thống", "Xây dựng hệ thống theo mô hình kiến trúc Microservices độc lập (Auth Service :8001, Core Service :8000, UI Service :3000), Backend viết bằng Python FastAPI và PostgreSQL 15, Frontend viết bằng Next.js React.")

    add_heading_2(doc, "5. Cấu trúc báo cáo")
    add_p(doc, "Báo cáo kết quả nghiên cứu bài tập lớn được cấu trúc thành ba chương chính như sau:")
    add_bullet(doc, "Chương 1: Cơ sở lý thuyết và Các phương pháp Trí tuệ nhân tạo", "Trình bày tổng quan về AI, Tác tử thông minh, Không gian trạng thái, các chiến lược tìm kiếm mù (BFS, DFS), tìm kiếm Heuristic (A*), lập luận xác suất Bayes, mạng Bayes, tổng quan toàn diện về Học máy (Machine Learning Pipeline, thang đo đánh giá, phân loại mô hình), mô hình nhúng vector, Cosine Similarity và kiến trúc RAG.")
    add_bullet(doc, "Chương 2: Phân tích và Xây dựng chương trình", "Phân tích chi tiết bài toán tư vấn học tập CNTT, xác định yêu cầu và Input/Output, thiết kế sơ đồ khối kiến trúc hệ thống Microservices, mô tả chi tiết 4 thuật toán then chốt (Intent Classification, Prerequisite DAG Traversal, Hybrid RAG + Facts Injection, Per-user Semantic Caching), mô tả bộ dữ liệu học vụ và kho tài liệu PDF, trình bày cài đặt hệ thống và minh họa toàn diện hệ thống giao diện tương tác qua hơn 30 hình ảnh thực tế.")
    add_bullet(doc, "Chương 3: Thực nghiệm và Đánh giá", "Trình bày môi trường thực nghiệm, phân tích kết quả thử nghiệm mô hình qua 5 kịch bản kiểm thử thực tế (test cases), đánh giá định lượng độ chính xác truy hồi ngữ nghĩa, phân tích triệt tiêu ảo giác và thời gian phản hồi hệ thống.")
    add_bullet(doc, "Phần Kết luận, Tài liệu tham khảo và Phụ lục", "Tổng kết các kết quả đạt được, chỉ ra những hạn chế, đề xuất hướng phát triển mở rộng trong tương lai, danh mục tài liệu tham khảo chuẩn và liên kết mã nguồn GitHub chính thức của dự án.")

    doc.add_page_break()

    # =========================================================================
    # CHƯƠNG 1: CƠ SỞ LÝ THUYẾT VÀ CÁC PHƯƠNG PHÁP TRÍ TUỆ NHÂN TẠO
    # =========================================================================
    add_heading_1(doc, "CHƯƠNG 1: CƠ SỞ LÝ THUYẾT VÀ CÁC PHƯƠNG PHÁP TRÍ TUỆ NHÂN TẠO")
    
    add_heading_2(doc, "1.1 Tổng quan về Trí tuệ nhân tạo và Tác tử thông minh trong Hệ thống Hỏi - Đáp")
    
    add_heading_3(doc, "1.1.1 Khái niệm Trí tuệ nhân tạo (AI)")
    add_p(doc, "Trí tuệ nhân tạo (Artificial Intelligence - AI) là ngành khoa học và kỹ thuật máy tính nghiên cứu về các cơ chế, phương pháp làm cho hệ thống máy tính có được những năng lực trí tuệ tương tự như con người, chẳng hạn như khả năng học tập, suy luận logic, giải quyết vấn đề và hiểu ngôn ngữ tự nhiên. Thuật ngữ 'Trí tuệ nhân tạo' chính thức được nhà khoa học máy tính John McCarthy đề xuất tại Hội nghị Dartmouth vào mùa hè năm 1956, đánh dấu sự ra đời của một lĩnh vực khoa học độc lập và đầy triển vọng.")
    add_p(doc, "Trong khoa học AI hiện đại, các định nghĩa về trí tuệ nhân tạo thường được phân thành bốn nhóm tiếp cận chính:")
    add_bullet(doc, "Hệ thống suy nghĩ như con người (Thinking Humanly)", "Mô phỏng quy trình nhận thức và hoạt động tư duy của bộ não người (tiếp cận theo khoa học nhận thức).")
    add_bullet(doc, "Hệ thống hành động như con người (Acting Humanly)", "Tạo ra máy tính có khả năng thực hiện các nhiệm vụ đòi hỏi trí thông minh con người, được đánh giá qua Phép thử Turing (Turing Test, 1950).")
    add_bullet(doc, "Hệ thống suy nghĩ hợp lý (Thinking Rationally)", "Dựa trên các quy luật logic hình thức để suy luận ra các kết luận đúng đắn từ các tiền đề đã biết (tiếp cận theo quy luật tư duy).")
    add_bullet(doc, "Tiếp cận Tác tử hợp lý (Rational Agent)", "Xây dựng tác tử có khả năng đưa ra hành động tối ưu nhất nhằm đạt được mục tiêu mong muốn dựa trên các tri thức và thông tin cảm nhận được từ môi trường.")

    add_heading_3(doc, "1.1.2 Mô hình Tác tử thông minh (Intelligent Agent) và Khuôn khổ PEAS")
    add_p(doc, "Một tác tử (Agent) là bất kỳ thực thể nào có khả năng cảm nhận môi trường xung quanh thông qua các cảm biến (Sensors) và tác động trở lại môi trường thông qua các cơ cấu thực thi (Actuators). Kiến trúc tổng quát của tác tử được biểu diễn bởi công thức:")
    add_p(doc, "Agent = Architecture + Program", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    add_p(doc, "Trong đó Architecture là hạ tầng phần cứng/máy chủ và Program là thuật toán thực thi hàm tác tử (Agent Function) ánh xạ chuỗi cảm nhận (Percept Sequence) thành các hành động (Actions). Để mô tả toàn diện và thiết kế chuẩn xác một tác tử giải quyết bài toán tư vấn học tập, lý thuyết AI sử dụng khuôn khổ PEAS (Performance, Environment, Actuators, Sensors):")
    
    headers_peas = ["Thành phần PEAS", "Đặc tả chi tiết trong Hệ thống Cố vấn Học tập Khoa CNTT"]
    rows_peas = [
        ["Độ đo hiệu quả (Performance Measure)", "Độ chính xác và độ trung thực của câu trả lời (Faithfulness / RAG Triad), điểm tương đồng ngữ nghĩa (Cosine Similarity > 0.75), thời gian phản hồi (Cache Hit < 100ms, LLM Generation < 2.5s), tỷ lệ bao phủ tài liệu đúng (Recall@K), không bịa mã môn học (Zero Hallucination)."],
        ["Môi trường (Environment)", "Người dùng (sinh viên các khóa, giảng viên cố vấn), cơ sở tri thức chương trình đào tạo CNTT, kho tài liệu học tập (giáo trình, đề cương, bài giảng PDF), cơ sở dữ liệu quan hệ (PostgreSQL 15), Vector Database (Qdrant), hàng đợi bộ nhớ đệm (Redis)."],
        ["Cơ cấu thực thi (Actuators)", "Giao diện Web Chatbot Next.js tương tác thời gian thực, cơ chế sinh câu trả lời tự nhiên (LLM Streaming), trích dẫn nguồn tài liệu tham khảo (Citations / PDF Links), hiển thị danh sách môn đủ điều kiện, bảng điểm cá nhân và giọng nói trực tiếp (Live Voice)."],
        ["Cảm biến (Sensors)", "Khung nhập liệu văn bản của người dùng (User Query), giọng nói micro người dùng (Web Audio Stream), HTTP RESTful API request payload, token xác thực JWT (định danh sinh viên, vai trò người dùng RBAC), lịch sử phiên hội thoại (Chat Session Context)."]
    ]
    add_styled_table(doc, headers_peas, rows_peas, [2.0, 4.5], "Bảng 1.1: Đặc tả khuôn khổ PEAS cho Hệ thống Cố vấn Học tập Khoa CNTT")

    add_heading_3(doc, "1.1.3 Lịch sử phát triển của AI và Bước chuyển dịch sang Kỷ nguyên RAG")
    add_p(doc, "Kể từ khi được khai sinh, lịch sử hình thành và phát triển của Trí tuệ nhân tạo đã trải qua nhiều giai đoạn thăng trầm với những bước chuyển mình mang tính thời đại:")
    add_bullet(doc, "Giai đoạn khởi đầu (1943 - 1956)", "Mô hình nơ-ron nhân tạo hình thức của McCulloch & Pitts (1943); bài báo Computing Machinery and Intelligence của Alan Turing (1950) đề xuất Phép thử Turing; Hội nghị Dartmouth (1956) khai sinh ngành AI.")
    add_bullet(doc, "Giai đoạn phát triển ban đầu (1956 - 1974)", "Các nghiên cứu thành công ban đầu với các chương trình giải toán tổng quát (General Problem Solver), trò chơi cờ đam của Arthur Samuel, hệ thống chứng minh định lý tự động.")
    add_bullet(doc, "Mùa đông AI (1974 - 1980 & 1987 - 1993)", "Do giới hạn về năng lực phần cứng và kỳ vọng quá cao không đạt được, các quỹ đầu tư bị cắt giảm tạo nên các thời kỳ 'Mùa đông AI'.")
    add_bullet(doc, "Thời kỳ Hệ chuyên gia (1980 - 1987)", "Sự thành công vượt bậc của các Hệ chuyên gia thương mại (như R1/XCON của DEC, MYCIN trong y tế, DENDRAL trong hóa học) dựa trên tri thức chuyên gia và hệ luật sinh.")
    add_bullet(doc, "Kỷ nguyên Học máy và Học sâu (1993 - 2017)", "Sự trỗi dậy mạnh mẽ của Học máy (Machine Learning), Xử lý ngôn ngữ tự nhiên (NLP), Dữ liệu lớn (Big Data) và Mạng nơ-ron tích chập/tái hồi (CNN, RNN/LSTM).")
    add_bullet(doc, "Kỷ nguyên LLMs và Kiến trúc RAG (2017 - nay)", "Kiến trúc Transformer (Vaswani et al., 2017) ra đời đã tạo ra cuộc cách mạng với các Mô hình ngôn ngữ lớn (Large Language Models - LLMs) như GPT, Gemini. Tuy nhiên, các mô hình ngôn ngữ lớn thuần túy gặp phải nhược điểm nghiêm trọng là hiện tượng ảo giác (hallucination) và không có khả năng cập nhật dữ liệu nội bộ riêng biệt. Do đó, kiến trúc Tạo sinh tăng cường truy xuất (Retrieval-Augmented Generation - RAG) ra đời như một giải pháp chuẩn mực, kết hợp sức mạnh truy hồi thông tin chính xác từ cơ sở dữ liệu chuyên ngành với năng lực sinh ngôn ngữ tự nhiên xuất sắc của LLM.")

    add_heading_3(doc, "1.1.4 Các lĩnh vực nghiên cứu và ứng dụng chính của AI")
    add_p(doc, "Các lĩnh vực nghiên cứu cốt lõi của AI bao gồm:")
    add_bullet(doc, "Xử lý ngôn ngữ tự nhiên (Natural Language Processing - NLP)", "Giúp máy tính hiểu, phân tích, dịch thuật và sinh ngôn ngữ tự nhiên của con người. Ứng dụng nổi bật là Hệ thống Hỏi - Đáp thông minh (Question Answering - QA Systems) và Trợ lý ảo (Chatbots).")
    add_bullet(doc, "Hệ chuyên gia (Expert Systems) và Hệ hỗ trợ ra quyết định", "Mô phỏng quy trình suy luận của chuyên gia con người trong một lĩnh vực hẹp dựa trên cơ sở tri thức (Knowledge Base) và động cơ suy luận (Inference Engine).")
    add_bullet(doc, "Học máy (Machine Learning) và Khai phá dữ liệu (Data Mining)", "Xây dựng các mô hình trích xuất tri thức, phân loại văn bản và gợi ý lộ trình thông minh.")

    # 1.2 Không gian trạng thái
    add_heading_2(doc, "1.2 Không gian trạng thái và Các phương pháp tìm kiếm trong Quản lý Lộ trình Học tập")
    add_heading_3(doc, "1.2.1 Biểu diễn vấn đề trong không gian trạng thái (State Space Representation)")
    add_p(doc, "Trong Trí tuệ nhân tạo, giải quyết vấn đề (Problem Solving) là một trong những nhiệm vụ trọng tâm hàng đầu. Để máy tính có thể tự động tìm kiếm lời giải cho một bài toán phức tạp, phương pháp nền tảng là hình thức hóa và biểu diễn bài toán đó trong Không gian trạng thái (State Space).")
    add_p(doc, "Một bài toán được hình thức hóa đầy đủ bởi bộ 4 yếu tố cấu thành:")
    add_p(doc, "P = < S, s0, O, G >", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    add_p(doc, "Trong đó:")
    add_bullet(doc, "Tập trạng thái S", "Tập hợp tất cả các trạng thái có thể có của bài toán (State Space). Trong bài toán tư vấn học tập, mỗi trạng thái s thuộc S biểu diễn một tập hợp các môn học mà sinh viên đã tích lũy và điều kiện tín chỉ hiện tại.")
    add_bullet(doc, "Trạng thái ban đầu s0 thuộc S", "Trạng thái bắt đầu của bài toán (Initial State). Đối với sinh viên, s0 là trạng thái ban đầu khi mới nhập học (chưa có điểm tích lũy) hoặc danh sách các môn đã hoàn thành tính đến thời điểm hiện tại.")
    add_bullet(doc, "Tập các phép toán O (Operators / Actions)", "Tập hợp các hành động / phép toán chuyển trạng thái hợp lệ o: S -> S. Một phép toán chỉ được thực hiện khi thỏa mãn các điều kiện tiên quyết của môn học tương ứng.")
    add_bullet(doc, "Tập trạng thái đích G con của S", "Tập hợp một hoặc nhiều trạng thái thỏa mãn mục tiêu của bài toán (Goal States). Trong đề tài, trạng thái đích G là trạng thái sinh viên hoàn thành đầy đủ tất cả các học phần bắt buộc, tự chọn chuyên ngành và tích lũy đủ số tín chỉ quy định để tốt nghiệp.")
    add_p(doc, "Đồ thị không gian trạng thái (State Space Graph) là đồ thị có hướng trong đó các nút biểu diễn trạng thái và các cung có hướng biểu diễn các phép toán chuyển trạng thái. Quá trình giải bài toán chính là quá trình tìm kiếm một đường đi từ trạng thái đầu s0 đến một trạng thái đích thuộc G.")

    add_heading_3(doc, "1.2.2 Các phương pháp tìm kiếm mù (Uninformed / Blind Search)")
    add_p(doc, "Tìm kiếm mù (Uninformed Search hay Blind Search, còn gọi là tìm kiếm không có thông tin) là nhóm các chiến lược tìm kiếm chỉ dựa hoàn toàn vào cấu trúc không gian trạng thái đã cho và trật tự sinh các nút kế tiếp, mà không sử dụng thêm bất kỳ tri thức ước lượng nào về khoảng cách hay chi phí từ trạng thái hiện tại tới trạng thái đích.")
    add_bullet(doc, "Tìm kiếm theo chiều rộng (Breadth-First Search - BFS)", 
               "Nguyên lý: Phát triển các nút theo từng mức độ sâu tăng dần; các nút ở mức d được mở rộng trước tất cả các nút ở mức d + 1. Cài đặt sử dụng cấu trúc hàng đợi L kiểu FIFO (First-In, First-Out). Đánh giá thuật toán: BFS có tính đầy đủ (Complete) và tính tối ưu (Optimal). Độ phức tạp thời gian và không gian bộ nhớ đều là O(b^d), với b là hệ số nhánh (branching factor) và d là độ sâu của đích. Trong đề tài, BFS được áp dụng để tìm lộ trình học tập hoàn thành môn học mục tiêu qua ít học kỳ nhất.")
    add_bullet(doc, "Tìm kiếm theo chiều sâu (Depth-First Search - DFS)", 
               "Nguyên lý: Phát triển nhánh sâu nhất chưa xét; luôn chọn mở rộng một trong các nút con ở mức sâu nhất của cây tìm kiếm. Cài đặt sử dụng danh sách kiểu LIFO (Ngăn xếp Stack). Độ phức tạp bộ nhớ rất nhỏ gọn O(b*m) (với m là độ sâu tối đa), thời gian là O(b^m). Trong đề tài, DFS được áp dụng hiệu quả trong việc truy vết đệ quy chuỗi môn học tiên quyết (Prerequisite Chain Traversal) từ một môn học chuyên ngành lùi dần về các môn cơ sở ngành và đại cương trên đồ thị có hướng không chu trình (DAG).")

    add_heading_3(doc, "1.2.3 Các phương pháp tìm kiếm có kinh nghiệm / Heuristic (Informed Search)")
    add_p(doc, "Khác với tìm kiếm mù, tìm kiếm có kinh nghiệm (Informed Search hay Heuristic Search) khai thác các tri thức bổ sung mang tính đặc thù của bài toán để định hướng quá trình tìm kiếm. Bằng cách sử dụng hàm đánh giá f(n) và hàm Heuristic h(n), thuật toán có thể ước lượng triển vọng của từng trạng thái để ưu tiên mở rộng các nhánh có khả năng dẫn đến đích nhanh nhất và tiết kiệm chi phí tính toán.")
    add_bullet(doc, "Hàm Heuristic h(n)", "Ước lượng chi phí từ nút n hiện tại đến trạng thái đích. Giá trị h(n) = 0 khi n là trạng thái đích.")
    add_bullet(doc, "Tìm kiếm tốt nhất đầu tiên (Best-First Search)", "Là thuật toán kết hợp giữa tìm kiếm theo chiều rộng và hàm đánh giá. Các nút được lưu trong hàng đợi ưu tiên (Priority Queue) sắp xếp theo thứ tự ưu tiên của hàm đánh giá.")
    add_bullet(doc, "Thuật toán tìm kiếm A*", "Là thuật toán tìm kiếm Heuristic quan trọng và phổ biến nhất trong AI:")
    add_p(doc, "f(n) = g(n) + h(n)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p(doc, "Trong đó g(n) là chi phí thực tế đã đi từ trạng thái ban đầu s0 đến nút n; h(n) là ước lượng chi phí từ nút n đến trạng thái đích; f(n) là tổng chi phí ước lượng của đường đi qua n đến đích. Nếu hàm Heuristic h(n) là chấp nhận được (Admissible), tức là 0 <= h(n) <= h*(n) với mọi nút n, thì thuật toán A* đảm bảo luôn tìm được lời giải tối ưu nhất. Trong hệ thống tư vấn, A* được vận dụng để xây dựng lộ trình đăng ký môn học tối ưu hóa tổng điểm tích lũy và dàn đều tải trọng tín chỉ.")

    add_heading_3(doc, "1.2.4 Phương pháp tìm kiếm cục bộ và leo đồi (Hill-Climbing Search)")
    add_p(doc, "Tìm kiếm leo đồi (Hill-Climbing Search) là một kỹ thuật tìm kiếm cục bộ (Local Search) kết hợp nguyên lý tìm kiếm theo chiều sâu với việc sử dụng hàm đánh giá Heuristic để dẫn dắt hành trình. Tại mỗi bước, thuật toán chọn trong số các nút con nút nào có giá trị hàm đánh giá triển vọng nhất để tiếp tục đi tiếp. Hạn chế của thuật toán là dễ bị mắc kẹt tại các điểm cực trị cục bộ (Local Maxima), cao nguyên (Plateau) hoặc sống núi (Ridge).")

    # 1.3 Lập luận xác suất
    add_heading_2(doc, "1.3 Lập luận xác suất và Xử lý thông tin không chắc chắn")
    add_heading_3(doc, "1.3.1 Vấn đề thông tin không chắc chắn khi lập luận")
    add_p(doc, "Trong các hệ thống Trí tuệ nhân tạo tương tác thực tế, thông tin tiếp nhận từ môi trường hay người sử dụng hiếm khi hoàn hảo và chính xác tuyệt đối. Sự không chắc chắn (Uncertainty) thường xuất hiện từ nhiều nguyên nhân khách quan:")
    add_bullet(doc, "Dữ liệu câu hỏi người dùng mơ hồ", "Sinh viên hỏi 'Kỳ này em nên học môn gì?' mà chưa cung cấp chuyên ngành, khóa học hay số tín chỉ tích lũy, hoặc câu hỏi chứa từ viết tắt, tiếng lóng học tập, lỗi chính tả.")
    add_bullet(doc, "Quan hệ ngữ nghĩa không tất định", "Mối quan hệ giữa câu hỏi tự nhiên và nội dung tài liệu quy chế không mang tính xác định tuyệt đối mà mang tính xác suất phân phối ngữ nghĩa.")
    add_p(doc, "Để xử lý trường hợp không chắc chắn, Trí tuệ nhân tạo sử dụng phương pháp tiếp cận thống kê và lý thuyết xác suất để lượng hóa mức độ tin cậy (Belief) cho từng kết luận.")

    add_heading_3(doc, "1.3.2 Lập luận xác suất và Định lý Bayes")
    add_p(doc, "Định lý Bayes (Bayes' Theorem) là nền tảng toán học cốt lõi cho việc cập nhật xác suất của một giả thuyết khi có thêm bằng chứng (Evidence) quan sát được:")
    add_p(doc, "P(A|B) = [P(B|A) * P(A)] / P(B)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    add_p(doc, "Trong đó P(A) là xác suất tiên nghiệm (Prior Probability); P(B|A) là xác suất có điều kiện (Likelihood); P(A|B) là xác suất hậu nghiệm (Posterior Probability); P(B) là xác suất toàn phần của bằng chứng B. Trong hệ thống truy hồi thông tin và RAG, định lý Bayes được vận dụng để ước lượng xác suất một đoạn tài liệu c là phù hợp với câu hỏi truy vấn q của sinh viên.")

    add_heading_3(doc, "1.3.3 Mạng Bayes (Bayesian Networks)")
    add_p(doc, "Mạng Bayes (Bayesian Network hay Belief Network) là một mô hình đồ thị xác suất đặc biệt hiệu quả, cho phép biểu diễn trực quan và chặt chẽ cấu trúc phụ thuộc có điều kiện giữa tập hợp các biến ngẫu nhiên:")
    add_bullet(doc, "Cấu trúc mạng", "Đồ thị có hướng không chu trình (DAG): Các nút biểu diễn các biến ngẫu nhiên; các cung có hướng biểu diễn ảnh hưởng trực tiếp giữa các biến.")
    add_bullet(doc, "Bảng CPT", "Bảng phân bố xác suất có điều kiện (CPT - Conditional Probability Table): Mỗi nút X_i có một bảng CPT định lượng mức độ ảnh hưởng của các nút cha Parents(X_i) lên X_i.")
    add_p(doc, "Phân rã phân bố xác suất đồng thời trong Mạng Bayes được tính theo công thức:")
    add_p(doc, "P(X1, X2, ..., Xn) = ∏ P(X_i | Parents(X_i))", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    add_p(doc, "Ứng dụng trong đề tài: Mạng Bayes cho phép hệ thống ước lượng xác suất sinh viên vượt qua một môn học chuyên ngành nâng cao dựa trên phân phối xác suất điểm số của chuỗi các môn học tiên quyết và cơ sở.")

    # 1.4 HỌC MÁY VÀ NLP TRONG KIẾN TRÚC RAG (TÍCH HỢP TỪ BAO_CAO_TONG_QUAN_HOC_MAY)
    add_heading_2(doc, "1.4 Tổng quan Học máy và Xử lý ngôn ngữ tự nhiên trong Kiến trúc Chatbot RAG")
    
    add_heading_3(doc, "1.4.1 Khái niệm Học máy (Machine Learning) và Bộ ba (Task, Performance, Experience)")
    add_p(doc, "Học máy (Machine Learning - ML) là một phân ngành nghiên cứu cốt lõi của Trí tuệ nhân tạo (AI) và Khoa học máy tính, tập trung vào việc nghiên cứu, phát triển các lý thuyết và thuật toán cho phép máy tính có khả năng tự động học hỏi quy luật, rút trích tri thức từ dữ liệu hoặc kinh nghiệm trong quá khứ, từ đó tự nâng cao hiệu năng thực thi nhiệm vụ mà không cần phải lập trình tường minh (explicitly programmed) từng dòng mã cho từng tình huống cụ thể.")
    add_p(doc, "Về mặt khoa học hàn lâm, học máy được định nghĩa một cách chặt chẽ qua các quan điểm kinh điển:")
    add_bullet(doc, "Định nghĩa của Tom Mitchell (1997 - CMU)", "“Một chương trình máy tính được xem là học từ kinh nghiệm E (Experience) đối với một lớp tác vụ T (Task) và tiêu chí đánh giá hiệu năng P (Performance), nếu hiệu năng của nó tại các tác vụ trong T, được đo lường bởi P, được cải thiện cùng với kinh nghiệm E”. Đây là định nghĩa toán học - kỹ thuật nền tảng và chuẩn mực nhất của ngành khoa học máy tính cho đến nay.")
    add_bullet(doc, "Định nghĩa của Herbert Simon (1983 - Nobel & Turing)", "“Học máy là quá trình mà nhờ đó một hệ thống có khả năng tự cải thiện hiệu quả hoạt động (hiệu suất) của chính mình dựa trên những tác vụ đã từng thực thi trong quá khứ”.")
    add_bullet(doc, "Định nghĩa của Ethem Alpaydin (2010)", "“Học máy là việc lập trình các hệ thống máy tính nhằm mục tiêu tối ưu hóa một tiêu chí hiệu suất đã chọn trước, dựa trên dữ liệu mẫu hoặc kinh nghiệm thu nhận được từ quá khứ”.")
    add_p(doc, "Bản chất toán học của Học máy là việc xấp xỉ một hàm ánh xạ mục tiêu y = f(x) từ không gian quan sát đầu vào X (các biến đặc trưng) sang không gian đầu ra Y (nhãn dự đoán hoặc giá trị liên tục). Sau khi mô hình được huấn luyện trên tập dữ liệu đã biết, nó phải có năng lực khái quát hóa (generalization) – tức là dự đoán chính xác trên các tập dữ liệu mới lạ chưa từng xuất hiện trong quá trình học.")

    add_heading_3(doc, "1.4.2 Phân tích các thành phần kỹ thuật của một giải pháp Học máy")
    add_p(doc, "Về mặt triển khai trong khoa học dữ liệu, một giải pháp học máy hoàn chỉnh bao gồm 4 khối thành phần kỹ thuật liên kết chặt chẽ:")
    add_bullet(doc, "Dữ liệu (Data - D)", "Gồm tập mẫu huấn luyện (Training set), tập kiểm định (Validation set) và tập kiểm thử (Test set). Mỗi quan sát x_i được biểu diễn bằng một vectơ đặc trưng d chiều: x_i = (x_i1, x_i2, ..., x_id)^T, đi kèm với nhãn y_i (nếu có).")
    add_bullet(doc, "Không gian giả thiết / Mô hình (Hypothesis Space / Model - f(x; θ))", "Là tập hợp toàn bộ các hàm toán học tiềm năng mà thuật toán có thể lựa chọn để mô tả quan hệ giữa dữ liệu đầu vào x và đầu ra y. Tham số θ (weights, biases) là các trọng số nội tại của mô hình sẽ được cập nhật trong quá trình học.")
    add_bullet(doc, "Hàm mất mát / Hàm chi phí (Loss / Cost Function - L(y, ŷ))", "Công cụ toán học định lượng mức độ sai khác giữa nhãn thực tế y và kết quả dự đoán ŷ = f(x; θ). Hàm mất mát càng nhỏ thì mô hình dự đoán càng chính xác.")
    add_bullet(doc, "Thuật toán tối ưu (Optimization Algorithm)", "Phương pháp toán học giải bài toán cực tiểu hóa hàm mất mát để tìm ra bộ trọng số tối ưu θ* (như Gradient Descent, Adam, Stochastic Gradient Descent).")

    add_heading_3(doc, "1.4.3 Các ví dụ minh họa kinh điển của bài toán Học máy")
    add_bullet(doc, "Ví dụ 1: Hệ thống lọc thư rác (Email Spam Filtering)", 
               "Nhiệm vụ T: Phân loại email đến thành 'Thư thường' (Ham) hoặc 'Thư rác' (Spam). Kinh nghiệm E: Tập hàng trăm nghìn email quá khứ đã được gán nhãn, trích xuất đặc trưng tần suất từ khóa khả nghi, IP máy chủ, tệp đính kèm. Tiêu chí P: Tỷ lệ phân loại đúng (Accuracy) và đặc biệt là Precision trên lớp Spam để tránh mất thư quan trọng.")
    add_bullet(doc, "Ví dụ 2: Hệ thống nhận dạng chữ số viết tay (Handwritten Digit Recognition)", 
               "Nhiệm vụ T: Nhận dạng ảnh chữ viết tay thành một trong 10 chữ số từ 0 đến 9 (bộ dữ liệu MNIST). Kinh nghiệm E: 70.000 ảnh kích thước 28x28 điểm ảnh có nhãn. Tiêu chí P: Tỷ lệ phần trăm các chữ số trong tập kiểm thử được nhận dạng hoàn toàn chính xác.")
    add_bullet(doc, "Ví dụ 3: Hệ thống xe ô tô tự hành (Autonomous Vehicle)", 
               "Nhiệm vụ T: Điều khiển góc quay vô-lăng, lực ga, lực phanh để di chuyển an toàn trên đường phố. Kinh nghiệm E: Luồng video camera, LiDAR, Radar qua hàng triệu km thực tế và giả lập, cùng tín hiệu thưởng/phạt. Tiêu chí P: Số km trung bình xe tự vận hành an toàn không cần can thiệp.")

    add_heading_3(doc, "1.4.4 Phân biệt Học máy và Lập trình thông thường")
    add_p(doc, "Sự ra đời của Học máy đánh dấu bước chuyển dịch mang tính cách mạng từ mô hình phát triển phần mềm truyền thống (Phần mềm 1.0 - Software 1.0) sang mô hình phần mềm điều khiển bởi dữ liệu (Phần mềm 2.0 - Software 2.0):")
    add_bullet(doc, "Lập trình thông thường (Software 1.0)", "Tiếp cận diễn dịch (deductive). Lập trình viên tự tay viết mã tường minh từng quy tắc logic (if-else, công thức toán học). Mô hình: DỮ LIỆU (DATA) + QUY TẮC (RULES) ➔ KẾT QUẢ (ANSWERS).")
    add_bullet(doc, "Học máy (Software 2.0)", "Tiếp cận quy nạp (inductive). Cung cấp cho máy tính Dữ liệu lịch sử cùng Kết quả mẫu. Thuật toán tự động khám phá tương quan và tổng hợp ra Mô hình quy tắc. Mô hình: DỮ LIỆU (DATA) + KẾT QUẢ MẪU (ANSWERS) ➔ MÔ HÌNH QUY TẮC (MODEL). Khi có dữ liệu mới: DỮ LIỆU MỚI + MÔ HÌNH ➔ DỰ ĐOÁN (PREDICTIONS).")
    
    headers_cmp_prog = ["Tiêu chí so sánh", "Lập trình thông thường (Software 1.0)", "Học máy (Software 2.0)"]
    rows_cmp_prog = [
        ["Bản chất tiếp cận", "Tất định (Deterministic); dựa trên các luật logic và giải thuật do con người đặt ra.", "Thống kê quy nạp (Probabilistic); tự động rút trích mô hình mẫu từ dữ liệu."],
        ["Đầu vào ban đầu", "Dữ liệu (Data) và các khối mã lệnh quy tắc (Program/Rules).", "Dữ liệu quan sát (Data) và Nhãn kết quả mẫu trong quá khứ (Answers)."],
        ["Đầu ra sản phẩm", "Kết quả tính toán cụ thể cho từng đầu vào (Answers/Output).", "Mô hình thuật toán chứa trọng số đại diện cho tri thức tự học (Model)."],
        ["Khả năng thích ứng", "Kém linh hoạt; khi quy tắc thay đổi bắt buộc lập trình viên phải sửa và biên dịch lại mã nguồn.", "Rất cao; hệ thống tự thích nghi khi được cấp thêm dữ liệu mới để tái huấn luyện (retraining)."],
        ["Xử lý bài toán phức tạp", "Bất khả thi đối với các bài toán phi cấu trúc nhiều chiều (nhận diện khuôn mặt, dịch giọng nói).", "Rất xuất sắc đối với dữ liệu âm thanh, hình ảnh, video, văn bản tự nhiên và dữ liệu chuỗi."],
        ["Tính minh bạch", "Rất rõ ràng (White-box); dễ dàng theo dõi, kiểm thử (trace/debug) từng dòng mã lệnh.", "Khó giải thích hơn (nhiều mô hình là Black-box như Deep Learning/Ensemble)."],
        ["Vai trò của con người", "Tự tay tư duy và hiện thực hóa toàn bộ thuật toán xử lý.", "Thu thập, làm sạch dữ liệu, chọn kiến trúc mô hình và thiết kế hàm mục tiêu."],
        ["Tài nguyên phần cứng", "Đòi hỏi tài nguyên phần cứng vừa phải, tính toán nhẹ nhàng trên CPU tiêu chuẩn.", "Yêu cầu tài nguyên tính toán lớn (GPU, TPU, máy chủ phân tán) và dung lượng RAM cao."]
    ]
    add_styled_table(doc, headers_cmp_prog, rows_cmp_prog, [1.5, 2.5, 2.5], "Bảng 1.2: So sánh toàn diện giữa Lập trình thông thường và Học máy")

    add_heading_3(doc, "1.4.5 Phân loại các mô hình học máy cơ bản")
    add_p(doc, "Dựa trên sự hiện diện của tín hiệu giám sát (nhãn dữ liệu) và phương thức tiếp nhận phản hồi từ môi trường, các mô hình học máy được phân thành 4 nhóm chính:")
    add_bullet(doc, "Học có giám sát (Supervised Learning)", "Huấn luyện trên tập dữ liệu đã biết trước cả đầu vào x và nhãn đầu ra y: D = {(x_i, y_i)}. Hai bài toán trọng tâm: Phân loại (Classification - nhãn rời rạc; thuật toán: Naive Bayes, SVM, Decision Tree, Random Forest, Logistic Regression, CNN) và Hồi quy (Regression - nhãn số thực liên tục; thuật toán: Linear Regression, Ridge/Lasso, SVR, XGBoost).")
    add_bullet(doc, "Học không giám sát (Unsupervised Learning)", "Tập dữ liệu chỉ chứa các quan sát đầu vào mà hoàn toàn không có nhãn mục tiêu. Các bài toán cốt lõi: Phân cụm dữ liệu (K-Means, DBSCAN, Hierarchical Clustering), Giảm số chiều dữ liệu (PCA, t-SNE, Autoencoder), Khai phá luật kết hợp (Apriori, FP-Growth) và Phát hiện điểm bất thường (Isolation Forest, One-Class SVM).")
    add_bullet(doc, "Học bán giám sát (Semi-supervised Learning)", "Kết hợp một tập nhỏ dữ liệu đã gắn nhãn D_L với một tập lớn dữ liệu chưa có nhãn D_U. Áp dụng kỹ thuật tự gán nhãn (Self-training / Pseudo-labeling) và Co-training nhằm tiết kiệm chi phí dán nhãn thủ công khổng lồ.")
    add_bullet(doc, "Học tăng cường (Reinforcement Learning - RL)", "Thực thể học (Agent) tương tác thử - sai với môi trường theo Quy trình quyết định Markov (MDP) bao gồm 5 thành tố (S, A, P, R, γ). Mục tiêu tối thượng là tìm Chiến lược tối ưu π* để tối đa hóa Tổng phần thưởng tích lũy dài hạn. Thuật toán: Q-Learning, DQN, Policy Gradient, PPO, và đặc biệt là RLHF (Reinforcement Learning from Human Feedback) dùng để căn chỉnh các mô hình ngôn ngữ lớn như Gemini hay ChatGPT.")

    headers_ml_types = ["Phương pháp", "Bản chất dữ liệu", "Mục tiêu bài toán", "Thuật toán tiêu biểu", "Ứng dụng thực tiễn"]
    rows_ml_types = [
        ["Học có giám sát (Supervised)", "Có đầy đủ vector thuộc tính và nhãn (X, Y)", "Tìm ánh xạ f(X) ➔ Y để phân loại hoặc hồi quy", "SVM, Random Forest, XGBoost, CNN, Logistic Reg", "Lọc thư rác, nhận diện mặt, phân loại ý định người dùng"],
        ["Học không giám sát (Unsupervised)", "Chỉ có vector quan sát X, không có nhãn Y", "Tìm cấu trúc ẩn, gom cụm, giảm số chiều dữ liệu", "K-Means, PCA, DBSCAN, Apriori, Isolation Forest", "Phân khúc sinh viên, phát hiện bất thường, nén vector"],
        ["Học bán giám sát (Semi-supervised)", "Tập nhỏ có nhãn + Khối lượng lớn chưa nhãn", "Tận dụng dữ liệu chưa nhãn để nâng cao độ chính xác", "Pseudo-labeling, Co-training, Graph-based SSL", "Gán nhãn câu hỏi sinh viên tự động, y tế, âm thanh"],
        ["Học tăng cường (Reinforcement)", "Không có nhãn; chỉ có phản hồi thưởng/phạt", "Học chiến lược hành động tối đa hóa phần thưởng", "Q-Learning, DQN, Policy Gradient, PPO, Actor-Critic", "AlphaGo, Robot tự hành, Tinh chỉnh LLM (RLHF)"]
    ]
    add_styled_table(doc, headers_ml_types, rows_ml_types, [1.3, 1.3, 1.3, 1.3, 1.3], "Bảng 1.3: Tổng kết so sánh 4 mô hình học máy cơ bản")

    add_heading_3(doc, "1.4.6 Đánh giá mô hình học máy")
    add_p(doc, "Đánh giá mô hình học máy đòi hỏi tuân thủ nghiêm ngặt các nguyên tắc khoa học:")
    add_bullet(doc, "Nguyên tắc vàng (Golden Rule)", "Không bao giờ được đánh giá chất lượng cuối cùng của mô hình trên chính tập dữ liệu đã dùng để huấn luyện nó nhằm triệt tiêu hiện tượng rò rỉ dữ liệu (Data Leakage). Áp dụng phân chia Hold-out (Train 70%, Validation 15%, Test 15%) hoặc Đánh giá chéo K-lần (K-Fold Cross-Validation).")
    add_bullet(doc, "Ma trận nhầm lẫn (Confusion Matrix)", "Thống kê 4 trường hợp kết quả: True Positive (TP), True Negative (TN), False Positive (FP - Dương tính giả / Sai lầm loại I), False Negative (FN - Âm tính giả / Sai lầm loại II).")
    add_bullet(doc, "Các chỉ số phân loại", "Accuracy = (TP + TN) / Tổng; Precision = TP / (TP + FP); Recall = TP / (TP + FN); F1-Score = 2 * (Precision * Recall) / (Precision + Recall); Đường cong ROC và chỉ số AUC.")
    add_bullet(doc, "Các thang đo hồi quy", "Sai số tuyệt đối trung bình (MAE), Sai số toàn phương trung bình (MSE), Căn bậc hai sai số toàn phương (RMSE) và Hệ số xác định (R^2).")
    add_bullet(doc, "Overfitting, Underfitting và Bias-Variance Tradeoff", "Hiện tượng Quá khớp (Overfitting - sai số tập học cực thấp nhưng sai số tập test rất cao); Hiện tượng Chưa khớp (Underfitting - sai số cao trên cả tập học lẫn tập test). Sự đánh đổi giữa Độ chệch (Bias) và Phương sai (Variance) đòi hỏi kỹ sư tìm điểm dung hòa tối ưu (Sweet Spot).")

    add_heading_3(doc, "1.4.7 Quy trình phát triển một mô hình học máy (Machine Learning Pipeline theo MLOps)")
    add_p(doc, "Việc phát triển một hệ thống học máy trong môi trường sản xuất thực tế là một quy trình kỹ nghệ phần mềm khép kín và có tính chu kỳ liên tục lặp lại theo tiêu chuẩn MLOps (Machine Learning Operations), bao gồm 7 giai đoạn kế tiếp nhau:")
    
    headers_pipeline = ["Giai đoạn thực hiện", "Nội dung nhiệm vụ trọng tâm", "Kết quả bàn giao (Deliverables)"]
    rows_pipeline = [
        ["Bước 1: Xác định bài toán (Problem Formulation)", "Phân tích yêu cầu nghiệp vụ, chuyển thành bài toán ML cụ thể, thiết lập KPIs và tiêu chí thành công.", "Tài liệu đặc tả bài toán, mục tiêu định lượng & metrics."],
        ["Bước 2: Thu thập dữ liệu (Data Collection)", "Tập hợp dữ liệu từ CSDL nội bộ, Data Warehouse, API, web crawling, log hệ thống; kiểm tra tính hợp pháp.", "Tập dữ liệu thô (Raw Dataset) có tính đại diện cao."],
        ["Bước 3: Khám phá & Tiền xử lý (EDA & Preprocessing)", "Phân tích thống kê EDA, xử lý dữ liệu khuyết, loại bỏ ngoại lai, mã hóa danh mục, chuẩn hóa thang đo.", "Bộ dữ liệu sạch, ma trận đặc trưng chuẩn hóa hoàn chỉnh."],
        ["Bước 4: Huấn luyện mô hình (Model Training)", "Chia tập Train/Val/Test, xây dựng mô hình cơ sở (baseline), thử nghiệm song song nhiều thuật toán ứng viên.", "Các mô hình ứng viên được huấn luyện sơ bộ trên tập Train."],
        ["Bước 5: Đánh giá & Tinh chỉnh (Evaluation & Tuning)", "Đánh giá chéo K-Fold, phân tích ma trận nhầm lẫn, tối ưu siêu tham số (Grid/Random/Bayesian Search).", "Mô hình tốt nhất được kiểm định chốt trên tập Test."],
        ["Bước 6: Triển khai vào thực tế (Model Deployment)", "Đóng gói mô hình (joblib/ONNX), xây dựng RESTful API/gRPC, đóng gói Docker container, triển khai Cloud.", "Dịch vụ dự đoán sẵn sàng phục vụ người dùng cuối."],
        ["Bước 7: Giám sát & Vận hành (Monitoring & Retraining)", "Giám sát tài nguyên, phát hiện trôi dạt dữ liệu (Data Drift) và khái niệm (Concept Drift), tự động tái đào tạo.", "Dashboard giám sát MLOps, pipeline tự động tái học."]
    ]
    add_styled_table(doc, headers_pipeline, rows_pipeline, [1.8, 2.7, 2.0], "Bảng 1.4: Quy trình 7 bước phát triển hệ thống Học máy chuẩn MLOps")

    add_heading_3(doc, "1.4.8 Kỹ thuật Tiền xử lý và Phân đoạn văn bản tiếng Việt (Vietnamese Text Chunking)")
    add_p(doc, "Trong các hệ thống RAG thực tế, việc nạp toàn bộ một tài liệu PDF hoặc Word dài hàng chục trang vào mô hình sẽ gây tràn cửa sổ ngữ cảnh (Context Window) và làm suy giảm độ chính xác tìm kiếm. Do đó, kỹ thuật Phân đoạn văn bản (Text Chunking) là bước tiền xử lý bắt buộc:")
    add_bullet(doc, "Chuẩn hóa văn bản tiếng Việt", "Loại bỏ các khoảng trắng thừa, chuẩn hóa các ký tự xuống dòng liên tiếp và xử lý bảng mã Unicode.")
    add_bullet(doc, "Phân đoạn đệ quy tối ưu theo dấu ngắt câu tiếng Việt", "Sử dụng danh sách các ký tự phân tách theo thứ tự ưu tiên giảm dần: ngắt đoạn (\\n\\n), xuống dòng (\\n), dấu chấm (. ), dấu chấm than (! ), dấu hỏi (? ), dấu chấm phẩy (; ), dấu hai chấm (: ), dấu phẩy (, ), khoảng trắng ( ).")
    add_bullet(doc, "Thiết lập kích thước phân đoạn và độ chồng lấp", "Mỗi đoạn văn bản (chunk) được khống chế ở kích thước chuẩn chunk_size = 1024 ký tự, kết hợp độ chồng lấp chunk_overlap = 20 đến 100 ký tự nhằm đảm bảo không làm đứt gãy thông tin ngữ cảnh giữa hai đoạn văn bản liền kề.")

    add_heading_3(doc, "1.4.9 Biểu diễn văn bản trong Không gian Vector: Từ TF-IDF đến Dense Vector Embedding")
    add_p(doc, "Mô hình TF-IDF biểu diễn văn bản dựa trên tần số xuất hiện của từ ngữ trong tài liệu và độ hiếm của từ trong toàn bộ kho tài liệu:")
    add_p(doc, "TF-IDF(t, d, D) = TF(t, d) * IDF(t, D)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p(doc, "Mặc dù TF-IDF tính toán nhanh, nhưng mô hình này chỉ dựa vào sự trùng khớp mặt chữ (Keyword Matching), không hiểu được nghĩa đồng nghĩa hoặc ngữ cảnh ngữ nghĩa.")
    add_p(doc, "Để vượt qua hạn chế của TF-IDF, hệ thống áp dụng Mô hình nhúng câu đa chiều dựa trên kiến trúc Sentence-BERT chuyên biệt cho tiếng Việt (mô hình keepitreal/vietnamese-sbert). Mô hình ánh xạ mỗi câu hoặc đoạn văn bản bất kỳ thành một vector đặc trưng thực dầy đặc trong không gian 768 chiều:")
    add_p(doc, "v = Embed(text) ∈ R^{768}, với ||v||_2 = 1", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p(doc, "Các đoạn văn bản có ý nghĩa ngữ nghĩa tương đồng (dù sử dụng các từ ngữ khác nhau) sẽ nằm rất gần nhau trong không gian vector đa chiều này.")

    add_heading_3(doc, "1.4.10 Đo lường độ tương đồng ngữ nghĩa bằng Cosine Similarity và Vector Database")
    add_p(doc, "Để tìm kiếm các đoạn văn bản có nội dung phù hợp nhất với câu hỏi của sinh viên, hệ thống tính toán độ đo Cosine Similarity giữa vector câu hỏi q và từng vector đoạn văn bản d_i trong kho tri thức:")
    add_p(doc, "Cosine_Similarity(q, d_i) = (q . d_i) / (||q||_2 * ||d_i||_2)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p(doc, "Khoảng cách Cosine (Cosine Distance) được định nghĩa là: Cosine_Distance(q, d_i) = 1 - Cosine_Similarity(q, d_i). Hệ thống sử dụng Cơ sở dữ liệu vector chuyên dụng Qdrant (Vector Database), hỗ trợ lập chỉ mục đồ thị HNSW (Hierarchical Navigable Small World) để thực hiện tìm kiếm lân cận gần nhất (Approximate Nearest Neighbors - ANN) với độ trễ cực thấp (< 20ms) ngay cả khi quy mô kho dữ liệu lên tới hàng triệu vector.")

    add_heading_3(doc, "1.4.11 Kỹ thuật Tái xếp hạng (Cross-Encoder Reranking) và Tạo sinh tăng cường truy xuất (RAG)")
    add_p(doc, "Quy trình truy hồi hai giai đoạn (Two-Stage Retrieval) trong hệ thống bao gồm:")
    add_bullet(doc, "Giai đoạn 1 - Bi-Encoder Retrieval", "Sử dụng vector embedding và Qdrant để lọc nhanh Top-20 đoạn văn bản có độ tương đồng Cosine cao nhất.")
    add_bullet(doc, "Giai đoạn 2 - Cross-Encoder Reranking", "Đưa câu hỏi và từng đoạn văn bản đồng thời vào mô hình Cross-Encoder để tính toán điểm tương thích ngữ cảnh sâu sắc (Relevance Score), từ đó sắp xếp lại và trích xuất Top-5 đoạn chất lượng nhất.")
    add_bullet(doc, "Giai đoạn 3 - LLM Generation", "Tại giai đoạn sinh câu trả lời, hệ thống kết hợp System Prompt chuyên gia + Tiêm tri thức học vụ [AcademicFacts] + Lịch sử hội thoại + Top-5 đoạn văn bản ngữ cảnh được trích xuất + Câu hỏi sinh viên để gửi tới Google Gemini LLM API (gemini-1.5-flash / gemini-2.0-flash). Cơ chế này đảm bảo câu trả lời luôn bám sát tài liệu quy chế chính thức, có trích dẫn nguồn cụ thể và loại bỏ hoàn toàn hiện tượng ảo giác thông tin.")

    headers_rag_cmp = ["Phương pháp / Kỹ thuật", "Ưu điểm nổi bật", "Hạn chế chính", "Ứng dụng trong hệ thống"]
    rows_rag_cmp = [
        ["Mô hình TF-IDF & Keyword Matching", "Tốc độ tính toán nhanh, chi phí phần cứng thấp, chính xác với mã môn học.", "Không nắm bắt được từ đồng nghĩa và quan hệ ngữ nghĩa tiềm ẩn.", "Truy vấn nhanh mã môn học, tra cứu theo từ khóa chính xác."],
        ["Dense Embedding (Vietnamese-SBERT)", "Hiểu sâu sắc ngữ nghĩa tiếng Việt, không phụ thuộc mặt chữ, vector 768 chiều chuẩn hóa.", "Cần tài nguyên tính toán (CPU/GPU) để sinh vector nhúng.", "Giai đoạn 1 của RAG: Tìm kiếm Top-20 đoạn văn bản liên quan trong Qdrant."],
        ["Cross-Encoder Reranker & LLM (Gemini)", "Đánh giá tương quan ngữ cảnh đa chiều chính xác tuyệt đối, sinh câu trả lời tự nhiên.", "Thời gian xử lý lâu hơn Bi-Encoder (~200ms rerank, ~1.5s LLM).", "Giai đoạn 2 của RAG: Lọc Top-5 đoạn tinh hoa và sinh câu trả lời hoàn chỉnh."]
    ]
    add_styled_table(doc, headers_rag_cmp, rows_rag_cmp, [1.6, 2.0, 1.5, 1.4], "Bảng 1.5: So sánh tổng quan các kỹ thuật phân loại và truy hồi văn bản")

    # 1.5 Phương pháp đánh giá
    add_heading_2(doc, "1.5 Phương pháp đánh giá mô hình và hệ thống Hỏi - Đáp")
    add_p(doc, "Để đánh giá một cách định lượng và khách quan chất lượng của mô hình học máy và hệ thống hỏi đáp RAG, cơ chế đánh giá tiêu chuẩn kết hợp cả các chỉ số phân lớp truyền thống và các chỉ số tìm kiếm thông tin hiện đại:")
    add_bullet(doc, "Mean Reciprocal Rank (MRR)", "Đo lường chất lượng xếp hạng đoạn văn bản theo vị trí xuất hiện của đoạn tài liệu đúng đầu tiên trong danh sách kết quả: MRR = (1 / |Q|) * ∑ (1 / rank_i).")
    add_bullet(doc, "Hit Rate@K", "Tỷ lệ các câu hỏi mà ít nhất một đoạn văn bản thực sự liên quan xuất hiện trong Top-K kết quả trả về từ Qdrant và Reranker.")
    add_bullet(doc, "Average Similarity Score", "Điểm tương đồng Cosine trung bình giữa câu hỏi và các đoạn trích dẫn được chọn, phản ánh mức độ gắn kết ngữ cảnh.")
    add_bullet(doc, "Phân rã độ trễ phản hồi (Latency Breakdown)", "Đo lường thời gian xử lý qua các công đoạn: Thời gian kiểm tra Semantic Cache (< 100ms), Thời gian tính toán Embedding (~50ms), Thời gian tìm kiếm Vector trong Qdrant (~20ms), Thời gian Cross-Encoder Rerank (~200ms) và Thời gian sinh câu trả lời của LLM (~1.5s - 2.0s).")

    # 1.6 Công cụ, Thư viện và Hạ tầng
    add_heading_2(doc, "1.6 Công cụ, Thư viện và Hạ tầng công nghệ phát triển hệ thống")
    add_p(doc, "Toàn bộ hệ thống được thiết kế và triển khai theo kiến trúc Microservices phân tán hiện đại, tận dụng sức mạnh của hệ sinh thái Python, cơ sở dữ liệu quan hệ PostgreSQL 15, cơ sở dữ liệu vector chuyên dụng Qdrant và các công nghệ AI tiên tiến:")
    
    headers_infra = ["Công cụ / Thư viện", "Phân loại / Vai trò", "Ứng dụng cụ thể trong Hệ thống"]
    rows_infra = [
        ["Python 3.11", "Ngôn ngữ Backend chính", "Xây dựng toàn bộ logic xử lý nghiệp vụ cho Core Service (Port 8000) và Auth Service (Port 8001)."],
        ["FastAPI & Uvicorn", "High-performance Web Framework", "Xây dựng hệ thống RESTful API bất đồng bộ (async/await), tài liệu hóa tự động Swagger/OpenAPI."],
        ["PostgreSQL 15 & asyncpg", "Relational Database", "Lưu trữ dữ liệu người dùng, vai trò RBAC, danh mục môn học, quan hệ tiên quyết và bảng điểm sinh viên."],
        ["Qdrant Vector DB", "Vector Database chuyên dụng", "Lưu trữ các vector nhúng ngữ nghĩa (768 chiều), thực hiện tìm kiếm tương đồng vector với Cosine Distance."],
        ["Redis & Semantic Cache", "In-memory Cache & Job Queue", "Quản lý hàng đợi tác vụ xử lý tài liệu nền (Worker) và lưu trữ Semantic Cache phân lập theo sinh viên."],
        ["Sentence-Transformers", "Deep Embedding Toolkit", "Tải và thực thi mô hình keepitreal/vietnamese-sbert để vector hóa văn bản và Cross-Encoder Reranker."],
        ["LangChain Text Splitters", "Text Chunking Toolkit", "Phân đoạn văn bản đệ quy tiếng Việt (chunk_size=1024, chunk_overlap=20) theo cấu trúc ngữ nghĩa."],
        ["PyPDF & python-docx", "Document Parser", "Trích xuất tự động toàn bộ nội dung văn bản từ các tệp giáo trình PDF, đề cương và tài liệu Word (.docx)."],
        ["Google Generative AI", "Large Language Model (LLM)", "Tích hợp mô hình Gemini 1.5/2.0 Flash để tổng hợp ngữ cảnh RAG và sinh câu trả lời tiếng Việt chuẩn mực."],
        ["Next.js 14 & React", "Frontend Web Application", "Xây dựng giao diện tương tác người dùng đa thiết bị (Desktop & Mobile) thời gian thực qua REST API / SSE."]
    ]
    add_styled_table(doc, headers_infra, rows_infra, [1.8, 1.8, 2.9], "Bảng 1.6: Tổng hợp hạ tầng công nghệ và thư viện triển khai hệ thống")

    doc.add_page_break()
