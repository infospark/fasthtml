from playwright.sync_api import Page, expect

from sigma_demo import SIGMA_DEMO_URL, Edge


def has_node(page: Page, node_id: str) -> bool:
    eval_result = page.evaluate(
        f"() => window.graph.hasNode('{node_id}')"
    )
    return eval_result is True # the evaluate could return anything - just check for truthiness

def has_edge(page: Page, edge: Edge) -> bool:
    eval_result = page.evaluate(
        f"() => window.graph.hasEdge('{edge.source}', '{edge.target}')"
    )
    return eval_result is True # the evaluate could return anything - just check for truthiness

def test_sigma_demo(page: Page, server: None) -> None:
    # Navigate to the local dev server
    page.goto(f"http://localhost:5001{SIGMA_DEMO_URL}")

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
        assert has_node(page, node_id), f"Node {node_id} should exist"

    # Check that the expected edges exist
    expected_edges = [Edge("node1", "node2"), Edge("node2", "node3"), Edge("node3", "node1")]
    for edge in expected_edges:
        assert has_edge(page, edge), f"Edge {edge} should exist"
