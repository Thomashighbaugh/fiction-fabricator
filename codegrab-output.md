# Project Structure

```
fiction-fabricator/
├── .github/
│   ├── documentation/
│   │   ├── 1_introduction_and_features.md
│   │   ├── 2_installation_guide.md
│   │   ├── 3_configuration_guide.md
│   │   ├── 4_usage_workflow.md
│   │   └── 5_advanced_tools.md
│   └── improvements/
│       └── TODOs.md
├── Tools/
│   ├── PremiseGenerator.py
│   ├── PromptGenerator.py
│   ├── ShortStoryWriter.py
│   ├── Test.py
│   └── WebNovelChapterWriter.py
├── Writer/
│   ├── Chapter/
│   │   ├── ChapterDetector.py
│   │   ├── ChapterGenSummaryCheck.py
│   │   ├── ChapterGenerator.py
│   │   └── __init__.py
│   ├── Interface/
│   │   ├── OpenRouter.py
│   │   ├── Wrapper.py
│   │   └── __init__.py
│   ├── Outline/
│   │   ├── StoryElements.py
│   │   └── __init__.py
│   ├── Scene/
│   │   ├── ChapterByScene.py
│   │   ├── ChapterOutlineToScenes.py
│   │   ├── SceneOutlineToScene.py
│   │   └── ScenesToJSON.py
│   ├── Config.py
│   ├── CritiqueRevision.py
│   ├── LLMEditor.py
│   ├── LLMUtils.py
│   ├── NarrativeContext.py
│   ├── NovelEditor.py
│   ├── OutlineGenerator.py
│   ├── PrintUtils.py
│   ├── Prompts.py
│   ├── Scrubber.py
│   ├── Statistics.py
│   ├── StoryInfo.py
│   ├── SummarizationUtils.py
│   ├── Translator.py
│   └── __init__.py
├── .gitignore
├── Evaluate.py
├── README.md
├── Write.py
├── config.ini
└── requirements.txt
```

# Project Files

## File: `.github/documentation/1_introduction_and_features.md`

```markdown
# 1. Introduction and Features

Fiction Fabricator is an advanced, AI-powered framework for generating complete, multi-chapter novels from a single creative prompt. It leverages a suite of modern Language Learning Models (LLMs) through a unified interface, employing a sophisticated, multi-stage pipeline of outlining, scene-by-scene generation, and iterative revision to produce high-quality, coherent long-form narratives.

This project is a significantly modified and enhanced fork of **[AIStoryteller by datacrystals](https://github.com/datacrystals/AIStoryteller)**. It was created to enhance the original project with a focus on provider flexibility, improved narrative coherence, and a more powerful, user-configurable generation process.

## Purpose

The purpose of this project is to create long-form fictional prose content leveraging the text generation capabilities of modern LLMs. Fiction Fabricator is designed to be a powerful, flexible, and transparent tool for creating long-form fiction with AI, which unlike other projects that focus on content generation, Fiction Fabricator is especially tailored to creating coherent, enjoyable novels that can be read and enjoyed by humans but which require minimal human intervention during the creation process.

### Creation Workflow

To give you a high level overview of the book creation process this project enables, here is a brief outline of the workflow:

1. Human provides a prompt, which is a premise written into several sentences (Tools/PromptGenerator.py can help with this and Tools/PremiseGenerator.py can help brainstorm ideas).
2. Human selects a model from the list of available models on the screen
3. Fiction Fabricator then outlines, critiques, revises and then writes the book, chapter by chapter with each chapter being broken down into scenes.
4. Content is dumped into the `Stories/` directory, with each run generating a unique, timestamped directory containing the final story, run statistics, and detailed debug files for every LLM call, providing complete transparency into the generation process.
5. User should then read the content and make any necessary edits as the content is not guaranteed to be perfect and making edits is what case law suggests is necessary to own the copyright to the content.

Frighteningly simple, right? A lot simpler than Steven King doing a gram of cocaine per page while writing "It".

## Key Features & Modifications

- **Unified Multi-Provider Interface**: Seamlessly switch between LLM providers like **Google Gemini, Groq, Mistral, Ollama, and NVIDIA NIM** using a simple URI format (e.g., `groq://llama3-70b-8192`).
- **Robust & Predictable NVIDIA NIM Integration**: The NVIDIA integration has been specifically hardened to provide full user control. Models are **manually and explicitly listed** in the `config.ini` file, removing the unpredictability of a dynamic discovery function and ensuring that any model you have access to can be used.
- **Flexible API Configuration**: Easily configure API endpoints, including the crucial `NVIDIA_BASE_URL`, either through a `.env` file for security or directly in `config.ini` for simplicity.
- **Advanced Scene-by-Scene Generation**: Instead of attempting to generate entire chapters at once, Fiction Fabricator breaks chapter outlines down into individual scenes. It writes each scene with context from the preceding one, dramatically improving narrative flow and short-term coherence.
- **Iterative Critique & Revision Engine**: At critical stages of generation (outline, scene breakdown, chapter writing), the system uses an LLM to critique its own output and then revise it based on that feedback. This self-correction loop significantly enhances the quality of the final product.
- **Intelligent Prompt Engineering**: Includes a powerful utility (`Tools/PromptGenerator.py`) that takes a user's simple idea and uses an LLM-driven, multi-step process to expand it into a rich, detailed prompt perfect for generating a complex story.
- **Short Story Generator (`Tools/ShortStoryWriter.py`)**: A dedicated tool that uses an iterative generation process to quickly write complete, self-contained short stories from a single premise, saving them to a separate `Short_Story/` directory.
- **Episodic Chapter Generator (`Tools/WebNovelChapterWriter.py`)**: A powerful tool for writing individual chapters for web novels or other serialized content. Provide a master premise and a topic for the current chapter, and optionally provide the previous chapter to ensure perfect narrative continuity between writing sessions.
- **Comprehensive Logging**: Every run generates a unique, timestamped directory in `Logs/`, containing the final story, run statistics, and detailed debug files for every LLM call, providing complete transparency into the generation process.
- **Developer & Power-User Utilities**:
  - **`Tools/Test.py`**: A testing script for quickly running generations with different pre-defined model configurations.
  - **`Evaluate.py`**: A powerful A/B testing tool that uses an LLM to compare two generated stories on multiple axes, such as plot, style, and dialogue.
  - **`Tools/PromptGenerator.py`**: A tool to generate the more comprehensive prompt in `Prompt/` expected as a parameter by `Write.py`.
  - **`Tools/PremiseGenerator.py`**: A brainstorming tool to generate 10 unique premises from a high-level theme.

```

## File: `.github/documentation/2_installation_guide.md`

```markdown
# 2. Installation Guide

This guide provides everything you need to know to install the project and set up its dependencies.

## Prerequisites

- Python 3.10 or higher.
- `git` for cloning the repository.

## Installation Steps

Follow these steps from your terminal to get the project running.

```bash
# 1. Clone the repository
# Replace <your-repository-url> with the actual URL of the project repository
git clone <your-repository-url>

# 2. Navigate into the project directory
cd fiction-fabricator # Or your project's root directory name

# 3. (Recommended) Create and activate a virtual environment
# This isolates the project's dependencies from your system's Python installation.
python -m venv venv

# Activate the virtual environment:
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 4. Install the required packages
# The requirements.txt file contains all necessary Python libraries.
pip install -r requirements.txt
```

Once these steps are complete, the application is installed and you can proceed to the configuration step.

```

## File: `.github/documentation/3_configuration_guide.md`

```markdown
# 3. Configuration Guide

Configuration for Fiction Fabricator is handled by two key files located in the project's root directory: `.env` for secret API keys and `config.ini` for general application settings.

## The `.env` File (For Secrets)

This is the **most secure and recommended** place for your API keys. The application will automatically load this file if it exists. Create a file named `.env` in the project's root directory.

**Example `.env` file content:**

```
# Provider API Keys
GOOGLE_API_KEY="your-google-api-key"
MISTRAL_API_KEY="your-mistral-api-key"
GROQ_API_KEY="your-groq-api-key"

# For NVIDIA, the API key is required.
NVIDIA_API_KEY="nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# The NVIDIA Base URL is optional here. If set, it will OVERRIDE the value in config.ini.
# This is useful for pointing to custom, preview, or self-hosted NIM endpoints.
# NVIDIA_BASE_URL="https://your-custom-nim-url.com/v1"

# For GitHub Models Marketplace, you must provide your GitHub Access Token
# and the correct endpoint URL.
GITHUB_ACCESS_TOKEN="github_pat_..."
AZURE_OPENAI_ENDPOINT="https://models.github.ai/inference"
```

## The `config.ini` File (For Settings)

This file controls the application's behavior, default model selection, and generation parameters. You can override most of these settings with command-line arguments when you run the `Write.py` script.

### [LLM_SELECTION]

Set the default models for each step of the generation process.

- **Format:** `provider://model_identifier`
- **Examples:** `google://gemini-1.5-pro-latest`, `groq://mixtral-8x7b-32768`, `ollama://llama3`

### [NVIDIA_SETTINGS]

- `base_url`: The API endpoint for NVIDIA models. The default (`https://integrate.api.nvidia.com/v1`) is for standard, managed models.
- `available_models`: **This is a crucial, manual list.** Add the specific model IDs you have access to and wish to use, separated by commas. These will appear in the interactive selection menu.
  - _Example_: `available_models = meta/llama3-70b-instruct, mistralai/mistral-large`

### [GITHUB_SETTINGS]

- `api_version`: The specific API version required by the Azure OpenAI client used for the GitHub provider. It's best not to change this unless you know what you are doing.

### [WRITER_SETTINGS]

Fine-tune the generation process.

- `scene_generation_pipeline`: (Default: `true`) Highly recommended. Enables the advanced scene-by-scene workflow.
- `enable_final_edit_pass`: (Default: `false`) Performs a final, holistic edit of the entire novel. Can increase cost and time but may improve consistency.
- `expand_outline`: (Default: `true`) Enables the multi-group detailed outline generation process.
- `minimum_chapters`: The minimum number of chapters the final outline should have.
- `seed`: A seed for randomization to ensure reproducible results.
- `debug`: (Default: `false`) Enables verbose logging, including saving all LLM prompts and responses.

### [TIMEOUTS]

- `default_timeout`: Request timeout in seconds for most API calls.
- `ollama_timeout`: A longer timeout specifically for Ollama, which may have long load times for local models.

```

## File: `.github/documentation/4_usage_workflow.md`

```markdown
# 4. Usage Workflow

This guide outlines the recommended workflow for generating a novel with Fiction Fabricator, from initial idea to final output.

## Step 1: Brainstorm Premises (Optional but Recommended)

If you only have a high-level theme (e.g., "haunted spaceship"), you can use the `PremiseGenerator.py` tool to brainstorm more concrete ideas.

````bash
# Run the tool with your high-level theme
python Tools/PremiseGenerator.py -i "haunted spaceship"```

The tool will present a model selection menu and then generate 10 distinct premises based on your theme. The output is saved to a timestamped file in the `Premises/` directory. You can use any of these premises as input for the next step.

## Step 2: Create a High-Quality Prompt

A detailed prompt produces a better story. Use the `PromptGenerator.py` tool to expand a simple idea or one of the premises from the previous step into a rich, detailed prompt suitable for the main application.

```bash
# Run the tool with your chosen story title and premise
python Tools/PromptGenerator.py -t "The Last Signal" -i "A lone astronaut on Mars discovers a strange, repeating signal from a polar ice cap, but her mission command on Earth insists it's just a malfunction."
````

This will again prompt you to select a model for the generation and will save a detailed `prompt.txt` file in `Prompts/The_Last_Signal/`.

## Step 3: Write the Novel

Use the main `Write.py` script to start the full generation process, using the prompt file you just created.

### Interactive Mode (Easiest)

Simply provide the prompt file path. The script will present an interactive menu to select the primary writing model from all your configured providers.

```bash
python Write.py -Prompt "Prompts/The_Last_Signal/prompt.txt"
```

### Custom/Headless Mode

You can specify all models and settings via command-line arguments. This is useful for automated runs or for overriding the settings in `config.ini`.

```bash
# Example of a custom run using different models for different tasks
python Write.py \
-Prompt "Prompts/The_Last_Signal/prompt.txt" \
-InitialOutlineModel "google://gemini-1.5-pro-latest" \
-ChapterS1Model "groq://llama3-70b-8192" \
-ChapterRevisionModel "nvidia://meta/llama3-70b-instruct" \
-EnableFinalEditPass \
-Seed 42
```

## Step 4: Find Your Story

All output is saved to uniquely named directories to prevent overwriting your work.

- **`Stories/`**: Contains the final, user-facing output. For each run, you will get:

  - `Your_Story_Title.md`: A markdown file with the formatted story, generation statistics, and the full outline.
  - `Your_Story_Title.json`: A structured JSON file containing the complete narrative context, including all outlines, chapter text, and summaries. This file can be used for analysis or further processing.

- **`Logs/`**: Contains detailed logs for debugging. A new directory is created for each run, containing:
  - `Main.log`: A human-readable log of all steps, warnings, and errors.
  - `LangchainDebug/`: A folder with `.json` and `.md` files for every single call made to an LLM, showing the exact prompts and responses. This is invaluable for debugging and understanding the generation process.

```

## File: `.github/documentation/5_advanced_tools.md`

```markdown
# 5. Advanced Tools

Fiction Fabricator includes several powerful utilities for power users, developers, and those who want to experiment with different models and generation strategies.

## Generating Short Stories (`Tools/ShortStoryWriter.py`)

This tool is designed for quickly creating self-contained short stories using an iterative generation method similar to the main novel writer, but optimized for shorter-form content.

### How to Use:

Provide a premise directly on the command line. The tool handles the rest: creating an outline, writing the story in iterative chunks, and saving the final result.

```bash
# Example command
python Tools/ShortStoryWriter.py --premise "A clockmaker in a city where time has stopped is the only one who can hear it ticking again, but each tick ages him rapidly."
```

The tool will present the standard model selection menu and then generate the story. All output is saved to a timestamped file in the **`Short_Story/`** directory.

## Generating Episodic Chapters (`Tools/WebNovelChapterWriter.py`)

This tool is perfect for writing stories one chapter at a time, making it ideal for web novels, light novels, or CYOA-style narratives. It ensures continuity between chapters even if they are written days apart.

### How to Use:

The tool requires a file with your overall story premise and a prompt for the specific chapter's events.

```bash
# --- Writing Chapter 1 ---
# First, you need a premise file (e.g., MyStoryPremise.txt)
# Then, run the tool with the chapter topic and desired output path.
python Tools/WebNovelChapterWriter.py \
  --premise_file "path/to/your/premise.txt" \
  --chapter_topic "Our hero, a young starship pilot, receives a cryptic distress call from a supposedly dead colony." \
  --output_file "Web_Novel_Chapters/MyStory/Chapter_1.md"

# --- Writing Chapter 2 (later) ---
# To ensure continuity, provide the previously written chapter as context.
# The tool will summarize it and use that to inform the next chapter's generation.
python Tools/WebNovelChapterWriter.py \
  --premise_file "path/to/your/premise.txt" \
  --chapter_topic "Following the signal, the pilot discovers the colony is not dead, but has evolved into a strange, hostile ecosystem." \
  --previous_chapter_file "Web_Novel_Chapters/MyStory/Chapter_1.md" \
  --output_file "Web_Novel_Chapters/MyStory/Chapter_2.md"
```

This workflow uses the project's powerful scene-by-scene generation pipeline for each chapter, ensuring high quality and coherence. By default, it's best to organize outputs in the **`Web_Novel_Chapters/`** directory.

## Testing Model Configurations (`Tools/Test.py`)

The `Test.py` script is designed for rapid experimentation. You can define different sets of models for various roles directly within the Python script and then quickly launch a generation with that pre-defined configuration.

### How to Use:

1.  **Edit `Tools/Test.py`**: Open the file and modify the `MODEL_CONFIGS` dictionary. You can add new configurations or change existing ones.
    ```python
    # Example configuration in Test.py
    "7": {
        "name": "NVIDIA Llama3 70B (Full Stack)",
        "models": {
            "InitialOutlineModel": "nvidia://meta/llama3-70b-instruct",
            "ChapterOutlineModel": "nvidia://meta/llama3-70b-instruct",
            # ... and so on for all model parameters
        }
    },
    ```
2.  **Run the script**:
    ```bash
    python Tools/Test.py
    ```
3.  **Select a Configuration**: The script will prompt you to choose one of your defined configurations, select a prompt, and add any extra flags. It then constructs and executes the full `Write.py` command for you.

This is the perfect tool for testing the performance and writing style of different LLM providers and models.

## Evaluating Stories (`Evaluate.py`)

After generating two or more stories, you might want to compare them objectively. The `Evaluate.py` tool uses a powerful LLM to act as a literary critic, comparing two generated stories on multiple axes.

### How to Use:

The tool takes the `.json` output files from two different story runs as input.

```bash
# Example command
python Evaluate.py -Story1 "Stories/Story_A_output.json" -Story2 "Stories/Story_B_output.json" -Output "Comparison_Report.md"
```

The script will:

1.  Prompt the evaluation model to compare the outlines of both stories.
2.  Prompt the model to compare each chapter, one by one.
3.  Tally the "wins" for each story across categories like Plot, Style, and Dialogue.
4.  Generate a detailed `Comparison_Report.md` file with its findings.

```

## File: `.github/improvements/TODOs.md`

```markdown
# Project To-Do List

My rough list and attempt to keep some order and sanity in my work on this project moving forward. Using special highlighting and todo tracking via GitHub issues and Neovim plugins that _hopefully_ will prompt me to refer back to this list and keep it updated.

## Of Immediate Concern

These are items I am intending to get to sooner rather than later, this list will guide subsequent commits I make to the project repo directly.

- [ ] TODO debug cycle by using project to create at least 3 books and catch any errors during that process.
  - [x] DONE Book 1: Still too short, need to break the scene generation into smaller chunks
  - [x] DONE Book 2: Still too short, cut off in critique phase and cut offs in the beginning contextual generation, which have been fixed and the generation cycle is now more iterative. Still getting more errors than I would like from the word count minimum checks but we will see how it goes.
- [ ] TODO Create a tool to write short stories using the project's infrastructure, using the same prompt as a novel but with a shorter length
- [ ] TODO Create a unified menu the user can use to select if they want to generate a book, short story, generate ideas or generate a novel prompt

- [ ] TODO create a tool to write individual chapters for a web based lightnovel or CYOA style story

## Intended in Future

These are not pressing needs, but medium to long term mile markers along the project roadmap (**_pull requests always welcome_**).

- [ ] TODO means of picking back up from an uncompleted generation attempt
- [ ] TODO failover for when API calls exceed rate limits (because I do use the free tier of course, I am poor)

## Archive

These are items that have been completed, obviously. Kept here for posterity and as a means of seeing how much progress has been made trekking towards that horizon of feature-completeness.

- [x] DONE rebase on original project, refactoring while preserving more of original functionality
- [x] DONE integrate Nvidia NIM endpoints efficiently
- [x] DONE Integrating at least some of the Github Models using the means provided on the model playground pages _vis-a-vis_ GitHub Models
- [x] DONE timeout for generations, preventing hanging calls from compromising generation pipeline
- [x] DONE Create tool to generate the ideas to feed into `Tools/PromptGeneration.py`
- [x] DONE create documentation for the project and link to it on the README.md

```

## File: `Tools/PremiseGenerator.py`

```python
# File: Tools/PremiseGenerator.py
# Purpose: Generates 10 story premises from a rough theme or idea using an LLM.
# This script is self-contained and should be run from the project's root directory.

"""
FictionFabricator Premise Generator Utility.
"""

import argparse
import os
import sys
import json
import datetime
import dotenv

# --- Add project root to path for imports and load .env explicitly ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    dotenv_path = os.path.join(project_root, '.env')
    if os.path.exists(dotenv_path):
        dotenv.load_dotenv(dotenv_path=dotenv_path)
        print(f"--- Successfully loaded .env file from: {dotenv_path} ---")
    else:
        print("--- .env file not found, proceeding with environment variables if available. ---")
except Exception as e:
    print(f"--- Error loading .env file: {e} ---")

# --- Standardized Imports from Main Project ---
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
# --- Refactored Import for Centralized LLM Utilities ---
from Writer.LLMUtils import get_llm_selection_menu_for_tool


# --- FIXED Prompts ---

SYSTEM_PROMPT_STYLE_GUIDE = """
You are a creative brainstorming assistant and an expert in crafting compelling story premises. Your goal is to generate ideas that are fresh, intriguing, and rich with narrative potential, tailored to the user's request.
"""

GENERATE_PREMISES_PROMPT_TEMPLATE = """
A user has provided a rough theme or idea and wants you to generate 10 distinct, compelling story premises based on it.

**User's Theme/Idea:** "{idea}"

Your task is to generate 10 unique story premises that are directly inspired by the user's idea. Each premise must be a self-contained concept, detailed enough to be used as input for another AI tool.

For each premise, you must include:
- A compelling core conflict.
- A brief sketch of one or more main characters.
- A hint about the setting and its atmosphere.
- The central stakes of the story.
- A unique twist, "what if" scenario, or narrative hook that makes the premise original and avoids clichés associated with the user's idea.

**CRITICAL:** Your entire output must be a single, valid JSON object.
The JSON object should have one key, "premises", which is a list of exactly 10 strings. Each string is one of the detailed premises you have created.

Do not include any other text, titles, or explanations outside of this JSON object.
"""

CRITIQUE_PREMISES_PROMPT_TEMPLATE = """
You are a professional story editor with a strong aversion to clichés and a love for innovative narratives. You have been given a list of story premises based on a user's initial idea. Your task is to provide sharp, constructive criticism to elevate the list.

**USER'S ORIGINAL IDEA:** "{idea}"

**LIST OF PREMISES TO CRITIQUE:**
---
{premises_json}
---

Please critique the list based on the following rigorous criteria:
1.  **Conceptual Originality vs. Cliché:** Do these premises creatively explore the *core* of the user's idea, or do they immediately fall back on the most predictable, overused tropes for this genre? Identify specific premises that are too generic and suggest pushing for a more unique angle.
2.  **Thematic Cohesion:** Does every premise remain faithful to the spirit and concept of the user's original idea? Flag any premise that introduces elements that seem to clash with the core concept.
3.  **Narrative Potential:** Do the premises offer enough depth for a compelling story? Do they hint at interesting conflicts, characters, and stakes? Or are they shallow and one-dimensional?
4.  **Variety:** Does the list offer a good variety of takes on the user's idea, or are they all minor variations of the same basic plot?

Provide your critique as a few bullet points of direct, actionable feedback. Your goal is to guide the next AI to create a stronger, more original, and more thematically interesting set of premises. Your output should be a plain string of text.
"""

REVISE_PREMISES_BASED_ON_CRITIQUE_TEMPLATE = """
You are a master storyteller. Your task is to revise a list of 10 story premises based on an editor's sharp critique. The critique is focused on avoiding clichés and pushing the ideas towards greater originality and narrative depth.

**USER'S ORIGINAL IDEA:** "{idea}"

**ORIGINAL LIST OF PREMISES:**
---
{original_premises_json}
---

**EDITOR'S CRITIQUE:**
---
{critique}
---

**YOUR TASK:**
Rewrite the list of 10 premises to directly address the points in the "EDITOR'S CRITIQUE".
- **Eliminate Clichés & Boost Originality:** For any premise the critique flagged as generic, invent a more original concept that still honors the user's core idea. Subvert common tropes.
- **Enforce Thematic Cohesion:** Refine or remove any elements that clash with the user's core concept, as pointed out by the critique. Ensure every premise is a unique but *consistent* exploration of the original idea.
- **Deepen the Concepts:** For any premise noted as shallow, flesh it out with a stronger conflict, more interesting character dynamics, and clearer stakes.

**CRUCIAL:** Your entire output MUST be a single, valid JSON object, identical in format to the original. It must have one key, "premises", which is a list of exactly 10 strings. Do not include any text or explanations outside of the JSON object.
"""

def main():
    parser = argparse.ArgumentParser(description="FictionFabricator Self-Contained Premise Generator.")
    parser.add_argument("-i", "--idea", required=True, help="The user's high-level story theme or genre.")
    parser.add_argument("--temp", type=float, default=0.8, help="Temperature for LLM generation (default: 0.8).")
    args = parser.parse_args()

    generation_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    print("--- FictionFabricator Premise Generator ---")
    sys_logger = Logger("PremiseGenLogs")

    # --- Dynamic Model Selection ---
    selected_model_uri = get_llm_selection_menu_for_tool(sys_logger, tool_name="Premise Generator")
    if not selected_model_uri:
        sys_logger.Log("No model was selected or discovered. Exiting.", 7)
        sys.exit(1)

    interface = Interface()
    interface.LoadModels([selected_model_uri])

    # Step 1: Generate Initial Premises
    print(f"\nStep 1: Brainstorming 10 initial premises for the idea: '{args.idea}'...")
    generation_prompt = GENERATE_PREMISES_PROMPT_TEMPLATE.format(idea=args.idea)
    model_with_params = f"{selected_model_uri}?temperature={args.temp}&max_tokens=4000"

    messages = [
        interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
        interface.BuildUserQuery(generation_prompt)
    ]
    _, initial_response_json = interface.SafeGenerateJSON(
        sys_logger, messages, model_with_params, _RequiredAttribs=["premises"]
    )

    if not initial_response_json or "premises" not in initial_response_json or not isinstance(initial_response_json["premises"], list):
        print("Error: Failed to generate an initial valid list of premises. Aborting.")
        sys.exit(1)

    final_premises = initial_response_json['premises']

    # Step 2: Critique the generated premises
    print("\nStep 2: Critiquing the initial list of premises...")
    critique_prompt = CRITIQUE_PREMISES_PROMPT_TEMPLATE.format(
        idea=args.idea, premises_json=json.dumps(initial_response_json, indent=2)
    )
    critique_messages = [
        interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
        interface.BuildUserQuery(critique_prompt)
    ]
    critique_history = interface.SafeGenerateText(
        sys_logger, critique_messages, model_with_params, min_word_count_target=50
    )
    critique = interface.GetLastMessageText(critique_history).strip()

    # Step 3: Revise the premises based on critique
    if "[ERROR:" in critique or not critique:
        print("\nWarning: Critique step failed or returned empty. Skipping revision and using initial premises.")
    else:
        print("\n--- Critique ---")
        print(critique)
        print("----------------")
        print("\nStep 3: Revising premises based on critique...")
        revision_prompt = REVISE_PREMISES_BASED_ON_CRITIQUE_TEMPLATE.format(
            idea=args.idea,
            original_premises_json=json.dumps(initial_response_json, indent=2),
            critique=critique
        )
        revision_messages = [
            interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
            interface.BuildUserQuery(revision_prompt)
        ]
        _, revised_response_json = interface.SafeGenerateJSON(
            sys_logger, revision_messages, model_with_params, _RequiredAttribs=["premises"]
        )

        if revised_response_json and "premises" in revised_response_json and isinstance(revised_response_json["premises"], list):
            final_premises = revised_response_json['premises']
            print("Successfully revised premises.")
        else:
            print("\nWarning: Revision step failed to produce valid JSON. Using initial premises.")

    if not final_premises:
        print("Error: The final list of premises is empty. Aborting.")
        sys.exit(1)

    print("\n--- Final Generated Premises ---")
    formatted_output = ""
    for i, premise in enumerate(final_premises):
        premise_text = f"## Premise {i+1}\n\n{premise}\n\n---\n"
        print(premise_text)
        formatted_output += premise_text
    print("--------------------------")

    premises_base_dir = os.path.join(project_root, "Premises")
    os.makedirs(premises_base_dir, exist_ok=True)

    output_filename = f"Premise_List_{generation_timestamp}.txt"
    output_path = os.path.join(premises_base_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Premises for Idea: {args.idea}\n")
            f.write(f"# Generated on: {generation_timestamp}\n\n")
            f.write(formatted_output)
        print(f"\nSuccessfully saved generated premises to: {output_path}")
    except OSError as e:
        print(f"Error creating directory or writing file to '{output_path}': {e}")
        sys.exit(1)

    print("\n--- Premise Generation Complete ---")
    print("You can now use any of these premises as input for Tools/PromptGenerator.py")


if __name__ == "__main__":
    main()

```

## File: `Tools/PromptGenerator.py`

```python
# File: Tools/PromptGenerator.py
# Purpose: Generates a refined prompt.txt for FictionFabricator using an LLM.
# This script is self-contained and should be run from the project's root directory.

"""
FictionFabricator Prompt Generator Utility.

This script takes a basic user idea and a desired story title to generate a more
detailed and refined `prompt.txt` file. This output file is structured to be an
effective input for the main Write.py script.

The process involves:
1. Dynamically selecting an LLM from available providers.
2. Expanding the user's initial idea using the selected LLM.
3. Having the LLM critique its own expansion.
4. Refining the prompt based on this critique.
5. Saving the final prompt to `Prompts/<SanitizedTitle>/prompt.txt`.

Requirements:
- All packages from the main project's `requirements.txt`.
- A configured `.env` file with API keys for desired providers.
- An accessible Ollama server if using local models.

Usage:
python Tools/prompt_generator.py -t "CrashLanded" -i "After the surveying vessel crashed on the planet it was sent to determine viability for human colonization, the spunky 23 year old mechanic Jade and the hardened 31 year old security officer Charles find the planet is not uninhabited but teeming with humans living in primitive tribal conditions and covered in the ruins of an extinct human society which had advanced technologies beyond what are known to Earth. Now they must navigate the politics of these tribes while trying to repair their communication equipment to call for rescue, while learning to work together despite their initial skepticism about the other."
"""

import argparse
import os
import sys
import re
import dotenv

# --- Add project root to path for imports and load .env explicitly ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    dotenv_path = os.path.join(project_root, '.env')
    if os.path.exists(dotenv_path):
        dotenv.load_dotenv(dotenv_path=dotenv_path)
        print(f"--- Successfully loaded .env file from: {dotenv_path} ---")
    else:
        print("--- .env file not found, proceeding with environment variables if available. ---")
except Exception as e:
    print(f"--- Error loading .env file: {e} ---")

# --- Standardized Imports from Main Project ---
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
# --- Refactored Import for Centralized LLM Utilities ---
from Writer.LLMUtils import get_llm_selection_menu_for_tool


# --- Prompts for this script (Refactored for Flexibility) ---

SYSTEM_PROMPT_STYLE_GUIDE = """
You are a creative assistant and expert prompt engineer. Your goal is to help a user transform their story idea into a rich, detailed, and effective prompt for an AI story generator.
"""

EXPAND_IDEA_PROMPT_TEMPLATE = """
You are a creative assistant helping to flesh out a story idea into a detailed prompt suitable for an AI story generator.
Your goal is to expand the user's basic idea into a richer concept that is faithful to their original vision.

User's Title: "{title}"
User's Basic Idea: "{idea}"

Expand this into a more detailed story prompt. You must capture and enhance the following based on the user's idea:
- **Genre and Tone:** Identify the likely genre and tone from the user's idea (e.g., Sci-Fi Adventure, Psychological Thriller, Fantasy Romance) and write the prompt to reflect it.
- **Core Conflict:** What is the central problem the characters will face?
- **Main Character(s) Sketch:** Briefly introduce the main characters as described or implied by the idea.
- **Setting Snippet:** A brief hint about the world or primary location that establishes its atmosphere.
- **Potential a Ending Direction:** Hint at a possible conclusion that would be a satisfying and logical outcome of the premise, whether it's happy, tragic, or ambiguous.

Your response should be *only* the expanded story prompt itself.
Do not include any titles, headings, preambles, or other conversational text.
Make it engaging and provide enough substance for an AI to build a complex story upon.
"""

CRITIQUE_EXPANDED_PROMPT_TEMPLATE = """
You are an expert AI prompt engineer evaluating a story prompt intended for an advanced AI story generation system.

Here is the expanded story prompt you need to critique:
---
{expanded_prompt}
---

Critique this prompt based on its effectiveness for generating a compelling narrative that matches the user's apparent intent:
1.  **Clarity and Specificity:** Is the core story idea clear? Is the central conflict understandable? Are the characters distinct enough to start with?
2.  **Adherence to Intended Tone:** Does the prompt's tone match the user's idea? (e.g., if the idea is adventurous, is the prompt exciting? If the idea is mysterious, is the prompt intriguing?).
3.  **Potential for Complexity:** Does the prompt provide enough substance for the AI to generate a multi-chapter plot with interesting characters and meaningful conflict? Or is it a simple, one-note concept?
4.  **Actionability for AI:** Are there clear starting points for the AI? Are there any ambiguities that might confuse the AI or lead it astray from the user's original idea?

Provide your critique as a list of bullet points (strengths and weaknesses). Be constructive. The goal is to identify areas for improvement to make the prompt stronger.
"""

REFINE_PROMPT_BASED_ON_CRITIQUE_TEMPLATE = """
You are a master creative assistant. You have an expanded story prompt and a critique of that prompt.
Your task is to revise and improve the original expanded prompt based *only* on the provided critique.
The goal is to create a final, high-quality `prompt.txt` file that will be excellent input for an AI story generator.

Original Expanded Story Prompt:
---
{expanded_prompt}
---

Critique of the Expanded Story Prompt:
---
{critique}
---

Based on the critique, revise the "Original Expanded Story Prompt".
- **Clarify and Enhance the Intended Tone:** Double down on the elements that make the prompt reflect the user's original idea. Be more explicit about the desired tone and feeling.
- **Flesh out Details:** Address any weaknesses noted in the critique regarding character motivation, setting, or plot specificity.

Your entire response MUST be *only* the revised story prompt text itself.
Do NOT include any titles, headings, introductory sentences, or explanations.
The output will be saved directly to a file, so it must contain *only* the story prompt.
"""


def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be suitable for a filename or directory name."""
    name = re.sub(
        r"[^\w\s-]", "", name
    ).strip()  # Remove non-alphanumeric (except underscore, hyphen, space)
    name = re.sub(r"[-\s]+", "_", name)  # Replace spaces and hyphens with underscores
    return name if name else "Untitled_Prompt"


def _extract_core_prompt(llm_response: str) -> str:
    """
    Cleans LLM response to extract only the core prompt text.
    Removes common preambles, headers, and other conversational/formatting artifacts.
    """
    if not isinstance(llm_response, str):
        return ""

    lines = llm_response.strip().split("\n")
    start_index = 0
    # Skip any leading blank lines
    while start_index < len(lines) and not lines[start_index].strip():
        start_index += 1
    lines = lines[start_index:]
    if not lines:
        return ""

    # Patterns for common headers to be removed
    header_patterns = [
        re.compile(r"^\s*HERE(?:'S| IS)? THE (?:REVISED|FINAL|EXPANDED|REQUESTED)?\s*PROMPT\s*[:.]?\s*$", re.IGNORECASE),
        re.compile(r"^\s*(?:REVISED|FINAL|EXPANDED|STORY)?\s*PROMPT\s*[:]?\s*$", re.IGNORECASE),
        re.compile(r"^\s*OKAY\s*[,.]?.*$", re.IGNORECASE),
    ]

    if lines:
        first_line_content = lines[0].strip()
        for pattern in header_patterns:
            if pattern.fullmatch(first_line_content):
                lines.pop(0)
                # Also remove any blank lines that followed the header
                while lines and not lines[0].strip():
                    lines.pop(0)
                break

    return "\n".join(lines).strip()


def main():
    parser = argparse.ArgumentParser(description="FictionFabricator Self-Contained Prompt Generator.")
    parser.add_argument("-t", "--title", required=True, help="Desired title for the story (used for subdirectory name).")
    parser.add_argument("-i", "--idea", required=True, help="The user's basic story idea or concept.")
    parser.add_argument("--temp", type=float, default=0.7, help="Temperature for LLM generation (default: 0.7).")
    args = parser.parse_args()

    print("--- FictionFabricator Prompt Generator ---")
    sys_logger = Logger("PromptGenLogs")

    # --- Dynamic Model Selection ---
    selected_model_uri = get_llm_selection_menu_for_tool(sys_logger, tool_name="Prompt Generator")
    if not selected_model_uri:
        sys_logger.Log("No model was selected or discovered. Exiting.", 7)
        sys.exit(1)

    # --- Instantiate Interface and load selected model ---
    interface = Interface()
    interface.LoadModels([selected_model_uri])

    # --- Generation Logic ---
    print("\nStep 1: Expanding user's idea...")
    expand_user_prompt = EXPAND_IDEA_PROMPT_TEMPLATE.format(title=args.title, idea=args.idea)
    # Increased max_tokens to prevent cutoff
    expand_model_with_params = f"{selected_model_uri}?temperature={args.temp}&max_tokens=2048"

    expand_messages = [
        interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
        interface.BuildUserQuery(expand_user_prompt)
    ]
    response_history = interface.SafeGenerateText(sys_logger, expand_messages, expand_model_with_params, min_word_count_target=100)
    expanded_prompt_raw = interface.GetLastMessageText(response_history)

    if "[ERROR:" in expanded_prompt_raw:
        print(f"Failed to expand prompt: {expanded_prompt_raw}")
        sys.exit(1)

    expanded_prompt = _extract_core_prompt(expanded_prompt_raw)
    print("\n--- Expanded Prompt (Post-Cleaning) ---")
    print(expanded_prompt)
    print("-------------------------------------")

    if not expanded_prompt.strip():
        print("Error: Expanded prompt is empty after cleaning. Exiting.")
        sys.exit(1)

    print("\nStep 2: Critiquing the expanded prompt...")
    critique_user_prompt = CRITIQUE_EXPANDED_PROMPT_TEMPLATE.format(expanded_prompt=expanded_prompt)
    critique_model_with_params = f"{selected_model_uri}?temperature=0.5&max_tokens=1000"

    critique_messages = [
        interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
        interface.BuildUserQuery(critique_user_prompt)
    ]
    critique_history = interface.SafeGenerateText(sys_logger, critique_messages, critique_model_with_params, min_word_count_target=20)
    critique = interface.GetLastMessageText(critique_history).strip()

    final_prompt_text_candidate: str
    if "[ERROR:" in critique or not critique.strip():
        print("Warning: Critique failed or was empty. Proceeding with the initially expanded prompt.")
        final_prompt_text_candidate = expanded_prompt
    else:
        print("\n--- Critique ---")
        print(critique)
        print("----------------")

        print("\nStep 3: Refining prompt based on critique...")
        refine_user_prompt = REFINE_PROMPT_BASED_ON_CRITIQUE_TEMPLATE.format(expanded_prompt=expanded_prompt, critique=critique)
        # Increased max_tokens to prevent cutoff
        refine_model_with_params = f"{selected_model_uri}?temperature={args.temp}&max_tokens=2048"

        refine_messages = [
            interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
            interface.BuildUserQuery(refine_user_prompt)
        ]
        refine_history = interface.SafeGenerateText(sys_logger, refine_messages, refine_model_with_params, min_word_count_target=100)
        refined_text_raw = interface.GetLastMessageText(refine_history)

        if "[ERROR:" in refined_text_raw:
            print(f"Warning: Refinement failed: {refined_text_raw}. Using the initially expanded prompt.")
            final_prompt_text_candidate = expanded_prompt
        else:
            final_prompt_text_candidate = _extract_core_prompt(refined_text_raw)

    final_prompt_text = final_prompt_text_candidate
    if not final_prompt_text.strip():
        print("Error: Final prompt is empty after all processing. Exiting.")
        # Fallback logic to prevent empty file
        if expanded_prompt.strip():
            print("Fallback to last valid prompt (the expanded version).")
            final_prompt_text = expanded_prompt
        else:
            sys.exit(1)

    print("\n--- Final Prompt Content for prompt.txt ---")
    print(final_prompt_text)
    print("-------------------------------------------")

    prompts_base_dir = os.path.join(project_root, "Prompts")
    os.makedirs(prompts_base_dir, exist_ok=True)

    sanitized_title = sanitize_filename(args.title)
    prompt_subdir = os.path.join(prompts_base_dir, sanitized_title)

    try:
        os.makedirs(prompt_subdir, exist_ok=True)
        output_path = os.path.join(prompt_subdir, "prompt.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_prompt_text)
        print(f"\nSuccessfully generated and saved prompt to: {output_path}")
    except OSError as e:
        print(f"Error creating directory or writing file to '{prompt_subdir}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during file saving: {e}")
        sys.exit(1)

    print("\n--- Prompt Generation Complete ---")


if __name__ == "__main__":
    main()

```

## File: `Tools/ShortStoryWriter.py`

```python
# File: Tools/ShortStoryWriter.py
# Purpose: Generates a complete short story using an iterative process.
# This script is self-contained and should be run from the project's root directory.

"""
FictionFabricator Short Story Writer.

This tool takes a single premise and uses an LLM to generate a complete,
self-contained short story. It follows an iterative generation process.

The process involves:
1. Dynamically selecting an LLM from available providers.
2. Generating a title and a structured 5-point outline from the user's premise.
3. Writing the beginning of the story.
4. Iteratively generating the rest of the story in chunks until the LLM
   signals completion by outputting 'IAMDONE'.
5. Saving the final story to the `Short_Story/` directory.

Usage:
python Tools/ShortStoryWriter.py --premise "A librarian discovers that every book is a portal to the world it describes, but can only enter a book once."
"""

import argparse
import os
import sys
import datetime
import re

# --- Add project root to path for imports and load .env explicitly ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# dotenv is loaded by the centralized utilities, but we'll try here too for robustness.
try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(project_root, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        print(f"--- Successfully loaded .env file from: {dotenv_path} ---")
    else:
        print("--- .env file not found, proceeding with environment variables if available. ---")
except (ImportError, Exception) as e:
    print(f"--- Info: Could not load .env file: {e} ---")

# --- Standardized Imports from Main Project ---
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
# --- Refactored Import for Centralized LLM Utilities ---
from Writer.LLMUtils import get_llm_selection_menu_for_tool


# --- Short Story Prompts (Refactored for Better Structure) ---

PERSONA = """
You are a celebrated author of short stories, known for crafting concise yet deeply impactful narratives that linger in the reader's mind. Your goal is to write a complete, compelling short story from beginning to end, following a clear narrative structure.
"""

GUIDELINES = """
## Writing Guidelines

- **Focus on Brevity and Impact:** Every sentence must count. Focus on a single, compelling narrative arc.
- **Show, Don't Tell:** Use vivid descriptions and character actions to convey emotion and plot.
- **Complete Arc:** The story must have a clear beginning, rising action, climax, falling action, and a definitive resolution, as defined in your outline.
- **Embrace the Premise:** Fully explore the core concept of the premise within the confines of the short story format.
"""

TITLE_AND_OUTLINE_PROMPT_TEMPLATE = """
{persona}

You have been given a gripping premise for a short story:

**Premise:** "{premise}"

Your first task is to:
1.  **Create a Title:** Generate a fitting and evocative title for this short story.
2.  **Create a 5-Point Outline:** Write a clear, bullet-point outline covering the five essential plot points of a complete narrative arc.

Your entire response must be in the following format, with nothing else:

**Title:** [Your Title Here]

**Outline:**
- **Beginning:** [Introduce the main character, setting, and the inciting incident.]
- **Rising Action:** [Describe the series of events and conflicts that build tension and lead to the climax.]
- **Climax:** [Detail the story's peak, the main turning point for the protagonist.]
- **Falling Action:** [Explain the immediate aftermath of the climax.]
- **Resolution:** [Provide a definitive conclusion, showing the final outcome for the protagonist.]
"""

STARTING_PROMPT_TEMPLATE = """
{persona}

**Premise:** "{premise}"

**Title:** "{title}"

**Your Full Outline (Roadmap):**
---
{outline}
---

{guidelines}

---
First, silently review the outline and premise.

Now, begin writing the story. Your task is to write the **Beginning** of the story, covering the start of your outline. Write at least 500 words. Do **not** finish the entire story now.
"""

CONTINUATION_PROMPT_TEMPLATE = """
{persona}

**Premise:** "{premise}"

**Title:** "{title}"

**Your Full Outline (Roadmap):**
---
{outline}
---

**Here is the story you have written so far:**
---
{story_text}
---

{guidelines}

---
First, silently review the story so far and your full outline. Identify the next logical part of the outline to write (e.g., if you just wrote the 'Beginning', now write the 'Rising Action').

Your task is to continue where the story left off. Write the next section, moving the plot forward according to your outline. Write at least 500 words.

**IMPORTANT:** Once the story's conclusion (the **Resolution**) is fully written and the narrative is complete based on your outline, and only then, write the exact phrase `IAMDONE` on a new line at the very end of your response. Do NOT write `IAMDONE` if you are only writing the rising action or climax.
"""

def sanitize_filename(name: str) -> str:
    """Sanitizes a string for use as a filename."""
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'[-\s]+', '_', name)
    return name if name else "Untitled_Story"

def main():
    parser = argparse.ArgumentParser(description="FictionFabricator Short Story Writer.")
    parser.add_argument("--premise", required=True, help="The premise for the short story.")
    parser.add_argument("--temp", type=float, default=0.75, help="Temperature for LLM generation.")
    parser.add_argument("--max_iterations", type=int, default=10, help="Safety break for generation loop.")
    args = parser.parse_args()

    generation_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    sys_logger = Logger("ShortStoryLogs")

    selected_model_uri = get_llm_selection_menu_for_tool(sys_logger, "Short Story Writer")
    if not selected_model_uri:
        sys.exit(1)

    interface = Interface()
    interface.LoadModels([selected_model_uri])
    model_with_params = f"{selected_model_uri}?temperature={args.temp}&max_tokens=2000"

    # --- Step 1: Generate Title and Outline ---
    sys_logger.Log("Generating title and a structured 5-point outline...", 2)
    title_prompt = TITLE_AND_OUTLINE_PROMPT_TEMPLATE.format(persona=PERSONA, premise=args.premise)
    response_history = interface.SafeGenerateText(sys_logger, [interface.BuildUserQuery(title_prompt)], model_with_params, min_word_count_target=50)
    title_and_outline_text = interface.GetLastMessageText(response_history)

    try:
        title = re.search(r"Title:\s*(.*)", title_and_outline_text, re.IGNORECASE).group(1).strip()
        outline = title_and_outline_text.split("Outline:")[1].strip()
    except (AttributeError, IndexError):
        sys_logger.Log("Failed to parse title and outline from the LLM response. Exiting.", 7)
        print("--- LLM Response ---")
        print(title_and_outline_text)
        print("--------------------")
        sys.exit(1)

    sys_logger.Log(f"Title: {title}", 5)
    sys_logger.Log(f"Outline:\n{outline}", 4)

    # --- Step 2: Generate Start of Story ---
    sys_logger.Log("Generating the beginning of the story...", 2)
    start_prompt = STARTING_PROMPT_TEMPLATE.format(persona=PERSONA, premise=args.premise, title=title, outline=outline, guidelines=GUIDELINES)
    response_history = interface.SafeGenerateText(sys_logger, [interface.BuildUserQuery(start_prompt)], model_with_params, min_word_count_target=500)
    story_draft = interface.GetLastMessageText(response_history)


    # --- Step 3: Iteratively Continue Story ---
    sys_logger.Log("Continuing story generation iteratively...", 2)
    iteration_count = 1
    while 'IAMDONE' not in story_draft and iteration_count <= args.max_iterations:
        sys_logger.Log(f"--- Continuing generation (Iteration {iteration_count}) ---", 3)
        continuation_prompt = CONTINUATION_PROMPT_TEMPLATE.format(
            persona=PERSONA, premise=args.premise, title=title, outline=outline, story_text=story_draft, guidelines=GUIDELINES
        )
        response_history = interface.SafeGenerateText(sys_logger, [interface.BuildUserQuery(continuation_prompt)], model_with_params, min_word_count_target=500)
        continuation = interface.GetLastMessageText(response_history)
        story_draft += '\n\n' + continuation
        iteration_count += 1

    if iteration_count > args.max_iterations:
        sys_logger.Log(f"Reached max iterations ({args.max_iterations}). Story may be incomplete.", 6)

    sys_logger.Log("Story generation complete.", 5)

    # --- Step 4: Finalize and Save ---
    final_story = story_draft.replace('IAMDONE', '').strip()

    output_dir = os.path.join(project_root, "Short_Story")
    os.makedirs(output_dir, exist_ok=True)

    safe_title = sanitize_filename(title)
    output_filename = f"{safe_title}_{generation_timestamp}.md"
    output_path = os.path.join(output_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Premise:** {args.premise}\n\n")
            f.write(f"**Generated on:** {generation_timestamp}\n\n")
            f.write("---\n\n")
            f.write(f"## Outline\n\n{outline}\n\n")
            f.write("---\n\n")
            f.write(final_story)
        sys_logger.Log(f"Successfully saved short story to: {output_path}", 5)
    except Exception as e:
        sys_logger.Log(f"Error saving story to file: {e}", 7)

    print(f"\n--- Short Story Generation Complete. Find your story at: {output_path} ---")

if __name__ == "__main__":
    main()

```

## File: `Tools/Test.py`

```python
#!/usr/bin/python3

import os

# --- Configuration Definitions ---

# Define different sets of models for various testing scenarios.
# This makes it easy to add or change test configurations.
MODEL_CONFIGS = {
    "1": {
        "name": "Gemini 1.5 Flash (Writer) + Gemini 1.5 Pro (Editor)",
        "models": {
            "InitialOutlineModel": "google://gemini-1.5-pro-latest",
            "ChapterOutlineModel": "google://gemini-1.5-flash-latest",
            "ChapterS1Model": "google://gemini-1.5-flash-latest",
            "ChapterS2Model": "google://gemini-1.5-flash-latest",
            "ChapterS3Model": "google://gemini-1.5-flash-latest",
            "ChapterRevisionModel": "google://gemini-1.5-pro-latest",
            "RevisionModel": "google://gemini-1.5-pro-latest",
            "EvalModel": "google://gemini-1.5-flash-latest",
            "InfoModel": "google://gemini-1.5-flash-latest",
            "CritiqueLLM": "google://gemini-1.5-pro-latest",
        }
    },
    "2": {
        "name": "Full Gemini 1.5 Flash",
        "models": {
            "InitialOutlineModel": "google://gemini-1.5-flash-latest",
            "ChapterOutlineModel": "google://gemini-1.5-flash-latest",
            "ChapterS1Model": "google://gemini-1.5-flash-latest",
            "ChapterS2Model": "google://gemini-1.5-flash-latest",
            "ChapterS3Model": "google://gemini-1.5-flash-latest",
            "ChapterRevisionModel": "google://gemini-1.5-flash-latest",
            "RevisionModel": "google://gemini-1.5-flash-latest",
            "EvalModel": "google://gemini-1.5-flash-latest",
            "InfoModel": "google://gemini-1.5-flash-latest",
            "CritiqueLLM": "google://gemini-1.5-flash-latest",
        }
    },
    "3": {
        "name": "Full Gemini 1.5 Pro",
        "models": {
            "InitialOutlineModel": "google://gemini-1.5-pro-latest",
            "ChapterOutlineModel": "google://gemini-1.5-pro-latest",
            "ChapterS1Model": "google://gemini-1.5-pro-latest",
            "ChapterS2Model": "google://gemini-1.5-pro-latest",
            "ChapterS3Model": "google://gemini-1.5-pro-latest",
            "ChapterRevisionModel": "google://gemini-1.5-pro-latest",
            "RevisionModel": "google://gemini-1.5-pro-latest",
            "EvalModel": "google://gemini-1.5-pro-latest",
            "InfoModel": "google://gemini-1.5-pro-latest",
            "CritiqueLLM": "google://gemini-1.5-pro-latest",
        }
    },
    "4": {
        "name": "GroqCloud Mixtral (Fast)",
        "models": {
            "InitialOutlineModel": "groq://mixtral-8x7b-32768",
            "ChapterOutlineModel": "groq://mixtral-8x7b-32768",
            "ChapterS1Model": "groq://mixtral-8x7b-32768",
            "ChapterS2Model": "groq://mixtral-8x7b-32768",
            "ChapterS3Model": "groq://mixtral-8x7b-32768",
            "ChapterRevisionModel": "groq://gemma-7b-it", # Use a different model for revision
            "RevisionModel": "groq://gemma-7b-it",
            "EvalModel": "groq://gemma-7b-it",
            "InfoModel": "groq://mixtral-8x7b-32768",
            "CritiqueLLM": "groq://gemma-7b-it",
        }
    },
    "5": {
        "name": "Ollama Llama3 8B (Local Fast Debug)",
        "models": {
            "InitialOutlineModel": "ollama://llama3:8b",
            "ChapterOutlineModel": "ollama://llama3:8b",
            "ChapterS1Model": "ollama://llama3:8b",
            "ChapterS2Model": "ollama://llama3:8b",
            "ChapterS3Model": "ollama://llama3:8b",
            "ChapterRevisionModel": "ollama://llama3:8b",
            "RevisionModel": "ollama://llama3:8b",
            "EvalModel": "ollama://llama3:8b",
            "InfoModel": "ollama://llama3:8b",
            "CritiqueLLM": "ollama://llama3:8b",
        }
    },
    "6": {
        "name": "Ollama Llama3 70B (Local High Quality)",
        "models": {
            "InitialOutlineModel": "ollama://llama3:70b",
            "ChapterOutlineModel": "ollama://llama3:70b",
            "ChapterS1Model": "ollama://llama3:70b",
            "ChapterS2Model": "ollama://llama3:70b",
            "ChapterS3Model": "ollama://llama3:70b",
            "ChapterRevisionModel": "ollama://llama3:70b",
            "RevisionModel": "ollama://llama3:70b",
            "EvalModel": "ollama://llama3:70b",
            "InfoModel": "ollama://llama3:70b",
            "CritiqueLLM": "ollama://llama3:70b",
        }
    },
    "7": {
        "name": "NVIDIA Llama3 70B (Full Stack)",
        "models": {
            "InitialOutlineModel": "nvidia://meta/llama3-70b-instruct",
            "ChapterOutlineModel": "nvidia://meta/llama3-70b-instruct",
            "ChapterS1Model": "nvidia://meta/llama3-70b-instruct",
            "ChapterS2Model": "nvidia://meta/llama3-70b-instruct",
            "ChapterS3Model": "nvidia://meta/llama3-70b-instruct",
            "ChapterRevisionModel": "nvidia://meta/llama3-70b-instruct",
            "RevisionModel": "nvidia://meta/llama3-70b-instruct",
            "EvalModel": "nvidia://meta/llama3-70b-instruct",
            "InfoModel": "nvidia://meta/llama3-70b-instruct",
            "CritiqueLLM": "nvidia://meta/llama3-70b-instruct",
        }
    },
}

# --- User Input ---

print("Developer Testing Utility.")

# Get Choice For Model Configuration
print("\nChoose Model Configuration:")
print("-------------------------------------------")
for key, config in MODEL_CONFIGS.items():
    print(f"{key} -> {config['name']}")
print("-------------------------------------------")
choice = input("> ")

if choice not in MODEL_CONFIGS:
    print("Invalid selection. Exiting.")
    exit()

selected_config = MODEL_CONFIGS[choice]

# Get Choice For Prompt
# --- CORRECTED: Use `Prompts/` directory instead of non-existent `ExamplePrompts/` ---
print("\nChoose Prompt:")
print("-------------------------------------------")
# List available prompt directories dynamically
prompt_base_dir = "Prompts"
available_prompts = []
if os.path.isdir(prompt_base_dir):
    for item in sorted(os.listdir(prompt_base_dir)):
        item_path = os.path.join(prompt_base_dir, item)
        prompt_file = os.path.join(item_path, "prompt.txt")
        if os.path.isdir(item_path) and os.path.isfile(prompt_file):
            available_prompts.append(prompt_file)

if not available_prompts:
    print("No prompts found in the 'Prompts/' directory.")
    print("Please create one first using Tools/PromptGenerator.py")
    exit()

for i, p_file in enumerate(available_prompts):
    print(f"{i+1} -> {p_file}")
print("-------------------------------------------")
prompt_choice = input("> ")

prompt_file = ""
try:
    choice_index = int(prompt_choice) - 1
    if 0 <= choice_index < len(available_prompts):
        prompt_file = available_prompts[choice_index]
    else:
        print("Invalid prompt choice. Exiting.")
        exit()
except (ValueError, IndexError):
    print("Invalid selection. Exiting.")
    exit()


# Get Any Extra Flags
print("\nExtra Flags (e.g., -Debug -NoScrubChapters):")
print("Default = '-ExpandOutline'")
print("-------------------------------------------")
extra_flags = input("> ")

if extra_flags == "":
    extra_flags = "-ExpandOutline"


# --- Command Construction and Execution ---

# Build the base command
# Corrected to be run from the project root where Test.py is located
command_parts = [
    "python ./Write.py",
    f"-Prompt \"{prompt_file}\"", # Use quotes for paths with spaces
    "-Seed 999",  # Use a consistent seed for reproducibility
]

# Add model arguments from the selected configuration
for model_arg, model_name in selected_config['models'].items():
    command_parts.append(f"-{model_arg} \"{model_name}\"")

# Add extra flags
if extra_flags:
    command_parts.append(extra_flags)

# Join all parts into a single command string
final_command = " ".join(command_parts)

# Print the command to be executed for verification
print("\nExecuting command:")
print("-------------------------------------------")
print(final_command)
print("-------------------------------------------")

# Execute the command
os.system(final_command)

```

## File: `Tools/WebNovelChapterWriter.py`

```python
#!/usr/bin/python3
import argparse
import time
import datetime
import os
import sys
import json
import dotenv
import termcolor

# --- Explicitly load the .env file from the project root and add verbose logging ---
# This makes the script runnable from any directory and provides clear debug info.
print(termcolor.colored("--- Initializing Environment ---", "yellow"))
try:
    project_root = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(project_root, '.env')
    if os.path.exists(dotenv_path):
        dotenv.load_dotenv(dotenv_path=dotenv_path, verbose=True)
        print(termcolor.colored(f"[ENV] Attempted to load .env file from: {dotenv_path}", "cyan"))
        # Explicitly check for NVIDIA keys right after loading
        if os.environ.get("NVIDIA_API_KEY"):
            print(termcolor.colored("[ENV] NVIDIA_API_KEY: Found", "green"))
        else:
            print(termcolor.colored("[ENV] NVIDIA_API_KEY: NOT FOUND in environment", "red"))
        if os.environ.get("NVIDIA_BASE_URL"):
            print(termcolor.colored("[ENV] NVIDIA_BASE_URL: Found", "green"))
        else:
            print(termcolor.colored("[ENV] NVIDIA_BASE_URL: NOT FOUND in environment", "red"))
    else:
        print(termcolor.colored(f"[ENV] .env file not found at: {dotenv_path}", "red"))
except Exception as e:
    print(termcolor.colored(f"--- Error loading .env file: {e} ---", "red"))
print(termcolor.colored("--------------------------------", "yellow"))


import Writer.Config
import Writer.Interface.Wrapper
import Writer.PrintUtils
import Writer.Scrubber
import Writer.Statistics
import Writer.OutlineGenerator
import Writer.Chapter.ChapterGenerator
import Writer.StoryInfo
import Writer.NovelEditor
import Writer.Prompts
from Writer.NarrativeContext import NarrativeContext

def get_ollama_models(logger):
    try:
        import ollama
        logger.Log("Querying Ollama for local models...", 1)
        models_data = ollama.list().get("models", [])
        available_models = [f"ollama://{model.get('name') or model.get('model')}" for model in models_data if model.get('name') or model.get('model')]
        print(f"-> Ollama: Found {len(available_models)} models.")
        return available_models
    except Exception as e:
        logger.Log(f"Could not get Ollama models. (Error: {e})", 6)
        return []

def get_google_models(logger):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("-> Google: GOOGLE_API_KEY not found in .env file. Skipping.")
        return []
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        logger.Log("Querying Google for available Gemini models...", 1)
        available = [f"google://{m.name.replace('models/', '')}" for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"-> Google: Found {len(available)} models.")
        return available
    except Exception as e:
        logger.Log(f"Failed to query Google models. (Error: {e})", 6)
        return []

def get_groq_models(logger):
    if not os.environ.get("GROQ_API_KEY"):
        print("-> GroqCloud: GROQ_API_KEY not found in .env file. Skipping.")
        return []
    try:
        from groq import Groq
        logger.Log("Querying GroqCloud for available models...", 1)
        client = Groq()
        models = client.models.list().data
        print(f"-> GroqCloud: Found {len(models)} models.")
        return [f"groq://{model.id}" for model in models]
    except Exception as e:
        logger.Log(f"Failed to query GroqCloud models. (Error: {e})", 6)
        return []

def get_mistral_models(logger):
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("-> MistralAI: MISTRAL_API_KEY not found in .env file. Skipping.")
        return []
    try:
        from mistralai.client import MistralClient
        logger.Log("Querying MistralAI for available models...", 1)
        client = MistralClient(api_key=api_key)
        models_data = client.list_models().data
        known_chat_prefixes = ['mistral-large', 'mistral-medium', 'mistral-small', 'open-mistral', 'open-mixtral']
        available_models = [f"mistralai://{model.id}" for model in models_data if any(model.id.startswith(prefix) for prefix in known_chat_prefixes)]
        print(f"-> MistralAI: Found {len(available_models)} compatible models.")
        return available_models
    except Exception as e:
        logger.Log(f"Failed to query MistralAI models. (Error: {e})", 6)
        return []

def get_nvidia_models(logger):
    """Reads the user-defined NVIDIA models from config.ini."""
    if not os.environ.get("NVIDIA_API_KEY"):
        logger.Log("NVIDIA provider skipped: NVIDIA_API_KEY not found in environment.", 6)
        return []
    
    logger.Log("Reading manual NVIDIA model list from config.ini...", 1)
    model_list_str = Writer.Config.NVIDIA_AVAILABLE_MODELS
    if not model_list_str:
        logger.Log("NVIDIA provider skipped: No models listed in config.ini under [NVIDIA_SETTINGS] -> 'available_models'.", 6)
        return []
    
    model_names = [name.strip() for name in model_list_str.split(',') if name.strip()]
    available_models = [f"nvidia://{name}" for name in model_names]
    logger.Log(f"Found {len(available_models)} NVIDIA models in config.ini.", 3)
    return available_models

def get_github_models(logger):
    """Returns a static list of available GitHub models, checking for required env vars."""
    if not os.environ.get("GITHUB_ACCESS_TOKEN") or not os.environ.get("AZURE_OPENAI_ENDPOINT"):
        logger.Log("GitHub provider skipped: GITHUB_ACCESS_TOKEN or AZURE_OPENAI_ENDPOINT not found in environment.", 6)
        return []

    logger.Log("Loading GitHub model list...", 1)
    
    # Static list of the exact deployment names for models from the GitHub Marketplace.
    deployment_names = [
        "openai/o1", "openai/o1-mini", "openai/o1-preview", "openai/gpt-4o-mini", "openai/gpt-4o",
        "deepseek/DeepSeek-V3-0324", "deepseek/DeepSeek-R1",
        "ai21-labs/AI21-Jamba-1.5-Large", "ai21-labs/AI21-Jamba-1.5-Mini",
        "cohere/cohere-command-r", "cohere/cohere-command-r-plus", "cohere/cohere-command-a",
        "mistral-ai/Mistral-Nemo", "mistral-ai/Mistral-Small",
        "mistral-ai/Mistral-Large-2411", "mistral-ai/Codestral-22B-v0.1",
        "meta/Llama-3.2-11B-Vision-Instruct", "meta/Llama-3.2-90B-Vision-Instruct",
        "meta/Llama-3.3-70B-Instruct", "meta/Llama-3.1-8B-Instruct",
        "meta/Llama-3.1-70B-Instruct", "meta/Llama-3.1-405B-Instruct",
        "meta/Llama-3-8B-Instruct", "meta/Llama-3-70B-Instruct",
        "microsoft/Phi-4", "microsoft/Phi-3.5-MoE-instruct",
        "microsoft/Phi-3.5-mini-instruct", "microsoft/Phi-3.5-vision-instruct",
        "microsoft/Phi-3-mini-4k-instruct", "microsoft/Phi-3-mini-128k-instruct",
        "microsoft/Phi-3-small-8k-instruct", "microsoft/Phi-3-small-128k-instruct",
        "microsoft/Phi-3-medium-4k-instruct", "microsoft/Phi-3-medium-128k-instruct",
        "xai/grok-3",
        "core42/jais-30b-chat"
    ]
    
    available_models = [f"github://{name}" for name in deployment_names]
    logger.Log(f"Found {len(available_models)} GitHub models.", 3)
    return available_models

def get_llm_selection_menu_dynamic(logger):
    print("\n--- Querying available models from configured providers... ---")
    all_models = []
    all_models.extend(get_google_models(logger))
    all_models.extend(get_groq_models(logger))
    all_models.extend(get_mistral_models(logger))
    all_models.extend(get_nvidia_models(logger))
    all_models.extend(get_github_models(logger))
    all_models.extend(get_ollama_models(logger))
    if not all_models:
        logger.Log("No models found from any provider. Please check API keys in .env and model lists in config.ini.", 7)
        return {}
    print("\n--- Fiction Fabricator LLM Selection ---")
    print("Please select the primary model for writing:")
    sorted_models = sorted(all_models)
    for i, model in enumerate(sorted_models):
        print(f"[{i+1}] {model}")
    print("[c] Custom (use settings from config.ini or command-line args)")
    choice = input("> ").strip().lower()
    if choice.isdigit() and 1 <= int(choice) <= len(sorted_models):
        selected_model = sorted_models[int(choice) - 1]
        print(f"Selected: {selected_model}")
        return {'INITIAL_OUTLINE_WRITER_MODEL':selected_model, 'CHAPTER_OUTLINE_WRITER_MODEL':selected_model, 'CHAPTER_STAGE1_WRITER_MODEL':selected_model, 'CHAPTER_STAGE2_WRITER_MODEL':selected_model, 'CHAPTER_STAGE3_WRITER_MODEL':selected_model, 'CHAPTER_STAGE4_WRITER_MODEL':selected_model, 'CHAPTER_REVISION_WRITER_MODEL':selected_model, 'CRITIQUE_LLM':selected_model, 'REVISION_MODEL':selected_model, 'EVAL_MODEL':selected_model, 'INFO_MODEL':selected_model, 'SCRUB_MODEL':selected_model, 'CHECKER_MODEL':selected_model}
    else:
        print("Invalid choice or 'c' selected. Using custom/default configuration.")
        return {}

def main():
    Parser = argparse.ArgumentParser(description=f"Run the {Writer.Config.PROJECT_NAME} novel generation pipeline.")
    Parser.add_argument("-Prompt", required=True)
    Parser.add_argument("-Output", default="", type=str)
    Parser.add_argument("-Seed", default=Writer.Config.SEED, type=int)
    Parser.add_argument("-Debug", action="store_true", default=Writer.Config.DEBUG)
    Parser.add_argument("-InitialOutlineModel", default=Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterOutlineModel", default=Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS1Model", default=Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS2Model", default=Writer.Config.CHAPTER_STAGE2_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS3Model", default=Writer.Config.CHAPTER_STAGE3_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS4Model", default=Writer.Config.CHAPTER_STAGE4_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterRevisionModel", default=Writer.Config.CHAPTER_REVISION_WRITER_MODEL, type=str)
    Parser.add_argument("-CritiqueLLM", default=Writer.Config.CRITIQUE_LLM, type=str)
    Parser.add_argument("-RevisionModel", default=Writer.Config.REVISION_MODEL, type=str)
    Parser.add_argument("-EvalModel", default=Writer.Config.EVAL_MODEL, type=str)
    Parser.add_argument("-InfoModel", default=Writer.Config.INFO_MODEL, type=str)
    Parser.add_argument("-ScrubModel", default=Writer.Config.SCRUB_MODEL, type=str)
    Parser.add_argument("-CheckerModel", default=Writer.Config.CHECKER_MODEL, type=str)
    Parser.add_argument("-OutlineMinRevisions", default=Writer.Config.OUTLINE_MIN_REVISIONS, type=int)
    Parser.add_argument("-OutlineMaxRevisions", default=Writer.Config.OUTLINE_MAX_REVISIONS, type=int)
    Parser.add_argument("-ChapterMinRevisions", default=Writer.Config.CHAPTER_MIN_REVISIONS, type=int)
    Parser.add_argument("-ChapterMaxRevisions", default=Writer.Config.CHAPTER_MAX_REVISIONS, type=int)
    Parser.add_argument("-MinChapters", default=Writer.Config.MINIMUM_CHAPTERS, type=int)
    Parser.add_argument("-NoChapterRevision", action="store_true", default=Writer.Config.CHAPTER_NO_REVISIONS)
    Parser.add_argument("-NoScrubChapters", action="store_true", default=Writer.Config.SCRUB_NO_SCRUB)
    Parser.add_argument("-NoExpandOutline", action="store_false", dest="ExpandOutline", default=Writer.Config.EXPAND_OUTLINE)
    Parser.add_argument("-EnableFinalEditPass", action="store_true", default=Writer.Config.ENABLE_FINAL_EDIT_PASS)
    Parser.add_argument("-NoSceneGenerationPipeline", action="store_false", dest="SceneGenerationPipeline", default=Writer.Config.SCENE_GENERATION_PIPELINE)
    Args = Parser.parse_args()

    StartTime = time.time()
    SysLogger = Writer.PrintUtils.Logger()
    SysLogger.Log(f"Welcome to {Writer.Config.PROJECT_NAME}!", 2)

    selected_models = get_llm_selection_menu_dynamic(SysLogger)
    if not selected_models:
        SysLogger.Log("No model was selected or discovered. Using models from config/args.", 4)
    else:
        for key, value in selected_models.items():
            setattr(Writer.Config, key.upper(), value)

    for arg, value in vars(Args).items():
        if hasattr(Writer.Config, arg.upper()) and value != Parser.get_default(arg):
            setattr(Writer.Config, arg.upper(), value)

    Writer.Config.CHAPTER_NO_REVISIONS = Args.NoChapterRevision
    Writer.Config.SCRUB_NO_SCRUB = Args.NoScrubChapters
    Writer.Config.EXPAND_OUTLINE = Args.ExpandOutline
    Writer.Config.ENABLE_FINAL_EDIT_PASS = Args.EnableFinalEditPass
    Writer.Config.SCENE_GENERATION_PIPELINE = Args.SceneGenerationPipeline
    Writer.Config.DEBUG = Args.Debug
    Writer.Config.OPTIONAL_OUTPUT_NAME = Args.Output
    Writer.Config.MINIMUM_CHAPTERS = Args.MinChapters

    models_to_load = list(set([Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, Writer.Config.CHAPTER_STAGE2_WRITER_MODEL, Writer.Config.CHAPTER_STAGE3_WRITER_MODEL, Writer.Config.CHAPTER_STAGE4_WRITER_MODEL, Writer.Config.CHAPTER_REVISION_WRITER_MODEL, Writer.Config.CRITIQUE_LLM, Writer.Config.REVISION_MODEL, Writer.Config.EVAL_MODEL, Writer.Config.INFO_MODEL, Writer.Config.SCRUB_MODEL, Writer.Config.CHECKER_MODEL]))
    Interface = Writer.Interface.Wrapper.Interface(models_to_load)

    try:
        with open(Args.Prompt, "r", encoding='utf-8') as f:
            Prompt = f.read()
    except FileNotFoundError:
        SysLogger.Log(f"Error: Prompt file not found at {Args.Prompt}", 7)
        return

    # CORRECTED LINE: Pass the style_guide from Prompts.py during initialization.
    narrative_context = NarrativeContext(initial_prompt=Prompt, style_guide=Writer.Prompts.LITERARY_STYLE_GUIDE)
    narrative_context = Writer.OutlineGenerator.GenerateOutline(Interface, SysLogger, Prompt, narrative_context)
    SysLogger.Log("Starting Chapter Writing phase...", 2)
    total_chapters = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, SysLogger, narrative_context.base_novel_outline_markdown)
    if total_chapters > 0 and total_chapters < 100:
        for i in range(1, total_chapters + 1):
            Writer.Chapter.ChapterGenerator.GenerateChapter(Interface, SysLogger, i, total_chapters, narrative_context)
    else:
        SysLogger.Log(f"Invalid chapter count ({total_chapters}) detected. Aborting chapter generation.", 7)

    if Writer.Config.ENABLE_FINAL_EDIT_PASS:
        narrative_context = Writer.NovelEditor.EditNovel(Interface, SysLogger, narrative_context)
    if not Writer.Config.SCRUB_NO_SCRUB:
        narrative_context = Writer.Scrubber.ScrubNovel(Interface, SysLogger, narrative_context)
    else:
        SysLogger.Log("Skipping final scrubbing pass due to config.", 4)

    StoryBodyText = "\n\n\n".join([f"### Chapter {chap.chapter_number}\n\n{chap.generated_content}" for chap in narrative_context.chapters if chap.generated_content])
    
    info_messages = [Interface.BuildUserQuery(narrative_context.base_novel_outline_markdown)]
    Info = Writer.StoryInfo.GetStoryInfo(Interface, SysLogger, info_messages)
    Title = Info.get("Title", "Untitled Story")

    SysLogger.Log(f"Story Title: {Title}", 5)
    SysLogger.Log(f"Summary: {Info.get('Summary', 'N/A')}", 3)
    ElapsedTime = time.time() - StartTime
    TotalWords = Writer.Statistics.GetWordCount(StoryBodyText)
    SysLogger.Log(f"Total story word count: {TotalWords}", 4)

    StatsString = f"""
## Work Statistics
- **Title**: {Title}
- **Summary**: {Info.get('Summary', 'N/A')}
- **Tags**: {Info.get('Tags', 'N/A')}
- **Generation Time**: {ElapsedTime:.2f}s
- **Average WPM**: {60 * (TotalWords / ElapsedTime) if ElapsedTime > 0 else 0:.2f}
- **Generator**: {Writer.Config.PROJECT_NAME}

## Generation Settings
- **Base Prompt**: {Prompt[:150]}...
- **Seed**: {Writer.Config.SEED}
- **Primary Model Used**: {Writer.Config.INITIAL_OUTLINE_WRITER_MODEL} (and others if set by args)
"""

    os.makedirs("Stories", exist_ok=True)
    safe_title = "".join(c for c in Title if c.isalnum() or c in (' ', '_')).rstrip()
    file_name_base = f"Stories/{safe_title.replace(' ', '_')}"
    if Writer.Config.OPTIONAL_OUTPUT_NAME:
        file_name_base = f"Stories/{Writer.Config.OPTIONAL_OUTPUT_NAME}"
    
    md_file_path = f"{file_name_base}.md"
    json_file_path = f"{file_name_base}.json"

    # Write the Markdown file
    with open(md_file_path, "w", encoding="utf-8") as f:
        output_content = f"# {Title}\n\n{StoryBodyText}\n\n---\n\n{StatsString}\n\n---\n\n## Full Outline\n```\n{narrative_context.base_novel_outline_markdown}\n```"
        f.write(output_content)

    # Write the JSON file
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(narrative_context.to_dict(), f, indent=4)
    
    # Log the final, correct output paths
    SysLogger.Log("Generation complete!", 5)
    final_message = f"""
--------------------------------------------------
Output Files Saved:
- Markdown Story: {os.path.abspath(md_file_path)}
- JSON Data File: {os.path.abspath(json_file_path)}
--------------------------------------------------"""
    print(termcolor.colored(final_message, "green"))


if __name__ == "__main__":
    main()

```

## File: `Writer/Chapter/ChapterDetector.py`

```python
#!/usr/bin/python3

import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def LLMCountChapters(Interface: Interface, _Logger: Logger, _Summary: str) -> int:
    """
    Counts the number of chapters in a given story outline using an LLM.
    This is a non-creative, JSON-focused task with a built-in retry mechanism.
    """
    prompt = Writer.Prompts.CHAPTER_COUNT_PROMPT.format(_Summary=_Summary)
    messages = [Interface.BuildUserQuery(prompt)]

    max_retries = 3
    for attempt in range(max_retries):
        _Logger.Log(f"Attempting to get chapter count (Attempt {attempt + 1}/{max_retries})...", 5)

        _, response_json = Interface.SafeGenerateJSON(
            _Logger,
            messages,
            Writer.Config.EVAL_MODEL,
            _RequiredAttribs=["TotalChapters"]
        )

        if not response_json:
             _Logger.Log("LLMCountChapters failed to get a JSON response. Retrying...", 6)
             continue

        try:
            total_chapters = int(response_json.get("TotalChapters", -1))
            # A valid chapter count should be a reasonable positive number.
            if total_chapters > 0 and total_chapters < 100:
                _Logger.Log(f"LLM detected {total_chapters} chapters.", 5)
                return total_chapters
            else:
                _Logger.Log(f"LLM returned an invalid or unreasonable chapter count: {total_chapters}. Retrying...", 7)

        except (ValueError, TypeError) as e:
            _Logger.Log(f"Could not parse 'TotalChapters'. Error: {e}. Retrying...", 7)

    _Logger.Log(f"CRITICAL: Failed to determine chapter count after {max_retries} attempts.", 7)
    return -1

```

## File: `Writer/Chapter/ChapterGenSummaryCheck.py`

```python
#!/usr/bin/python3

import json
import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def LLMSummaryCheck(Interface: Interface, _Logger: Logger, _RefSummary: str, _Work: str) -> (bool, str):
    """
    Generates a summary of the work provided, compares that to the reference summary (outline),
    and asks if the work correctly followed the prompt. This is a validation step, not a creative one.
    """
    # A simple guard against empty or near-empty responses.
    if len(_Work.split()) < 100:
        _Logger.Log(
            "Check failed: Generated work didn't meet the length requirement (100 words), so it likely failed to generate properly.",
            7,
        )
        return False, "The generated text was too short. Please write a full, detailed response."

    # --- Step 1: Summarize the generated work ---
    _Logger.Log("Summarizing the generated work for comparison...", 3)
    SummaryWorkMessages = [
        Interface.BuildUserQuery(Writer.Prompts.SUMMARY_CHECK_PROMPT.format(_Work=_Work))
    ]
    SummaryWorkHistory = Interface.SafeGenerateText(
        _Logger, SummaryWorkMessages, Writer.Config.CHECKER_MODEL, min_word_count_target=30
    )
    WorkSummary = Interface.GetLastMessageText(SummaryWorkHistory)

    # Robustness Check
    if not WorkSummary.strip() or "[ERROR:" in WorkSummary:
        _Logger.Log("Check failed: Could not generate a summary of the provided work.", 7)
        return False, "Failed to generate a summary of the work for validation."


    # --- Step 2: Summarize the reference outline ---
    _Logger.Log("Summarizing the reference outline for comparison...", 3)
    SummaryOutlineMessages = [
        Interface.BuildUserQuery(Writer.Prompts.SUMMARY_OUTLINE_PROMPT.format(_RefSummary=_RefSummary))
    ]
    SummaryOutlineHistory = Interface.SafeGenerateText(
        _Logger, SummaryOutlineMessages, Writer.Config.CHECKER_MODEL, min_word_count_target=30
    )
    OutlineSummary = Interface.GetLastMessageText(SummaryOutlineHistory)

    # Robustness Check
    if not OutlineSummary.strip() or "[ERROR:" in OutlineSummary:
        _Logger.Log("Check failed: Could not generate a summary of the reference outline.", 7)
        return False, "Failed to generate a summary of the reference outline for validation."


    # --- Step 3: Generate a JSON comparison ---
    _Logger.Log("Comparing summaries to check for outline adherence...", 3)
    ComparisonMessages = [
        Interface.BuildUserQuery(
            Writer.Prompts.SUMMARY_COMPARE_PROMPT.format(
                WorkSummary=WorkSummary, OutlineSummary=OutlineSummary
            )
        )
    ]

    # This is a non-creative, JSON-focused task.
    _, ResponseJSON = Interface.SafeGenerateJSON(
        _Logger,
        ComparisonMessages,
        Writer.Config.EVAL_MODEL, # Use the EVAL_MODEL for this check
        _RequiredAttribs=["DidFollowOutline", "Suggestions"]
    )

    if not ResponseJSON:
        _Logger.Log("Check failed: Could not get a valid JSON comparison from the LLM.", 7)
        return False, "Failed to get a valid comparison from the evaluator model."

    did_follow = ResponseJSON.get("DidFollowOutline", False)
    suggestions = ResponseJSON.get("Suggestions", "")

    # Ensure the output format is correct for the calling function
    if isinstance(did_follow, str):
        did_follow = did_follow.lower() == 'true'

    feedback_string = f"### Adherence Check Feedback:\n{suggestions}" if suggestions else ""

    _Logger.Log(f"Outline Adherence Check Result: {did_follow}", 4)

    return did_follow, feedback_string

```

## File: `Writer/Chapter/ChapterGenerator.py`

```python
#!/usr/bin/python3

import re
import Writer.Config
import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Prompts
import Writer.Scene.ChapterByScene
import Writer.SummarizationUtils
import Writer.CritiqueRevision
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext, ChapterContext
from Writer.PrintUtils import Logger


def GenerateChapter(
    Interface: Interface,
    _Logger: Logger,
    _ChapterNum: int,
    _TotalChapters: int,
    narrative_context: NarrativeContext,
) -> str:
    """
    Generates a single chapter of the novel, either through a multi-stage process or
    a scene-by-scene pipeline, and ensures it is coherent with the story so far.
    """

    # --- Step 1: Setup Chapter Context ---
    _Logger.Log(f"Setting up context for Chapter {_ChapterNum} generation.", 2)

    # Determine which outline to use for this chapter
    chapter_specific_outline = ""
    if narrative_context.expanded_novel_outline_markdown:
        # Try to extract the specific chapter outline from the expanded outline
        search_str = f"# Chapter {_ChapterNum}"
        parts = narrative_context.expanded_novel_outline_markdown.split(search_str)
        if len(parts) > 1:
            chapter_specific_outline = parts[1].split("# Chapter ")[0].strip()
        else:
            _Logger.Log(f"Could not find specific outline for Chapter {_ChapterNum} in expanded outline.", 6)
            # Fallback to LLM extraction
            messages = [Interface.BuildUserQuery(Writer.Prompts.CHAPTER_GENERATION_PROMPT.format(_Outline=narrative_context.base_novel_outline_markdown, _ChapterNum=_ChapterNum))]
            messages = Interface.SafeGenerateText(_Logger, messages, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, min_word_count_target=50)
            chapter_specific_outline = Interface.GetLastMessageText(messages)
    else:
        # Fallback to extracting from the base outline
        messages = [Interface.BuildUserQuery(Writer.Prompts.CHAPTER_GENERATION_PROMPT.format(_Outline=narrative_context.base_novel_outline_markdown, _ChapterNum=_ChapterNum))]
        messages = Interface.SafeGenerateText(_Logger, messages, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, min_word_count_target=50)
        chapter_specific_outline = Interface.GetLastMessageText(messages)

    if not chapter_specific_outline:
        _Logger.Log(f"CRITICAL: Could not generate or find an outline for Chapter {_ChapterNum}. Aborting.", 7)
        return f"// ERROR: Failed to obtain outline for Chapter {_ChapterNum}. //"

    chapter_context = ChapterContext(chapter_number=_ChapterNum, initial_outline=chapter_specific_outline)
    _Logger.Log(f"Created Chapter Context for Chapter {_ChapterNum}", 3)


    # --- Step 2: Generate Initial Chapter Draft ---

    if Writer.Config.SCENE_GENERATION_PIPELINE:
        # Use the Scene-by-Scene pipeline for the initial draft
        _Logger.Log(f"Using Scene-by-Scene pipeline for Chapter {_ChapterNum}.", 3)
        initial_chapter_draft = Writer.Scene.ChapterByScene.ChapterByScene(
            Interface, _Logger, chapter_context, narrative_context
        )
    else:
        # Use the multi-stage generation pipeline for the initial draft
        _Logger.Log(f"Using Multi-Stage pipeline for Chapter {_ChapterNum}.", 3)

        # STAGE 1: Plot
        plot_text = execute_generation_stage(
            Interface, _Logger, "Plot Generation",
            Writer.Prompts.CHAPTER_GENERATION_STAGE1,
            {"ThisChapterOutline": chapter_specific_outline, "Feedback": ""},
            _ChapterNum, _TotalChapters,
            Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
            narrative_context
        )

        # STAGE 2: Character Development
        char_dev_text = execute_generation_stage(
            Interface, _Logger, "Character Development",
            Writer.Prompts.CHAPTER_GENERATION_STAGE2,
            {"ThisChapterOutline": chapter_specific_outline, "Stage1Chapter": plot_text, "Feedback": ""},
            _ChapterNum, _TotalChapters,
            Writer.Config.CHAPTER_STAGE2_WRITER_MODEL,
            narrative_context
        )

        # STAGE 3: Dialogue
        dialogue_text = execute_generation_stage(
            Interface, _Logger, "Dialogue Addition",
            Writer.Prompts.CHAPTER_GENERATION_STAGE3,
            {"ThisChapterOutline": chapter_specific_outline, "Stage2Chapter": char_dev_text, "Feedback": ""},
            _ChapterNum, _TotalChapters,
            Writer.Config.CHAPTER_STAGE3_WRITER_MODEL,
            narrative_context
        )
        initial_chapter_draft = dialogue_text

    _Logger.Log(f"Initial draft for Chapter {_ChapterNum} completed.", 4)

    # --- Step 3: Revision Cycle ---

    if Writer.Config.CHAPTER_NO_REVISIONS:
        _Logger.Log("Chapter revision disabled in config. Skipping revision loop.", 4)
        final_chapter_text = initial_chapter_draft
    else:
        _Logger.Log(f"Entering feedback/revision loop for Chapter {_ChapterNum}.", 4)
        current_chapter_text = initial_chapter_draft
        iterations = 0
        while True:
            iterations += 1

            is_complete = Writer.LLMEditor.GetChapterRating(Interface, _Logger, current_chapter_text)

            if iterations > Writer.Config.CHAPTER_MAX_REVISIONS:
                _Logger.Log("Max revisions reached. Exiting.", 6)
                break
            if iterations > Writer.Config.CHAPTER_MIN_REVISIONS and is_complete:
                _Logger.Log("Chapter meets quality standards. Exiting.", 5)
                break

            _Logger.Log(f"Chapter Revision Iteration {iterations}", 4)

            feedback = Writer.LLMEditor.GetFeedbackOnChapter(
                Interface, _Logger, current_chapter_text, narrative_context.base_novel_outline_markdown
            )

            _Logger.Log("Revising chapter based on feedback...", 2)
            revision_prompt = Writer.Prompts.CHAPTER_REVISION.format(
                _Chapter=current_chapter_text, _Feedback=feedback
            )
            revision_messages = [
                Interface.BuildSystemQuery(Writer.Prompts.LITERARY_STYLE_GUIDE),
                Interface.BuildUserQuery(revision_prompt)
            ]

            # Use robust word count and a high floor for revisions
            word_count = len(re.findall(r'\b\w+\b', current_chapter_text))
            min_word_count_target = max(150, int(word_count * 0.8))

            revision_messages = Interface.SafeGenerateText(
                _Logger, revision_messages, Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
                min_word_count_target=min_word_count_target
            )
            current_chapter_text = Interface.GetLastMessageText(revision_messages)
            _Logger.Log("Done revising chapter.", 2)

        final_chapter_text = current_chapter_text
        _Logger.Log(f"Exited revision loop for Chapter {_ChapterNum}.", 4)

    # --- Step 4: Finalize and Update Context ---

    chapter_context.set_generated_content(final_chapter_text)

    chapter_summary = Writer.SummarizationUtils.summarize_chapter(
        Interface, _Logger, final_chapter_text, narrative_context, _ChapterNum
    )
    chapter_context.set_summary(chapter_summary)
    _Logger.Log(f"Chapter {chapter_context.chapter_number} Summary: {chapter_context.summary}", 2)

    narrative_context.add_chapter(chapter_context)

    return final_chapter_text


def execute_generation_stage(
    Interface: Interface,
    _Logger: Logger,
    stage_name: str,
    prompt_template: str,
    format_args: dict,
    chapter_num: int,
    total_chapters: int,
    model: str,
    narrative_context: NarrativeContext,
) -> str:
    """
    Executes a single stage of the multi-stage chapter generation process,
    including a critique and revision cycle.
    """
    _Logger.Log(f"Executing Stage: {stage_name} for Chapter {chapter_num}", 5)

    # --- Initial Generation ---
    _Logger.Log(f"Generating initial content for {stage_name}...", 3)
    
    narrative_context_str = narrative_context.get_context_for_chapter_generation(chapter_num)

    full_format_args = {
        "narrative_context": narrative_context_str,
        "_ChapterNum": chapter_num,
        "_TotalChapters": total_chapters,
        **format_args
    }
    prompt = prompt_template.format(**full_format_args)
    messages = [
        Interface.BuildSystemQuery(Writer.Prompts.LITERARY_STYLE_GUIDE),
        Interface.BuildUserQuery(prompt)
    ]

    # Set minimum word count with a high floor to prevent cascading failures
    min_words = 200  # Default for Stage 1 (Plot)
    if "Stage2Chapter" in format_args: # Stage 3 (Dialogue)
        word_count = len(re.findall(r'\b\w+\b', format_args["Stage2Chapter"]))
        min_words = max(250, int(word_count * 0.95))
    elif "Stage1Chapter" in format_args: # Stage 2 (Char Dev)
        word_count = len(re.findall(r'\b\w+\b', format_args["Stage1Chapter"]))
        min_words = max(250, int(word_count * 0.95))

    messages = Interface.SafeGenerateText(
        _Logger, messages, model, min_word_count_target=min_words
    )
    initial_content = Interface.GetLastMessageText(messages)

    # --- Critique and Revise ---
    _Logger.Log(f"Critiquing and revising content for {stage_name}...", 3)

    task_description = f"You are writing a novel. Your current task is '{stage_name}' for Chapter {chapter_num}. You need to generate content that fulfills this stage's specific goal (e.g., plot, character development, dialogue) while remaining coherent with the overall story and adhering to a dark, literary style."

    revised_content = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_content,
        task_description=task_description,
        narrative_context_summary=narrative_context_str,
        initial_user_prompt=narrative_context.initial_prompt,
        style_guide=narrative_context.style_guide,
    )

    _Logger.Log(f"Finished stage: {stage_name}", 5)
    return revised_content

```

## File: `Writer/Interface/OpenRouter.py`

```python
import json, requests, time
from typing import Any, List, Mapping, Optional, Literal, Union, TypedDict

class OpenRouter:
    """OpenRouter.
    https://openrouter.ai/docs#models
    https://openrouter.ai/docs#llm-parameters
    """

    Message_Type = TypedDict('Message', { 'role': Literal['user', 'assistant', 'system', 'tool'], 'content': str })
    ProviderPreferences_Type = TypedDict(
        'ProviderPreferences', {
            'allow_fallbacks': Optional[bool],
            'require_parameters': Optional[bool],
            'data_collection': Union[Literal['deny'], Literal['allow'], None],
            'order': Optional[List[Literal[
                'OpenAI', 'Anthropic', 'HuggingFace', 'Google', 'Together', 'DeepInfra', 'Azure', 'Modal',
                'AnyScale', 'Replicate', 'Perplexity', 'Recursal', 'Fireworks', 'Mistral', 'Groq', 'Cohere',
                'Lepton', 'OctoAI', 'Novita', 'DeepSeek', 'Infermatic', 'AI21', 'Featherless', 'Mancer',
                'Mancer 2', 'Lynn 2', 'Lynn'
            ]]]
        }, total=False
    )

    def __init__(self,
        api_key: str,
        provider: Optional[ProviderPreferences_Type] | None = None,
        model: str = "microsoft/wizardlm-2-7b",
        max_tokens: int = 0,
        temperature: Optional[float] | None = 1.0,
        top_k: Optional[int] | None = 0.0,
        top_p: Optional[float] = 1.0,
        presence_penalty: Optional[float] = 0.0,
        frequency_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = 1.0,
        min_p: Optional[float] = 0.0,
        top_a: Optional[float] = 0.0,
        seed: Optional[int] | None = None,
        logit_bias: Optional[Mapping[int, int]] | None = None,
        response_format: Optional[Mapping[str, str]] | None = None,
        stop: Optional[Mapping[str, str]] | None = None,
        set_p50: bool = False,
        set_p90: bool = False,
        api_url: str = "https://openrouter.ai/api/v1/chat/completions",
        timeout: int = 3600,
        ):

        self.api_url = api_url
        self.api_key = api_key
        self.provider = provider
        self.model = model
        self.max_tokens = max_tokens
        self.seed = seed
        self.logit_bias = logit_bias
        self.response_format = response_format
        self.stop = stop
        self.timeout = timeout

        # Get the top LLM sampling parameter configurations used by users on OpenRouter.
        # https://openrouter.ai/docs/parameters-api
        if (set_p90 or set_p50):
            parameters_url = f'https://openrouter.ai/api/v1/parameters/{self.model}'
            headers = {
                'accept': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            params = requests.get(parameters_url, headers=headers).json()["data"]
            # I am so sorry
            self.temperature = params["temperature_p50"] if set_p50 else params["temperature_p90"]
            self.top_k = params["top_k_p50"] if set_p50 else params["top_k_p90"]
            self.top_p = params["top_p_p50"] if set_p50 else params["top_p_p90"]
            self.presence_penalty = params["presence_penalty_p50"] if set_p50 else params["presence_penalty_p90"]
            self.frequency_penalty = params["frequency_penalty_p50"] if set_p50 else params["frequency_penalty_p90"]
            self.repetition_penalty = params["repetition_penalty_p50"] if set_p50 else params["repetition_penalty_p90"]
            self.min_p = params["min_p_p50"] if set_p50 else params["min_p_p90"]
            self.top_a = params["top_a_p50"] if set_p50 else params["top_a_p90"]
        else: 
            self.temperature = temperature 
            self.top_k = top_k 
            self.top_p = top_p 
            self.presence_penalty = presence_penalty 
            self.frequency_penalty = frequency_penalty 
            self.repetition_penalty = repetition_penalty 
            self.min_p = min_p 
            self.top_a = top_a 

    def set_params(self,
        max_tokens: Optional[int] | None = None,
        presence_penalty: Optional[float] | None = None,
        frequency_penalty: Optional[float] | None = None,
        repetition_penalty: Optional[float] | None = None,
        response_format: Optional[Mapping[str, str]] | None = None,
        temperature: Optional[float] | None = None,
        seed: Optional[int] | None = None,
        top_k: Optional[int] | None = None,
        top_p: Optional[float] | None = None,
        min_p: Optional[float] | None = None,
        top_a: Optional[float] | None = None,
        ):

        if max_tokens is not None: self.max_tokens = max_tokens
        if presence_penalty is not None: self.presence_penalty = presence_penalty
        if frequency_penalty is not None: self.frequency_penalty = frequency_penalty
        if repetition_penalty is not None: self.repetition_penalty = repetition_penalty
        if response_format is not None: self.response_format = response_format
        if temperature is not None: self.temperature = temperature
        if seed is not None: self.seed = seed
        if top_k is not None: self.top_k = top_k
        if top_p is not None: self.top_p = top_p
        if min_p is not None: self.min_p = min_p
        if top_a is not None: self.top_a = top_a
    def ensure_array(self,
            input_msg: List[Message_Type] | Message_Type
        ) -> List[Message_Type]:
        if isinstance(input_msg, (list, tuple)):
            return input_msg
        else:
            return [input_msg]

    def chat(self,
            messages: Message_Type,
            max_retries: int = 10,
            seed: int = None
    ):
        messages = self.ensure_array(messages)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            'HTTP-Referer': 'https://github.com/datacrystals/AIStoryWriter',
            'X-Title': 'StoryForgeAI',
        }
        body={
            "model": self.model,
            "messages": messages,
            "max_token": self.max_tokens,
            "temperature": self.temperature,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
            "repetition_penalty": self.repetition_penalty,
            "min_p": self.min_p,
            "top_a": self.top_a,
            "seed": self.seed if seed is None else seed,
            "logit_bias": self.logit_bias,
            "response_format": self.response_format,
            "stop": self.stop,
            "provider": self.provider,
            "stream": False,
        }

        retries = 0
        while retries < max_retries:
            try:
                response = requests.post(url=self.api_url, headers=headers, data=json.dumps(body), timeout=self.timeout, stream=False)
                response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
                if 'choices' in response.json():
                    # Return result from request
                    return response.json()["choices"][0]["message"]["content"]
                elif 'error' in response.json():
                    print(f"Openrouter returns error '{response.json()['error']['code']}' with message '{response.json()['error']['message']}', retry attempt {retries + 1}.")
                    if response.json()['error']['code'] == 400:
                        print("Bad Request (invalid or missing params, CORS)")
                    if response.json()['error']['code'] == 401:
                        raise Exception ("Invalid credentials (OAuth session expired, disabled/invalid API key)")
                    if response.json()['error']['code'] == 402:
                        raise Exception ("Your account or API key has insufficient credits. Add more credits and retry the request.")   
                    if response.json()['error']['code'] == 403:
                        print("Your chosen model requires moderation and your input was flagged")
                    if response.json()['error']['code'] == 408:
                        print("Your request timed out")
                    if response.json()['error']['code'] == 429:
                        print("You are being rate limited")
                        print("Waiting 10 seconds")
                        time.sleep(10)
                    if response.json()['error']['code'] == 502:
                        print("Your chosen model is down or we received an invalid response from it")
                    if response.json()['error']['code'] == 503:
                        print("There is no available model provider that meets your routing requirements")
                else:
                    from pprint import pprint
                    print(f"Response without error but missing choices, retry attempt {retries + 1}.")
                    pprint(response.json())
            except requests.exceptions.HTTPError as http_err:
                # HTTP error status code
                print(f"HTTP error occurred: '{http_err}' - Status Code: '{http_err.response.status_code}', retry attempt {retries + 1}.")
                # Funny Cloudflare being funny.
                # This is a lie: https://community.cloudflare.com/t/community-tip-fixing-error-524-a-timeout-occurred/42342
                if http_err.response.status_code == 524:
                    time.sleep(10)
            except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as err:
                # timeouts and redirects
                print(f"Retry attempt {retries + 1} after error: '{err}'")
            except requests.exceptions.RequestException as req_err:
                # any other request errors that haven't been caught by the previous except blocks
                print(f"An error occurred while making the request: '{req_err}', retry attempt {retries + 1}.")
            except Exception as e:
                # all other exceptions
                print(f"An unexpected error occurred: '{e}', retry attempt {retries + 1}.")
            retries += 1

```

## File: `Writer/Interface/Wrapper.py`

```python
#!/usr/bin/python3

import os
import time
import json
import random
import platform
import re
import signal
from urllib.parse import parse_qs, urlparse

# Import Prompts to access the new JSON_PARSE_ERROR template
import Writer.Config
import Writer.Prompts
from Writer.PrintUtils import Logger

# --- Langchain Provider Imports ---
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_models import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_groq import ChatGroq
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import AzureChatOpenAI, ChatOpenAI

# Whitelist of supported bindable parameters for each provider to prevent 422 errors.
SAFE_PARAMS = {
    "google": ["temperature", "top_p", "top_k", "max_output_tokens", "seed", "response_mime_type"],
    "groq": ["temperature", "top_p", "max_tokens", "seed"],
    "nvidia": ["temperature", "top_p", "max_tokens", "seed"],
    "github": ["temperature", "top_p", "max_tokens"],
    "ollama": ["temperature", "top_p", "top_k", "seed", "format", "num_predict"],
    "mistralai": ["temperature", "top_p", "max_tokens"]
}


class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

class Interface:

    def __init__(self, Models: list = []):
        self.Clients: dict = {}
        self.History: list = []
        self.LoadModels(Models)

    def GetModelAndProvider(self, _Model: str) -> (str, str, str, dict):
        """
        Parses a model string like 'Provider://Model@Host?param1=val1' using robust string splitting.
        """
        if "://" not in _Model:
            return "ollama", _Model, "localhost:11434", {}

        parsed_url = urlparse(_Model)
        provider = parsed_url.scheme
        model_part = parsed_url.netloc + parsed_url.path
        
        provider_model = model_part
        host = None
        if "@" in model_part:
            provider_model, host = model_part.split("@", 1)

        if provider == 'ollama' and not host:
            host = 'localhost:11434'

        flat_params = {}
        if parsed_url.query:
            for key, values in parse_qs(parsed_url.query).items():
                val = values[0]
                try:
                    if val.isdigit() and '.' not in val:
                        flat_params[key] = int(val)
                    else:
                        flat_params[key] = float(val)
                except ValueError:
                    if val.lower() in ['true', 'false']:
                        flat_params[key] = val.lower() == 'true'
                    else:
                        flat_params[key] = val

        return provider, provider_model, host, flat_params


    def LoadModels(self, Models: list):
        _Logger = Logger()
        for Model in list(set(Models)): # Use set to avoid redundant loads
            base_model_uri = Model.split('?')[0]
            if base_model_uri in self.Clients:
                continue

            Provider, ProviderModel, ModelHost, ModelOptions = self.GetModelAndProvider(Model)
            _Logger.Log(f"Verifying config for Model '{ProviderModel}' from '{Provider}'", 2)
            try:
                if Provider == "ollama":
                    self.Clients[base_model_uri] = ChatOllama(model=ProviderModel, base_url=f"http://{ModelHost}" if ModelHost else "http://localhost:11434")
                elif Provider == "google":
                    self.Clients[base_model_uri] = ChatGoogleGenerativeAI(model=ProviderModel, convert_system_message_to_human=True)
                elif Provider == "mistralai":
                    self.Clients[base_model_uri] = ChatMistralAI(model=ProviderModel)
                elif Provider == "groq":
                    self.Clients[base_model_uri] = ChatGroq(model_name=ProviderModel)
                elif Provider == "nvidia":
                     self.Clients[base_model_uri] = ChatNVIDIA(model=ProviderModel, base_url=os.environ.get("NVIDIA_BASE_URL") or Writer.Config.NVIDIA_BASE_URL)
                elif Provider == "github":
                    if not os.environ.get("GITHUB_ACCESS_TOKEN") or not os.environ.get("AZURE_OPENAI_ENDPOINT"):
                        raise ValueError("GITHUB_ACCESS_TOKEN or AZURE_OPENAI_ENDPOINT not in environment variables.")
                    self.Clients[base_model_uri] = "GITHUB_PLACEHOLDER"
                else:
                    raise ValueError(f"Model Provider '{Provider}' for '{Model}' is not supported.")

                _Logger.Log(f"Successfully verified config for '{base_model_uri}'.", 3)
            except Exception as e:
                _Logger.Log(f"CRITICAL: Failed to load config for model '{Model}'. Error: {e}", 7)

    def SafeGenerateText(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _Format: str = None, min_word_count_target: int = 50) -> list:
        _Messages = [msg for msg in _Messages if msg.get("content", "").strip()]
        max_tokens_override = int(min_word_count_target * 5)
        NewMsgHistory = self.ChatAndStreamResponse(_Logger, _Messages, _Model, _SeedOverride, _Format, max_tokens_override=max_tokens_override)
        last_response_text = self.GetLastMessageText(NewMsgHistory)
        word_count = len(re.findall(r'\b\w+\b', last_response_text))

        if not last_response_text.strip() or word_count < min_word_count_target or "[ERROR:" in last_response_text:
            log_reason = "empty response" if not last_response_text.strip() else "error in response" if "[ERROR:" in last_response_text else f"response too short ({word_count} words, target: {min_word_count_target})"
            _Logger.Log(f"SafeGenerateText: Generation failed ({log_reason}). Forcing a retry...", 7)

            if NewMsgHistory and NewMsgHistory[-1].get("role") == "assistant":
                NewMsgHistory.pop()

            forceful_retry_prompt = f"The previous response was insufficient. You MUST generate a detailed and comprehensive response of AT LEAST {min_word_count_target} words. Do not stop writing until you have met this requirement. Fulfill the original request completely and at the required length."
            NewMsgHistory.append(self.BuildUserQuery(forceful_retry_prompt))

            max_tokens_override_retry = int(min_word_count_target * 8)
            NewMsgHistory = self.ChatAndStreamResponse(_Logger, NewMsgHistory, _Model, random.randint(0, 99999), _Format, max_tokens_override=max_tokens_override_retry)

        return NewMsgHistory

    def SafeGenerateJSON(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _RequiredAttribs: list = [], _MaxRetries: int = 3) -> (list, dict):
        max_tokens_override = 8192
        messages_copy = list(_Messages)
        for attempt in range(_MaxRetries):
            current_seed = _SeedOverride if _SeedOverride != -1 and attempt == 0 else random.randint(0, 99999)
            ResponseHistory = self.ChatAndStreamResponse(_Logger, messages_copy, _Model, current_seed, _Format="json", max_tokens_override=max_tokens_override)
            RawResponse = self.GetLastMessageText(ResponseHistory)
            try:
                if '```json' in RawResponse:
                    json_text_match = re.search(r'```json\s*([\s\S]+?)\s*```', RawResponse)
                    json_text = json_text_match.group(1) if json_text_match else RawResponse
                else:
                    start_brace = RawResponse.find('{')
                    end_brace = RawResponse.rfind('}')
                    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
                        json_text = RawResponse[start_brace : end_brace + 1]
                    else:
                        json_text = RawResponse
                
                JSONResponse = json.loads(json_text)
                missing_attribs = [attr for attr in _RequiredAttribs if attr not in JSONResponse]
                if missing_attribs:
                    raise KeyError(f"Required attribute(s) '{', '.join(missing_attribs)}' not in JSON response.")
                return ResponseHistory, JSONResponse
            except (json.JSONDecodeError, KeyError) as e:
                log_message = f"JSON Error (Attempt {attempt + 1}/{_MaxRetries}): {e}."
                if Writer.Config.DEBUG:
                    log_message += f"\n--- Faulty Response Text ---\n{RawResponse}\n--------------------------"
                _Logger.Log(log_message, 7)

                messages_copy = list(ResponseHistory)
                if messages_copy and messages_copy[-1].get("role") == "assistant":
                    messages_copy.pop()

                error_correction_prompt = Writer.Prompts.JSON_PARSE_ERROR.format(_Error=str(e))
                messages_copy.append(self.BuildUserQuery(error_correction_prompt))
                continue

        _Logger.Log(f"CRITICAL: Failed to generate valid JSON after {_MaxRetries} attempts. Returning empty dictionary.", 7)
        return messages_copy, {}


    def ChatAndStreamResponse(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _Format: str = None, max_tokens_override: int = None) -> list:
        Provider, ProviderModel, ModelHost, ModelOptions = self.GetModelAndProvider(_Model)
        
        # --- THE CORRECT FIX ---
        # This line ensures we are always using a string as the key, not a list.
        base_model_uri = _Model.split('?')[0]

        if not self.Clients.get(base_model_uri):
             _Logger.Log(f"Model client for '{base_model_uri}' not loaded. Attempting to load now.", 6)
             self.LoadModels([_Model])

        client = self.Clients.get(base_model_uri)
        if not client:
            _Logger.Log(f"Model client for '{base_model_uri}' could not be loaded or created. Aborting.", 7)
            return _Messages + [{"role": "assistant", "content": f"[ERROR: Model {base_model_uri} not loaded.]"}]

        if _SeedOverride != -1:
            ModelOptions['seed'] = _SeedOverride
        elif 'seed' not in ModelOptions and Writer.Config.SEED != -1:
            ModelOptions['seed'] = Writer.Config.SEED

        if _Format and _Format.lower() == 'json':
            if Provider == 'ollama':
                ModelOptions['format'] = 'json'
            elif Provider == 'google':
                ModelOptions['response_mime_type'] = 'application/json'

        if max_tokens_override is not None:
            if Provider == 'ollama':
                ModelOptions['num_predict'] = max_tokens_override
            elif Provider == 'google':
                ModelOptions['max_output_tokens'] = max_tokens_override
            else:
                ModelOptions['max_tokens'] = max_tokens_override

        if Provider == "github":
            try:
                github_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
                github_token = os.environ.get("GITHUB_ACCESS_TOKEN")
                if ProviderModel.startswith("mistral-ai/"):
                    client = ChatMistralAI(endpoint=github_endpoint, api_key=github_token, model=ProviderModel)
                elif ProviderModel.startswith(("openai/", "cohere/", "xai/", "deepseek/", "ai21-labs/")):
                    client = ChatOpenAI(base_url=github_endpoint, api_key=github_token, model=ProviderModel)
                else:
                    client = AzureChatOpenAI(azure_endpoint=github_endpoint, api_key=github_token, azure_deployment=ProviderModel, api_version=Writer.Config.GITHUB_API_VERSION)
            except Exception as e:
                _Logger.Log(f"Failed to create on-demand GitHub client for '{ProviderModel}'. Error: {e}", 7)
                return _Messages + [{"role": "assistant", "content": "[ERROR: Failed to create GitHub client.]"}]

        provider_safe_params = SAFE_PARAMS.get(Provider, [])
        filtered_options = {k: v for k, v in ModelOptions.items() if k in provider_safe_params}

        if Provider == 'ollama' and 'max_tokens' in filtered_options:
            filtered_options['num_predict'] = filtered_options.pop('max_tokens')
        if Provider == 'google' and 'max_tokens' in filtered_options:
            filtered_options['max_output_tokens'] = filtered_options.pop('max_tokens')

        _Logger.Log(f"Using Model '{ProviderModel}' from '{Provider}'", 4)
        if Writer.Config.DEBUG:
            _Logger.Log(f"Message History:\n{json.dumps(_Messages, indent=2)}", 1)
            if filtered_options:
                _Logger.Log(f"Applying SAFE Params for {Provider}: {filtered_options}", 1)

        langchain_messages = [SystemMessage(content=msg["content"]) if msg["role"] == "system" else AIMessage(content=msg["content"]) if msg["role"] == "assistant" else HumanMessage(content=msg["content"]) for msg in _Messages]
        start_time = time.time()
        full_response = ""
        timeout_duration = Writer.Config.OLLAMA_TIMEOUT if Provider == 'ollama' else Writer.Config.DEFAULT_TIMEOUT

        if platform.system() != "Windows":
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_duration)

        try:
            if Provider == 'google':
                generation_config = {k: v for k, v in filtered_options.items() if k in SAFE_PARAMS['google']}
                stream = client.stream(langchain_messages, generation_config=generation_config)
            else:
                bound_client = client.bind(**filtered_options) if filtered_options else client
                stream = bound_client.stream(langchain_messages)

            _Logger.Log(f"Streaming response (timeout set to {timeout_duration}s)...", 0)
            for chunk in stream:
                chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
                full_response += chunk_text
                print(chunk_text, end="", flush=True)
            print("\n")

        except TimeoutException:
            full_response = f"[ERROR: Generation timed out after {timeout_duration} seconds.]"
            _Logger.Log(f"CRITICAL: LLM call to '{_Model}' timed out.", 7)
        except Exception as e:
            full_response = f"[ERROR: Generation failed. {e}]"
            _Logger.Log(f"CRITICAL: Exception during LLM call to '{_Model}': {e}", 7)
        finally:
            if platform.system() != "Windows":
                signal.alarm(0)

        _Logger.Log(f"Generated response in {time.time() - start_time:.2f}s", 4)
        _Messages.append({"role": "assistant", "content": full_response})
        return _Messages

    def BuildUserQuery(self, _Query: str) -> dict:
        return {"role": "user", "content": _Query}

    def BuildSystemQuery(self, _Query: str) -> dict:
        return {"role": "system", "content": _Query}

    def BuildAssistantQuery(self, _Query: str) -> dict:
        return {"role": "assistant", "content": _Query}

    def GetLastMessageText(self, _Messages: list) -> str:
        return _Messages[-1].get("content", "") if _Messages else ""

```

## File: `Writer/Outline/StoryElements.py`

```python
import Writer.Config
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def GenerateStoryElements(Interface: Interface, _Logger: Logger, _OutlinePrompt: str):

    Prompt: str = f"""
I'm working on writing a fictional story, and I'd like your help writing out the story elements.

Here's the prompt for my story.
<PROMPT>
{_OutlinePrompt}
</PROMPT>

Please make your response have the following format:

<RESPONSE_TEMPLATE>
# Story Title

## Genre
- **Category**: (e.g., romance, mystery, science fiction, fantasy, horror)

## Theme
- **Central Idea or Message**:

## Pacing
- **Speed**: (e.g., slow, fast)

## Style
- **Language Use**: (e.g., sentence structure, vocabulary, tone, figurative language)

## Plot
- **Exposition**:
- **Rising Action**:
- **Climax**:
- **Falling Action**:
- **Resolution**:

## Setting
### Setting 1
- **Time**: (e.g., present day, future, past)
- **Location**: (e.g., city, countryside, another planet)
- **Culture**: (e.g., modern, medieval, alien)
- **Mood**: (e.g., gloomy, high-tech, dystopian)

(Repeat the above structure for additional settings)

## Conflict
- **Type**: (e.g., internal, external)
- **Description**:

## Symbolism
### Symbol 1
- **Symbol**:
- **Meaning**:

(Repeat the above structure for additional symbols)

## Characters
### Main Character(s)
#### Main Character 1
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Motivation**:

(Repeat the above structure for additional main characters)


### Supporting Characters
#### Character 1
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 2
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 3
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 4
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 5
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 6
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 7
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 8
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

(Repeat the above structure for additional supporting character)

</RESPONSE_TEMPLATE>

Of course, don't include the XML tags - those are just to indicate the example.
Also, the items in parenthesis are just to give you a better idea of what to write about, and should also be omitted from your response.
    
    """

    # Generate Initial Story Elements
    _Logger.Log("Generating Main Story Elements", 4)
    Messages = [Interface.BuildUserQuery(Prompt)]
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, min_word_count_target=150
    )
    Elements: str = Interface.GetLastMessageText(Messages)
    _Logger.Log("Done Generating Main Story Elements", 4)

    return Elements

```

## File: `Writer/Scene/ChapterByScene.py`

```python
#!/usr/bin/python3

import Writer.Config
import Writer.SummarizationUtils
import Writer.Scene.ChapterOutlineToScenes
import Writer.Scene.ScenesToJSON
import Writer.Scene.SceneOutlineToScene
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext, ChapterContext, SceneContext
from Writer.PrintUtils import Logger


def ChapterByScene(
    Interface: Interface,
    _Logger: Logger,
    chapter_context: ChapterContext, # Now receives the chapter context object
    narrative_context: NarrativeContext,
) -> str:
    """
    Calls all other scene-by-scene generation functions and creates a full chapter
    based on the new scene pipeline.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        chapter_context: The context object for the chapter to be written.
        narrative_context: The overall context object for the novel.

    Returns:
        The fully generated chapter text, assembled from its scenes.
    """
    _Logger.Log(f"Starting Scene-By-Scene Chapter Generation Pipeline for Chapter {chapter_context.chapter_number}", 2)

    # Step 1: Get the detailed, scene-by-scene markdown outline for this chapter
    scene_by_scene_outline_md = Writer.Scene.ChapterOutlineToScenes.ChapterOutlineToScenes(
        Interface,
        _Logger,
        chapter_context.initial_outline,
        narrative_context,
        chapter_context.chapter_number,
    )

    # Step 2: Convert the markdown outline into a structured JSON list of scene outlines
    scene_json_list = Writer.Scene.ScenesToJSON.ScenesToJSON(
        Interface, _Logger, scene_by_scene_outline_md
    )

    if not scene_json_list:
        _Logger.Log(f"Failed to generate or parse scene list for Chapter {chapter_context.chapter_number}. Aborting scene pipeline for this chapter.", 7)
        return f"// ERROR: Scene generation failed for Chapter {chapter_context.chapter_number}. Could not break the chapter into scenes. //"


    # Step 3: Iterate through each scene, write it, summarize it, and build the chapter
    rough_chapter_text: str = ""
    for i, scene_outline in enumerate(scene_json_list):
        scene_num = i + 1
        _Logger.Log(f"--- Processing Chapter {chapter_context.chapter_number}, Scene {scene_num} ---", 3)

        # A. Create a context object for the current scene. This object will be mutated by the generation function.
        current_scene_context = SceneContext(scene_number=scene_num, initial_outline=scene_outline)
        
        # B. Generate the full text for the scene using the iterative, piece-by-piece method.
        # This function will populate the current_scene_context with its generated pieces.
        Writer.Scene.SceneOutlineToScene.SceneOutlineToScene(
            Interface,
            _Logger,
            current_scene_context,
            narrative_context,
            chapter_context.chapter_number,
            scene_num,
        )
        
        # C. Append the fully assembled scene text to the chapter
        scene_text = current_scene_context.generated_content
        rough_chapter_text += scene_text + "\n\n"

        # D. Generate a final, holistic summary for the completed scene and extract key points for coherence
        final_summary_data = Writer.SummarizationUtils.summarize_scene_and_extract_key_points(
            Interface,
            _Logger,
            scene_text,
            narrative_context,
            chapter_context.chapter_number,
            scene_num,
        )
        current_scene_context.set_final_summary(final_summary_data.get("summary"))
        for point in final_summary_data.get("key_points_for_next_scene", []):
            current_scene_context.add_key_point(point)
        
        _Logger.Log(f"Scene {scene_num} Final Summary: {current_scene_context.final_summary}", 1)
        _Logger.Log(f"Scene {scene_num} Key Points for Next Scene: {current_scene_context.key_points_for_next_scene}", 1)

        # E. Add the completed scene context (now full of pieces and a final summary) to the chapter context
        chapter_context.add_scene(current_scene_context)
        _Logger.Log(f"--- Finished processing Scene {scene_num} ---", 3)


    _Logger.Log(f"Finished Scene-By-Scene Chapter Generation Pipeline for Chapter {chapter_context.chapter_number}", 2)

    return rough_chapter_text.strip()

```

## File: `Writer/Scene/ChapterOutlineToScenes.py`

```python
#!/usr/bin/python3

import Writer.Config
import Writer.CritiqueRevision
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext
from Writer.PrintUtils import Logger


def ChapterOutlineToScenes(
    Interface: Interface,
    _Logger: Logger,
    _ThisChapterOutline: str,
    narrative_context: NarrativeContext,
    _ChapterNum: int,
) -> str:
    """
    Converts a chapter outline into a more detailed outline for each scene within that chapter.
    This process involves a creative critique and revision cycle to ensure a high-quality,
    well-structured scene breakdown.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        _ThisChapterOutline: The outline for the specific chapter to be broken down.
        narrative_context: The context object for the entire novel.
        _ChapterNum: The number of the chapter being processed.

    Returns:
        A string containing the detailed, scene-by-scene markdown outline for the chapter.
    """
    _Logger.Log(f"Splitting Chapter {_ChapterNum} into a scene-by-scene outline.", 2)

    # --- Step 1: Initial Generation ---
    _Logger.Log("Generating initial scene breakdown...", 5)
    initial_prompt = Writer.Prompts.CHAPTER_TO_SCENES.format(
        _ThisChapter=_ThisChapterOutline,
        _Outline=narrative_context.base_novel_outline_markdown,
        _Prompt=narrative_context.initial_prompt,
    )

    messages = [
        Interface.BuildSystemQuery(Writer.Prompts.LITERARY_STYLE_GUIDE),
        Interface.BuildUserQuery(initial_prompt),
    ]

    response_messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, min_word_count_target=100
    )
    initial_scene_breakdown = Interface.GetLastMessageText(response_messages)
    _Logger.Log("Finished initial scene breakdown generation.", 5)

    # --- Step 2: Critique and Revise ---
    _Logger.Log("Critiquing and revising scene breakdown for coherence and quality...", 3)

    task_description = f"Break down the provided chapter outline for Chapter {_ChapterNum} into a detailed, scene-by-scene plan. Each scene should have a clear purpose, setting, character list, and a summary of events, contributing to the chapter's overall arc and adhering to the novel's dark, literary style."

    context_summary = narrative_context.get_context_for_chapter_generation(_ChapterNum)
    context_summary += f"\n\nThis chapter's specific outline, which you need to expand into scenes, is:\n{_ThisChapterOutline}"

    revised_scene_breakdown = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_scene_breakdown,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
        style_guide=narrative_context.style_guide,
    )

    _Logger.Log(f"Finished splitting Chapter {_ChapterNum} into scenes.", 2)
    return revised_scene_breakdown

```

## File: `Writer/Scene/SceneOutlineToScene.py`

```python
#!/usr/bin/python3

import Writer.Config
import Writer.CritiqueRevision
import Writer.Prompts
import Writer.SummarizationUtils
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext, SceneContext
from Writer.PrintUtils import Logger

def _is_scene_complete(
    Interface: Interface,
    _Logger: Logger,
    scene_outline: str,
    full_scene_text: str,
) -> bool:
    """
    Uses an LLM to check if the generated scene text fulfills the scene's outline/goals.
    """
    _Logger.Log("Checking if scene has met its objectives...", 1)
    prompt = Writer.Prompts.IS_SCENE_COMPLETE_PROMPT.format(
        _SceneOutline=scene_outline,
        full_scene_text=full_scene_text
    )
    messages = [Interface.BuildUserQuery(prompt)]

    # This is a non-creative check, so we use a checker model and SafeGenerateJSON
    _, response_json = Interface.SafeGenerateJSON(
        _Logger, messages, Writer.Config.CHECKER_MODEL, _RequiredAttribs=["IsComplete"]
    )
    
    is_complete = response_json.get("IsComplete", False)
    if isinstance(is_complete, str):
        is_complete = is_complete.lower() == 'true'

    _Logger.Log(f"Scene completion check returned: {is_complete}", 1)
    return is_complete

def SceneOutlineToScene(
    Interface: Interface,
    _Logger: Logger,
    scene_context: SceneContext, # Receives the mutable scene context object
    narrative_context: NarrativeContext,
    _ChapterNum: int,
    _SceneNum: int,
) -> str:
    """
    Generates the full text for a single scene by building it iteratively in pieces.
    Each piece is generated, critiqued, revised, and summarized. The summary of
    the previous piece informs the generation of the next, ensuring coherence.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        scene_context: The context object for the specific scene being written.
        narrative_context: The context object for the entire novel.
        _ChapterNum: The number of the current chapter.
        _SceneNum: The number of the current scene.

    Returns:
        A string containing the fully written scene text.
    """
    _Logger.Log(f"Starting iterative SceneOutlineToScene generation for C{_ChapterNum} S{_SceneNum}.", 2)
    MAX_PIECES = 7 # Safety break to prevent infinite loops

    # --- Iterative Scene Generation Loop ---
    while len(scene_context.pieces) < MAX_PIECES:
        
        # Step 1: Get summary of what's been written so far in this scene
        summary_of_previous_pieces = scene_context.get_summary_of_all_pieces()
        if not summary_of_previous_pieces:
            summary_of_previous_pieces = "This is the beginning of the scene."
        _Logger.Log(f"Context for next piece: \"{summary_of_previous_pieces}\"", 1)

        # Step 2: Generate the next piece of the scene
        _Logger.Log(f"Generating piece {len(scene_context.pieces) + 1} for C{_ChapterNum} S{_SceneNum}...", 5)
        
        # Determine the right prompt (start of scene vs. continuation)
        if not scene_context.pieces:
            # First piece: Use the main scene generation prompt
            generation_prompt = Writer.Prompts.SCENE_OUTLINE_TO_SCENE.format(
                narrative_context=narrative_context.get_context_for_scene_generation(_ChapterNum, _SceneNum),
                _SceneOutline=scene_context.initial_outline,
                style_guide=narrative_context.style_guide
            )
        else:
            # Subsequent pieces: Use the continuation prompt
            generation_prompt = Writer.Prompts.CONTINUE_SCENE_PIECE_PROMPT.format(
                summary_of_previous_pieces=summary_of_previous_pieces,
                _SceneOutline=scene_context.initial_outline,
                style_guide=narrative_context.style_guide
            )
        
        messages = [Interface.BuildSystemQuery(Writer.Prompts.LITERARY_STYLE_GUIDE), Interface.BuildUserQuery(generation_prompt)]

        # Generate the initial text for the piece
        response_messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, min_word_count_target=250 # Aim for substantial pieces
        )
        initial_piece_text = Interface.GetLastMessageText(response_messages)

        # Step 3: Critique and Revise the generated piece
        _Logger.Log(f"Critiquing and revising piece {len(scene_context.pieces) + 1}...", 3)
        task_description = f"Write a piece of a scene for Chapter {_ChapterNum}, Scene {_SceneNum}. The writing must be compelling, adhere to a dark literary style, and seamlessly continue from the previous text."
        
        revised_piece_text = Writer.CritiqueRevision.critique_and_revise_creative_content(
            Interface,
            _Logger,
            initial_content=initial_piece_text,
            task_description=task_description,
            narrative_context_summary=narrative_context.get_context_for_scene_generation(_ChapterNum, _SceneNum),
            initial_user_prompt=narrative_context.initial_prompt,
            style_guide=narrative_context.style_guide
        )

        # Step 4: Summarize the revised piece for the next iteration's context
        piece_summary = Writer.SummarizationUtils.summarize_scene_piece(Interface, _Logger, revised_piece_text)
        
        # Step 5: Add the completed piece to the scene context
        scene_context.add_piece(revised_piece_text, piece_summary)
        _Logger.Log(f"Finished piece {len(scene_context.pieces)}. Current scene length: {len(scene_context.generated_content.split())} words.", 4)
        
        # Step 6: Check if the scene is complete
        if _is_scene_complete(Interface, _Logger, scene_context.initial_outline, scene_context.generated_content):
            _Logger.Log(f"Scene C{_ChapterNum} S{_SceneNum} is complete.", 5)
            break
    else:
        # This block executes if the while loop finishes due to MAX_PIECES being reached
        _Logger.Log(f"Scene C{_ChapterNum} S{_SceneNum} reached max pieces ({MAX_PIECES}). Forcing scene to conclude.", 6)

    final_scene_text = scene_context.generated_content
    _Logger.Log(f"Finished SceneOutlineToScene generation for C{_ChapterNum} S{_SceneNum}. Final word count: {len(final_scene_text.split())}", 2)
    return final_scene_text

```

## File: `Writer/Scene/ScenesToJSON.py`

```python
#!/usr/bin/python3

import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger

def ScenesToJSON(
    Interface: Interface, _Logger: Logger, _SceneOutlineMD: str
) -> list:
    """
    Converts a markdown-formatted, scene-by-scene outline into a structured
    JSON list of strings. Each string in the list represents one scene's outline.

    This is a non-creative, structural conversion task.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        _SceneOutlineMD: A string containing the full markdown of the scene-by-scene outline.

    Returns:
        A list of strings, where each string is the outline for a single scene.
        Returns an empty list if the conversion fails.
    """
    _Logger.Log("Converting scene outline markdown to JSON list...", 4)

    # Prepare the prompt for the LLM
    prompt = Writer.Prompts.SCENES_TO_JSON.format(_Scenes=_SceneOutlineMD)
    messages = [Interface.BuildUserQuery(prompt)]

    # Use SafeGenerateJSON to ensure a valid JSON list is returned.
    # The prompt specifically requests a list of strings, so we don't need
    # to check for specific attributes, just that the result is a list.
    _, response_json = Interface.SafeGenerateJSON(
        _Logger,
        messages,
        Writer.Config.CHECKER_MODEL, # Use a fast, reliable model for this conversion
    )

    # Validate that the response is a list
    if isinstance(response_json, list):
        _Logger.Log(f"Successfully converted markdown to a list of {len(response_json)} scenes.", 5)
        return response_json
    else:
        _Logger.Log(f"Conversion failed: LLM did not return a valid JSON list. Response: {response_json}", 7)
        return []

```

## File: `Writer/Config.py`

```python
#!/usr/bin/python3

import configparser
import os
import termcolor

# --- Configuration Loading ---

# Create a ConfigParser instance
config = configparser.ConfigParser()

# Define the path to config.ini relative to this file's location
# This assumes Config.py is in Writer/, and config.ini is in the project root.
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')

# Read the configuration file and add explicit, prominent logging
print(termcolor.colored("--- Initializing Configuration ---", "yellow"))
if os.path.exists(config_path):
    try:
        config.read(config_path)
        # Convert section names to lowercase for consistency
        config._sections = {k.lower(): v for k, v in config._sections.items()}
        print(termcolor.colored(f"[CONFIG] Successfully read config.ini from: {config_path}", "green"))
        loaded_sections = list(config.sections())
        print(termcolor.colored(f"[CONFIG] Found sections: {loaded_sections}", "cyan"))

        # Explicitly check for NVIDIA section and key for debugging
        if 'nvidia_settings' in loaded_sections:
            nvidia_models_value = config.get('nvidia_settings', 'available_models', fallback="[NOT FOUND]")
            nvidia_url_value = config.get('nvidia_settings', 'base_url', fallback="[NOT FOUND]")
            print(termcolor.colored(f"[CONFIG] Raw value for [nvidia_settings]/available_models: '{nvidia_models_value}'", "cyan"))
            print(termcolor.colored(f"[CONFIG] Raw value for [nvidia_settings]/base_url: '{nvidia_url_value}'", "cyan"))
        else:
            print(termcolor.colored("[CONFIG] Section [nvidia_settings] not found in config.ini.", "red"))

    except configparser.Error as e:
        print(termcolor.colored(f"[CONFIG] CRITICAL: Failed to parse config.ini. Error: {e}", "red"))
else:
    print(termcolor.colored(f"[CONFIG] WARNING: config.ini not found at expected path: {config_path}", "red"))

print(termcolor.colored("------------------------------------", "yellow"))


def get_config_or_default(section, key, default, is_bool=False, is_int=False):
    """
    Safely get a value from the config file, otherwise return the default.
    Handles type conversion for boolean and integer values.
    Uses lowercase for section names as per configparser standard.
    """
    section = section.lower()
    if is_bool:
        return config.getboolean(section, key, fallback=default)
    if is_int:
        return config.getint(section, key, fallback=default)
    return config.get(section, key, fallback=default)

# --- Project Info ---
PROJECT_NAME = get_config_or_default('PROJECT_INFO', 'project_name', 'Fiction Fabricator')


# --- LLM Model Selection ---
INITIAL_OUTLINE_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'initial_outline_writer_model', "google://gemini-1.5-pro-latest")
CHAPTER_OUTLINE_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_outline_writer_model', "google://gemini-1.5-flash-latest")
CHAPTER_STAGE1_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_stage1_writer_model', "google://gemini-1.5-flash-latest")
CHAPTER_STAGE2_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_stage2_writer_model', "google://gemini-1.5-flash-latest")
CHAPTER_STAGE3_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_stage3_writer_model', "google://gemini-1.5-flash-latest")
CHAPTER_STAGE4_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_stage4_writer_model', "google://gemini-1.5-flash-latest")
CHAPTER_REVISION_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_revision_writer_model', "google://gemini-1.5-pro-latest")
CRITIQUE_LLM = get_config_or_default('LLM_SELECTION', 'critique_llm', "google://gemini-1.5-flash-latest")
REVISION_MODEL = get_config_or_default('LLM_SELECTION', 'revision_model', "google://gemini-1.5-flash-latest")
EVAL_MODEL = get_config_or_default('LLM_SELECTION', 'eval_model', "google://gemini-1.5-flash-latest")
INFO_MODEL = get_config_or_default('LLM_SELECTION', 'info_model', "google://gemini-1.5-flash-latest")
SCRUB_MODEL = get_config_or_default('LLM_SELECTION', 'scrub_model', "google://gemini-1.5-flash-latest")
CHECKER_MODEL = get_config_or_default('LLM_SELECTION', 'checker_model', "google://gemini-1.5-flash-latest")


# --- NVIDIA Specific Settings (if used) ---
NVIDIA_AVAILABLE_MODELS = get_config_or_default('NVIDIA_SETTINGS', 'available_models', '')
NVIDIA_BASE_URL = get_config_or_default('NVIDIA_SETTINGS', 'base_url', 'https://integrate.api.nvidia.com/v1')


# --- GitHub Specific Settings (if used) ---
GITHUB_API_VERSION = get_config_or_default('GITHUB_SETTINGS', 'api_version', '2024-05-01-preview')


# --- Ollama Specific Settings (if used) ---
OLLAMA_CTX = get_config_or_default('WRITER_SETTINGS', 'ollama_ctx', 8192, is_int=True)


# --- Writer Settings ---
SEED = get_config_or_default('WRITER_SETTINGS', 'seed', 108, is_int=True)
OUTLINE_MIN_REVISIONS = get_config_or_default('WRITER_SETTINGS', 'outline_min_revisions', 0, is_int=True)
OUTLINE_MAX_REVISIONS = get_config_or_default('WRITER_SETTINGS', 'outline_max_revisions', 3, is_int=True)
CHAPTER_NO_REVISIONS = get_config_or_default('WRITER_SETTINGS', 'chapter_no_revisions', False, is_bool=True)
CHAPTER_MIN_REVISIONS = get_config_or_default('WRITER_SETTINGS', 'chapter_min_revisions', 1, is_int=True)
CHAPTER_MAX_REVISIONS = get_config_or_default('WRITER_SETTINGS', 'chapter_max_revisions', 3, is_int=True)
MINIMUM_CHAPTERS = get_config_or_default('WRITER_SETTINGS', 'minimum_chapters', 12, is_int=True)
SCRUB_NO_SCRUB = get_config_or_default('WRITER_SETTINGS', 'scrub_no_scrub', False, is_bool=True)
EXPAND_OUTLINE = get_config_or_default('WRITER_SETTINGS', 'expand_outline', True, is_bool=True)
ENABLE_FINAL_EDIT_PASS = get_config_or_default('WRITER_SETTINGS', 'enable_final_edit_pass', False, is_bool=True)
SCENE_GENERATION_PIPELINE = get_config_or_default('WRITER_SETTINGS', 'scene_generation_pipeline', True, is_bool=True)
DEBUG = get_config_or_default('WRITER_SETTINGS', 'debug', False, is_bool=True)


# --- Timeout Settings ---
DEFAULT_TIMEOUT = get_config_or_default('TIMEOUTS', 'default_timeout', 180, is_int=True)
OLLAMA_TIMEOUT = get_config_or_default('TIMEOUTS', 'ollama_timeout', 360, is_int=True)


# Optional output name override from command-line (not set from config)
OPTIONAL_OUTPUT_NAME = ""


# Example models for reference:
# "google://gemini-1.5-pro-latest"
# "mistralai://mistral-large-latest"
# "groq://mixtral-8x7b-32768"
# "nvidia://meta/llama3-8b-instruct"
# "github://o1-mini"
# "ollama://llama3:70b"
# "ollama://command-r-plus@10.1.65.4:11434"

```

## File: `Writer/CritiqueRevision.py`

```python
#!/usr/bin/python3

import json
import re
import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def _clean_revised_content(
    Interface: Interface,
    _Logger: Logger,
    text_to_clean: str
) -> str:
    """
    Takes text from a revision process and cleans out any non-narrative artifacts.
    This is a fast, non-creative cleanup step.
    """
    if not text_to_clean or "[ERROR:" in text_to_clean:
        return text_to_clean

    _Logger.Log("Performing final cleanup on revised content...", 1)

    prompt = Writer.Prompts.CLEAN_REVISED_TEXT_PROMPT.format(text_to_clean=text_to_clean)
    messages = [Interface.BuildUserQuery(prompt)]
    min_word_target = int(len(text_to_clean.split()) * 0.7)

    response_history = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHECKER_MODEL, min_word_count_target=max(50, min_word_target)
    )

    return Interface.GetLastMessageText(response_history)


def critique_and_revise_creative_content(
    Interface: Interface,
    _Logger: Logger,
    initial_content: str,
    task_description: str,
    narrative_context_summary: str,
    initial_user_prompt: str,
    style_guide: str,
    is_json: bool = False,
) -> str:
    """
    Orchestrates the critique and revision process for a piece of generated creative content.
    This process is a single pass: critique -> revise -> clean.
    """
    # --- FIXED: Add robustness check for initial content ---
    if not initial_content or not initial_content.strip() or "[ERROR:" in initial_content:
        _Logger.Log("CritiqueRevision called with empty, invalid, or error-containing initial content. Skipping process.", 6)
        return initial_content

    # --- Step 1: Generate Critique ---
    _Logger.Log("Starting critique generation for the latest content.", 5)

    json_guidance = (
        "The content is JSON. Focus your critique on the substance, clarity, and narrative value of the data. Respond with your critique as a plain string."
    ) if is_json else "Respond with your critique as a plain string."

    critique_prompt = Writer.Prompts.CRITIQUE_CREATIVE_CONTENT_PROMPT.format(
        text_to_critique=initial_content,
        task_description=task_description,
        narrative_context_summary=narrative_context_summary,
        initial_user_prompt=initial_user_prompt,
        style_guide=style_guide,
        is_json_output=json_guidance
    )
    critique_messages = [Interface.BuildSystemQuery(style_guide), Interface.BuildUserQuery(critique_prompt)]
    critique_model = Writer.Config.CRITIQUE_LLM
    
    critique_messages = Interface.SafeGenerateText(
        _Logger, critique_messages, critique_model, min_word_count_target=100
    )
    critique = Interface.GetLastMessageText(critique_messages)
    _Logger.Log(f"Critique received:\n---\n{critique}\n---", 1)

    # --- FIXED: Handle critique failure gracefully ---
    if "[ERROR:" in critique or not critique.strip():
        _Logger.Log("Critique step failed or returned empty. Skipping revision and returning original content.", 6)
        return initial_content

    # --- Step 2: Generate Revision ---
    _Logger.Log("Starting revision based on the received critique.", 5)

    json_instructions = (
        "Important: Your final output must be a single, valid JSON object. Revise the *content* within the JSON structure based on the critique. Do not add any explanatory text outside of the JSON object itself."
    ) if is_json else (
        "Ensure your final output is only the revised text. Do not write a reflection on the changes."
    )

    revision_prompt = Writer.Prompts.REVISE_CREATIVE_CONTENT_BASED_ON_CRITIQUE_PROMPT.format(
        original_text=initial_content,
        critique=critique,
        task_description=task_description,
        narrative_context_summary=narrative_context_summary,
        initial_user_prompt=initial_user_prompt,
        style_guide=style_guide,
        json_instructions=json_instructions
    )
    revision_messages = [Interface.BuildSystemQuery(style_guide), Interface.BuildUserQuery(revision_prompt)]
    revision_model = Writer.Config.CHAPTER_REVISION_WRITER_MODEL

    revised_content_messy = ""
    if is_json:
        _, revised_json = Interface.SafeGenerateJSON(_Logger, revision_messages, revision_model)
        if not revised_json:
             _Logger.Log("Revision step failed to produce valid JSON. Returning original content.", 6)
             return initial_content
        revised_content_messy = json.dumps(revised_json, indent=2)
    else:
        word_count = len(re.findall(r'\b\w+\b', initial_content))
        min_words = max(100, int(word_count * 0.8))
        final_messages = Interface.SafeGenerateText(
            _Logger, revision_messages, revision_model, min_word_count_target=min_words
        )
        revised_content_messy = Interface.GetLastMessageText(final_messages)

    # --- FIXED: Handle revision failure gracefully ---
    if "[ERROR:" in revised_content_messy or not revised_content_messy.strip():
        _Logger.Log("Revision step failed or returned empty. Returning original content.", 6)
        return initial_content

    _Logger.Log("Content revision complete.", 4)

    # --- Step 3: Clean the revised content ---
    if is_json:
        return revised_content_messy
    else:
        cleaned_content = _clean_revised_content(Interface, _Logger, revised_content_messy)
        if "[ERROR:" in cleaned_content or not cleaned_content.strip():
             _Logger.Log("Final cleaning step failed. Returning the pre-cleaned (but revised) content.", 6)
             return revised_content_messy
        return cleaned_content

```

## File: `Writer/LLMEditor.py`

```python
#!/usr/bin/python3
# File: Writer/LLMEditor.py
# Purpose: Provides functions for LLM-based critique and quality checks.

import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger

def GetChapterRating(Interface: Interface, _Logger: Logger, _Chapter: str) -> bool:
    """
    Uses an LLM to rate a chapter and determine if it's complete and of high quality.
    """
    _Logger.Log("Getting chapter quality rating...", 4)
    prompt = Writer.Prompts.CHAPTER_COMPLETE_PROMPT.format(_Chapter=_Chapter)
    messages = [Interface.BuildUserQuery(prompt)]
    
    _, response_json = Interface.SafeGenerateJSON(
        _Logger, messages, Writer.Config.EVAL_MODEL, _RequiredAttribs=["IsComplete"]
    )
    
    is_complete = response_json.get("IsComplete", False)
    if isinstance(is_complete, str):
        is_complete = is_complete.lower() == 'true'

    return is_complete

def GetFeedbackOnChapter(Interface: Interface, _Logger: Logger, _Chapter: str, _Outline: str) -> str:
    """
    Uses an LLM to generate constructive feedback on a given chapter.
    """
    _Logger.Log("Getting feedback on chapter...", 4)
    prompt = Writer.Prompts.CRITIC_CHAPTER_PROMPT.format(_Chapter=_Chapter)
    messages = [Interface.BuildUserQuery(prompt)]

    response_messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CRITIQUE_LLM, min_word_count_target=100
    )
    
    return Interface.GetLastMessageText(response_messages)

def GetOutlineRating(Interface: Interface, _Logger: Logger, _Outline: str) -> bool:
    """
    Uses an LLM to rate an outline and determine if it's complete and well-structured.
    """
    _Logger.Log("Getting outline completeness rating...", 4)
    prompt = Writer.Prompts.OUTLINE_COMPLETE_PROMPT.format(_Outline=_Outline)
    messages = [Interface.BuildUserQuery(prompt)]
    
    _, response_json = Interface.SafeGenerateJSON(
        _Logger, messages, Writer.Config.EVAL_MODEL, _RequiredAttribs=["IsComplete"]
    )
    
    is_complete = response_json.get("IsComplete", False)
    if isinstance(is_complete, str):
        is_complete = is_complete.lower() == 'true'

    return is_complete

def GetFeedbackOnOutline(Interface: Interface, _Logger: Logger, _Outline: str) -> str:
    """
    Uses an LLM to generate constructive feedback on a given novel outline.
    """
    _Logger.Log("Getting feedback on outline...", 4)
    prompt = Writer.Prompts.CRITIC_OUTLINE_PROMPT.format(_Outline=_Outline)
    messages = [Interface.BuildUserQuery(prompt)]

    response_messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CRITIQUE_LLM, min_word_count_target=100
    )

    return Interface.GetLastMessageText(response_messages)

```

## File: `Writer/LLMUtils.py`

```python
# File: Writer/LLMUtils.py
# Purpose: Centralized utility functions for LLM discovery and selection.

import os
import sys

# Add project root to path for imports to ensure this utility can be called from any script.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import Writer.Config
from Writer.PrintUtils import Logger

def get_ollama_models(logger: Logger):
    """Queries local Ollama for available models."""
    try:
        import ollama
        logger.Log("Querying Ollama for local models...", 1)
        models_data = ollama.list().get("models", [])
        available_models = [f"ollama://{model.get('name') or model.get('model')}" for model in models_data if model.get('name') or model.get('model')]
        logger.Log(f"Found {len(available_models)} Ollama models.", 3)
        return available_models
    except ImportError:
        logger.Log("'ollama' library not installed. Skipping Ollama provider.", 6)
        return []
    except Exception as e:
        logger.Log(f"Could not get Ollama models. (Error: {e})", 6)
        return []

def get_google_models(logger: Logger):
    """Queries Google for available Gemini models."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.Log("Google provider skipped: GOOGLE_API_KEY not found in environment.", 1)
        return []
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        logger.Log("Querying Google for available Gemini models...", 1)
        available = [f"google://{m.name.replace('models/', '')}" for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        logger.Log(f"Found {len(available)} Google models.", 3)
        return available
    except ImportError:
        logger.Log("'google-generativeai' library not installed. Skipping Google provider.", 6)
        return []
    except Exception as e:
        logger.Log(f"Failed to query Google models. (Error: {e})", 6)
        return []

def get_groq_models(logger: Logger):
    """Queries GroqCloud for available models."""
    if not os.environ.get("GROQ_API_KEY"):
        logger.Log("GroqCloud provider skipped: GROQ_API_KEY not found in environment.", 1)
        return []
    try:
        from groq import Groq
        logger.Log("Querying GroqCloud for available models...", 1)
        client = Groq()
        models = client.models.list().data
        logger.Log(f"Found {len(models)} GroqCloud models.", 3)
        return [f"groq://{model.id}" for model in models]
    except ImportError:
        logger.Log("'groq' library not installed. Skipping GroqCloud provider.", 6)
        return []
    except Exception as e:
        logger.Log(f"Failed to query GroqCloud models. (Error: {e})", 6)
        return []

def get_mistral_models(logger: Logger):
    """Queries MistralAI for available models."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        logger.Log("MistralAI provider skipped: MISTRAL_API_KEY not found in environment.", 1)
        return []
    try:
        from mistralai.client import MistralClient
        logger.Log("Querying MistralAI for available models...", 1)
        client = MistralClient(api_key=api_key)
        models_data = client.list_models().data
        known_chat_prefixes = ['mistral-large', 'mistral-medium', 'mistral-small', 'open-mistral', 'open-mixtral']
        available_models = [f"mistralai://{model.id}" for model in models_data if any(model.id.startswith(prefix) for prefix in known_chat_prefixes)]
        logger.Log(f"Found {len(available_models)} compatible MistralAI models.", 3)
        return available_models
    except ImportError:
        logger.Log("'mistralai' library not installed. Skipping MistralAI provider.", 6)
        return []
    except Exception as e:
        logger.Log(f"Failed to query MistralAI models. (Error: {e})", 6)
        return []

def get_nvidia_models(logger: Logger):
    """Reads the user-defined NVIDIA models from config.ini."""
    if not os.environ.get("NVIDIA_API_KEY"):
        logger.Log("NVIDIA provider skipped: NVIDIA_API_KEY not found in environment.", 1)
        return []

    logger.Log("Reading manual NVIDIA model list from config.ini...", 1)
    model_list_str = Writer.Config.NVIDIA_AVAILABLE_MODELS
    if not model_list_str:
        logger.Log("NVIDIA provider skipped: No models listed in config.ini under [NVIDIA_SETTINGS] -> 'available_models'.", 6)
        return []

    model_names = [name.strip() for name in model_list_str.split(',') if name.strip()]
    available_models = [f"nvidia://{name}" for name in model_names]
    logger.Log(f"Found {len(available_models)} NVIDIA models in config.ini.", 3)
    return available_models

def get_github_models(logger: Logger):
    """Returns a static list of available GitHub models, checking for required env vars."""
    if not os.environ.get("GITHUB_ACCESS_TOKEN") or not os.environ.get("AZURE_OPENAI_ENDPOINT"):
        logger.Log("GitHub provider skipped: GITHUB_ACCESS_TOKEN or AZURE_OPENAI_ENDPOINT not found in environment.", 1)
        return []

    logger.Log("Loading GitHub model list...", 1)
    deployment_names = [
        "openai/o1", "openai/o1-mini", "openai/o1-preview", "openai/gpt-4o-mini", "openai/gpt-4o",
        "deepseek/DeepSeek-V3-0324", "deepseek/DeepSeek-R1",
        "ai21-labs/AI21-Jamba-1.5-Large", "ai21-labs/AI21-Jamba-1.5-Mini",
        "cohere/cohere-command-r", "cohere/cohere-command-r-plus", "cohere/cohere-command-a",
        "mistral-ai/Mistral-Nemo", "mistral-ai/Mistral-Small",
        "mistral-ai/Mistral-Large-2411", "mistral-ai/Codestral-22B-v0.1",
        "meta/Llama-3.2-11B-Vision-Instruct", "meta/Llama-3.2-90B-Vision-Instruct",
        "meta/Llama-3.3-70B-Instruct", "meta/Llama-3.1-8B-Instruct",
        "meta/Llama-3.1-70B-Instruct", "meta/Llama-3.1-405B-Instruct",
        "meta/Llama-3-8B-Instruct", "meta/Llama-3-70B-Instruct",
        "microsoft/Phi-4", "microsoft/Phi-3.5-MoE-instruct",
        "microsoft/Phi-3.5-mini-instruct", "microsoft/Phi-3.5-vision-instruct",
        "microsoft/Phi-3-mini-4k-instruct", "microsoft/Phi-3-mini-128k-instruct",
        "microsoft/Phi-3-small-8k-instruct", "microsoft/Phi-3-small-128k-instruct",
        "microsoft/Phi-3-medium-4k-instruct", "microsoft/Phi-3-medium-128k-instruct",
        "xai/grok-3",
        "core42/jais-30b-chat"
    ]
    available_models = [f"github://{name}" for name in deployment_names]
    logger.Log(f"Found {len(available_models)} GitHub models.", 3)
    return available_models

def get_llm_selection_menu_for_tool(logger: Logger, tool_name: str = "Tool") -> str:
    """
    Queries all providers, presents a sorted menu to the user, and returns the chosen model URI.
    """
    print(f"\n--- Querying available models from configured providers for {tool_name}... ---")
    all_models = []
    all_models.extend(get_google_models(logger))
    all_models.extend(get_groq_models(logger))
    all_models.extend(get_mistral_models(logger))
    all_models.extend(get_nvidia_models(logger))
    all_models.extend(get_github_models(logger))
    all_models.extend(get_ollama_models(logger))

    if not all_models:
        logger.Log("No models found from any provider. Please check API keys in .env and model lists in config.ini. Aborting.", 7)
        return None

    print(f"\n--- {tool_name} LLM Selection ---")
    print("Please select the model for this task:")
    sorted_models = sorted(list(set(all_models)))
    for i, model in enumerate(sorted_models):
        print(f"[{i+1}] {model}")

    while True:
        try:
            choice = input(f"> ").strip().lower()
            if choice.isdigit() and 1 <= int(choice) <= len(sorted_models):
                selected_model = sorted_models[int(choice) - 1]
                print(f"Selected: {selected_model}")
                return selected_model
            else:
                print("Invalid choice. Please enter a number from the list.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter a number corresponding to your choice.")
        except (KeyboardInterrupt, EOFError):
             print("\nSelection cancelled by user.")
             return None

```

## File: `Writer/NarrativeContext.py`

```python
#!/usr/bin/python3

from typing import Optional, List, Dict, Any

class ScenePiece:
    """
    Holds the content and summary for a single, small generated piece of a scene.
    This is the most granular level of generated text.
    """
    def __init__(self, piece_number: int, content: str, summary: str):
        self.piece_number: int = piece_number
        self.content: str = content
        self.summary: str = summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "piece_number": self.piece_number,
            "content": self.content,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScenePiece':
        return cls(data["piece_number"], data["content"], data["summary"])


class SceneContext:
    """
    Holds contextual information for a single scene, including its component pieces.
    """
    def __init__(self, scene_number: int, initial_outline: str):
        self.scene_number: int = scene_number
        self.initial_outline: str = initial_outline # The outline specific to this scene
        self.pieces: List[ScenePiece] = [] # A scene is now composed of smaller pieces
        self.final_summary: Optional[str] = None # A final, holistic summary of the assembled scene
        self.key_points_for_next_scene: List[str] = [] # Key takeaways to carry forward

    @property
    def generated_content(self) -> str:
        """Returns the full, assembled text of the scene from its pieces."""
        return "\n\n".join(piece.content for piece in sorted(self.pieces, key=lambda p: p.piece_number))

    def add_piece(self, piece_content: str, piece_summary: str):
        """Adds a new generated piece to the scene."""
        piece_number = len(self.pieces) + 1
        new_piece = ScenePiece(piece_number=piece_number, content=piece_content, summary=piece_summary)
        self.pieces.append(new_piece)

    def get_summary_of_all_pieces(self) -> str:
        """Concatenates the summaries of all pieces to provide running context."""
        return " ".join(piece.summary for piece in sorted(self.pieces, key=lambda p: p.piece_number))

    def set_final_summary(self, summary: str):
        """Sets the final, holistic summary after the scene is fully assembled."""
        self.final_summary = summary

    def add_key_point(self, point: str):
        self.key_points_for_next_scene.append(point)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_number": self.scene_number,
            "initial_outline": self.initial_outline,
            "pieces": [piece.to_dict() for piece in self.pieces],
            "final_summary": self.final_summary,
            "key_points_for_next_scene": self.key_points_for_next_scene,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneContext':
        scene = cls(data["scene_number"], data["initial_outline"])
        scene.pieces = [ScenePiece.from_dict(p_data) for p_data in data.get("pieces", [])]
        scene.final_summary = data.get("final_summary")
        scene.key_points_for_next_scene = data.get("key_points_for_next_scene", [])
        return scene


class ChapterContext:
    """
    Holds contextual information for a single chapter, including its scenes.
    """
    def __init__(self, chapter_number: int, initial_outline: str):
        self.chapter_number: int = chapter_number
        self.initial_outline: str = initial_outline # The outline for the entire chapter
        self.generated_content: Optional[str] = None # Full generated text of the chapter
        self.scenes: List[SceneContext] = []
        self.summary: Optional[str] = None # Summary of what happened in this chapter
        self.theme_elements: List[str] = [] # Themes specific or emphasized in this chapter
        self.character_arcs_progress: Dict[str, str] = {} # CharacterName: ProgressNote

    def add_scene(self, scene_context: SceneContext):
        self.scenes.append(scene_context)

    def get_scene(self, scene_number: int) -> Optional[SceneContext]:
        for scene in self.scenes:
            if scene.scene_number == scene_number:
                return scene
        return None

    def get_last_scene_summary(self) -> Optional[str]:
        if self.scenes:
            return self.scenes[-1].final_summary
        return None

    def set_generated_content(self, content: str):
        self.generated_content = content

    def set_summary(self, summary: str):
        self.summary = summary

    def add_theme_element(self, theme: str):
        self.theme_elements.append(theme)

    def update_character_arc(self, character_name: str, progress_note: str):
        self.character_arcs_progress[character_name] = progress_note

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_number": self.chapter_number,
            "initial_outline": self.initial_outline,
            "generated_content": self.generated_content,
            "scenes": [scene.to_dict() for scene in self.scenes],
            "summary": self.summary,
            "theme_elements": self.theme_elements,
            "character_arcs_progress": self.character_arcs_progress,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChapterContext':
        chapter = cls(data["chapter_number"], data["initial_outline"])
        chapter.generated_content = data.get("generated_content")
        chapter.scenes = [SceneContext.from_dict(s_data) for s_data in data.get("scenes", [])]
        chapter.summary = data.get("summary")
        chapter.theme_elements = data.get("theme_elements", [])
        chapter.character_arcs_progress = data.get("character_arcs_progress", {})
        return chapter


class NarrativeContext:
    """
    Manages and stores the overall narrative context for the entire novel.
    This includes premise, themes, and records of generated chapters and scenes.
    """
    def __init__(self, initial_prompt: str, style_guide: str, overall_theme: Optional[str] = None):
        self.initial_prompt: str = initial_prompt
        self.style_guide: str = style_guide # The guiding principles for the novel's tone and prose
        self.story_elements_markdown: Optional[str] = None # From StoryElements.py
        self.base_novel_outline_markdown: Optional[str] = None # The rough overall outline
        self.expanded_novel_outline_markdown: Optional[str] = None # Detailed, chapter-by-chapter
        self.base_prompt_important_info: Optional[str] = None # Extracted by OutlineGenerator

        self.overall_theme: Optional[str] = overall_theme
        self.motifs: List[str] = []
        self.chapters: List[ChapterContext] = []
        self.generation_log: List[str] = [] # Log of significant generation events or decisions

    def set_story_elements(self, elements_md: str):
        self.story_elements_markdown = elements_md

    def set_base_novel_outline(self, outline_md: str):
        self.base_novel_outline_markdown = outline_md

    def set_expanded_novel_outline(self, outline_md: str):
        self.expanded_novel_outline_markdown = outline_md

    def set_base_prompt_important_info(self, info: str):
        self.base_prompt_important_info = info

    def add_motif(self, motif: str):
        self.motifs.append(motif)

    def add_chapter(self, chapter_context: ChapterContext):
        self.chapters.append(chapter_context)
        self.chapters.sort(key=lambda c: c.chapter_number) # Keep chapters sorted

    def get_chapter(self, chapter_number: int) -> Optional[ChapterContext]:
        for chapter in self.chapters:
            if chapter.chapter_number == chapter_number:
                return chapter
        return None

    def get_previous_chapter_summary(self, current_chapter_number: int) -> Optional[str]:
        if current_chapter_number <= 1:
            return None
        prev_chapter = self.get_chapter(current_chapter_number - 1)
        if prev_chapter:
            return prev_chapter.summary
        return None

    def get_all_previous_chapter_summaries(self, current_chapter_number: int) -> List[Dict[str, Any]]:
        summaries = []
        for i in range(1, current_chapter_number):
            chapter = self.get_chapter(i)
            if chapter and chapter.summary:
                summaries.append({
                    "chapter_number": chapter.chapter_number,
                    "summary": chapter.summary
                })
        return summaries

    def get_full_story_summary_so_far(self, current_chapter_number: Optional[int] = None) -> str:
        """
        Concatenates summaries of all chapters up to (but not including) current_chapter_number.
        If current_chapter_number is None, summarizes all chapters.
        """
        relevant_chapters = self.chapters
        if current_chapter_number is not None:
            relevant_chapters = [ch for ch in self.chapters if ch.chapter_number < current_chapter_number]

        full_summary = ""
        if self.overall_theme:
            full_summary += f"Overall Theme: {self.overall_theme}\n"
        if self.motifs:
            full_summary += f"Key Motifs: {', '.join(self.motifs)}\n"

        full_summary += "\nPrevious Chapter Summaries:\n"
        for chapter in relevant_chapters:
            if chapter.summary:
                full_summary += f"\nChapter {chapter.chapter_number} Summary:\n{chapter.summary}\n"
            if chapter.character_arcs_progress:
                full_summary += f"Character Arc Notes for Chapter {chapter.chapter_number}:\n"
                for char, prog in chapter.character_arcs_progress.items():
                    full_summary += f"  - {char}: {prog}\n"
        return full_summary

    def log_event(self, event_description: str):
        self.generation_log.append(event_description)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "initial_prompt": self.initial_prompt,
            "style_guide": self.style_guide,
            "story_elements_markdown": self.story_elements_markdown,
            "base_novel_outline_markdown": self.base_novel_outline_markdown,
            "expanded_novel_outline_markdown": self.expanded_novel_outline_markdown,
            "base_prompt_important_info": self.base_prompt_important_info,
            "overall_theme": self.overall_theme,
            "motifs": self.motifs,
            "chapters": [chapter.to_dict() for chapter in self.chapters],
            "generation_log": self.generation_log,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeContext':
        # Import here to avoid circular dependency with Prompts.py
        from Writer.Prompts import LITERARY_STYLE_GUIDE
        # Provide a default style guide if it's missing from older JSON files
        style_guide = data.get("style_guide", LITERARY_STYLE_GUIDE)
        context = cls(data["initial_prompt"], style_guide, data.get("overall_theme"))
        context.story_elements_markdown = data.get("story_elements_markdown")
        context.base_novel_outline_markdown = data.get("base_novel_outline_markdown")
        context.expanded_novel_outline_markdown = data.get("expanded_novel_outline_markdown")
        context.base_prompt_important_info = data.get("base_prompt_important_info")
        context.motifs = data.get("motifs", [])
        context.chapters = [ChapterContext.from_dict(ch_data) for ch_data in data.get("chapters", [])]
        context.generation_log = data.get("generation_log", [])
        return context

    def get_context_for_chapter_generation(self, chapter_number: int) -> str:
        """
        Prepares a string of context to be injected into prompts for chapter generation.
        Includes original prompt, overall theme, motifs, and summaries of previous chapters.
        """
        context_str = f"The original user prompt (the source of truth) for the story is:\n---BEGIN PROMPT---\n{self.initial_prompt}\n---END PROMPT---\n\n"

        if self.overall_theme:
            context_str += f"Recall the novel's central theme: {self.overall_theme}\n"
        if self.motifs:
            context_str += f"Remember to weave in the following motifs: {', '.join(self.motifs)}\n"

        if self.base_prompt_important_info:
            context_str += f"\nImportant context from the initial story idea:\n{self.base_prompt_important_info}\n"

        previous_chapter_summaries = self.get_all_previous_chapter_summaries(chapter_number)
        if previous_chapter_summaries:
            context_str += "\nSummary of events from previous chapters:\n"
            for ch_summary_info in previous_chapter_summaries:
                context_str += f"Chapter {ch_summary_info['chapter_number']}:\n{ch_summary_info['summary']}\n\n"

        prev_chapter = self.get_chapter(chapter_number - 1)
        if prev_chapter:
            if prev_chapter.character_arcs_progress:
                context_str += f"Character development notes from the end of Chapter {prev_chapter.chapter_number}:\n"
                for char, prog in prev_chapter.character_arcs_progress.items():
                    context_str += f"  - {char}: {prog}\n"
            if prev_chapter.scenes and prev_chapter.scenes[-1].key_points_for_next_scene:
                context_str += f"Key points to carry over from the last scene of Chapter {prev_chapter.chapter_number}:\n"
                for point in prev_chapter.scenes[-1].key_points_for_next_scene:
                    context_str += f"  - {point}\n"

        return context_str.strip() if context_str else "This is the first chapter, so begin the story!"

    def get_context_for_scene_generation(self, chapter_number: int, scene_number: int) -> str:
        """
        Prepares a string of context for scene generation.
        Includes chapter context and previous scene summary within the same chapter.
        """
        context_str = f"The original user prompt (the source of truth) for the story is:\n---BEGIN PROMPT---\n{self.initial_prompt}\n---END PROMPT---\n\n"

        chapter_ctx = self.get_chapter(chapter_number)
        if not chapter_ctx:
            return "Error: Chapter context not found."

        context_str += f"Currently writing Chapter {chapter_number}, Scene {scene_number}.\n"
        if chapter_ctx.summary:
             context_str += f"So far in this chapter:\n{chapter_ctx.summary}\n"
        elif chapter_ctx.initial_outline:
             context_str += f"The outline for this chapter is:\n{chapter_ctx.initial_outline}\n"

        if chapter_ctx.theme_elements:
            context_str += f"Themes to emphasize in this chapter: {', '.join(chapter_ctx.theme_elements)}\n"

        if scene_number > 1:
            prev_scene = chapter_ctx.get_scene(scene_number - 1)
            if prev_scene and prev_scene.final_summary:
                context_str += f"\nSummary of the previous scene (Scene {prev_scene.scene_number}):\n{prev_scene.final_summary}\n"
                if prev_scene.key_points_for_next_scene:
                    context_str += "Key points to address from the previous scene:\n"
                    for point in prev_scene.key_points_for_next_scene:
                        context_str += f"  - {point}\n"
            else:
                 context_str += f"\nThis is Scene {scene_number}. The previous scene's summary is not available.\n"
        else:
            context_str += f"\nThis is the first scene of Chapter {chapter_number}.\n"
            if chapter_number > 1:
                prev_chapter_summary = self.get_previous_chapter_summary(chapter_number)
                if prev_chapter_summary:
                     context_str += f"To remind you, Chapter {chapter_number-1} ended with:\n{prev_chapter_summary}\n"

        return context_str.strip()

```

## File: `Writer/NovelEditor.py`

```python
#!/usr/bin/python3

import Writer.Config
import Writer.Prompts
import Writer.CritiqueRevision
import Writer.Statistics
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext
from Writer.PrintUtils import Logger


def EditNovel(
    Interface: Interface,
    _Logger: Logger,
    narrative_context: NarrativeContext,
) -> NarrativeContext:
    """
    Performs a final, holistic editing pass on the entire novel.
    It iterates through each chapter, re-editing it with the full context of the novel so far,
    applying a critique-and-revision cycle to each edit.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        narrative_context: The context object containing all chapters and story info.

    Returns:
        The updated NarrativeContext object with edited chapters.
    """
    _Logger.Log("Starting final holistic novel editing pass...", 2)

    total_chapters = len(narrative_context.chapters)
    if total_chapters == 0:
        _Logger.Log("No chapters found in narrative context to edit.", 6)
        return narrative_context

    # Create a static list of original chapter content to use as context
    original_chapters_content = {
        chap.chapter_number: chap.generated_content for chap in narrative_context.chapters
    }

    for i in range(total_chapters):
        chapter_num = i + 1
        _Logger.Log(f"--- Editing Chapter {chapter_num}/{total_chapters} ---", 3)

        chapter_to_edit_content = original_chapters_content.get(chapter_num)
        if not chapter_to_edit_content:
            _Logger.Log(f"Chapter {chapter_num} has no content to edit. Skipping.", 6)
            continue

        # --- Step 1: Initial Edit Generation ---
        _Logger.Log(f"Generating initial edit for Chapter {chapter_num}...", 5)

        # Build the context from all *other* chapters using the original, unedited content
        novel_text_context = ""
        for num, content in original_chapters_content.items():
            if num != chapter_num:
                novel_text_context += f"### Chapter {num}\n\n{content}\n\n\n"

        prompt = Writer.Prompts.CHAPTER_EDIT_PROMPT.format(
            _Outline=narrative_context.base_novel_outline_markdown,
            NovelText=novel_text_context,
            i=chapter_num,
            _Chapter=chapter_to_edit_content,
            style_guide=narrative_context.style_guide
        )

        messages = [
            Interface.BuildSystemQuery(narrative_context.style_guide),
            Interface.BuildUserQuery(prompt)
        ]

        min_words = int(len(chapter_to_edit_content.split()) * 0.9)

        messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.CHAPTER_REVISION_WRITER_MODEL, min_word_count_target=min_words
        )
        initial_edited_chapter = Interface.GetLastMessageText(messages)

        # --- Step 2: Critique and Revise the Edit ---
        _Logger.Log(f"Critiquing and revising the edit for Chapter {chapter_num}...", 4)

        task_description = (
            f"You are performing a final, holistic edit on Chapter {chapter_num}. "
            "Your goal is to refine the chapter to improve its pacing, prose, and consistency, "
            f"ensuring it flows perfectly with the preceding and succeeding chapters and adheres to the novel's dark, literary style."
        )

        context_summary = narrative_context.get_full_story_summary_so_far()

        revised_edited_chapter = Writer.CritiqueRevision.critique_and_revise_creative_content(
            Interface,
            _Logger,
            initial_content=initial_edited_chapter,
            task_description=task_description,
            narrative_context_summary=context_summary,
            initial_user_prompt=narrative_context.initial_prompt,
            style_guide=narrative_context.style_guide,
        )

        # Update the chapter in the narrative context object
        chapter_obj = narrative_context.get_chapter(chapter_num)
        if chapter_obj:
            chapter_obj.set_generated_content(revised_edited_chapter)

        chapter_word_count = Writer.Statistics.GetWordCount(revised_edited_chapter)
        _Logger.Log(f"New word count for edited Chapter {chapter_num}: {chapter_word_count}", 3)

        _Logger.Log(f"--- Finished editing Chapter {chapter_num} ---", 3)

    _Logger.Log("Finished final novel editing pass.", 2)
    return narrative_context

```

## File: `Writer/OutlineGenerator.py`

```python
#!/usr/bin/python3

import re
import Writer.Config
import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Prompts
import Writer.CritiqueRevision
import Writer.Chapter.ChapterDetector
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext
from Writer.PrintUtils import Logger


def GenerateStoryElements(
    Interface: Interface,
    _Logger: Logger,
    _OutlinePrompt: str,
    narrative_context: NarrativeContext,
) -> str:
    """Generates the core story elements using a critique and revision cycle."""

    prompt = Writer.Prompts.GENERATE_STORY_ELEMENTS_PROMPT.format(
        _OutlinePrompt=_OutlinePrompt,
        style_guide=narrative_context.style_guide
    )

    _Logger.Log("Generating initial Story Elements...", 4)
    messages = [Interface.BuildUserQuery(prompt)]
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, min_word_count_target=150
    )
    initial_elements = Interface.GetLastMessageText(messages)
    _Logger.Log("Done generating initial Story Elements.", 4)

    _Logger.Log("Critiquing and revising Story Elements for quality...", 3)
    task_description = "Generate the core story elements (genre, theme, plot points, setting, characters) based on a user's prompt. The output should be a detailed, well-structured markdown document that adheres to a dark, literary style."
    context_summary = f"The user has provided the following high-level prompt for a new story:\n{_OutlinePrompt}"

    revised_elements = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_elements,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=_OutlinePrompt,
        style_guide=narrative_context.style_guide,
    )

    _Logger.Log("Finished revising Story Elements.", 4)
    return revised_elements


def _generate_expanded_outline_for_chapter(
    Interface: Interface,
    _Logger: Logger,
    chapter_num: int,
    _FullOutline: str,
    narrative_context: NarrativeContext,
    _PreviousChaptersSummary: str,
) -> str:
    """
    Generates a detailed, scene-by-scene outline for a SINGLE chapter and runs a critique/revision cycle.
    """
    _Logger.Log(f"Generating detailed outline for Chapter {chapter_num}", 4)

    # Step 1: Initial Generation for the chapter
    prompt = Writer.Prompts.GENERATE_CHAPTER_GROUP_OUTLINE_PROMPT.format(
        _StartChapter=chapter_num,
        _EndChapter=chapter_num,
        _Outline=_FullOutline,
        _OtherGroupsSummary=_PreviousChaptersSummary,
    )
    min_word_target = 150 # Word target for a single chapter's detailed outline
    messages = [
        Interface.BuildSystemQuery(narrative_context.style_guide),
        Interface.BuildUserQuery(prompt)
    ]
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, min_word_count_target=min_word_target
    )
    initial_chapter_outline = Interface.GetLastMessageText(messages)

    # Step 2: Critique and Revise the chapter outline
    _Logger.Log(f"Critiquing and revising outline for Chapter {chapter_num}...", 3)
    task_description = f"Generate a detailed, scene-by-scene outline for Chapter {chapter_num}, based on the main story outline and a summary of previous chapters. The detailed outline should break down the chapter's events, character beats, and setting for each scene, adhering to a dark, literary style."
    context_summary = f"Main Story Outline:\n{_FullOutline}\n\nSummary of Previous Chapters:\n{_PreviousChaptersSummary}"

    revised_chapter_outline = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_chapter_outline,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
        style_guide=narrative_context.style_guide,
    )

    _Logger.Log(f"Done generating detailed outline for Chapter {chapter_num}.", 4)
    return revised_chapter_outline


def GenerateOutline(
    Interface: Interface,
    _Logger: Logger,
    _OutlinePrompt: str,
    narrative_context: NarrativeContext,
) -> NarrativeContext:
    """
    Generates the complete story outline, including story elements and chapter breakdowns,
    and populates the provided NarrativeContext object.
    """
    # --- Step 1: Extract Important Base Context ---
    _Logger.Log("Extracting important base context from prompt...", 4)
    base_context_prompt = Writer.Prompts.GET_IMPORTANT_BASE_PROMPT_INFO.format(
        _Prompt=_OutlinePrompt
    )
    messages = [Interface.BuildUserQuery(base_context_prompt)]
    messages = Interface.SafeGenerateText(_Logger, messages, Writer.Config.INFO_MODEL, min_word_count_target=50)
    base_context = Interface.GetLastMessageText(messages)
    narrative_context.set_base_prompt_important_info(base_context)
    _Logger.Log("Done extracting important base context.", 4)

    # --- Step 2: Generate Story Elements ---
    story_elements = GenerateStoryElements(
        Interface, _Logger, _OutlinePrompt, narrative_context
    )
    narrative_context.set_story_elements(story_elements)

    # --- Step 3: Generate Initial Rough Outline ---
    _Logger.Log("Generating initial rough outline...", 4)
    initial_outline_prompt = Writer.Prompts.INITIAL_OUTLINE_PROMPT.format(
        StoryElements=story_elements,
        _OutlinePrompt=_OutlinePrompt,
        style_guide=narrative_context.style_guide,
    )
    messages = [Interface.BuildUserQuery(initial_outline_prompt)]
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, min_word_count_target=250
    )
    outline = Interface.GetLastMessageText(messages)
    _Logger.Log("Done generating initial rough outline.", 4)

    # --- Step 4: Revision Loop for the Rough Outline ---
    _Logger.Log("Entering feedback/revision loop for the rough outline...", 3)
    iterations = 0
    while True:
        iterations += 1
        is_complete = Writer.LLMEditor.GetOutlineRating(Interface, _Logger, outline)
        if iterations > Writer.Config.OUTLINE_MAX_REVISIONS:
            _Logger.Log("Max revisions reached. Exiting revision loop.", 6)
            break
        if iterations > Writer.Config.OUTLINE_MIN_REVISIONS and is_complete:
            _Logger.Log("Outline meets quality standards. Exiting revision loop.", 5)
            break
        _Logger.Log(f"Outline Revision Iteration {iterations}", 4)
        feedback = Writer.LLMEditor.GetFeedbackOnOutline(Interface, _Logger, outline)
        revision_prompt = Writer.Prompts.OUTLINE_REVISION_PROMPT.format(
            _Outline=outline,
            _Feedback=feedback,
            style_guide=narrative_context.style_guide,
        )
        _Logger.Log("Revising outline based on feedback...", 2)
        revision_messages = [Interface.BuildUserQuery(revision_prompt)]
        revision_messages = Interface.SafeGenerateText(
            _Logger,
            revision_messages,
            Writer.Config.INITIAL_OUTLINE_WRITER_MODEL,
            min_word_count_target=250,
        )
        outline = Interface.GetLastMessageText(revision_messages)
        _Logger.Log("Done revising outline.", 2)

    _Logger.Log("Quality standard met. Exiting feedback/revision loop.", 4)

    # --- Step 5: Enforce Minimum Chapter Count ---
    num_chapters = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, _Logger, outline)
    if 0 < num_chapters < Writer.Config.MINIMUM_CHAPTERS:
        _Logger.Log(f"Outline has {num_chapters} chapters, which is less than the minimum of {Writer.Config.MINIMUM_CHAPTERS}. Expanding...", 6)
        expansion_prompt = Writer.Prompts.EXPAND_OUTLINE_TO_MIN_CHAPTERS_PROMPT.format(
            _Outline=outline, _MinChapters=Writer.Config.MINIMUM_CHAPTERS
        )
        messages = [
            Interface.BuildSystemQuery(narrative_context.style_guide),
            Interface.BuildUserQuery(expansion_prompt)
        ]
        word_count = len(re.findall(r'\b\w+\b', outline))
        min_word_target = max(int(word_count * 1.2), 400)
        messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, min_word_count_target=min_word_target
        )
        outline = Interface.GetLastMessageText(messages)
        _Logger.Log("Outline expanded to meet minimum chapter count.", 5)

    narrative_context.set_base_novel_outline(outline)

    # --- Step 6: Generate Expanded Per-Chapter Outline (if enabled) ---
    if Writer.Config.EXPAND_OUTLINE:
        _Logger.Log("Starting per-chapter outline expansion...", 3)
        final_num_chapters = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, _Logger, outline)

        if final_num_chapters <= 0:
            _Logger.Log(f"Could not determine valid chapter count ({final_num_chapters}). Skipping expansion.", 6)
        else:
            # REFACTORED LOGIC: Generate one chapter at a time for reliability.
            expanded_outlines = []
            full_summary_so_far = "This is the start of the novel."

            for i in range(1, final_num_chapters + 1):
                _Logger.Log(f"Processing detailed outline for Chapter {i}/{final_num_chapters}", 2)

                # Generate the detailed outline for the current chapter
                chapter_outline_text = _generate_expanded_outline_for_chapter(
                    Interface, _Logger, i, outline, narrative_context, full_summary_so_far
                )
                expanded_outlines.append(chapter_outline_text)

                # Update the summary with the content of the chapter we just outlined
                _Logger.Log(f"Summarizing newly generated outline for Chapter {i} to build context...", 1)
                summary_prompt = Writer.Prompts.SUMMARIZE_OUTLINE_RANGE_PROMPT.format(
                    _Outline=chapter_outline_text, _StartChapter=i, _EndChapter=i
                )
                summary_messages = [Interface.BuildUserQuery(summary_prompt)]
                summary_messages = Interface.SafeGenerateText(
                    _Logger, summary_messages, Writer.Config.INFO_MODEL, min_word_count_target=50
                )
                new_summary = Interface.GetLastMessageText(summary_messages)
                full_summary_so_far += f"\n\nSummary for Chapter {i}:\n{new_summary}"

            full_expanded_outline = "\n\n".join(expanded_outlines)
            narrative_context.set_expanded_novel_outline(full_expanded_outline)
            _Logger.Log("Finished expanding all chapter outlines.", 3)

    return narrative_context

```

## File: `Writer/PrintUtils.py`

```python
#!/usr/bin/python3

import os
import json
import datetime
import termcolor
import Writer.Config


class Logger:

    def __init__(self, _LogfilePrefix="Logs"):
        """
        Initializes the logger, creating a unique directory for each run.
        """
        # Make Paths For Log
        log_dir_name = f"{Writer.Config.PROJECT_NAME}_" + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_dir_path = os.path.join(_LogfilePrefix, log_dir_name)
        
        self.LangchainDebugPath = os.path.join(log_dir_path, "LangchainDebug")
        os.makedirs(self.LangchainDebugPath, exist_ok=True)

        # Setup Log Path
        self.LogDirPrefix = log_dir_path
        self.LogPath = os.path.join(log_dir_path, "Main.log")
        self.File = open(self.LogPath, "a", encoding='utf-8')
        self.LangchainID = 0

    def SaveLangchain(self, _LangChainID: str, _LangChain: list):
        """
        Saves the entire language chain object as both JSON and Markdown for debugging.
        """
        # Sanitize the ID for use in file paths
        safe_id = "".join(c for c in _LangChainID if c.isalnum() or c in ('-', '_')).rstrip()
        
        # Calculate Filepath For This Langchain
        this_log_path_json = os.path.join(self.LangchainDebugPath, f"{self.LangchainID}_{safe_id}.json")
        this_log_path_md = os.path.join(self.LangchainDebugPath, f"{self.LangchainID}_{safe_id}.md")
        langchain_debug_title = f"{self.LangchainID}_{safe_id}"
        self.LangchainID += 1

        # Generate and Save JSON Version
        try:
            with open(this_log_path_json, "w", encoding='utf-8') as f:
                json.dump(_LangChain, f, indent=4, sort_keys=True)
        except Exception as e:
            self.Log(f"Failed to write Langchain JSON log for {langchain_debug_title}. Error: {e}", 7)

        # Now, Save Markdown Version
        try:
            with open(this_log_path_md, "w", encoding='utf-8') as f:
                markdown_version = f"# Debug LangChain {langchain_debug_title}\n**Note: '```' tags have been removed in this version.**\n"
                for message in _LangChain:
                    role = message.get('role', 'unknown')
                    content = message.get('content', '[NO CONTENT]')
                    markdown_version += f"\n\n\n## Role: {role}\n"
                    markdown_version += f"```\n{str(content).replace('```', '')}\n```"
                f.write(markdown_version)
        except Exception as e:
            self.Log(f"Failed to write Langchain Markdown log for {langchain_debug_title}. Error: {e}", 7)
            
        self.Log(f"Wrote LangChain debug logs for {langchain_debug_title}", 1)

    def Log(self, _Item, _Level: int = 1):
        """Logs an item to the console and the log file with appropriate color-coding."""
        # Create Log Entry
        log_entry = f"[{str(_Level).ljust(2)}] [{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}] {_Item}"

        # Write it to file
        self.File.write(log_entry + "\n")
        self.File.flush() # Ensure logs are written immediately

        # Now color and print it to the console
        color_map = {
            0: "white",   # Verbose debug
            1: "grey",    # Info
            2: "blue",    # Process start/end
            3: "cyan",    # Sub-process info
            4: "magenta", # Important info
            5: "green",   # Success/completion
            6: "yellow",  # Warning
            7: "red",     # Error/Critical
        }
        color = color_map.get(_Level, "white")
        
        try:
            print(termcolor.colored(log_entry, color))
        except Exception:
            # Fallback for environments that don't support color
            print(log_entry)


    def __del__(self):
        if self.File and not self.File.closed:
            self.File.close()

```

## File: `Writer/Prompts.py`

```python
# File: Writer/Prompts.py
# Purpose: A centralized repository for all LLM prompt templates used in the project.
# Refactored to improve clarity, flexibility, and robustness.

# ======================================================================================
# Prompts for Outline and Story Structure
# ======================================================================================

# A flexible style guide to be used as a system prompt for most creative tasks.
LITERARY_STYLE_GUIDE = """
Your writing must be sophisticated, clear, and compelling. Strive for prose that is rich with detail and psychological depth.

**Core Tenets of Your Writing Style:**
1.  **Show, Don't Tell:** Do not state an emotion; describe the actions and sensory details that reveal it. Let the narrative unfold organically through character actions and dialogue.
2.  **Psychological Depth:** Delve into the inner workings of your characters' minds. Their motivations should be complex and their reliability questionable. The psychological landscape is as important as the physical one.
3.  **Avoid AI Tropes:** Do not start sentences with predictable phrases like "Meanwhile," or "As the sun began to set,". Avoid overly simplistic emotional descriptions. The narrative should feel organic and unpredictable.
"""

# New prompt for generating story elements, focusing on user's prompt.
GENERATE_STORY_ELEMENTS_PROMPT = """
You are a master storyteller. Your task is to analyze a user's story prompt and define its core creative elements.

<USER_PROMPT>
{_OutlinePrompt}
</USER_PROMPT>

Adhering to the spirit of the user's prompt, define the following elements in markdown format.

<RESPONSE_TEMPLATE>
# Story Title

## Genre
- **Category**: (e.g., Psychological Thriller, Sci-Fi Adventure, Fantasy Romance)

## Theme
- **Central Idea or Message**: (The core message or question explored in the story.)

## Pacing
- **Speed**: (e.g., slow-burn, relentless, feverish)

## Style
- **Language Use**: (e.g., Sparse and clinical, ornate and literary, stream-of-consciousness.)

## Plot
- **Exposition**:
- **Rising Action**:
- **Climax**:
- **Falling Action**:
- **Resolution**: (The story's conclusion, which should be a logical outcome of the premise.)

## Setting
### Setting 1
- **Time**:
- **Location**:
- **Culture**:
- **Mood**:

(Repeat for additional settings)

## Conflict
- **Type**: (e.g., internal (man vs. self), external (man vs. society))
- **Description**: (The central conflict driving the narrative.)

## Characters
### Main Character(s)
#### Main Character 1
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Motivation**:

(Repeat for additional main characters)

### Supporting Characters
#### Character 1
- **Name**:
- **Role in the story**:

(Repeat for additional supporting characters)
</RESPONSE_TEMPLATE>

Do not include the XML tags in your response. Infuse the spirit of the user's prompt into every element you create.
"""

CHAPTER_COUNT_PROMPT = """
<OUTLINE>
{_Summary}
</OUTLINE>

Please provide a JSON formatted response containing the total number of chapters in the above outline.

Respond with {{"TotalChapters": <total chapter count>}}
Please do not include any other text, just the JSON, as your response will be parsed by a computer.
"""

INITIAL_OUTLINE_PROMPT = """
You are a master storyteller tasked with creating a compelling, chapter-by-chapter novel outline.

**Your Style Guide:**
---
{style_guide}
---

**Core Story Concept:**
Use the user's prompt and the defined story elements to build your outline.
<PROMPT>
{_OutlinePrompt}
</PROMPT>

<ELEMENTS>
{StoryElements}
</ELEMENTS>

**Your Task:**
Write a detailed, chapter-by-chapter outline in markdown format.
- The plot must be coherent, with each chapter building on the last toward a satisfying conclusion.
- Ensure it is very clear what content belongs in each chapter. Add significant detail to guide the writing process.
"""

OUTLINE_REVISION_PROMPT = """
You are a master storyteller revising a novel outline based on editorial feedback.

**Your Style Guide:**
---
{style_guide}
---

**Outline to Revise:**
<OUTLINE>
{_Outline}
</OUTLINE>

**Editorial Feedback:**
<FEEDBACK>
{_Feedback}
</FEEDBACK>

**Your Task:**
Rewrite the entire outline, incorporating the feedback to improve it.
- Deepen the plot, character arcs, and thematic complexity.
- Ensure the revised outline is aligned with the style guide.
- Add more detail to every chapter, making the sequence of events and character motivations crystal clear.
- The final outline must be a complete, chapter-by-chapter markdown document.
"""

GET_IMPORTANT_BASE_PROMPT_INFO = """
Please extract any important information from the user's prompt below.
Focus on instructions that are not part of the story's plot or characters, but are about the writing style, format, length, or overall vision.

<USER_PROMPT>
{_Prompt}
</USER_PROMPT>

Please use the below template for formatting your response.
(Don't use the xml tags though - those are for example only)

<EXAMPLE>
# Important Additional Context
- Important point 1
- Important point 2
</EXAMPLE>

Do NOT write the outline itself, **just the extra context**. Keep your responses short and in a bulleted list.
If the prompt provides no such context, you must respond with "No additional context found."
"""

EXPAND_OUTLINE_TO_MIN_CHAPTERS_PROMPT = """
You are a master story developer. Your task is to revise a novel outline to meet a minimum chapter count by adding meaningful content.

# CURRENT OUTLINE
---
{_Outline}
---

# TASK
Revise the outline so that it contains at least **{_MinChapters}** chapters.
Do NOT just split existing chapters. Instead, expand the story by:
- Developing subplots that explore the story's core themes.
- Giving more space to character arcs.
- Adding new events or complications that are consistent with the story's tone and plot.
- Fleshing out the rising action, climax, or falling action with more detail.

The goal is a richer, more detailed story that naturally fills the required number of chapters.
Your response should be the new, complete, chapter-by-chapter markdown outline.
"""

SUMMARIZE_OUTLINE_RANGE_PROMPT = """
You are a story analyst. Your task is to read a novel outline and summarize a specific range of chapters.

# FULL NOVEL OUTLINE
---
{_Outline}
---

# YOUR TASK
Provide a concise summary of the events, character arcs, and key plot points that occur between **Chapter {_StartChapter} and Chapter {_EndChapter}**, based *only* on the full outline provided.

Your response should be a single, coherent paragraph.
"""

GENERATE_CHAPTER_GROUP_OUTLINE_PROMPT = """
You are a master storyteller. Your task is to expand a part of a novel outline into a detailed, scene-by-scene breakdown.

# FULL NOVEL OUTLINE
This is the complete outline for the entire story. Use it for high-level context.
---
{_Outline}
---

# SUMMARY OF OTHER STORY PARTS
Here is a summary of the major events from other parts of the story. You must ensure the chapters you are outlining connect logically to these events.
---
{_OtherGroupsSummary}
---

# YOUR TASK
Your sole focus is to generate detailed, scene-by-scene outlines for **Chapters {_StartChapter} through {_EndChapter}**.

For EACH chapter in this range, provide a markdown block that includes:
- A main markdown header for the chapter (e.g., `# Chapter X: The Title`).
- Multiple scene-by-scene breakdowns under that chapter header.
- For each scene, please provide a clear heading, a list of characters, a description of the setting, and a summary of the key events.

Your output should be a single, continuous markdown document containing the detailed outlines for ALL chapters in the specified range.
"""

# ======================================================================================
# Prompts for Chapter Generation
# ======================================================================================

CHAPTER_GENERATION_PROMPT = """
Please extract the part of this outline that is just for chapter {_ChapterNum}.

<OUTLINE>
{_Outline}
</OUTLINE>

Do not include anything else in your response except just the content for chapter {_ChapterNum}.
"""

CHAPTER_GENERATION_STAGE1 = """
# Context
Here is the context for the novel so far, including themes, motifs, and summaries of previous chapters. Use this to ensure your writing is coherent.
---
{narrative_context}
---

# Your Task
Write the PLOT for chapter {_ChapterNum} of {_TotalChapters}.
Base your writing on the following chapter outline. Your main goal is to establish the sequence of events.
It is imperative that your writing connects well with the previous chapter.

**Crucial:** You must adhere to the literary style defined in the system prompt.

<CHAPTER_OUTLINE>
{ThisChapterOutline}
</CHAPTER_OUTLINE>
"""

CHAPTER_GENERATION_STAGE2 = """
# Context
Here is the context for the novel so far. Use this to inform your writing.
---
{narrative_context}
---

# Your Task
Expand upon the provided chapter plot by adding CHARACTER DEVELOPMENT for chapter {_ChapterNum} of {_TotalChapters}.
Do not remove existing content; instead, enrich it with character thoughts, feelings, and motivations, adhering to the established literary style.

Here is the current chapter's plot:
<CHAPTER_PLOT>
{Stage1Chapter}
</CHAPTER_PLOT>
"""

CHAPTER_GENERATION_STAGE3 = """
# Context
Here is the context for the novel so far. Use this to inform your writing.
---
{narrative_context}
---

# Your Task
Expand upon the provided chapter content by adding DIALOGUE for chapter {_ChapterNum} of {_TotalChapters}.
Do not remove existing content; instead, weave natural and purposeful conversations into the scenes. Dialogue should reveal character and subtext.

Here's what I have so far for this chapter:
<CHAPTER_CONTENT>
{Stage2Chapter}
</CHAPTER_CONTENT>

As you add dialogue, please remove any leftover headings or author notes. Your output should be clean, final chapter text.
"""


# ======================================================================================
# Prompts for Summarization and Coherence
# ======================================================================================

SUMMARIZE_SCENE_PROMPT = """
Please analyze the following scene and provide a structured JSON response.

<SCENE_TEXT>
{scene_text}
</SCENE_TEXT>

Your response must be a single JSON object with two keys:
1. "summary": A concise paragraph summarizing the key events, character interactions, and setting of the scene.
2. "key_points_for_next_scene": A list of 2-4 bullet points identifying crucial pieces of information (e.g., unresolved conflicts, new character goals, important objects, lingering questions) that must be carried forward to ensure continuity in the next scene.

Provide only the JSON object in your response.
"""

SUMMARIZE_CHAPTER_PROMPT = """
Please provide a concise, one-paragraph summary of the following chapter text.
Focus on the main plot advancements, significant character developments, and the state of the story at the chapter's conclusion.

<CHAPTER_TEXT>
{chapter_text}
</CHAPTER_TEXT>

Do not include anything in your response except the summary paragraph.
"""

SUMMARIZE_SCENE_PIECE_PROMPT = """
You are a story coherence assistant. Your task is to read a small chunk of a scene and summarize it very concisely. This summary will be used to prompt the AI to write the *next* chunk of the scene, so it must be accurate and capture the immediate state of things.

# SCENE CHUNK
---
{scene_piece_text}
---

# YOUR TASK
Provide a 1-2 sentence summary of the chunk above. Focus only on what happened in this specific text. What is the very last thing that happened? Who is present and what is their immediate situation?
"""

# ======================================================================================
# Prompts for Critique and Revision
# ======================================================================================

CRITIQUE_CREATIVE_CONTENT_PROMPT = """
You are a literary editor providing feedback on a piece of writing for a novel.
Your goal is to provide specific, constructive criticism to help the author improve the piece, ensuring it aligns with the original creative vision and the required literary style.

# STYLE GUIDE (Non-negotiable)
---
{style_guide}
---

# ORIGINAL USER PROMPT (The Source of Truth)
This is the core idea the author started with.
---
{initial_user_prompt}
---

# CONTEXT OF THE STORY SO FAR
This is a summary of events written so far.
---
{narrative_context_summary}
---

# TASK DESCRIPTION
The author was trying to accomplish the following: "{task_description}"

# TEXT TO CRITIQUE
---
{text_to_critique}
---

# YOUR INSTRUCTIONS
Critique the "TEXT TO CRITIQUE". Your feedback is crucial.
1.  **Style Adherence:** Does the text follow the **STYLE GUIDE**? Is it compelling and psychologically complex?
2.  **Prompt Adherence:** Does it honor the core ideas from the "ORIGINAL USER PROMPT"?
3.  **Coherence:** Does it logically follow from the "CONTEXT OF THE STORY SO FAR"?
4.  **Task Fulfillment:** Did it successfully achieve its "TASK DESCRIPTION"?

Provide a few bullet points of direct, actionable feedback.
{is_json_output}
"""

REVISE_CREATIVE_CONTENT_BASED_ON_CRITIQUE_PROMPT = """
You are a master fiction writer tasked with revising a piece of text based on an editor's critique.

# STYLE GUIDE (Non-negotiable)
Your revision must embody this style.
---
{style_guide}
---

# ORIGINAL USER PROMPT (The Source of Truth)
Your revision MUST align with this core idea.
---
{initial_user_prompt}
---

# STORY CONTEXT
This is the background for the story you are working on.
---
{narrative_context_summary}
---

# ORIGINAL TEXT
This was the first draft.
---
{original_text}
---

# EDITOR'S CRITIQUE
Here is the feedback you must address.
---
{critique}
---

# YOUR TASK
Rewrite the "ORIGINAL TEXT" to address the points in the "EDITOR'S CRITIQUE".
- You MUST stay true to the original text's purpose, as described here: "{task_description}".
- You MUST ensure your revision is strongly aligned with the "STYLE GUIDE" and "ORIGINAL USER PROMPT".
- You MUST ensure the revised text is coherent with the story's context.

{json_instructions}
"""

CLEAN_REVISED_TEXT_PROMPT = """
You are a cleanup utility. The following text was generated by an AI that was instructed to revise a piece of creative writing. It may have included extraneous notes or other non-narrative text.

# TEXT TO CLEAN
---
{text_to_clean}
---

# YOUR TASK
Your sole job is to extract and return ONLY the core, clean, narrative prose from the text above.
- Remove any headings, author notes, or meta-commentary (e.g., "Here is the revised text:").
- Return only the story content itself.
"""

CHAPTER_REVISION = """
Please revise the following chapter based on the provided feedback, adhering to the literary style defined in the system prompt.

<CHAPTER_CONTENT>
{_Chapter}
</CHAPTER_CONTENT>

<FEEDBACK>
{_Feedback}
</FEEDBACK>

Do not reflect on the revisions; just write the improved chapter.
"""

CRITIC_OUTLINE_PROMPT = """
Please critique the following outline. Provide constructive criticism on how it can be improved and point out any problems with plot, pacing, or characterization.

<OUTLINE>
{_Outline}
</OUTLINE>
"""

OUTLINE_COMPLETE_PROMPT = """
<OUTLINE>
{_Outline}
</OUTLINE>

Does this outline meet all of the following criteria?
- Pacing: The story does not rush over important plot points or excessively focus on minor ones.
- Flow: Chapters flow logically into each other with a clear and consistent narrative structure.
- Completeness: The outline presents a full and coherent story from beginning to end.

Give a JSON formatted response, containing the key \"IsComplete\" with a boolean value (true/false).
Please do not include any other text, just the JSON.
"""

# --- NEW: Specific prompt for JSON parsing errors ---
JSON_PARSE_ERROR = "Your previous response was not valid JSON and could not be parsed. The parser returned the following error: `{_Error}`. It is crucial that your entire response be a single, valid JSON object. Please correct your response and provide only the valid JSON."

CRITIC_CHAPTER_PROMPT = """<CHAPTER>
{_Chapter}
</CHAPTER>

Please give feedback on the above chapter based on pacing, flow, characterization, and overall narrative quality.
"""

CHAPTER_COMPLETE_PROMPT = """
<CHAPTER>
{_Chapter}
</CHAPTER>

Does this chapter meet the following criteria?
- Pacing and Flow: The chapter is well-paced and flows logically.
- Quality Writing: The chapter is engaging, detailed, and written in a sophisticated, human-like style.
- Narrative Cohesion: The chapter feels like a complete part of a larger novel.

Give a JSON formatted response, with the key \"IsComplete\" and a boolean value (true/false).
Please do not include any other text, just the JSON.
"""
CHAPTER_EDIT_PROMPT = """
You are a developmental editor performing a holistic edit on a chapter to ensure it fits perfectly within the novel.

# STYLE GUIDE
---
{style_guide}
---

# FULL STORY OUTLINE
For context, here is the master outline for the entire novel.
---
{_Outline}
---

# FULL TEXT OF OTHER CHAPTERS
Here is the text of the surrounding chapters. Use this to ensure seamless transitions and consistent character voice.
---
{NovelText}
---

# CHAPTER TO EDIT
Now, please perform a detailed edit of Chapter {i}.
---
{_Chapter}
---

# YOUR TASK
Rewrite Chapter {i}. Improve its prose, pacing, and dialogue. Most importantly, ensure it aligns perfectly with the STYLE GUIDE, the full story outline, and connects seamlessly with the other chapters provided. Output only the revised chapter text.
"""
CHAPTER_SCRUB_PROMPT = """
<CHAPTER>
{_Chapter}
</CHAPTER>

Given the above chapter, please clean it up so that it is ready to be published.
Remove any leftover outlines, author notes, or editorial comments, leaving only the finished story text.
Do not comment on your task; your output will be the final print version.
"""
STATS_PROMPT = """
Please write a JSON formatted response based on the story written in previous messages.

{{
"Title": "a short, evocative title for the story",
"Summary": "a paragraph that summarizes the story from start to finish",
"Tags": "a string of tags separated by commas that describe the story's genre and themes",
"OverallRating": "your overall score for the story from 0-100"
}}

Remember to make your response valid JSON with no extra words.
"""

# ======================================================================================
# Prompts for Scene-by-Scene Generation (Refactored)
# ======================================================================================

CHAPTER_TO_SCENES = """
# CONTEXT
I am writing a story based on the high-level user prompt below.
<USER_PROMPT>
{_Prompt}
</USER_PROMPT>

Below is my overall novel outline derived from that prompt:
<OUTLINE>
{_Outline}
</OUTLINE>

# OBJECTIVE
Create a detailed scene-by-scene outline for the chapter detailed below. For each scene, describe what happens, its tone, the characters present, and the setting.

Here's the specific chapter outline to expand into scenes:
<CHAPTER_OUTLINE>
{_ThisChapter}
</CHAPTER_OUTLINE>

# REQUIREMENTS
- You MUST generate a minimum of 3 scenes. If the chapter outline is simple, expand it with additional character moments or complications that fit the narrative.
- Format your response in markdown, with clear headings for each scene. Add enough detail to guide the writing of a full scene.
"""

SCENES_TO_JSON = """
# CONTEXT
I need to convert the following scene-by-scene outline into a JSON formatted list of strings.
<SCENE_OUTLINE>
{_Scenes}
</SCENE_OUTLINE>

# OBJECTIVE
Create a JSON list where each element is a string containing the full markdown content for one scene.
Example:
[
    "## Scene 1: The Confrontation\\n- **Characters:** Kaelan, Informant\\n- **Setting:** The Rusty Flagon...",
    "## Scene 2: The Escape\\n- **Characters:** Kaelan\\n- **Setting:** The city streets..."
]

Do not include any other json fields; it must be a simple list of strings. Respond in pure, valid JSON. Do not lose any information from the original outline.
"""

SCENE_OUTLINE_TO_SCENE = """
# CONTEXT
You are a creative writer. I need your help writing a full scene based on the scene outline below.
Here is a summary of the story and relevant events so far:
---
{narrative_context}
---

# STYLE GUIDE
---
{style_guide}
---

# OBJECTIVE
Write a full, engaging scene based on the following scene outline. Include dialogue, character actions, thoughts, and descriptions as appropriate.

<SCENE_OUTLINE>
{_SceneOutline}
</SCENE_OUTLINE>

Your writing style must adhere to the **STYLE GUIDE**. Show, don't tell. Focus on psychological depth and sensory details.
Output only the scene's text.
"""

CONTINUE_SCENE_PIECE_PROMPT = """
# CONTEXT
You are writing a scene for a novel, continuing from where the last writer left off.
Here is a summary of what has happened in the scene so far:
---
{summary_of_previous_pieces}
---

# SCENE GOALS
This is the overall outline for the *entire* scene you are writing. Use it to understand the scene's ultimate destination.
---
{_SceneOutline}
---

# STYLE GUIDE
---
{style_guide}
---

# YOUR TASK
Write the very next part of the scene, picking up *immediately* where the previous part left off.
- Write approximately 300-400 words.
- Your writing must flow seamlessly from the summary of the previous pieces.
- Continue to advance the plot and character development towards the goals in the **SCENE GOALS**.
- Adhere strictly to the **STYLE GUIDE**.

Do not repeat what has already happened. Do not summarize. Do not add author notes. Write only the next block of prose for the scene.
"""

IS_SCENE_COMPLETE_PROMPT = """
You are a story structure analyst. You need to determine if a scene has reached a satisfactory conclusion based on its objectives.

# SCENE OUTLINE / GOALS
This is what the scene was supposed to accomplish.
---
{_SceneOutline}
---

# GENERATED SCENE TEXT
This is the full text of the scene that has been written so far.
---
{full_scene_text}
---

# YOUR TASK
Has the "GENERATED SCENE TEXT" fully and satisfactorily accomplished all the key objectives described in the "SCENE OUTLINE / GOALS"?
- Consider if the plot points have been addressed and character moments have occurred.
- Consider if the scene has reached a logical stopping point or a natural transition point.

Respond with a single JSON object with one key, "IsComplete", and a boolean value (true/false).
Do not include any other text. Example: `{{ "IsComplete": true }}`
"""

```

## File: `Writer/Scrubber.py`

```python
#!/usr/bin/python3

import Writer.Config
import Writer.Prompts
import Writer.Statistics
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext
from Writer.PrintUtils import Logger


def ScrubNovel(
    Interface: Interface, _Logger: Logger, narrative_context: NarrativeContext
) -> NarrativeContext:
    """
    Cleans up the final generated chapters by removing any leftover outlines,
    editorial comments, or other LLM artifacts.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        narrative_context: The context object containing the chapters to be scrubbed.

    Returns:
        The updated NarrativeContext object with scrubbed chapters.
    """
    _Logger.Log("Starting novel scrubbing pass...", 2)

    total_chapters = len(narrative_context.chapters)
    if total_chapters == 0:
        _Logger.Log("No chapters found in context to scrub.", 6)
        return narrative_context

    for chapter in narrative_context.chapters:
        chapter_num = chapter.chapter_number
        original_content = chapter.generated_content

        if not original_content:
            _Logger.Log(f"Chapter {chapter_num} has no content to scrub. Skipping.", 6)
            continue
        
        _Logger.Log(f"Scrubbing Chapter {chapter_num}/{total_chapters}...", 5)

        prompt = Writer.Prompts.CHAPTER_SCRUB_PROMPT.format(_Chapter=original_content)
        
        messages = [Interface.BuildUserQuery(prompt)]
        
        # --- FIX: Implement robust word count target for scrubbing ---
        # Calculate the original word count to prevent the chapter from being overwritten by a short, failed response.
        original_word_count = Writer.Statistics.GetWordCount(original_content)
        
        # Set a safe minimum word count for the scrubbed output. It should be a large fraction of the original.
        # We set a floor of 50 words to handle very short chapters.
        min_word_target = max(50, int(original_word_count * 0.8))
        _Logger.Log(f"Scrubbing Chapter {chapter_num} with a minimum word target of {min_word_target} (original was {original_word_count}).", 1)

        # SafeGenerateText ensures we get a response that meets the robust word count target.
        # Scrubbing is non-creative, so no critique cycle is needed.
        messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.SCRUB_MODEL, min_word_count_target=min_word_target
        )
        
        scrubbed_content = Interface.GetLastMessageText(messages)
        
        # Update the chapter content in the narrative context object
        chapter.set_generated_content(scrubbed_content)

        # Log the change in word count
        new_word_count = Writer.Statistics.GetWordCount(scrubbed_content)
        _Logger.Log(f"Finished scrubbing Chapter {chapter_num}. New word count: {new_word_count}", 3)

    _Logger.Log("Finished scrubbing all chapters.", 2)
    return narrative_context


```

## File: `Writer/Statistics.py`

```python
#!/usr/bin/python3

def GetWordCount(_Text: str) -> int:
    """
    Calculates the total number of words in a given string.
    Words are determined by splitting the string by whitespace.

    Args:
        _Text: The string to be analyzed.

    Returns:
        The integer word count. Returns 0 if input is not a string.
    """
    if not isinstance(_Text, str):
        return 0
    return len(_Text.split())


```

## File: `Writer/StoryInfo.py`

```python
#!/usr/bin/python3

import json
import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def GetStoryInfo(Interface: Interface, _Logger: Logger, _Messages: list) -> dict:
    """
    Generates final story information (Title, Summary, Tags) using an LLM.
    This is a non-creative, JSON-focused task.
    """
    prompt = Writer.Prompts.STATS_PROMPT

    _Logger.Log("Prompting LLM to generate story info (JSON)...", 5)

    # We append the stats prompt to the existing message history to give the LLM
    # the full context of the generated story.
    _Messages.append(Interface.BuildUserQuery(prompt))

    # Use SafeGenerateJSON to handle the request. It will retry if the JSON is invalid.
    # We require the main keys to be present in the response.
    _, response_json = Interface.SafeGenerateJSON(
        _Logger,
        _Messages,
        Writer.Config.INFO_MODEL,
        _RequiredAttribs=["Title", "Summary", "Tags", "OverallRating"]
    )

    _Logger.Log("Finished getting story info.", 5)
    
    # Return the validated JSON dictionary, or an empty dict if something went wrong
    # (though SafeGenerateJSON is designed to prevent that).
    return response_json if isinstance(response_json, dict) else {}

```

## File: `Writer/SummarizationUtils.py`

```python
#!/usr/bin/python3

import json
import Writer.Config
import Writer.Prompts
import Writer.CritiqueRevision
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from Writer.NarrativeContext import NarrativeContext

def summarize_scene_piece(
    Interface: Interface,
    _Logger: Logger,
    scene_piece_text: str
) -> str:
    """
    Creates a very concise summary of a small piece of a scene.
    This is a fast, non-creative task intended to provide immediate context
    for the next piece in a scene generation loop. It does not use critique/revision.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        scene_piece_text: The text of the scene chunk to summarize.

    Returns:
        A short, 1-2 sentence summary of the scene piece.
    """
    _Logger.Log("Summarizing scene piece for iterative context...", 1)
    prompt = Writer.Prompts.SUMMARIZE_SCENE_PIECE_PROMPT.format(scene_piece_text=scene_piece_text)
    messages = [Interface.BuildUserQuery(prompt)]

    # This is a simple, non-creative task. We expect a very short response.
    # We use SafeGenerateText with a low word count target.
    response_history = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHECKER_MODEL, min_word_count_target=10
    )
    summary = Interface.GetLastMessageText(response_history)

    if "[ERROR:" in summary:
        _Logger.Log("Failed to summarize scene piece. Returning empty string.", 7)
        return ""

    return summary.strip()


def summarize_scene_and_extract_key_points(
    Interface: Interface,
    _Logger: Logger,
    scene_text: str,
    narrative_context: NarrativeContext,
    chapter_num: int,
    scene_num: int
) -> dict:
    """
    Generates a final, holistic summary for a fully assembled scene and extracts key points.
    This is a creative/analytical task and will undergo critique and revision.

    Returns:
        A dictionary with "summary" and "key_points_for_next_scene".
    """
    _Logger.Log(f"Generating final summary for Chapter {chapter_num}, Scene {scene_num}", 4)

    # Prepare context for the summarization task
    task_description = f"You are summarizing scene {scene_num} of chapter {chapter_num}. The goal is to create a concise summary of the scene's events and to identify key plot points, character changes, or unresolved tensions that must be carried into the next scene to maintain narrative continuity."

    context_summary = narrative_context.get_full_story_summary_so_far(chapter_num)
    if chapter_ctx := narrative_context.get_chapter(chapter_num):
        if scene_num > 1:
            if prev_scene := chapter_ctx.get_scene(scene_num - 1):
                if prev_scene.final_summary:
                    context_summary += f"\nImmediately preceding this scene (C{chapter_num} S{scene_num-1}):\n{prev_scene.final_summary}"

    prompt = Writer.Prompts.SUMMARIZE_SCENE_PROMPT.format(scene_text=scene_text)
    messages = [Interface.BuildSystemQuery(Writer.Prompts.LITERARY_STYLE_GUIDE), Interface.BuildUserQuery(prompt)]

    _Logger.Log("Generating initial summary and key points...", 5)
    _, initial_summary_json = Interface.SafeGenerateJSON(
        _Logger, messages, Writer.Config.CHECKER_MODEL, _RequiredAttribs=["summary", "key_points_for_next_scene"]
    )
    initial_summary_text = json.dumps(initial_summary_json, indent=2)
    _Logger.Log("Initial summary and key points generated.", 5)

    # Critique and revise the summary for quality and coherence
    revised_summary_text = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_summary_text,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
        style_guide=narrative_context.style_guide,
        is_json=True
    )

    try:
        final_summary_data = json.loads(revised_summary_text)
        if "summary" not in final_summary_data or "key_points_for_next_scene" not in final_summary_data:
             _Logger.Log("Revised summary JSON is missing required keys. Falling back to initial summary.", 7)
             return initial_summary_json

        _Logger.Log(f"Successfully generated and revised final summary for C{chapter_num} S{scene_num}.", 4)
        return final_summary_data
    except json.JSONDecodeError as e:
        _Logger.Log(f"Failed to parse final revised summary JSON: {e}. Falling back to initial summary.", 7)
        return initial_summary_json


def summarize_chapter(
    Interface: Interface,
    _Logger: Logger,
    chapter_text: str,
    narrative_context: NarrativeContext,
    chapter_num: int
) -> str:
    """
    Summarizes the content of a full chapter.
    This is a creative/analytical task and will undergo critique and revision.

    Returns:
        A string containing the chapter summary.
    """
    _Logger.Log(f"Generating summary for Chapter {chapter_num}", 4)

    task_description = f"You are summarizing the key events, character developments, and plot advancements of chapter {chapter_num} of a novel."
    context_summary = narrative_context.get_full_story_summary_so_far(chapter_num)

    prompt = Writer.Prompts.SUMMARIZE_CHAPTER_PROMPT.format(chapter_text=chapter_text)
    messages = [Interface.BuildSystemQuery(Writer.Prompts.LITERARY_STYLE_GUIDE), Interface.BuildUserQuery(prompt)]

    _Logger.Log("Generating initial chapter summary...", 5)
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHECKER_MODEL, min_word_count_target=50
    )
    initial_summary = Interface.GetLastMessageText(messages)
    _Logger.Log("Initial chapter summary generated.", 5)

    revised_summary = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_summary,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
        style_guide=narrative_context.style_guide,
        is_json=False
    )

    _Logger.Log(f"Successfully generated and revised summary for Chapter {chapter_num}.", 4)
    return revised_summary

```

## File: `Writer/Translator.py`

```python
import Writer.PrintUtils
import Writer.Config
import Writer.Prompts


def TranslatePrompt(Interface, _Logger, _Prompt: str, _Language: str = "French"):

    Prompt: str = Writer.Prompts.TRANSLATE_PROMPT.format(
        _Prompt=_Prompt, _Language=_Language
    )
    _Logger.Log("Prompting LLM To Translate User Prompt", 5)
    Messages = []
    Messages.append(Interface.BuildUserQuery(Prompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.TRANSLATOR_MODEL, min_word_count_target=50
    )
    _Logger.Log("Finished Prompt Translation", 5)

    return Interface.GetLastMessageText(Messages)


def TranslateNovel(
    Interface, _Logger, _Chapters: list, _TotalChapters: int, _Language: str = "French"
):

    EditedChapters = _Chapters

    for i in range(_TotalChapters):

        Prompt: str = Writer.Prompts.CHAPTER_TRANSLATE_PROMPT.format(
            _Chapter=EditedChapters[i], _Language=_Language
        )
        _Logger.Log(f"Prompting LLM To Perform Chapter {i+1} Translation", 5)
        Messages = []
        Messages.append(Interface.BuildUserQuery(Prompt))
        Messages = Interface.SafeGenerateText(
            _Logger, Messages, Writer.Config.TRANSLATOR_MODEL
        )
        _Logger.Log(f"Finished Chapter {i+1} Translation", 5)

        NewChapter = Interface.GetLastMessageText(Messages)
        EditedChapters[i] = NewChapter
        ChapterWordCount = Writer.Statistics.GetWordCount(NewChapter)
        _Logger.Log(f"Translation Chapter Word Count: {ChapterWordCount}", 3)

    return EditedChapters

```

## File: `.gitignore`

```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/#use-with-ide
.pdm.toml

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
#.idea/


Stories/*
Prompts/*
Premises/*
PremiseGenLogs/*
PromptGenLogs/*
/Short_Story/*
/Web_Novel_Chapters/*
Logs/*
EvalLogs/*
node_modules/*
package-lock.json
.github/Improvements
.github/improvements/prompt*
.vscode

```

## File: `Evaluate.py`

```python
#!/usr/bin/python3

import argparse
import time
import json
import os

import Writer.Config
import Writer.Interface.Wrapper
import Writer.PrintUtils

# --- Main Evaluation Functions ---

def EvaluateOutline(_Client: Writer.Interface.Wrapper.Interface, _Logger: Writer.PrintUtils.Logger, _Outline1: str, _Outline2: str):
    """
    Compares two different outlines using an LLM to determine which is better based on several criteria.
    """
    _Logger.Log("Evaluating outlines...", 4)
    
    prompt = f"""
Please evaluate which of the following two outlines is better written for a novel.

<OUTLINE_A>
{_Outline1}
</OUTLINE_A>

<OUTLINE_B>
{_Outline2}
</OUTLINE_B>

Use the following criteria to evaluate. For each criterion, choose A, B, or Tie.
- **Plot**: Coherence, creativity, and engagement of the plot.
- **Chapters**: Logical flow between chapters, uniqueness of each chapter.
- **Style**: Clarity and effectiveness of the writing style.
- **Tropes**: Interesting and well-integrated use of genre tropes.
- **Genre**: Clarity and consistency of the story's genre.
- **Narrative Structure**: The underlying structure and its suitability for the story.

Please give your response in a valid JSON format with no other text:

{{
    "Thoughts": "Your overall notes and reasoning on which of the two is better and why.",
    "Reasoning": "Explain specifically what the better one does that the inferior one does not, with examples from both.",
    "Plot": "<A, B, or Tie>",
    "PlotExplanation": "Explain your reasoning.",
    "Style": "<A, B, or Tie>",
    "StyleExplanation": "Explain your reasoning.",
    "Chapters": "<A, B, or Tie>",
    "ChaptersExplanation": "Explain your reasoning.",
    "Tropes": "<A, B, or Tie>",
    "TropesExplanation": "Explain your reasoning.",
    "Genre": "<A, B, or Tie>",
    "GenreExplanation": "Explain your reasoning.",
    "Narrative": "<A, B, or Tie>",
    "NarrativeExplanation": "Explain your reasoning.",
    "OverallWinner": "<A, B, or Tie>"
}}
"""
    
    messages = [
        _Client.BuildSystemQuery("You are a helpful AI language model and literary critic."),
        _Client.BuildUserQuery(prompt)
    ]
    
    _, response_json = _Client.SafeGenerateJSON(_Logger, messages, Args.Model)
    
    # Format the report from the JSON
    report = ""
    for key, value in response_json.items():
        if "Explanation" not in key and key not in ["Thoughts", "Reasoning"]:
            report += f"- Winner of {key}: {value}\n"
            
    _Logger.Log("Finished evaluating outlines.", 4)
    return report, response_json


def EvaluateChapter(_Client: Writer.Interface.Wrapper.Interface, _Logger: Writer.PrintUtils.Logger, _ChapterA: str, _ChapterB: str):
    """
    Compares two different, separate chapters using an LLM to determine which is better written.
    """
    _Logger.Log("Evaluating chapters...", 4)

    # CORRECTED PROMPT
    prompt = f"""
Please evaluate which of the two separate and unrelated chapters below is better written.

<CHAPTER_A>
{_ChapterA}
---END OF CHAPTER A---
</CHAPTER_A>

<CHAPTER_B>
{_ChapterB}
---END OF CHAPTER B---
</CHAPTER_B>

Use the following criteria to evaluate. For each criterion, choose A, B, or Tie.
- **Plot**: Coherence and creativity of the plot within the chapter.
- **Style**: Effectiveness of the prose, pacing, and description.
- **Dialogue**: Believability, character-specificity, and purpose of the dialogue.
- **Tropes**: Interesting and well-integrated use of genre tropes.
- **Genre**: Clarity and consistency of the chapter's genre.
- **Narrative Structure**: The underlying structure and its suitability for the chapter's content.

Please provide your response in a valid JSON format with no other text.

{{
    "Thoughts": "Your overall notes and reasoning on which of the two is better and why.",
    "Plot": "<A, B, or Tie>",
    "PlotExplanation": "Explain your reasoning.",
    "Style": "<A, B, or Tie>",
    "StyleExplanation": "Explain your reasoning.",
    "Dialogue": "<A, B, or Tie>",
    "DialogueExplanation": "Explain your reasoning.",
    "Tropes": "<A, B, or Tie>",
    "TropesExplanation": "Explain your reasoning.",
    "Genre": "<A, B, or Tie>",
    "GenreExplanation": "Explain your reasoning.",
    "Narrative": "<A, B, or Tie>",
    "NarrativeExplanation": "Explain your reasoning.",
    "OverallWinner": "<A, B, or Tie>"
}}

Remember, these are two separate renditions of a chapter for similar stories; they are not sequential.
"""
    
    messages = [
        _Client.BuildSystemQuery("You are a helpful AI language model and literary critic."),
        _Client.BuildUserQuery(prompt)
    ]
    
    _, response_json = _Client.SafeGenerateJSON(_Logger, messages, Args.Model)
    
    # Format the report from the JSON
    report = ""
    for key, value in response_json.items():
        if "Explanation" not in key and key not in ["Thoughts"]:
             report += f"- Winner of {key}: {value}\n"
    
    _Logger.Log("Finished evaluating chapters.", 4)
    return report, response_json


# --- Main Execution Block ---

if __name__ == "__main__":
    # Setup Argparser
    Parser = argparse.ArgumentParser(description="Evaluate and compare two generated stories.")
    Parser.add_argument("-Story1", required=True, help="Path to JSON file for story 1")
    Parser.add_argument("-Story2", required=True, help="Path to JSON file for story 2")
    Parser.add_argument("-Output", default="Report.md", type=str, help="Optional file output path for the report.")
    Parser.add_argument("-Model", default="google://gemini-1.5-pro-latest", type=str, help="Model to use for the evaluation.")
    Args = Parser.parse_args()

    # Measure Generation Time
    StartTime_s = time.time()

    # Setup Logger and Interface
    Logger = Writer.PrintUtils.Logger("EvalLogs")
    Logger.Log(f"Starting evaluation with model: {Args.Model}", 2)
    Interface = Writer.Interface.Wrapper.Interface([Args.Model])

    # Load story data from JSON files
    try:
        with open(Args.Story1, "r", encoding='utf-8') as f:
            Story1 = json.load(f)
        with open(Args.Story2, "r", encoding='utf-8') as f:
            Story2 = json.load(f)
    except FileNotFoundError as e:
        Logger.Log(f"Error: Story file not found - {e}", 7)
        exit(1)
    except json.JSONDecodeError as e:
        Logger.Log(f"Error: Could not parse story JSON file - {e}", 7)
        exit(1)

    # Begin Report
    Report = f"# Fiction Fabricator - Story Evaluation Report\n\n"
    Report += f"**Story A:** `{Args.Story1}`\n"
    Report += f"**Story B:** `{Args.Story2}`\n\n---\n\n"

    # Evaluate Outlines
    Report += "## Outline Comparison\n"
    OutlineReport, _ = EvaluateOutline(Interface, Logger, Story1.get("Outline", ""), Story2.get("Outline", ""))
    Report += OutlineReport + "\n\n"

    # Evaluate Chapters
    shortest_story_len = min(len(Story1.get("UnscrubbedChapters", [])), len(Story2.get("UnscrubbedChapters", [])))
    if shortest_story_len > 0:
        Report += "---\n\n## Chapter-by-Chapter Comparison\n"
        for i in range(shortest_story_len):
            Report += f"### Chapter {i+1}\n"
            ChapterReport, _ = EvaluateChapter(Interface, Logger, Story1["UnscrubbedChapters"][i], Story2["UnscrubbedChapters"][i])
            Report += ChapterReport + "\n"

    # Final Vote Tally
    Report += "\n---\n\n## Vote Totals\n"
    Report += f"- **Total A Wins:** {Report.count(': A')}\n"
    Report += f"- **Total B Wins:** {Report.count(': B')}\n"
    Report += f"- **Total Ties:** {Report.count(': Tie')}\n"

    # Calculate and log total evaluation time
    EndTime_s = time.time()
    TotalEvalTime_s = round(EndTime_s - StartTime_s)
    Logger.Log(f"Evaluation finished in {TotalEvalTime_s} seconds.", 2)
    Report += f"\n*Evaluation completed in {TotalEvalTime_s} seconds using model `{Args.Model}`.*"

    # Write Report To Disk
    try:
        with open(Args.Output, "w", encoding='utf-8') as f:
            f.write(Report)
        Logger.Log(f"Evaluation report saved to {Args.Output}", 5)
    except IOError as e:
        Logger.Log(f"Error saving report to file: {e}", 7)

    print("\n--- Evaluation Complete ---")
    print(f"Report saved to {Args.Output}")

```

## File: `README.md`

```markdown
# Fiction Fabricator

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

Fiction Fabricator is an advanced, AI-powered framework for generating complete, multi-chapter novels, short stories, and episodic web novel chapters from creative prompts. It leverages a suite of modern Language Learning Models (LLMs) through a unified interface, employing a sophisticated, multi-stage pipeline of outlining, scene-by-scene generation, and iterative revision to produce high-quality, coherent long-form narratives.

## Acknowledgement of Origin

This project is a significantly modified and enhanced fork of **[AIStoryteller by datacrystals](httpss://github.com/datacrystals/AIStoryteller)**. I would like to expressing extend my immense gratitude to the original author for providing the foundational concepts and architecture. Fiction Fabricator builds upon that excellent groundwork with new features, a refactored generation pipeline, and a robust, multi-provider backend to suit a different set of use cases focused on flexibility, quality, and developer control.

---

## Full Documentation

For detailed guides on how to install, configure, and use Fiction Fabricator—including its new short story and web novel tools—please see the full documentation linked below.

- **[1. Introduction and Features](./.github/documentation/1_introduction_and_features.md)**
- **[2. Installation Guide](./.github/documentation/2_installation_guide.md)**
- **[3. Configuration Guide](./.github/documentation/3_configuration_guide.md)**
- **[4. Usage Workflow](./.github/documentation/4_usage_workflow.md)**
- **[5. Advanced Tools](./.github/documentation/5_advanced_tools.md)**

---

This project is designed to be a powerful, flexible, and transparent tool for creating long-form fiction with AI. We welcome feedback and hope you find it useful.

```

## File: `Write.py`

```python
#!/usr/bin/python3
import argparse
import time
import datetime
import os
import sys
import json
import dotenv
import termcolor

# --- Explicitly load the .env file from the project root and add verbose logging ---
# This makes the script runnable from any directory and provides clear debug info.
print(termcolor.colored("--- Initializing Environment ---", "yellow"))
try:
    project_root = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(project_root, '.env')
    if os.path.exists(dotenv_path):
        dotenv.load_dotenv(dotenv_path=dotenv_path, verbose=True)
        print(termcolor.colored(f"[ENV] Attempted to load .env file from: {dotenv_path}", "cyan"))
        # Explicitly check for NVIDIA keys right after loading
        if os.environ.get("NVIDIA_API_KEY"):
            print(termcolor.colored("[ENV] NVIDIA_API_KEY: Found", "green"))
        else:
            print(termcolor.colored("[ENV] NVIDIA_API_KEY: NOT FOUND in environment", "red"))
        if os.environ.get("NVIDIA_BASE_URL"):
            print(termcolor.colored("[ENV] NVIDIA_BASE_URL: Found", "green"))
        else:
            print(termcolor.colored("[ENV] NVIDIA_BASE_URL: NOT FOUND in environment", "red"))
    else:
        print(termcolor.colored(f"[ENV] .env file not found at: {dotenv_path}", "red"))
except Exception as e:
    print(termcolor.colored(f"--- Error loading .env file: {e} ---", "red"))
print(termcolor.colored("--------------------------------", "yellow"))


import Writer.Config
import Writer.Interface.Wrapper
import Writer.PrintUtils
import Writer.Scrubber
import Writer.Statistics
import Writer.OutlineGenerator
import Writer.Chapter.ChapterGenerator
import Writer.StoryInfo
import Writer.NovelEditor
import Writer.Prompts
from Writer.NarrativeContext import NarrativeContext

def get_ollama_models(logger):
    try:
        import ollama
        logger.Log("Querying Ollama for local models...", 1)
        models_data = ollama.list().get("models", [])
        available_models = [f"ollama://{model.get('name') or model.get('model')}" for model in models_data if model.get('name') or model.get('model')]
        print(f"-> Ollama: Found {len(available_models)} models.")
        return available_models
    except Exception as e:
        logger.Log(f"Could not get Ollama models. (Error: {e})", 6)
        return []

def get_google_models(logger):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("-> Google: GOOGLE_API_KEY not found in .env file. Skipping.")
        return []
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        logger.Log("Querying Google for available Gemini models...", 1)
        available = [f"google://{m.name.replace('models/', '')}" for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"-> Google: Found {len(available)} models.")
        return available
    except Exception as e:
        logger.Log(f"Failed to query Google models. (Error: {e})", 6)
        return []

def get_groq_models(logger):
    if not os.environ.get("GROQ_API_KEY"):
        print("-> GroqCloud: GROQ_API_KEY not found in .env file. Skipping.")
        return []
    try:
        from groq import Groq
        logger.Log("Querying GroqCloud for available models...", 1)
        client = Groq()
        models = client.models.list().data
        print(f"-> GroqCloud: Found {len(models)} models.")
        return [f"groq://{model.id}" for model in models]
    except Exception as e:
        logger.Log(f"Failed to query GroqCloud models. (Error: {e})", 6)
        return []

def get_mistral_models(logger):
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("-> MistralAI: MISTRAL_API_KEY not found in .env file. Skipping.")
        return []
    try:
        from mistralai.client import MistralClient
        logger.Log("Querying MistralAI for available models...", 1)
        client = MistralClient(api_key=api_key)
        models_data = client.list_models().data
        known_chat_prefixes = ['mistral-large', 'mistral-medium', 'mistral-small', 'open-mistral', 'open-mixtral']
        available_models = [f"mistralai://{model.id}" for model in models_data if any(model.id.startswith(prefix) for prefix in known_chat_prefixes)]
        print(f"-> MistralAI: Found {len(available_models)} compatible models.")
        return available_models
    except Exception as e:
        logger.Log(f"Failed to query MistralAI models. (Error: {e})", 6)
        return []

def get_nvidia_models(logger):
    """Reads the user-defined NVIDIA models from config.ini."""
    if not os.environ.get("NVIDIA_API_KEY"):
        logger.Log("NVIDIA provider skipped: NVIDIA_API_KEY not found in environment.", 6)
        return []
    
    logger.Log("Reading manual NVIDIA model list from config.ini...", 1)
    model_list_str = Writer.Config.NVIDIA_AVAILABLE_MODELS
    if not model_list_str:
        logger.Log("NVIDIA provider skipped: No models listed in config.ini under [NVIDIA_SETTINGS] -> 'available_models'.", 6)
        return []
    
    model_names = [name.strip() for name in model_list_str.split(',') if name.strip()]
    available_models = [f"nvidia://{name}" for name in model_names]
    logger.Log(f"Found {len(available_models)} NVIDIA models in config.ini.", 3)
    return available_models

def get_github_models(logger):
    """Returns a static list of available GitHub models, checking for required env vars."""
    if not os.environ.get("GITHUB_ACCESS_TOKEN") or not os.environ.get("AZURE_OPENAI_ENDPOINT"):
        logger.Log("GitHub provider skipped: GITHUB_ACCESS_TOKEN or AZURE_OPENAI_ENDPOINT not found in environment.", 6)
        return []

    logger.Log("Loading GitHub model list...", 1)
    
    # Static list of the exact deployment names for models from the GitHub Marketplace.
    deployment_names = [
        "openai/o1", "openai/o1-mini", "openai/o1-preview", "openai/gpt-4o-mini", "openai/gpt-4o",
        "deepseek/DeepSeek-V3-0324", "deepseek/DeepSeek-R1",
        "ai21-labs/AI21-Jamba-1.5-Large", "ai21-labs/AI21-Jamba-1.5-Mini",
        "cohere/cohere-command-r", "cohere/cohere-command-r-plus", "cohere/cohere-command-a",
        "mistral-ai/Mistral-Nemo", "mistral-ai/Mistral-Small",
        "mistral-ai/Mistral-Large-2411", "mistral-ai/Codestral-22B-v0.1",
        "meta/Llama-3.2-11B-Vision-Instruct", "meta/Llama-3.2-90B-Vision-Instruct",
        "meta/Llama-3.3-70B-Instruct", "meta/Llama-3.1-8B-Instruct",
        "meta/Llama-3.1-70B-Instruct", "meta/Llama-3.1-405B-Instruct",
        "meta/Llama-3-8B-Instruct", "meta/Llama-3-70B-Instruct",
        "microsoft/Phi-4", "microsoft/Phi-3.5-MoE-instruct",
        "microsoft/Phi-3.5-mini-instruct", "microsoft/Phi-3.5-vision-instruct",
        "microsoft/Phi-3-mini-4k-instruct", "microsoft/Phi-3-mini-128k-instruct",
        "microsoft/Phi-3-small-8k-instruct", "microsoft/Phi-3-small-128k-instruct",
        "microsoft/Phi-3-medium-4k-instruct", "microsoft/Phi-3-medium-128k-instruct",
        "xai/grok-3",
        "core42/jais-30b-chat"
    ]
    
    available_models = [f"github://{name}" for name in deployment_names]
    logger.Log(f"Found {len(available_models)} GitHub models.", 3)
    return available_models

def get_llm_selection_menu_dynamic(logger):
    print("\n--- Querying available models from configured providers... ---")
    all_models = []
    all_models.extend(get_google_models(logger))
    all_models.extend(get_groq_models(logger))
    all_models.extend(get_mistral_models(logger))
    all_models.extend(get_nvidia_models(logger))
    all_models.extend(get_github_models(logger))
    all_models.extend(get_ollama_models(logger))
    if not all_models:
        logger.Log("No models found from any provider. Please check API keys in .env and model lists in config.ini.", 7)
        return {}
    print("\n--- Fiction Fabricator LLM Selection ---")
    print("Please select the primary model for writing:")
    sorted_models = sorted(all_models)
    for i, model in enumerate(sorted_models):
        print(f"[{i+1}] {model}")
    print("[c] Custom (use settings from config.ini or command-line args)")
    choice = input("> ").strip().lower()
    if choice.isdigit() and 1 <= int(choice) <= len(sorted_models):
        selected_model = sorted_models[int(choice) - 1]
        print(f"Selected: {selected_model}")
        return {'INITIAL_OUTLINE_WRITER_MODEL':selected_model, 'CHAPTER_OUTLINE_WRITER_MODEL':selected_model, 'CHAPTER_STAGE1_WRITER_MODEL':selected_model, 'CHAPTER_STAGE2_WRITER_MODEL':selected_model, 'CHAPTER_STAGE3_WRITER_MODEL':selected_model, 'CHAPTER_STAGE4_WRITER_MODEL':selected_model, 'CHAPTER_REVISION_WRITER_MODEL':selected_model, 'CRITIQUE_LLM':selected_model, 'REVISION_MODEL':selected_model, 'EVAL_MODEL':selected_model, 'INFO_MODEL':selected_model, 'SCRUB_MODEL':selected_model, 'CHECKER_MODEL':selected_model}
    else:
        print("Invalid choice or 'c' selected. Using custom/default configuration.")
        return {}

def main():
    Parser = argparse.ArgumentParser(description=f"Run the {Writer.Config.PROJECT_NAME} novel generation pipeline.")
    Parser.add_argument("-Prompt", required=True)
    Parser.add_argument("-Output", default="", type=str)
    Parser.add_argument("-Seed", default=Writer.Config.SEED, type=int)
    Parser.add_argument("-Debug", action="store_true", default=Writer.Config.DEBUG)
    Parser.add_argument("-InitialOutlineModel", default=Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterOutlineModel", default=Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS1Model", default=Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS2Model", default=Writer.Config.CHAPTER_STAGE2_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS3Model", default=Writer.Config.CHAPTER_STAGE3_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS4Model", default=Writer.Config.CHAPTER_STAGE4_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterRevisionModel", default=Writer.Config.CHAPTER_REVISION_WRITER_MODEL, type=str)
    Parser.add_argument("-CritiqueLLM", default=Writer.Config.CRITIQUE_LLM, type=str)
    Parser.add_argument("-RevisionModel", default=Writer.Config.REVISION_MODEL, type=str)
    Parser.add_argument("-EvalModel", default=Writer.Config.EVAL_MODEL, type=str)
    Parser.add_argument("-InfoModel", default=Writer.Config.INFO_MODEL, type=str)
    Parser.add_argument("-ScrubModel", default=Writer.Config.SCRUB_MODEL, type=str)
    Parser.add_argument("-CheckerModel", default=Writer.Config.CHECKER_MODEL, type=str)
    Parser.add_argument("-OutlineMinRevisions", default=Writer.Config.OUTLINE_MIN_REVISIONS, type=int)
    Parser.add_argument("-OutlineMaxRevisions", default=Writer.Config.OUTLINE_MAX_REVISIONS, type=int)
    Parser.add_argument("-ChapterMinRevisions", default=Writer.Config.CHAPTER_MIN_REVISIONS, type=int)
    Parser.add_argument("-ChapterMaxRevisions", default=Writer.Config.CHAPTER_MAX_REVISIONS, type=int)
    Parser.add_argument("-MinChapters", default=Writer.Config.MINIMUM_CHAPTERS, type=int)
    Parser.add_argument("-NoChapterRevision", action="store_true", default=Writer.Config.CHAPTER_NO_REVISIONS)
    Parser.add_argument("-NoScrubChapters", action="store_true", default=Writer.Config.SCRUB_NO_SCRUB)
    Parser.add_argument("-NoExpandOutline", action="store_false", dest="ExpandOutline", default=Writer.Config.EXPAND_OUTLINE)
    Parser.add_argument("-EnableFinalEditPass", action="store_true", default=Writer.Config.ENABLE_FINAL_EDIT_PASS)
    Parser.add_argument("-NoSceneGenerationPipeline", action="store_false", dest="SceneGenerationPipeline", default=Writer.Config.SCENE_GENERATION_PIPELINE)
    Args = Parser.parse_args()

    StartTime = time.time()
    SysLogger = Writer.PrintUtils.Logger()
    SysLogger.Log(f"Welcome to {Writer.Config.PROJECT_NAME}!", 2)

    selected_models = get_llm_selection_menu_dynamic(SysLogger)
    if not selected_models:
        SysLogger.Log("No model was selected or discovered. Using models from config/args.", 4)
    else:
        for key, value in selected_models.items():
            setattr(Writer.Config, key.upper(), value)

    for arg, value in vars(Args).items():
        if hasattr(Writer.Config, arg.upper()) and value != Parser.get_default(arg):
            setattr(Writer.Config, arg.upper(), value)

    Writer.Config.CHAPTER_NO_REVISIONS = Args.NoChapterRevision
    Writer.Config.SCRUB_NO_SCRUB = Args.NoScrubChapters
    Writer.Config.EXPAND_OUTLINE = Args.ExpandOutline
    Writer.Config.ENABLE_FINAL_EDIT_PASS = Args.EnableFinalEditPass
    Writer.Config.SCENE_GENERATION_PIPELINE = Args.SceneGenerationPipeline
    Writer.Config.DEBUG = Args.Debug
    Writer.Config.OPTIONAL_OUTPUT_NAME = Args.Output
    Writer.Config.MINIMUM_CHAPTERS = Args.MinChapters

    models_to_load = list(set([Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, Writer.Config.CHAPTER_STAGE2_WRITER_MODEL, Writer.Config.CHAPTER_STAGE3_WRITER_MODEL, Writer.Config.CHAPTER_STAGE4_WRITER_MODEL, Writer.Config.CHAPTER_REVISION_WRITER_MODEL, Writer.Config.CRITIQUE_LLM, Writer.Config.REVISION_MODEL, Writer.Config.EVAL_MODEL, Writer.Config.INFO_MODEL, Writer.Config.SCRUB_MODEL, Writer.Config.CHECKER_MODEL]))
    Interface = Writer.Interface.Wrapper.Interface(models_to_load)

    try:
        with open(Args.Prompt, "r", encoding='utf-8') as f:
            Prompt = f.read()
    except FileNotFoundError:
        SysLogger.Log(f"Error: Prompt file not found at {Args.Prompt}", 7)
        return

    # CORRECTED LINE: Pass the style_guide from Prompts.py during initialization.
    narrative_context = NarrativeContext(initial_prompt=Prompt, style_guide=Writer.Prompts.LITERARY_STYLE_GUIDE)
    narrative_context = Writer.OutlineGenerator.GenerateOutline(Interface, SysLogger, Prompt, narrative_context)
    SysLogger.Log("Starting Chapter Writing phase...", 2)
    total_chapters = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, SysLogger, narrative_context.base_novel_outline_markdown)
    if total_chapters > 0 and total_chapters < 100:
        for i in range(1, total_chapters + 1):
            Writer.Chapter.ChapterGenerator.GenerateChapter(Interface, SysLogger, i, total_chapters, narrative_context)
    else:
        SysLogger.Log(f"Invalid chapter count ({total_chapters}) detected. Aborting chapter generation.", 7)

    if Writer.Config.ENABLE_FINAL_EDIT_PASS:
        narrative_context = Writer.NovelEditor.EditNovel(Interface, SysLogger, narrative_context)
    if not Writer.Config.SCRUB_NO_SCRUB:
        narrative_context = Writer.Scrubber.ScrubNovel(Interface, SysLogger, narrative_context)
    else:
        SysLogger.Log("Skipping final scrubbing pass due to config.", 4)

    StoryBodyText = "\n\n\n".join([f"### Chapter {chap.chapter_number}\n\n{chap.generated_content}" for chap in narrative_context.chapters if chap.generated_content])
    
    info_messages = [Interface.BuildUserQuery(narrative_context.base_novel_outline_markdown)]
    Info = Writer.StoryInfo.GetStoryInfo(Interface, SysLogger, info_messages)
    Title = Info.get("Title", "Untitled Story")

    SysLogger.Log(f"Story Title: {Title}", 5)
    SysLogger.Log(f"Summary: {Info.get('Summary', 'N/A')}", 3)
    ElapsedTime = time.time() - StartTime
    TotalWords = Writer.Statistics.GetWordCount(StoryBodyText)
    SysLogger.Log(f"Total story word count: {TotalWords}", 4)

    StatsString = f"""
## Work Statistics
- **Title**: {Title}
- **Summary**: {Info.get('Summary', 'N/A')}
- **Tags**: {Info.get('Tags', 'N/A')}
- **Generation Time**: {ElapsedTime:.2f}s
- **Average WPM**: {60 * (TotalWords / ElapsedTime) if ElapsedTime > 0 else 0:.2f}
- **Generator**: {Writer.Config.PROJECT_NAME}

## Generation Settings
- **Base Prompt**: {Prompt[:150]}...
- **Seed**: {Writer.Config.SEED}
- **Primary Model Used**: {Writer.Config.INITIAL_OUTLINE_WRITER_MODEL} (and others if set by args)
"""

    os.makedirs("Stories", exist_ok=True)
    safe_title = "".join(c for c in Title if c.isalnum() or c in (' ', '_')).rstrip()
    file_name_base = f"Stories/{safe_title.replace(' ', '_')}"
    if Writer.Config.OPTIONAL_OUTPUT_NAME:
        file_name_base = f"Stories/{Writer.Config.OPTIONAL_OUTPUT_NAME}"
    
    md_file_path = f"{file_name_base}.md"
    json_file_path = f"{file_name_base}.json"

    # Write the Markdown file
    with open(md_file_path, "w", encoding="utf-8") as f:
        output_content = f"# {Title}\n\n{StoryBodyText}\n\n---\n\n{StatsString}\n\n---\n\n## Full Outline\n```\n{narrative_context.base_novel_outline_markdown}\n```"
        f.write(output_content)

    # Write the JSON file
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(narrative_context.to_dict(), f, indent=4)
    
    # Log the final, correct output paths
    SysLogger.Log("Generation complete!", 5)
    final_message = f"""
--------------------------------------------------
Output Files Saved:
- Markdown Story: {os.path.abspath(md_file_path)}
- JSON Data File: {os.path.abspath(json_file_path)}
--------------------------------------------------"""
    print(termcolor.colored(final_message, "green"))


if __name__ == "__main__":
    main()

```

## File: `config.ini`

```ini
; Fiction Fabricator Configuration File
; Lines starting with ; or # are comments.

[API_KEYS]
; Store your API keys in a .env file in the project root for better security.
; The application will automatically load a .env file if it exists.
;
; Example .env file content:
;
; GOOGLE_API_KEY="your_google_api_key"
; MISTRAL_API_KEY="your_mistral_api_key"
; GROQ_API_KEY="your_groq_api_key"
;
; For NVIDIA NIM endpoints, you must provide the API key.
; NVIDIA_API_KEY="nvapi-..."
;
; The Base URL can also be set in the .env file, which will override the
; value in [NVIDIA_SETTINGS] below.
; NVIDIA_BASE_URL="https://your-custom-nim-url.com/v1"
;
; For GitHub Models Marketplace, you must provide your GitHub Access Token
; and the correct endpoint URL.
; GITHUB_ACCESS_TOKEN="github_pat_..."
; AZURE_OPENAI_ENDPOINT="https://models.github.ai/inference"


[LLM_SELECTION]
; Specify the LLM models to be used for different tasks.
; The format is typically: provider://model_identifier
; Examples:
;   google://gemini-1.5-pro-latest
;   mistralai://mistral-large-latest
;   groq://mixtral-8x7b-32768
;   nvidia://meta/llama3-70b-instruct
;   github://o1-mini
;   ollama://llama3:70b
;   ollama://llama3:70b@192.168.1.100:11434 (for Ollama on a specific host)

; Model for generating critiques (used by CritiqueRevision.py)
critique_llm = google://gemini-1.5-flash-latest

; Models for various stages of story generation, matching Writer.Config.py variables
initial_outline_writer_model = google://gemini-1.5-pro-latest
chapter_outline_writer_model = google://gemini-1.5-flash-latest
chapter_stage1_writer_model = google://gemini-1.5-flash-latest
chapter_stage2_writer_model = google://gemini-1.5-flash-latest
chapter_stage3_writer_model = google://gemini-1.5-flash-latest
; Note: Stage 4 is currently commented out in ChapterGenerator
chapter_stage4_writer_model = google://gemini-1.5-flash-latest
chapter_revision_writer_model = google://gemini-1.5-pro-latest
; For generating constructive criticism (LLMEditor)
revision_model = google://gemini-1.5-flash-latest
; For evaluation tasks like rating (LLMEditor)
eval_model = google://gemini-1.5-flash-latest
; For generating summary/info at the end (StoryInfo)
info_model = google://gemini-1.5-flash-latest
; For scrubbing the story (Scrubber)
scrub_model = google://gemini-1.5-flash-latest
; For checking LLM outputs (e.g., summary checks, JSON format)
checker_model = google://gemini-1.5-flash-latest


[NVIDIA_SETTINGS]
; This is a manually curated list. Models for NVIDIA are NOT discovered automatically.
; Add the exact model IDs you have access to here, separated by commas. These will
; appear in the selection menu if your NVIDIA_API_KEY is set.
;
; Example:
; available_moels = meta/llama3-8b-instruct, mistralai/mistral-large

available_models = mistralai/mistral-medium-3-instruct,mistralai/mistral-nemotron,qwen/qwen3-235b-a22b,nvidia/llama-3.1-nemotron-ultra-253b-v1,nvidia/llama-3.3-nemotron-super-49b-v1,writer/palmyra-creative-122b, mistralai/mixtral-8x22b-instruct-v0.1,ai21labs/jamba-1.5-large-instruct,meta/llama-4-maverick-17b-128e-instruct,deepseek-ai/deepseek-r1,qwen/qwq-32b

; The base URL for the NVIDIA API. The default is for NVIDIA's managed endpoints.
; This can be overridden by setting NVIDIA_BASE_URL in your .env file.
base_url = https://integrate.api.nvidia.com/v1


[GITHUB_SETTINGS]
; API Version required by the Azure OpenAI client used for the GitHub provider.
api_version = 2024-05-01-preview


[WRITER_SETTINGS]
; Seed for randomization in LLM generation. Overridden by command-line -Seed.
seed = 108

; Outline generation revision settings. Overridden by command-line args.
outline_min_revisions = 0
outline_max_revisions = 3

; Chapter generation revision settings. Overridden by command-line args.
; Valid values: true, false, yes, no, on, off, 1, 0
chapter_no_revisions = false
chapter_min_revisions = 1
chapter_max_revisions = 3
minimum_chapters = 12

; Other generation settings. Overridden by command-line args.
; Disables final scrub pass.
scrub_no_scrub = false
; Enables chapter-by-chapter outline expansion.
expand_outline = true
; Enables a full-novel edit pass before scrubbing.
enable_final_edit_pass = true
; Uses scene-by-scene generation.
scene_generation_pipeline = true

; Debug mode. Overridden by command-line -Debug.
debug = false

; Ollama specific settings (if Ollama is use)
ollama_ctx = 8192

[PROJECT_INFO]
project_name = Fiction Fabricator

[TIMEOUTS]
; Request timeout in seconds. It's recommended to have a longer timeout
; for local providers like Ollama that may have long load times.
default_timeout = 180
ollama_timeout = 360

```

## File: `requirements.txt`

```text
# Core Langchain and provider packages for LLM integration
langchain
langchain-core
langchain-community
langchain-google-genai
google-generativeai
# CORRECTED: Pin mistralai to a version compatible with langchain-mistralai
langchain-mistralai
mistralai==0.1.8
langchain-groq
langchain-nvidia-ai-endpoints
azure-ai-inference
langchain-openai

# Ollama client library for local model support
ollama

# Utility packages
python-dotenv
termcolor
requests
configparser

```

