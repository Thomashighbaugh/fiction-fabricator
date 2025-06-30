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
