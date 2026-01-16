import asyncio
from collections.abc import AsyncIterable

from fasthtml.common import (
    Html,
    Script,
    fast_app,
    serve,
)

from chat import setup_chat_routes
from onboarding import setup_onboarding_routes

HTMX_REQUEST_HEADERS = {"HX-Request": "true"}
OK = 200

MOCK_RESPONSE_TIME = 0.1

# 1. Setup with SSE headers
sse_hdrs = Html(Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"))
app, rt = fast_app(hdrs=[sse_hdrs])


async def process_chat(prompt: str) -> AsyncIterable[str]:
    responses = ["hello", "world"]
    for resp in responses:
        await asyncio.sleep(MOCK_RESPONSE_TIME)
        yield resp


setup_onboarding_routes(app)
setup_chat_routes(app, process_chat)

serve()
