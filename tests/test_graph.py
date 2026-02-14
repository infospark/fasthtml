
from graph import PERSON, Edge, Graph, GraphID, Node, NodeId


def test_create_graph() -> None:
    nodes = [Node(node_id=NodeId("node1")), Node(node_id=NodeId("node2"))]
    edges = [Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2"))]
    graph = Graph(graph_id=GraphID("graph1"), nodes=nodes, edges=edges)
    assert graph.nodes == nodes
    assert graph.edges == edges

def test_node_attributes() -> None:
    node = Node(node_id=NodeId("node1"), type=PERSON)
    assert node.node_id == NodeId("node1")
    assert node.type == PERSON
