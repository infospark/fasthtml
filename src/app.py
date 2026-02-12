from collections.abc import AsyncIterable, Callable

from fasthtml.common import (
    FastHTML,
    Script,
    fast_app,
)

from chat_routes import parrot_chat, setup_chat_routes
from data_types import Failure
from dropadoc import setup_dropadoc_routes
from graph_manager import GraphManager
from graph_routes import setup_graph_routes
from onboarding_routes import setup_onboarding_routes
from styles import BODY_CLASSES, HTML_CLASSES

HTMX_REQUEST_HEADERS = {"HX-Request": "true"}
OK_CODE = 200
REDIRECT_CODES = [302, 307]

# Setup with SSE and Tailwind CDN
sse_hdr = Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")
tailwind_hdr = Script(src="https://cdn.tailwindcss.com")


def start_app(
    process_chat: Callable[[str, str], AsyncIterable[Failure | str | None]] = parrot_chat,
    graph_manager: None | GraphManager = None,) -> FastHTML:
    app, rt = fast_app(
        hdrs=(sse_hdr, tailwind_hdr),
        pico=False,
        htmlkw={"cls": HTML_CLASSES},
        bodykw={"cls": BODY_CLASSES},
    )
    if not graph_manager:
        graph_manager = GraphManager()
    setup_onboarding_routes(app)
    setup_chat_routes(app, process_chat)
    setup_dropadoc_routes(app)
    setup_graph_routes(app, graph_manager)
    return app
