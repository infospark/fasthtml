import time
from collections.abc import AsyncIterable

import pytest
from bs4 import BeautifulSoup
from fasthtml.common import FT, Div

from chat_routes import SSE_DIV_ID, gemini_chat, get_sse_chat_generator, parrot_chat, split_string_into_words
from data_types import Failure


@pytest.mark.asyncio
async def test_parrot_chat() -> None:
    prompt = "Assert prompt."
    received_chunks = []
    timestamps = []

    # Iterate through the stream
    async for chunk in parrot_chat(prompt):
        timestamps.append(time.perf_counter())
        received_chunks.append(chunk)

    list_of_chunks = list(received_chunks)
    # Check that the response parrots the prompt in one word chunks
    assert any("Assert " in chunk for chunk in list_of_chunks if isinstance(chunk, str))
    assert any("prompt." in chunk for chunk in list_of_chunks if isinstance(chunk, str))


def test_split_string_into_words() -> None:
    assert split_string_into_words("Assert prompt.") == ["Assert ", "prompt."]


@pytest.mark.asyncio
async def test_gemini_chat() -> None:
    prompt = "What is the capital of France?"
    received_chunks = []

    # Iterate through the stream
    async for chunk in gemini_chat(prompt):
        received_chunks.append(chunk)

    list_of_chunks = list(received_chunks)
    # Check that all received chunks are strings
    assert all(isinstance(chunk, str) for chunk in list_of_chunks)
    # Check that paris appears somewhere in the response (slightly verbose due to mypy)
    assert "paris" in " ".join([c for c in list_of_chunks if isinstance(c, str)]).lower()


@pytest.mark.asyncio
async def test_gemini_chat_with_prompt_plus_conversation() -> None:
    prompt = "Oh ok - what is the capital city?"
    conversation = "User: which country has the best Bratwurst?\nAI: Germany"
    received_chunks = []

    async for chunk in gemini_chat(prompt, conversation):
        received_chunks.append(chunk)

    assert any("berlin" in chunk.lower() for chunk in received_chunks if isinstance(chunk, str))


@pytest.mark.asyncio
async def test_gemini_chat_with_invalid_api_key_env_var() -> None:
    prompt = "What is the capital of France?"
    received_chunks = []
    timestamps = []

    # Iterate through the stream
    async for chunk in gemini_chat(prompt, api_key_env_var="WIBBLE"):
        timestamps.append(time.perf_counter())
        received_chunks.append(chunk)

    list_of_chunks = list(received_chunks)
    # Check that the response is a failure
    assert all(isinstance(chunk, Failure) for chunk in list_of_chunks)


@pytest.mark.asyncio
async def test_get_sse_chat_generator() -> None:
    async def process_chat(prompt: str, conversation: str) -> AsyncIterable[Failure | str | None]:
        yield "Hello world"

    def get_message_form(conversation: str) -> FT:
        return Div("Hello world")

    all_messages = []
    async for msg in get_sse_chat_generator(process_chat_function=process_chat, get_message_form_function=get_message_form, prompt="Hello world", conversation="Conversation begins here"):
        all_messages.append(msg)
    assert len(all_messages) > 0
    # Ensure the the first message contains the text "Hello world"
    first_message = all_messages[0]
    assert "Hello world" in first_message

    # Ensure the last message contains a div with the ID SSE_DIV_ID - this is swapping out the SSE connection with an empty div
    last_message = all_messages[-1]
    soup = BeautifulSoup(last_message, "html.parser")
    sse_div = soup.select_one(f"div#{SSE_DIV_ID}")
    assert sse_div is not None


@pytest.mark.asyncio
async def test_get_sse_chat_generator_failure_from_process_chat() -> None:
    async def process_chat(prompt: str, conversation: str) -> AsyncIterable[Failure | str | None]:
        yield Failure(message="Test failure")

    def get_message_form(conversation: str) -> FT:
        return Div("Hello world")

    all_messages = []
    async for msg in get_sse_chat_generator(process_chat_function=process_chat, get_message_form_function=get_message_form, prompt="Hello world", conversation="Conversation begins here"):
        all_messages.append(msg)
    # we should still get the last message
    assert len(all_messages) > 0
    # the last message should contain a div with the ID SSE_DIV_ID
    last_message = all_messages[-1]
    soup = BeautifulSoup(last_message, "html.parser")
    sse_div = soup.select_one(f"div#{SSE_DIV_ID}")
    assert sse_div is not None
