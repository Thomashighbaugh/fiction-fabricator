# Fiction Fabricator - Agents Guide

## Build/Lint/Test Commands
- **Run application:** `python main.py`
- **Install dependencies:** `pip install -r requirements.txt`
- **Test LLM7 integration:** `python test_llm7.py`
- **Linting:** No formal linter configured; follow style guidelines below.
- **Testing:** No automated test framework. To test, run the application and verify output manually.
- **Single test:** Isolate functionality in main.py or relevant module, run `python main.py` and check results.

## Code Style Guidelines
- **Imports:** Standard library first, then third-party, then local imports.
- **Formatting:** 4 spaces per indent, max 120 chars/line, no trailing whitespace.
- **Naming:**
  - Functions/variables: snake_case
  - Classes: PascalCase
  - Constants: UPPER_SNAKE_CASE (see Config.py)
- **Types:** Use type hints where possible, especially for public APIs.
- **Functions:** Descriptive docstrings required.
- **Error Handling:** Use try/except with specific exceptions; fallback to defaults gracefully.
- **Logging:** Use the custom Logger class for all logs; prefer termcolor for console output.

## Agentic Conventions
- Access config via `get_config_or_default()`.
- Use `os.path.join()` for file paths.
- Environment variables loaded via python-dotenv.
- LLM models use provider prefixes (e.g., `google://`, `mistralai://`, `llm7://`).
- LLM7 models: Use `llm7://model-name` format (e.g., `llm7://gpt-4.1-nano-2025-04-14`).
- Lorebook management via main menu.

---
For questions, consult documentation/ or ask a maintainer.
