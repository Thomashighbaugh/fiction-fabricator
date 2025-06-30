# Project Structure

```
fiction-fabricator/
├── Tools/
│   ├── PromptGenerator.py
│   └── Test.py
├── Writer/
│   ├── Chapter/
│   │   ├── ChapterDetector.py
│   │   ├── ChapterGenSummaryCheck.py
│   │   ├── ChapterGenerator.py
│   │   └── \
│   ├── Interface/
│   │   ├── OpenRouter.py
│   │   └── Wrapper.py
│   ├── Outline/
│   │   └── StoryElements.py
│   ├── Scene/
│   │   ├── ChapterByScene.py
│   │   ├── ChapterOutlineToScenes.py
│   │   ├── SceneOutlineToScene.py
│   │   └── ScenesToJSON.py
│   ├── Config.py
│   ├── CritiqueRevision.py
│   ├── LLMEditor.py
│   ├── NarrativeContext.py
│   ├── NovelEditor.py
│   ├── OutlineGenerator.py
│   ├── PrintUtils.py
│   ├── Prompts.py
│   ├── Scrubber.py
│   ├── Statistics.py
│   ├── StoryInfo.py
│   ├── SummarizationUtils.py
│   └── Translator.py
├── Evaluate.py
├── README.md
├── Write.py
├── config.ini
└── requirements.txt
```

# Project Files

## File: `Tools/PromptGenerator.py`

```python
# File: Tools/prompt_generator.py
# Purpose: Generates a refined prompt.txt for FictionFabricator using an LLM.
# This script is self-contained and should be run from the project's root directory.

"""
FictionFabricator Prompt Generator Utility.

This script takes a basic user idea and a desired story title to generate a more
detailed and refined `prompt.txt` file. This output file is structured to be an
effective input for the main Write.py script.

The process involves:
1. Dynamically selecting an LLM from available providers (Google, Groq, Mistral, Ollama, NVIDIA).
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
import json
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
import Writer.Config # Import config to access NVIDIA model list

# --- Model Discovery Functions (copied from Write.py) ---
def get_ollama_models(logger):
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

def get_google_models(logger):
    """Queries Google for available Gemini models."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("-> Google: GOOGLE_API_KEY not found in .env file. Skipping.")
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

def get_groq_models(logger):
    """Queries GroqCloud for available models."""
    if not os.environ.get("GROQ_API_KEY"):
        print("-> GroqCloud: GROQ_API_KEY not found in .env file. Skipping.")
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

def get_mistral_models(logger):
    """Queries MistralAI for available models."""
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
        logger.Log(f"Found {len(available_models)} compatible MistralAI models.", 3)
        return available_models
    except ImportError:
        logger.Log("'mistralai' library not installed. Skipping MistralAI provider.", 6)
        return []
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

def get_llm_selection_menu_for_tool(logger):
    """
    Queries providers, presents a menu to the user, and returns the chosen model URI.
    """
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
        return None

    print("\n--- Prompt Generator LLM Selection ---")
    print("Please select the model for prompt generation:")
    sorted_models = sorted(all_models)
    for i, model in enumerate(sorted_models):
        print(f"[{i+1}] {model}")

    while True:
        choice = input("> ").strip().lower()
        if choice.isdigit() and 1 <= int(choice) <= len(sorted_models):
            selected_model = sorted_models[int(choice) - 1]
            print(f"Selected: {selected_model}")
            return selected_model
        else:
            print("Invalid choice. Please enter a number from the list.")

# --- Prompts for this script ---

EXPAND_IDEA_PROMPT_TEMPLATE = """
You are a creative assistant helping to flesh out a story idea into a more detailed prompt suitable for an AI story generator like FictionFabricator.
The user has provided a basic idea and a title.
Your goal is to expand this into a richer concept that FictionFabricator can effectively use.

User's Title: "{title}"
User's Basic Idea: "{idea}"

Expand this into a more detailed story prompt. Consider including or hinting at:
- **Genre and Tone:** What kind of story is it (e.g., sci-fi, fantasy, mystery, horror, romance)? What is the desired mood (e.g., dark, humorous, adventurous, introspective)?
- **Core Conflict:** What is the central problem or challenge the characters will face?
- **Main Character(s) Sketch:** Briefly introduce 1-2 main characters. What are their key traits or motivations related to the idea?
- **Setting Snippet:** A brief hint about the world or primary location.
- **Key Plot Beats (Optional but helpful):** If any specific events or turning points come to mind from the user's idea, mention them.
- **Specific "Do's" or "Don'ts" (Optional):** Are there any constraints or desired inclusions that would be important for the AI story generator? For example, "The story must include a talking cat," or "Avoid overly graphic violence."
- **Target Audience/Style (Optional):** E.g., "Young Adult fantasy with a fast pace," or "Literary fiction with deep character exploration."

Your response should be *only* the expanded story prompt itself.
Do not include any titles, headings, preambles (e.g., "Here is the expanded idea:"), or other conversational text.
Begin your response *directly* with the expanded story prompt text.
Make it engaging and provide enough substance for the AI to build upon.
"""

CRITIQUE_EXPANDED_PROMPT_TEMPLATE = """
You are an expert AI prompt engineer evaluating a story prompt intended for an advanced AI story generation system.
The system will use this prompt to generate story elements, an outline, and then the full narrative.

Here is the expanded story prompt you need to critique:
---
{expanded_prompt}
---

Critique this prompt based on the following criteria for its effectiveness as input to FictionFabricator:
1.  **Clarity and Specificity:**
    *   Is the core story idea clear?
    *   Are genre, tone, and style sufficiently indicated or implied?
    *   Are main characters (if mentioned) distinct enough to start with?
    *   Is the central conflict understandable?
    *   Does it provide enough specific detail for the AI to avoid overly generic output, without being overly prescriptive and stifling creativity?
2.  **Completeness (for FictionFabricator):**
    *   Does it hint at enough elements for `StoryElements.generate_story_elements` to work well (e.g., potential for themes, setting details, character motivations)?
    *   Does it provide a good foundation for `OutlineGenerator.generate_outline` to create a multi-chapter plot?
3.  **Actionability for AI:**
    *   Are there clear starting points for the AI?
    *   Are there any ambiguities or contradictions that might confuse the AI?
4.  **Engagement Factor:**
    *   Does the prompt itself sound interesting and inspire creative possibilities?

Provide your critique as a list of bullet points (strengths and weaknesses).
Be constructive. The goal is to identify areas for improvement.
Example:
- Strength: Clearly defines the sci-fi genre and a compelling central mystery.
- Weakness: Main character motivation is vague. Suggest adding a specific goal.
- Weakness: Setting is too generic. Suggest adding 1-2 unique details about the world.
"""

REFINE_PROMPT_BASED_ON_CRITIQUE_TEMPLATE = """
You are a master creative assistant. You have an expanded story prompt and a critique of that prompt.
Your task is to revise and improve the original expanded prompt based *only* on the provided critique.
The goal is to create a final, high-quality prompt.txt file that will be excellent input for an AI story generator like FictionFabricator.

Original Expanded Story Prompt:
---
{expanded_prompt}
---

Critique of the Expanded Story Prompt:
---
{critique}
---

Based on the critique, revise the "Original Expanded Story Prompt".
Your entire response MUST be *only* the revised story prompt text itself.
Do NOT include:
- Any titles or headings (e.g., "Revised Prompt:", "Final Prompt").
- Any introductory or leading sentences (e.g., "Here is the revised prompt:", "Okay, I have revised the prompt as follows:").
- Any concluding remarks or summaries (e.g., "This prompt now addresses all points.", "I hope this is helpful.").
- Any explanations of the changes made or how you followed instructions.
- Any text other than the core, revised story prompt.

The output will be saved directly to a file, so it must contain *only* the story prompt.
Begin your response *directly* with the revised story prompt.
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
    while start_index < len(lines) and not lines[start_index].strip():
        start_index += 1
    lines = lines[start_index:]
    if not lines:
        return ""

    header_patterns = [
        re.compile(r"^\s*(?:OKAY|SURE|CERTAINLY|ALRIGHT|UNDERSTOOD)\s*[,.]?\s*HERE(?:'S| IS)? THE (?:REVISED|FINAL|EXPANDED|REQUESTED)?\s*PROMPT\s*[:.]?\s*$", re.IGNORECASE),
        re.compile(r"^\s*HERE(?:'S| IS)? THE (?:REVISED|FINAL|EXPANDED|REQUESTED)?\s*PROMPT\s*[:.]?\s*$", re.IGNORECASE),
        re.compile(r"^\s*(?:REVISED|FINAL|EXPANDED|STORY)?\s*PROMPT\s*[:]?\s*$", re.IGNORECASE),
        re.compile(r"^\s*OUTPUT\s*[:]?\s*$", re.IGNORECASE),
        re.compile(r"^\s*HERE IS THE .* PROMPT TEXT(?:,? CONTAINING ONLY THE PROMPT ITSELF)?\s*[:.]?\s*$", re.IGNORECASE),
        re.compile(r"^\s*OKAY\s*[,.]?\s*$", re.IGNORECASE),
        re.compile(r"^\s*SURE\s*[,.]?\s*$", re.IGNORECASE),
        re.compile(r"^\s*HERE YOU GO\s*[:.]?\s*$", re.IGNORECASE),
    ]

    if lines:
        first_line_content = lines[0].strip()
        for pattern in header_patterns:
            if pattern.fullmatch(first_line_content):
                lines.pop(0)
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
    selected_model_uri = get_llm_selection_menu_for_tool(sys_logger)
    if not selected_model_uri:
        sys_logger.Log("No model was selected or discovered. Exiting.", 7)
        sys.exit(1)

    # --- Instantiate Interface and load selected model ---
    interface = Interface()
    interface.LoadModels([selected_model_uri])

    # --- Generation Logic ---
    print("\nStep 1: Expanding user's idea...")
    expand_user_prompt = EXPAND_IDEA_PROMPT_TEMPLATE.format(title=args.title, idea=args.idea)
    expand_model_with_params = f"{selected_model_uri}?temperature={args.temp}&max_tokens=1500"

    expand_messages = [
        interface.BuildSystemQuery("You are a creative assistant helping to flesh out story ideas."),
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
        interface.BuildSystemQuery("You are an expert AI prompt engineer and literary critic."),
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
        refine_model_with_params = f"{selected_model_uri}?temperature={args.temp}&max_tokens=1500"

        refine_messages = [
            interface.BuildSystemQuery("You are a master creative assistant, skilled at revising text based on feedback."),
            interface.BuildUserQuery(refine_user_prompt)
        ]
        refine_history = interface.SafeGenerateText(sys_logger, refine_messages, refine_model_with_params, min_word_count_target=100)
        refined_text_raw = interface.GetLastMessageText(refine_history)

        if "[ERROR:" in refined_text_raw:
            print(f"Failed to refine prompt: {refined_text_raw}")
            print("Warning: Refinement failed. Using the initially expanded prompt.")
            final_prompt_text_candidate = expanded_prompt
        else:
            final_prompt_text_candidate = _extract_core_prompt(refined_text_raw)

    final_prompt_text = final_prompt_text_candidate
    if not final_prompt_text.strip():
        print("Error: Final prompt is empty after all processing. Exiting.")
        if expanded_prompt.strip():
            print("Fallback to last valid prompt (expanded).")
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
print("\nChoose Prompt:")
print("-------------------------------------------")
print("1 -> ExamplePrompts/Example1/Prompt.txt (Default)")
print("2 -> ExamplePrompts/Example2/Prompt.txt")
print("3 -> Custom Prompt")
print("-------------------------------------------")
prompt_choice = input("> ")

prompt_file = ""
if prompt_choice in ["", "1"]:
    prompt_file = "ExamplePrompts/Example1/Prompt.txt"
elif prompt_choice == "2":
    prompt_file = "ExamplePrompts/Example2/Prompt.txt"
elif prompt_choice == "3":
    prompt_file = input("Enter Prompt File Path: ")
else:
    print("Invalid prompt choice. Using default.")
    prompt_file = "ExamplePrompts/Example1/Prompt.txt"

# Get Any Extra Flags
print("\nExtra Flags (e.g., -Debug -NoScrubChapters):")
print("Default = '-ExpandOutline'")
print("-------------------------------------------")
extra_flags = input("> ")

if extra_flags == "":
    extra_flags = "-ExpandOutline"


# --- Command Construction and Execution ---

# Build the base command
command_parts = [
    "cd .. && ./Write.py",
    f"-Prompt {prompt_file}",
    "-Seed 999",  # Use a consistent seed for reproducibility
]

# Add model arguments from the selected configuration
for model_arg, model_name in selected_config["models"].items():
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
    This is a non-creative, JSON-focused task.
    """
    prompt = Writer.Prompts.CHAPTER_COUNT_PROMPT.format(_Summary=_Summary)

    _Logger.Log("Prompting LLM to get chapter count (JSON)...", 5)
    
    messages = [Interface.BuildUserQuery(prompt)]

    # Use SafeGenerateJSON to handle the request. It will retry if the JSON is invalid.
    # No critique-revision cycle is needed for this simple, non-creative task.
    _, response_json = Interface.SafeGenerateJSON(
        _Logger,
        messages,
        Writer.Config.EVAL_MODEL,
        _RequiredAttribs=["TotalChapters"]
    )

    try:
        total_chapters = int(response_json.get("TotalChapters", -1))
        if total_chapters > 0:
            _Logger.Log(f"LLM detected {total_chapters} chapters.", 5)
            return total_chapters
        else:
            _Logger.Log(f"LLM returned an invalid chapter count: {total_chapters}. Defaulting to -1.", 7)
            return -1
            
    except (ValueError, TypeError) as e:
        _Logger.Log(f"Critical Error: Could not parse 'TotalChapters' as an integer. Error: {e}", 7)
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
    # LLM Length Check - A simple guard against empty or near-empty responses.
    if len(_Work.split()) < 100:
        _Logger.Log(
            "Previous response didn't meet the length requirement (100 words), so it likely failed to generate properly.",
            7,
        )
        return False, "The generated text was too short. Please write a full, detailed response."

    # --- Step 1: Summarize the generated work ---
    _Logger.Log("Summarizing the generated work for comparison...", 3)
    SummaryLangchain = [
        Interface.BuildSystemQuery(Writer.Prompts.SUMMARY_CHECK_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.SUMMARY_CHECK_PROMPT.format(_Work=_Work))
    ]
    SummaryLangchain = Interface.SafeGenerateText(
        _Logger, SummaryLangchain, Writer.Config.CHECKER_MODEL, min_word_count_target=30
    )
    WorkSummary = Interface.GetLastMessageText(SummaryLangchain)

    # --- Step 2: Summarize the reference outline ---
    _Logger.Log("Summarizing the reference outline for comparison...", 3)
    SummaryLangchain = [
        Interface.BuildSystemQuery(Writer.Prompts.SUMMARY_OUTLINE_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.SUMMARY_OUTLINE_PROMPT.format(_RefSummary=_RefSummary))
    ]
    SummaryLangchain = Interface.SafeGenerateText(
        _Logger, SummaryLangchain, Writer.Config.CHECKER_MODEL, min_word_count_target=30
    )
    OutlineSummary = Interface.GetLastMessageText(SummaryLangchain)

    # --- Step 3: Generate a JSON comparison ---
    _Logger.Log("Comparing summaries to check for outline adherence...", 3)
    ComparisonLangchain = [
        Interface.BuildSystemQuery(Writer.Prompts.SUMMARY_COMPARE_INTRO),
        Interface.BuildUserQuery(
            Writer.Prompts.SUMMARY_COMPARE_PROMPT.format(
                WorkSummary=WorkSummary, OutlineSummary=OutlineSummary
            )
        )
    ]
    
    # This is a non-creative, JSON-focused task.
    _, ResponseJSON = Interface.SafeGenerateJSON(
        _Logger,
        ComparisonLangchain,
        Writer.Config.EVAL_MODEL, # Use the EVAL_MODEL for this check
        _RequiredAttribs=["DidFollowOutline", "Suggestions"]
    )
    
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

    # Get the rich context summary from the narrative context object
    context_for_generation = narrative_context.get_context_for_chapter_generation(_ChapterNum)

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
            context_for_generation, _ChapterNum, _TotalChapters,
            Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
            narrative_context
        )

        # STAGE 2: Character Development
        char_dev_text = execute_generation_stage(
            Interface, _Logger, "Character Development",
            Writer.Prompts.CHAPTER_GENERATION_STAGE2,
            {"ThisChapterOutline": chapter_specific_outline, "Stage1Chapter": plot_text, "Feedback": ""},
            context_for_generation, _ChapterNum, _TotalChapters,
            Writer.Config.CHAPTER_STAGE2_WRITER_MODEL,
            narrative_context
        )

        # STAGE 3: Dialogue
        dialogue_text = execute_generation_stage(
            Interface, _Logger, "Dialogue Addition",
            Writer.Prompts.CHAPTER_GENERATION_STAGE3,
            {"ThisChapterOutline": chapter_specific_outline, "Stage2Chapter": char_dev_text, "Feedback": ""},
            context_for_generation, _ChapterNum, _TotalChapters,
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
            revision_messages = [Interface.BuildUserQuery(revision_prompt)]
            revision_messages = Interface.SafeGenerateText(
                _Logger, revision_messages, Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
                min_word_count_target=int(len(current_chapter_text.split()) * 0.8)
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
    narrative_context_str: str,
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

    full_format_args = {
        "narrative_context": narrative_context_str,
        "_ChapterNum": chapter_num,
        "_TotalChapters": total_chapters,
        **format_args
    }
    prompt = prompt_template.format(**full_format_args)
    messages = [Interface.BuildUserQuery(prompt)]

    min_words = 150
    if "Stage1Chapter" in format_args:
        min_words = len(format_args["Stage1Chapter"].split())
    if "Stage2Chapter" in format_args:
        min_words = len(format_args["Stage2Chapter"].split())

    messages = Interface.SafeGenerateText(
        _Logger, messages, model, min_word_count_target=min_words
    )
    initial_content = Interface.GetLastMessageText(messages)

    # --- Critique and Revise ---
    _Logger.Log(f"Critiquing and revising content for {stage_name}...", 3)

    task_description = f"You are writing a novel. Your current task is '{stage_name}' for Chapter {chapter_num}. You need to generate content that fulfills this stage's specific goal (e.g., plot, character development, dialogue) while remaining coherent with the overall story."

    revised_content = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_content,
        task_description=task_description,
        narrative_context_summary=narrative_context_str,
        initial_user_prompt=narrative_context.initial_prompt,
    )

    _Logger.Log(f"Finished stage: {stage_name}", 5)
    return revised_content

```

## File: `Writer/Chapter/\`

```text
#!/usr/bin/python3

import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def LLMCountChapters(Interface: Interface, _Logger: Logger, _Summary: str) -> int:
    """
    Counts the number of chapters in a given story outline using an LLM.
    This is a non-creative, JSON-focused task.
    """
    prompt = Writer.Prompts.CHAPTER_COUNT_PROMPT.format(_Summary=_Summary)

    _Logger.Log("Prompting LLM to get chapter count (JSON)...", 5)
    
    messages = [Interface.BuildUserQuery(prompt)]

    # Use SafeGenerateJSON to handle the request. It will retry if the JSON is invalid.
    # No critique-revision cycle is needed for this simple, non-creative task.
    _, response_json = Interface.SafeGenerateJSON(
        _Logger,
        messages,
        Writer.Config.EVAL_MODEL,
        _RequiredAttribs=["TotalChapters"]
    )

    try:
        total_chapters = int(response_json.get("TotalChapters", -1))
        if total_chapters > 0:
            _Logger.Log(f"LLM detected {total_chapters} chapters.", 5)
            return total_chapters
        else:
            _Logger.Log(f"LLM returned an invalid chapter count: {total_chapters}. Defaulting to -1.", 7)
            return -1
            
    except (ValueError, TypeError) as e:
        _Logger.Log(f"Critical Error: Could not parse 'TotalChapters' as an integer. Error: {e}", 7)
        return -1

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
import inspect
import signal
import platform
from urllib.parse import parse_qs

import Writer.Config
from Writer.PrintUtils import Logger

# --- Langchain Provider Imports ---
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.chat_models import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_groq import ChatGroq
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import AzureChatOpenAI, ChatOpenAI

# Note: dotenv is loaded at the main entry point in Write.py.

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
        self.History = []
        self.LoadModels(Models)

    def GetModelAndProvider(self, _Model: str) -> (str, str, str, dict):
        """
        Parses a model string like 'Provider://Model@Host?param1=val1' using robust string splitting.
        """
        if "://" not in _Model:
            return "ollama", _Model, "localhost:11434", {}

        provider_part, rest = _Model.split("://", 1)
        Provider = provider_part
        main_part = rest
        query_part = ""
        if "?" in rest:
            main_part, query_part = rest.split("?", 1)

        Host = None
        ProviderModel = main_part
        if "@" in main_part:
            ProviderModel, Host = main_part.split("@", 1)

        if Provider == 'ollama' and not Host:
            Host = 'localhost:11434'

        FlatParams = {}
        if query_part:
            for key, values in parse_qs(query_part).items():
                val = values[0]
                try:
                    if val.isdigit() and '.' not in val:
                        FlatParams[key] = int(val)
                    else:
                        FlatParams[key] = float(val)
                except ValueError:
                    if val.lower() in ['true', 'false']:
                        FlatParams[key] = val.lower() == 'true'
                    else:
                        FlatParams[key] = val

        return Provider, ProviderModel, Host, FlatParams

    def LoadModels(self, Models: list):
        for Model in Models:
            base_model_uri = Model.split('?')[0]
            if base_model_uri in self.Clients:
                continue

            Provider, ProviderModel, ModelHost, ModelOptions = self.GetModelAndProvider(Model)
            _Logger = Logger()
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
                _Logger.Log(f"CRITICAL: Failed to verify config for model '{Model}'. Error: {e}", 7)

    def SafeGenerateText(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _Format: str = None, min_word_count_target: int = 50) -> list:
        _Messages = [msg for msg in _Messages if msg.get("content", "").strip()]
        
        # --- First Attempt ---
        NewMsgHistory = self.ChatAndStreamResponse(_Logger, _Messages, _Model, _SeedOverride, _Format)
        
        last_response_text = self.GetLastMessageText(NewMsgHistory)
        word_count = len(last_response_text.split())

        # --- Check and Retry Logic ---
        if not last_response_text.strip() or word_count < min_word_count_target:
            if not last_response_text.strip():
                _Logger.Log("SafeGenerateText: Generation failed (empty). Retrying...", 7)
            else:
                _Logger.Log(f"SafeGenerateText: Generation failed (short response: {word_count} words, target: {min_word_count_target}). Retrying...", 7)

            if NewMsgHistory and NewMsgHistory[-1].get("role") == "assistant":
                NewMsgHistory.pop()

            # Append a corrective instruction to the last user message
            if NewMsgHistory and NewMsgHistory[-1].get("role") == "user":
                corrective_prompt = f"\n\n---SYSTEM NOTE---\nThe previous response was too short. Please generate a more detailed and comprehensive response that is at least {min_word_count_target} words long. Fulfill the original request completely."
                NewMsgHistory[-1]["content"] += corrective_prompt

            # --- Second Attempt ---
            NewMsgHistory = self.ChatAndStreamResponse(_Logger, NewMsgHistory, _Model, random.randint(0, 99999), _Format)
            
            last_response_text = self.GetLastMessageText(NewMsgHistory)
            word_count = len(last_response_text.split())
            
            # --- Final Check with User Interaction ---
            if not last_response_text.strip() or word_count < min_word_count_target:
                _Logger.Log(f"SafeGenerateText: Retry also failed to meet word count (got {word_count}, target {min_word_count_target}).", 6)
                while True:
                    user_choice = input("Do you want to [c]ontinue with the short response or [t]ry again? (c/t): ").lower()
                    if user_choice == 't':
                        if NewMsgHistory and NewMsgHistory[-1].get("role") == "assistant":
                            NewMsgHistory.pop()
                        NewMsgHistory = self.ChatAndStreamResponse(_Logger, NewMsgHistory, _Model, random.randint(0, 99999), _Format)
                        last_response_text = self.GetLastMessageText(NewMsgHistory)
                        word_count = len(last_response_text.split())
                        if word_count >= min_word_count_target:
                            _Logger.Log("Success on manual retry.", 5)
                            break
                        else:
                             _Logger.Log(f"Manual retry also failed (got {word_count}).", 6)
                    elif user_choice == 'c':
                        _Logger.Log("User chose to continue with the short response.", 4)
                        break
                    else:
                        print("Invalid input. Please enter 'c' or 't'.")

        return NewMsgHistory

    def SafeGenerateJSON(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _RequiredAttribs: list = []) -> (list, dict):
        while True:
            ResponseHistory = self.ChatAndStreamResponse(_Logger, _Messages, _Model, _SeedOverride, _Format="json")
            try:
                RawResponse = self.GetLastMessageText(ResponseHistory).replace("```json", "").replace("```", "").strip()
                JSONResponse = json.loads(RawResponse)
                for _Attrib in _RequiredAttribs:
                    if _Attrib not in JSONResponse:
                        raise KeyError(f"Required attribute '{_Attrib}' not in JSON response.")
                return ResponseHistory, JSONResponse
            except (json.JSONDecodeError, KeyError) as e:
                _Logger.Log(f"JSON Error: {e}. Retrying...", 7)
                if ResponseHistory and ResponseHistory[-1].get("role") == "assistant":
                    ResponseHistory.pop()
                _SeedOverride = random.randint(0, 99999)

    def ChatAndStreamResponse(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _Format: str = None) -> list:
        Provider, ProviderModel, ModelHost, ModelOptions = self.GetModelAndProvider(_Model)
        base_model_uri = _Model.split('?')[0]

        if _SeedOverride != -1:
            ModelOptions['seed'] = _SeedOverride
        elif 'seed' not in ModelOptions and Writer.Config.SEED != -1:
            ModelOptions['seed'] = Writer.Config.SEED

        if _Format and _Format.lower() == 'json':
            if Provider == 'ollama':
                ModelOptions['format'] = 'json'
            elif Provider == 'google':
                ModelOptions['response_mime_type'] = 'application/json'

        client = None
        if Provider == "github":
            try:
                github_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
                github_token = os.environ.get("GITHUB_ACCESS_TOKEN")
                
                if ProviderModel.startswith("mistral-ai/"):
                    _Logger.Log(f"Using MistralAI client for GitHub model: {ProviderModel}", 1)
                    client = ChatMistralAI(endpoint=github_endpoint, api_key=github_token, model=ProviderModel)
                elif ProviderModel.startswith(("openai/", "cohere/", "xai/", "deepseek/")):
                    _Logger.Log(f"Using OpenAI-compatible client for GitHub model: {ProviderModel}", 1)
                    client = ChatOpenAI(base_url=github_endpoint, api_key=github_token, model=ProviderModel)
                else: 
                    _Logger.Log(f"Using AzureOpenAI client for GitHub model: {ProviderModel}", 1)
                    client = AzureChatOpenAI(azure_endpoint=github_endpoint, api_key=github_token, azure_deployment=ProviderModel, api_version=Writer.Config.GITHUB_API_VERSION)
            except Exception as e:
                _Logger.Log(f"Failed to create on-demand GitHub client for '{ProviderModel}'. Error: {e}", 7)
                _Messages.append({"role": "assistant", "content": f"[ERROR: Failed to create GitHub client.]"})
                return _Messages
        else:
            client = self.Clients.get(base_model_uri)

        if not client:
            _Logger.Log(f"Model client for '{base_model_uri}' could not be loaded or created. Aborting.", 7)
            _Messages.append({"role": "assistant", "content": f"[ERROR: Model {base_model_uri} not loaded.]"})
            return _Messages

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
        
        # Determine appropriate timeout
        timeout_duration = Writer.Config.OLLAMA_TIMEOUT if Provider == 'ollama' else Writer.Config.DEFAULT_TIMEOUT
        
        # Set up signal handler for timeout, only on non-Windows systems
        if platform.system() != "Windows":
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_duration)
        
        try:
            if Provider == 'ollama':
                stream = client.stream(langchain_messages, options=filtered_options)
            elif Provider == 'google':
                gen_config_keys = ["temperature", "top_p", "top_k", "max_output_tokens", "response_mime_type"]
                generation_config = {k: v for k, v in filtered_options.items() if k in gen_config_keys}
                
                seed_to_bind = {}
                if 'seed' in filtered_options:
                    seed_to_bind['seed'] = filtered_options['seed']
                
                bound_client = client.bind(**seed_to_bind) if seed_to_bind else client
                stream = bound_client.stream(langchain_messages, generation_config=generation_config)
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
            _Logger.Log(f"CRITICAL: Exception during LLM call to '{_Model}': {e}", 7)
            full_response = f"[ERROR: Generation failed. {e}]"
        finally:
            # Disable the alarm
            if platform.system() != "Windows":
                signal.alarm(0)

        elapsed = time.time() - start_time
        _Logger.Log(f"Generated response in {elapsed:.2f}s", 4)
        _Messages.append({"role": "assistant", "content": full_response})
        return _Messages

    def BuildUserQuery(self, _Query: str) -> dict:
        return {"role": "user", "content": _Query}

    def BuildSystemQuery(self, _Query: str) -> dict:
        return {"role": "system", "content": _Query}

    def BuildAssistantQuery(self, _Query: str) -> dict:
        return {"role": "assistant", "content": _Query}

    def GetLastMessageText(self, _Messages: list) -> str:
        if not _Messages:
            return ""
        return _Messages[-1].get("content", "")

```

## File: `Writer/Outline/StoryElements.py`

```python
import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config


def GenerateStoryElements(Interface, _Logger, _OutlinePrompt):

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

        # A. Create a context object for the current scene
        current_scene_context = SceneContext(scene_number=scene_num, initial_outline=scene_outline)
        
        # B. Generate the full text for the scene
        scene_text = Writer.Scene.SceneOutlineToScene.SceneOutlineToScene(
            Interface,
            _Logger,
            scene_outline,
            narrative_context,
            chapter_context.chapter_number,
            scene_num,
        )
        current_scene_context.set_generated_content(scene_text)
        rough_chapter_text += scene_text + "\n\n" # Append scene to the chapter text

        # C. Summarize the scene and extract key points for coherence
        if Writer.Config.SCENE_GENERATION_PIPELINE: # Check if summarization is part of the flow
            summary_data = Writer.SummarizationUtils.summarize_scene_and_extract_key_points(
                Interface,
                _Logger,
                scene_text,
                narrative_context,
                chapter_context.chapter_number,
                scene_num,
            )
            current_scene_context.set_summary(summary_data.get("summary"))
            for point in summary_data.get("key_points_for_next_scene", []):
                current_scene_context.add_key_point(point)
            
            _Logger.Log(f"Scene {scene_num} Summary: {current_scene_context.summary}", 1)
            _Logger.Log(f"Scene {scene_num} Key Points: {current_scene_context.key_points_for_next_scene}", 1)

        # D. Add the completed scene context to the chapter context
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
        _Prompt=narrative_context.initial_prompt, # Anchor to the original prompt
    )

    messages = [
        Interface.BuildSystemQuery(Writer.Prompts.DEFAULT_SYSTEM_PROMPT),
        Interface.BuildUserQuery(initial_prompt),
    ]

    response_messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, min_word_count_target=100
    )
    initial_scene_breakdown = Interface.GetLastMessageText(response_messages)
    _Logger.Log("Finished initial scene breakdown generation.", 5)

    # --- Step 2: Critique and Revise ---
    _Logger.Log("Critiquing and revising scene breakdown for coherence and quality...", 3)

    task_description = f"Break down the provided chapter outline for Chapter {_ChapterNum} into a detailed, scene-by-scene plan. Each scene should have a clear purpose, setting, character list, and a summary of events, contributing to the chapter's overall arc."

    context_summary = narrative_context.get_context_for_chapter_generation(_ChapterNum)
    context_summary += f"\n\nThis chapter's specific outline, which you need to expand into scenes, is:\n{_ThisChapterOutline}"

    revised_scene_breakdown = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_scene_breakdown,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
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
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext
from Writer.PrintUtils import Logger


def SceneOutlineToScene(
    Interface: Interface,
    _Logger: Logger,
    _ThisSceneOutline: str,
    narrative_context: NarrativeContext,
    _ChapterNum: int,
    _SceneNum: int,
) -> str:
    """
    Generates the full text for a single scene based on its detailed outline.
    This is a creative task that undergoes a critique and revision cycle.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        _ThisSceneOutline: The detailed markdown outline for the specific scene to be written.
        narrative_context: The context object for the entire novel.
        _ChapterNum: The number of the current chapter.
        _SceneNum: The number of the current scene.

    Returns:
        A string containing the fully written scene text.
    """
    _Logger.Log(f"Starting SceneOutline -> Scene generation for C{_ChapterNum} S{_SceneNum}.", 2)

    # --- Step 1: Initial Generation ---
    _Logger.Log("Generating initial scene text...", 5)

    scene_context_for_prompt = narrative_context.get_context_for_scene_generation(
        _ChapterNum, _SceneNum
    )

    initial_prompt = Writer.Prompts.SCENE_OUTLINE_TO_SCENE.format(
        _SceneOutline=_ThisSceneOutline,
        narrative_context=scene_context_for_prompt,
    )

    messages = [
        Interface.BuildSystemQuery(Writer.Prompts.DEFAULT_SYSTEM_PROMPT),
        Interface.BuildUserQuery(initial_prompt),
    ]

    response_messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, min_word_count_target=100
    )
    initial_scene_text = Interface.GetLastMessageText(response_messages)
    _Logger.Log("Finished initial scene generation.", 5)

    # --- Step 2: Critique and Revise ---
    _Logger.Log(f"Critiquing and revising C{_ChapterNum} S{_SceneNum} for quality...", 3)

    task_description = f"Write a full, compelling scene for Chapter {_ChapterNum}, Scene {_SceneNum}, based on its outline. The scene should include engaging prose, character interactions, and dialogue, and it must seamlessly connect with the preceding events."

    context_summary = scene_context_for_prompt

    revised_scene_text = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_scene_text,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
    )

    _Logger.Log(f"Finished SceneOutline -> Scene generation for C{_ChapterNum} S{_SceneNum}.", 2)
    return revised_scene_text

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
import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def critique_and_revise_creative_content(
    Interface: Interface,
    _Logger: Logger,
    initial_content: str,
    task_description: str,
    narrative_context_summary: str,
    initial_user_prompt: str,
    is_json: bool = False,
) -> str:
    """
    Orchestrates the critique and revision process for a piece of generated creative content.
    This process is a single pass: critique -> revise.

    1. Prompts a critique LLM to generate feedback on the initial_content.
    2. Prompts a revision LLM to revise the initial_content based on the received critique.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        initial_content: The text to be critiqued and revised.
        task_description: A description of what the content was supposed to achieve.
        narrative_context_summary: A summary of the story so far to provide context.
        initial_user_prompt: The original prompt from the user, to ensure alignment.
        is_json: A flag to indicate if the content is JSON and should be handled accordingly.

    Returns:
        The revised content as a string.
    """

    # --- Step 1: Generate Critique ---
    _Logger.Log("Starting critique generation for the latest content.", 5)

    json_guidance = (
        "The content is JSON. Focus your critique on the substance, clarity, and narrative value "
        "of the data within the JSON structure, not just the format. Respond with your critique as a plain string."
    ) if is_json else "Respond with your critique as a plain string."

    critique_prompt = Writer.Prompts.CRITIQUE_CREATIVE_CONTENT_PROMPT.format(
        text_to_critique=initial_content,
        task_description=task_description,
        narrative_context_summary=narrative_context_summary,
        initial_user_prompt=initial_user_prompt,
        is_json_output=json_guidance
    )

    critique_messages = [Interface.BuildUserQuery(critique_prompt)]

    critique_model = Writer.Config.CRITIQUE_LLM if hasattr(Writer.Config, 'CRITIQUE_LLM') else Writer.Config.REVISION_MODEL

    critique_messages = Interface.SafeGenerateText(
        _Logger,
        critique_messages,
        critique_model,
        min_word_count_target=20
    )
    critique = Interface.GetLastMessageText(critique_messages)
    _Logger.Log(f"Critique received:\n---\n{critique}\n---", 4)

    # --- Step 2: Generate Revision ---
    _Logger.Log("Starting revision based on the received critique.", 5)

    json_instructions = (
        "Important: Your final output must be a single, valid JSON object, just like the original. "
        "Revise the *content* within the JSON structure based on the critique. "
        "Do not add any explanatory text, comments, or markdown outside of the JSON object itself."
    ) if is_json else (
        "Ensure your final output is only the revised text. Maintain the original's intent and narrative role, "
        "but improve it by addressing the points in the critique. Do not write a reflection on the changes."
    )

    revision_prompt = Writer.Prompts.REVISE_CREATIVE_CONTENT_BASED_ON_CRITIQUE_PROMPT.format(
        original_text=initial_content,
        critique=critique,
        task_description=task_description,
        narrative_context_summary=narrative_context_summary,
        initial_user_prompt=initial_user_prompt,
        json_instructions=json_instructions
    )

    revision_messages = [Interface.BuildUserQuery(revision_prompt)]

    revision_model = Writer.Config.CHAPTER_REVISION_WRITER_MODEL
    revision_format = "json" if is_json else None

    if is_json:
        final_messages, _ = Interface.SafeGenerateJSON(
            _Logger,
            revision_messages,
            revision_model
        )
        revised_content = Interface.GetLastMessageText(final_messages)
    else:
        min_words = max(10, int(len(initial_content.split()) * 0.75))
        final_messages = Interface.SafeGenerateText(
            _Logger,
            revision_messages,
            revision_model,
            _Format=revision_format,
            min_word_count_target=min_words
        )
        revised_content = Interface.GetLastMessageText(final_messages)

    _Logger.Log("Content revision complete.", 4)
    return revised_content

```

## File: `Writer/LLMEditor.py`

```python
#!/usr/bin/python3

import json
import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger

def GetFeedbackOnOutline(Interface: Interface, _Logger: Logger, _Outline: str) -> str:
    """
    Generates a critique of a given story outline. This function is intended to be
    the 'critique' step in a larger revision process.
    """
    # Setup Initial Context History
    History = [
        Interface.BuildSystemQuery(Writer.Prompts.CRITIC_OUTLINE_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.CRITIC_OUTLINE_PROMPT.format(_Outline=_Outline))
    ]

    _Logger.Log("Prompting LLM to critique outline...", 5)
    # This is a creative task, so we want a substantive response.
    History = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.REVISION_MODEL, min_word_count_target=50
    )
    _Logger.Log("Finished getting outline feedback.", 5)

    return Interface.GetLastMessageText(History)


def GetOutlineRating(Interface: Interface, _Logger: Logger, _Outline: str) -> bool:
    """
    Asks an LLM to evaluate if an outline is complete and meets quality criteria.
    Returns a simple boolean. This is a non-creative check.
    """
    History = [
        Interface.BuildSystemQuery(Writer.Prompts.OUTLINE_COMPLETE_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.OUTLINE_COMPLETE_PROMPT.format(_Outline=_Outline))
    ]

    _Logger.Log("Prompting LLM for outline completion rating (JSON)...", 5)
    
    # This call generates non-creative JSON. The SafeGenerateJSON function handles retries for format.
    _, ResponseJSON = Interface.SafeGenerateJSON(
        _Logger, History, Writer.Config.EVAL_MODEL, _RequiredAttribs=["IsComplete"]
    )
    
    IsComplete = ResponseJSON.get("IsComplete", False)
    _Logger.Log(f"Editor determined IsComplete: {IsComplete}", 5)
    
    # Ensure the returned value is a boolean
    if isinstance(IsComplete, bool):
        return IsComplete
    elif isinstance(IsComplete, str):
        return IsComplete.lower() == 'true'
    return False


def GetFeedbackOnChapter(Interface: Interface, _Logger: Logger, _Chapter: str, _Outline: str) -> str:
    """
    Generates a critique of a given chapter. This function is intended to be
    the 'critique' step in a larger revision process.
    """
    History = [
        Interface.BuildSystemQuery(Writer.Prompts.CRITIC_CHAPTER_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.CRITIC_CHAPTER_PROMPT.format(_Chapter=_Chapter, _Outline=_Outline))
    ]

    _Logger.Log("Prompting LLM to critique chapter...", 5)
    Messages = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.REVISION_MODEL, min_word_count_target=50
    )
    _Logger.Log("Finished getting chapter feedback.", 5)

    return Interface.GetLastMessageText(Messages)


def GetChapterRating(Interface: Interface, _Logger: Logger, _Chapter: str) -> bool:
    """
    Asks an LLM to evaluate if a chapter is complete and meets quality criteria.
    Returns a simple boolean. This is a non-creative check.
    """
    History = [
        Interface.BuildSystemQuery(Writer.Prompts.CHAPTER_COMPLETE_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.CHAPTER_COMPLETE_PROMPT.format(_Chapter=_Chapter))
    ]

    _Logger.Log("Prompting LLM for chapter completion rating (JSON)...", 5)

    # This call generates non-creative JSON.
    _, ResponseJSON = Interface.SafeGenerateJSON(
        _Logger, History, Writer.Config.EVAL_MODEL, _RequiredAttribs=["IsComplete"]
    )

    IsComplete = ResponseJSON.get("IsComplete", False)
    _Logger.Log(f"Editor determined IsComplete: {IsComplete}", 5)

    if isinstance(IsComplete, bool):
        return IsComplete
    elif isinstance(IsComplete, str):
        return IsComplete.lower() == 'true'
    return False

```

## File: `Writer/NarrativeContext.py`

```python
#!/usr/bin/python3

from typing import Optional, List, Dict, Any

class SceneContext:
    """
    Holds contextual information for a single scene.
    """
    def __init__(self, scene_number: int, initial_outline: str):
        self.scene_number: int = scene_number
        self.initial_outline: str = initial_outline # The outline specific to this scene
        self.generated_content: Optional[str] = None
        self.summary: Optional[str] = None # Summary of what happened in this scene
        self.key_points_for_next_scene: List[str] = [] # Key takeaways to carry forward

    def set_generated_content(self, content: str):
        self.generated_content = content

    def set_summary(self, summary: str):
        self.summary = summary

    def add_key_point(self, point: str):
        self.key_points_for_next_scene.append(point)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_number": self.scene_number,
            "initial_outline": self.initial_outline,
            "generated_content": self.generated_content,
            "summary": self.summary,
            "key_points_for_next_scene": self.key_points_for_next_scene,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneContext':
        scene = cls(data["scene_number"], data["initial_outline"])
        scene.generated_content = data.get("generated_content")
        scene.summary = data.get("summary")
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
            return self.scenes[-1].summary
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
    def __init__(self, initial_prompt: str, overall_theme: Optional[str] = None):
        self.initial_prompt: str = initial_prompt
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
        context = cls(data["initial_prompt"], data.get("overall_theme"))
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
            if prev_scene and prev_scene.summary:
                context_str += f"\nSummary of the previous scene (Scene {prev_scene.scene_number}):\n{prev_scene.summary}\n"
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
            _Chapter=chapter_to_edit_content
        )

        messages = [Interface.BuildUserQuery(prompt)]

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
            f"ensuring it flows perfectly with the preceding and succeeding chapters."
        )

        context_summary = narrative_context.get_full_story_summary_so_far()

        revised_edited_chapter = Writer.CritiqueRevision.critique_and_revise_creative_content(
            Interface,
            _Logger,
            initial_content=initial_edited_chapter,
            task_description=task_description,
            narrative_context_summary=context_summary,
            initial_user_prompt=narrative_context.initial_prompt,
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

    prompt = Writer.Prompts.GENERATE_STORY_ELEMENTS_PROMPT.format(_OutlinePrompt=_OutlinePrompt)

    _Logger.Log("Generating initial Story Elements...", 4)
    messages = [Interface.BuildUserQuery(prompt)]
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, min_word_count_target=150
    )
    initial_elements = Interface.GetLastMessageText(messages)
    _Logger.Log("Done generating initial Story Elements.", 4)

    _Logger.Log("Critiquing and revising Story Elements for quality...", 3)
    task_description = "Generate the core story elements (genre, theme, plot points, setting, characters) based on a user's prompt. The output should be a detailed, well-structured markdown document."
    context_summary = f"The user has provided the following high-level prompt for a new story:\n{_OutlinePrompt}"

    revised_elements = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_elements,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=_OutlinePrompt,
    )

    _Logger.Log("Finished revising Story Elements.", 4)
    return revised_elements


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
    messages = Interface.SafeGenerateText(_Logger, messages, Writer.Config.INFO_MODEL)
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
        StoryElements=story_elements, _OutlinePrompt=_OutlinePrompt
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
            _Outline=outline, _Feedback=feedback
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
    if num_chapters > 0 and num_chapters < Writer.Config.MINIMUM_CHAPTERS:
        _Logger.Log(f"Outline has {num_chapters} chapters, which is less than the minimum of {Writer.Config.MINIMUM_CHAPTERS}. Expanding...", 6)
        expansion_prompt = Writer.Prompts.EXPAND_OUTLINE_TO_MIN_CHAPTERS_PROMPT.format(
            _Outline=outline, _MinChapters=Writer.Config.MINIMUM_CHAPTERS
        )
        messages = [Interface.BuildUserQuery(expansion_prompt)]
        messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, min_word_count_target=int(len(outline.split()) * 1.1)
        )
        outline = Interface.GetLastMessageText(messages)
        _Logger.Log("Outline expanded to meet minimum chapter count.", 5)

    narrative_context.set_base_novel_outline(outline)

    # --- Step 6: Generate Expanded Per-Chapter Outline (if enabled) ---
    if Writer.Config.EXPAND_OUTLINE:
        _Logger.Log("Starting per-chapter outline expansion...", 3)
        # Recalculate chapter count after potential expansion
        final_num_chapters = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, _Logger, outline)

        if final_num_chapters > 0 and final_num_chapters < 50:
            expanded_outlines = []
            for i in range(1, final_num_chapters + 1):
                chapter_outline = GeneratePerChapterOutline(
                    Interface, _Logger, i, outline, narrative_context
                )
                expanded_outlines.append(chapter_outline)

            full_expanded_outline = "\n\n".join(expanded_outlines)
            narrative_context.set_expanded_novel_outline(full_expanded_outline)
            _Logger.Log("Finished expanding all chapter outlines.", 3)
        else:
            _Logger.Log(f"Could not determine valid chapter count ({final_num_chapters}). Skipping expansion.", 6)

    return narrative_context


def GeneratePerChapterOutline(
    Interface: Interface,
    _Logger: Logger,
    _ChapterNum: int,
    _FullOutline: str,
    narrative_context: NarrativeContext,
) -> str:
    """
    Generates a more detailed, scene-by-scene outline for a single chapter.
    This is a creative task and uses a critique/revision cycle.
    """
    _Logger.Log(f"Generating detailed outline for Chapter {_ChapterNum}", 5)

    prompt = Writer.Prompts.CHAPTER_OUTLINE_PROMPT.format(
        _Chapter=_ChapterNum, _Outline=_FullOutline
    )
    messages = [Interface.BuildUserQuery(prompt)]
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, min_word_count_target=50
    )
    initial_chapter_outline = Interface.GetLastMessageText(messages)

    _Logger.Log(f"Critiquing and revising outline for Chapter {_ChapterNum}...", 3)
    task_description = f"Generate a detailed, scene-by-scene outline for Chapter {_ChapterNum}, based on the main story outline. The detailed outline should break down the chapter's events, character beats, and setting for each scene."
    context_summary = narrative_context.get_full_story_summary_so_far(_ChapterNum)
    context_summary += f"\n\nMain Story Outline:\n{_FullOutline}"

    revised_chapter_outline = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_chapter_outline,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
    )

    _Logger.Log(f"Done generating detailed outline for Chapter {_ChapterNum}.", 5)
    return revised_chapter_outline

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


    def SaveStory(self, _StoryContent: str):
        """Saves the given story to disk."""
        story_path = os.path.join(self.LogDirPrefix, "Story.md")
        try:
            with open(story_path, "w", encoding='utf-8') as f:
                f.write(_StoryContent)
            self.Log(f"Wrote final story to disk at {story_path}", 5)
        except Exception as e:
            self.Log(f"Failed to write final story to disk. Error: {e}", 7)


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
# ======================================================================================
# Prompts for Outline and Chapter Structure
# ======================================================================================

GENERATE_STORY_ELEMENTS_PROMPT = """
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

(Repeat the above structure for additional supporting character)

</RESPONSE_TEMPLATE>

Of course, don't include the XML tags - those are just to indicate the example.
Also, the items in parenthesis are just to give you a better idea of what to write about, and should also be omitted from your response.
"""

CHAPTER_COUNT_PROMPT = """
<OUTLINE>
{_Summary}
</OUTLINE>

Please provide a JSON formatted response containing the total number of chapters in the above outline.

Respond with {{"TotalChapters": <total chapter count>}}
Please do not include any other text, just the JSON as your response will be parsed by a computer.
"""

INITIAL_OUTLINE_PROMPT = """
Please write a markdown formatted outline based on the following prompt:

<PROMPT>
{_OutlinePrompt}
</PROMPT>

<ELEMENTS>
{StoryElements}
</ELEMENTS>

As you write, remember to ask yourself the following questions:
    - What is the conflict?
    - Who are the characters (at least two characters)?
    - What do the characters mean to each other?
    - Where are we located?
    - What are the stakes (is it high, is it low, what is at stake here)?
    - What is the goal or solution to the conflict?

Don't answer these questions directly; instead, make your outline implicitly answer them. (Show, don't tell)

Please keep your outline clear as to what content is in what chapter.
Make sure to add lots of detail as you write.

Also, include information about the different characters and how they change over the course of the story.
We want to have rich and complex character development!"""

OUTLINE_REVISION_PROMPT = """
Please revise the following outline:
<OUTLINE>
{_Outline}
</OUTLINE>

Based on the following feedback:
<FEEDBACK>
{_Feedback}
</FEEDBACK>

Remember to expand upon your outline and add content to make it as best as it can be!

As you write, keep the following in mind:
    - What is the conflict?
    - Who are the characters (at least two characters)?
    - What do the characters mean to each other?
    - Where are we located?
    - What are the stakes (is it high, is it low, what is at stake here)?
    - What is the goal or solution to the conflict?

Please keep your outline clear as to what content is in what chapter.
Make sure to add lots of detail as you write.

Don't answer these questions directly; instead, make your writing implicitly answer them. (Show, don't tell)
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

Do NOT write the outline itself, just the extra context. Keep your responses short and in a bulleted list.
If no such context exists, respond with "No additional context found."
"""

EXPAND_OUTLINE_TO_MIN_CHAPTERS_PROMPT = """
You are a master story developer and editor. Your task is to revise a novel outline to meet a minimum chapter count.
The current outline is too short and needs to be expanded thoughtfully.

# CURRENT OUTLINE
---
{_Outline}
---

# TASK
Revise the outline so that it contains at least **{_MinChapters}** chapters.
Do NOT just split existing chapters. Instead, expand the story by:
- Developing subplots.
- Giving more space to character arcs.
- Adding new events or complications that are consistent with the story's theme and plot.
- Fleshing out the rising action, climax, or falling action with more detail and steps.

The goal is a richer, more detailed story that naturally fills the required number of chapters, not a stretched-out version of the original.
Your response should be the new, complete, chapter-by-chapter markdown outline.
"""

CHAPTER_OUTLINE_PROMPT = """
You are a master storyteller and outliner. Your task is to expand a single chapter from a high-level novel outline into a more detailed, scene-by-scene breakdown.

# FULL NOVEL OUTLINE
Here is the complete outline for the story, providing context for the chapter you are about to detail.
---
{_Outline}
---

# YOUR TASK
Now, focus *only* on **Chapter {_Chapter}** from the outline above.
Expand this single chapter into a detailed scene-by-scene outline.

For each scene, please provide:
- A clear heading (e.g., "Scene 1: The Ambush").
- A list of characters present.
- A description of the setting.
- A summary of the key events and actions that take place.
- Notes on character development or important dialogue beats.

Your output should be formatted in markdown and contain *only* the detailed outline for Chapter {_Chapter}. Do not re-state the full outline or add introductory text.
"""

# ======================================================================================
# Prompts for Chapter Generation Stages
# ======================================================================================

CHAPTER_GENERATION_INTRO = """You are a great fiction writer, working on a new novel. You are about to write a chapter based on an outline and the story so far. Pay close attention to the provided context to ensure continuity."""

CHAPTER_GENERATION_PROMPT = """
Please help me extract the part of this outline that is just for chapter {_ChapterNum}.

<OUTLINE>
{_Outline}
</OUTLINE>

Do not include anything else in your response except just the content for chapter {_ChapterNum}.
"""

# The following stage prompts are simplified by using a single context block.
CHAPTER_GENERATION_STAGE1 = """
# Context
Here is the context for the novel so far, including themes, motifs, and summaries of previous chapters. Use this to ensure your writing is coherent and flows logically from what has come before.
---
{narrative_context}
---

# Your Task
Write the PLOT for chapter {_ChapterNum} of {_TotalChapters}.
Base your writing on the following chapter outline. Your main goal is to establish the sequence of events.
It is imperative that your writing connects well with the previous chapter and flows into the next.

<CHAPTER_OUTLINE>
{ThisChapterOutline}
</CHAPTER_OUTLINE>

As you write, ensure you are implicitly addressing these questions about the plot:
- Pacing: Are you skipping days at a time? Don't summarize events; add scenes to detail them. Is the story rushing over certain plot points?
- Flow: Does the plot make logical sense? Does it follow a clear narrative structure?
- Genre: What is the genre? Does the plot support the genre?

{Feedback}"""

CHAPTER_GENERATION_STAGE2 = """
# Context
Here is the context for the novel so far. Use this to inform your writing.
---
{narrative_context}
---

# Your Task
Expand upon the provided chapter plot by adding CHARACTER DEVELOPMENT for chapter {_ChapterNum} of {_TotalChapters}.
Do not remove existing content; instead, enrich it with character thoughts, feelings, and motivations.

Here is what I have for the current chapter's plot:
<CHAPTER_PLOT>
{Stage1Chapter}
</CHAPTER_PLOT>

Expand on the work above, keeping these criteria in mind:
- Characters: Who are the characters in this chapter? What is the situation between them? Is there conflict or tension?
- Development: What are the goals of each character? Do they exhibit growth or change? Do their goals shift?
- Details: (Show, don't tell) Implicitly answer the questions above by weaving them into the narrative.

Remember, your goal is to enhance the character depth of the chapter.

{Feedback}"""

CHAPTER_GENERATION_STAGE3 = """
# Context
Here is the context for the novel so far. Use this to inform your writing.
---
{narrative_context}
---

# Your Task
Expand upon the provided chapter content by adding DIALOGUE for chapter {_ChapterNum} of {_TotalChapters}.
Do not remove existing content; instead, weave natural and purposeful conversations into the scenes.

Here's what I have so far for this chapter:
<CHAPTER_CONTENT>
{Stage2Chapter}
</CHAPTER_CONTENT>

As you add dialogue, keep the following in mind:
- Dialogue: Does the dialogue make sense for the situation and characters? Is its pacing appropriate for the scene (e.g., fast-paced during action, slow during a thoughtful moment)?
- Disruptions: If dialogue is disrupted, what is the cause? How does it affect the conversation?
- Purpose: Does the dialogue reveal character, advance the plot, or provide exposition?

Also, please remove any leftover headings or author notes from the text. Your output should be the clean, final chapter text.

{Feedback}"""

CHAPTER_GENERATION_STAGE4 = """
Please provide a final edit of the following chapter. Your goal is to polish the writing, ensuring it's seamless and ready for publication.
Do not summarize. Expand where needed to improve flow, but do not add major new plot points.

For your reference, here is the full story outline:
<OUTLINE>
{_Outline}
</OUTLINE>

And here is the chapter to tweak and improve:
<CHAPTER>
{Stage3Chapter}
</CHAPTER>

As you edit, focus on these criteria:
- Pacing and Flow: Smooth out transitions between scenes.
- Character Voice: Ensure character thoughts and dialogue are consistent.
- Description: Refine descriptions. Is the language too flowery or too plain?
- Consistency: Ensure the chapter aligns with the outline and the tone of the novel.

Remember to remove any author notes or non-chapter text.
"""

# ======================================================================================
# Prompts for Summarization and Coherence (NEW)
# ======================================================================================

SUMMARIZE_SCENE_PROMPT = """
Please analyze the following scene and provide a structured JSON response.

<SCENE_TEXT>
{scene_text}
</SCENE_TEXT>

Your response must be a single JSON object with two keys:
1. "summary": A concise paragraph summarizing the key events, character interactions, and setting of the scene.
2. "key_points_for_next_scene": A list of 2-4 bullet points identifying crucial pieces of information (e.g., unresolved conflicts, new character goals, important objects, lingering questions) that must be carried forward to ensure continuity in the next scene.

Example Response Format:
{{
  "summary": "In the dimly lit tavern, Kaelan confronts the mysterious informant, learning that the stolen artifact is not a mere trinket but a key to the city's ancient defenses. The informant slips away after a cryptic warning about a traitor in the city guard, leaving Kaelan with more questions than answers.",
  "key_points_for_next_scene": [
    "Kaelan now knows the artifact is a key.",
    "A traitor is suspected within the city guard.",
    "The informant's warning was cryptic and needs deciphering.",
    "Kaelan is left alone in the tavern, contemplating his next move."
  ]
}}

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

# ======================================================================================
# Prompts for Critique and Revision (NEW)
# ======================================================================================

CRITIQUE_CREATIVE_CONTENT_PROMPT = """
You are a literary editor providing feedback on a piece of writing for a novel.
Your goal is to provide specific, constructive criticism to help the author improve the piece, ensuring it aligns with the original creative vision.

# ORIGINAL USER PROMPT (The Source of Truth)
This is the core idea the author started with. All generated content should serve this vision.
---
{initial_user_prompt}
---

# CONTEXT OF THE STORY SO FAR
This is a summary of events that have been written so far.
---
{narrative_context_summary}
---

# TASK DESCRIPTION
The author was trying to accomplish the following with this piece of writing:
"{task_description}"

# TEXT TO CRITIQUE
---
{text_to_critique}
---

# YOUR INSTRUCTIONS
Please critique the "TEXT TO CRITIQUE" based on its adherence to the "ORIGINAL USER PROMPT", the task it was supposed to accomplish, and its coherence with the story's context.
Focus on:
- **Prompt Adherence:** Does the text honor the core ideas, characters, and constraints from the original user prompt?
- **Coherence:** Does it logically follow from the story context? Does it maintain character voice and plot continuity?
- **Task Fulfillment:** Did it successfully achieve the goal described in the "TASK DESCRIPTION"?
- **Quality:** Is the writing engaging? Is the pacing effective? Is there anything unclear or confusing?

Provide a few bullet points of direct, actionable feedback.
{is_json_output}
"""

REVISE_CREATIVE_CONTENT_BASED_ON_CRITIQUE_PROMPT = """
You are a master fiction writer tasked with revising a piece of text based on an editor's critique.

# ORIGINAL USER PROMPT (The Source of Truth)
Your revision MUST align with this core idea.
---
{initial_user_prompt}
---

# CONTEXT OF THE STORY SO FAR
This is the background for the story you are working on.
---
{narrative_context_summary}
---

# ORIGINAL TEXT
This was the first draft of the text.
---
{original_text}
---

# EDITOR'S CRITIQUE
Here is the feedback you must address in your revision.
---
{critique}
---

# YOUR TASK
Your goal is to rewrite the "ORIGINAL TEXT" to address the points raised in the "EDITOR'S CRITIQUE".
- You MUST stay true to the original text's purpose, as described here: "{task_description}".
- You MUST ensure your revision is strongly aligned with the "ORIGINAL USER PROMPT".
- You MUST incorporate the feedback from the critique.
- You MUST ensure the revised text is coherent with the story's context.

{json_instructions}
"""

# ======================================================================================
# Prompts for Legacy Revision and Checking
# ======================================================================================

CHAPTER_REVISION = """
Please revise the following chapter:

<CHAPTER_CONTENT>
{_Chapter}
</CHAPTER_CONTENT>

Based on the following feedback:
<FEEDBACK>
{_Feedback}
</FEEDBACK>

Do not reflect on the revisions; just write the improved chapter that addresses the feedback and prompt criteria.
Remember not to include any author notes.
"""

SUMMARY_CHECK_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
SUMMARY_CHECK_PROMPT = """
Please summarize the following chapter:

<CHAPTER>
{_Work}
</CHAPTER>

Do not include anything in your response except the summary."""
SUMMARY_OUTLINE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
SUMMARY_OUTLINE_PROMPT = """
Please summarize the following chapter outline:

<OUTLINE>
{_RefSummary}
</OUTLINE>

Do not include anything in your response except the summary."""
SUMMARY_COMPARE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
SUMMARY_COMPARE_PROMPT = """
Please compare the provided summary of a chapter and the associated outline, and indicate if the provided content roughly follows the outline.

Please write a JSON formatted response with no other content with the following keys.
Note that a computer is parsing this JSON so it must be correct.

<CHAPTER_SUMMARY>
{WorkSummary}
</CHAPTER_SUMMARY>

<OUTLINE>
{OutlineSummary}
</OUTLINE>

Please respond with the following JSON fields:

{{
"Suggestions": "str",
"DidFollowOutline": "true/false"
}}

Suggestions should include a string containing detailed markdown formatted feedback that will be used to prompt the writer on the next iteration of generation.
Specify general things that would help the writer remember what to do in the next iteration.
The writer is not aware of each iteration - so provide detailed information in the prompt that will help guide it.
Start your suggestions with 'Important things to keep in mind as you write: \\n'.

It's okay if the summary isn't a perfect match, but it should have roughly the same plot and pacing.

Again, remember to make your response JSON formatted with no extra words. It will be fed directly to a JSON parser.
"""
CRITIC_OUTLINE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
CRITIC_OUTLINE_PROMPT = """
Please critique the following outline - make sure to provide constructive criticism on how it can be improved and point out any problems with it.

<OUTLINE>
{_Outline}
</OUTLINE>

As you revise, consider the following criteria:
    - Pacing: Is the story rushing over certain plot points and excessively focusing on others?
    - Details: How are things described? Is it repetitive?
    - Flow: Does each chapter flow into the next? Does the plot make logical sense?
    - Genre: What is the genre? Do the scenes and tone support the genre?

Also, please check if the outline is written chapter-by-chapter, not in sections spanning multiple chapters or subsections.
It should be very clear which chapter is which, and the content in each chapter."""

OUTLINE_COMPLETE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
OUTLINE_COMPLETE_PROMPT = """
<OUTLINE>
{_Outline}
</OUTLINE>

Does this outline meet all of the following criteria?
    - Pacing: The story does not rush over important plot points or excessively focus on minor ones.
    - Flow: Chapters flow logically into each other with a clear and consistent narrative structure.
    - Genre: The tone and content of the outline clearly support a specific genre.

Give a JSON formatted response, containing the key \"IsComplete\" with a boolean value (true/false).
Please do not include any other text, just the JSON as your response will be parsed by a computer.
"""
JSON_PARSE_ERROR = "Please revise your JSON. It encountered the following error during parsing: {_Error}. Remember that your entire response is plugged directly into a JSON parser, so don't write **anything** except pure json."
CRITIC_CHAPTER_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
CRITIC_CHAPTER_PROMPT = """<CHAPTER>
{_Chapter}
</CHAPTER>

Please give feedback on the above chapter based on the following criteria:
    - Pacing & Flow: Is the pacing effective? Does the chapter connect well with an implied previous chapter?
    - Characterization: Are the characters believable? Is their dialogue and development effective?
    - Narrative Quality: Is the writing engaging? Is the plot advanced in a meaningful way?
"""
CHAPTER_COMPLETE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
CHAPTER_COMPLETE_PROMPT = """
<CHAPTER>
{_Chapter}
</CHAPTER>

Does this chapter meet the following criteria?
    - Pacing and Flow: The chapter is well-paced and flows logically.
    - Quality Writing: The chapter is engaging, detailed, and contributes effectively to the story.
    - Narrative Cohesion: The chapter feels like a complete and coherent part of a larger novel.

Give a JSON formatted response, containing the key \"IsComplete\", with a boolean value (true/false).
Please do not include any other text, just the JSON as your response will be parsed by a computer.
"""
CHAPTER_EDIT_PROMPT = """
You are a developmental editor performing a holistic edit on a chapter to ensure it fits perfectly within the novel.

# FULL STORY OUTLINE
For context, here is the master outline for the entire novel.
---
{_Outline}
---

# FULL TEXT OF OTHER CHAPTERS
Here is the text of the surrounding chapters. Use this to ensure seamless transitions, consistent character voice, and coherent plot progression.
---
{NovelText}
---

# CHAPTER TO EDIT
Now, please perform a detailed edit of the following chapter, Chapter {i}.
---
{_Chapter}
---

# YOUR TASK
Rewrite Chapter {i}. Improve its prose, pacing, dialogue, and character moments. Most importantly, ensure it aligns perfectly with the full story outline and connects seamlessly with the other chapters provided. Do not just summarize; perform a deep, line-by-line developmental edit. Output only the revised chapter text.
"""
CHAPTER_SCRUB_PROMPT = """
<CHAPTER>
{_Chapter}
</CHAPTER>

Given the above chapter, please clean it up so that it is ready to be published.
That is, please remove any leftover outlines, author notes, or editorial comments, leaving only the finished story text.

Do not comment on your task, as your output will be the final print version.
"""
STATS_PROMPT = """
Please write a JSON formatted response with no other content with the following keys.
Note that a computer is parsing this JSON so it must be correct.

Base your answers on the story written in previous messages.

{{
"Title": "a short title that's three to eight words",
"Summary": "a paragraph or two that summarizes the story from start to finish",
"Tags": "a string of tags separated by commas that describe the story",
"OverallRating": "your overall score for the story from 0-100"
}}

Again, remember to make your response JSON formatted with no extra words. It will be fed directly to a JSON parser.
"""

# ======================================================================================
# Prompts for Scene-by-Scene Generation
# ======================================================================================

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant."""
CHAPTER_TO_SCENES = """
# CONTEXT #
I am writing a story based on the high-level user prompt below. This is the ultimate source of truth for the story's direction.
<USER_PROMPT>
{_Prompt}
</USER_PROMPT>

Below is my overall novel outline, which was derived from the user prompt:
<OUTLINE>
{_Outline}
</OUTLINE>

# OBJECTIVE #
Create a scene-by-scene outline for the chapter detailed below.
This outline will be used to write the chapter, so be detailed. For each scene, describe what happens, its tone, the characters present, and the setting.
Crucially, ensure the scenes you design are directly inspired by and consistent with the original <USER_PROMPT>.

Here's the specific chapter outline that we need to split up into scenes:
<CHAPTER_OUTLINE>
{_ThisChapter}
</CHAPTER_OUTLINE>

# STYLE #
Provide a creative response that adds depth and plot to the story while still following the provided chapter outline and, most importantly, the original user prompt.
Format your response in markdown, with clear headings for each scene.

# RESPONSE #
Be detailed and well-formatted in your response, yet ensure you have a well-thought-out and creative output.
"""
SCENES_TO_JSON = """
# CONTEXT #
I need to convert the following scene-by-scene outline into a JSON formatted list of strings.
<SCENE_OUTLINE>
{_Scenes}
</SCENE_OUTLINE>

# OBJECTIVE #
Create a JSON list where each element in the list is a string containing the full markdown content for that scene.
Example:
[
    "## Scene 1: The Confrontation\\n- **Characters:** Kaelan, Informant\\n- **Setting:** The Rusty Flagon tavern\\n- **Events:** Kaelan meets the informant...",
    "## Scene 2: The Escape\\n- **Characters:** Kaelan\\n- **Setting:** The city streets\\n- **Events:** Kaelan is pursued by city guards..."
]

Do not include any other json fields; it must be a simple list of strings.

# STYLE #
Respond in pure, valid JSON.

# RESPONSE #
Do not lose any information from the original outline; just format it to fit into a JSON list of strings.
"""
SCENE_OUTLINE_TO_SCENE = """
# CONTEXT #
You are a creative writer. I need your help writing a full scene based on the scene outline below.
For context, here is a summary of the story and relevant events so far:
---
{narrative_context}
---

# OBJECTIVE #
Write a full, engaging scene based on the following scene outline.
Include dialogue, character actions, thoughts, and descriptions as appropriate to bring the scene to life.

<SCENE_OUTLINE>
{_SceneOutline}
</SCENE_OUTLINE>

# STYLE #
Your writing style should be creative and match the tone described in the scene outline. If no tone is specified, use your best judgment based on the events and character motivations. (Show, don't tell).

# RESPONSE #
Ensure your response is a well-thought-out and creative piece of writing that follows the provided scene outline and fits coherently into the larger story based on the context provided. Output only the scene's text.
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
        
        # SafeGenerateText ensures we get a non-empty response.
        # Scrubbing is non-creative, so no critique cycle is needed.
        messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.SCRUB_MODEL, min_word_count_target=1
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
        _RequiredAttribs=["Title", "Summary", "Tags"]
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

def summarize_scene_and_extract_key_points(
    Interface: Interface,
    _Logger: Logger,
    scene_text: str,
    narrative_context: NarrativeContext,
    chapter_num: int,
    scene_num: int
) -> dict:
    """
    Summarizes a scene's content and extracts key points for the next scene to ensure coherence.
    This is a creative/analytical task and will undergo critique and revision.

    Returns:
        A dictionary with "summary" and "key_points_for_next_scene".
    """
    _Logger.Log(f"Generating summary for Chapter {chapter_num}, Scene {scene_num}", 4)

    # Prepare context for the summarization task
    task_description = f"You are summarizing scene {scene_num} of chapter {chapter_num}. The goal is to create a concise summary of the scene's events and to identify key plot points, character changes, or unresolved tensions that must be carried into the next scene to maintain narrative continuity."

    context_summary = narrative_context.get_full_story_summary_so_far(chapter_num)
    if chapter_ctx := narrative_context.get_chapter(chapter_num):
        if scene_num > 1:
            if prev_scene := chapter_ctx.get_scene(scene_num - 1):
                if prev_scene.summary:
                    context_summary += f"\nImmediately preceding this scene (C{chapter_num} S{scene_num-1}):\n{prev_scene.summary}"

    prompt = Writer.Prompts.SUMMARIZE_SCENE_PROMPT.format(scene_text=scene_text)
    messages = [Interface.BuildUserQuery(prompt)]

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
        is_json=True
    )

    try:
        final_summary_data = json.loads(revised_summary_text)
        if "summary" not in final_summary_data or "key_points_for_next_scene" not in final_summary_data:
             _Logger.Log("Revised summary JSON is missing required keys. Falling back to initial summary.", 7)
             return initial_summary_json

        _Logger.Log(f"Successfully generated and revised summary for C{chapter_num} S{scene_num}.", 4)
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
    messages = [Interface.BuildUserQuery(prompt)]

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
        SysLogger.Log("No model was selected or discovered. Exiting.", 7)
        return
        
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

    narrative_context = NarrativeContext(initial_prompt=Prompt)
    narrative_context = Writer.OutlineGenerator.GenerateOutline(Interface, SysLogger, Prompt, narrative_context)
    SysLogger.Log("Starting Chapter Writing phase...", 2)
    total_chapters = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, SysLogger, narrative_context.base_novel_outline_markdown)
    if total_chapters > 0 and total_chapters < 50:
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
    Info = Writer.StoryInfo.GetStoryInfo(Interface, SysLogger, [Interface.BuildUserQuery(narrative_context.base_novel_outline_markdown)])
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
        file_name_base = Writer.Config.OPTIONAL_OUTPUT_NAME
    with open(f"{file_name_base}.md", "w", encoding="utf-8") as f:
        output_content = f"# {Title}\n\n{StoryBodyText}\n\n---\n\n{StatsString}\n\n---\n\n## Full Outline\n```\n{narrative_context.base_novel_outline_markdown}\n```"
        f.write(output_content)
        SysLogger.SaveStory(output_content)

    with open(f"{file_name_base}.json", "w", encoding="utf-8") as f:
        json.dump(narrative_context.to_dict(), f, indent=4)
    SysLogger.Log("Generation complete!", 5)

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

available_models = mistralai/mistral-medium-3-instruct,mistralai/mistral-nemotron,qwen/qwen3-235b-a22b,nvidia/llama-3.1-nemotron-ultra-253b-v1,nvidia/llama-3.3-nemotron-super-49b-v1,writer/palmyra-creative-122b
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
enable_final_edit_pass = false
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
langchain-openai

# Ollama client library for local model support
ollama

# Utility packages
python-dotenv
termcolor
requests
configparser

```

