from fasthtml.common import FT, to_xml


def format_for_sse(ft: FT, event: str = "message") -> str:
    content = to_xml(ft).replace("\n", "")
    return f"event: {event}\ndata: {content}\n\n"
