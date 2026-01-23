# This is your core logic function
import asyncio
import logging
import os
import re
from collections.abc import AsyncIterable, Callable
from urllib.parse import urlencode
from uuid import uuid4

from fasthtml.common import FT, Article, Button, Div, FastHTML, Form, Input, Main, Span, StreamingResponse, Textarea
from google import genai

from utils import Failure, format_for_sse

CHAT_URL = "/chat"
CHAT_PROMPT_URL = "/chat/prompt"
CHAT_RESPONSE_STREAM_URL = "/chat/response-stream"

SSE_DIV_ID = "sse-div"
MESSAGE_CONTAINER_ID = "message-container"
CONVERSATION_CONTAINER_ID = "conversation-container"
CHAT_RESPONSE_CONTENT_CLASS = "response-content"

MOCK_RESPONSE_TIME = 0.5

GEMINI_MODEL = "gemini-2.0-flash"


def split_string_into_words(s: str) -> list[str]:
    # Split on punctuation and whitespace but keep the punctuation and whitespace in the response
    return re.findall(r"\S+\s*", s)


async def parrot_chat(prompt: str, conversation: str = "") -> AsyncIterable[Failure | str | None]:
    # This chat function is used for testing and just returns the prompt split into words
    logging.info(f"parrot_chat: Prompt: {prompt} Conversation: {conversation}")
    responses = split_string_into_words(prompt)
    for r in responses:
        await asyncio.sleep(MOCK_RESPONSE_TIME)
        logging.info(f"process_chat:Yielding response: {r}")
        yield r


STANDARD_PROMPT = "You are a helpful assistant."


async def gemini_chat(prompt: str, conversation: str = "", api_key_env_var: str = "GEMINI_API_KEY") -> AsyncIterable[Failure | str | None]:
    gemini_api_key = os.getenv(api_key_env_var)
    if not gemini_api_key:
        yield Failure(f"{api_key_env_var} is not set")
    else:
        client = genai.Client(api_key=gemini_api_key)

        content = f"{STANDARD_PROMPT}\n{conversation}\nUser: {prompt}"

        # Use .aio to access asynchronous methods
        response = await client.aio.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=content,
        )

        async for chunk in response:
            yield chunk.text


def _make_response_ids() -> tuple[str, str, str]:
    suffix = uuid4().hex
    return f"response-box-{suffix}", f"response-content-{suffix}", f"{SSE_DIV_ID}-{suffix}"


def setup_chat_routes(app: FastHTML, process_chat: Callable[[str, str], AsyncIterable[Failure | str | None]]) -> None:
    def get_message_form(conversation: str = "", swap_oob: str | None = None) -> FT:
        logging.info("setup_chat_routes: Rendering the message form with conversation: {conversation}")
        return (
            Div(
                id=MESSAGE_CONTAINER_ID,
                hx_swap_oob=swap_oob,
            )(
                Form(hx_post=post_chat_prompt, hx_target=f"#{CONVERSATION_CONTAINER_ID}", hx_swap="beforeend", cls="new-message-form")(
                    Input(
                        name="prompt",
                        cls="secondary",  # This makes it gray in Dark Mode
                        style="border-radius: 2rem;",
                    ),
                    Button("Submit", id="submit-btn", cls="primary", hidden=True),
                    Textarea(conversation, name="conversation", hidden=True),
                )
            ),
        )

    @app.get(CHAT_URL)
    def get_chat_page(conversation: str = "") -> FT:
        logging.info(f"Getting chat page using conversation starter: {conversation}")
        # if we got a conversation starter then show it in a response-box div
        if conversation:
            conversation_elements = [Div(cls="ai-response")(Div()(conversation))]
        else:
            conversation_elements = []
        return Main(cls="container chat-shell")(
            Article(id=CONVERSATION_CONTAINER_ID, cls="conversation-pane")(*conversation_elements),
            get_message_form(conversation=conversation),
        )

    @app.post(CHAT_PROMPT_URL)
    def post_chat_prompt(prompt: str, conversation: str = "") -> FT:
        # Pass the prompt and conversation in and return a div that will be filled with the response stream
        logging.info(f"post_chat_prompt: {prompt} with conversation: {conversation}")
        # Add the prompt to the conversation
        conversation += f"\nUser: {prompt}"
        response_box_id, response_content_id, sse_div_id = _make_response_ids()
        stream_url = f"{CHAT_RESPONSE_STREAM_URL}?{urlencode({'prompt': prompt, 'conversation': conversation, 'sse_div_id': sse_div_id})}"
        # Return the original prompt - now read only - and two divs - one for the sse and one for the response
        return Div()(
            Div(cls="message-row")(
                Div(prompt, cls="user-message"),
                Div(id=response_box_id, cls="ai-response")(
                    Div(id=sse_div_id, hx_ext="sse", sse_connect=stream_url, sse_swap="message", hx_swap="beforeend", hx_target=f"#{response_content_id}")(),
                    Div(id=response_content_id, cls=CHAT_RESPONSE_CONTENT_CLASS)(),
                ),
            ),
            get_message_form(conversation=conversation, swap_oob="true"),
        )

    @app.get(CHAT_RESPONSE_STREAM_URL)
    async def get_chat_response_stream(prompt: str, conversation: str, sse_div_id: str = SSE_DIV_ID) -> StreamingResponse:
        logging.info(f"get_chat_response_stream: Getting chat response stream for prompt: {prompt} and conversation: {conversation}")

        return StreamingResponse(
            get_sse_chat_generator(
                process_chat_function=process_chat,
                get_message_form_function=get_message_form,
                prompt=prompt,
                conversation=conversation,
                sse_div_id=sse_div_id,
            ),
            media_type="text/event-stream",
        )


async def get_sse_chat_generator(
    process_chat_function: Callable[[str, str], AsyncIterable[Failure | str | None]],
    get_message_form_function: Callable[[str], FT],
    prompt: str,
    conversation: str,
    sse_div_id: str,
) -> AsyncIterable[str]:
    aggregated_response = ""
    async for msg in process_chat_function(prompt, conversation):
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

    # update the input form with the latest conversation
    yield format_for_sse(get_message_form_function(conversation))

    # replace the sse container with an emtpy one to close down the SSE connection
    yield format_for_sse(Div(id=sse_div_id, hx_swap_oob="true")())
