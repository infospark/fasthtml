from pathlib import Path

from playwright.sync_api import Page, expect

from dragadoc import DROPADOC_URL

# Get the directory where this test_file.py is located
current_dir = Path(__file__).parent

def test_onboarding_e2e(page: Page, server: None) -> None:
    # 1. Navigate to your local dev server
    page.goto(f"http://localhost:5001{DROPADOC_URL}")

    drop_box = page.locator("#drop_box")
    expect(drop_box).to_contain_text("Drag & Drop your documents here")

    upload_btn = drop_box.locator("#upload-btn")
    expect(upload_btn).to_have_text("Select Files")
