"""Extra screenshots: dataset detail, chatbot config, teacher grades with student, prereq modal."""
from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import TimeoutError as PwTimeout
from playwright.sync_api import sync_playwright

from capture_ui_screenshots import (
    BASE,
    OUT,
    PASSWORD,
    VIEWPORT,
    hide_overlays,
    login,
    shot,
    wait_loaded,
)

CHATBOT_ID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
DATASET_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"
SV001_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"


def capture_teacher_filled() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT, locale="vi-VN")
        page = context.new_page()
        login(page, "gv01@eaut.edu.vn")

        page.goto(f"{BASE}/dashboard/grades?student_id={SV001_ID}", wait_until="domcontentloaded")
        wait_loaded(page, 1800)
        shot(page, "21_gv_quan_ly_diem.png")

        page.goto(f"{BASE}/dashboard/courses", wait_until="domcontentloaded")
        wait_loaded(page, 800)
        btn = page.get_by_role("button", name=re.compile(r"Xem tiên quyết")).nth(3)
        btn.click()
        page.wait_for_timeout(800)
        shot(page, "23b_gv_tien_quyet.png", full_page=False)
        page.keyboard.press("Escape")

        page.goto(f"{BASE}/dashboard/datasets/{DATASET_ID}", wait_until="domcontentloaded")
        wait_loaded(page, 1500)
        shot(page, "25_gv_chi_tiet_bo_du_lieu.png")

        context.close()
        browser.close()


def capture_admin_detail() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT, locale="vi-VN")
        page = context.new_page()
        login(page, "admin@eaut.edu.vn")

        page.goto(f"{BASE}/admin/chatbots/{CHATBOT_ID}", wait_until="domcontentloaded")
        wait_loaded(page, 1500)
        shot(page, "35_admin_cau_hinh_chatbot.png")

        page.goto(f"{BASE}/admin/chatbots/create", wait_until="domcontentloaded")
        wait_loaded(page, 1000)
        shot(page, "35b_admin_tao_chatbot.png")

        page.goto(f"{BASE}/dashboard/datasets/{DATASET_ID}", wait_until="domcontentloaded")
        wait_loaded(page, 1500)
        shot(page, "38b_admin_chi_tiet_bo_du_lieu.png")

        page.goto(f"{BASE}/admin/grades", wait_until="domcontentloaded")
        wait_loaded(page, 800)
        combo = page.locator(".ant-select").first
        combo.click()
        page.wait_for_timeout(500)
        page.keyboard.type("SV001", delay=40)
        page.wait_for_timeout(600)
        option = page.locator(".ant-select-item-option").filter(has_text=re.compile(r"SV001|Lê Hải Đăng")).first
        if option.count() > 0:
            option.click()
            wait_loaded(page, 1800)
        shot(page, "37_admin_bang_diem.png")

        context.close()
        browser.close()


def capture_student_sources() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT, locale="vi-VN")
        page = context.new_page()
        login(page, "sv01@eaut.edu.vn")
        page.goto(f"{BASE}/dashboard/chat", wait_until="domcontentloaded")
        wait_loaded(page, 1200)
        # Open the latest conversation in sidebar
        item = page.get_by_text("Em chào cô ạ.").first
        try:
            item.click(timeout=4000)
            wait_loaded(page, 1500)
        except PwTimeout:
            pass
        src = page.get_by_text(re.compile(r"Tài liệu tham khảo"))
        if src.count() > 0:
            src.first.click()
            page.wait_for_timeout(800)
            shot(page, "12b_sv_chat_nguon_tham_khao.png", full_page=False)
        else:
            print("no source citations visible")
        context.close()
        browser.close()


if __name__ == "__main__":
    print("OUT =", OUT)
    for fn in (capture_teacher_filled, capture_admin_detail, capture_student_sources):
        try:
            fn()
        except Exception as exc:
            print(f"{fn.__name__} FAILED:", exc)
    files = sorted(OUT.glob("*.png"))
    print(f"done: {len(files)} png files")
    for f in files:
        print(f"  {f.name:40s} {f.stat().st_size:8d}")
