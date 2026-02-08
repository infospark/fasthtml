from data_types import Edge, Failure, Graph, GraphID, GraphManager, Node, NodeId, Success
from graph_routes import graph_to_cytoscape_elements


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
    assert graph.add_nodes([Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2"))])
    assert graph.add_edges([Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))])
    assert graph.nodes == [Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2"))]
    assert graph.edges == [Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))]


def test_graph_add_node_is_idempotent() -> None:
    graph = Graph(graph_id=GraphID("test"), nodes=[], edges=[])
    graph.add_node(Node(node_id=NodeId("node1")))
    graph.add_node(Node(node_id=NodeId("node1")))
    assert len(graph.nodes) == 1
    assert graph.nodes == [Node(node_id=NodeId("node1"))]


def test_graph_is_empty() -> None:
    graph = Graph(graph_id=GraphID("test"), nodes=[], edges=[])
    assert graph.is_empty()
    graph.add_node(Node(node_id=NodeId("node1")))
    assert not graph.is_empty()


def test_graph_add_edge_is_idempotent() -> None:
    graph = Graph(graph_id=GraphID("test"))
    graph.add_nodes([Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2"))])
    graph.add_edge(Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))
    graph.add_edge(Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))
    assert len(graph.edges) == 1
    assert graph.edges == [Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))]


def test_graph_add_elements() -> None:
    graph = Graph(graph_id=GraphID("test"))
    result = graph.add_elements([Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2")), Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))])
    assert isinstance(result, Success)
    assert graph.nodes == [Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2"))]
    assert graph.edges == [Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))]


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
