import time

import pytest

from chat import gemini_chat, parrot_chat, split_string_into_words
from utils import Failure


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
