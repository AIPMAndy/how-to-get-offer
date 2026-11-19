"""Chromium mobile/desktop regression gate; not an iOS/Android device certification.

Run: python build.py && python -m http.server 8765 &
     python tests/browser_smoke.py --base-url http://127.0.0.1:8765/
"""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "browser-qa"


def assert_no_overflow(page, label):
    dimensions = page.evaluate("""() => ({
        viewport: document.documentElement.clientWidth,
        document: document.documentElement.scrollWidth,
        body: document.body.scrollWidth
    })""")
    assert dimensions["document"] <= dimensions["viewport"] + 2, (label, dimensions)
    assert dimensions["body"] <= dimensions["viewport"] + 2, (label, dimensions)


def run(base_url):
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for label, width, height in (
                ("mobile-390", 390, 844),
                ("mobile-360", 360, 780),
                ("desktop-1280", 1280, 900),
            ):
                ctx = browser.new_context(viewport={"width": width, "height": height},
                                          device_scale_factor=1, locale="zh-CN",
                                          accept_downloads=True)
                page = ctx.new_page()
                failures = []
                page.on("pageerror", lambda error: failures.append(str(error)))
                response = page.goto(base_url, wait_until="networkidle")
                assert response is not None and response.status == 200, (label, "homepage status")
                assert page.title().startswith("社招拿 Offer"), (label, page.title())
                page.locator("#taskList .task").first.wait_for()
                assert page.locator("#taskList .task").count() == 100, label
                assert "0 / 100" in page.locator("#progressNum").inner_text(), label
                assert page.locator("#salaryResults .salary-row").count() == 2, label
                assert page.locator("#copyWechat").count() == 1, label
                assert page.locator("a[href$='how-to-get-offer-guide.pdf']").count() >= 1, label
                assert_no_overflow(page, label + "/initial")

                # 100-item task list must be usable, persisted locally, and searchable.
                page.locator("#taskList .task input[type=checkbox]").first.check()
                assert "1 / 100" in page.locator("#progressNum").inner_text(), label
                page.reload(wait_until="networkidle")
                assert page.locator("#taskList .task input[type=checkbox]").first.is_checked(), label
                page.locator("#taskSearch").fill("term-that-cannot-match-any-task-zzzz")
                assert page.locator("#taskList .task").count() == 0, label
                page.locator("#taskSearch").fill("")
                assert page.locator("#taskList .task").count() == 100, label

                # The uncompleted-only view respects saved progress; reset restores all 100 tasks.
                page.locator("#pendingOnly").check()
                assert page.locator("#taskList .task").count() == 99, label
                page.locator("#taskSearch").fill("term-that-cannot-match-any-task-zzzz")
                assert page.locator("#taskEmpty").is_visible(), label
                page.locator("#resetTaskFilters").click()
                assert page.locator("#taskList .task").count() == 100, label
                assert not page.locator("#pendingOnly").is_checked(), label
                assert page.locator("#taskSearch").evaluate("(el) => document.activeElement === el"), label
                with page.expect_download() as task_file_info:
                    page.locator("#taskTxtExport").click()
                task_export = Path(task_file_info.value.path()).read_text(encoding="utf-8-sig")
                assert "当前筛选共 100 项" in task_export, label
                assert "微信：AIPMAndy" in task_export, label
                assert "执行：" in task_export and "凭证：" in task_export, label
                assert "<img src=x" not in task_export, label

                # A user-provided company name must be rendered as text, never as HTML.
                suspicious = "<img src=x onerror=alert(1)>"
                page.locator("#jobCompany").fill(suspicious)
                page.locator("#jobRole").fill("测试产品岗位")
                page.locator("#jobForm button[type=submit]").click()
                assert suspicious in page.locator("#jobRows").inner_text(), label
                assert page.locator("#jobRows img").count() == 0, label
                assert page.locator("#jobsAll").inner_text().strip() == "1", label
                page.reload(wait_until="networkidle")
                assert page.locator("#jobsAll").inner_text().strip() == "1", label
                with page.expect_download() as download_info:
                    page.locator("#csvExport").click()
                download = download_info.value
                assert download.suggested_filename.endswith(".csv"), label

                # Check accessible action, not clipboard permission state on an emulator.
                page.locator("#copyWechat").click()
                page.wait_for_function("""() => document.querySelector("#copyWechat").textContent.includes("AIPMAndy")""", timeout=5000)
                assert_no_overflow(page, label + "/after-interactions")
                page.screenshot(path=str(OUT / (label + ".png")), full_page=True)
                assert not failures, (label, failures)
                # Published Markdown reader has its own canonical, author and source trail.
                chapter = page.goto(base_url + "guides/00-start-here.html", wait_until="networkidle")
                assert chapter is not None and chapter.status == 200, (label, "reader status")
                assert page.locator('link[rel="canonical"]').get_attribute("href") == base_url + "guides/00-start-here.html", label
                assert page.locator('script[type="application/ld+json"]').count() == 1, label
                assert page.get_by_role("link", name="公司官网 ↗").count() == 1, label
                assert page.get_by_role("link", name="研究来源及历史核验日").count() == 1, label
                assert_no_overflow(page, label + "/reader")
                page.screenshot(path=str(OUT / (label + "-reader.png")), full_page=True)
                print(f"PASS {label}: 100 tasks, local persistence, job form, CSV, XSS escaping, layout")
                ctx.close()
        finally:
            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8765/")
    args = parser.parse_args()
    run(args.base_url)
