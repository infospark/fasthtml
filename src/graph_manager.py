import asyncio
import json
import logging
import uuid
from collections import defaultdict
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field

from data_types import Failure, Success
from graph import Edge, Graph, GraphID, Node


@dataclass
class NodeAdded:
    graph_id: GraphID
    node: Node


@dataclass
class EdgeAdded:
    graph_id: GraphID
    edge: Edge

GraphEvent = NodeAdded | EdgeAdded


@dataclass
class GraphManager:
    _graphs: dict[GraphID, Graph] = field(default_factory=dict)
    _subscribers: dict[GraphID, set[asyncio.Queue[GraphEvent]]] = field(default_factory=lambda: defaultdict(set))
    # The ASGI server (Uvicorn) event loop, captured on first subscribe().
    # We need this so _publish() can safely put events on asyncio.Queue from any thread.
    _loop: asyncio.AbstractEventLoop | None = field(default=None, init=False)

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
        self._loop = asyncio.get_running_loop()
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
        if not self._loop:
            return
        for queue in queues:
            # asyncio.Queue is not thread-safe, so we can't call put_nowait() directly
            # from another thread. call_soon_threadsafe schedules put_nowait to run on
            # the event loop's thread, which properly wakes up any "await queue.get()".
            self._loop.call_soon_threadsafe(queue.put_nowait, event)


def graph_event_to_sse_data(event: GraphEvent) -> str:
    if isinstance(event, NodeAdded):
        return json.dumps({"type": "node_added", "graph_id": event.graph_id, "node_id": event.node.node_id})
    if isinstance(event, EdgeAdded):
        return json.dumps({"type": "edge_added", "graph_id": event.graph_id, "source_node_id": event.edge.source_node_id, "target_node_id": event.edge.target_node_id})


def graph_sse_stream(graph_manager: GraphManager, graph_id: GraphID, stop_after_n: int | None = None) -> AsyncGenerator[str, None]:
    subscription = graph_manager.subscribe(graph_id)

    async def _stream() -> AsyncGenerator[str, None]:
        count = 0
        logging.info(f"graph_sse_stream: Subscribed to graph {graph_id}")
        async for event in subscription:
            logging.info(f"graph_sse_stream: Yielding event: {event}")
            data = graph_event_to_sse_data(event)
            yield f"event: graph_update\ndata: {data}\n\n"
            count += 1
            if stop_after_n is not None and count >= stop_after_n:
                logging.info(f"graph_sse_stream: Stopping after {count} events")
                return

    return _stream()
