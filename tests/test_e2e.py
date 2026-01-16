from playwright.sync_api import Page, expect

from onboarding import ONBOARDING_URL


def test_onboarding_flow(page: Page, server: None) -> None:
    # 1. Navigate to your local dev server
    # (Ensure your FastHTML app is running on 5001)
    page.goto(f"http://localhost:5001{ONBOARDING_URL}")

    # 2. Verify Initial State
    # Expect there to be one or more company input fields
    company_inputs = page.locator('input[name="companies"]')
    # expect at least two company input fields
    expect(company_inputs).to_have_count(2)

    # 3. Test HTMX Interaction
    # Fill in a company name and press a button (assuming you have one)
    page.fill('input[name="companies"]', "Acme Corp")
    page.click("button#submit-btn")

    # 4. Test SSE / Dynamic Updates
    # If your StatusStep updates via SSE, we wait for the '✅' icon to appear
    # This proves the Python -> SSE -> JS -> DOM chain is unbroken
    status_item = page.locator("h4", has_text="🚀 All company tasks completed!")
    expect(status_item).to_be_visible(timeout=10000)
