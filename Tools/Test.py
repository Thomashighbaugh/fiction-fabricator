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
