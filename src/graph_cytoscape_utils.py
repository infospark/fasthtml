from typing import Any
from urllib.parse import quote

from fasthtml.common import FT, Script

from graph import DOCUMENT, NOT_SPECIFIED, PERSON, Node, NodeType
from graph_manager import Graph

# Font Awesome Free 6.7.2 (CC BY 4.0) — https://fontawesome.com/license/free
_PERSON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path fill="#FFFFFF" d="M224 256A128 128 0 1 0 224 0a128 128 0 1 0 0 256zm-45.7 48C79.8 304 0 383.8 0 482.3C0 498.7 13.3 512 29.7 512l388.6 0c16.4 0 29.7-13.3 29.7-29.7C448 383.8 368.2 304 269.7 304l-91.4 0z"/></svg>'
_DOCUMENT_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><path fill="#FFFFFF" d="M0 64C0 28.7 28.7 0 64 0L224 0l0 128c0 17.7 14.3 32 32 32l128 0 0 288c0 35.3-28.7 64-64 64L64 512c-35.3 0-64-28.7-64-64L0 64zm384 64l-128 0L256 0 384 128z"/></svg>'
_NOT_SPECIFIED_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="#FFFFFF" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM169.8 165.3c7.9-22.3 29.1-37.3 52.8-37.3l58.3 0c34.9 0 63.1 28.3 63.1 63.1c0 22.6-12.1 43.5-31.7 54.8L280 264.4c-.2 13-10.9 23.6-24 23.6c-13.3 0-24-10.7-24-24l0-13.5c0-8.6 4.6-16.5 12.1-20.8l44.3-25.4c4.7-2.7 7.6-7.7 7.6-13.1c0-8.4-6.8-15.1-15.1-15.1l-58.3 0c-3.4 0-6.4 2.1-7.5 5.3l-.4 1.2c-4.4 12.5-18.2 19-30.6 14.6s-19-18.2-14.6-30.6l.4-1.2zM224 352a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"/></svg>'

_ICON_MAP: dict[NodeType, str] = {
    PERSON: f"data:image/svg+xml,{quote(_PERSON_SVG)}",
    DOCUMENT: f"data:image/svg+xml,{quote(_DOCUMENT_SVG)}",
    NOT_SPECIFIED: f"data:image/svg+xml,{quote(_NOT_SPECIFIED_SVG)}",
}


def node_type_to_icon(node_type: NodeType) -> str:
    return _ICON_MAP.get(node_type, _ICON_MAP[NOT_SPECIFIED])


# Node styling
NODE_SIZE = 5
NODE_FONT_SIZE = 2
NODE_COLOR = "white"
NODE_LABEL_COLOR = "white"

# Edge styling
EDGE_WIDTH = 0.1
EDGE_COLOR = "#ccc"
EDGE_ARROW_SCALE = 0.1

# Layout
ANIMATION_DURATION_MS = 4000
LAYOUT_PADDING = 30


def node_to_cytoscape_element(node: Node) -> dict[str, Any]:
    return {"data": {"id": node.node_id, "label": node.node_id, "type": node.type}}


def graph_to_cytoscape_elements(graph: Graph) -> list[dict[str, Any]]:
    nodes = [node_to_cytoscape_element(node) for node in graph.nodes]
    edges = [{"data": {"source": edge.source_node_id, "target": edge.target_node_id}} for edge in graph.edges]
    return nodes + edges


def _node_type_style(node_type: NodeType) -> str:
    icon = node_type_to_icon(node_type)
    return f"""{{
                    selector: 'node[type="{node_type}"]',
                    style: {{
                        'background-image': '{icon}',
                        'background-fit': 'contain',
                        'background-clip': 'none',
                        'background-opacity': 0
                    }}
                }}"""


def get_cytoscape_script(elements_json: str) -> FT:
    type_styles = ",\n                ".join(_node_type_style(t) for t in [PERSON, DOCUMENT, NOT_SPECIFIED])
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
                        'label': 'data(label)',
                        'font-size': {NODE_FONT_SIZE},
                        'color': '{NODE_LABEL_COLOR}',
                        'text-valign': 'bottom',
                        'text-halign': 'center',
                        'text-margin-y': 4
                    }}
                }},
                {type_styles},
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
                name: 'cola',
                infinite: true,
                convergenceThreshold: 0.5,
                fit: true,
                padding: {LAYOUT_PADDING}
            }}
        }});

        // EXPOSE FOR TESTING
        window.cy = cy;
        window.graph = cy;
    """)


def get_graph_sse_script(events_url: str, graph_id: str) -> FT:
    return Script(f"""
        const evtSource = new EventSource("{events_url}?graph_id={graph_id}");
        evtSource.addEventListener("graph_update", function(e) {{
            const data = JSON.parse(e.data);
            if (data.type === "node_added") {{
                window.cy.add({{ group: 'nodes', data: {{ id: data.node_id, label: data.node_id }} }});
            }} else if (data.type === "edge_added") {{
                window.cy.add({{ group: 'edges', data: {{ source: data.source_node_id, target: data.target_node_id }} }});
            }}
        }});
    """)
