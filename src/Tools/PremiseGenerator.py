# File: Tools/PremiseGenerator.py
# Purpose: Generates 10 story premises from a rough theme or idea using an LLM.

import os
import sys
import json
import datetime
import re

# --- Add project root to path for imports ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# --- Standardized Imports from Main Project ---
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from Writer.LLMUtils import get_llm_selection_menu_for_tool

# --- Prompts for this script ---

SYSTEM_PROMPT_STYLE_GUIDE = """
You are a creative brainstorming assistant and an expert in crafting compelling story premises. Your goal is to generate ideas that are fresh, intriguing, and rich with narrative potential, tailored to the user's request and adhering to specific stylistic guidelines.
"""

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

def generate_premises(logger: Logger, interface: Interface, idea: str, temp: float = 0.8):
    """
    Generates 10 story premises from a rough theme or idea using an LLM.
    """
    generation_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    logger.Log("--- FictionFabricator Premise Generator ---", 2)

    # --- Dynamic Model Selection ---
    selected_model_uri = get_llm_selection_menu_for_tool(logger, tool_name="Premise Generator")
    if not selected_model_uri:
        logger.Log("No model was selected or discovered. Exiting.", 7)
        return

    interface.LoadModels([selected_model_uri])

    # Step 1: Generate Initial Premises
    logger.Log(f"\nStep 1: Brainstorming 10 initial premises for the idea: '{idea}'...", 2)
    generation_prompt = GENERATE_PREMISES_PROMPT_TEMPLATE.format(idea=idea)
    model_with_params = f"{selected_model_uri}?temperature={temp}&max_tokens=4000"

    messages = [
        interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
        interface.BuildUserQuery(generation_prompt)
    ]
    _, initial_response_json = interface.SafeGenerateJSON(
        logger, messages, model_with_params, _RequiredAttribs=["premises"]
    )

    if not initial_response_json or "premises" not in initial_response_json or not isinstance(initial_response_json["premises"], list) or len(initial_response_json["premises"]) != 10:
        logger.Log("Error: Failed to generate an initial valid list of 10 premises. Aborting.", 7)
        return

    final_premises = initial_response_json['premises']

    # Step 2: Critique the generated premises
    logger.Log("\nStep 2: Critiquing the initial list of premises...", 2)
    critique_prompt = CRITIQUE_PREMISES_PROMPT_TEMPLATE.format(
        idea=idea, premises_json=json.dumps(initial_response_json, indent=2)
    )
    critique_messages = [
        interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
        interface.BuildUserQuery(critique_prompt)
    ]
    critique_model_with_params = f"{selected_model_uri}?temperature=0.5&max_tokens=2000"
    critique_history = interface.SafeGenerateText(
        logger, critique_messages, critique_model_with_params, min_word_count_target=50
    )
    critique = interface.GetLastMessageText(critique_history).strip()

    # Step 3: Revise the premises based on critique
    if "[ERROR:" in critique or not critique:
        logger.Log("\nWarning: Critique step failed or returned empty. Skipping revision and using initial premises.", 6)
    else:
        logger.Log("\n--- Critique ---", 3)
        logger.Log(critique, 3)
        logger.Log("----------------", 3)
        logger.Log("\nStep 3: Revising premises based on critique...", 2)
        revision_prompt = REVISE_PREMISES_BASED_ON_CRITIQUE_TEMPLATE.format(
            idea=idea,
            original_premises_json=json.dumps(initial_response_json, indent=2),
            critique=critique
        )
        revision_messages = [
            interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
            interface.BuildUserQuery(revision_prompt)
        ]
        revision_model_with_params = f"{selected_model_uri}?temperature={temp}&max_tokens=4000"
        _, revised_response_json = interface.SafeGenerateJSON(
             logger, revision_messages, revision_model_with_params, _RequiredAttribs=["premises"]
        )

        if revised_response_json and "premises" in revised_response_json and isinstance(revised_response_json["premises"], list) and len(revised_response_json["premises"]) == 10:
            final_premises = revised_response_json['premises']
            logger.Log("Successfully revised premises.", 5)
        else:
            logger.Log("\nWarning: Revision step failed to produce a valid list of 10 premises. Using initial premises.", 6)

    if not final_premises:
        logger.Log("Error: The final list of premises is empty. Aborting.", 7)
        return

    logger.Log("\n--- Final Generated Premises ---", 5)
    formatted_output = ""
    for i, premise in enumerate(final_premises):
        premise_text = f"## Premise {i+1}\n\n{premise}\n\n---\n"
        print(premise_text)
        formatted_output += premise_text
    logger.Log("--------------------------", 5)

    premises_base_dir = os.path.join(project_root, "Logs", "Premises")
    os.makedirs(premises_base_dir, exist_ok=True)

    output_filename = f"Premise_List_{generation_timestamp}.txt"
    output_path = os.path.join(premises_base_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Premises for Idea: {idea}\n")
            f.write(f"# Generated on: {generation_timestamp}\n\n")
            f.write(formatted_output)
        logger.Log(f"\nSuccessfully saved generated premises to: {output_path}", 5)
    except OSError as e:
        logger.Log(f"Error creating directory or writing file to '{output_path}': {e}", 7)

    logger.Log("\n--- Premise Generation Complete ---", 5)
    logger.Log("You can now use any of these premises as input for Tools/PromptGenerator.py", 3)



