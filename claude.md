# Claude Development Guidelines

## Core Principles

### Functional Programming & Pure Functions
- Prefer pure functions: same input always produces same output, no side effects
- Separate pure logic from side effects (I/O, state mutations, etc.)
- Make dependencies explicit through function parameters
- Keep functions small and focused on a single responsibility

### Railway-Oriented Programming
- Functions should only return their declared type - **do not throw exceptions**
- Use `Failure | T` return types instead of raising exceptions
- Example: a function that gets something from Gemini should return `Failure | str`
- Support "Railway style" with multiple return statements (PLR0911 ignored in ruff)

### Test-Driven Development (TDD)
- Write tests first (Functional TDD approach)
- Tests should drive the design of pure functions
- Aim for high test coverage, especially for business logic
- Tests should be clear, readable, and serve as documentation

## Project Structure
- `/tests` contains pytest files
- `/src` contains source code
- Modules are organized by feature

## Code Style

### Type Hints
- **MyPy strict mode enabled** - all functions must have type hints
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
- Test files in `tests/` directory
- Test path: `tests/`
- Source path: `src/`
- Run with: `PYTHONPATH=$PYTHONPATH:$(pwd)/src pytest --cov=src`
- Coverage excludes: `src/main.py`

### End-to-end Testing
- Uses Playwright with Chromium
- Install: `playwright install --with-deps chromium`
- Supports headless mode: `HEADLESS=True pytest`

### Static Analysis
- **MyPy**: Run with `mypy .`
- **Ruff**: Run with `ruff check .`

## Architecture & Patterns

### Error Handling
- **No exceptions** in pure functions
- Use union types: `Failure | SuccessType`
- Railway-oriented programming pattern

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
