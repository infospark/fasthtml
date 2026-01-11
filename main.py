from fasthtml.common import *
import asyncio

app, rt = fast_app(exts='sse') # Enable SSE extension

async def long_process():
    for i in range(1, 4):
        await asyncio.sleep(2) # Simulate work
        # We yield a "message" that HTMX will swap into the UI
        yield sse_message(P(f"Completed step {i} of 3..."), event="progress")
    yield sse_message(P("✅ Onboarding Complete!", cls="text-success"), event="progress")

@rt("/")
def get():
    return Titled("Onboard Company",
        Div(hx_ext="sse", sse_connect="/run-task")( # Connect to the stream
            Div(sse_swap="progress")("Waiting to start...") # This gets swapped
        )
    )

@rt("/run-task")
async def get():
    return EventStream(long_process())

serve()