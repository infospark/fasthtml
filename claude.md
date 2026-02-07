# Claude Development Guidelines

## Core Principles

### Functional TDD (Test-Driven Development)
- **All code must be written to pass a test first**
- No code should be added without a corresponding test
- Tests drive the design of functions
- Tests should be clear, readable, and serve as documentation
- Write the test, watch it fail, write the minimal code to pass, refactor

### No Exceptions - Railway-Oriented Programming
- **Functions must never throw exceptions**
- Functions should only return their declared type
- Pure functions: use `Failure | T` return types
- Side-effect functions: use `Failure | Success` return types
- Example: `def fetch_from_api(url: str) -> Failure | str`
- Example: `def save_to_db(data: Data) -> Failure | Success`
- Support "Railway style" with multiple return statements (PLR0911 ignored in ruff)

### Functional Programming & Pure Functions
- Prefer pure functions: same input always produces same output, no side effects
- Separate pure logic from side effects (I/O, state mutations, etc.)
- Make dependencies explicit through function parameters
- Keep functions small and focused on a single responsibility

## Project Structure
- `/tests` contains pytest files
- `/src` contains source code
- Modules are organized by feature

## Code Style

### Type Hints
- **MyPy strict mode enabled** - all functions must have type hints
- Every function must respect its declared signature
- Return types must be honored (no exceptions bypassing the type system)
- `disallow_untyped_decorators = false` (for FastHTML routes)
- `implicit_reexport = true`
- `warn_unused_ignores = true`

### Documentation
- **No docstrings** - code should be self-documenting

### Line Length & Formatting
- **Line length: 200 characters** (ruff.toml)
- Target Python 3.12

### Linting (Ruff)
**Enabled rules:**
- F: Pyflakes
- E/W: pycodestyle errors/warnings
- I: isort (imports)
- B: flake8-bugbear (common bugs)
- C4: flake8-comprehensions
- UP: pyupgrade (modern syntax)
- C90: McCabe complexity (max 10)
- PL: Pylint
- N: pep8-naming (classes are CapWords, functions are snake_case)

**Ignored rules:**
- E501: Line length (use 200 instead)
- PLR0911: Too many return statements (Railway style)
- PLR0913: Too many arguments (global ignore)
- N802: Allow upper case function names (FastHTML component style)

## Testing

### Framework: pytest
- **Tests come first** - write the test before the implementation
- Test files in `tests/` directory
- Test path: `tests/`
- Source path: `src/`
- Run with: `PYTHONPATH=$PYTHONPATH:$(pwd)/src pytest --cov=src`
- Coverage excludes: `src/main.py`
- No code without a test

### End-to-end Testing
- Uses Playwright with Chromium
- Install: `playwright install --with-deps chromium`
- Supports headless mode: `HEADLESS=True pytest`

### Static Analysis
- **MyPy**: Run with `mypy .`
- **Ruff**: Run with `ruff check .`

### Development Workflow
After making changes, run checks efficiently:
1. `mypy .` - type checking
2. `ruff check .` - linting
3. `PYTHONPATH=$PYTHONPATH:$(pwd)/src pytest tests/test_<impacted>.py` - run only impacted test file(s)

Only run `./build.sh` (full test suite) before committing.

## Architecture & Patterns

### Error Handling
- **No exceptions anywhere** - never use `raise`
- Pure functions return: `Failure | T` where T is the success type
- Side-effect functions return: `Failure | Success`
- Railway-oriented programming: chain operations, short-circuit on Failure
- Use pattern matching or isinstance checks to handle results

### FastHTML Specific
- Allow uppercase function names for component-style functions (N802 ignored)
- Route decorators don't require type hints (disallow_untyped_decorators = false)

### Configuration
- Use `.env` file for secrets (e.g., `GEMINI_API_KEY`)
- Load with `python-dotenv`

## Dependencies
- FastHTML for web framework
- Google genai (requires Rust for tiktoken)
- Playwright for E2E testing
- pytest with coverage
- mypy for type checking
- ruff for linting
