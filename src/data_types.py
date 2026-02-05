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


@dataclass
class GraphManager:
    _graphs: dict[GraphID, Graph] = field(default_factory=dict)

    def create_graph(self, graph: Graph | None = None) -> Graph:
        if not graph:
            graph_id = GraphID(str(uuid.uuid4()))
            graph = Graph(graph_id=graph_id, nodes=[], edges=[])
        self._graphs[graph.graph_id] = graph
        return graph

    def get_graph(self, graph_id: GraphID) -> Graph:
        return self._graphs[graph_id]
