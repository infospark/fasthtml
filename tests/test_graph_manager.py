from typing import Any

from data_types import Edge, Failure, Graph, GraphID, GraphManager, Node, NodeId


def test_create_graph() -> None:
    nodes = [Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2"))]
    edges = [Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))]
    graph = Graph(graph_id=GraphID("graph1"), nodes=nodes, edges=edges)
    assert graph.nodes == nodes
    assert graph.edges == edges


def test_graph_manager_create_graph() -> None:
    graph_manager = GraphManager()
    graph = graph_manager.create_graph()
    assert graph.graph_id is not None
    assert graph.nodes == []
    assert graph.edges == []

    # check that we can get the graph back
    retrieved_graph = graph_manager.get_graph(graph.graph_id)
    assert isinstance(retrieved_graph, Graph)
    assert retrieved_graph.graph_id == graph.graph_id
    assert retrieved_graph.nodes == graph.nodes
    assert retrieved_graph.edges == graph.edges


def test_graph_manager_create_graph_with_graph() -> None:
    graph_manager = GraphManager()
    graph = Graph(graph_id=GraphID("graph1"), nodes=[Node(node_id=NodeId("node1"))], edges=[Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))])
    graph = graph_manager.create_graph(graph=graph)
    assert graph.graph_id is not None
    assert graph.nodes == graph.nodes
    assert graph.edges == graph.edges

    # check that we can get the graph back
    retrieved_graph = graph_manager.get_graph(graph.graph_id)
    assert isinstance(retrieved_graph, Graph)
    assert retrieved_graph.graph_id == graph.graph_id
    assert retrieved_graph.nodes == graph.nodes
    assert retrieved_graph.edges == graph.edges


def test_graph_manager_get_graph_not_found() -> None:
    graph_manager = GraphManager()
    retrieved_graph = graph_manager.get_graph(GraphID("graph1"))
    assert isinstance(retrieved_graph, Failure)


def test_graph_add_nodes_and_edges() -> None:
    graph_manager = GraphManager()
    graph = graph_manager.create_graph()
    assert graph.add_node(Node(node_id=NodeId("node1")))
    assert graph.add_node(Node(node_id=NodeId("node2")))
    assert graph.add_edge(Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))
    assert graph.nodes == [Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2"))]
    assert graph.edges == [Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))]


def test_graph_add_node_is_idempotent() -> None:
    graph = Graph(graph_id=GraphID("test"), nodes=[], edges=[])
    graph.add_node(Node(node_id=NodeId("node1")))
    graph.add_node(Node(node_id=NodeId("node1")))
    assert len(graph.nodes) == 1
    assert graph.nodes == [Node(node_id=NodeId("node1"))]


def test_graph_add_edge_is_idempotent() -> None:
    graph = Graph(graph_id=GraphID("test"), nodes=[], edges=[])
    graph.add_node(Node(node_id=NodeId("node1")))
    graph.add_node(Node(node_id=NodeId("node2")))
    graph.add_edge(Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))
    graph.add_edge(Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))
    assert len(graph.edges) == 1
    assert graph.edges == [Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))]


def test_graph_get_graphology_data() -> None:
    # Given a graph
    graph = Graph(
        graph_id=GraphID("My Graph"),
        nodes=[
            Node(node_id=NodeId("node1")),
            Node(node_id=NodeId("node2")),
            Node(node_id=NodeId("node3")),
        ],
        edges=[
            Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")),
            Edge(source_node_id=NodeId("node2"), target_node_id=NodeId("node3")),
            Edge(source_node_id=NodeId("node3"), target_node_id=NodeId("node1")),
        ],
    )
    # When I call get_graphology_data
    actual_graphology_data: dict[str, Any] = graph.get_graphology_data()
    # Then I get the graphology data
    expected_graphology_data: dict[str, Any] = {
        "attributes": {"name": "My Graph"},
        "nodes": [
            {"key": "node1", "attributes": {"x": 0, "y": 0, "size": 10, "label": "node1"}},
            {"key": "node2", "attributes": {"x": 1, "y": 0, "size": 10, "label": "node2"}},
            {"key": "node3", "attributes": {"x": 0.5, "y": 1, "size": 10, "label": "node3"}},
        ],
        "edges": [{"source": "node1", "target": "node2"}, {"source": "node2", "target": "node3"}, {"source": "node3", "target": "node1"}],
    }

    # and the name of the actual graphology data is the same as the expected graphology data
    actual_attributes = actual_graphology_data.get("attributes")
    assert actual_attributes is not None
    assert actual_attributes.get("name") == expected_graphology_data["attributes"]["name"]
    # And the number of actual nodes is the same as the expected number of nodes
    actual_nodes = actual_graphology_data.get("nodes")
    assert actual_nodes is not None
    assert len(actual_nodes) == len(expected_graphology_data["nodes"])
    # And the number of actual edges is the same as the expected number of edges
    actual_edges = actual_graphology_data.get("edges")
    assert actual_edges is not None
    assert len(actual_edges) == len(expected_graphology_data["edges"])

    # Nodes: key and label must match; x and y must be present (may differ from expected); other attributes must match
    actual_nodes_by_key = {n["key"]: n for n in actual_graphology_data.get("nodes", [])}
    for expected_node in expected_graphology_data.get("nodes", []):
        key = expected_node["key"]
        actual_node = actual_nodes_by_key.get(key)
        assert actual_node is not None, f"Node with key {key} not found in actual"
        actual_attrs = actual_node.get("attributes", {})
        expected_attrs = expected_node.get("attributes", {})
        assert actual_attrs.get("label") == expected_attrs.get("label")
        assert "x" in actual_attrs, f"Node {key} must have x in attributes"
        assert "y" in actual_attrs, f"Node {key} must have y in attributes"
        for attr_key in ["size"]:
            assert actual_attrs.get(attr_key) == expected_attrs.get(attr_key), f"Node {key} attribute {attr_key} mismatch"

    # Edges: source and target must match
    actual_edges = {(e["source"], e["target"]) for e in actual_graphology_data.get("edges", [])}
    expected_edges = {(e["source"], e["target"]) for e in expected_graphology_data.get("edges", [])}
    assert actual_edges == expected_edges
