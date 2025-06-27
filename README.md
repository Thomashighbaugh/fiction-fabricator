# Fiction Fabricator

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

Fiction Fabricator is an advanced, AI-powered framework for generating complete, multi-chapter novels from a single creative prompt. It leverages a suite of modern Language Learning Models (LLMs) through a unified interface, employing a sophisticated, multi-stage pipeline of outlining, scene-by-scene generation, and iterative revision to produce high-quality, coherent long-form narratives.

## Acknowledgement of Origin

This project is a significantly modified and enhanced fork of **[AIStoryteller by datacrystals](https://github.com/datacrystals/AIStoryteller)**. I would like to expressing extend my immense gratitude to the original author for providing the foundational concepts and architecture. Fiction Fabricator builds upon that excellent groundwork with new features, a refactored generation pipeline (tailored to my use case of course), and a robust, multi-provider backend to suit a different set of use cases focused on flexibility, quality, and developer control.

## What's New in Fiction Fabricator?

This fork was created to enhance the original project with a focus on provider flexibility, improved narrative coherence, and a more powerful, user-configurable generation process.

### Key Features & Modifications:

- **Unified Multi-Provider Interface**: Seamlessly switch between LLM providers like **Google Gemini, Groq, Mistral, Ollama, and NVIDIA NIM** using a simple URI format (e.g., `groq://llama3-70b-8192`).
- **Robust & Predictable NVIDIA NIM Integration**: The NVIDIA integration has been specifically hardened to provide full user control. Models are **manually and explicitly listed** in the `config.ini` file, removing the unpredictability of a dynamic discovery function and ensuring that any model you have access to can be used.
- **Flexible API Configuration**: Easily configure API endpoints, including the crucial `NVIDIA_BASE_URL`, either through a `.env` file for security or directly in `config.ini` for simplicity.
- **Advanced Scene-by-Scene Generation**: Instead of attempting to generate entire chapters at once, Fiction Fabricator breaks chapter outlines down into individual scenes. It writes each scene with context from the preceding one, dramatically improving narrative flow and short-term coherence.
- **Iterative Critique & Revision Engine**: At critical stages of generation (outline, scene breakdown, chapter writing), the system uses an LLM to critique its own output and then revise it based on that feedback. This self-correction loop significantly enhances the quality of the final product.
- **Intelligent Prompt Engineering**: Includes a powerful utility (`Tools/PromptGenerator.py`) that takes a user's simple idea and uses an LLM-driven, multi-step process to expand it into a rich, detailed prompt perfect for generating a complex story.
- **Comprehensive Logging**: Every run generates a unique, timestamped directory in `Logs/`, containing the final story, run statistics, and detailed debug files for every LLM call, providing complete transparency into the generation process.
- **Developer & Power-User Utilities**:
  - **`Tools/Test.py`**: A testing script for quickly running generations with different pre-defined model configurations.
  - **`Evaluate.py`**: A powerful A/B testing tool that uses an LLM to compare two generated stories on multiple axes, such as plot, style, and dialogue.

---

## Exhaustive Guide to Fiction Fabricator

This guide provides everything you need to know to install, configure, and use the project.

### 1. Installation

Get started by cloning the repository and setting up the required environment.

```bash
# 1. Clone the repository
git clone <your-repository-url>
cd REBASE-AIStorywriter

# 2. (Recommended) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# 3. Install the required packages
pip install -r requirements.txt
```

### 2. Configuration

Configuration is handled by two key files: `.env` for secrets and `config.ini` for settings.

#### The `.env` File

This is the **most secure** place for your API keys. Create a file named `.env` in the project's root directory.

```
# Example .env file

# Provider API Keys
GOOGLE_API_KEY="your-google-api-key"
MISTRAL_API_KEY="your-mistral-api-key"
GROQ_API_KEY="your-groq-api-key"

# For NVIDIA, the API key is required.
NVIDIA_API_KEY="nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# The NVIDIA Base URL is optional here. If set, it will OVERRIDE the value in config.ini.
# This is useful for pointing to custom, preview, or self-hosted NIM endpoints.
# NVIDIA_BASE_URL="https://your-custom-nim-url.com/v1"
```

#### The `config.ini` File

This file controls the application's behavior and model selection.

- **`[LLM_SELECTION]`**: Set the default models for each step of the generation process. You can override any of these via command-line flags.
- **`[NVIDIA_SETTINGS]`**:
  - `base_url`: The API endpoint for NVIDIA models. The default (`https://integrate.api.nvidia.com/v1`) is for standard models.
  - `available_models`: **This is a crucial, manual list.** Add the specific model IDs you have access to and wish to use, separated by commas.
    _Example_: `available_models = meta/llama3-70b-instruct, mistralai/mistral-nemotron`
- **`[WRITER_SETTINGS]`**: Fine-tune the generation process.
  - `scene_generation_pipeline`: (Default: `true`) Highly recommended. Enables the advanced scene-by-scene workflow.
  - `enable_final_edit_pass`: (Default: `false`) Performs a final, holistic edit of the entire novel. Can increase cost and time but may improve consistency.
  - `minimum_chapters`: The minimum number of chapters the final outline should have.
  - `seed`: A seed for randomization to ensure reproducible results.

### 3. Usage Workflow

Follow these steps to generate your first novel.

#### Step 1: Create a High-Quality Prompt (Recommended)

A detailed prompt produces a better story. Use the `PromptGenerator` tool to expand a simple idea.

```bash
# Run the tool with your story title and a basic idea
python Tools/PromptGenerator.py -t "The Last Signal" -i "A lone astronaut on Mars discovers a strange, repeating signal from a polar ice cap, but her mission command on Earth insists it's just a malfunction."
```

This will guide you through selecting a model for the generation and will save a detailed `prompt.txt` file in `Prompts/The_Last_Signal/prompt.txt`.

#### Step 2: Write the Novel

Use the main `Write.py` script to start the generation process.

**Interactive Mode (Easiest)**:
Simply provide the prompt file path. The script will present an interactive menu to select the primary writing model from all available providers.

```bash
python Write.py -Prompt "Prompts/The_Last_Signal/prompt.txt"
```

**Custom/Headless Mode**:
You can specify all models and settings via command-line arguments, which override `config.ini`. This is useful for automated runs.

```bash
python Write.py \
-Prompt "Prompts/The_Last_Signal/prompt.txt" \
-InitialOutlineModel "google://gemini-1.5-pro-latest" \
-ChapterS1Model "groq://llama3-70b-8192" \
-ChapterRevisionModel "nvidia://meta/llama3-70b-instruct" \
-EnableFinalEditPass \
-Seed 42
```

#### Step 3: Find Your Story

All output is saved to uniquely named directories:

- **`Stories/`**: Contains the final output. For each run, you will get:
  - `Your_Story_Title.md`: A markdown file with the formatted story and generation statistics.
  - `Your_Story_Title.json`: A structured JSON file containing the full narrative context, including all outlines, chapter text, and summaries.
- **`Logs/`**: Contains detailed logs for debugging. A new directory is created for each run, containing:
  - `Main.log`: A log of all steps taken.
  - `LangchainDebug/`: A folder with `.json` and `.md` files for every single call made to an LLM, showing the exact prompts and responses.

### 4. Advanced Usage

- **Testing Model Configurations (`Tools/Test.py`)**: Edit this file to define different sets of models for various roles. Running `python Tools/Test.py` allows you to quickly launch a generation with a specific configuration, perfect for testing provider performance.
- **Evaluating Stories (`Evaluate.py`)**: After generating two stories, use this tool to have an LLM compare them. It provides a detailed, chapter-by-chapter analysis and a final verdict on which story is better according to multiple criteria.
  ```bash
  python Evaluate.py -Story1 "Stories/Story_A.json" -Story2 "Stories/Story_B.json" -Output "Comparison_Report.md"
  ```

---

This project is designed to be a powerful, flexible, and transparent tool for creating long-form fiction with AI. We welcome feedback and hope you find it useful.
