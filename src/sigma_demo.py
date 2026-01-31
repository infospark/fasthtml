from dataclasses import dataclass

from fasthtml.common import FT, H1, Div, FastHTML, Script, Title

from styles import CONTAINER_CLASSES, GRAPH_CONTAINER_STYLE

SIGMA_DEMO_URL = "/sigma-demo"

def setup_sigma_demo_routes(app: FastHTML) -> None:

    @app.get(SIGMA_DEMO_URL)
    def get_sigma_page() -> FT:
        return Div(
            Title("Sigma Demo"),

            Div(id="onboarding-container", cls=CONTAINER_CLASSES)(
                H1("Sigma Demo"),
                Script(src="https://unpkg.com/graphology@0.25.4/dist/graphology.umd.min.js"),
                Script(src="https://unpkg.com/sigma@3.0.0-beta.29/dist/sigma.min.js"),
                Div(id="graph-container", style=GRAPH_CONTAINER_STYLE),
                Script("""
                    const graph = new graphology.Graph();

                    // Add three nodes
                    graph.addNode("node1", { x: 0, y: 0, size: 10, label: "Node 1", color: "#4285F4" });
                    graph.addNode("node2", { x: 1, y: 0, size: 10, label: "Node 2", color: "#EA4335" });
                    graph.addNode("node3", { x: 0.5, y: 1, size: 10, label: "Node 3", color: "#FBBC04" });

                    // Connect each node to the other two
                    graph.addEdge("node1", "node2");
                    graph.addEdge("node2", "node3");
                    graph.addEdge("node3", "node1");

                    const renderer = new Sigma(graph, document.getElementById('graph-container'), {
                        renderLabels: true,
                        labelColor: { color: "blue" }
                    });

                    // EXPOSE FOR TESTING
                    window.graph = graph;
                    window.renderer = renderer;
                """)
        ))


@dataclass
class Edge:
    source: str
    target: str
