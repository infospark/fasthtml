import asyncio
import logging
from collections.abc import AsyncIterable, Callable

from fasthtml.common import (
    FastHTML,
    Html,
    Script,
    fast_app,
)

from chat import setup_chat_routes
from onboarding import setup_onboarding_routes

HTMX_REQUEST_HEADERS = {"HX-Request": "true"}
OK = 200

MOCK_RESPONSE_TIME = 0.5

# 1. Setup with SSE headers
sse_hdrs = Html(Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"))


async def process_chat(prompt: str) -> AsyncIterable[str]:
    responses = ["hello", "world"]
    for resp in responses:
        await asyncio.sleep(MOCK_RESPONSE_TIME)
        logging.info(f"process_chat:Yielding response: {resp}")
        yield resp


def start_app(process_chat: Callable[[str], AsyncIterable[str]]) -> FastHTML:
    app, rt = fast_app(hdrs=[sse_hdrs])

    setup_onboarding_routes(app)
    setup_chat_routes(app, process_chat)

    return app
