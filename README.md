
# Fiction Fabricator -- GOAT Storytelling Agent Edition 
# GOAT Storytelling Agent: Enhanced Edition

This project is an enhanced version of the original GOAT Storytelling Agent, designed to generate long-form fiction (short stories, novels, etc.) from a simple user-provided topic or idea.  It leverages the power of large language models (LLMs) and a structured, iterative writing process.

## Key Improvements

This enhanced edition features several improvements over the original:

* **Simplified User Interaction:**  A text-based user interface (TUI) menu guides users through the story creation process, making it more intuitive and user-friendly.
* **Streamlined LLM Interaction:**  Optimized to reduce the number of LLM calls, mitigating rate limiting issues and improving efficiency.
* **Uses GLHF API:**  Utilizes the GLHF API for access to powerful LLMs, enabling more sophisticated story generation capabilities.
* **Clearer Codebase:**  Refactored for improved readability and maintainability, with descriptive variable names and comprehensive comments.
* **Enhanced Error Handling:**  More robust error handling to gracefully handle unexpected situations and provide helpful feedback to the user.

## Features

* **Book Specification Generation:**  Creates and refines a detailed specification for your story, covering genre, setting, characters, plot, and more.
* **Plot Outline Creation:**  Develops a three-act plot outline with chapters, ensuring a compelling narrative arc.
* **Scene Breakdown:**  Breaks down chapters into individual scenes, each with detailed specifications for characters, setting, events, and emotional tone.
* **Scene Writing:**  Generates scene text, incorporating dark, cynical, and erotic elements as per the specified tone.
* **Scene Continuation:**  Allows for continuing existing scenes, maintaining narrative consistency.
* **Full Story Generation:**  Generates a complete story based on the defined specifications and plot.
* **Story Saving:** Option to save the generated story to a file.


## Getting Started

1. **Prerequisites:**
    - Python 3.9 or higher
    - An active GLHF authentication token (set as the `GLHF_AUTH_TOKEN` environment variable)

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

    Follow the on-screen prompts to provide a story topic and navigate through the menu options.


## Configuration

The `config.py` file allows you to configure the LLM used:

* `MODEL_NAME`: Specifies the name of the LLM on GLHF. Make sure to keep the `hf:` prefix for Hugging Face models.


## Contributing

Contributions are welcome!  Please open an issue or submit a pull request.



## License

This project is licensed under the [MIT License](LICENSE).  The original GOAT Storytelling Agent was created by [Original Author Name/GitHub username].  This enhanced edition is maintained by [Your Name/GitHub Username].



## Acknowledgements

- Thanks to the original creator of the GOAT Storytelling Agent for providing the foundation for this project.
- Thanks to GLHF for providing access to powerful LLMs.
