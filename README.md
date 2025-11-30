# Fiction Fabricator

## Next-Generation Agentic AI Novel Generation Platform

**Fiction Fabricator** is an advanced, autonomous AI-powered narrative generation system that leverages cutting-edge large language models to produce publication-quality fiction manuscripts. Our sophisticated agentic architecture employs multi-phase content synthesis, intelligent context management, and adaptive refinement algorithms to transform simple concepts into professionally crafted full-length novels and short stories.

Built on a foundation of **agentic AI workflows**, Fiction Fabricator delivers exceptional narrative coherence, character consistency, and thematic depth through its revolutionary multi-agent orchestration system. The platform's **state-of-the-art content generation pipeline** produces manuscripts that rival human-authored works in quality, creativity, and literary sophistication.

### Revolutionary Features:
- **Autonomous Multi-Phase Generation**: Sophisticated AI agents handle outlining, drafting, and refinement with minimal human intervention
- **Adaptive Context Intelligence**: Advanced lorebook system maintains perfect narrative consistency across complex multi-chapter works  
- **Publication-Ready Output**: Generates professionally formatted manuscripts in EPUB, HTML, and Markdown formats
- **Interactive Human-AI Collaboration**: Seamless integration of human creativity with AI capability for optimal results

Heavily inspired by [pulpgen](https://github.com/pulpgen-dev/pulpgen) and other agentic text generation platforms, Fiction Fabricator advances the field with enhanced modular architecture, expanded API provider support, and innovative XML-based state management for superior content persistence and modification workflows.

---

##  Quick Start

1.  **Install:** Requires Python 3.13+ and `uv`.
    ```bash
    # Clone or download the code first
    cd fiction-fabricator
    uv sync
    ```
2.  **API Key:** Create a `.env` file in the `fiction fabricator` directory with `GEMINI_API_KEY=YOUR_KEY_HERE`
    API Key can be created in Google AI Studio: https://aistudio.google.com/app/apikey

3.  **Run (New Project):**

    ```bash
    # Example using a prompt file:
    uv run python main.py --prompt your_idea.txt
:qw
    # Or run without --prompt to enter your idea interactively:
    uv run python main.py
    ```

4.  **Run (Resume Project):**
    ```bash
    uv run python main.py --resume path/to/your/project_folder
    ```
5.  **Output:** Finds/creates a project folder (like `YYYYMMDD-slug-uuid`) containing XML state files and exported manuscripts.

---

## Core Features

Fiction Fabricator combines cutting-edge AI technology with intuitive user interfaces to deliver a comprehensive narrative generation platform:

### 🚀 **Autonomous Story Generation**
- **Multi-Phase Pipeline**: Intelligent agents handle outline creation, content drafting, and iterative refinement
- **Adaptive Context Management**: Advanced lorebook system ensures perfect narrative consistency across complex works
- **Interactive Editing Suite**: AI-powered tools for chapter expansion, rewriting, and quality enhancement
- **Publication-Ready Exports**: Professional formatting in EPUB, HTML, and Markdown formats

### 🧠 **Advanced AI Features**
- **Prompt Enhancement Engine**: Transform basic ideas into rich, detailed story foundations
- **Context-Aware Generation**: Sophisticated keyword matching and content injection systems
- **Human-AI Collaboration**: Seamless integration of creative input with AI capability
- **Quality Assurance**: Built-in consistency checking and narrative optimization

### 📚 **Professional Workflow Tools**
- **Project State Management**: Advanced XML-based persistence with resume capabilities
- **Lorebook Integration**: Tavern AI compatible world-building and character management
- **Interactive UI**: Rich console interface with comprehensive editing menus
- **Flexible Export Options**: Multiple output formats for different publishing needs

For detailed usage instructions, see the [Complete Usage Guide](.github/documentation/USAGE.md).

## License

MIT License. See the [LICENSE](LICENSE) file for the legalese.

## Feature Overview & Documentation

Fiction Fabricator provides a comprehensive suite of advanced narrative generation capabilities:

### 🎯 **Core Generation Features**
- **[Autonomous Story Generation](.github/documentation/GENERATORS.md)** - Multi-phase content creation pipeline with intelligent outline generation, adaptive content drafting, and iterative refinement
- **[Interactive Editing Suite](.github/documentation/USAGE.md#interactive-editing-features)** - AI-powered chapter expansion, targeted rewrites, fresh perspective generation, and comprehensive manuscript analysis
- **[Export System](.github/documentation/EXPORT_OPTIONS.md)** - Professional formatting in EPUB, HTML, Markdown, PDF, TXT, and chapter-based outputs for publishing workflows

### 🧠 **Advanced AI Capabilities**
- **[Prompt Enhancement Engine](.github/documentation/PROMPT_ENHANCEMENT.md)** - Transform basic concepts into rich, detailed story foundations with AI-assisted expansion and optimization
  - [Prompt Template Guide](.github/documentation/PROMPT_TEMPLATE_GUIDE.md)
  - [Comprehensive Prompt Example](.github/examples/example_comprehensive_prompt.txt)
  - [Enhanced Prompt Sample](.github/examples/enhanced_prompt_20250923_144247.txt)
- **[Lorebook System](.github/documentation/LOREBOOK.md)** - Advanced world-building and context management with automatic injection, consistency enforcement, and Tavern AI compatibility
  - [Lorebook Quick Guide](.github/documentation/LOREBOOK_QUICK.md)
  - [Example Lorebook](.github/examples/example_lorebook.json)
- **[Context Intelligence](.github/documentation/USAGE.md#content-pipeline)** - Sophisticated keyword matching, relevance scoring, and dynamic content integration for narrative coherence

### 🔧 **Professional Workflow Tools**
- **[Project Management](.github/documentation/PROJECT_MANAGEMENT.md)** - XML-based state persistence, resume functionality, and project organization with automatic versioning
- **[User Interface](.github/documentation/USER_INTERFACE.md)** - Rich console interface with interactive menus, real-time feedback, and comprehensive editing controls
- **[Configuration System](.github/documentation/CONFIGURATION.md)** - Flexible API management, system optimization, and workflow customization

### 📖 **Getting Started Resources**
- **[Complete Usage Guide](.github/documentation/USAGE.md)** - Comprehensive walkthrough of all features and workflows
- **[Quick Start Tutorial](.github/documentation/GETTING_STARTED.md)** - Installation, setup, and first project creation
- **[Architecture Overview](.github/documentation/ARCHITECTURE.md)** - Technical architecture and system design principles

### 🔬 **Technical Documentation**
- **[AI Agent Architecture](.github/documentation/AI_AGENT_ARCHITECTURE.md)** - Multi-phase agentic design philosophy and implementation details that enable exceptional long-form fiction generation
- **[Orchestrator System](.github/documentation/ORCHESTRATOR.md)** - Multi-phase workflow management and agent coordination
- **[Development Guide](.github/documentation/DEVELOPMENT.md)** - Code style, contribution guidelines, and extension development
- **[API Integration](.github/documentation/CONFIGURATION.md#llm-client)** - Language model integration and provider management
