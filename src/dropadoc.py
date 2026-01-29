

import shutil
from pathlib import Path

from fasthtml.common import FT, Button, Div, FastHTML, Form, Input, Main, P, Script, UploadFile

from styles import BUTTON_PRIMARY_CLASSES, CONTENT_WRAPPER_CLASSES, DROP_ZONE_CLASSES, PAGE_CONTAINER_CLASSES

DROPADOC_URL = "/dropadoc"
DROPADOC_UPLOAD_URL = "/dropadoc/upload"
DROPADOC_FORM_ID = "dropadoc-form"
UPLOAD_STATUS_ID = "upload-status"
INBOX_DIR = Path(__file__).resolve().parent.parent / "inbox"


def get_dropadoc_container() -> FT:
    return Main(cls=PAGE_CONTAINER_CLASSES)(
        Div(cls=CONTENT_WRAPPER_CLASSES)(
        Div(id="drop_box", cls=DROP_ZONE_CLASSES)(
            Form(
                id=DROPADOC_FORM_ID,
                hx_post=DROPADOC_UPLOAD_URL,
                hx_target=f"#{UPLOAD_STATUS_ID}",
                hx_trigger="change",
                hx_encoding="multipart/form-data",
                enctype="multipart/form-data",
                cls="flex flex-col items-center",
            )(
                P("Drag & Drop your documents here", cls="text-gray-400 text-xl mb-2"),
                P("or", cls="text-gray-500 text-sm mb-4"),
                Input(
                    type="file",
                    name="file",
                    id="file-input",
                    multiple=True,
                    hidden=True,
                ),
                Button("Select Files", id="upload-btn", cls=f"{BUTTON_PRIMARY_CLASSES} px-8", type="button"),
            ),
            Div(id=UPLOAD_STATUS_ID, cls="mt-6 text-center"),
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
    )

def setup_dropadoc_routes(app: FastHTML) -> None:
    @app.get(DROPADOC_URL)
    def get_dropadoc_page() -> FT:
        return get_dropadoc_container()

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
            return P("No files selected", cls="text-red-400")
        if len(saved_names) == 1:
            return P(f"✅ Successfully uploaded {saved_names[0]}", cls="text-green-400 font-semibold")
        return P(f"✅ Successfully uploaded {len(saved_names)} files", cls="text-green-400 font-semibold")
