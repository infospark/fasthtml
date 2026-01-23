from pathlib import Path

from playwright.sync_api import Page, expect

from dropadoc import DROPADOC_URL

# Get the directory where this test_file.py is located
current_dir = Path(__file__).parent
project_root = current_dir.parent

def test_onboarding_e2e(page: Page, server: None) -> None:
    # 1. Navigate to your local dev server
    page.goto(f"http://localhost:5001{DROPADOC_URL}")

    drop_box = page.locator("#drop_box")
    expect(drop_box).to_contain_text("Drag & Drop your documents here")

    upload_btn = drop_box.locator("#upload-btn")
    expect(upload_btn).to_have_text("Select Files")

def test_onboarding_e2e_upload_file(page: Page, server: None) -> None:
    page.goto(f"http://localhost:5001{DROPADOC_URL}")

    # 1. Verify initial state
    drop_box = page.locator("#drop_box")
    expect(drop_box).to_contain_text("Drag & Drop your documents here")

    # 3. Perform the "Drop" action
    # We find the file path relative to this test file
    file_path = current_dir / "assets" / "sample.pdf"

    # Playwright's set_input_files works even if the input is hidden/styled
    # It simulates selecting the file via the OS dialog or dropping it
    page.set_input_files("#file-input", file_path)

    # 5. Assert the file landed in the inbox
    # We check the UI first
    expect(page.locator("#upload-status")).to_contain_text("Successfully uploaded")

    # Then we check the actual file system
    inbox_path = project_root / "inbox" / "sample.pdf"
    assert inbox_path.exists(), f"File not found at {inbox_path}"
