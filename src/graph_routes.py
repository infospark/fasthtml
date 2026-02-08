import json
import logging

from fasthtml.common import FT, H1, Div, FastHTML, RedirectResponse, Script, Title

from data_types import Edge, Failure, Graph, GraphID, GraphManager, Node, NodeId, Success
from graph_cytoscape_utils import get_cytoscape_script, graph_to_cytoscape_elements
from styles import CONTAINER_CLASSES, GRAPH_CONTAINER_STYLE

GRAPH_URL = "/graph"


def create_new_graph_and_redirect(graph_manager: GraphManager) -> RedirectResponse:
    graph = graph_manager.create_graph()
    logging.info(f"Creating new graph with id: {graph.graph_id}")
    return RedirectResponse(f"{GRAPH_URL}?graph_id={graph.graph_id}")


def add_example_nodes_and_edges(graph: Graph) -> Success | Failure:
    try:
        graph.add_node(Node(node_id=NodeId("node1")))
        graph.add_node(Node(node_id=NodeId("node2")))
        graph.add_node(Node(node_id=NodeId("node3")))
        graph.add_edge(Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))
        graph.add_edge(Edge(source_node_id=NodeId("node2"), target_node_id=NodeId("node3")))
        graph.add_edge(Edge(source_node_id=NodeId("node3"), target_node_id=NodeId("node1")))
        return Success()
    except Exception as e:
        return Failure(f"Error adding example nodes and edges: {e}")


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
            add_example_nodes_and_edges(graph)
        elements = json.dumps(graph_to_cytoscape_elements(graph))

        content = Div(
            Title("Graph Demo"),
            Div(id="onboarding-container", cls=CONTAINER_CLASSES)(
                H1("Graph Demo"),
                Div(id="graph-container", style=GRAPH_CONTAINER_STYLE),
                Script(src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"),
                get_cytoscape_script(elements),
            ),
        )
        return content
