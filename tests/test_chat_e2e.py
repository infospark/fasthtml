from playwright.sync_api import Page, expect

from chat import CHAT_URL


def test_chat_e2e_ux(page: Page, server: None) -> None:
    # 1. Navigate to your local dev server
    # (Ensure your FastHTML app is running on 5001)
    page.goto(f"http://localhost:5001{CHAT_URL}")

    # 2. Verify Initial State
    # Expect there to be one or more company input fields
    initial_prompt = "Well hello prompty!"
    prompt_input = page.locator('input[name="prompt"]')
    # Type "Well hello prompty!"
    prompt_input.fill(initial_prompt)
    # User hits enter to submit the prompt
    page.keyboard.press("Enter")

    # Once the submit button is clicked the input should be converted to a static text box
    # There should be a span element that contains the initial prompt
    initial_prompt_span = page.locator(".user-message", has_text=initial_prompt)
    expect(initial_prompt_span).to_be_visible()
    # There should not be an input field with the name "prompt" anymore
    expect(prompt_input).not_to_be_visible()

    response_div = page.locator("div#response-content")
    # Expect the response box to contain "hello"
    expect(response_div).to_contain_text("hello")
    # Expect the response box to contain "world"
    expect(response_div).to_contain_text("hello world.")

    expect(response_div).to_contain_text("End")

    # once the End of the previous response is reached a new input field should appear below the previous response
    new_prompt_input = page.locator('input[name="prompt"]')
    expect(new_prompt_input).to_be_visible()

    # TODO - I should be able to type in a new prompt and submit it
    # TODO - WHen I post again the whole conversation should be passed back to the server - via hidden input fields?
    # TODO - Or should the whole conversation be in one form?§
    # TODO - and it should be added to the conversation
