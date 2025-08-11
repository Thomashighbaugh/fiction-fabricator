# File: Tools/PromptGenerator.py
# Purpose: Generates a refined prompt.txt for FictionFabricator using an LLM.
# This script is self-contained and should be run from the project's root directory.

"""
FictionFabricator Prompt Generator Utility.

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
import re
import dotenv

# --- Add project root to path for imports and load .env explicitly ---
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


# --- Prompts for this script (Refactored for Flexibility) ---

SYSTEM_PROMPT_STYLE_GUIDE = """
You are a creative assistant and expert prompt engineer. Your goal is to help a user transform their story idea into a rich, detailed, and effective prompt for an AI story generator.
"""

EXPAND_IDEA_PROMPT_TEMPLATE = """
You are a creative assistant helping to flesh out a story idea into a detailed prompt suitable for an AI story generator.
Your goal is to expand the user's basic idea into a richer concept that is faithful to their original vision.

User's Title: "{title}"
User's Basic Idea: "{idea}"

User's Title: "{title}"
User's Basic Idea: "{idea}"

Expand this into a more detailed story prompt. You must capture and enhance the following based on the user's idea. Your response MUST start directly with the '## Genre and Tone' heading, followed by the content for each section.

## Genre and Tone
Identify the likely genre and tone from the user's idea (e.g., Sci-Fi Adventure, Psychological Thriller, Fantasy Romance) and write the prompt to reflect it.

## Stylistic Guidelines (Dos and Don'ts)
Specify the desired writing style, narrative voice, and any elements to include or strictly avoid (e.g., "Focus on vivid descriptions," "Avoid excessive exposition," "Maintain a fast pace," "No deus ex machina endings").

## Intended Audience
Describe the target audience for this story (e.g., "Young Adult readers who enjoy dystopian themes," "Adults seeking a gritty detective noir," "Children aged 8-12 who like magical adventures").

## Core Characters
Provide a more detailed sketch of the main characters, including their key traits, motivations, initial conflicts, and potential arcs.

## Core Conflict
Elaborate on the central problem the characters will face, including its stakes and immediate implications.

## Antagonist(s) (if applicable)
Describe the primary antagonist(s), their motivations, powers/abilities, and their relationship to the core conflict and main characters. If no explicit antagonist, describe the opposing force.

## Theme/Moral
What underlying message, moral, or philosophical question should the story explore? (e.g., "The resilience of the human spirit," "The dangers of unchecked power," "The importance of family").

## Setting Snippet
A brief hint about the world or primary location that establishes its atmosphere.

## Potential Ending Direction
Hint at a possible conclusion that would be a satisfying and logical outcome of the premise, whether it's happy, tragic, or ambiguous.

Your response should be *only* the expanded story prompt itself.
Do not include any titles, headings, preambles, or other conversational text.
Make it engaging and provide enough substance for an AI to build a complex story upon.
"""

CRITIQUE_EXPANDED_PROMPT_TEMPLATE = """
You are an expert AI prompt engineer evaluating a story prompt intended for an advanced AI story generation system.

Here is the expanded story prompt you need to critique:
---
{expanded_prompt}
---

Critique this prompt based on its effectiveness for generating a compelling narrative that matches the user's apparent intent:
1.  **Clarity and Specificity:** Is the core story idea clear? Is the central conflict understandable? Are the characters distinct enough to start with?
2.  **Adherence to Intended Tone:** Does the prompt's tone match the user's idea? (e.g., if the idea is adventurous, is the prompt exciting? If the idea is mysterious, is the prompt intriguing?).
3.  **Potential for Complexity:** Does the prompt provide enough substance for the AI to generate a multi-chapter plot with interesting characters and meaningful conflict? Or is it a simple, one-note concept?
4.  **Actionability for AI:** Are there clear starting points for the AI? Are there any ambiguities that might confuse the AI or lead it astray from the user's original idea?

Provide your critique as a list of bullet points (strengths and weaknesses). Be constructive. The goal is to identify areas for improvement to make the prompt stronger.
"""

REFINE_PROMPT_BASED_ON_CRITIQUE_TEMPLATE = """
You are a master creative assistant. You have an expanded story prompt and a critique of that prompt.
Your task is to revise and improve the original expanded prompt based *only* on the provided critique.
The goal is to create a final, high-quality `prompt.txt` file that will be excellent input for an AI story generator.

Original Expanded Story Prompt:
---
{expanded_prompt}
---

Critique of the Expanded Story Prompt:
---
{critique}
---

Based on the critique, revise the "Original Expanded Story Prompt".
- **Clarify and Enhance the Intended Tone:** Double down on the elements that make the prompt reflect the user's original idea. Be more explicit about the desired tone and feeling.
- **Flesh out Details:** Address any weaknesses noted in the critique regarding character motivation, setting, plot specificity, stylistic guidelines, audience, antagonist details, or thematic depth. Ensure all requested sections are well-developed.

Your entire response MUST be *only* the revised story prompt text itself.
Do NOT include any titles, headings, introductory sentences, or explanations.
The output will be saved directly to a file, so it must contain *only* the story prompt.
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

    # Remove leading/trailing markdown code block fences if they exist
    if len(lines) >= 1 and re.fullmatch(r"^\s*```(?:markdown)?\s*$", lines[0], re.IGNORECASE):
        lines.pop(0)
    if len(lines) >= 1 and re.fullmatch(r"^\s*```\s*$", lines[-1], re.IGNORECASE):
        lines.pop(-1)

    # Remove any remaining leading/trailing blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop(-1)

    return "\n".join(lines).strip()


def generate_prompt(title: str, idea: str):

    print("--- FictionFabricator Prompt Generator ---")
    sys_logger = Logger(os.path.join(project_root, "Logs", "PromptGenLogs"))

    # --- Dynamic Model Selection ---
    selected_model_uri = get_llm_selection_menu_for_tool(sys_logger, tool_name="Prompt Generator")
    if not selected_model_uri:
        sys_logger.Log("No model was selected or discovered. Exiting.", 7)
        sys.exit(1)

    # --- Instantiate Interface and load selected model ---
    interface = Interface()
    interface.LoadModels([selected_model_uri])

    temp_str = input("Enter the temperature for the LLM (0.0-2.0, default: 0.7): ")
    try:
        temp = float(temp_str) if temp_str else 0.7
    except ValueError:
        print("Invalid temperature format. Using default value 0.7.")
        temp = 0.7

    # --- Generation Logic ---
    print("\nStep 1: Expanding user's idea...")
    expand_user_prompt = EXPAND_IDEA_PROMPT_TEMPLATE.format(title=title, idea=idea)
    # Increased max_tokens to prevent cutoff
    expand_model_with_params = f"{selected_model_uri}?temperature={temp}&max_tokens=2048"

    expand_messages = [
        interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
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
        interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
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
        # Increased max_tokens to prevent cutoff
        refine_model_with_params = f"{selected_model_uri}?temperature={temp}&max_tokens=2048"

        refine_messages = [
            interface.BuildSystemQuery(SYSTEM_PROMPT_STYLE_GUIDE),
            interface.BuildUserQuery(refine_user_prompt)
        ]
        refine_history = interface.SafeGenerateText(sys_logger, refine_messages, refine_model_with_params, min_word_count_target=100)
        refined_text_raw = interface.GetLastMessageText(refine_history)

        if "[ERROR:" in refined_text_raw:
            print(f"Warning: Refinement failed: {refined_text_raw}. Using the initially expanded prompt.")
            final_prompt_text_candidate = expanded_prompt
        else:
            final_prompt_text_candidate = _extract_core_prompt(refined_text_raw)

    final_prompt_text = final_prompt_text_candidate
    if not final_prompt_text.strip():
        print("Error: Final prompt is empty after all processing. Exiting.")
        # Fallback logic to prevent empty file
        if expanded_prompt.strip():
            print("Fallback to last valid prompt (the expanded version).")
            final_prompt_text = expanded_prompt
        else:
            sys.exit(1)

    print("\n--- Final Prompt Content for prompt.txt ---")
    print(final_prompt_text)
    print("-------------------------------------------")

    prompts_base_dir = os.path.join(project_root, "Generated_Content", "Prompts")
    os.makedirs(prompts_base_dir, exist_ok=True)

    sanitized_title = sanitize_filename(title)
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



