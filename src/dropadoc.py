

import shutil
from pathlib import Path

from fasthtml.common import FT, Button, Div, FastHTML, Form, Input, Main, P, Script, UploadFile

DROPADOC_URL = "/dropadoc"
DROPADOC_UPLOAD_URL = "/dropadoc/upload"
INBOX_DIR = Path(__file__).resolve().parent.parent / "inbox"


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
            Form(
                id="dropadoc-form",
                hx_post=DROPADOC_UPLOAD_URL,
                hx_target="#upload-status",
                hx_trigger="change",
                hx_encoding="multipart/form-data",
                enctype="multipart/form-data",
            )(
                P("Drag & Drop your documents here", cls="text-muted"),
                P("or", cls="text-xs"),
                Input(
                    type="file",
                    name="file",
                    id="file-input",
                    multiple=True,
                    hidden=True,
                    style="margin-bottom: 20px;",
                ),
                Button("Select Files", id="upload-btn", cls="primary", type="button"),
            ),
            Div(id="upload-status"),
            Script(
                """
                const dropBox = document.getElementById("drop_box");
                const fileInput = document.getElementById("file-input");
                const uploadBtn = document.getElementById("upload-btn");

                uploadBtn.addEventListener("click", () => fileInput.click());
                dropBox.addEventListener("dragover", (event) => {
                  event.preventDefault();
                });
                dropBox.addEventListener("drop", (event) => {
                  event.preventDefault();
                  if (!event.dataTransfer || !event.dataTransfer.files.length) return;
                  fileInput.files = event.dataTransfer.files;
                  fileInput.dispatchEvent(new Event("change", { bubbles: true }));
                });
                """
            ),
        )
    )

def setup_dragadrop_routes(app: FastHTML) -> None:
    @app.get(DROPADOC_URL)
    def get_dropadoc_page() -> FT:
        return Main(cls="container")(get_dropadoc_container())

    @app.post(DROPADOC_UPLOAD_URL)
    def dropadoc_upload(file: list[UploadFile]) -> FT:
        INBOX_DIR.mkdir(parents=True, exist_ok=True)
        saved_names: list[str] = []
        for upload in file:
            if not upload.filename:
                continue
            safe_name = Path(upload.filename).name
            dest = INBOX_DIR / safe_name
            with dest.open("wb") as out:
                shutil.copyfileobj(upload.file, out)
            saved_names.append(safe_name)
        if not saved_names:
            return P("No files selected")
        if len(saved_names) == 1:
            return P(f"Successfully uploaded {saved_names[0]}")
        return P(f"Successfully uploaded {len(saved_names)} files")
