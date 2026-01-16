
from fasthtml.common import (
    Html,
    Script,
    fast_app,
    serve,
)

from onboarding import setup_onboarding_routes

# 1. Setup with SSE headers
sse_hdrs = Html(Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"))
app, rt = fast_app(hdrs=[sse_hdrs])

setup_onboarding_routes(app)

serve()
