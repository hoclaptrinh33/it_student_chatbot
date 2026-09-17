# -*- coding: utf-8 -*-
"""
make_full_report.py
Tạo báo cáo BTL Trí tuệ nhân tạo toàn diện và chuẩn mực:
- Đề tài: XÂY DỰNG CHƯƠNG TRÌNH HỎI ĐÁP BẰNG NGÔN NGỮ TỰ NHIÊN HỖ TRỢ CHỌN MÔN HỌC VÀ TÀI LIỆU HỌC TẬP CHO SINH VIÊN KHOA CNTT
- Font: Times New Roman 100%
- Màu sắc: Chữ đen nền trắng (RGB 0, 0, 0)
- Tích hợp toàn diện Báo Cáo Tổng Quan Học Máy vào Chương 1
- Đầy đủ Chương 2, Chương 3, Kết luận, Tài liệu tham khảo, Phụ lục
- Nhúng toàn bộ 35 hình ảnh giao diện từ Report/image với caption chuẩn
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

BLACK = RGBColor(0, 0, 0)
FONT_NAME = 'Times New Roman'

def set_run_font(run, name=FONT_NAME, size_pt=13, bold=False, italic=False, color=BLACK):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:eastAsia'), name)
    rFonts.set(qn('w:cs'), name)
    rPr.append(rFonts)

def add_p(doc, text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.3, first_indent=0.3):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if first_indent > 0 and align == WD_ALIGN_PARAGRAPH.JUSTIFY:
        p.paragraph_format.first_line_indent = Inches(first_indent)
    if text:
        r = p.add_run(text)
        set_run_font(r, FONT_NAME, 13, False, False, BLACK)
    return p

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    set_run_font(r, FONT_NAME, 15, bold=True, color=BLACK)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    set_run_font(r, FONT_NAME, 13.5, bold=True, color=BLACK)
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    set_run_font(r, FONT_NAME, 13, bold=True, italic=True, color=BLACK)
    return p

def add_bullet(doc, bold_prefix, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.left_indent = Inches(0.25)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    r_bullet = p.add_run("• ")
    set_run_font(r_bullet, FONT_NAME, 13, bold=True, color=BLACK)
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix + ": ")
        set_run_font(r_pre, FONT_NAME, 13, bold=True, color=BLACK)
    
    r_txt = p.add_run(text)
    set_run_font(r_txt, FONT_NAME, 13, bold=False, color=BLACK)
    return p

def set_table_borders(table):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>\n'
            f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D0D0D0"/>\n'
            f'  <w:insideV w:val="none"/>\n'
            f'  <w:left w:val="none"/>\n'
            f'  <w:right w:val="none"/>\n'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)

def add_styled_table(doc, headers, rows, col_widths=None, caption=""):
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(8)
        p_cap.paragraph_format.space_after = Pt(4)
        r = p_cap.add_run(caption)
        set_run_font(r, FONT_NAME, 11, bold=True, color=BLACK)
        
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)
    
    # Header row
    hdr_cells = table.rows[0].cells
    for i, h_text in enumerate(headers):
        hdr_cells[i].text = ""
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(h_text)
        set_run_font(r, FONT_NAME, 11, bold=True, color=BLACK)
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F5F5F5"/>')
        hdr_cells[i]._element.get_or_add_tcPr().append(shd)
        
    # Data rows
    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = ""
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx > 0 and len(str(val)) > 20 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(str(val))
            set_run_font(r, FONT_NAME, 11, bold=False, color=BLACK)
            
    if col_widths and len(col_widths) == len(headers):
        for row in table.rows:
            for c_idx, w in enumerate(col_widths):
                row.cells[c_idx].width = Inches(w)
                
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(2)
    p_after.paragraph_format.space_after = Pt(6)
    return table

def add_figure(doc, img_path, caption, width_in=5.6):
    if not os.path.exists(img_path):
        print(f"Warning: Image {img_path} not found.")
        return None
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(2)
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(width_in))
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(8)
    r_cap = p_cap.add_run(caption)
    set_run_font(r_cap, FONT_NAME, 11, italic=True, color=BLACK)
    return p_img

def add_code_snippet(doc, code_str, caption=""):
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_cap.paragraph_format.space_before = Pt(6)
        p_cap.paragraph_format.space_after = Pt(2)
        r = p_cap.add_run(caption)
        set_run_font(r, FONT_NAME, 11, bold=True, italic=True, color=BLACK)
        
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    cell.width = Inches(6.0)
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="888888"/>\n'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="888888"/>\n'
        f'  <w:left w:val="single" w:sz="12" w:space="0" w:color="000000"/>\n'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="888888"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="FAFAFA"/>')
    tcPr.append(shd)
    
    cell.text = ""
    for line in code_str.strip().split('\n'):
        p = cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(line)
        set_run_font(r, 'Consolas', 9.5, False, False, BLACK)
        
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(2)
    p_after.paragraph_format.space_after = Pt(6)

print("Setup completed. Ready to build full report.")
