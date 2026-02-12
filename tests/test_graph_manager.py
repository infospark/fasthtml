import pytest

from data_types import Edge, EdgeAdded, Failure, Graph, GraphID, GraphManager, Node, NodeAdded, NodeId, Success


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
    assert graph._add_nodes([Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2"))])
    assert graph._add_edges([Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))])
    assert graph.nodes == [Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2"))]
    assert graph.edges == [Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))]


def test_graph_add_node_is_idempotent() -> None:
    graph = Graph(graph_id=GraphID("test"), nodes=[], edges=[])
    graph._add_node(Node(node_id=NodeId("node1")))
    graph._add_node(Node(node_id=NodeId("node1")))
    assert len(graph.nodes) == 1
    assert graph.nodes == [Node(node_id=NodeId("node1"))]


def test_graph_is_empty() -> None:
    graph = Graph(graph_id=GraphID("test"), nodes=[], edges=[])
    assert graph.is_empty()
    graph._add_node(Node(node_id=NodeId("node1")))
    assert not graph.is_empty()


def test_graph_add_edge_is_idempotent() -> None:
    graph = Graph(graph_id=GraphID("test"))
    graph._add_nodes([Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2"))])
    graph._add_edge(Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))
    graph._add_edge(Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))
    assert len(graph.edges) == 1
    assert graph.edges == [Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))]


def test_graph_add_elements() -> None:
    graph = Graph(graph_id=GraphID("test"))
    result = graph._add_elements([Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2")), Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))])
    assert isinstance(result, Success)
    assert graph.nodes == [Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2"))]
    assert graph.edges == [Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))]


def test_node_added_event() -> None:
    graph_id = GraphID("graph1")
    node = Node(node_id=NodeId("node1"))
    event = NodeAdded(graph_id=graph_id, node=node)
    assert event.graph_id == graph_id
    assert event.node == node


def test_edge_added_event() -> None:
    graph_id = GraphID("graph1")
    edge = Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))
    event = EdgeAdded(graph_id=graph_id, edge=edge)
    assert event.graph_id == graph_id
    assert event.edge == edge


def test_graph_manager_add_node() -> None:
    graph_manager = GraphManager()
    graph = graph_manager.create_graph()
    result = graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node1")))
    assert isinstance(result, Success)
    assert graph.nodes == [Node(node_id=NodeId("node1"))]


def test_graph_manager_add_node_to_unknown_graph() -> None:
    graph_manager = GraphManager()
    result = graph_manager.add_node(GraphID("unknown"), Node(node_id=NodeId("node1")))
    assert isinstance(result, Failure)


def test_graph_manager_add_node_duplicate() -> None:
    graph_manager = GraphManager()
    graph = graph_manager.create_graph()
    graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node1")))
    result = graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node1")))
    assert isinstance(result, Failure)


def test_graph_manager_add_edge() -> None:
    graph_manager = GraphManager()
    graph = graph_manager.create_graph()
    graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node1")))
    graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node2")))
    result = graph_manager.add_edge(graph.graph_id, Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))
    assert isinstance(result, Success)
    assert graph.edges == [Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))]


def test_graph_manager_add_edge_to_unknown_graph() -> None:
    graph_manager = GraphManager()
    result = graph_manager.add_edge(GraphID("unknown"), Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))
    assert isinstance(result, Failure)


@pytest.mark.asyncio
async def test_graph_manager_subscribe_receives_node_added() -> None:
    graph_manager = GraphManager()
    graph = graph_manager.create_graph()

    subscription = graph_manager.subscribe(graph.graph_id)

    graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node1")))

    event = await anext(subscription)
    assert isinstance(event, NodeAdded)
    assert event.graph_id == graph.graph_id
    assert event.node == Node(node_id=NodeId("node1"))

    await subscription.aclose()


@pytest.mark.asyncio
async def test_graph_manager_subscribe_receives_edge_added() -> None:
    graph_manager = GraphManager()
    graph = graph_manager.create_graph()

    subscription = graph_manager.subscribe(graph.graph_id)

    graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node1")))
    graph_manager.add_node(graph.graph_id, Node(node_id=NodeId("node2")))
    graph_manager.add_edge(graph.graph_id, Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))

    event1 = await anext(subscription)
    event2 = await anext(subscription)
    event3 = await anext(subscription)

    assert isinstance(event1, NodeAdded)
    assert isinstance(event2, NodeAdded)
    assert isinstance(event3, EdgeAdded)
    assert event3.edge == Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))

    await subscription.aclose()
