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
    Div,
    EventStream,
    FastHTML,
    Form,
    Input,
    Main,
    P,
    Title,
)

from styles import BUTTON_PRIMARY_CLASSES, COMPANY_INPUT_CLASSES, CONTENT_WRAPPER_CLASSES, ONBOARDING_CONTAINER_CLASSES, PAGE_CONTAINER_CLASSES
from utils import format_for_sse


def CompanyInput() -> FT:
    # Using 'name="companies"' for all inputs creates a list in the backend
    return Input(name="companies", placeholder="Company Name", cls=COMPANY_INPUT_CLASSES)


def StatusStep(text: str, is_done: bool = False) -> FT:
    icon = "✅" if is_done else "⏳"
    return Div(P(f"{icon} {text}"), cls="py-2 text-gray-200")


def get_onboarding_event_stream(names: str) -> EventStream:
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
            Div(id="onboarding-container", hx_swap_oob="true", cls=ONBOARDING_CONTAINER_CLASSES)(
                H4("🚀 All company tasks completed!", cls="text-2xl font-bold mb-4 text-green-400"),
                P("The connection is now closed.", cls="text-gray-300"),
            )
        )

    return EventStream(msg_generator())


# --- ROUTES ---


ONBOARDING_URL = "/onboarding"
ONBOARDING_ADD_COMPANY_URL = "/onboarding/add-company"
ONBOARDING_START_TASKS_URL = "/onboarding/start-tasks"
ONBOARDING_STREAM_TASKS_STATUS_URL = "/onboarding/stream-tasks-status"


def setup_onboarding_routes(app: FastHTML) -> None:
    def get_onboarding_container() -> FT:
        return (
            Title("Bulk Onboarding"),
            H2("Onboard Companies", cls="text-3xl font-bold mb-6 text-white"),
            Div(id="onboarding-container", cls=ONBOARDING_CONTAINER_CLASSES)(
                Form(hx_post=onboarding_start_tasks, hx_target="#onboarding-container", cls="space-y-4")(
                    Div(id="input-list", cls="space-y-2")(CompanyInput(), CompanyInput()),
                    # Clickable text to add more inputs
                    A(
                        "+ Add More",
                        hx_get=onboarding_add_input,
                        hx_target="#input-list",
                        hx_swap="beforeend",
                        cls="text-blue-400 hover:text-blue-300 cursor-pointer block mb-5",
                    ),
                    Button("Submit All", id="submit-btn", cls=f"w-full {BUTTON_PRIMARY_CLASSES}"),
                )
            ),
        )

    @app.get(ONBOARDING_URL)
    def get_onboarding_page() -> FT:
        return Main(cls=PAGE_CONTAINER_CLASSES)(
            Div(cls=CONTENT_WRAPPER_CLASSES)(get_onboarding_container())
        )

    @app.get(ONBOARDING_STREAM_TASKS_STATUS_URL)
    async def onboarding_stream_tasks_status(names: str) -> EventStream:
        return get_onboarding_event_stream(names)

    @app.get(ONBOARDING_ADD_COMPANY_URL)
    def onboarding_add_input() -> FT:
        # Just returns one more input field to be appended
        return CompanyInput()

    @app.post(ONBOARDING_START_TASKS_URL)
    def onboarding_start_tasks(companies: list[str]) -> FT:
        # Filter out empty strings if the user left any blank
        valid_companies = [c for c in companies if c.strip()]

        # Pass the list to the stream via a query parameter or session
        # For simplicity here, we'll pass names as a comma-separated string in the URL
        names_param = ",".join(valid_companies)
        stream_url = f"{ONBOARDING_STREAM_TASKS_STATUS_URL}?{urlencode({'names': names_param})}"
        return Div(hx_ext="sse", sse_connect=stream_url, cls=ONBOARDING_CONTAINER_CLASSES)(Div(sse_swap="message", cls="space-y-2")("Preparing bulk onboarding..."))
