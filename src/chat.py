# This is your core logic function
import asyncio
import logging
from collections.abc import AsyncIterable, Callable
from urllib.parse import urlencode

from fasthtml.common import FT, H2, Article, Button, Card, Div, FastHTML, Form, Header, Input, Main, P, StreamingResponse, Title

from utils import format_for_sse

CHAT_URL = "/chat"
CHAT_PROMPT_URL = "/chat/prompt"
CHAT_RESPONSE_STREAM_URL = "/chat/response-stream"


def setup_chat_routes(app: FastHTML, process_chat: Callable[[str], AsyncIterable[str]]) -> None:
    def get_chat_container() -> FT:
        return (
            Title("Chat"),
            H2("Chat"),
            Div(id="chat-container")(
                Form(hx_post=post_chat_prompt, hx_target="#response-box-content", hx_swap="innerHTML")(
                    Input(name="prompt"),
                    Button("Submit", id="submit-btn", cls="primary"),
                ),
                Article(id="response-box")(
                    Header("Response"),
                    Div(id="response-box-content"),
                ),
            ),
        )

    @app.get(CHAT_URL)
    def get_chat_page() -> FT:
        logging.info("Getting chat page")
        return Main(cls="container")(get_chat_container())

    @app.post(CHAT_PROMPT_URL)
    def post_chat_prompt(prompt: str) -> FT:
        # Pass the prompt in and return a div that will be filled with the response stream
        logging.info(f"Posting chat prompt: {prompt}")
        stream_url = f"{CHAT_RESPONSE_STREAM_URL}?{urlencode({'prompt': prompt})}"
        return Div(id="sse-container", hx_ext="sse", sse_connect=stream_url)(Card(Div(sse_swap="message")("Processing chat prompt...")))

    @app.get(CHAT_RESPONSE_STREAM_URL)
    async def get_chat_response_stream(prompt: str) -> StreamingResponse:
        logging.info(f"Getting chat response stream for prompt: {prompt}")

        # TODO - aggregate the responses - adding each time not replacing the entire container
        async def sse_generator() -> AsyncIterable[str]:
            async for msg in process_chat(prompt):
                # Manually do what EventStream does
                yield format_for_sse(Div(msg))
            await asyncio.sleep(0.5)
            logging.info("Chat response stream completed")
            yield format_for_sse(
                # We replace the entire container by ID
                Div(id="sse-container", hx_swap_oob="true")(
                    P("The connection is now closed."),
                )
            )

        return StreamingResponse(sse_generator(), media_type="text/event-stream")
