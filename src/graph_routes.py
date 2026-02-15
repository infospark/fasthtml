import json
import logging

from fasthtml.common import FT, H1, Div, FastHTML, RedirectResponse, Script, StreamingResponse, Title

from data_types import Failure, Success
from graph import DOCUMENT, PERSON, Edge, GraphID, Node, NodeId
from graph_cytoscape_utils import get_cytoscape_script, get_graph_sse_script, graph_to_cytoscape_elements
from graph_manager import GraphManager, graph_sse_stream
from styles import CONTAINER_CLASSES, GRAPH_CONTAINER_STYLE

GRAPH_URL = "/graph"
GRAPH_EVENTS_URL = "/graph/events"


def create_new_graph_and_redirect(graph_manager: GraphManager) -> RedirectResponse:
    graph = graph_manager.create_graph()
    logging.info(f"Creating new graph with id: {graph.graph_id}")
    return RedirectResponse(f"{GRAPH_URL}?graph_id={graph.graph_id}")


def add_example_nodes_and_edges(graph_manager: GraphManager, graph_id: GraphID) -> Success | Failure:
    for node in [Node(node_id=NodeId("node1"), type=PERSON), Node(node_id=NodeId("node2"), type=DOCUMENT), Node(node_id=NodeId("node3"), type=PERSON)]:
        result = graph_manager.add_node(graph_id, node)
        if isinstance(result, Failure):
            return result
    for edge in [
        Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")),
        Edge(source_node_id=NodeId("node2"), target_node_id=NodeId("node1")),
        Edge(source_node_id=NodeId("node2"), target_node_id=NodeId("node3")),
        Edge(source_node_id=NodeId("node3"), target_node_id=NodeId("node1")),
    ]:
        result = graph_manager.add_edge(graph_id, edge)
        if isinstance(result, Failure):
            return result
    return Success()


def setup_graph_routes(app: FastHTML, graph_manager: GraphManager) -> None:
    @app.get(GRAPH_URL)
    def get_graph_page(graph_id: str | None = None) -> FT:
        if not graph_id:
            return create_new_graph_and_redirect(graph_manager)

        graph = graph_manager.get_graph(GraphID(graph_id))
        if isinstance(graph, Failure):
            return create_new_graph_and_redirect(graph_manager)

        # Add a starter graph
        if graph.is_empty():
            add_example_nodes_and_edges(graph_manager, GraphID(graph_id))
        elements = json.dumps(graph_to_cytoscape_elements(graph))

        content = Div(
            Title("Graph Demo"),
            Div(id="onboarding-container", cls=CONTAINER_CLASSES)(
                H1("Graph Demo"),
                Div(id="graph-container", style=GRAPH_CONTAINER_STYLE),
                Script(src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"),
                Script(src="https://unpkg.com/cytoscape-euler/cytoscape-euler.js"),
                get_cytoscape_script(elements),
                get_graph_sse_script(GRAPH_EVENTS_URL, graph_id),
            ),
        )
        return content

    @app.get(GRAPH_EVENTS_URL)
    async def get_graph_events(graph_id: str, stop_after_n: int | None = None) -> StreamingResponse:
        logging.info(f"get_graph_events: Getting graph events for graph {graph_id} with stop_after_n: {stop_after_n}")
        return StreamingResponse(
            graph_sse_stream(graph_manager, GraphID(graph_id), stop_after_n=stop_after_n),
            media_type="text/event-stream",
        )
