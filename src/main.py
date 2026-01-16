import logging

from fasthtml.common import serve

from app import process_chat, start_app

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create the app instance at the module level
# This allows Uvicorn to find the 'app' object
app = start_app(process_chat)

if __name__ == "__main__":
    # Only block and serve if we are running this file directly
    serve()
