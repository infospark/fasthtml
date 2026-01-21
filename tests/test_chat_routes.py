from collections.abc import Generator

import pytest
from starlette.testclient import TestClient

from app import HTMX_REQUEST_HEADERS, OK, start_app  # or wherever your FastHTML app is
from chat import CHAT_PROMPT_URL, CHAT_RESPONSE_STREAM_URL, parrot_chat


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    # The 'with' block ensures the app's lifespan events (if any) run
    with TestClient(start_app(parrot_chat)) as client:
        yield client


def test_chat_prompt(client: TestClient) -> None:
    # Act: Request the start bulk task page
    # Include HX-Request header to simulate HTMX request, so FastHTML returns just the fragment
    response = client.post(
        CHAT_PROMPT_URL,
        json={"prompt": "Hello world", "conversation": "Conversation begins here"},
        headers=HTMX_REQUEST_HEADERS,
    )

    # Assert
    assert response.status_code == OK
    # Check that the response is a Fast Tag element (not wrapped in full HTML page)
    assert "div" in response.text
    assert "hx-ext='sse'" in response.text or 'hx-ext="sse"' in response.text
    # FastHTML URL-encodes the query string, so check for the encoded version
    assert f'sse-connect="{CHAT_RESPONSE_STREAM_URL}' in response.text
    assert "prompt=Hello+world" in response.text
    # url encode the conversation
    assert "conversation=Conversation+begins+here" in response.text
