# Fiction Fabricator - Gemini Context

## Project Overview

Fiction Fabricator is a sophisticated Python-based framework designed for generating long-form fictional content, including novels, short stories, and episodic web novels, using advanced AI language models. It aims to provide a flexible and powerful toolset for writers and creators, enabling them to bring their ideas to life through AI.

The project leverages a variety of LLM providers (Google Generative AI, Mistral AI, Groq, OpenAI, Azure AI, and local Ollama models) through a unified interface, managed by the Langchain ecosystem. It employs a multi-stage generation pipeline that includes:

*   **Premise Generation:** Creating story ideas based on user input.
*   **Prompt Generation:** Developing detailed prompts to guide the AI.
*   **Lorebook Management:** Creating and utilizing lorebooks to maintain consistency and depth in generated content.
*   **Story Writing:** Generating short stories, complete novels, and individual web novel chapters.
*   **Evaluation:** Comparing and evaluating different AI-generated stories.

The architecture is modular, with distinct tools for each major function, and utilizes various utility classes within the `src/Writer` directory for managing narrative elements, LLM interactions, and output formatting.

## Building and Running

The project is a Python application. To run it, you will need to install the dependencies listed in `requirements.txt`.

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application:**
    The main entry point is `main.py`. You can run it from the project's root directory:
    ```bash
    python main.py
    ```
    This will launch an interactive command-line interface (CLI) where you can choose to generate premises, prompts, stories, manage lorebooks, or evaluate content.

3.  **Configuration:**
    The project uses environment variables for configuration, likely including API keys for LLM providers. It appears to load these from a `.env` file (as indicated by `dotenv.load_dotenv()` in `main.py`). Ensure you have a `.env` file set up with the necessary credentials.

4.  **Testing:**
    There are no explicit testing commands mentioned in the files I've reviewed. However, the presence of `Evaluate.py` suggests a capability for comparing generated outputs. It's recommended to explore the `.github/documentation` for any specific testing guidelines or to implement unit tests for the various modules.

## Development Conventions

*   **Modularity:** The codebase is well-organized into `src/Tools` and `src/Writer` directories, with subdirectories for specific components like `Chapter`, `Interface`, `Outline`, and `Scene`. This promotes modularity and maintainability.
*   **LLM Abstraction:** The project abstracts LLM interactions through classes like `Writer.Interface.Wrapper.Interface` and `Writer.LLMUtils.py`, allowing for easier integration of different AI models.
*   **Logging and Output:** The `src/Writer/PrintUtils.py` module (used via `Logger` in `main.py`) suggests a standardized way of handling output and logging.
*   **Documentation:** The project includes comprehensive documentation in the `.github/documentation` directory, covering introduction, installation, configuration, usage, advanced tools, and maintenance. This is a strong indicator of good development practices.
*   **Environment Variables:** Uses `python-dotenv` to manage environment variables, which is a standard practice for handling sensitive information like API keys.

## Key Files and Directories

*   `main.py`: The main entry point for the CLI application.
*   `requirements.txt`: Lists all Python dependencies.
*   `src/Tools/`: Contains modules for specific generation tasks (Premise, Prompt, Short Story, Novel, Web Novel, Lorebook, Evaluation).
*   `src/Writer/`: Contains core classes for writing, editing, and managing narrative elements, including LLM utilities and interface wrappers.
*   `.github/documentation/`: Contains detailed user and developer documentation.
*   `config.ini`: Potentially used for configuration, though `main.py` focuses on environment variables.
*   `.env` (assumed): For storing environment variables and API keys.

This file provides a foundational understanding of the Fiction Fabricator project. For more in-depth information, please refer to the documentation within the `.github/documentation` directory.
