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
