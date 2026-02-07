import json
import logging

from fasthtml.common import FT, H1, Div, FastHTML, RedirectResponse, Script, Title

from data_types import Edge, Failure, GraphID, GraphManager, Node, NodeId
from styles import CONTAINER_CLASSES, GRAPH_CONTAINER_STYLE

GRAPH_URL = "/graph"


def create_new_graph_and_redirect(graph_manager: GraphManager) -> RedirectResponse:
    graph = graph_manager.create_graph()
    logging.info(f"Creating new graph with id: {graph.graph_id}")
    return RedirectResponse(f"{GRAPH_URL}?graph_id={graph.graph_id}")


def setup_graph_routes(app: FastHTML, graph_manager: GraphManager) -> None:
    @app.get(GRAPH_URL)
    def get_graph_page(graph_id: str | None = None) -> FT:
        if not graph_id:
            return create_new_graph_and_redirect(graph_manager)

        graph = graph_manager.get_graph(GraphID(graph_id))
        if isinstance(graph, Failure):
            return create_new_graph_and_redirect(graph_manager)

        # Add a starter graph
        graph.add_node(Node(node_id=NodeId("node1")))
        graph.add_node(Node(node_id=NodeId("node2")))
        graph.add_node(Node(node_id=NodeId("node3")))
        graph.add_edge(Edge(source_node_id=NodeId("node1"), target_node_id=NodeId("node2")))
        graph.add_edge(Edge(source_node_id=NodeId("node2"), target_node_id=NodeId("node3")))
        graph.add_edge(Edge(source_node_id=NodeId("node3"), target_node_id=NodeId("node1")))
        graphology_data = json.dumps(graph.get_graphology_data())

        content = Div(
            Title("Graph Demo"),
            Div(id="onboarding-container", cls=CONTAINER_CLASSES)(
                H1("Graph Demo"),
                Div(id="graph-container", style=GRAPH_CONTAINER_STYLE),
                Script(f"""
                    import Graph from 'https://cdn.jsdelivr.net/npm/graphology@0.25.4/+esm';
                    import Sigma from 'https://cdn.jsdelivr.net/npm/sigma@3.0.0-beta.29/+esm';
                    import forceAtlas2 from 'https://cdn.jsdelivr.net/npm/graphology-layout-forceatlas2@0.10.1/+esm';

                    const graph = new Graph();
                    graph.import({graphology_data});

                    // Apply force-directed layout
                    const settings = forceAtlas2.inferSettings(graph);
                    forceAtlas2.assign(graph, {{iterations: 100, settings}});

                    const renderer = new Sigma(graph, document.getElementById('graph-container'), {{
                        renderLabels: true,
                        labelColor: {{color: "blue"}}
                    }});

                    // EXPOSE FOR TESTING
                    window.graph = graph;
                    window.renderer = renderer;
                """, type="module"),
            ),
        )
        return content
