"""Upload demo PDFs and bind them to dataset dddddddd-... (needs running stack).

Usage:
    python document/demo_materials/ingest_demo_materials.py

Env:
    AUTH_URL   default http://localhost:8001
    CORE_URL   default http://localhost:8000
    AUTH_EMAIL default admin@fit.edu.vn
    AUTH_PASSWORD default Pass123
    DATASET_ID default dddddddd-dddd-dddd-dddd-dddddddddddd
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
DATASET_ID = os.environ.get("DATASET_ID", "dddddddd-dddd-dddd-dddd-dddddddddddd")
AUTH_URL = os.environ.get("AUTH_URL", "http://localhost:8001").rstrip("/")
CORE_URL = os.environ.get("CORE_URL", "http://localhost:8000").rstrip("/")
EMAIL = os.environ.get("AUTH_EMAIL", "admin@fit.edu.vn")
PASSWORD = os.environ.get("AUTH_PASSWORD", "Pass123")

FILES = [
    ("INT1101", "SYLLABUS", "INT1101_syllabus.pdf"),
    ("INT1101", "SLIDE", "INT1101_slides.pdf"),
    ("INT1203", "SYLLABUS", "INT1203_syllabus.pdf"),
    ("INT1203", "SLIDE", "INT1203_slides.pdf"),
    ("INT2104", "SYLLABUS", "INT2104_syllabus.pdf"),
    ("INT2104", "SLIDE", "INT2104_slides.pdf"),
    ("INT2202", "SYLLABUS", "INT2202_syllabus.pdf"),
    ("INT2202", "SLIDE", "INT2202_slides.pdf"),
]


def _request(url: str, *, data: bytes | None = None, headers: dict[str, str] | None = None, method: str = "GET") -> Any:
    req = Request(url, data=data, headers=headers or {}, method=method)
    with urlopen(req, timeout=30) as resp:
        raw = resp.read()
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))


def login() -> str:
    payload = json.dumps({"email": EMAIL, "password": PASSWORD}).encode("utf-8")
    body = _request(
        f"{AUTH_URL}/api/auth/login",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    token = body.get("access_token") if isinstance(body, dict) else None
    if not token:
        raise RuntimeError(f"login did not return access_token: {body}")
    return token


def course_id(token: str, code: str) -> str:
    qs = urlencode({"code": code})
    rows = _request(
        f"{CORE_URL}/api/v1/courses?{qs}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if not rows:
        raise RuntimeError(f"course {code} not found")
    return rows[0]["id"]


def upload_file(token: str, path: Path) -> str:
    boundary = "----DemoBoundary" + uuid.uuid4().hex
    file_bytes = path.read_bytes()
    parts = [
        f"--{boundary}\r\n".encode("ascii"),
        (
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
            "Content-Type: application/pdf\r\n\r\n"
        ).encode("ascii"),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("ascii"),
    ]
    body = b"".join(parts)
    result = _request(
        f"{CORE_URL}/api/v1/files/upload",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    file_id = result.get("id") if isinstance(result, dict) else None
    if not file_id:
        raise RuntimeError(f"upload failed for {path.name}: {result}")
    return file_id


def add_to_dataset(token: str, file_id: str, cid: str, material_type: str) -> Any:
    payload = json.dumps(
        {"file_ids": [file_id], "course_id": cid, "material_type": material_type}
    ).encode("utf-8")
    return _request(
        f"{CORE_URL}/api/v1/datasets/{DATASET_ID}/files",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )


def curl_help() -> str:
    return f"""
Stack is not up or ingest failed. PDFs are already committed under document/demo_materials/.
When Auth+Core+worker are running:

  python document/demo_materials/ingest_demo_materials.py

Or curl (repeat per file, bind INT1101/INT1203/INT2104/INT2202):

  TOKEN=$(curl -s {AUTH_URL}/api/auth/login -H "Content-Type: application/json" \\
    -d "{{\\"email\\":\\"{EMAIL}\\",\\"password\\":\\"{PASSWORD}\\"}}" | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
  COURSE=$(curl -s "{CORE_URL}/api/v1/courses?code=INT2104" -H "Authorization: Bearer $TOKEN" | python -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")
  FILE_ID=$(curl -s {CORE_URL}/api/v1/files/upload -H "Authorization: Bearer $TOKEN" \\
    -F "file=@document/demo_materials/INT2104_syllabus.pdf;type=application/pdf" | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
  curl -s {CORE_URL}/api/v1/datasets/{DATASET_ID}/files -H "Authorization: Bearer $TOKEN" \\
    -H "Content-Type: application/json" \\
    -d "{{\\"file_ids\\":[\\"$FILE_ID\\"],\\"course_id\\":\\"$COURSE\\",\\"material_type\\":\\"SYLLABUS\\"}}"
""".strip()


def main() -> int:
    missing = [name for _, _, name in FILES if not (HERE / name).is_file()]
    if missing:
        print("Missing PDFs:", ", ".join(missing), file=sys.stderr)
        print("Run: python document/demo_materials/generate_pdfs.py", file=sys.stderr)
        return 1
    try:
        token = login()
        cache: dict[str, str] = {}
        for code, material_type, name in FILES:
            cid = cache.get(code) or course_id(token, code)
            cache[code] = cid
            file_id = upload_file(token, HERE / name)
            result = add_to_dataset(token, file_id, cid, material_type)
            print(f"{name} -> file_id={file_id} course={code} {material_type} dataset={DATASET_ID}")
            skipped = result.get("skipped") if isinstance(result, dict) else None
            if skipped:
                print(f"  skipped: {skipped}")
        print("Ingest queued. Worker must be running to chunk into Qdrant.")
        return 0
    except (URLError, HTTPError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Live ingest skipped/failed: {exc}", file=sys.stderr)
        print(curl_help(), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
