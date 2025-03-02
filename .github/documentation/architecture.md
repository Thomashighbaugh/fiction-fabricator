# Fiction Fabricator - Software Architecture

This document outlines the software architecture of the Fiction Fabricator application.

## 1. Overview

Fiction Fabricator is a Streamlit-based web application that assists users in generating long-form fictional content using a local Ollama language model. The application guides users through a structured workflow:

1.  **Story Idea Input:** The user provides a brief story idea.
2.  **Book Specification Generation:** The application generates a detailed book specification (title, genre, setting, themes, tone, point of view, characters, premise) based on the story idea.
3.  **Plot Outline Generation:** A three-act plot outline is generated from the book specification.
4.  **Chapter Outline Generation:** The plot outline is broken down into individual chapter outlines.
5.  **Scene Outline Generation:** Each chapter outline is further divided into scene outlines.
6.  **Scene Part Generation:** The application generates the actual text content for each scene, part by part.
7.  **Enhancement:** At each stage (Book Spec, Plot Outline, Chapter Outlines, Scene Outlines, Scene Parts), the user can request the LLM to enhance the generated content based on a critique/rewrite cycle.
8. **Saving and Loading:** Users can save and load their projects, preserving the entire state of the generation process.

## 2. Modular Structure

The application is structured into several key modules:

```
fiction_fabricator/
├── .github/
│   └── documentation/        <- This file and other documentation
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
│   │   ├── plot_outline_view.py <- Display, edit, and enhance PlotOutline
│   │   └── chapter_outline_view.py <- Display, edit, and enhance ChapterOutlines
├── utils/
│   ├── __init__.py
│   ├── config.py             <- Configuration management
│   ├── file_handler.py       <- File operations (save/load JSON)
│   ├── logger.py             <- Logging setup
│   ├── async_utils.py       <- Utilities for async operations (e.g., timeouts)
│   └── data_validation.py      <- Custom data validation functions
├── run                     <- Script to run the Streamlit app
└── requirements.txt        <- Project dependencies

```

### 2.1. `core`

*   **`book_spec.py`:** Defines the `BookSpec` Pydantic model, representing the structure of a book specification.
*   **`plot_outline.py`:** Defines Pydantic models for `PlotOutline`, `ChapterOutline`, and `SceneOutline`.
*   **`content_generator/`:** Contains classes for generating different content types.
    *   **`base_generator.py`:**  An abstract base class (`BaseContentGenerator`) that provides common functionality (prompt formatting, LLM interaction, structure checking) to all specific content generators.
    *   **`book_spec_generator.py`:**  `BookSpecGenerator` class, inherits from `BaseContentGenerator`, handles generation and enhancement of `BookSpec` objects.
    *   **`plot_outline_generator.py`:** `PlotOutlineGenerator` class, handles generation and enhancement of `PlotOutline` objects.
    *   **`chapter_outline_generator.py`:** `ChapterOutlineGenerator` class, handles generation and enhancement of `ChapterOutline` objects.
    *   **`scene_outline_generator.py`:** `SceneOutlineGenerator` class, handles generation and enhancement of `SceneOutline` objects.
    *   **`scene_part_generator.py`:** `ScenePartGenerator` class, handles generation and enhancement of scene part text.
*   **`project_manager.py`:**  The `ProjectManager` class handles saving and loading the entire project state (including all generated content) to/from JSON files.

### 2.2. `llm`

*   **`llm_client.py`:** The `OllamaClient` class provides an interface for interacting with the local Ollama instance. It handles sending requests and receiving responses.  Timeouts are *not* used at the Ollama API level, as per project requirements.
*   **`prompt_manager/`:** This package manages the prompts used for interacting with the LLM.
    *   **`base_prompts.py`:** Contains common prompt templates and utility functions (e.g., instructions for the novelist role, structure checking instructions, JSON output formatting).  This promotes DRY (Don't Repeat Yourself) principles in prompt management.
    *   **`book_spec_prompts.py`:** Contains prompt templates specific to `BookSpec` generation, enhancement, critique, rewrite, and structure checks.  These templates utilize the common templates from `base_prompts.py`.
    *   **`plot_outline_prompts.py`:** Prompt templates for `PlotOutline`.
    *   **`chapter_outline_prompts.py`:** Prompt templates for `ChapterOutline`.
    *   **`scene_outline_prompts.py`:** Prompt templates for `SceneOutline`.
    *   **`scene_part_prompts.py`:** Prompt templates for `ScenePart`.

### 2.3. `streamlit_app`

*   **`app.py`:** The main Streamlit application script.  This file orchestrates the entire user interface, workflow, and interactions with the backend components.  It initializes the necessary classes (generators, client, project manager), manages session state, and handles user input and output.
*   **`components/`:** Contains reusable Streamlit components.
    *   **`book_spec_view.py`:** A component for displaying, editing, generating, and enhancing `BookSpec` objects.
    *   **`plot_outline_view.py`:**  A component for displaying, editing, generating, and enhancing `PlotOutline` objects.
    *  **`chapter_outline_view.py`:** A component for displaying, editing, and enhancing `ChapterOutline` objects.

### 2.4. `utils`

*   **`config.py`:** Manages application configuration using Pydantic `BaseSettings`.  Loads settings from environment variables and a `.env` file.
*   **`file_handler.py`:** Provides utility functions for saving and loading JSON files (used by `ProjectManager`).
*   **`logger.py`:** Sets up and configures the application logger.
*   **`async_utils.py`:** Provides utility functions for asynchronous operations, including a `timeout_wrapper` to apply timeouts to *any* async function.
*   **`data_validation.py`:**  Houses custom data validation functions beyond what Pydantic provides.

## 3. Data Flow

1.  **User Input:** The user interacts with the Streamlit UI in `app.py`, providing input such as a story idea, selecting options, and clicking buttons.
2.  **Session State:**  `app.py` uses Streamlit's `st.session_state` to store the application's state, including user input, generated content, and selected options.
3.  **Content Generation:**
    *   When the user triggers a generation action (e.g., clicking "Generate Book Specification"), `app.py` calls the appropriate method on the relevant `ContentGenerator` instance (e.g., `BookSpecGenerator.generate()`).
    *   The `ContentGenerator` retrieves the corresponding prompt template from the appropriate `prompt_manager` module (e.g., `BookSpecPrompts`).
    *   The prompt template is formatted with the necessary variables (e.g., story idea, current book spec data).
    *   The formatted prompt is sent to the `OllamaClient`.
    *   The `OllamaClient` sends the request to the local Ollama instance.
    *   The LLM response is received by the `OllamaClient` and returned to the `ContentGenerator`.
    *   The `ContentGenerator` parses the response (e.g., from JSON to a Pydantic model).
    *   Structure checks and fixes are performed using dedicated prompts.
    *   The generated content is stored in `st.session_state`.
4.  **Enhancement:** The enhancement process follows a similar flow, using critique and rewrite prompts. The `ContentGenerator`'s `enhance` method orchestrates this.
5.  **Display:**  `app.py` (and potentially reusable components in `streamlit_app/components/`) retrieves the generated content from `st.session_state` and displays it to the user.
6.  **Project Management:** The `ProjectManager` handles saving and loading the entire `st.session_state` to/from a JSON file, allowing users to persist their work.

## 4. Key Technologies

*   **Streamlit:**  Web application framework.
*   **Ollama:**  Local language model.
*   **aiohttp:** Asynchronous HTTP client for interacting with Ollama.
*   **Pydantic:** Data validation and settings management.
*   **python-dotenv:**  Loading environment variables.

## 5. Error Handling
Error handling is implemented throughout the application with these methods:
*  **Try-Except Blocks**: These are used within file I/O operations, JSON parsing and in calls made to the Ollama API. 
* **Logging**: A logger instance from utils.logger is used to log errors, warnings, and informational messages.
* **Specific Exception Handling**: Code anticipates specific exceptions such as `FileNotFoundError`, `json.JSONDecodeError`, `aiohttp.ClientError`, and `pydantic.ValidationError`.
* **Re-raising Exceptions**: In `file_handler.py` and `project_manager.py`, exceptions are re-raised after logging to allow calling functions to handle them further.
* **`None` Returns**: Content generation functions return `None` to indicate failure, which triggers error messages in the Streamlit application.

## 6. Asynchronous Operations

The application uses `asyncio` and `aiohttp` for asynchronous operations, primarily for interacting with the Ollama API. This allows the application to remain responsive even during potentially long-running LLM calls. The `utils/async_utils.py` module includes additional functionality such as a `timeout_wrapper` to add timeouts to async functions.
