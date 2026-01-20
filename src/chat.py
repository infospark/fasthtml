# This is your core logic function
import asyncio
import logging
from collections.abc import AsyncIterable, Callable
from urllib.parse import urlencode

from fasthtml.common import FT, Article, Button, Div, FastHTML, Form, Input, Main, P, Span, StreamingResponse

from utils import format_for_sse

CHAT_URL = "/chat"
CHAT_PROMPT_URL = "/chat/prompt"
CHAT_RESPONSE_STREAM_URL = "/chat/response-stream"
SSE_DIV_ID = "sse-div"
MESSAGE_CONTAINER_ID = "message-container"
CONVERSATION_CONTAINER_ID = "conversation-container"


def setup_chat_routes(app: FastHTML, process_chat: Callable[[str], AsyncIterable[str]]) -> None:
    def get_message_form() -> FT:
        return (
            Div(id=MESSAGE_CONTAINER_ID)(
                Form(hx_post=post_chat_prompt, hx_target=f"#{MESSAGE_CONTAINER_ID}", hx_swap="outerHTML")(
                    Input(
                        name="prompt",
                        cls="secondary",  # This makes it gray in Dark Mode
                        style="border-radius: 2rem;",
                    ),
                    Button("Submit", id="submit-btn", cls="primary", hidden=True),
                )
            ),
        )

    @app.get(CHAT_URL)
    def get_chat_page() -> FT:
        logging.info("Getting chat page")
        return Main(cls="container")(Article(id=CONVERSATION_CONTAINER_ID)(get_message_form()))

    @app.post(CHAT_PROMPT_URL)
    def post_chat_prompt(prompt: str) -> FT:
        # Pass the prompt in and return a div that will be filled with the response stream
        logging.info(f"Posting chat prompt: {prompt}")
        stream_url = f"{CHAT_RESPONSE_STREAM_URL}?{urlencode({'prompt': prompt})}"

        # Return the original prompt - now read only - and two divs - one for the sse and one for the response
        return Div()(
            Div(cls="message-row")(
                Div(prompt, cls="user-message"),
                Div(id="response-box", cls="ai-response")(
                    Div(id=SSE_DIV_ID, hx_ext="sse", sse_connect=stream_url, sse_swap="message", hx_swap="beforeend", hx_target="#response-content")(),
                    Div(id="response-content")(),
                ),
            ),
        )

    @app.get(CHAT_RESPONSE_STREAM_URL)
    async def get_chat_response_stream(prompt: str) -> StreamingResponse:
        logging.info(f"Getting chat response stream for prompt: {prompt}")

        async def sse_generator() -> AsyncIterable[str]:
            async for msg in process_chat(prompt):
                # Manually do what EventStream does
                yield format_for_sse(Span(msg))
            await asyncio.sleep(0.5)
            logging.info("Chat response stream completed")
            yield format_for_sse(P("End."))
            # add a new message form - use htmx to target beforeend of the conversation container
            yield format_for_sse(Div(hx_target=f"#{CONVERSATION_CONTAINER_ID}", hx_swap="beforeend")(Div()(get_message_form())))
            # replace the sse container with an emtpy one to close down the SSE connection
            yield format_for_sse(Div(id=SSE_DIV_ID, hx_swap_oob="true")())

        return StreamingResponse(sse_generator(), media_type="text/event-stream")
