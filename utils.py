from fasthtml.common import FT, to_xml


def format_for_sse(ft: FT) -> str:
    content = to_xml(ft).replace("\n", "")
    return f"event: message\ndata: {content}\n\n"
