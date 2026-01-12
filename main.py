from fasthtml.common import *
import asyncio

# 1. Setup with SSE headers
sse_hdrs = Html(Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"))
app, rt = fast_app(hdrs=[sse_hdrs])

# --- UI COMPONENTS ---

def CompanyInput():
    # Using 'name="companies"' for all inputs creates a list in the backend
    return Input(name="companies", placeholder="Company Name", style="margin-bottom: 10px;")

def StatusStep(text, is_done=False):
    icon = "✅" if is_done else "⏳"
    return Div(P(f"{icon} {text}"), cls="status-item")

def format_for_sse(elt, event="message"):
    content = to_xml(elt).replace('\n', '')
    return f"event: {event}\ndata: {content}\n\n"

# --- ROUTES ---

@rt("/")
async def get():
    return Titled("Bulk Onboarding",
        Main(cls="container")(
            H2("Onboard Companies"),
            Div(id="onboarding-container")(
                Form(hx_post=start_bulk_task, hx_target="#onboarding-container")(
                    Div(id="input-list")(
                        CompanyInput(),
                        CompanyInput()
                    ),
                    # Clickable text to add more inputs
                    A("+ Add More", 
                      hx_get=get_add_input, 
                      hx_target="#input-list", 
                      hx_swap="beforeend",
                      style="cursor: pointer; display: block; margin-bottom: 20px;"),
                    
                    Button("Submit All", cls="primary")
                )
            )
        )
    )

@rt("/stream-bulk")
async def get_stream(names: str):
    company_list = names.split(",")
    
    async def msg_generator():
        for name in company_list:
            yield format_for_sse(StatusStep(f"Starting {name}..."))
            await asyncio.sleep(1)
            
            for i in range(1, 3):
                await asyncio.sleep(0.5)
                yield format_for_sse(StatusStep(f"[{name}] Step {i} complete"))
            
            yield format_for_sse(StatusStep(f"Finished {name}", is_done=True))
            await asyncio.sleep(0.5)
            
        yield format_for_sse(H4("🚀 All company tasks completed!"))
    
    return StreamingResponse(msg_generator(), media_type="text/event-stream")


@rt("/add-input")
def get_add_input():
    # Just returns one more input field to be appended
    return CompanyInput()

@rt("/start-bulk-task")
async def start_bulk_task(companies: list[str]):
    # Filter out empty strings if the user left any blank
    valid_companies = [c for c in companies if c.strip()]
    
    # Pass the list to the stream via a query parameter or session
    # For simplicity here, we'll pass names as a comma-separated string in the URL
    names_param = ",".join(valid_companies)
    stream_url = uri(get_stream, names=names_param)
    return Div(hx_ext="sse", sse_connect=stream_url)(
        Card(
            Div(sse_swap="message")("Preparing bulk onboarding...")
        )
    )

serve()