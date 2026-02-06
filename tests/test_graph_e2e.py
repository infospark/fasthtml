import random
import re
import time

import pytest
from playwright.sync_api import Page, expect

from app import start_app
from data_types import Edge, Failure, Graph, GraphID, GraphManager, Node, NodeId, Success
from graph_routes import GRAPH_URL
from tests.conftest import ThreadedUvicorn


def page_has_node(page: Page, node_id: str) -> bool:
    eval_result = page.evaluate(f"() => window.graph.hasNode('{node_id}')")
    return eval_result is True  # the evaluate could return anything - just check for truthiness


def page_has_edge(page: Page, source_node_id: str, target_node_id: str) -> bool:
    eval_result = page.evaluate(f"() => window.graph.hasEdge('{source_node_id}', '{target_node_id}')")
    return eval_result is True  # the evaluate could return anything - just check for truthiness


def add_node(page: Page, node_id: str) -> Failure | Success:
    try:
        page.evaluate("""() =>
            window.graph.addNode('node4', {
                label: 'Node 4',
                x: 0,
                y: 0,
                size: 10,
                color: 'blue'
            })""")
        return Success()
    except Exception as e:
        return Failure(f"Got error adding node: {e}")


def test_graph_e2e(page: Page, server: None) -> None:
    # Navigate to the graph page
    page.goto(f"http://localhost:5001{GRAPH_URL}?session_id=test_graph")

    # Ensure there is an h1 element with the text Sigma Demo
    expect(page.locator("h1")).to_have_text("Graph Demo")

    # Check that window.graph and window.renderer are exposed
    graph_exists = page.evaluate("() => typeof window.graph !== 'undefined'")
    renderer_exists = page.evaluate("() => typeof window.renderer !== 'undefined'")

    assert graph_exists, "window.graph should be exposed"
    assert renderer_exists, "window.renderer should be exposed"

    # Check that the expected nodes exist
    expected_nodes = ["node1", "node2", "node3"]
    for node_id in expected_nodes:
        assert page_has_node(page, node_id), f"Node {node_id} should exist"

    # Check that the expected edges exist
    expected_edges = [("node1", "node2"), ("node2", "node3"), ("node3", "node1")]
    for source_node_id, target_node_id in expected_edges:
        assert page_has_edge(page, source_node_id, target_node_id), f"Edge {source_node_id} -> {target_node_id} should exist"


def test_graph_inject_node_using_js(page: Page, server: None) -> None:
    # Navigate to the graph page
    page.goto(f"http://localhost:5001{GRAPH_URL}")

    # dynamically add node 4 to the graph
    assert add_node(page, "node4")
    # check that the node exists
    assert page_has_node(page, "node4")


def start_server_with_graph_manager(graph_manager: GraphManager, port: int) -> Failure | Success:
    try:
        # create a graph manager
        app = start_app(graph_manager=graph_manager)

        # 2. Start Uvicorn in a background thread
        server_thread = ThreadedUvicorn(app, port=port)
        server_thread.start()

        # 3. Wait for the server to be ready
        timeout = 5
        start_time = time.time()
        while not server_thread.server.started:
            if time.time() - start_time > timeout:
                server_thread.stop()
                raise RuntimeError(f"Server failed to start on port {port}")
            time.sleep(0.1)

        return Success()
    except Exception as e:
        return Failure(f"Got error starting server: {e}")


def test_graph_route_creates_new_graph(page: Page) -> None:
    # use a unique port for the server
    port = 5005 + random.randint(0, 10)
    # create a graph manager
    graph_manager = GraphManager()
    assert start_server_with_graph_manager(graph_manager, port)

    # Navigate to the graph page
    page.goto(f"http://localhost:{port}{GRAPH_URL}")

    # The page should redirect to a page with a graph_id in the query params
    expect(page).to_have_url(re.compile(f"http://localhost:{port}{GRAPH_URL}\\?graph_id=.*"))

    # Get the graph_id from the query params
    graph_id = page.url.split("graph_id=")[1]

    # Ensure that the graph_manager has the corresponding graph
    graph = graph_manager.get_graph(GraphID(graph_id))
    assert isinstance(graph, Graph)


def test_graph_route_uses_existing_graph(page: Page) -> None:
    # use a unique port for the server
    port = 5005 + random.randint(0, 10)
    # create a graph manager
    graph_manager = GraphManager()
    assert start_server_with_graph_manager(graph_manager, port)

    # create a graph
    graph = graph_manager.create_graph()
    graph_id = graph.graph_id

    # Navigate to the graph page
    url = f"http://localhost:{port}{GRAPH_URL}?graph_id={graph_id}"
    page.goto(url)

    # The page should be at the correct URL - i.e. we do not redirect to a page with a new graph_id
    expect(page).to_have_url(url)


@pytest.mark.skip("Not implemented yet - specifically the page does not render the graph that was requested")
def test_graph_page_shows_graph(page: Page) -> None:
    # use a unique port for the server
    port = 5005 + random.randint(0, 10)
    # create a graph manager
    graph_manager = GraphManager()
    assert start_server_with_graph_manager(graph_manager, port)

    # create a graph
    graph = graph_manager.create_graph()
    assert isinstance(graph, Graph)
    assert graph.add_node(Node(node_id=NodeId("node X")))
    assert graph.add_node(Node(node_id=NodeId("node Y")))
    assert graph.add_edge(Edge(source_node_id=NodeId("node X"), target_node_id=NodeId("node Y")))

    # Navigate to the graph page
    url = f"http://localhost:{port}{GRAPH_URL}?graph_id={graph.graph_id}"
    page.goto(url)

    # The page should be at the correct URL - i.e. we do not redirect to a page with a new graph_id
    expect(page).to_have_url(url)

    # Check that the expected nodes exist
    expect(page.locator("h1")).to_have_text("Graph Demo")

    # Now check the graph is rendered correctly
    assert page_has_node(page, "node1")
    assert page_has_node(page, "node Y")
    assert page_has_edge(page, "node X", "node Y")


# TODO - live streaming of changes to the graph:
# So SSE would be sitting waiting for events to be given to it
# SO do that first - set up SSE on the server side and just start streaming messages from server to browser
# On the server side I need some kind of generator that will emit new Node/Edges - for now it can just iterate over a list that I pass to it from the test
# Later something else will generate those events
# Remember - I can run page.evaluate on the server side when testing - i cannot run page.evaluate on some users' browser!

# TODO - mimic a user interacting with the graph - say moving node? ensure we pick that up too
