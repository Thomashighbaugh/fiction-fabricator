# Fiction Fabricator

An AI-powered narrative generation system that transforms story concepts into full-length novels and short stories using large language models. Fiction Fabricator employs multi-phase content synthesis, intelligent context management, and interactive editing tools to create fiction manuscripts.

## Key Features

- **Multi-Phase Generation**: Automated outline creation, content drafting, and iterative refinement
- **Interactive Editing**: Chapter management, story element customization, and AI-powered rewrites
- **Lorebook System**: Auto-generated world-building entries with Tavern AI compatibility
- **Export Options**: EPUB, HTML, Markdown, PDF, and TXT formats
- **Project Management**: XML-based state persistence with resume capabilities

Inspired by [pulpgen](https://github.com/pulpgen-dev/pulpgen). Built with enhanced modular architecture and XML-based state management.

---

## Quick Start

```bash
# 1. Install dependencies (requires Python 3.13+ and uv)
cd fiction-fabricator
uv sync

# 2. Configure API key in .env file
echo "GEMINI_API_KEY=YOUR_KEY_HERE" > .env

# 3. Run with interactive menu
uv run python main.py

# Or with a prompt file
uv run python main.py --prompt your_idea.txt

# Resume existing project
uv run python main.py --resume projects/your-project-folder
```

Get your API key: https://aistudio.google.com/app/apikey

For detailed setup instructions, see [INSTALLATION.md](.github/documentation/INSTALLATION.md).

---

## Documentation

| Documentation | Description |
|---------------|-------------|
| [Overview](.github/documentation/OVERVIEW.md) | Project overview, capabilities, and use cases |
| [Installation](.github/documentation/INSTALLATION.md) | Setup guide, requirements, and troubleshooting |
| [Usage Guide](.github/documentation/USAGE.md) | Complete walkthrough of features and workflows |
| [New Features](.github/documentation/NEW_FEATURES.md) | Recent additions and enhancements |
| [Architecture](.github/documentation/ARCHITECTURE.md) | Technical design and XML-based state management |
| [AI Agent Architecture](.github/documentation/AI_AGENT_ARCHITECTURE.md) | Multi-phase agentic design philosophy |
| [Lorebook System](.github/documentation/LOREBOOK.md) | World-building and context management |
| [Export Options](.github/documentation/EXPORT_OPTIONS.md) | Output formats and publishing workflows |
| [Configuration](.github/documentation/CONFIGURATION.md) | API management and system optimization |
| [Prompt Enhancement](.github/documentation/PROMPT_ENHANCEMENT.md) | AI-assisted prompt expansion |
| [Development Guide](.github/documentation/DEVELOPMENT.md) | Code style and contribution guidelines |
| [**Changelog**](.github/CHANGELOG.md) | **Project history and version changes** |

### Examples

| File | Description |
|------|-------------|
| [Comprehensive Prompt](.github/examples/example_comprehensive_prompt.txt) | Detailed story prompt example |
| [Prompt Template](.github/examples/template_comprehensive_prompt.txt) | Template for creating prompts |
| [Lorebook Example](.github/examples/example_lorebook.json) | Sample Tavern AI lorebook |

## License

MIT License. See [LICENSE](LICENSE) for details.
