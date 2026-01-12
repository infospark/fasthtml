from fasthtml.common import Div

from utils import format_for_sse


def test_format_for_sse() -> None:
    # When I invoke format_for_sse() to format a Fast Tag element
    ft = Div("Test")
    formatted = format_for_sse(ft)
    # Then I should get a formatted string
    assert formatted == "event: message\ndata: <div>Test</div>\n\n"
