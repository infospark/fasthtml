from collections.abc import AsyncIterable, Callable

from fasthtml.common import (
    FastHTML,
    Script,
    fast_app,
)

from chat import setup_chat_routes
from dropadoc import setup_dropadoc_routes
from onboarding import setup_onboarding_routes
from sigma_demo import setup_sigma_demo_routes
from styles import BODY_CLASSES, HTML_CLASSES
from utils import Failure

HTMX_REQUEST_HEADERS = {"HX-Request": "true"}
OK = 200

# Setup with SSE and Tailwind CDN
sse_hdr = Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")
tailwind_hdr = Script(src="https://cdn.tailwindcss.com")

def start_app(process_chat: Callable[[str, str], AsyncIterable[Failure | str | None]]) -> FastHTML:
    app, rt = fast_app(
        hdrs=(sse_hdr, tailwind_hdr),
        pico=False,
        htmlkw={"cls": HTML_CLASSES},
        bodykw={"cls": BODY_CLASSES},
    )

    setup_onboarding_routes(app)
    setup_chat_routes(app, process_chat)
    setup_dropadoc_routes(app)
    setup_sigma_demo_routes(app)
    return app
