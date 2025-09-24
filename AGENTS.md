# AGENTS.md - Development Guide for Fiction Fabricator

## Build & Run Commands
- **Install dependencies**: `uv sync`
- **Run application**: `uv run python main.py`
- **Run with prompt file**: `uv run python main.py --prompt idea.txt`
- **Resume project**: `uv run python main.py --resume project-folder`
- **Use lorebook**: `uv run python main.py --lorebook world.json --prompt idea.txt`
- **Create/edit lorebook**: `uv run python main.py --create-lorebook world.json`
- **Create enhanced prompt**: `uv run python main.py --create-prompt`
- **No test framework configured** - check src/ for manual testing

## Code Style & Conventions
- **Python**: Use UTF-8 encoding header `# -*- coding: utf-8 -*-`
- **Imports**: Standard library first, third-party, then local (src.module)
- **Type hints**: Use modern syntax (`str | None`, not `Optional[str]`)
- **Error handling**: Catch specific exceptions, use rich console for user messages
- **Classes**: PascalCase, methods snake_case, constants UPPER_CASE
- **Docstrings**: Use triple quotes with brief description
- **Rich UI**: Use rich.console for all user output, panels for status messages

## Project Structure
- `src/` - Main package with config, LLM client, orchestrator, project management
- `main.py` - Entry point with argparse CLI
- Dependencies: google-generativeai, rich, lxml, ebooklib, python-dotenv
- Requires Python 3.13+ and GEMINI_API_KEY in .env file

## Lorebook Features
- **Lorebook Support**: Load Tavern AI format JSON lorebooks for world-building context
- **Interactive Manager**: Create/edit lorebooks with `--create-lorebook` flag
- **LLM Integration**: AI-assisted entry creation, expansion, and condensing
- **Auto-Context**: Keyword-based automatic context injection during story generation
- **Documentation**: See `LOREBOOK.md` for comprehensive usage guide

## Prompt Enhancement Features
- **Enhanced Prompt Creation**: Transform basic ideas into comprehensive prompts with `--create-prompt`
- **Interactive Workflow**: Choose story type (novel/short story), target length, and genre preferences
- **LLM-Powered Expansion**: AI transforms simple concepts into detailed story prompts with rich world-building
- **Lorebook Integration**: Automatically incorporates relevant lorebook context when available
- **Multiple Output Options**: Save to file, copy to clipboard, or immediately start story generation