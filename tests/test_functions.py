from fasthtml.common import FT, to_xml

from onboarding import CompanyInput, StatusStep


def test_company_input() -> None:
    # When I invoke CompanyInput() to create a company input field
    company_input = CompanyInput()
    # Then I should get a Fast Tag element
    assert isinstance(company_input, FT)
    # And the company input field should have a name of "companies"
    assert company_input.name == "companies"
    # And the company input field should have a placeholder of "Company Name"
    assert company_input.placeholder == "Company Name"


def test_status_step() -> None:
    # When I invoke StatusStep() to create a status step
    status_step = StatusStep("Step 1", is_done=False)
    # Then I should get a Fast Tag element
    assert isinstance(status_step, FT)
    # And the status step should have a text of "Step 1"
    assert "⏳ Step 1" in to_xml(status_step)
