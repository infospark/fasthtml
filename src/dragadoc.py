

from fasthtml.common import FT, Button, Div, FastHTML, Input, Main, P

DROPADOC_URL = "/dropadoc"


def get_dropadoc_container() -> FT:
    # Define the styling for the drop zone
    # 'flex-1' and 'min-h-[60vh]' ensure it occupies significant vertical space
    drop_zone_style = (
        "border: 3px dashed #ccc; "
        "border-radius: 20px; "
        "display: flex; "
        "flex-direction: column; "
        "align-items: center; "
        "justify-content: center; "
        "padding: 40px; "
        "margin: 20px; "
        "min-height: 60vh; " # Fills 60% of the viewport height
        "cursor: pointer; "
        "transition: border-color 0.3s;"
    )

    return Main(cls="container")(
        Div(id="drop_box", style=drop_zone_style)(

            P("Drag & Drop your documents here", cls="text-muted"),
            P("or", cls="text-xs"),

            Input(type="file", name="file", id="file-input", multiple=True, hidden=True,
                  style="margin-bottom: 20px;"),

            Button("Select Files", id="upload-btn", cls="primary"),

        )
    )

def setup_dragadrop_routes(app: FastHTML) -> None:
    @app.get(DROPADOC_URL)
    def get_dropadoc_page() -> FT:
        return Main(cls="container")(get_dropadoc_container())
