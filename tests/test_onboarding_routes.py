from collections.abc import Generator

import pytest
from starlette.testclient import TestClient

from app import HTMX_REQUEST_HEADERS, OK, start_app
from chat import parrot_chat
from onboarding import (
    ONBOARDING_ADD_COMPANY_URL,
    ONBOARDING_START_TASKS_URL,
    ONBOARDING_STREAM_TASKS_STATUS_URL,
    ONBOARDING_URL,
)  # Import your FastHTML app object


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    # The 'with' block ensures the app's lifespan events (if any) run
    with TestClient(start_app(parrot_chat)) as client:
        yield client


def test_get_onboarding_page(client: TestClient) -> None:
    # When I invoke get_root() to get the root page
    response = client.get(ONBOARDING_URL)
    assert response.status_code == OK

    # The root page should have a title of "Bulk Onboarding" and a heading of "Onboard Companies"
    assert "Bulk Onboarding" in response.text
    assert "Onboard Companies" in response.text


def test_get_onboarding_page_with_filters(client: TestClient) -> None:
    # Act: Request the dashboard with a specific 'status' filter
    response = client.get(ONBOARDING_URL, params={"status": "pending"}, headers=HTMX_REQUEST_HEADERS)

    assert response.status_code == OK
    # Check that the 'pending' state is reflected in the HTML
    assert "Bulk Onboarding" in response.text


def test_onboarding_stream_tasks_status(client: TestClient) -> None:
    # Act: Request the stream with a specific 'names' parameter
    response = client.get(
        ONBOARDING_STREAM_TASKS_STATUS_URL,
        params={"names": "Acme Corp,Example Inc"},
        headers=HTMX_REQUEST_HEADERS,
    )

    assert response.status_code == OK
    # Check that the 'Acme Corp' and 'Example Inc' names are reflected in the HTML
    assert "Acme Corp" in response.text
    assert "Example Inc" in response.text


def test_onboarding_add_company(client: TestClient) -> None:
    # Act: Request the add input page
    response = client.get(ONBOARDING_ADD_COMPANY_URL, headers=HTMX_REQUEST_HEADERS)

    # Assert
    assert response.status_code == OK
    # Check that the response is a Fast Tag element
    assert "input" in response.text
    assert 'name="companies"' in response.text


def test_onboarding_start_tasks(client: TestClient) -> None:
    # Act: Request the start bulk task page
    # Include HX-Request header to simulate HTMX request, so FastHTML returns just the fragment
    response = client.post(
        ONBOARDING_START_TASKS_URL,
        json={"companies": ["Acme Corp", "Example Inc"]},
        headers=HTMX_REQUEST_HEADERS,
    )

    # Assert
    assert response.status_code == OK
    # Check that the response is a Fast Tag element (not wrapped in full HTML page)
    assert "div" in response.text
    assert "hx-ext='sse'" in response.text or 'hx-ext="sse"' in response.text
    # FastHTML URL-encodes the query string, so check for the encoded version
    assert f'sse-connect="{ONBOARDING_STREAM_TASKS_STATUS_URL}?names=Acme+Corp%2CExample+Inc"' in response.text
