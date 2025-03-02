# .github/documentation/prompt_engineering.md
# Fiction Fabricator - Prompt Engineering Guide

This document details the prompt engineering strategies used in the Fiction Fabricator application. Understanding these strategies is crucial for modifying existing prompts or adding new ones.

## 1. General Principles

*   **Role-Playing:** Prompts consistently use role-playing, instructing the LLM to act as a "world-class novelist," "meticulous editor," or "skilled writer." This helps guide the LLM's output style and expertise.
*   **Clear Instructions:** Prompts provide very specific and detailed instructions on the task, desired output format, and any constraints.
*   **Templating:**  Prompt templates are used extensively (via `llm/prompt_manager/base_prompts.py` and the individual prompt modules) to reduce redundancy and improve maintainability. Common elements like role definitions, output format instructions, and critique/rewrite frameworks are defined as reusable templates.
*   **JSON Output:**  For structured data (BookSpec), the LLM is explicitly instructed to return its response in valid JSON format. This ensures consistent parsing.
*   **Structure Check and Fix:** A two-step process is used to ensure the structural integrity of generated content:
    1.  **Structure Check:** A separate prompt asks the LLM to check if the generated content adheres to the required structure. It responds with "STRUCTURE_OK" if valid, or with a description of the problems otherwise.
    2.  **Structure Fix:** If the structure check fails, another prompt is used to instruct the LLM to fix the identified structural issues.
*   **Critique and Rewrite Cycle:** For enhancement, a critique/rewrite cycle is employed:
    1.  **Critique:** A prompt asks the LLM to provide a concise, actionable critique of the current content.
    2.  **Rewrite:**  A separate prompt instructs the LLM to rewrite the content based on the generated critique.
* **Context Provision**: Prompts include comprehensive information when generating scene parts such as full `BookSpec`, `ChapterOutline`, and `SceneOutline`.

## 2. Prompt Structure

Most prompts follow a general structure:

1.  **Role Definition:**  Assign the LLM a role (e.g., "You are a world-class novelist...").
2.  **Task Description:** Clearly state the task the LLM should perform (e.g., "Generate a detailed book specification...").
3.  **Input Data:** Provide any input data required for the task (e.g., the story idea, the current BookSpec). This is often formatted within the prompt using ```` ``` blocks.
4.  **Specific Instructions:** Give detailed instructions on what to include in the output, how to format it, and any constraints.
5.  **Output Format:**  Specify the desired output format (e.g., plain text, JSON).
6.  **Constraints:** Specify what the LLM is not allowed to generate, for example, "Do not include any explanation or introductory text, just the valid JSON."

## 3. Key Prompt Templates (`base_prompts.py`)

*   **`COMMON_INSTRUCTIONS_NOVELIST`:** Defines the LLM's role as a novelist.
*   **`STRUCTURE_CHECK_INSTRUCTIONS`:**  Defines the LLM's role as an editor checking structure.
*   **`STRUCTURE_FIX_PROMPT_TEMPLATE`:**  Provides a template for prompts that fix structural issues.
*   **`JSON_OUTPUT_FORMAT_INSTRUCTIONS`:**  Enforces JSON output and provides a placeholder for the JSON schema.
*   **`CRITIQUE_PROMPT_TEMPLATE`:**  Provides a framework for generating critiques.
*   **`REWRITE_PROMPT_TEMPLATE`:**  Provides a framework for rewriting content based on a critique.

## 4. Specific Prompt Modules

Each content type (BookSpec, PlotOutline, ChapterOutline, SceneOutline, ScenePart) has its own prompt module within `llm/prompt_manager/`.  These modules define the specific prompts for generating, enhancing, checking, and fixing that content type. They utilize the base templates from `base_prompts.py`.

For example, `llm/prompt_manager/book_spec_prompts.py` contains:

*   `create_book_spec_generation_prompt()`
*   `create_book_spec_structure_check_prompt()`
*   `create_book_spec_structure_fix_prompt()`
*   `create_book_spec_critique_prompt()`
*   `create_book_spec_rewrite_prompt()`

## 5. Modifying Prompts

When modifying prompts:

1.  **Understand the Existing Prompt:** Carefully analyze the existing prompt's structure, instructions, and use of templates.
2.  **Make Incremental Changes:**  Modify the prompt in small increments and test the changes thoroughly.
3.  **Use the Streamlit UI:** The Fiction Fabricator application provides a convenient way to test prompt modifications.  Make changes to the prompt files, then use the application to generate content and observe the results.
4.  **Consider the Base Templates:** If your changes involve common elements, consider updating the base templates in `base_prompts.py`.
5.  **Maintain Consistency:**  Ensure that your changes are consistent with the overall prompt engineering principles used in the application.

## 6. Adding New Prompts

When adding new prompts:

1.  **Determine the Purpose:**  Clearly define the purpose of the new prompt (e.g., generate a new content type, perform a new type of enhancement).
2.  **Choose the Appropriate Module:**  Decide which prompt module the new prompt belongs to (or create a new module if necessary).
3.  **Utilize Base Templates:**  Leverage the existing base templates in `base_prompts.py` as much as possible.
4.  **Follow the Established Structure:**  Adhere to the general prompt structure outlined above.
5.  **Test Thoroughly:** Test the new prompt extensively using the Streamlit application.

By following these guidelines, you can effectively modify and extend the prompt engineering aspects of the Fiction Fabricator application.