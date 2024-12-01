--- START OF FILE goat_storytelling_agent/README.md ---
# Fiction Fabricator -- GOAT Storytelling Agent Enhanced Edition

This project generates long-form fiction (short stories, novels) from a user-provided topic. It uses large language models (LLMs) and a structured, iterative writing process.

## Key Improvements

* **Simplified User Interaction:** A text-based menu guides users.
* **Streamlined LLM Interaction:** Fewer LLM calls for efficiency.
* **GLHF API:** Access to powerful LLMs.
* **Clearer Codebase:** Improved readability and maintainability.
* **Enhanced Error Handling:**  Robust handling and feedback.
* **Automatic Scene Generation and Enhancement:** Automated workflow for writing and expanding scenes.
* **Title Generation:**  LLM generates a title based on the topic.
* **Output Caching:** Saves LLM responses to markdown files.
* **Model Selection:** User can choose from a list of LLMs.


## Features

* **Book Specification:** Creates and refines story details.
* **Plot Outline:** Develops a three-act plot with chapters.
* **Scene Breakdown:** Divides chapters into scenes with specifications.
* **Scene Writing:** Generates scene text (dark, cynical, erotic).
* **Scene Continuation:** Expands existing scenes.


## Getting Started

1. **Prerequisites:**
    - Python 3.9+
    - GLHF authentication token (`GLHF_AUTH_TOKEN` environment variable)

2. **Installation:**
    ```bash
    cd goat-storytelling-agent-enhanced
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3. **Usage:**
    ```bash
    python menu.py
    ```

    Follow the prompts to provide a topic and navigate the menu.

## Configuration

`config.py`:

* `MODEL_NAME`: LLM name on GLHF (keep `hf:` prefix for Hugging Face models).
* `TIMEOUT`: Timeout for LLM calls (seconds).
* `RETRY_WAIT`: Wait time before retrying (seconds).

## Contributing

Contributions are welcome! Open an issue or submit a pull request.

## License

MIT License. Original GOAT Storytelling Agent by Thomas Leon Highbaugh. This enhanced edition is maintained by Thomas Leon Highbaugh.

## Acknowledgements

- Thanks to GLHF.
