import logging
import os
import socket
import subprocess
import time
from collections.abc import Generator

import pytest


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


@pytest.fixture(scope="session", autouse=True)
def server() -> Generator[None, None, None]:
    # 1. Start the FastHTML server in the background
    # Set PYTHONPATH to include src directory so imports work
    env = os.environ.copy()
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_path = os.path.join(project_root, "src")
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")

    proc = subprocess.Popen(
        ["python", "src/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Combine stderr with stdout
        text=True,
        cwd=project_root,
        env=env,
    )
    logging.info("Starting server...")
    # 2. Wait for the server to actually be ready
    timeout = 5
    start_time = time.time()
    while not is_port_open(5001):
        if time.time() - start_time > timeout:
            proc.terminate()
            raise RuntimeError("Server failed to start on port 5001")
        time.sleep(0.1)
    logging.info("Server started successfully on port 5001")
    yield  # This is where the tests run

    # 3. Shutdown after all tests are finished
    proc.terminate()
