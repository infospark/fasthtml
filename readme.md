# FastHTML Experimental App

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

Note: We use Google genai which relies on TikTokens which needs Rust to build. If the pip install fails with ERROR: Failed building wheel for tiktoken then run"
```curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
pip install --upgrade setuptools wheel```

2. **Install Playwright browsers (required for testing):**
   ```bash
   playwright install --with-deps chromium
   ```

## Testing

**Run static analysis (MyPy):**
```bash
mypy .
```

**Run linting (Ruff):**
```bash
ruff check .
```

**Environment variables:**
Note: This project relies on Gemini via the genai package
Please set up a .env file in the root of this project with an API Key:
GEMINI_API_KEY = "<<YOUR_API_KEY>>"

**Run all tests with coverage:**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest --cov=src
```

**Run tests in headless mode (for CI):**
```bash
HEADLESS=True pytest --cov=src
```
