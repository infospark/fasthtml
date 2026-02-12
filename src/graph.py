
from dataclasses import dataclass, field
from typing import NewType

from data_types import Failure, Success

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
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def _add_node(self, node: Node) -> Success | Failure:
        if any(n.node_id == node.node_id for n in self.nodes):
            return Failure(f"Node {node.node_id} already exists")
        self.nodes.append(node)
        return Success()

    def _add_nodes(self, nodes: list[Node]) -> Success | Failure:
        for node in nodes:
            result = self._add_node(node)
            if isinstance(result, Failure):
                return result
        return Success()

    def _add_edge(self, edge: Edge) -> Success | Failure:
        if any(e.source_node_id == edge.source_node_id and e.target_node_id == edge.target_node_id for e in self.edges):
            return Success()
        self.edges.append(edge)
        return Success()

    def _add_edges(self, edges: list[Edge]) -> Success | Failure:
        for edge in edges:
            result = self._add_edge(edge)
            if isinstance(result, Failure):
                return result
        return Success()

    def _add_elements(self, elements: list[Node | Edge]) -> Success | Failure:
        nodes = [element for element in elements if isinstance(element, Node)]
        edges = [element for element in elements if isinstance(element, Edge)]
        result = self._add_nodes(nodes)
        if isinstance(result, Failure):
            return result
        result = self._add_edges(edges)
        if isinstance(result, Failure):
            return result
        return Success()

    def is_empty(self) -> bool:
        return len(self.nodes) == 0 and len(self.edges) == 0
