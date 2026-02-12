import asyncio
import uuid
from collections import defaultdict
from collections.abc import AsyncGenerator
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
class NodeAdded:
    graph_id: GraphID
    node: Node


@dataclass
class EdgeAdded:
    graph_id: GraphID
    edge: Edge


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


GraphEvent = NodeAdded | EdgeAdded


@dataclass
class GraphManager:
    _graphs: dict[GraphID, Graph] = field(default_factory=dict)
    _subscribers: dict[GraphID, set[asyncio.Queue[GraphEvent]]] = field(default_factory=lambda: defaultdict(set))

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

    def add_node(self, graph_id: GraphID, node: Node) -> Success | Failure:
        graph = self._graphs.get(graph_id)
        if graph is None:
            return Failure(f"Graph with id {graph_id} not found")
        result = graph._add_node(node)
        if isinstance(result, Failure):
            return result
        self._publish(NodeAdded(graph_id=graph_id, node=node))
        return Success()

    def add_edge(self, graph_id: GraphID, edge: Edge) -> Success | Failure:
        graph = self._graphs.get(graph_id)
        if graph is None:
            return Failure(f"Graph with id {graph_id} not found")
        result = graph._add_edge(edge)
        if isinstance(result, Failure):
            return result
        self._publish(EdgeAdded(graph_id=graph_id, edge=edge))
        return Success()

    def subscribe(self, graph_id: GraphID) -> AsyncGenerator[GraphEvent, None]:
        queue: asyncio.Queue[GraphEvent] = asyncio.Queue()
        self._subscribers[graph_id].add(queue)

        async def _stream() -> AsyncGenerator[GraphEvent, None]:
            try:
                while True:
                    yield await queue.get()
            finally:
                self._subscribers[graph_id].remove(queue)
                if not self._subscribers[graph_id]:
                    del self._subscribers[graph_id]

        return _stream()

    def _publish(self, event: GraphEvent) -> None:
        queues = self._subscribers.get(event.graph_id, set())
        for queue in queues:
            queue.put_nowait(event)
