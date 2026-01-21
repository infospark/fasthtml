# This is your core logic function
import asyncio
import logging
import os
import re
from collections.abc import AsyncIterable, Callable
from urllib.parse import urlencode

from fasthtml.common import FT, Article, Button, Div, FastHTML, Form, Input, Main, Span, StreamingResponse, Textarea
from google import genai

from utils import Failure, format_for_sse

CHAT_URL = "/chat"
CHAT_PROMPT_URL = "/chat/prompt"
CHAT_RESPONSE_STREAM_URL = "/chat/response-stream"

SSE_DIV_ID = "sse-div"
MESSAGE_CONTAINER_ID = "message-container"
CONVERSATION_CONTAINER_ID = "conversation-container"
CHAT_RESPONSE_CONTENT_ID = "response-content"

MOCK_RESPONSE_TIME = 0.5

GEMINI_MODEL = "gemini-2.0-flash"


def split_string_into_words(s: str) -> list[str]:
    # Split on puncuation and whitespace but keep the punctuation and whitespace in the response
    return re.findall(r"\S+\s*", s)


async def parrot_chat(prompt: str) -> AsyncIterable[Failure | str | None]:
    # This chat function is used for testing and just returns the prompt split into words
    responses = split_string_into_words(prompt)
    for r in responses:
        await asyncio.sleep(MOCK_RESPONSE_TIME)
        logging.info(f"process_chat:Yielding response: {r}")
        yield r


async def gemini_chat(prompt: str, api_key_env_var: str = "GEMINI_API_KEY") -> AsyncIterable[Failure | str | None]:
    gemini_api_key = os.getenv(api_key_env_var)
    if not gemini_api_key:
        yield Failure(f"{api_key_env_var} is not set")
    else:
        client = genai.Client(api_key=gemini_api_key)

        # Use .aio to access asynchronous methods
        response = await client.aio.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        async for chunk in response:
            yield chunk.text


def setup_chat_routes(app: FastHTML, process_chat: Callable[[str], AsyncIterable[Failure | str | None]]) -> None:
    def get_message_form(conversation: str = "") -> FT:
        logging.info("setup_chat_routes: Rendering the message form with conversation: {conversation}")
        return (
            Div(id=MESSAGE_CONTAINER_ID)(
                Form(hx_post=post_chat_prompt, hx_target=f"#{MESSAGE_CONTAINER_ID}", hx_swap="outerHTML")(
                    Input(
                        name="prompt",
                        cls="secondary",  # This makes it gray in Dark Mode
                        style="border-radius: 2rem;",
                    ),
                    Button("Submit", id="submit-btn", cls="primary", hidden=True),
                    Textarea(conversation, name="conversation"),
                )
            ),
        )

    @app.get(CHAT_URL)
    def get_chat_page() -> FT:
        logging.info("Getting chat page")
        return Main(cls="container")(Article(id=CONVERSATION_CONTAINER_ID)(get_message_form(conversation="Conversation begins here")))

    @app.post(CHAT_PROMPT_URL)
    def post_chat_prompt(prompt: str, conversation: str = "") -> FT:
        # Pass the prompt and conversation in and return a div that will be filled with the response stream
        logging.info(f"post_chat_prompt: {prompt} with conversation: {conversation}")
        # Add the prompt to the conversation
        conversation += f"\nUser: {prompt}"
        stream_url = f"{CHAT_RESPONSE_STREAM_URL}?{urlencode({'prompt': prompt, 'conversation': conversation})}"
        # Return the original prompt - now read only - and two divs - one for the sse and one for the response
        return Div()(
            Div(cls="message-row")(
                Div(prompt, cls="user-message"),
                Div(id="response-box", cls="ai-response")(
                    Div(id=SSE_DIV_ID, hx_ext="sse", sse_connect=stream_url, sse_swap="message", hx_swap="beforeend", hx_target=f"#{CHAT_RESPONSE_CONTENT_ID}")(),
                    Div(id=CHAT_RESPONSE_CONTENT_ID)(),
                ),
            ),
        )

    @app.get(CHAT_RESPONSE_STREAM_URL)
    async def get_chat_response_stream(prompt: str, conversation: str) -> StreamingResponse:
        logging.info(f"get_chat_response_stream: Getting chat response stream for prompt: {prompt} and conversation: {conversation}")

        async def sse_generator(conversation: str) -> AsyncIterable[str]:
            aggregated_response = ""
            async for msg in process_chat(prompt):
                # Keep track of the whole response so far
                if isinstance(msg, str):
                    aggregated_response += msg
                elif isinstance(msg, Failure):
                    logging.error(f"get_chat_response_stream: Error: {msg.message}")
                    break
                # Yield each chunk of the response so the browser can render it incrementally
                yield format_for_sse(Span(msg))
            await asyncio.sleep(0.5)
            logging.info("Chat response stream completed")
            # We need to update the conversation with the final response from the process_chat function
            conversation += f"\nAI: {aggregated_response}"

            # add a new message form - use htmx to target beforeend of the conversation container
            yield format_for_sse(Div(hx_target=f"#{CONVERSATION_CONTAINER_ID}", hx_swap="beforeend")(Div()(get_message_form(conversation=conversation))))

            # replace the sse container with an emtpy one to close down the SSE connection
            yield format_for_sse(Div(id=SSE_DIV_ID, hx_swap_oob="true")())

        return StreamingResponse(sse_generator(conversation=conversation), media_type="text/event-stream")
