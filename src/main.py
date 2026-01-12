import asyncio
import logging
from collections.abc import AsyncIterator
from urllib.parse import urlencode

from fasthtml.common import (
    FT,
    H2,
    H4,
    A,
    Button,
    Card,
    Div,
    EventStream,
    Form,
    Html,
    Input,
    Main,
    P,
    Script,
    Title,
    fast_app,
    serve,
)

from utils import format_for_sse

# 1. Setup with SSE headers
sse_hdrs = Html(Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"))
app, rt = fast_app(hdrs=[sse_hdrs])

# --- UI COMPONENTS ---


def CompanyInput() -> FT:
    # Using 'name="companies"' for all inputs creates a list in the backend
    return Input(
        name="companies", placeholder="Company Name", style="margin-bottom: 10px;"
    )


def StatusStep(text: str, is_done: bool = False) -> FT:
    icon = "✅" if is_done else "⏳"
    return Div(P(f"{icon} {text}"), cls="status-item")


def get_event_stream(names: str) -> EventStream:
    company_list = names.split(",")

    async def msg_generator() -> AsyncIterator[str]:
        for name in company_list:
            for i in range(1, 5):
                logging.info(f"[{name}] Step {i} complete")
                yield format_for_sse(StatusStep(f"[{name}] Step {i} complete"))
                await asyncio.sleep(0.5)

        # This tells the JS on the browser: "Stop listening and close the socket."
        logging.info(f"Finished {name}")
        yield format_for_sse(
            # We replace the entire container by ID
            Div(id="onboarding-container", hx_swap_oob="true")(
                H4("🚀 All company tasks completed!"),
                P("The connection is now closed."),
            )
        )

    return EventStream(msg_generator())


# --- ROUTES ---


@rt("/")
def get_root() -> FT:
    return Main(cls="container")(
        Title("Bulk Onboarding"),
        H2("Onboard Companies"),
        Div(id="onboarding-container")(
            Form(hx_post=start_bulk_task, hx_target="#onboarding-container")(
                Div(id="input-list")(CompanyInput(), CompanyInput()),
                # Clickable text to add more inputs
                A(
                    "+ Add More",
                    hx_get=get_add_input,
                    hx_target="#input-list",
                    hx_swap="beforeend",
                    style="cursor: pointer; display: block; margin-bottom: 20px;",
                ),
                Button("Submit All", id="submit-btn", cls="primary"),
            )
        ),
    )


@rt("/stream-bulk")
async def get_stream(names: str) -> EventStream:
    return get_event_stream(names)


@rt("/add-input")
def get_add_input() -> FT:
    # Just returns one more input field to be appended
    return CompanyInput()


@rt("/start-bulk-task")
def start_bulk_task(companies: list[str]) -> FT:
    # Filter out empty strings if the user left any blank
    valid_companies = [c for c in companies if c.strip()]

    # Pass the list to the stream via a query parameter or session
    # For simplicity here, we'll pass names as a comma-separated string in the URL
    names_param = ",".join(valid_companies)
    stream_url = f"/stream-bulk?{urlencode({'names': names_param})}"
    return Div(hx_ext="sse", sse_connect=stream_url)(
        Card(Div(sse_swap="message")("Preparing bulk onboarding..."))
    )


serve()
