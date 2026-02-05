import threading
import time
from collections.abc import Generator

import pytest
import uvicorn
from fasthtml.common import FastHTML

from app import start_app  # Import your factory and logic
from chat_routes import parrot_chat


class ThreadedUvicorn(threading.Thread):
    def __init__(self, app: FastHTML, host: str = "127.0.0.1", port: int = 5001) -> None:
        super().__init__(daemon=True)
        self.server = uvicorn.Server(
            uvicorn.Config(
                app,
                host=host,
                port=port,
                log_level="warning",  # Reduce noise
                ws="none",  # <--- ADD THIS: Disables the websocket protocol
            )
        )

    def run(self) -> None:
        self.server.run()

    def stop(self) -> None:
        self.server.should_exit = True


@pytest.fixture(scope="session")
def server() -> Generator[None, None, None]:
    # 1. Initialize the app instance using your factory
    # This is where dependency injection happens for your tests!
    app = start_app(parrot_chat)

    # 2. Start Uvicorn in a background thread
    server_thread = ThreadedUvicorn(app, port=5001)
    server_thread.start()

    # 3. Wait for the server to be ready
    timeout = 5
    start_time = time.time()
    while not server_thread.server.started:
        if time.time() - start_time > timeout:
            server_thread.stop()
            raise RuntimeError("Server failed to start on port 5001")
        time.sleep(0.1)

    yield  # Tests run here

    # 4. Clean shutdown
    server_thread.stop()
    server_thread.join(timeout=2)
