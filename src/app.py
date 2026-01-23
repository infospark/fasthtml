from collections.abc import AsyncIterable, Callable

from fasthtml.common import (
    FastHTML,
    Html,
    Script,
    Style,
    fast_app,
)

from chat import setup_chat_routes
from dropadoc import setup_dragadrop_routes
from onboarding import setup_onboarding_routes
from utils import Failure

HTMX_REQUEST_HEADERS = {"HX-Request": "true"}
OK = 200



# 1. Setup with SSE headers
sse_hdrs = Html(Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"))


chat_styles = Style("""
    html, body {
        background-color: #000;
        color: #fff;
    }
    main, .container, .chat-shell, .conversation-pane {
        background-color: #000;
    }
    /* The container that spans the full width of the chat */
    .message-row { display: flex; flex-direction: column; margin-bottom: 1.5rem; }
    /* User prompt bubble aligned to the right */
    .user-message {
        align-self: flex-end;
        background-color: #1a1a1a; /* Slight contrast on black */
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
        margin-top: 1.5rem;
    }
    input[name="prompt"] {
        border-radius: 2rem;
        border: 2px solid transparent;
        background:
            linear-gradient(#1a1a1a, #1a1a1a) padding-box,
            linear-gradient(90deg, #ff5f6d, #ffc371, #9be15d, #00d2ff, #7f00ff) border-box;
        outline: none;
    }
    /* CHAT_RESPONSE_CONTENT_CLASS give some margin-top to the first response */
    .response-content {
        margin-top: 3rem;
    }
    .chat-shell {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }
    .conversation-pane {
        flex: 1 1 auto;
        overflow-y: auto;
        padding-bottom: 6rem;
    }
    #message-container {
        position: sticky;
        bottom: 0;
        padding-top: 1rem;
        background: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.85) 30%, rgba(0, 0, 0, 1) 100%);
    }
""")


def start_app(process_chat: Callable[[str, str], AsyncIterable[Failure | str | None]]) -> FastHTML:
    focus_script = Script(
        """
        const focusPromptInput = () => {
            const input = document.querySelector('#message-container input[name="prompt"]');
            if (input) {
                input.focus();
                const end = input.value.length;
                input.setSelectionRange(end, end);
            }
        };

        document.body.addEventListener('htmx:oobAfterSwap', (event) => {
            if (event.target && event.target.id === 'message-container') {
                requestAnimationFrame(focusPromptInput);
            }
        });

        document.body.addEventListener('htmx:afterSwap', (event) => {
            if (event.target && event.target.id === 'message-container') {
                requestAnimationFrame(focusPromptInput);
            }
        });

        window.addEventListener('DOMContentLoaded', () => {
            requestAnimationFrame(focusPromptInput);
        });
        """
    )
    app, rt = fast_app(hdrs=[sse_hdrs, chat_styles, focus_script, Script('document.documentElement.setAttribute("data-theme", "dark")')])

    setup_onboarding_routes(app)
    setup_chat_routes(app, process_chat)
    setup_dragadrop_routes(app)

    return app
