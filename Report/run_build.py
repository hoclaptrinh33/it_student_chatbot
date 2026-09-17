# -*- coding: utf-8 -*-
"""
run_build.py
Master script tổng hợp và tạo file Báo cáo Word hoàn chỉnh:
Report/BTL_TTNT_NHOM_15.docx
"""

import os
import sys
import io

# Đảm bảo in UTF-8 không bị lỗi mã trang trên Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Thêm thư mục hiện tại vào sys.path
report_dir = os.path.dirname(os.path.abspath(__file__))
if report_dir not in sys.path:
    sys.path.insert(0, report_dir)

from make_full_report import FONT_NAME, BLACK
from content_cover import build_cover_and_preamble
from content_intro_ch1 import build_introduction_and_chapter_1
from content_ch2 import build_chapter_2
from content_ch3_conclusion import build_chapter_3_and_conclusion

def build_full_report(output_path):
    print("=== BẮT ĐẦU KHỞI TẠO BÁO CÁO WORD ===")
    doc = docx.Document()
    
    # Thiết lập căn lề chuẩn học thuật Việt Nam
    # Top: 2.0 cm, Bottom: 2.0 cm, Left: 3.0 cm, Right: 2.0 cm
    section = doc.sections[0]
    section.top_margin = Inches(0.79)      # 2.0 cm
    section.bottom_margin = Inches(0.79)   # 2.0 cm
    section.left_margin = Inches(1.18)     # 3.0 cm
    section.right_margin = Inches(0.79)    # 2.0 cm
    
    # Thiết lập mặc định Style Normal
    style_normal = doc.styles['Normal']
    style_normal.font.name = FONT_NAME
    style_normal.font.size = Pt(13)
    style_normal.font.color.rgb = BLACK
    
    rPr = style_normal._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), FONT_NAME)
    rFonts.set(qn('w:hAnsi'), FONT_NAME)
    rFonts.set(qn('w:eastAsia'), FONT_NAME)
    rFonts.set(qn('w:cs'), FONT_NAME)
    rPr.append(rFonts)
    
    print("[1/4] Xây dựng Trang bìa, Lời cảm ơn, Mục lục, Danh mục từ viết tắt...")
    build_cover_and_preamble(doc)
    
    print("[2/4] Xây dựng Phần mở đầu & Chương 1 (Cơ sở lý thuyết & Báo cáo Học máy)...")
    build_introduction_and_chapter_1(doc)
    
    print("[3/4] Xây dựng Chương 2 (Phân tích, 4 Thuật toán, Dataset & 35 Hình ảnh giao diện)...")
    build_chapter_2(doc)
    
    print("[4/4] Xây dựng Chương 3, Kết luận, Tài liệu tham khảo & Phụ lục GitHub...")
    build_chapter_3_and_conclusion(doc)
    
    print(f"Đang lưu tệp Word tại: {output_path}...")
    doc.save(output_path)
    print(">>> TẠO BÁO CÁO BTL_TTNT_NHOM_15.docx THÀNH CÔNG! <<<")

if __name__ == "__main__":
    out_file = os.path.join(report_dir, "BTL_TTNT_NHOM_15.docx")
    build_full_report(out_file)
