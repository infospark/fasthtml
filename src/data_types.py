import uuid
from dataclasses import dataclass, field
from typing import NewType


@dataclass
class Failure:
    message: str

    def __bool__(self) -> bool:
        return False


@dataclass
class Success:
    message: None | str = None

    def __bool__(self) -> bool:
        return True


GraphID = NewType("GraphID", str)
NodeId = NewType("NodeId", str)


@dataclass
class Node:
    node_id: NodeId


@dataclass
class Edge:
    source_node_id: NodeId
    target_node_id: NodeId


@dataclass
class Graph:
    graph_id: GraphID
    nodes: list[Node]
    edges: list[Edge]

    def add_node(self, node: Node) -> Success | Failure:
        if any(n.node_id == node.node_id for n in self.nodes):
            return Success()
        self.nodes.append(node)
        return Success()

    def add_edge(self, edge: Edge) -> Success | Failure:
        if any(e.source_node_id == edge.source_node_id and e.target_node_id == edge.target_node_id for e in self.edges):
            return Success()
        self.edges.append(edge)
        return Success()

    def is_empty(self) -> bool:
        return len(self.nodes) == 0 and len(self.edges) == 0


@dataclass
class GraphManager:
    _graphs: dict[GraphID, Graph] = field(default_factory=dict)

    def create_graph(self, graph: Graph | None = None) -> Graph:
        if not graph:
            graph_id = GraphID(str(uuid.uuid4()))
            graph = Graph(graph_id=graph_id, nodes=[], edges=[])
        self._graphs[graph.graph_id] = graph
        return graph

    def get_graph(self, graph_id: GraphID) -> Failure | Graph:
        graph = self._graphs.get(graph_id)
        if graph is not None:
            return graph
        return Failure(f"Graph with id {graph_id} not found")
