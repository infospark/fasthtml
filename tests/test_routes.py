from collections.abc import Generator

import pytest
from starlette.testclient import TestClient

from main import app  # Import your FastHTML app object

htmx_request_headers = {"HX-Request": "true"}


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    # The 'with' block ensures the app's lifespan events (if any) run
    with TestClient(app) as client:
        yield client


def test_get_root(client: TestClient) -> None:
    # When I invoke get_root() to get the root page
    response = client.get("/")
    # Then I should get a Fast Tag element
    assert response.status_code == 200
    # And the root page should have a title of "Bulk Onboarding" and a heading of "Onboard Companies"
    assert "Bulk Onboarding" in response.text
    assert "Onboard Companies" in response.text


def test_dashboard_filters(client: TestClient) -> None:
    # Act: Request the dashboard with a specific 'status' filter
    response = client.get(
        "/", params={"status": "pending"}, headers=htmx_request_headers
    )

    # Assert
    assert response.status_code == 200
    # Check that the 'pending' state is reflected in the HTML
    assert "Bulk Onboarding" in response.text


def test_get_stream(client: TestClient) -> None:
    # Act: Request the stream with a specific 'names' parameter
    response = client.get(
        "/stream-bulk",
        params={"names": "Acme Corp,Example Inc"},
        headers=htmx_request_headers,
    )

    # Assert
    assert response.status_code == 200
    # Check that the 'Acme Corp' and 'Example Inc' names are reflected in the HTML
    assert "Acme Corp" in response.text
    assert "Example Inc" in response.text


def test_get_add_input(client: TestClient) -> None:
    # Act: Request the add input page
    response = client.get("/add-input", headers=htmx_request_headers)

    # Assert
    assert response.status_code == 200
    # Check that the response is a Fast Tag element
    assert "input" in response.text
    assert 'name="companies"' in response.text


def test_start_bulk_task(client: TestClient) -> None:
    # Act: Request the start bulk task page
    # Include HX-Request header to simulate HTMX request, so FastHTML returns just the fragment
    response = client.post(
        "/start-bulk-task",
        json={"companies": ["Acme Corp", "Example Inc"]},
        headers=htmx_request_headers,
    )

    # Assert
    assert response.status_code == 200
    # Check that the response is a Fast Tag element (not wrapped in full HTML page)
    assert "div" in response.text
    assert "hx-ext='sse'" in response.text or 'hx-ext="sse"' in response.text
    # FastHTML URL-encodes the query string, so check for the encoded version
    assert 'sse-connect="/stream-bulk?names=Acme+Corp%2CExample+Inc"' in response.text
