from collections.abc import Generator

import pytest
from starlette.testclient import TestClient

from chat import CHAT_PROMPT_URL, CHAT_RESPONSE_STREAM_URL
from main import HTMX_REQUEST_HEADERS, OK, app  # or wherever your FastHTML app is


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    # The 'with' block ensures the app's lifespan events (if any) run
    with TestClient(app) as client:
        yield client


def test_onboarding_start_tasks(client: TestClient) -> None:
    # Act: Request the start bulk task page
    # Include HX-Request header to simulate HTMX request, so FastHTML returns just the fragment
    response = client.post(
        CHAT_PROMPT_URL,
        json={"prompt": "Hello"},
        headers=HTMX_REQUEST_HEADERS,
    )

    # Assert
    assert response.status_code == OK
    # Check that the response is a Fast Tag element (not wrapped in full HTML page)
    assert "div" in response.text
    assert "hx-ext='sse'" in response.text or 'hx-ext="sse"' in response.text
    # FastHTML URL-encodes the query string, so check for the encoded version
    assert f'sse-connect="{CHAT_RESPONSE_STREAM_URL}?prompt=Hello"' in response.text
