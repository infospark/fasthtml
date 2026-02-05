from collections.abc import Generator

import pytest
from starlette.testclient import TestClient

from app import OK_CODE, start_app
from chat_routes import parrot_chat
from data_types import GraphID, GraphManager
from graph_routes import GRAPH_URL


@pytest.fixture
def graph_manager() -> Generator[GraphManager, None, None]:
    yield GraphManager()


@pytest.fixture
def client(graph_manager: GraphManager) -> Generator[TestClient, None, None]:
    # The 'with' block ensures the app's lifespan events (if any) run
    with TestClient(start_app(parrot_chat, graph_manager)) as client:
        yield client


def test_get_graph_page(client: TestClient) -> None:
    response = client.get(GRAPH_URL)
    assert response.status_code == OK_CODE

    assert "Graph Demo" in response.text


def test_get_graph_page_without_graph_id_creates_new_graph(client: TestClient, graph_manager: GraphManager) -> None:
    response = client.get(GRAPH_URL)

    assert response.status_code == OK_CODE
    assert "graph_id=" in str(response.url)

    # check graph_manager for the graph
    url_after_redirect = str(response.url)
    graph_id = url_after_redirect.split("graph_id=")[1]
    graph = graph_manager.get_graph(GraphID(graph_id))
    assert graph
