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
