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
