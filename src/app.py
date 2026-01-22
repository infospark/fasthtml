from collections.abc import AsyncIterable, Callable

from fasthtml.common import (
    FastHTML,
    Html,
    Script,
    Style,
    fast_app,
)

from chat import setup_chat_routes
from dragadoc import setup_dragadrop_routes
from onboarding import setup_onboarding_routes
from utils import Failure

HTMX_REQUEST_HEADERS = {"HX-Request": "true"}
OK = 200



# 1. Setup with SSE headers
sse_hdrs = Html(Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"))


chat_styles = Style("""
    /* The container that spans the full width of the chat */
    .message-row { display: flex; flex-direction: column; margin-bottom: 1.5rem; }
    /* User prompt bubble aligned to the right */
    .user-message {
        align-self: flex-end;
        background-color: #2f2f2f; /* Darker gray for user bubble */
        color: #e3e3e3;
        padding: 0.75rem 1.25rem;
        border-radius: 1.5rem;
        border-bottom-right-radius: 0.25rem; /* Makes it look like a speech bubble */
        max-width: 80%;
    }
    /* AI response container on the left */
    .ai-response {
        align-self: flex-start;
        width: 100%;
        margin-top: 1rem;
        color: white;
    }
    /* New message form */
    .new-message-form {
        margin-top: 3rem;
    }
    /* CHAT_RESPONSE_CONTENT_ID give some margin-top to the first response */
    #response-content {
        margin-top: 3rem;
    }
""")


def start_app(process_chat: Callable[[str, str], AsyncIterable[Failure | str | None]]) -> FastHTML:
    app, rt = fast_app(hdrs=[sse_hdrs, chat_styles, Script('document.documentElement.setAttribute("data-theme", "dark")')])

    setup_onboarding_routes(app)
    setup_chat_routes(app, process_chat)
    setup_dragadrop_routes(app)

    return app
