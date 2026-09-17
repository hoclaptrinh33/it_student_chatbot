"""Capture UI screenshots for the project report into Report/image."""
from __future__ import annotations

import re
import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PwTimeout
from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
OUT = Path(__file__).resolve().parent / "image"
OUT.mkdir(parents=True, exist_ok=True)

PASSWORD = "Pass123"
VIEWPORT = {"width": 1440, "height": 900}


def shot(page, name: str, full_page: bool = True, delay_ms: int = 400) -> None:
    page.wait_for_timeout(delay_ms)
    hide_overlays(page)
    dest = OUT / name
    page.screenshot(path=str(dest), full_page=full_page, animations="disabled")
    print(f"saved {dest.name} ({dest.stat().st_size} bytes)")


def hide_overlays(page) -> None:
    page.evaluate(
        """
        () => {
          document.querySelectorAll('.ant-message, .ant-notification, .ant-spin-fullscreen')
            .forEach(el => { el.style.display = 'none'; });
        }
        """
    )


def wait_loaded(page, extra_ms: int = 600) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=12000)
    except PwTimeout:
        page.wait_for_load_state("domcontentloaded", timeout=8000)
    try:
        page.locator(".ant-spin-spinning").first.wait_for(state="hidden", timeout=8000)
    except PwTimeout:
        pass
    page.wait_for_timeout(extra_ms)


def login(page, email: str) -> None:
    page.goto(f"{BASE}/auth/login", wait_until="domcontentloaded")
    wait_loaded(page, 400)
    page.get_by_placeholder(re.compile(r"Email")).fill(email)
    page.get_by_placeholder("Mật khẩu").fill(PASSWORD)
    page.get_by_role("button", name="Đăng nhập").click()
    page.wait_for_url(re.compile(r"/dashboard"), timeout=20000)
    wait_loaded(page, 800)
    hide_overlays(page)


def logout_if_needed(page) -> None:
    page.evaluate(
        """
        () => {
          localStorage.clear();
          sessionStorage.clear();
        }
        """
    )
    page.context.clear_cookies()


def capture_auth(browser) -> None:
    context = browser.new_context(viewport=VIEWPORT, locale="vi-VN")
    page = context.new_page()

    page.goto(f"{BASE}/auth/login", wait_until="domcontentloaded")
    wait_loaded(page)
    shot(page, "01_dang_nhap.png", full_page=False)

    page.goto(f"{BASE}/auth/register", wait_until="domcontentloaded")
    wait_loaded(page)
    shot(page, "02_dang_ky.png", full_page=False)

    page.goto(f"{BASE}/auth/forgot-password", wait_until="domcontentloaded")
    wait_loaded(page)
    shot(page, "03_quen_mat_khau.png", full_page=False)

    # Mobile login
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{BASE}/auth/login", wait_until="domcontentloaded")
    wait_loaded(page)
    shot(page, "01b_dang_nhap_mobile.png", full_page=False)

    context.close()


def wait_chat_ready(page, timeout_ms: int = 90000) -> None:
    page.wait_for_function(
        """() => {
          const el = document.querySelector('textarea[placeholder*="Nhập câu hỏi"]');
          return !!(el && !el.disabled);
        }""",
        timeout=timeout_ms,
    )


def send_chat(page, question: str, timeout_ms: int = 90000) -> bool:
    box = page.get_by_placeholder(re.compile(r"Nhập câu hỏi"))
    box.wait_for(timeout=15000)
    wait_chat_ready(page, timeout_ms)
    box.fill(question)
    send_btn = page.locator("button").filter(has=page.locator(".anticon-send")).first
    if send_btn.count() == 0:
        page.get_by_role("button", name=re.compile(r"Gửi|Send", re.I)).first.click()
    else:
        send_btn.click()
    try:
        page.wait_for_function(
            """() => {
              const el = document.querySelector('textarea[placeholder*="Nhập câu hỏi"]');
              return !!(el && el.disabled);
            }""",
            timeout=8000,
        )
    except PwTimeout:
        pass
    wait_chat_ready(page, timeout_ms)
    page.wait_for_timeout(800)
    return True


def capture_student(browser) -> None:
    context = browser.new_context(viewport=VIEWPORT, locale="vi-VN")
    page = context.new_page()
    login(page, "sv01@eaut.edu.vn")

    page.goto(f"{BASE}/dashboard/chat", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "10_sv_chat_trang_chu.png", full_page=False)

    try:
        wait_chat_ready(page, 20000)
        ok = send_chat(page, "Em chào cô ạ.", timeout_ms=40000)
        print("student greeting chat:", ok)
        shot(page, "11_sv_chat_chao_hoi.png", full_page=False)
    except Exception as exc:
        print("greeting chat failed:", exc)
        shot(page, "11_sv_chat_chao_hoi.png", full_page=False)

    try:
        ok2 = send_chat(
            page,
            "E muốn theo đường dev web thì học kì này lên học những môn nào",
            timeout_ms=120000,
        )
        print("student course-advice chat:", ok2)
        shot(page, "12_sv_chat_tu_van_mon.png", full_page=False)
    except Exception as exc:
        print("course-advice chat failed:", exc)
        shot(page, "12_sv_chat_tu_van_mon.png", full_page=False)

    try:
        page.get_by_role("button", name=re.compile(r"Live Voice")).click(timeout=4000)
        page.wait_for_timeout(1200)
        shot(page, "18_sv_live_voice.png", full_page=False)
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)
    except Exception as exc:
        print("live voice skip:", exc)

    page.goto(f"{BASE}/dashboard/eligible-courses", wait_until="domcontentloaded")
    wait_loaded(page, 1000)
    shot(page, "13_sv_mon_du_dieu_kien.png")

    page.goto(f"{BASE}/dashboard/transcript", wait_until="domcontentloaded")
    wait_loaded(page, 1000)
    shot(page, "14_sv_bang_diem.png")

    page.goto(f"{BASE}/dashboard/materials", wait_until="domcontentloaded")
    wait_loaded(page, 1000)
    shot(page, "15_sv_tai_lieu.png")

    page.goto(f"{BASE}/dashboard/profile", wait_until="domcontentloaded")
    wait_loaded(page, 800)
    shot(page, "16_sv_ho_so.png")

    # Mobile chat
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{BASE}/dashboard/chat", wait_until="domcontentloaded")
    wait_loaded(page, 1000)
    shot(page, "17_sv_chat_mobile.png", full_page=False)

    context.close()


def capture_teacher(browser) -> None:
    context = browser.new_context(viewport=VIEWPORT, locale="vi-VN")
    page = context.new_page()
    login(page, "gv01@eaut.edu.vn")

    page.goto(f"{BASE}/dashboard", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "20_gv_bang_dieu_khien.png")

    page.goto(f"{BASE}/dashboard/grades", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "21_gv_quan_ly_diem.png")

    page.goto(f"{BASE}/dashboard/materials", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "22_gv_tai_lieu.png")

    page.goto(f"{BASE}/dashboard/courses", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "23_gv_mon_hoc.png")

    page.goto(f"{BASE}/dashboard/datasets", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "24_gv_bo_du_lieu.png")

    # Open first dataset if a row/card is clickable
    opened = False
    for sel in [
        "a[href*='/dashboard/datasets/']",
        ".ant-card",
        "tr.ant-table-row",
    ]:
        loc = page.locator(sel).first
        if loc.count() > 0:
            try:
                loc.click(timeout=3000)
                page.wait_for_url(re.compile(r"/dashboard/datasets/.+"), timeout=8000)
                wait_loaded(page, 1000)
                shot(page, "25_gv_chi_tiet_bo_du_lieu.png")
                opened = True
                break
            except Exception as exc:
                print("dataset open skip:", exc)
    if not opened:
        print("no dataset detail opened")

    page.goto(f"{BASE}/dashboard/chat", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "26_gv_tro_ly_ai.png", full_page=False)

    context.close()


def capture_admin(browser) -> None:
    context = browser.new_context(viewport=VIEWPORT, locale="vi-VN")
    page = context.new_page()
    login(page, "admin@eaut.edu.vn")

    page.goto(f"{BASE}/dashboard", wait_until="domcontentloaded")
    wait_loaded(page, 1500)
    shot(page, "30_admin_bang_dieu_khien.png")

    page.goto(f"{BASE}/admin/users", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "31_admin_nguoi_dung.png")

    page.goto(f"{BASE}/admin/roles", wait_until="domcontentloaded")
    wait_loaded(page, 1000)
    shot(page, "32_admin_vai_tro.png")

    page.goto(f"{BASE}/admin/permissions", wait_until="domcontentloaded")
    wait_loaded(page, 1000)
    shot(page, "33_admin_quyen_han.png")

    page.goto(f"{BASE}/admin/chatbots", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "34_admin_chatbots.png")

    opened = False
    for sel in ["a[href*='/admin/chatbots/']", "tr.ant-table-row", ".ant-card"]:
        loc = page.locator(sel).first
        if loc.count() > 0:
            try:
                loc.click(timeout=3000)
                page.wait_for_url(re.compile(r"/admin/chatbots/.+"), timeout=8000)
                wait_loaded(page, 1200)
                shot(page, "35_admin_cau_hinh_chatbot.png")
                opened = True
                break
            except Exception as exc:
                print("chatbot open skip:", exc)
    if not opened:
        print("no chatbot detail opened")

    page.goto(f"{BASE}/admin/courses", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "36_admin_mon_hoc.png")

    page.goto(f"{BASE}/admin/grades", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "37_admin_bang_diem.png")

    page.goto(f"{BASE}/dashboard/datasets", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "38_admin_bo_du_lieu.png")

    page.goto(f"{BASE}/admin/settings", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "39_admin_cai_dat.png")

    page.goto(f"{BASE}/dashboard/chat", wait_until="domcontentloaded")
    wait_loaded(page, 1200)
    shot(page, "40_admin_tro_chuyen.png", full_page=False)

    context.close()


def main() -> None:
    print("OUT =", OUT)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        skip_auth = any((OUT / n).exists() for n in ("01_dang_nhap.png", "02_dang_ky.png"))
        if skip_auth:
            print("skip auth screenshots (already exist)")
        else:
            capture_auth(browser)
        capture_student(browser)
        capture_teacher(browser)
        capture_admin(browser)
        browser.close()
    files = sorted(OUT.glob("*.png"))
    print(f"done: {len(files)} png files")
    for f in files:
        print(f"  {f.name:40s} {f.stat().st_size:8d}")


if __name__ == "__main__":
    main()
