import time

import pytest

from main import process_chat


@pytest.mark.asyncio
async def test_process_chat() -> None:
    prompt = "Test prompt"
    received_chunks = []
    timestamps = []

    # Iterate through the stream
    async for chunk in process_chat(prompt):
        timestamps.append(time.perf_counter())
        received_chunks.append(chunk)

    # Assertions
    assert any("hello" in chunk for chunk in received_chunks)
    assert any("world" in chunk for chunk in received_chunks)
