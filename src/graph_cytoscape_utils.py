from typing import Any

from fasthtml.common import FT, Script

from graph_manager import Graph

# Node styling
NODE_SIZE = 20
NODE_FONT_SIZE = 4
NODE_COLOR = "#666"
NODE_LABEL_COLOR = "blue"

# Edge styling
EDGE_WIDTH = 0.5
EDGE_COLOR = "#ccc"
EDGE_ARROW_SCALE = 0.3

# Layout
ANIMATION_DURATION_MS = 4000
LAYOUT_PADDING = 30


def graph_to_cytoscape_elements(graph: Graph) -> list[dict[str, Any]]:
    nodes = [{"data": {"id": node.node_id, "label": node.node_id}} for node in graph.nodes]
    edges = [{"data": {"source": edge.source_node_id, "target": edge.target_node_id}} for edge in graph.edges]
    return nodes + edges


def get_cytoscape_script(elements_json: str) -> FT:
    return Script(f"""
        const cy = cytoscape({{
            container: document.getElementById('graph-container'),
            elements: {elements_json},
            style: [
                {{
                    selector: 'node',
                    style: {{
                        'width': {NODE_SIZE},
                        'height': {NODE_SIZE},
                        'background-color': '{NODE_COLOR}',
                        'label': 'data(label)',
                        'font-size': {NODE_FONT_SIZE},
                        'color': '{NODE_LABEL_COLOR}',
                        'text-valign': 'center',
                        'text-halign': 'center'
                    }}
                }},
                {{
                    selector: 'edge',
                    style: {{
                        'width': {EDGE_WIDTH},
                        'line-color': '{EDGE_COLOR}',
                        'target-arrow-color': '{EDGE_COLOR}',
                        'target-arrow-shape': 'triangle',
                        'arrow-scale': {EDGE_ARROW_SCALE},
                        'curve-style': 'bezier'
                    }}
                }}
            ],
            layout: {{
                name: 'cose',
                animate: true,
                animationDuration: {ANIMATION_DURATION_MS},
                fit: true,
                padding: {LAYOUT_PADDING}
            }}
        }});

        // EXPOSE FOR TESTING
        window.cy = cy;
        window.graph = cy;
    """)
