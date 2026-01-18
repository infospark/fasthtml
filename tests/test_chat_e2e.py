from playwright.sync_api import Page, expect

from chat import CHAT_URL


def test_chat_e2e(page: Page, server: None) -> None:
    # 1. Navigate to your local dev server
    # (Ensure your FastHTML app is running on 5001)
    page.goto(f"http://localhost:5001{CHAT_URL}")

    # 2. Verify Initial State
    # Expect there to be one or more company input fields
    prompt_input = page.locator('input[name="prompt"]')
    # Type "Well hello prompty!"
    prompt_input.fill("Well hello prompty!")
    # Press the submit button
    page.click("button#submit-btn")

    # Find the response box
    response_box = page.locator("div#response-box-content")
    # Expect the response box to contain "hello"
    expect(response_box).to_have_text("hello")
    # Expect the response box to contain "world"
    expect(response_box).to_have_text("hello world.")

    expect(response_box).to_contain_text("End")
