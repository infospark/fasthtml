from graph import DOCUMENT, NOT_SPECIFIED, PERSON, Node, NodeId, NodeType
from graph_cytoscape_utils import node_to_cytoscape_element, node_type_to_icon


def test_node_to_cytoscape_element_default_type() -> None:
    node = Node(node_id=NodeId("node1"))
    result = node_to_cytoscape_element(node)
    assert result == {"data": {"id": "node1", "label": "node1", "type": NOT_SPECIFIED}}


def test_node_to_cytoscape_element_person_type() -> None:
    node = Node(node_id=NodeId("node1"), type=PERSON)
    result = node_to_cytoscape_element(node)
    assert result == {"data": {"id": "node1", "label": "node1", "type": PERSON}}


def test_node_to_cytoscape_element_document_type() -> None:
    node = Node(node_id=NodeId("node1"), type=DOCUMENT)
    result = node_to_cytoscape_element(node)
    assert result == {"data": {"id": "node1", "label": "node1", "type": DOCUMENT}}


def test_node_type_to_icon_person() -> None:
    result = node_type_to_icon(PERSON)
    assert result.startswith("data:image/svg+xml,")
    assert "viewBox" in result


def test_node_type_to_icon_document() -> None:
    result = node_type_to_icon(DOCUMENT)
    assert result.startswith("data:image/svg+xml,")
    assert "viewBox" in result


def test_node_type_to_icon_not_specified() -> None:
    result = node_type_to_icon(NOT_SPECIFIED)
    assert result.startswith("data:image/svg+xml,")
    assert "viewBox" in result


def test_node_type_to_icon_returns_different_icons() -> None:
    person_icon = node_type_to_icon(PERSON)
    document_icon = node_type_to_icon(DOCUMENT)
    not_specified_icon = node_type_to_icon(NOT_SPECIFIED)
    assert person_icon != document_icon
    assert person_icon != not_specified_icon
    assert document_icon != not_specified_icon


def test_node_type_to_icon_unknown_type_returns_not_specified() -> None:
    result = node_type_to_icon(NodeType("SomethingElse"))
    assert result == node_type_to_icon(NOT_SPECIFIED)
