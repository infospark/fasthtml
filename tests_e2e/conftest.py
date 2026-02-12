import threading
import time
from collections.abc import Generator

import pytest
import uvicorn
from fasthtml.common import FastHTML

from app import start_app
from graph_manager import GraphManager


class ThreadedUvicorn(threading.Thread):
    def __init__(self, app: FastHTML, host: str = "127.0.0.1", port: int = 5001) -> None:
        super().__init__(daemon=True)
        self.server = uvicorn.Server(
            uvicorn.Config(
                app,
                host=host,
                port=port,
                log_level="warning",
                ws="none",
            )
        )

    def run(self) -> None:
        self.server.run()

    def stop(self) -> None:
        self.server.should_exit = True


@pytest.fixture(scope="session")
def server() -> Generator[None, None, None]:
    app = start_app()

    server_thread = ThreadedUvicorn(app, port=5001)
    server_thread.start()

    timeout = 5
    start_time = time.time()
    while not server_thread.server.started:
        if time.time() - start_time > timeout:
            server_thread.stop()
            raise RuntimeError("Server failed to start on port 5001")
        time.sleep(0.1)

    yield

    server_thread.stop()
    server_thread.join(timeout=2)


@pytest.fixture()
def graph_server() -> Generator[tuple[GraphManager, int], None, None]:
    port = 5010
    graph_manager = GraphManager()
    app = start_app(graph_manager=graph_manager)

    server_thread = ThreadedUvicorn(app, port=port)
    server_thread.start()

    timeout = 5
    start_time = time.time()
    while not server_thread.server.started:
        if time.time() - start_time > timeout:
            server_thread.stop()
            raise RuntimeError(f"Server failed to start on port {port}")
        time.sleep(0.1)

    yield graph_manager, port

    server_thread.stop()
    server_thread.join(timeout=2)
