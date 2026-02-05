import logging

from dotenv import load_dotenv
from fasthtml.common import serve

from app import start_app
from chat_routes import gemini_chat

# load the env values into process env for local runs/debugging.
load_dotenv()

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create the app instance at the module level using live Gemini chat
app = start_app(gemini_chat)

if __name__ == "__main__":
    # Only call serve (which is a blocking call) if we are running this file directly
    serve()
