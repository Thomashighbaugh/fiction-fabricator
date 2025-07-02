# 5. Advanced Tools

Fiction Fabricator includes several powerful utilities for power users, developers, and those who want to experiment with different models and generation strategies.

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

## Brainstorming Premises (`Tools/PremiseGenerator.py`)

As described in the Usage Workflow, this tool is your starting point when you only have a rough theme. It takes a high-level concept and generates 10 fleshed-out premises, each of which can serve as a high-quality input for `Tools/PromptGenerator.py`.

### How to Use:

```bash
python Tools/PremiseGenerator.py -i "A hardboiled detective who is also a ghost"
```

This will initiate the model selection menu and the generation/critique/revision cycle, saving the final 10 premises to a timestamped file in the `Premises/` directory.
