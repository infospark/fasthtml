from collections.abc import Generator

import pytest
from bs4 import BeautifulSoup
from starlette.testclient import TestClient

from app import HTMX_REQUEST_HEADERS, OK, start_app  # or wherever your FastHTML app is
from chat_routes import CHAT_PROMPT_URL, CHAT_RESPONSE_STREAM_URL, CHAT_URL, parrot_chat


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


def test_get_chat_page(client: TestClient) -> None:
    response = client.get(
        CHAT_URL,
        params={"conversation": "Conversation begins here"},
    )
    assert response.status_code == OK
    # Check there's a div with class ai-response that contains the conversation starter
    soup = BeautifulSoup(response.text, "html.parser")
    ai_response_div = soup.select_one("[data-testid='ai-response']")
    assert ai_response_div is not None
    assert "Conversation begins here" in ai_response_div.get_text()
