# File: Tools/Test.py
# Purpose: Developer utility script for quickly running AIStoryWriter with predefined configurations.

"""
Developer Testing Utility for AIStoryWriter.

This script provides a simple command-line menu to run the main `Write.py`
script with various predefined sets of model configurations and common flags.
It's useful for developers to quickly test different LLM combinations or
features without manually typing long command-line arguments.

The script constructs and executes a command string that calls `../Write.py`.
"""

from typing import Any, Dict
from Writer.Config import Config
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Predefined model configurations (can be expanded)
# Each key is a menu option, value is a dictionary of model arguments for Write.py
# Using full URI format for models: "provider://model_id@host?params"
# Common host: @10.1.65.4:11434 for local server, or remove for default localhost for ollama
# Or specify OpenRouter models: "openrouter://<org>/<model_name>:<version>"
# Or Google models: "google://gemini-1.5-flash-latest" (host not applicable)

# Common model aliases for brevity in configurations
# These are illustrative. Replace with actual model URIs you use.
# Ensure your Config.py defaults or the URI parser in Wrapper.py can handle these.
# For Ollama, if no host is specified, it defaults to Config.OLLAMA_HOST
# Example: "ollama://llama3:70b" assumes default host.
# "ollama://llama3:70b@<your_ollama_ip>:11434" specifies host.

# Standard local models (examples, replace with your actual preferred models)
LLAMA3_8B_LOCAL = "ollama://llama3:8b"  # Assumes default host
LLAMA3_70B_LOCAL = "ollama://llama3:70b"  # Assumes default host
MIXTRAL_LOCAL = "ollama://mixtral:8x7b"  # Assumes default host
COMMAND_R_PLUS_LOCAL = "ollama://command-r-plus"  # Assumes default host

# Google models (ensure GOOGLE_API_KEY is set in .env)
GEMINI_1_5_FLASH = "google://gemini-1.5-flash-latest"
GEMINI_1_5_PRO = "google://gemini-1.5-pro-latest"

# OpenRouter models (ensure OPENROUTER_API_KEY is set in .env)
# Replace with actual desired OpenRouter models
OR_MISTRAL_7B = "openrouter://mistralai/mistral-7b-instruct"
OR_LLAMA3_8B_INSTRUCT = "openrouter://meta-llama/llama-3-8b-instruct"
OR_GEMMA_7B = "openrouter://google/gemma-7b-it"


# Define test configurations
# Structure: "Menu Name": {"model_args": {"-ArgName": "model_uri_or_value"}, "extra_flags": "additional_flags_string"}
# The "model_args" will be formatted into command line arguments.
# "extra_flags" are appended directly.

TEST_CONFIGURATIONS = {
    "1: All Llama3-8B (Local Ollama - Fast Debug)": {
        "model_args": {
            "-InitialOutlineModel": LLAMA3_8B_LOCAL,
            "-ModelStoryElementsGenerator": LLAMA3_8B_LOCAL,  # New specific model arg
            "-ModelSceneOutliner": LLAMA3_8B_LOCAL,  # New specific model arg
            "-ModelSceneNarrativeGenerator": LLAMA3_8B_LOCAL,  # New specific model arg
            "-ModelChapterContextSummarizer": LLAMA3_8B_LOCAL,  # New specific model arg
            "-ModelChapterAssemblyRefiner": LLAMA3_8B_LOCAL,  # New specific model arg
            "-ChapterRevisionModel": LLAMA3_8B_LOCAL,
            "-RevisionModel": LLAMA3_8B_LOCAL,  # For feedback
            "-EvalModel": LLAMA3_8B_LOCAL,  # For ratings & JSON checks
            "-InfoModel": LLAMA3_8B_LOCAL,
            "-ScrubModel": LLAMA3_8B_LOCAL,
            "-CheckerModel": LLAMA3_8B_LOCAL,  # For things like chapter count initially
            "-TranslatorModel": LLAMA3_8B_LOCAL,
        },
        "extra_flags": "-NoChapterRevision -NoScrubChapters -Debug",  # Fast, less quality
    },
    "2: All Gemini 1.5 Flash (Google Cloud)": {
        "model_args": {
            "-InitialOutlineModel": GEMINI_1_5_FLASH,
            "-ModelStoryElementsGenerator": GEMINI_1_5_FLASH,
            "-ModelSceneOutliner": GEMINI_1_5_FLASH,
            "-ModelSceneNarrativeGenerator": GEMINI_1_5_FLASH,
            "-ModelChapterContextSummarizer": GEMINI_1_5_FLASH,
            "-ModelChapterAssemblyRefiner": GEMINI_1_5_FLASH,
            "-ChapterRevisionModel": GEMINI_1_5_FLASH,
            "-RevisionModel": GEMINI_1_5_FLASH,
            "-EvalModel": GEMINI_1_5_FLASH,
            "-InfoModel": GEMINI_1_5_FLASH,
            "-ScrubModel": GEMINI_1_5_FLASH,
            "-CheckerModel": GEMINI_1_5_FLASH,
            "-TranslatorModel": GEMINI_1_5_FLASH,
        },
        "extra_flags": "-Debug",  # Default flags for quality
    },
    "3: Mixed: Gemini 1.5 Pro (Outline/Scene Gen) + Flash (Revisions/Utils)": {
        "model_args": {
            "-InitialOutlineModel": GEMINI_1_5_PRO,
            "-ModelStoryElementsGenerator": GEMINI_1_5_PRO,
            "-ModelSceneOutliner": GEMINI_1_5_PRO,
            "-ModelSceneNarrativeGenerator": GEMINI_1_5_PRO,  # Core creative tasks
            "-ModelChapterAssemblyRefiner": GEMINI_1_5_PRO,
            "-ModelChapterContextSummarizer": GEMINI_1_5_FLASH,  # Summaries can use faster model
            "-ChapterRevisionModel": GEMINI_1_5_FLASH,  # Revisions can use faster
            "-RevisionModel": GEMINI_1_5_FLASH,  # Feedback
            "-EvalModel": GEMINI_1_5_FLASH,  # Ratings
            "-InfoModel": GEMINI_1_5_FLASH,
            "-ScrubModel": GEMINI_1_5_FLASH,
            "-CheckerModel": GEMINI_1_5_FLASH,
            "-TranslatorModel": GEMINI_1_5_FLASH,
        },
        "extra_flags": "-Debug",
    },
    "4: All OpenRouter Mixtral (Example)": {  # Replace with your preferred OpenRouter model
        "model_args": {
            "-InitialOutlineModel": OR_MISTRAL_7B,  # Example: using Mistral 7B for all
            "-ModelStoryElementsGenerator": OR_MISTRAL_7B,
            "-ModelSceneOutliner": OR_MISTRAL_7B,
            "-ModelSceneNarrativeGenerator": OR_MISTRAL_7B,
            "-ModelChapterContextSummarizer": OR_MISTRAL_7B,
            "-ModelChapterAssemblyRefiner": OR_MISTRAL_7B,
            "-ChapterRevisionModel": OR_MISTRAL_7B,
            "-RevisionModel": OR_MISTRAL_7B,
            "-EvalModel": OR_MISTRAL_7B,
            "-InfoModel": OR_MISTRAL_7B,
            "-ScrubModel": OR_MISTRAL_7B,
            "-CheckerModel": OR_MISTRAL_7B,
            "-TranslatorModel": OR_MISTRAL_7B,
        },
        "extra_flags": "-Debug",
    },
    "5: Quality Focus: Llama3-70B (Local) for Creative, Llama3-8B (Local) for Utils": {
        "model_args": {
            "-InitialOutlineModel": LLAMA3_70B_LOCAL,
            "-ModelStoryElementsGenerator": LLAMA3_70B_LOCAL,
            "-ModelSceneOutliner": LLAMA3_70B_LOCAL,
            "-ModelSceneNarrativeGenerator": LLAMA3_70B_LOCAL,
            "-ModelChapterAssemblyRefiner": LLAMA3_70B_LOCAL,
            "-ChapterRevisionModel": LLAMA3_70B_LOCAL,  # Important revisions with strong model
            "-ModelChapterContextSummarizer": LLAMA3_8B_LOCAL,
            "-RevisionModel": LLAMA3_8B_LOCAL,  # Feedback generation
            "-EvalModel": LLAMA3_8B_LOCAL,  # Ratings, JSON
            "-InfoModel": LLAMA3_8B_LOCAL,
            "-ScrubModel": LLAMA3_8B_LOCAL,
            "-CheckerModel": LLAMA3_8B_LOCAL,
            "-TranslatorModel": LLAMA3_8B_LOCAL,
        },
        "extra_flags": "-EnableFinalEditPass -Debug",  # Enable all quality steps
    },
    # Add more configurations as needed...
    # For example, a specific config from the user's original Test.py if one was particularly effective.
    # Option 8 from original: Miqu-70B + Llama3-70B editor. Assuming miqu is available via ollama.
    # Replace "ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434" with your actual URI
    "6: User's Original Config 8 (Miqu-70B + Llama3-70B Editor)": {
        "model_args": {
            # Using Miqu for all main generation tasks
            "-InitialOutlineModel": "ollama://<your_miqu_model_id_here>",  # Replace!
            "-ModelStoryElementsGenerator": "ollama://<your_miqu_model_id_here>",
            "-ModelSceneOutliner": "ollama://<your_miqu_model_id_here>",
            "-ModelSceneNarrativeGenerator": "ollama://<your_miqu_model_id_here>",
            "-ModelChapterAssemblyRefiner": "ollama://<your_miqu_model_id_here>",
            "-ChapterRevisionModel": "ollama://<your_miqu_model_id_here>",
            # Using Llama3-70B for supporting tasks as per original config's editor
            "-RevisionModel": LLAMA3_70B_LOCAL,  # For feedback generation
            "-EvalModel": LLAMA3_70B_LOCAL,  # For ratings, JSON checks
            "-InfoModel": LLAMA3_70B_LOCAL,
            "-ScrubModel": LLAMA3_70B_LOCAL,
            "-CheckerModel": LLAMA3_70B_LOCAL,  # For chapter count, etc.
            "-ModelChapterContextSummarizer": LLAMA3_70B_LOCAL,  # Context summaries
            "-TranslatorModel": LLAMA3_70B_LOCAL,
        },
        "extra_flags": "-Debug -NoScrubChapters",  # As per original choice 8 extra flags
    },
}

PROMPT_OPTIONS = {
    "1": "../Prompts/Harem/prompt.txt",  # Example path from source, adjust if needed
    "2": "../Prompts/Glitch/prompt.txt",  # Example path from source, adjust if needed
    "3": "Custom Prompt Path",
}


def display_menu(title: str, options: Dict[str, Any]) -> str:
    """Displays a menu and gets user choice."""
    print(f"\n--- {title} ---")
    for key, value in options.items():
        # For model configs, just show the key (menu name)
        # For prompt configs, show the path or description
        if title == "Choose Model Configuration":
            print(f"{key}")
        else:  # Prompts
            print(f"{key}: {value}")

    print("-------------------------------------------")
    while True:
        choice = input(f"Enter your choice (number or full key for models): ")
        if choice in options:
            return choice
        # Allow entering just the number part of the key for model configs
        if title == "Choose Model Configuration" and any(
            key.startswith(choice + ":") for key in options
        ):
            # Find the full key that starts with the number choice + ":"
            full_key_choice = next(
                (k for k in options if k.startswith(choice + ":")), None
            )
            if full_key_choice:
                return full_key_choice
        print("Invalid choice. Please try again.")


def main():
    print("AIStoryWriter Developer Testing Utility")

    # 1. Choose Model Configuration
    chosen_config_key = display_menu("Choose Model Configuration", TEST_CONFIGURATIONS)
    selected_config = TEST_CONFIGURATIONS[chosen_config_key]

    model_args_dict = selected_config["model_args"]
    base_extra_flags = selected_config.get(
        "extra_flags", ""
    )  # Get base flags from config

    # 2. Choose Prompt
    chosen_prompt_key = display_menu("Choose Prompt File", PROMPT_OPTIONS)
    prompt_file_path = PROMPT_OPTIONS[chosen_prompt_key]
    if chosen_prompt_key == "3":  # Custom Prompt Path
        prompt_file_path = input("Enter the full path to your custom prompt file: ")
        if not os.path.exists(prompt_file_path):
            print(f"Error: Prompt file not found at '{prompt_file_path}'. Exiting.")
            sys.exit(1)

    # 3. Seed
    seed_input = input(f"Enter Seed value (default: {Config.SEED}): ")
    try:
        seed_value = int(seed_input) if seed_input else Config.SEED
    except ValueError:
        print(f"Invalid seed value. Using default: {Config.SEED}")
        seed_value = Config.SEED

    # 4. Output filename (optional)
    output_filename_base = input(
        "Enter optional base output filename (e.g., MyStoryTest) (leave blank for default): "
    ).strip()
    output_flag = f'-Output "{output_filename_base}"' if output_filename_base else ""

    # 5. Additional Custom Flags
    print("\n--- Additional Flags ---")
    print(f"Current base flags from config: '{base_extra_flags}'")
    custom_extra_flags = input(
        "Enter any *additional* custom flags (e.g., -Translate French -NoChapterRevision), or leave blank: "
    ).strip()

    # Combine base flags from config with custom user flags
    # Simple concatenation; more sophisticated merging might be needed if flags conflict.
    final_extra_flags = f"{base_extra_flags} {custom_extra_flags}".strip()

    # Construct the command
    # Go up one directory to execute Write.py from the project root if Test.py is in Tools/
    # Adjust the path to Write.py if your structure is different.
    # Assuming Test.py is in Tools/ and Write.py is in 
    script_path = os.path.join("..", "Write.py")
    if not os.path.exists(script_path):
        # Fallback if Test.py is run from project root
        script_path = "Write.py"
        if not os.path.exists(script_path):
            print(
                f"Error: Main script Write.py not found at expected locations. Current dir: {os.getcwd()}"
            )
            sys.exit(1)

    command_parts = [
        sys.executable,  # Path to Python interpreter
        script_path,
        f'-Prompt "{prompt_file_path}"',
        f"-Seed {seed_value}",
    ]

    # Add model arguments
    for arg_name, model_uri in model_args_dict.items():
        # Check for specific new model argument names from refactoring
        # This ensures backward compatibility if old model args are still in some configs by mistake
        # while prioritizing the new ones if they exist.
        if arg_name in [
            "-InitialOutlineModel",
            "-ModelStoryElementsGenerator",
            "-ModelSceneOutliner",
            "-ModelSceneNarrativeGenerator",
            "-ModelChapterContextSummarizer",
            "-ModelChapterAssemblyRefiner",
            "-ChapterRevisionModel",
            "-RevisionModel",
            "-EvalModel",
            "-InfoModel",
            "-ScrubModel",
            "-CheckerModel",
            "-TranslatorModel",
        ]:
            command_parts.append(f'{arg_name} "{model_uri}"')
        # Deprecate old stage-specific models, but include if still present for old configs
        elif arg_name.startswith("-ChapterS") and arg_name.endswith("Model"):
            # Silently ignore old stage models unless specifically needed for a legacy test case.
            # For new scene-by-scene, these are not primary.
            # One might choose to map them to the new model args if a direct translation is desired.
            # print(f"Warning: Legacy model argument '{arg_name}' found. Consider updating test config to new model roles.")
            # command_parts.append(f"{arg_name} \"{model_uri}\"") # Uncomment to include if needed
            pass

    if output_flag:
        command_parts.append(output_flag)

    if final_extra_flags:
        command_parts.append(final_extra_flags)

    final_command = " ".join(command_parts)

    print("\n--- Executing Command ---")
    print(final_command)
    print("---------------------------\n")

    # Execute the command
    # Note: os.system is simple but has security implications if inputs are not controlled.
    # For a developer tool with known inputs, it's often acceptable.
    # subprocess.run is generally preferred for more control.
    exit_code = os.system(final_command)

    if exit_code == 0:
        print("\n--- Command Executed Successfully ---")
    else:
        print(f"\n--- Command Exited with Code: {exit_code} ---")


if __name__ == "__main__":
    main()
