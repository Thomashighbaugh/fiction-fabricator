# File: Tools/PremiseGenerator.py
# Purpose: Generates 10 story premises from a rough theme or idea using an LLM.
# This script is self-contained and should be run from the project's root directory.

"""
FictionFabricator Premise Generator Utility.

This script takes a basic user idea and a desired story title to generate a more
detailed and refined `prompt.txt` file. This output file is structured to be an
effective input for the main Write.py script.

The process involves:
1. Dynamically selecting an LLM from available providers.
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
import datetime # <<< IMPORT ADDED HERE
import dotenv
import re # Import re for potential future use or robustness

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
# --- Refactored Import for Centralized LLM Utilities ---
from Writer.LLMUtils import get_llm_selection_menu_for_tool


# --- Prompts for this script (Refactored for Better Structure and Stylistic Guidance) ---

SYSTEM_PROMPT_STYLE_GUIDE = """
You are a creative brainstorming assistant and an expert in crafting compelling story premises. Your goal is to generate ideas that are fresh, intriguing, and rich with narrative potential, tailored to the user's request and adhering to specific stylistic guidelines.
"""

# --- REVISED Prompt Template ---
GENERATE_PREMISES_PROMPT_TEMPLATE = """
A user has provided a rough theme or idea and wants you to generate 10 distinct, compelling story premises based on it.

**User's Theme/Idea:** "{idea}"

Your task is to generate 10 unique story premises that are directly inspired by the user's idea. Each premise must be a self-contained concept, detailed enough to be used as input for another AI tool.

**CRITICAL GUIDELINES for EACH premise:**
-   **Coherence and Logic:** Each premise must be logically sound and avoid nonsensical or purely abstract concepts unless the user's theme explicitly calls for them. Ground the premise in a clear cause-and-effect or a relatable "what if" scenario.
-   **Narrative Potential:** Ensure each premise offers clear potential for a compelling story arc.
-   **Focus on Core Idea:** Deeply explore the user's provided theme or idea. The premise should be a creative extension of the core concept, not a departure into unrelated territory.
-   **Avoid Clichés (Unless Subverted):** While creativity is encouraged, avoid falling into the most predictable tropes for the given theme unless you are introducing a clever subversion.

**INCORPORATE THE FOLLOWING WRITING STYLES to enhance premise quality and depth:**
Use a combination of these styles to craft each premise. Aim for styles that promote detail, narrative cohesion, character depth, and thematic exploration, while avoiding incoherence or nonsense.
-   **Primary Styles to Blend:** `narrative`, `prose`, `inventive`, `suspenseful`, `exploratory`
-   **Secondary Styles for Flavor:** `ominous`, `rational`, `realistic`, `talletale`, `magic realism`

For each premise, you must include:
- A compelling core conflict that is clearly derived from the user's idea and enhanced by the chosen styles.
- A brief sketch of one or more main characters that are relevant to the conflict and the styles used.
- A hint about the setting and its atmosphere, which should complement the premise and the styles.
- The central stakes of the story – what is at risk?
- A unique twist or narrative hook that creatively elaborates on the user's idea and the chosen styles, making the premise original and intriguing.

**CRITICAL:** Your entire output must be a single, valid JSON object.
The JSON object should have one key, "premises", which is a list of exactly 10 strings. Each string is one of the detailed premises you have created.

Do not include any other text, titles, or explanations outside of this JSON object.
"""

CRITIQUE_PREMISES_PROMPT_TEMPLATE = """
You are a professional story editor with a strong aversion to clichés and a love for innovative narratives. You have been given a list of story premises based on a user's initial idea and specific stylistic guidelines. Your task is to provide sharp, constructive criticism to elevate the list.

**USER'S ORIGINAL IDEA:** "{idea}"
**STYLISTIC GUIDELINES PROVIDED:** Blend `narrative`, `prose`, `inventive`, `suspenseful`, `exploratory` styles, with secondary flavors of `ominous`, `rational`, `realistic`, `talletale`, `magic realism`.

**LIST OF PREMISES TO CRITIQUE:**
---
{premises_json}
---

Please critique the list based on the following rigorous criteria:
1.  **Conceptual Originality vs. Cliché:** Do these premises creatively explore the *core* of the user's idea, or do they immediately fall back on the most predictable, overused tropes for this genre? Identify specific premises that are too generic and suggest pushing for a more unique angle.
2.  **Thematic Cohesion:** Does every premise remain faithful to the spirit and concept of the user's original idea? Flag any premise that introduces elements that seem to clash with the core concept.
3.  **Narrative Potential:** Do the premises offer enough depth for a compelling story? Do they hint at interesting conflicts, characters, and stakes? Or are they shallow and one-dimensional?
4.  **Variety:** Does the list offer a good variety of takes on the user's idea, or are they all minor variations of the same basic plot?
5.  **Stylistic Adherence:** **(NEW)** Critically evaluate whether the premises successfully incorporate the requested blend of styles (`narrative`, `prose`, `inventive`, `suspenseful`, `exploratory`, with secondary flavors). Point out where the styles are missing, poorly implemented, or contribute to incoherence/nonsense.

Provide your critique as a few bullet points of direct, actionable feedback. Your goal is to guide the next AI to create a stronger, more original, and more thematically interesting set of premises. Your output should be a plain string of text.
"""

REVISE_PREMISES_BASED_ON_CRITIQUE_TEMPLATE = """
You are a master storyteller. Your task is to revise a list of 10 story premises based on an editor's sharp critique. The critique is focused on avoiding clichés, pushing the ideas towards greater originality and narrative depth, and ensuring adherence to the specified stylistic blend.

**USER'S ORIGINAL IDEA:** "{idea}"
**ORIGINAL STYLISTIC GUIDELINES:** Blend `narrative`, `prose`, `inventive`, `suspenseful`, `exploratory` styles, with secondary flavors of `ominous`, `rational`, `realistic`, `talletale`, `magic realism`.

**ORIGINAL LIST OF PREMISES:**
---
{original_premises_json}
---

**EDITOR'S CRITIQUE:**
---
{critique}
---

**YOUR TASK:**
Rewrite the list of 10 premises to directly address the points in the "EDITOR'S CRITIQUE".
-   **Eliminate Clichés & Boost Originality:** For any premise the critique flagged as generic, invent a more original concept that still honors the user's core idea. Subvert common tropes.
-   **Enforce Thematic Cohesion:** Refine or remove any elements that clash with the user's core concept, as pointed out by the critique. Ensure every premise is a unique but *consistent* exploration of the original idea.
-   **Deepen the Concepts:** For any premise noted as shallow, flesh it out with a stronger conflict, more interesting character dynamics, and clearer stakes.
-   **Adhere to Styles:** **(NEW)** Ensure the revised premises actively incorporate the requested blend of styles (`narrative`, `prose`, `inventive`, `suspenseful`, `exploratory`, with secondary flavors). Make the styles evident in the descriptions.

**CRUCIAL:** Your entire output MUST be a single, valid JSON object, identical in format to the original. It must have one key, "premises", which is a list of exactly 10 strings. Do not include any text or explanations outside of the JSON object.
"""

def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be suitable for a filename or directory name."""
    name = re.sub(
        r"[^\w\s-]", "", name
    ).strip()  # Remove non-alphanumeric (except underscore, hyphen, space)
    name = re.sub(r"[-\s]+", "_", name)  # Replace spaces and hyphens with underscores
    return name if name else "Untitled_Prompt"


def main():
    parser = argparse.ArgumentParser(description="FictionFabricator Self-Contained Premise Generator.")
    parser.add_argument("-i", "--idea", required=True, help="The user's high-level story theme or genre.")
    parser.add_argument("--temp", type=float, default=0.8, help="Temperature for LLM generation (default: 0.8).")
    args = parser.parse_args()

    generation_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # This line now has datetime available.

    print("--- FictionFabricator Premise Generator ---")
    sys_logger = Logger("PremiseGenLogs")

    # --- Dynamic Model Selection ---
    selected_model_uri = get_llm_selection_menu_for_tool(sys_logger, tool_name="Premise Generator")
    if not selected_model_uri:
        sys_logger.Log("No model was selected or discovered. Exiting.", 7)
        sys.exit(1)

    interface = Interface()
    interface.LoadModels([selected_model_uri])

    # Step 1: Generate Initial Premises
    print(f"\nStep 1: Brainstorming 10 initial premises for the idea: '{args.idea}'...")
    generation_prompt = GENERATE_PREMISES_PROMPT_TEMPLATE.format(idea=args.idea)
    # Increased max_tokens for potentially more detailed premises due to style blending
    model_with_params = f"{selected_model_uri}?temperature={args.temp}&max_tokens=4000"

    messages = [
        interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
        interface.BuildUserQuery(generation_prompt)
    ]
    _, initial_response_json = interface.SafeGenerateJSON(
        sys_logger, messages, model_with_params, _RequiredAttribs=["premises"]
    )

    if not initial_response_json or "premises" not in initial_response_json or not isinstance(initial_response_json["premises"], list) or len(initial_response_json["premises"]) != 10:
        print("Error: Failed to generate an initial valid list of 10 premises. Aborting.")
        sys_logger.Log("Initial premise generation failed to return 10 valid premises.", 7)
        sys.exit(1)

    final_premises = initial_response_json['premises']

    # Step 2: Critique the generated premises
    print("\nStep 2: Critiquing the initial list of premises...")
    critique_prompt = CRITIQUE_PREMISES_PROMPT_TEMPLATE.format(
        idea=args.idea, premises_json=json.dumps(initial_response_json, indent=2)
    )
    critique_messages = [
        interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
        interface.BuildUserQuery(critique_prompt)
    ]
    # Use a slightly lower temperature for critique for more focused feedback
    critique_model_with_params = f"{selected_model_uri}?temperature=0.5&max_tokens=2000"
    critique_history = interface.SafeGenerateText(
        sys_logger, critique_messages, critique_model_with_params, min_word_count_target=50
    )
    critique = interface.GetLastMessageText(critique_history).strip()

    # Step 3: Revise the premises based on critique
    if "[ERROR:" in critique or not critique:
        print("\nWarning: Critique step failed or returned empty. Skipping revision and using initial premises.")
        sys_logger.Log("Critique step failed or was empty, skipping revision.", 6)
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
            interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
            interface.BuildUserQuery(revision_prompt)
        ]
        # Use similar temperature for revision as generation, to maintain creativity under guidance
        revision_model_with_params = f"{selected_model_uri}?temperature={args.temp}&max_tokens=4000"
        revision_history = interface.SafeGenerateText(
            sys_logger, revision_messages, revision_model_with_params, min_word_count_target=100
        )
        # Use SafeGenerateJSON for the revision step as it expects a JSON output
        revised_response_json = interface.SafeGenerateJSON(
             sys_logger, revision_messages, revision_model_with_params, _RequiredAttribs=["premises"]
        )

        if revised_response_json and "premises" in revised_response_json and isinstance(revised_response_json["premises"], list) and len(revised_response_json["premises"]) == 10:
            final_premises = revised_response_json['premises']
            print("Successfully revised premises.")
            sys_logger.Log("Successfully revised premises based on critique.", 5)
        else:
            print("\nWarning: Revision step failed to produce a valid list of 10 premises. Using initial premises.")
            sys_logger.Log("Revision step failed to produce 10 valid premises, reverting to initial set.", 6)

    if not final_premises:
        print("Error: The final list of premises is empty. Aborting.")
        sys_logger.Log("Final premise list is empty after all steps. Aborting.", 7)
        sys.exit(1)

    print("\n--- Final Generated Premises ---")
    formatted_output = ""
    for i, premise in enumerate(final_premises):
        premise_text = f"## Premise {i+1}\n\n{premise}\n\n---\n"
        print(premise_text)
        formatted_output += premise_text
    print("--------------------------")

    premises_base_dir = os.path.join(project_root, "Premises")
    os.makedirs(premises_base_dir, exist_ok=True)

    output_filename = f"Premise_List_{generation_timestamp}.txt"
    output_path = os.path.join(premises_base_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Premises for Idea: {args.idea}\n")
            f.write(f"# Generated on: {generation_timestamp}\n\n")
            f.write(formatted_output)
        print(f"\nSuccessfully saved generated premises to: {output_path}")
        sys_logger.Log(f"Saved generated premises to {output_path}", 5)
    except OSError as e:
        print(f"Error creating directory or writing file to '{output_path}': {e}")
        sys_logger.Log(f"Error saving premises to file: {e}", 7)
        sys.exit(1)

    print("\n--- Premise Generation Complete ---")
    print("You can now use any of these premises as input for Tools/PromptGenerator.py")


if __name__ == "__main__":
    main()
