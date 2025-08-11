# 4. Usage Workflow

This guide outlines the recommended workflow for generating a novel with Fiction Fabricator, from initial idea to final output.

## Step 1: Brainstorm Premises (Optional but Recommended)

If you only have a high-level theme (e.g., "haunted spaceship"), you can use the `src/Tools/PremiseGenerator.py` tool to brainstorm more concrete ideas.

````bash
# Run the tool with your high-level theme
python src/Tools/PremiseGenerator.py -i "haunted spaceship"```

The tool will present a model selection menu and then generate 10 distinct premises based on your theme. The output is saved to a timestamped file in the `Logs/Premises/` directory. You can use any of these premises as input for the next step.

## Step 2: Create a High-Quality Prompt

A detailed prompt produces a better story. Use the `src/Tools/PromptGenerator.py` tool to expand a simple idea or one of the premises from the previous step into a rich, detailed prompt suitable for the main application.

```bash
# Run the tool with your chosen story title and premise
python src/Tools/PromptGenerator.py -t "The Last Signal" -i "A lone astronaut on Mars discovers a strange, repeating signal from a polar ice cap, but her mission command on Earth insists it's just a malfunction."
````

This will again prompt you to select a model for the generation and will save a detailed `prompt.txt` file in `Generated_Content/Prompts/The_Last_Signal/`.

## Step 3: Manage Lorebooks (Optional but Recommended for Consistency)

Lorebooks are external text files that provide consistent information about your story's world, characters, or specific plot points. They are crucial for maintaining continuity and richness, especially in long novels or series.

### Creating a Lorebook

Lorebooks are simple `.txt` files. You can create them manually in the `LoreBooks/` directory. Each Lorebook should contain key information you want the LLM to reference consistently. For example:

```
# LoreBooks/MyFantasyWorld.txt

**Characters:**
- Elara: A skilled elven archer, haunted by her past, seeking redemption.
- Kael: A gruff dwarven warrior, loyal but cynical, with a hidden soft spot.

**Locations:**
- Eldoria: The ancient elven forest, known for its glowing flora and hidden temples.
- The Iron Peaks: A harsh mountain range, home to dwarven mines and dangerous beasts.

**Magic System:**
- Elemental magic: Users can manipulate fire, water, earth, and air. Each element has strengths and weaknesses.
- Runes: Ancient symbols that amplify magic when inscribed on objects.
```

### Selecting a Lorebook during Generation

When you run `main.py` to write a short story, novel, or web novel chapter, the system will now prompt you to select a Lorebook. It will scan the `LoreBooks/` directory and present a list of available `.txt` files. You can choose one, or select the option to proceed without a Lorebook.

```
# Example prompt during generation:

Please select a Lorebook to use (optional):
1. MyFantasyWorld.txt
2. SciFiTech.txt
3. No Lorebook (continue without)
Enter your choice (1-3): 
```

The content of the selected Lorebook will be provided to the LLM as additional context during relevant generation steps, helping to ensure consistency with your established lore.

## Step 4: Write the Novel

Use the main `main.py` script to start the full generation process, using the prompt file you just created.

### Interactive Mode (Easiest)

Simply provide the prompt file path. The script will present an interactive menu to select the primary writing model from all your configured providers, and also prompt for Lorebook selection.

```bash
python main.py
# Then select option 4 for Novel Writing, or 3 for Short Story, or 5 for Web Novel Chapter.
```

### Custom/Headless Mode (for `main.py`)

You can specify all models and settings via command-line arguments. This is useful for automated runs or for overriding the settings in `config.ini`.

```bash
# Example of a custom run using different models for different tasks
python main.py \
-Prompt "Generated_Content/Prompts/The_Last_Signal/prompt.txt" \
-InitialOutlineModel "google://gemini-1.5-pro-latest" \
-ChapterS1Model "groq://llama3-70b-8192" \
-ChapterRevisionModel "nvidia://meta/llama3-70b-instruct" \
-EnableFinalEditPass \
-Seed 42 \
-Lorebook "LoreBooks/MyFantasyWorld.txt"
```

## Step 5: Find Your Story

All output is saved to uniquely named directories to prevent overwriting your work.

- **`Generated_Content/Stories/`**: Contains the final, user-facing output. For each run, you will get:

  - `Your_Story_Title.md`: A markdown file with the formatted story, generation statistics, and the full outline.
  - `Your_Story_Title.json`: A structured JSON file containing the complete narrative context, including all outlines, chapter text, and summaries. This file can be used for analysis or further processing.

- **`Logs/`**: Contains detailed logs for debugging. A new directory is created for each run, containing:
  - `Main.log`: A human-readable log of all steps, warnings, and errors.
  - `LangchainDebug/`: A folder with `.json` and `.md` files for every single call made to an LLM, showing the exact prompts and responses. This is invaluable for debugging and understanding the generation process.

- **`Generated_Content/Short_Story/`**: Contains short stories generated by `src/Tools/ShortStoryWriter.py`.
- **`Generated_Content/Web_Novel_Chapters/`**: Contains individual web novel chapters generated by `src/Tools/WebNovelWriter.py`.
- **`Logs/Premises/`**: Contains logs of generated premises from `src/Tools/PremiseGenerator.py`.
- **`Logs/PromptGenLogs/`**: Contains logs of prompt generation from `src/Tools/PromptGenerator.py`.
- **`LoreBooks/`**: The directory where you should place your custom Lorebook `.txt` files.
