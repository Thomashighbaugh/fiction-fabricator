# Fiction Fabricator

Fiction Fabricator, at present derived from [AIStoryteller by datacrystals](https://github.com/datacrystals/AIStoryteller) is a Python-based terminal application designed to generate high quality and long-form prose narratives, from initial user ideas to finished novels. 

It leverages Large Language Models (LLMs) through various providers (primarily using locally hosoted LLMs run with Ollama/llama.cpp, with tooling for Google and OpenRouter available) to orchestrate a sophisticated scene-by-scene story generation pipeline leveraging langchain and the use of the LLM to critique and refine the generated content . 






## Features

*   **Scene-by-Scene Generation:** Creates stories by first outlining chapters into detailed scenes, then writing narrative for each scene, ensuring better flow and coherence.
*   **Multi-LLM Support:** Primarily designed for local Ollama models, but includes wrappers for Google Generative AI and OpenRouter.
*   **Iterative Refinement:** Incorporates LLM-based feedback loops for improving outlines and chapter drafts.
*   **Modular Design:** Separates concerns into distinct modules for outlining, scene generation, context management, LLM interaction, etc.
*   **Comprehensive Logging:** Detailed logs for each generation session, including LLM interactions for debugging.
*   **Customizable Models:** Allows specifying different LLM models for various tasks (e.g., outlining, narrative writing, critiquing).
*   **Optional Processing:** Includes features for global novel editing, text scrubbing, and translation.
*   **Metadata Extraction:** Generates title, summary, and tags for the final story.
*   **Utility Scripts:** Includes tools for prompt generation and developer testing.

## Project Structure

```
FictionFabricator/
├── Prompts/                # Stores user-created and generated prompt.txt files
│   └── (ExampleStoryTitle)/
│       └── prompt.txt
├── Stories/                # Default output directory for generated stories
├── Logs/                   # Stores detailed logs for each run
├── EvaluationLogs/         # Stores logs for story evaluations
├── Tools/
│   ├── prompt_generator.py # Utility to help create detailed prompts
│   └── Test.py             # Developer utility for quick testing
├── Writer/                 # Core library for story generation
│   ├── Chapter/
│   │   ├── ChapterContext.py
│   │   ├── ChapterDetector.py
│   │   ├── ChapterGenSummaryCheck.py # (May be deprecated or integrated)
│   │   └── ChapterGenerator.py
│   ├── Interface/
│   │   ├── OpenRouter.py
│   │   └── Wrapper.py
│   ├── Outline/
│   │   └── StoryElements.py
│   ├── Scene/
│   │   ├── ChapterByScene.py          # (Likely deprecated or integrated into ChapterGenerator)
│   │   ├── ChapterOutlineToScenes.py  # (Likely deprecated or integrated into SceneOutliner)
│   │   ├── SceneGenerator.py
│   │   ├── SceneOutliner.py
│   │   ├── SceneParser.py
│   │   └── ScenesToJSON.py            # (Likely deprecated or integrated into SceneOutliner/Parser)
│   ├── Config.py
│   ├── LLMEditor.py
│   ├── NovelEditor.py
│   ├── OutlineGenerator.py
│   ├── PrintUtils.py
│   ├── Prompts.py           # Internal, optimized prompts for the system
│   ├── Scrubber.py
│   ├── Statistics.py
│   ├── StoryInfo.py
│   └── Translator.py
├── Evaluate.py
├── Write.py                 # Main script to run the story generation
└── requirements.txt
```

## Setup and Installation

### Prerequisites

*   Python 3.8 or higher.
*   An Ollama server running locally (recommended for most models). You can download Ollama from [ollama.ai](https://ollama.ai/).
*   Desired LLM models pulled into your Ollama instance (e.g., `ollama pull llama3:8b`).
*   (Optional) API keys for Google Generative AI or OpenRouter if you intend to use those services.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd FictionFabricator
    ```

2.  **Install dependencies:**
    It's highly recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
    The `requirements.txt` file includes:
    ```
    ollama
    termcolor
    google.generativeai
    python-dotenv
    requests
    ```

### Environment Variables

For Google Generative AI and OpenRouter, API keys are required. Create a `.env` file in the project root directory (`FictionFabricator/.env`) with your keys:

```env
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY"
# HTTP_REFERER="YOUR_OPENROUTER_SITE_URL" # Optional, for OpenRouter identification
```

The `Writer/Interface/Wrapper.py` script will automatically load these variables.

## Usage

### Step 1: Generating a Story Prompt (Optional but Recommended)

While `Write.py` can take a very basic idea, using `Tools/prompt_generator.py` helps create a more detailed and structured `prompt.txt` file, which often leads to better story generation.

#### `Tools/prompt_generator.py`

This self-contained script uses an LLM to expand a basic idea into a fuller prompt.

**Purpose:** To generate a `prompt.txt` file in a new subdirectory under `Prompts/`. This `prompt.txt` will be well-suited for the main `Write.py` script.

**Prerequisites:**
*   `ollama` Python library installed (`pip install ollama`).
*   An Ollama server running with the specified model available.

**Command:**
Run from the project root directory:
```bash
python Tools/prompt_generator.py -m "<ollama_model_uri>" -t "<Your Story Title>" -i "<Your Basic Story Idea>" [--host <ollama_host>] [--temp <temperature>]
```

**Arguments:**

*   `-m`, `--model` (required): Ollama model URI.
    *   Example: `"ollama://llama3:8b"` or simply `"llama3:8b"`
*   `-t`, `--title` (required): The desired title for your story. This will be used to create a subdirectory name (e.g., `Prompts/Your_Story_Title/`).
*   `-i`, `--idea` (required): Your basic story idea or concept in a sentence or two.
*   `--host` (optional): Ollama server host address.
    *   Default: `http://localhost:11434`
*   `--temp` (optional): Temperature for LLM generation during prompt expansion.
    *   Default: `0.7`

**Example:**
```bash
python Tools/prompt_generator.py -m "llama3:8b" -t "The Clockwork Heart of Veridia" -i "In a steampunk city powered by a giant clockwork heart, a young inventor discovers a conspiracy to stop the heart, which would doom the city. She must team up with a grizzled sky-captain to find a legendary power source before it's too late."
```

**Output:**
This command will:
1.  Use `llama3:8b` to expand, critique, and refine the idea.
2.  Create a directory: `FictionFabricator/Prompts/The_Clockwork_Heart_of_Veridia/`
3.  Save the final refined prompt into `FictionFabricator/Prompts/The_Clockwork_Heart_of_Veridia/prompt.txt`.

The content of `prompt.txt` might look something like this (generated by the LLM):

```
Title: The Clockwork Heart of Veridia

Genre: Steampunk Adventure with elements of Mystery and Political Intrigue.
Tone: Adventurous, with moments of tension, wonder, and a touch of hopeful determination. Aim for a moderately fast pace, especially during action sequences.

Core Conflict: The primary conflict is a race against time to save the city of Veridia from an internal conspiracy aiming to stop its life-giving Clockwork Heart. This involves uncovering the conspirators, understanding their motives, and finding an alternative or a way to protect the Heart.

Main Characters:
1.  Elara: A brilliant, resourceful young inventor (early 20s). She's more comfortable with cogs and gears than people but possesses a strong sense of justice and a deep love for her city. Her initial motivation is to understand a strange anomaly she detected in the Heart's rhythm, which leads her to uncover the conspiracy.
2.  Captain Rex "Rusty" Cogsworth: A veteran sky-captain (late 40s/early 50s), cynical and world-weary but with a hidden noble streak. He owns a somewhat dilapidated but reliable airship. He's initially reluctant to help Elara but is drawn in by the threat to his city and perhaps a past connection or debt.

Setting Snippet: Veridia is a magnificent city of brass towers, steam-powered automatons, and intricate sky-bridges, all built around and powered by the colossal, ever-ticking Clockwork Heart at its center. The city is layered, with the wealthy elite residing in the upper echelons closer to the Heart's rhythmic pulse, while the lower districts are shrouded in steam and industrial hum.

Key Plot Beats (Suggestions):
- Elara's discovery of the sabotage plot.
- Her desperate search for allies, leading her to Captain Cogsworth.
- A thrilling chase sequence through Veridia's skyways or a daring infiltration into a conspirator's stronghold.
- The revelation of the main antagonist and their (perhaps misguided) reasons.
- A climactic confrontation at the Clockwork Heart itself.

Specific "Do's":
- Emphasize the intricate mechanics and atmosphere of the steampunk setting.
- Show the societal impact if the Heart were to fail.
- Develop the dynamic between the optimistic Elara and the cynical Cogsworth.

Target Audience: Young Adult / Adult readers who enjoy steampunk, adventure, and a touch of mystery.
```

### Step 2: Writing the Story

#### `Write.py`

This is the main script to generate the full story.

**Command:**
```bash
python Write.py -Prompt "<path_to_prompt_file>" [OPTIONS]
```

**Key Arguments:**

*   `-Prompt` (required): Path to the `prompt.txt` file (e.g., `Prompts/MyStoryTitle/prompt.txt`).
*   `-Output` (optional): Base filename for output (e.g., `MyAwesomeStory`). If not provided, a name is generated from the story's LLM-generated title. Output files will be placed in the `Stories/` directory.
*   `-InitialOutlineModel`, `-ModelStoryElementsGenerator`, etc. (optional): Specify model URIs for different tasks. See `python Write.py --help` for all model arguments. Defaults are in `Writer/Config.py`.
    *   Model URI Format: `"provider://model_identifier@host?param1=value1"`
        *   Ollama (default provider if no `://`): `"ollama://llama3:8b@localhost:11434"` or simply `"llama3:8b"` (uses `Config.OLLAMA_HOST`).
        *   Google: `"google://gemini-1.5-flash-latest"`
        *   OpenRouter: `"openrouter://mistralai/mistral-7b-instruct"`
*   `-Seed` (optional): Integer seed for reproducibility (default: `42`).
*   `-Translate` (optional): Target language for final story translation (e.g., `"French"`).
*   `-TranslatePrompt` (optional): Target language for initial prompt translation if it's not in the LLM's primary working language (e.g., `"English"`).
*   `-NoChapterRevision`, `-NoScrubChapters`, `-EnableFinalEditPass`: Flags to control optional processing steps.
*   `-Debug`, `-DebugLevel`: For verbose logging.

**Example:**
```bash
python Write.py -Prompt "Prompts/The_Clockwork_Heart_of_Veridia/prompt.txt" -Output "ClockworkHeartStory" -InitialOutlineModel "ollama://mixtral:8x7b" -ModelSceneNarrativeGenerator "ollama://llama3:70b" -Debug
```

**Output:**
*   A main Markdown file (e.g., `Stories/ClockworkHeartStory.md`) containing:
    *   Generation statistics (title, summary, word count, time taken).
    *   Key configuration settings used.
    *   The full generated story.
    *   An appendix with the base context, story elements, and chapter-by-chapter outline.
*   A JSON data file (e.g., `Stories/ClockworkHeartStory_data.json`) containing detailed structured output of all generated components.
*   A log session directory in `Logs/Generation_<timestamp>/` containing:
    *   `Main.log`: Detailed log of the generation process.
    *   `LangchainDebug/`: JSON and Markdown files for each LLM interaction.
    *   Artifacts like `1_StoryElements.md`, `2_ChapterLevelOutline_Raw.md`, `2a_Chapter_X_PlotSegment.txt` (with scene outlines appended), `3_Chapter_X_Generated.md`, etc.

### Developer Testing Utility

#### `Tools/Test.py`

Provides a command-line menu to quickly run `Write.py` with predefined model configurations and common flags. Useful for developers to test different LLM combinations or features.

**Usage:**
```bash
python Tools/Test.py
```
Follow the on-screen menus to select model configurations, prompts, seed, etc.

### Story Evaluation

#### `Evaluate.py`

Compares two stories (or their components) generated by `Write.py` using an LLM for critique.

**Usage:**
```bash
python Evaluate.py -Story1 "<path_to_story1_data.json>" -Story2 "<path_to_story2_data.json>" [-Output <report_filename.md>] [-Model <eval_model_uri>]
```
*   `-Story1`, `-Story2`: Paths to the `_data.json` files generated by `Write.py`.

This script produces a Markdown report comparing outlines and chapters based on various literary criteria.

## Core Pipeline Overview

When `Write.py` is executed, it follows this general pipeline:

1.  **Initialization:**
    *   Parses command-line arguments.
    *   Initializes the `Logger`.
    *   Applies arguments to global `Config`.
    *   Initializes the `LLM Interface (Wrapper)` and loads specified models.
    *   Loads the user prompt from the specified file.

2.  **Prompt Translation (Optional):**
    *   If `-TranslatePrompt` is set, the user prompt is translated (e.g., into English) using `Translator.translate_user_prompt`.

3.  **Outline Generation (`OutlineGenerator.generate_outline`):**
    *   **Base Context Extraction:** Extracts overarching instructions from the user prompt (using `Prompts.GET_IMPORTANT_BASE_PROMPT_INFO`).
    *   **Story Elements Generation (`StoryElements.generate_story_elements`):** Uses an LLM (e.g., `Config.MODEL_STORY_ELEMENTS_GENERATOR`) with `Prompts.OPTIMIZED_STORY_ELEMENTS_GENERATION` to create:
        *   Title, Genre, Themes, Pacing, Writing Style
        *   Plot Synopsis (e.g., Five-Act Structure)
        *   Setting(s) details
        *   Primary Conflict
        *   Character profiles (main and supporting)
    *   **Initial Chapter-Level Outline:** Generates a chapter-by-chapter outline using `Config.INITIAL_OUTLINE_WRITER_MODEL` and `Prompts.OPTIMIZED_OVERALL_OUTLINE_GENERATION`, based on the user prompt and story elements.
    *   **Iterative Outline Revision:**
        *   `LLMEditor.GetFeedbackOnOutline`: Critiques the current outline.
        *   `LLMEditor.GetOutlineRating`: Checks if the outline meets quality standards.
        *   If revision is needed, the outline and feedback are sent back to the LLM (`Config.INITIAL_OUTLINE_WRITER_MODEL` with `Prompts.OUTLINE_REVISION_PROMPT`) to produce an improved version. This loop continues for `Config.OUTLINE_MIN_REVISIONS` to `Config.OUTLINE_MAX_REVISIONS`.

4.  **Chapter Segmentation & Plot Preparation:**
    *   **Chapter Count Detection (`ChapterDetector.llm_count_chapters`):** Determines the number of chapters from the finalized outline.
    *   **Outline Splitting (`split_overall_outline_into_chapter_plots` in `Write.py`):** The overall outline is segmented into individual plot descriptions for each chapter (using regex and LLM fallback).
    *   **Fallback Plot Generation (if needed):** If a chapter's plot segment is missing or poor, `_generate_fallback_plot_string_for_chapter` (in `Write.py`) uses an LLM with `Prompts.FALLBACK_CHAPTER_PLOT_GENERATION_PROMPT` to create a placeholder plot.

5.  **Chapter-by-Chapter Generation (Loop):**
    For each chapter:
    *   **Scene Outlining (`ChapterGenerator.generate_chapter_by_scenes` which calls `SceneOutliner.generate_detailed_scene_outlines`):**
        *   The chapter's plot segment is fed to `Config.MODEL_SCENE_OUTLINER` with `Prompts.OPTIMIZED_CHAPTER_TO_SCENES_BREAKDOWN`.
        *   This produces a JSON list of detailed scene blueprints for the current chapter. Each blueprint includes scene title, setting, characters, key events, dialogue points, pacing, tone, purpose, and transition hooks.
        *   `SceneParser.parse_llm_scene_outlines_response` is used to parse this JSON, with LLM-based correction for malformed responses.
        *   These scene outlines are logged to the chapter's `_PlotSegment.txt` file by `_log_generated_scenes_to_plot_file` (in `Write.py`).
    *   **Scene Narrative Generation (Inner loop within `ChapterGenerator`):**
        For each scene blueprint:
            *   `SceneGenerator.write_scene_narrative`: Takes the scene blueprint and context (overall outline, previous scene summary) and uses `Config.MODEL_SCENE_NARRATIVE_GENERATOR` with `Prompts.OPTIMIZED_SCENE_NARRATIVE_GENERATION` to write the full narrative text for the scene.
            *   `ChapterContext.generate_previous_scene_summary`: After a scene is written, a brief summary is generated to provide immediate context for the *next* scene in the same chapter.
    *   **Chapter Assembly & Refinement (within `ChapterGenerator`):**
        *   The narratives of all scenes in the chapter are compiled.
        *   If `Config.CHAPTER_NO_REVISIONS` is false, `Config.MODEL_CHAPTER_ASSEMBLY_REFINER` is used to smooth transitions and improve cohesion of the assembled scenes.
    *   **Chapter Revision Loop (within `ChapterGenerator`):**
        *   If `Config.CHAPTER_NO_REVISIONS` is false:
            *   `LLMEditor.GetFeedbackOnChapter`: Critiques the assembled (and possibly refined) chapter.
            *   `LLMEditor.GetChapterRating`: Checks if the chapter meets quality standards.
            *   If revision is needed, `Config.CHAPTER_REVISION_WRITER_MODEL` with `Prompts.CHAPTER_REVISION_PROMPT` revises the chapter based on feedback. This loop repeats based on `Config.CHAPTER_MIN_REVISIONS` and `Config.CHAPTER_MAX_REVISIONS`.
    *   **Inter-Chapter Context (`ChapterContext.generate_previous_chapter_summary`):** After a full chapter is finalized, a more comprehensive summary is generated to provide context for the *next chapter*.

6.  **Global Novel Editing (Optional) (`NovelEditor.edit_novel_globally`):**
    *   If `Config.ENABLE_FINAL_EDIT_PASS` is true, all generated chapters are reviewed by an LLM (`Config.CHAPTER_REVISION_WRITER_MODEL` with `Prompts.GLOBAL_NOVEL_CHAPTER_EDIT_PROMPT`) for inter-chapter consistency, flow, foreshadowing, and overall pacing.

7.  **Text Scrubbing (Optional) (`Scrubber.scrub_novel_chapters`):**
    *   If `Config.SCRUB_NO_SCRUB` is false, chapters are processed by `Config.SCRUB_MODEL` with `Prompts.CHAPTER_SCRUB_PROMPT` to remove any leftover author notes, outline markers, or non-narrative elements.

8.  **Story Translation (Optional) (`Translator.translate_novel_chapters`):**
    *   If `Config.TRANSLATE_LANGUAGE` is set, the finalized (and scrubbed) chapters are translated into the target language using `Config.TRANSLATOR_MODEL` and `Prompts.CHAPTER_TRANSLATE_PROMPT`.

9.  **Metadata Extraction (`StoryInfo.get_story_info`):**
    *   The full printable outline (or the final story) is sent to `Config.INFO_MODEL` with `Prompts.STATS_PROMPT`.
    *   The LLM generates a title, summary, tags, and an overall quality rating for the story.

10. **Output Generation:**
    *   The final story, along with statistics, configuration details, and appendices (story elements, final outline), is compiled into a Markdown file.
    *   A comprehensive JSON file containing all raw and processed data is also saved.

## Key Components

### Configuration (`Writer/Config.py`)
Central module for default model URIs, API settings, generation parameters (e.g., revision counts, seed), and feature flags. These can be overridden by command-line arguments to `Write.py`.

### LLM Interface (`Writer/Interface/Wrapper.py`)
*   Manages connections and interactions with various LLM providers (Ollama, Google, OpenRouter).
*   Handles dynamic installation of provider-specific packages.
*   Parses model URI strings.
*   Provides `safe_generate_text` and `safe_generate_json` methods with retries and error handling to ensure robust LLM responses.
*   Manages message history and logging of LLM calls.

### Logging (`Writer/PrintUtils.py`)
*   `Logger` class for timestamped logging to console (with colors) and a main log file (`Logs/Generation_<timestamp>/Main.log`).
*   Saves detailed LLM interactions (prompts and responses) to `Logs/Generation_<timestamp>/LangchainDebug/` for debugging.
*   Saves intermediate and final artifacts (outlines, chapters) to the session log directory.

### Prompts (`Writer/Prompts.py`)
A repository of all system-level, optimized prompt templates used to guide LLMs for various tasks like outlining, narrative generation, critique, summarization, etc.

### Outline Generation
*   **`Writer/Outline/StoryElements.py`:**
    *   `generate_story_elements()`: Takes the user's initial prompt and uses an LLM to expand it into detailed story elements (genre, themes, characters, plot synopsis, setting).
*   **`Writer/OutlineGenerator.py`:**
    *   `generate_outline()`: Orchestrates the creation of the main chapter-by-chapter story outline. It first calls `generate_story_elements`, then generates an initial outline, and refines it iteratively using feedback from `LLMEditor`.

### Chapter & Scene Generation
*   **`Writer/Chapter/ChapterDetector.py`:**
    *   `llm_count_chapters()`: Uses an LLM to determine the number of chapters from a generated outline.
*   **`Writer/Scene/SceneOutliner.py`:**
    *   `generate_detailed_scene_outlines()`: Takes a chapter's plot summary and breaks it down into a list of detailed scene blueprints (JSON objects).
*   **`Writer/Scene/SceneParser.py`:**
    *   `parse_llm_scene_outlines_response()`: Parses the LLM's (potentially malformed) JSON response for scene outlines, with an LLM-based correction mechanism.
*   **`Writer/Scene/SceneGenerator.py`:**
    *   `write_scene_narrative()`: Generates the full narrative text for an individual scene based on its detailed blueprint and contextual information.
*   **`Writer/Chapter/ChapterContext.py`:**
    *   `generate_previous_chapter_summary()`: Creates a summary of a completed chapter to provide context for the next chapter.
    *   `generate_previous_scene_summary()`: Creates a very brief summary of a completed scene for immediate context to the next scene within the same chapter.
*   **`Writer/Chapter/ChapterGenerator.py`:**
    *   `generate_chapter_by_scenes()`: The main orchestrator for generating a full chapter. It calls `SceneOutliner` to get scene blueprints, then iterates through them, calling `SceneGenerator` for each. It manages context flow and can optionally refine the assembled chapter and run it through a feedback/revision loop using `LLMEditor`. Returns the chapter text and the list of scene outlines used.

### Editing & Refinement
*   **`Writer/LLMEditor.py`:**
    *   `GetFeedbackOnOutline()`, `GetOutlineRating()`: Provide LLM-based critique and quality assessment for story outlines.
    *   `GetFeedbackOnChapter()`, `GetChapterRating()`: Provide LLM-based critique and quality assessment for individual chapters.
*   **`Writer/NovelEditor.py`:**
    *   `edit_novel_globally()`: Performs an optional high-level editing pass over the entire assembled novel for inter-chapter consistency and flow.

### Utilities
*   **`Writer/Scrubber.py`:**
    *   `scrub_novel_chapters()`: Cleans final chapter texts by removing author notes, outline remnants, etc.
*   **`Writer/Translator.py`:**
    *   `translate_user_prompt()`, `translate_novel_chapters()`: Handles translation of prompts and generated content.
*   **`Writer/StoryInfo.py`:**
    *   `get_story_info()`: Extracts final story metadata (title, summary, tags, rating) using an LLM.
*   **`Writer/Statistics.py`:**
    *   `get_word_count()`, etc.: Simple text statistics functions.

## Customization

### Models
You can customize the LLM models used for each stage of the generation process via command-line arguments to `Write.py` or by changing the defaults in `Writer/Config.py`. Ensure any Ollama models are pulled locally. For cloud providers, ensure API keys are set.

### Prompts
The internal prompts used by FictionFabricator are located in `Writer/Prompts.py`. Modifying these prompts can significantly alter the style, structure, and quality of the generated content. This is an advanced customization.

User-provided prompts (via the `-Prompt` argument to `Write.py`) are text files that define the initial story idea. The `Tools/prompt_generator.py` script can help create more detailed and effective user prompts.

## Troubleshooting

*   **Model Not Found (Ollama):** Ensure the Ollama server is running (`ollama serve`) and that you have pulled the specified model (e.g., `ollama pull llama3:8b`). The `Interface/Wrapper.py` will attempt to pull models if they are not found, but this requires an internet connection and for the model to be available on the Ollama registry.
*   **API Key Errors:** Double-check that your `.env` file is correctly formatted and contains valid API keys for Google or OpenRouter if you are using them.
*   **JSON Parsing Errors:** Occasionally, LLMs might produce malformed JSON, especially for complex structures like scene outlines.
    *   The system has retry and LLM-based correction mechanisms (`Interface.Wrapper.safe_generate_json`, `Scene.SceneParser`).
    *   If errors persist, the LLM model used for the task (or for correction via `Config.EVAL_MODEL`) might not be suitable or the prompt needs further refinement. Check the `LangchainDebug` logs for the exact LLM output.
    *   The `OPTIMIZED_CHAPTER_TO_SCENES_BREAKDOWN` prompt in `Writer/Prompts.py` has been updated to specifically warn against Python-style string concatenation, which was a source of such errors.
*   **Low-Quality Output:**
    *   Experiment with different models for different tasks. Larger, more capable models generally produce better creative text but are slower.
    *   Refine your input `prompt.txt`. A more detailed and clear input prompt leads to better results. Use `Tools/prompt_generator.py`.
    *   Adjust `Config.py` parameters like revision counts.
    *   Modify system prompts in `Writer/Prompts.py` (advanced).
*   **Long Generation Times:** Story generation, especially with multiple chapters and revisions, can be time-consuming. Using smaller/faster models or reducing revision counts can speed up the process at the potential cost of quality.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs, feature requests, or improvements as you feel so inclined.

## License

This project, in its present form, is a fork of [AIStoryWriter by datacrystals](https://github.com/datacrystals/AIStoryWriter) thus it inherits its license from the original repository, which wisely used the AGPL-3.0 license to insure that anyone offering services over a network must provide the source code of their modifications to the users of that service and that the code remains free and open for everyone to use, modify, and distribute regardless of its use as such.

## Acknowledgements

This project is a fork of [AIStoryWriter by datacrystals](https://github.com/datacrystals/AIStoryWriter) upon which I have built additional functionality to suite it to my more specific focus and the use case I have kept in mind in adapting it. Nonetheless, the original author's pipeline for generating the text remains the best I have thus far encourntered for the generation of long form fictional prose using a locally hosted LLM and is core to this version of this project and this project owes the original a profound debt of gratitude for their work and wisdom in its open-source licensing to prevent the code from being used in a close-source manner that would profit from the original author or my subsequent work on it.

Additionally, as I have retaineed in the branches of this repsitory several prior versions, differeing in the generation pipelines I have used as well as in the interface for user interaction, some of which wholly original attemptsand others which have implemented aspects of other projects I found were useful, I would like to acknowledge the entire open-source community that has worked on projects related to the generation of long form fictional prose using LLMs, the repositories of which I have scoured, examined and ran locally in too great a number to list here, but which have all contributed to the development of this project and the code I have written for it.

Which is ultimately the potency and power of open-source software, as these projects as well as this one, all provide future developers working on the same or similar projects a braod range of ideas and generation pipelines to draw from and hopefully improve upon such as to radically reduce the overhead, time and human resource capital need for software achieving the same goal to reach maturaity all why benefitting from the input of parties that the traditionally closed and zealously protected intellectual property system preferred by courts and large corporations would exclude from the process and prevent from contributions in ways detrimental to human society overall in its many forms and facets.

## Generated Text Caveat

If you intend to use this project to generate books, which is why it was written and adapted in the first place, note that even if I manage to make it generate text requiring relatively minimal editing, until you perform "substantial" edits to it (which is a deliberately vague concept in Legal French to enable future rulings to make it mean what4ever they want but stands at least for more than just spell checking and grammar corrections), it will technically be the intellectual property of the LLM which cannot be copywrited as per recent rulings.

So make substantial edits to it, whatever you think that is, as well as be honest about using AI in the process when submitting to Amazon or you may run into trouble. Any author pretending that they have not used AI at some point in their process of making Kindle books without a publisher providing the cover generation, editing and formatting then raping the author of their royalities would be lying, which is why Amazon is even asking I would assume as a truthfulness test but we can at this point all assume no author or other individual in their write mind (thus Steven King being an exception) will go through the labor of turning an idea into a multiple hundred pages of prose final product without using an LLM at least to develop the outline or take the place of their disinterested spouse in talking through its various aspects and facets.

## Potential Future Work

An even more obvious application of this project which would be the bane of its current bloated and parasitic surrounding publishing industry is to use it to generate textbooks or non-fictional works that exist to document and peer specifically into various topics (often to draw out conclusions with ulterior and temporal motivations from them like divination with bone throwing or tarot cards). This would be a relatively simple task to implement, with the only sticking point being implementing the RAG and possibly the information that the RAG would serve as its expert knowledge base to draw from. Which I can imagine its implementation readily now, so I may