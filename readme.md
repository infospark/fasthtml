# FastHTML Experimental App

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

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

**Run all tests with coverage:**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest --cov=src
```

**Run tests in headless mode (for CI):**
```bash
HEADLESS=True pytest --cov=src
```
