
# .github/documentation/developer_guide.md
# Fiction Fabricator - Developer Guide

This guide provides information for developers who want to contribute to or modify the Fiction Fabricator application.

## 1. Project Structure

The project has the following directory structure:

```
gui-fab-fict/
├── .github/
│   └── documentation/        <- Project documentation (architecture, usage, developer guide)
├── core/
│   ├── book_spec.py          <- Data model for Book Specification
│   ├── plot_outline.py       <- Data models for Plot, Chapter, and Scene Outlines
│   ├── content_generator/    <- Content generation logic
│   │   ├── __init__.py
│   │   ├── base_generator.py       <- Abstract base class for content generators
│   │   ├── book_spec_generator.py
│   │   ├── plot_outline_generator.py
│   │   ├── chapter_outline_generator.py
│   │   ├── scene_outline_generator.py
│   │   └── scene_part_generator.py
│   ├── project_manager.py    <- Project saving and loading
├── llm/
│   ├── __init__.py
│   ├── llm_client.py         <- Client for interacting with Ollama
│   ├── prompt_manager/       <- Prompt management
│   │   ├── __init__.py
│   │   ├── base_prompts.py         <- Common prompt templates
│   │   ├── book_spec_prompts.py
│   │   ├── plot_outline_prompts.py
│   │   ├── chapter_outline_prompts.py
│   │   ├── scene_outline_prompts.py
│   │   └── scene_part_prompts.py
├── streamlit_app/
│   ├── __init__.py
│   ├── app.py                <- Main Streamlit application logic
│   ├── components/           <- Reusable Streamlit components
│   │   ├── __init__.py
│   │   ├── book_spec_view.py   <- Display, edit, and enhance BookSpec
│   │   ├── plot_outline_view.py  <- Display, edit, and enhance Plot Outline.
│   │   └── chapter_outline_view.py <- Display, edit, and enhance Chapter Outline.
├── utils/
│   ├── __init__.py
│   ├── config.py             <- Configuration management
│   ├── file_handler.py       <- File operations (save/load JSON)
│   ├── logger.py             <- Logging setup
│   ├── async_utils.py      <- Asynchronous operation utilities
│   └── data_validation.py   <- Custom data validation
├── run                     <- Script to run the Streamlit app
└── requirements.txt        <- Project dependencies
```

See the `architecture.md` file for a detailed explanation of each module.

## 2. Setting up a Development Environment

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd gui-fab-fict
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Ollama:** Follow the instructions on the [Ollama website](https://ollama.ai/) to install and run Ollama locally.  Pull at least one model (e.g., `mistral`).

5.  **Run the application:**
    ```bash
    ./run
    ```
    This will start the Streamlit application.

## 3. Code Style and Conventions

*   **PEP 8:** Follow the PEP 8 style guide for Python code.
*   **Type Hints:** Use type hints throughout the code.
*   **Docstrings:**  Write clear and comprehensive docstrings for all modules, classes, and functions. Use the Google style docstrings.
*   **Logging:** Use the `utils.logger` module for logging.
*   **Error Handling:** Implement robust error handling using `try...except` blocks and appropriate logging.
*   **Asynchronous Programming:** Use `async` and `await` for interacting with the Ollama API and other potentially long-running operations.

## 4. Key Modules and Classes

### 4.1. `core`

*   **`BookSpec`, `PlotOutline`, `ChapterOutline`, `SceneOutline` (Pydantic Models):**  These models define the structure of the data used throughout the application.  Familiarize yourself with these models to understand how the data is represented.
*   **`BaseContentGenerator`:** Understand the abstract base class and how it provides common functionality to the specific content generators.  When adding new content generation capabilities, inherit from `BaseContentGenerator`.
*   **Specific Content Generators (`BookSpecGenerator`, `PlotOutlineGenerator`, etc.):**  These classes implement the content generation logic for each specific type of content. They interact with the `PromptManager` and `OllamaClient`.

### 4.2. `llm`

*   **`OllamaClient`:**  This class handles the communication with the Ollama API.  All interactions with Ollama should go through this client.
*   **`prompt_manager`:** Understand how prompts are organized and managed using templates.  When modifying or adding prompts, follow the established pattern of using `base_prompts.py` for common elements and separate modules for each content type's specific prompts.

### 4.3. `streamlit_app`

*   **`app.py`:** This is the main entry point for the Streamlit application. It handles UI layout, user input, session state, and calls to the backend components.
*   **`components/`:** This directory contains reusable Streamlit components.  When adding new UI elements, consider whether they should be implemented as reusable components.

### 4.4. `utils`

*   **`config.py`:** Understand how the application configuration is managed using Pydantic `BaseSettings`.
*   **`async_utils.py`:** Review the `timeout_wrapper` function and consider using it for any new asynchronous operations that require timeouts.

## 5. Contributing

1.  **Fork the repository.**
2.  **Create a new branch** for your feature or bug fix.
3.  **Make your changes**, following the code style and conventions.
4.  **Write tests** for your changes (where applicable).
5.  **Commit your changes** with clear and descriptive commit messages.
6.  **Push your branch** to your forked repository.
7.  **Create a pull request** to the main repository.

## 6. Testing
The current project does not implement testing, however, additions of testing via a library such as `pytest` are appreciated.

This guide provides a starting point for developers.  Refer to the `architecture.md` and `usage.md` documents for additional context.  By following these guidelines, you can contribute to the Fiction Fabricator project effectively and maintainably.
