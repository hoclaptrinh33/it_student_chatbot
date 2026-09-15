"""Generate short demo syllabus/slide PDFs (stdlib only, Helvetica/ASCII)."""
from __future__ import annotations

from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent

MATERIALS = [
    (
        "INT1101_syllabus.pdf",
        "INT1101 Syllabus - Introduction to Programming",
        [
            "Course: INT1101 Nhap mon lap trinh (3 credits). Track: GENERAL. Semester 1.",
            "Language: C/Python. Topics: syntax, data types, control flow, functions.",
            "Assessment: labs 30%, midterm 20%, final exam 50%.",
            "This syllabus belongs to course INT1101 only. Do not confuse with INT1204 OOP.",
            "Next courses: INT1201 Data Structures (PREREQUISITE INT1101), INT1204 OOP.",
        ],
    ),
    (
        "INT1101_slides.pdf",
        "INT1101 Slides - Weeks 1-8",
        [
            "INT1101 lecture slides. Week 1: variables, types, IO.",
            "Week 2-3: if/else, loops. Week 4-5: functions and scope.",
            "Week 6-7: arrays/lists. Week 8: file IO and debugging.",
            "Practice in C or Python. Course code INT1101. Material type SLIDE.",
        ],
    ),
    (
        "INT1203_syllabus.pdf",
        "INT1203 Syllabus - Computer Architecture",
        [
            "Course: INT1203 Kien truc may tinh (3 credits). Track: GENERAL. Semester 2.",
            "Topics: CPU, memory hierarchy, I/O, assembly, instruction pipeline.",
            "Failed INT1203 blocks INT2101 Operating Systems (hard PREREQUISITE).",
            "INT2102 Computer Networks lists INT1203 as PREVIOUS (soft).",
            "Retake INT1203 if status is FAILED before taking INT2101.",
        ],
    ),
    (
        "INT1203_slides.pdf",
        "INT1203 Slides - CPU Memory IO",
        [
            "INT1203 slides. CPU datapath, registers, ALU, control unit.",
            "Memory: cache, RAM, virtual memory overview.",
            "I/O buses and interrupts. Assembly addressing modes.",
            "Pipeline hazards. Course code INT1203. Material type SLIDE.",
        ],
    ),
    (
        "INT2104_syllabus.pdf",
        "INT2104 Syllabus - Web Programming",
        [
            "Course: INT2104 Lap trinh Web (3 credits). Track: WEB. Semester 3.",
            "Hard PREREQUISITE: INT1204 Object-oriented Programming.",
            "Topics: HTML, CSS, JavaScript, HTTP, REST, basic backend.",
            "Next WEB course: INT2204 Phat trien ung dung Web requires INT2104 PASSED",
            "and INT1202 Database PASSED. Do not register INT2204 while INT2104 is IN_PROGRESS.",
            "INT3104 Advanced Web requires INT2204. Course code INT2104.",
        ],
    ),
    (
        "INT2104_slides.pdf",
        "INT2104 Slides - HTML CSS JS REST",
        [
            "INT2104 slides. Week 1-2: HTML5 and CSS layout.",
            "Week 3-4: JavaScript DOM and fetch. Week 5: HTTP methods and REST.",
            "Week 6-8: basic backend routes and JSON APIs.",
            "Career track WEB. Course code INT2104. Material type SLIDE.",
        ],
    ),
    (
        "INT2202_syllabus.pdf",
        "INT2202 Syllabus - Artificial Intelligence",
        [
            "Course: INT2202 Tri tue nhan tao (3 credits). Track: AI. Semester 4.",
            "Hard PREREQUISITE: INT1201 Data Structures. PREVIOUS: INT1103 Linear Algebra.",
            "Topics: search, heuristics, knowledge, agents, intro machine learning.",
            "Next AI course: INT3101 Machine Learning requires INT2202 PASSED and INT1103 PASSED.",
            "INT2202 is not a Web-track course. Do not treat it as INT2104/INT2204.",
        ],
    ),
    (
        "INT2202_slides.pdf",
        "INT2202 Slides - Search Agents ML intro",
        [
            "INT2202 slides. Uninformed and heuristic search.",
            "Knowledge representation and intelligent agents.",
            "Intro to supervised learning. Course code INT2202. Track AI.",
            "Follow-on: INT3101 Hoc may. Material type SLIDE.",
        ],
    ),
]


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(title: str, lines: list[str]) -> bytes:
    ops = [
        "BT",
        "/F1 16 Tf",
        "50 740 Td",
        f"({_escape(title)}) Tj",
        "/F1 11 Tf",
    ]
    for line in lines:
        ops.append("0 -18 Td")
        ops.append(f"({_escape(line)}) Tj")
    ops.append("ET")
    stream = "\n".join(ops).encode("latin-1")

    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
        ),
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objs, start=1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")

    xref_pos = len(out)
    out.extend(f"xref\n0 {len(objs) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(
        (
            f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(out)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, title, lines in MATERIALS:
        path = OUT_DIR / filename
        path.write_bytes(build_pdf(title, lines))
        print(f"wrote {path.name} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
