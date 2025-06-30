# File: Tools/PremiseGenerator.py
# Purpose: Generates 10 story premises from a rough theme or idea using an LLM.
# This script is self-contained and should be run from the project's root directory.

"""
FictionFabricator Premise Generator Utility.

This script takes a high-level user theme or genre (e.g., "space opera romance")
and uses an LLM to brainstorm 10 distinct story premises.

Each generated premise is formatted to be a suitable input for the
`Tools/PromptGenerator.py` script, which can then expand it into a full prompt
for the main `Write.py` application.

The process involves:
1. Dynamically selecting an LLM from available providers.
2. Prompting the LLM to generate 10 creative and detailed story premises based on the user's theme.
3. Having the LLM critique its own list of premises for quality and variety.
4. Revising the list of premises based on the critique.
5. Displaying the final, revised premises to the user.
6. Saving the list to a text file in the `Premises/` directory.

Requirements:
- All packages from the main project's `requirements.txt`.
- A configured `.env` file with API keys for desired providers.
- An accessible Ollama server if using local models.

Usage:
python Tools/PremiseGenerator.py -i "space opera romance"
python Tools/PremiseGenerator.py --idea "cyberpunk detective story with a philosophical twist"
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

# --- Model Discovery Functions (copied from Write.py / PromptGenerator.py) ---
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

    print("\n--- Premise Generator LLM Selection ---")
    print("Please select the model for premise generation:")
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

GENERATE_PREMISES_PROMPT_TEMPLATE = """
You are a creative brainstorming assistant and an expert in storytelling.
A user has provided a rough theme or genre and wants you to generate 10 distinct, compelling story premises based on it.

User's Theme/Idea: "{idea}"

Your task is to generate 10 unique story premises. Each premise must be a complete, self-contained idea, detailed enough to be used as input for another AI tool that expands on story concepts.

For each premise, you should include:
- A core conflict.
- At least two main characters with brief, defining traits.
- A hint about the setting and its unique elements.
- The central stakes of the story.
- A unique twist or a "what if" scenario that makes the premise interesting.

**IMPORTANT:** Your entire output must be a single, valid JSON object.
The JSON object should have one key, "premises", which is a list of exactly 10 strings. Each string in the list is one of the detailed premises you have created.

Example JSON structure:
{{
  "premises": [
    "Premise 1 as a detailed string...",
    "Premise 2 as a detailed string...",
    "Premise 3 as a detailed string...",
    "Premise 4 as a detailed string...",
    "Premise 5 as a detailed string...",
    "Premise 6 as a detailed string...",
    "Premise 7 as a detailed string...",
    "Premise 8 as a detailed string...",
    "Premise 9 as a detailed string...",
    "Premise 10 as a detailed string..."
  ]
}}

Do not include any other text, titles, or explanations outside of this JSON object.
"""

CRITIQUE_PREMISES_PROMPT_TEMPLATE = """
You are a professional story editor and creative consultant. You have been given a list of 10 story premises based on a user's initial idea. Your task is to provide constructive criticism to improve the list.

USER'S ORIGINAL IDEA: "{idea}"

LIST OF PREMISES TO CRITIQUE:
---
{premises_json}
---

Please critique the list based on the following criteria:
1.  **Variety:** Are the 10 premises sufficiently different from one another, or are they too similar? Do they explore the user's idea from different angles?
2.  **Creativity & Originality:** Do the premises feel fresh and exciting, or do they rely on common clichés for the given idea?
3.  **Completeness:** Does each premise contain a clear conflict, interesting characters, and compelling stakes, as requested?
4.  **Adherence to Theme:** How well does the list of premises align with the user's original idea?

Provide your critique as a few bullet points of actionable feedback. Your goal is to guide the next AI to create a stronger, more varied, and more interesting set of premises. Your output should be a plain string of text.
"""

REVISE_PREMISES_BASED_ON_CRITIQUE_TEMPLATE = """
You are a master storyteller and creative writer. Your task is to revise a list of 10 story premises based on an editor's critique.

USER'S ORIGINAL IDEA: "{idea}"

ORIGINAL LIST OF PREMISES:
---
{original_premises_json}
---

EDITOR'S CRITIQUE:
---
{critique}
---

YOUR TASK:
Rewrite the list of 10 premises to directly address the points in the "EDITOR'S CRITIQUE".
- If the critique mentioned a lack of variety, create more distinct premises.
- If the critique mentioned clichés, invent more original concepts.
- If premises were incomplete, flesh them out with stronger conflicts, characters, and stakes.
- Ensure all revised premises still align with the "USER'S ORIGINAL IDEA".

**CRUCIAL:** Your entire output MUST be a single, valid JSON object, identical in format to the original. It must have one key, "premises", which is a list of exactly 10 strings. Do not include any text or explanations outside of the JSON object.
"""

def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be suitable for a filename or directory name."""
    name = re.sub(
        r"[^\w\s-]", "", name
    ).strip()  # Remove non-alphanumeric (except underscore, hyphen, space)
    name = re.sub(r"[-\s]+", "_", name)  # Replace spaces and hyphens with underscores
    return name if name else "Untitled_Premise"


def main():
    parser = argparse.ArgumentParser(description="FictionFabricator Self-Contained Premise Generator.")
    parser.add_argument("-i", "--idea", required=True, help="The user's high-level story theme or genre.")
    parser.add_argument("--temp", type=float, default=0.8, help="Temperature for LLM generation (default: 0.8).")
    args = parser.parse_args()

    print("--- FictionFabricator Premise Generator ---")
    sys_logger = Logger("PremiseGenLogs")

    # --- Dynamic Model Selection ---
    selected_model_uri = get_llm_selection_menu_for_tool(sys_logger)
    if not selected_model_uri:
        sys_logger.Log("No model was selected or discovered. Exiting.", 7)
        sys.exit(1)

    # --- Instantiate Interface and load selected model ---
    interface = Interface()
    interface.LoadModels([selected_model_uri])

    # --- Generation Logic ---

    # Step 1: Generate Initial Premises
    print(f"\nStep 1: Brainstorming 10 initial premises for the idea: '{args.idea}'...")
    generation_prompt = GENERATE_PREMISES_PROMPT_TEMPLATE.format(idea=args.idea)
    model_with_params = f"{selected_model_uri}?temperature={args.temp}&max_tokens=4000"

    messages = [
        interface.BuildSystemQuery("You are a creative brainstorming assistant specialized in generating story premises in JSON format."),
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
        interface.BuildSystemQuery("You are a professional story editor and creative consultant."),
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
            interface.BuildSystemQuery("You are a master storyteller revising a list of premises in JSON format based on a critique."),
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


    # --- Save to File ---
    premises_base_dir = os.path.join(project_root, "Premises")
    os.makedirs(premises_base_dir, exist_ok=True)

    sanitized_idea = sanitize_filename(args.idea)
    output_filename = f"{sanitized_idea}.txt"
    output_path = os.path.join(premises_base_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Premises for Idea: {args.idea}\n\n")
            f.write(formatted_output)
        print(f"\nSuccessfully saved generated premises to: {output_path}")
    except OSError as e:
        print(f"Error creating directory or writing file to '{output_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during file saving: {e}")
        sys.exit(1)

    print("\n--- Premise Generation Complete ---")
    print("You can now use any of these premises as input for Tools/PromptGenerator.py")


if __name__ == "__main__":
    main()
