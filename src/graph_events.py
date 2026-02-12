import json
from collections.abc import AsyncGenerator

from data_types import EdgeAdded, GraphEvent, GraphID, GraphManager, NodeAdded


def graph_event_to_sse_data(event: GraphEvent) -> str:
    if isinstance(event, NodeAdded):
        return json.dumps({"type": "node_added", "graph_id": event.graph_id, "node_id": event.node.node_id})
    if isinstance(event, EdgeAdded):
        return json.dumps({"type": "edge_added", "graph_id": event.graph_id, "source_node_id": event.edge.source_node_id, "target_node_id": event.edge.target_node_id})


def graph_sse_stream(graph_manager: GraphManager, graph_id: GraphID) -> AsyncGenerator[str, None]:
    subscription = graph_manager.subscribe(graph_id)

    async def _stream() -> AsyncGenerator[str, None]:
        async for event in subscription:
            data = graph_event_to_sse_data(event)
            yield f"event: graph_update\ndata: {data}\n\n"

    return _stream()
