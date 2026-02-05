import re

from fasthtml.common import FT, to_xml


def format_for_sse(ft: FT, event: str = "message") -> str:
    content = to_xml(ft).replace("\n", "")
    return f"event: {event}\ndata: {content}\n\n"


def split_string_into_words(s: str) -> list[str]:
    # Split on punctuation and whitespace but keep the punctuation and whitespace in the response
    return re.findall(r"\S+\s*", s)
