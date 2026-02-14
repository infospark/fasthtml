import re

from playwright.sync_api import Page, expect

from data_types import Failure, Success
from graph import Edge, Graph, GraphID, Node, NodeId
from graph_manager import GraphManager
from graph_routes import GRAPH_URL


def page_has_node(page: Page, node_id: str) -> bool:
    eval_result = page.evaluate(f"() => window.cy.$id('{node_id}').length > 0")
    return eval_result is True


def page_has_edge(page: Page, source_node_id: str, target_node_id: str) -> bool:
    eval_result = page.evaluate(f'() => window.cy.edges(\'[source="{source_node_id}"][target="{target_node_id}"]\').length > 0')
    return eval_result is True


def add_node(page: Page, node_id: str) -> Failure | Success:
    try:
        page.evaluate(f"""() =>
            window.cy.add({{
                group: 'nodes',
                data: {{ id: '{node_id}', label: '{node_id}' }}
            }})""")
        return Success()
    except Exception as e:
        return Failure(f"Got error adding node: {e}")


def test_graph_e2e(page: Page, server: None) -> None:
    # Navigate to the graph page
    page.goto(f"http://localhost:5001{GRAPH_URL}?session_id=test_graph")

    # Ensure there is an h1 element with the text Sigma Demo
    expect(page.locator("h1")).to_have_text("Graph Demo")

    # Check that window.cy is exposed
    cy_exists = page.evaluate("() => typeof window.cy !== 'undefined'")
    assert cy_exists, "window.cy should be exposed"

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


def test_graph_route_creates_new_graph(page: Page, graph_server: tuple[GraphManager, int]) -> None:
    graph_manager, port = graph_server

    # Navigate to the graph page
    page.goto(f"http://localhost:{port}{GRAPH_URL}")

    # The page should redirect to a page with a graph_id in the query params
    expect(page).to_have_url(re.compile(f"http://localhost:{port}{GRAPH_URL}\\?graph_id=.*"))

    # Get the graph_id from the query params
    graph_id = page.url.split("graph_id=")[1]

    # Ensure that the graph_manager has the corresponding graph
    graph = graph_manager.get_graph(GraphID(graph_id))
    assert isinstance(graph, Graph)


def test_graph_route_uses_existing_graph(page: Page, graph_server: tuple[GraphManager, int]) -> None:
    graph_manager, port = graph_server

    # create a graph
    graph = graph_manager.create_graph()
    graph_id = graph.graph_id

    # Navigate to the graph page
    url = f"http://localhost:{port}{GRAPH_URL}?graph_id={graph_id}"
    page.goto(url)

    # The page should be at the correct URL - i.e. we do not redirect to a page with a new graph_id
    expect(page).to_have_url(url)


def test_graph_page_initial_graph_renders(page: Page, graph_server: tuple[GraphManager, int]) -> None:
    graph_manager, port = graph_server

    # create a graph
    graph = graph_manager.create_graph()
    assert isinstance(graph, Graph)
    assert graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node X")))
    assert graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node Y")))
    assert graph_manager.add_edge(graph.graph_id, Edge(source_node_id=NodeId("node X"), target_node_id=NodeId("node Y")))

    # Navigate to the graph page
    url = f"http://localhost:{port}{GRAPH_URL}?graph_id={graph.graph_id}"
    page.goto(url)

    # The page should be at the correct URL - i.e. we do not redirect to a page with a new graph_id
    expect(page).to_have_url(url)

    # Check that the page is at the correct URL
    expect(page.locator("h1")).to_have_text("Graph Demo")

    # Now check the graph is rendered correctly
    assert page_has_node(page, "node X")
    assert page_has_node(page, "node Y")
    assert page_has_edge(page, "node X", "node Y")


def test_graph_page_adds_node_to_existing_graph(page: Page, graph_server: tuple[GraphManager, int]) -> None:
    graph_manager, port = graph_server

    # create a graph with initial nodes and an edge
    graph = graph_manager.create_graph()
    assert isinstance(graph, Graph)
    graph_id = graph.graph_id
    assert graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node X")))
    assert graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node Y")))
    assert graph_manager.add_edge(graph.graph_id, Edge(source_node_id=NodeId("node X"), target_node_id=NodeId("node Y")))

    # Navigate to the graph page
    page.goto(f"http://localhost:{port}{GRAPH_URL}?graph_id={graph_id}")
    expect(page.locator("h1")).to_have_text("Graph Demo")

    # Verify initial graph rendered
    assert page_has_node(page, "node X")
    assert page_has_node(page, "node Y")
    assert page_has_edge(page, "node X", "node Y")

    # Add a new node server-side — should appear in browser via SSE
    graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node Z")))
    page.wait_for_function("() => window.cy.$id('node Z').length > 0", timeout=5000)

    # Add an edge server-side — should appear in browser via SSE
    graph_manager.add_edge(graph.graph_id, Edge(source_node_id=NodeId("node Y"), target_node_id=NodeId("node Z")))
    page.wait_for_function('() => window.cy.edges(\'[source="node Y"][target="node Z"]\').length > 0', timeout=5000)


# TODO - mimic a user interacting with the graph - say moving node? ensure we pick that up too
