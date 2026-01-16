# This is your core logic function
from collections.abc import AsyncIterable, Callable
from urllib.parse import urlencode

from fasthtml.common import FT, Card, Div, FastHTML, StreamingResponse

CHAT_PROMPT_URL = "/chat/prompt"
CHAT_RESPONSE_STREAM_URL = "/chat/response-stream"


def setup_chat_routes(app: FastHTML, process_chat: Callable[[str], AsyncIterable[str]]) -> None:
    @app.post(CHAT_PROMPT_URL)
    def onboarding_start_tasks(prompt: str) -> FT:
        # Pass the list to the stream via a query parameter or session
        # For simplicity here, we'll pass names as a comma-separated string in the URL
        stream_url = f"{CHAT_RESPONSE_STREAM_URL}?{urlencode({'prompt': prompt})}"
        return Div(hx_ext="sse", sse_connect=stream_url)(Card(Div(sse_swap="message")("Processing chat prompt...")))

    @app.get(CHAT_RESPONSE_STREAM_URL)
    async def chat_response_stream(prompt: str) -> StreamingResponse:
        async def sse_generator() -> AsyncIterable[str]:
            async for msg in process_chat(prompt):
                # Manually do what EventStream does
                yield f"data: {msg}\n\n"

        return StreamingResponse(sse_generator(), media_type="text/event-stream")
