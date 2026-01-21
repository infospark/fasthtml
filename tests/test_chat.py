import time

import pytest

from chat import parrot_chat, split_string_into_words


@pytest.mark.asyncio
async def test_parrot_chat() -> None:
    prompt = "Assert prompt."
    received_chunks = []
    timestamps = []

    # Iterate through the stream
    async for chunk in parrot_chat(prompt):
        timestamps.append(time.perf_counter())
        received_chunks.append(chunk)

    # Check that the response parrots the prompt in one word chunks
    assert any("Assert " in chunk for chunk in received_chunks)
    assert any("prompt." in chunk for chunk in received_chunks)


def test_split_string_into_words() -> None:
    assert split_string_into_words("Assert prompt.") == ["Assert ", "prompt."]
