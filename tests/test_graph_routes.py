import logging
import threading
import time
from collections.abc import Generator

import pytest
from starlette.testclient import TestClient

from app import OK_CODE, start_app
from chat_routes import parrot_chat
from graph import Edge, Graph, GraphID, Node, NodeId
from graph_cytoscape_utils import graph_to_cytoscape_elements
from graph_manager import GraphManager
from graph_routes import GRAPH_EVENTS_URL, GRAPH_URL


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


def test_graph_get_cytoscape_elements() -> None:
    graph = Graph(
        graph_id=GraphID("My Graph"),
        nodes=[
            Node(node_id=NodeId("node1")),
            Node(node_id=NodeId("node2")),
        ],
        edges=[
            Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")),
        ],
    )

    elements = graph_to_cytoscape_elements(graph)

    expected_nodes = [
        {"data": {"id": "node1", "label": "node1"}},
        {"data": {"id": "node2", "label": "node2"}},
    ]
    expected_edges = [
        {"data": {"source": "node1", "target": "node2"}},
    ]

    nodes = [e for e in elements if "source" not in e["data"]]
    edges = [e for e in elements if "source" in e["data"]]
    assert nodes == expected_nodes
    assert edges == expected_edges


def test_graph_events_sse_endpoint_returns_event_stream(graph_manager: GraphManager) -> None:
    graph = graph_manager.create_graph()

    def publish_after_delay() -> None:
        time.sleep(0.5)
        graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("sse_node")))
        logging.info("Published node")
    logging.info("Starting thread to publish node after delay")
    threading.Thread(target=publish_after_delay, daemon=True).start()

    with TestClient(start_app(parrot_chat, graph_manager)) as client:
        logging.info("Starting client stream")
        with client.stream("GET", f"{GRAPH_EVENTS_URL}?graph_id={graph.graph_id}&stop_after_n=1") as response:
            logging.info("Response stream started")
            assert response.status_code == OK_CODE
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            logging.info("Response stream headers received")
            chunk = next(response.iter_text())
            logging.info("Response stream chunk received")
            assert "event: graph_update" in chunk
            assert '"type": "node_added"' in chunk
            assert '"sse_node"' in chunk
