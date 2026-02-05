import pytest
from playwright.sync_api import Page, expect

from data_types import Failure, Success
from graph import GRAPH_URL


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


def test_sigma_demo(page: Page, server: None) -> None:
    # Navigate to the sigma demo page
    page.goto(f"http://localhost:5001{GRAPH_URL}?session_id=test_graph")

    # Ensure there is an h1 element with the text Sigma Demo
    expect(page.locator("h1")).to_have_text("Sigma Demo")

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


def test_sigma_demo_inject_node_using_js(page: Page, server: None) -> None:
    # Navigate to the sigma demo page
    page.goto(f"http://localhost:5001{GRAPH_URL}")

    # dynamically add node 4 to the graph
    assert add_node(page, "node4")
    # check that the node exists
    assert page_has_node(page, "node4")


@pytest.mark.skip("Not implemented")
def test_sigma_demo_node_passed_via_data_model(page: Page, server: None) -> None:
    # Navigate to the sigma demo page
    page.goto(f"http://localhost:5001{GRAPH_URL}")

    # new_node = "node5"
    # Pass the new node to the data model


# TODO - work out how to pass nodes and edges into the page - have it display them - be able to test them
# So SSE would be sitting waiting for events to be given to it
# SO do that first - set up SSE on the server side and just start streaming messages from server to browser
# On the server side I need some kind of generator that will emit new Node/Edges - for now it can just iterate over a list that I pass to it from the test
# Later something else will generate those events
# Remember - I can run page.evaluate on the server side when testing - i cannot run page.evaluate on some users' browser!
# TODO - start looking at layouts - how do I build that TDD??
# TODO - mimic a user interacting with the graph - say moving node? ensure we pick that up too
