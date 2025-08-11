# Fiction Fabricator - Agents Guide

## Build/Test Commands
- **Run application**: `python main.py`
- **Install dependencies**: `pip install -r requirements.txt`
- **No formal test framework** - manual testing via application usage

## Code Structure & Entry Points
- Main entry: `main.py` - CLI interface for all functionality
- Core modules: `src/Tools/` (generators), `src/Writer/` (writing pipeline)
- Configuration: `config.ini` (model selection, settings)
- LLM Providers: `src/Writer/Interface/` (OpenRouter, Wrapper)

## Python Code Style
- **Imports**: Standard library first, then third-party, then local imports
- **Functions**: snake_case naming, descriptive docstrings
- **Classes**: PascalCase, clear type hints where used
- **Variables**: snake_case, descriptive names
- **Constants**: UPPER_SNAKE_CASE in Config.py

## Error Handling
- Use try/except with specific exceptions
- Graceful fallbacks with default values
- Termcolor for colored console output
- Extensive logging via custom Logger class

## Key Conventions
- Config values accessed via `get_config_or_default()` helper
- LLM models specified with provider prefixes (e.g., "google://", "mistralai://")
- File paths use `os.path.join()` for cross-platform compatibility
- Environment variables loaded via python-dotenv
- Lorebook management via the main menu for creating, editing, and generating lorebooks.