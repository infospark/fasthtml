from playwright.sync_api import Page, expect

from chat import CHAT_URL


def test_chat_e2e(page: Page, server: None) -> None:
    # 1. Navigate to your local dev server
    # (Ensure your FastHTML app is running on 5001)
    page.goto(f"http://localhost:5001{CHAT_URL}")

    # 2. Verify Initial State
    # Expect there to be one or more company input fields
    initial_prompt = "Well hello prompty!"
    prompt_input = page.locator('input[name="prompt"]')
    # Type "Well hello prompty!"
    prompt_input.fill(initial_prompt)
    # Press the submit button
    page.click("button#submit-btn")

    # Once the submit button is clicked the input should be converted to a static text box
    # There should be a span element that contains the initial prompt
    initial_prompt_span = page.locator("span", has_text=initial_prompt)
    expect(initial_prompt_span).to_be_visible()
    # There should not be an input field with the name "prompt" anymore
    expect(prompt_input).not_to_be_visible()

    response_div = page.locator("div#response-content")
    # Expect the response box to contain "hello"
    expect(response_div).to_contain_text("hello")
    # Expect the response box to contain "world"
    expect(response_div).to_contain_text("hello world.")

    expect(response_div).to_contain_text("End")
