# File: Evaluate.py
# Purpose: Script for evaluating and comparing generated stories/outlines using an LLM.

"""
Story Evaluation Script.

This script provides a command-line interface to evaluate and compare
AI-generated stories or their outlines. It uses an LLM to perform the
evaluation based on predefined criteria.

The script can:
- Compare two story outlines.
- Compare two individual chapters.
- Output a report summarizing the LLM's evaluation.

The evaluation criteria typically include plot coherence, chapter flow,
writing style, dialogue quality, trope integration, genre adherence, and
narrative structure.
"""
import datetime
import argparse
import time
import json
import os  # For path manipulation if needed, not strictly used in this version of Evaluate.py
from typing import Dict, Any, Tuple, List

# Assuming these modules are in the PYTHONPATH or Writer is a package.
import Writer.Config as Config  # Using aliased import
import Writer.Interface.Wrapper as Wrapper  # Using aliased import
import Writer.PrintUtils as PrintUtils  # Using aliased import

# --- Evaluation Prompts (Internal to this script for now, could be moved to Prompts.py) ---

EVALUATE_OUTLINES_PROMPT_TEMPLATE = """
You are an expert literary critic AI. Your task is to meticulously compare two story outlines based on the criteria provided below.

**Story Outline A:**
<OutlineA>
{_OutlineA}
</OutlineA>

**Story Outline B:**
<OutlineB>
{_OutlineB}
</OutlineB>

**Evaluation Criteria (For each, choose A, B, or Tie, and provide a brief explanation):**
1.  **Plot Cohesion & Creativity**:
    *   Does the outline present a coherent, logical, and engaging plot?
    *   How creative or original are the plot ideas?
    *   Are there any noticeable plot holes or inconsistencies?
2.  **Chapter Structure & Flow**:
    *   Do the individual chapter summaries suggest a clear purpose and progression?
    *   Do the chapters seem to flow logically from one to the next, building narrative momentum?
    *   Is there a good balance in what each chapter aims to achieve?
3.  **Pacing (as suggested by outline)**:
    *   Does the outline suggest effective pacing for the story's genre and themes?
    *   Are crucial plot points given adequate development, or do some sections feel potentially rushed/dragged?
4.  **Character Arc Potential**:
    *   Do the main characters' goals, motivations, and potential for development seem clear and compelling within the outline?
5.  **Originality & Engagement**:
    *   Overall, which outline promises a more original, engaging, and satisfying story?

**Response Format:**
Please provide your response strictly in JSON format with the following structure.
Your explanations should be concise but insightful.

{{
    "OverallThoughts": "Your general comparative assessment and main reasons for preferring one outline (or declaring a tie).",
    "PlotComparison": {{
        "Winner": "<A, B, or Tie>",
        "Explanation": "Specific reasoning for your Plot choice, citing elements from both outlines if possible."
    }},
    "ChapterStructureComparison": {{
        "Winner": "<A, B, or Tie>",
        "Explanation": "Reasoning for Chapter Structure & Flow."
    }},
    "PacingComparison": {{
        "Winner": "<A, B, or Tie>",
        "Explanation": "Reasoning for Pacing."
    }},
    "CharacterArcPotentialComparison": {{
        "Winner": "<A, B, or Tie>",
        "Explanation": "Reasoning for Character Arc Potential."
    }},
    "OriginalityEngagementComparison": {{
        "Winner": "<A, B, or Tie>",
        "Explanation": "Reasoning for Originality & Engagement."
    }},
    "OverallWinner": "<A, B, or Tie>"
}}

Ensure your entire response is a single, valid JSON object.
"""

EVALUATE_CHAPTERS_PROMPT_TEMPLATE = """
You are an expert literary editor AI. Your task is to compare two distinct chapters of fictional writing.
These chapters are assumed to be from similar (but not necessarily identical) stories or different renditions of the same story segment. Evaluate them independently on their own merits, then comparatively.

**Chapter A:**
<CHAPTER_A>
{_ChapterA}
</CHAPTER_A>

**Chapter B:**
<CHAPTER_B>
{_ChapterB}
</CHAPTER_B>

**Evaluation Criteria (For each, choose A, B, or Tie, and provide a brief explanation):**
1.  **Prose Quality & Style**:
    *   Clarity, vividness, imagery, word choice, sentence fluency.
    *   Effectiveness of the narrative voice and tone.
2.  **Pacing & Flow (within the chapter)**:
    *   Does the chapter manage pacing effectively for its content?
    *   Do scenes/paragraphs transition smoothly?
3.  **Dialogue Quality**:
    *   Is the dialogue natural, engaging, character-specific, and purposeful?
4.  **Character Portrayal (within this chapter)**:
    *   Are characters depicted consistently and believably?
    *   Are their actions, thoughts, and emotions well-conveyed?
5.  **Plot Advancement/Scene Purpose**:
    *   Does the chapter (or its scenes) effectively advance a plot or serve a clear narrative purpose?
    *   Is there sufficient conflict or tension, if appropriate?
6.  **Engagement & Impact**:
    *   Which chapter is more immersive and impactful for the reader?

**Response Format:**
Please provide your response strictly in JSON format with the following structure.

{{
    "OverallThoughts": "Your general comparative assessment and main reasons for preferring one chapter (or declaring a tie).",
    "ProseQualityComparison": {{
        "Winner": "<A, B, or Tie>",
        "Explanation": "Reasoning for Prose Quality & Style."
    }},
    "PacingFlowComparison": {{
        "Winner": "<A, B, or Tie>",
        "Explanation": "Reasoning for Pacing & Flow."
    }},
    "DialogueQualityComparison": {{
        "Winner": "<A, B, or Tie>",
        "Explanation": "Reasoning for Dialogue Quality."
    }},
    "CharacterPortrayalComparison": {{
        "Winner": "<A, B, or Tie>",
        "Explanation": "Reasoning for Character Portrayal."
    }},
    "PlotAdvancementComparison": {{
        "Winner": "<A, B, or Tie>",
        "Explanation": "Reasoning for Plot Advancement/Scene Purpose."
    }},
    "EngagementImpactComparison": {{
        "Winner": "<A, B, or Tie>",
        "Explanation": "Reasoning for Engagement & Impact."
    }},
    "OverallWinner": "<A, B, or Tie>"
}}

Ensure your entire response is a single, valid JSON object.
"""

# --- Helper Functions ---


def load_story_json(filepath: str, logger: PrintUtils.Logger) -> Dict[str, Any]:
    """Loads a story data JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.Log(f"Successfully loaded story data from: {filepath}", 1)
        return data
    except FileNotFoundError:
        logger.Log(f"Error: Story file not found at {filepath}", 7)
        raise
    except json.JSONDecodeError as e:
        logger.Log(f"Error: Could not decode JSON from {filepath}. Error: {e}", 7)
        raise
    except Exception as e:
        logger.Log(f"An unexpected error occurred while loading {filepath}: {e}", 7)
        raise


def evaluate_outlines(
    interface: Wrapper.Interface,
    logger: PrintUtils.Logger,
    outline_a_text: str,
    outline_b_text: str,
    evaluation_model_uri: str,
) -> Tuple[str, Dict[str, Any]]:
    """Uses an LLM to compare two story outlines."""
    logger.Log("Starting evaluation of two story outlines...", 3)

    if not outline_a_text.strip() or not outline_b_text.strip():
        logger.Log("One or both outlines are empty. Cannot perform evaluation.", 6)
        return "Error: Outline text missing.", {"Error": "Outline text missing."}

    prompt = EVALUATE_OUTLINES_PROMPT_TEMPLATE.format(
        _OutlineA=outline_a_text, _OutlineB=outline_b_text
    )

    messages: List[Dict[str, str]] = [
        interface.build_system_query(
            "You are an AI literary critic specializing in outline analysis."
        ),
        interface.build_user_query(prompt),
    ]

    try:
        _response_messages, eval_json = interface.safe_generate_json(
            logger,
            messages,
            evaluation_model_uri,
            required_attribs=[
                "OverallWinner",
                "PlotComparison",
            ],  # Check a few key fields
        )

        # Construct a human-readable report snippet from the JSON
        report_snippet = (
            f"  Overall Thoughts: {eval_json.get('OverallThoughts', 'N/A')}\n"
        )
        for key, value_dict in eval_json.items():
            if isinstance(value_dict, dict) and "Winner" in value_dict:
                report_snippet += f"  - {key.replace('Comparison','')} Winner: {value_dict.get('Winner', 'N/A')} (Reason: {value_dict.get('Explanation', 'N/A')[:100]}...)\n"
        report_snippet += f"  Overall Winner: {eval_json.get('OverallWinner', 'N/A')}\n"

        logger.Log("Outline evaluation complete.", 4)
        return report_snippet, eval_json

    except Exception as e:
        logger.Log(f"Error during outline evaluation: {e}", 7)
        return f"Error in outline evaluation: {e}", {"Error": str(e)}


def evaluate_chapters(
    interface: Wrapper.Interface,
    logger: PrintUtils.Logger,
    chapter_a_text: str,
    chapter_b_text: str,
    evaluation_model_uri: str,
) -> Tuple[str, Dict[str, Any]]:
    """Uses an LLM to compare two individual chapters."""
    logger.Log("Starting evaluation of two chapters...", 3)

    if not chapter_a_text.strip() or not chapter_b_text.strip():
        logger.Log("One or both chapters are empty. Cannot perform evaluation.", 6)
        return "Error: Chapter text missing.", {"Error": "Chapter text missing."}

    prompt = EVALUATE_CHAPTERS_PROMPT_TEMPLATE.format(
        _ChapterA=chapter_a_text, _ChapterB=chapter_b_text
    )

    messages: List[Dict[str, str]] = [
        interface.build_system_query(
            "You are an AI literary editor specializing in chapter analysis."
        ),
        interface.build_user_query(prompt),
    ]

    try:
        _response_messages, eval_json = interface.safe_generate_json(
            logger,
            messages,
            evaluation_model_uri,
            required_attribs=[
                "OverallWinner",
                "ProseQualityComparison",
            ],  # Check a few key fields
        )

        report_snippet = (
            f"  Overall Thoughts: {eval_json.get('OverallThoughts', 'N/A')}\n"
        )
        for key, value_dict in eval_json.items():
            if isinstance(value_dict, dict) and "Winner" in value_dict:
                report_snippet += f"  - {key.replace('Comparison','')} Winner: {value_dict.get('Winner', 'N/A')} (Reason: {value_dict.get('Explanation', 'N/A')[:100]}...)\n"
        report_snippet += f"  Overall Winner: {eval_json.get('OverallWinner', 'N/A')}\n"

        logger.Log("Chapter evaluation complete.", 4)
        return report_snippet, eval_json

    except Exception as e:
        logger.Log(f"Error during chapter evaluation: {e}", 7)
        return f"Error in chapter evaluation: {e}", {"Error": str(e)}


# --- Main Script Logic ---
def main():
    parser = argparse.ArgumentParser(
        description="Evaluate AI-generated stories or outlines."
    )
    parser.add_argument(
        "-Story1",
        required=True,
        help="Path to JSON file for story 1 (output from Write.py).",
    )
    parser.add_argument(
        "-Story2",
        required=True,
        help="Path to JSON file for story 2 (output from Write.py).",
    )
    parser.add_argument(
        "-Output",
        default="Evaluation_Report.md",
        type=str,
        help="File path for the evaluation report markdown.",
    )
    parser.add_argument(
        "-Model",
        default=Config.EVAL_MODEL,
        type=str,
        help="LLM model URI to use for evaluation tasks.",
    )
    # Add other relevant args from Write.py if they affect Config, like -Host for Ollama
    # For simplicity, this example assumes -Model covers it or defaults are fine.

    args = parser.parse_args()

    # --- Initialization ---
    # Update Config with relevant args (primarily the evaluation model)
    Config.EVAL_MODEL = args.Model
    # If other Config settings are needed by Interface (like OLLAMA_HOST), pass them.
    # Config.OLLAMA_HOST = args.Host # Example if -Host was an arg

    start_time_s = time.time()

    # Setup Logger (using a sub-directory for evaluation logs)
    logger = PrintUtils.Logger(log_dir_base="EvaluationLogs")
    logger.Log("Evaluation Script Started.", 0)
    logger.Log(f"Story 1 Path: {args.Story1}", 0)
    logger.Log(f"Story 2 Path: {args.Story2}", 0)
    logger.Log(f"Evaluation Model: {args.Model}", 0)
    logger.Log(f"Output Report To: {args.Output}", 0)

    # Setup LLM Interface
    try:
        interface = Wrapper.Interface(
            models_to_load=[args.Model]
        )  # Load only the eval model
        logger.Log("LLM Interface initialized for evaluation.", 1)
    except Exception as e:
        logger.Log(f"Failed to initialize LLM Interface: {e}. Aborting.", 7)
        return

    # --- Load Story Data ---
    try:
        story1_data = load_story_json(args.Story1, logger)
        story2_data = load_story_json(args.Story2, logger)
    except Exception:
        logger.Log("Failed to load one or both story JSON files. Aborting.", 7)
        return  # Abort if data loading fails

    # --- Prepare Report ---
    full_report_content = f"# AI Story Evaluation Report\n\n"
    full_report_content += (
        f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    full_report_content += f"**Story A (Source):** `{args.Story1}`\n"
    full_report_content += f"**Story B (Source):** `{args.Story2}`\n"
    full_report_content += f"**Evaluation Model:** `{args.Model}`\n\n---\n\n"

    all_eval_jsons: Dict[str, Any] = {}  # To store all JSON results for a summary

    # --- Evaluate Outlines ---
    outline1 = story1_data.get(
        "chapter_level_outline", story1_data.get("Outline", "")
    )  # Try new key, fallback to old
    outline2 = story2_data.get("chapter_level_outline", story2_data.get("Outline", ""))

    if outline1.strip() and outline2.strip():
        full_report_content += "## I. Outline Comparison\n\n"
        outline_report_snippet, outline_eval_json = evaluate_outlines(
            interface, logger, outline1, outline2, args.Model
        )
        full_report_content += outline_report_snippet + "\n\n---\n\n"
        all_eval_jsons["OutlineComparison"] = outline_eval_json
    else:
        logger.Log(
            "Skipping outline comparison due to missing outline data in one or both stories.",
            6,
        )
        full_report_content += "## I. Outline Comparison\n\n*Skipped: Outline data not found or empty in one or both story files.*\n\n---\n\n"

    # --- Evaluate Chapters ---
    # Use 'scrubbed_chapters' if available, fallback to 'unscrubbed_chapters_raw_assembly' or 'UnscrubbedChapters'
    chapters1_key_options = [
        "scrubbed_chapters",
        "translated_chapters",
        "globally_edited_chapters",
        "unscrubbed_chapters_raw_assembly",
        "UnscrubbedChapters",
    ]
    chapters2_key_options = [
        "scrubbed_chapters",
        "translated_chapters",
        "globally_edited_chapters",
        "unscrubbed_chapters_raw_assembly",
        "UnscrubbedChapters",
    ]

    chapters1 = next(
        (story1_data.get(key) for key in chapters1_key_options if story1_data.get(key)),
        [],
    )
    chapters2 = next(
        (story2_data.get(key) for key in chapters2_key_options if story2_data.get(key)),
        [],
    )

    if not isinstance(chapters1, list):
        chapters1 = []  # Ensure it's a list
    if not isinstance(chapters2, list):
        chapters2 = []

    if chapters1 and chapters2:
        full_report_content += "## II. Chapter-by-Chapter Comparison\n\n"
        num_chapters_to_compare = min(len(chapters1), len(chapters2))
        if num_chapters_to_compare == 0:
            full_report_content += (
                "*No chapters found in one or both stories for comparison.*\n"
            )
        else:
            logger.Log(f"Comparing up to {num_chapters_to_compare} chapters.", 1)

        all_eval_jsons["ChapterComparisons"] = []
        for i in range(num_chapters_to_compare):
            logger.Log(f"Comparing Chapter {i+1}...", 3)
            chapter1_text = chapters1[i]
            chapter2_text = chapters2[i]

            if not isinstance(chapter1_text, str) or not isinstance(chapter2_text, str):
                logger.Log(
                    f"Skipping Chapter {i+1} comparison due to non-string chapter content.",
                    6,
                )
                full_report_content += f"### Chapter {i+1} Comparison\n\n*Skipped: Invalid chapter data type.*\n\n"
                continue

            if chapter1_text.strip() and chapter2_text.strip():
                chapter_report_snippet, chapter_eval_json = evaluate_chapters(
                    interface, logger, chapter1_text, chapter2_text, args.Model
                )
                full_report_content += (
                    f"### Chapter {i+1} Comparison\n{chapter_report_snippet}\n"
                )
                all_eval_jsons["ChapterComparisons"].append(chapter_eval_json)
            else:
                logger.Log(
                    f"Skipping Chapter {i+1} comparison due to empty content in one or both.",
                    6,
                )
                full_report_content += f"### Chapter {i+1} Comparison\n\n*Skipped: Empty chapter content.*\n\n"
            full_report_content += "\n"
    else:
        logger.Log(
            "Skipping chapter comparison due to missing chapter data in one or both stories.",
            6,
        )
        full_report_content += "## II. Chapter-by-Chapter Comparison\n\n*Skipped: Chapter data not found or empty in one or both story files.*\n\n"

    full_report_content += "\n---\n\n"

    # --- Summary of Votes ---
    # (This is a simple text-based count, more sophisticated aggregation could use the JSONs)
    # TODO: Improve vote counting based on the structured JSON rather than string search
    total_a_votes = full_report_content.count(
        "Winner: <A>"
    ) + full_report_content.count(
        "Winner: A"
    )  # Handle slight variations
    total_b_votes = full_report_content.count(
        "Winner: <B>"
    ) + full_report_content.count("Winner: B")
    total_tie_votes = full_report_content.count(
        "Winner: <Tie>"
    ) + full_report_content.count("Winner: Tie")

    full_report_content += (
        "## III. Vote Summary (Simple Count)\n"  # Placeholder for better summary
    )
    full_report_content += f"- Total 'A' Wins: {total_a_votes}\n"
    full_report_content += f"- Total 'B' Wins: {total_b_votes}\n"
    full_report_content += f"- Total Ties: {total_tie_votes}\n"

    # --- Save Report ---
    try:
        with open(args.Output, "w", encoding="utf-8") as f_report:
            f_report.write(full_report_content)
        logger.Log(f"Evaluation report saved to: {args.Output}", 1)
        # Optionally save the aggregated JSON results too
        json_output_path = args.Output.replace(".md", "_details.json")
        with open(json_output_path, "w", encoding="utf-8") as f_json_details:
            json.dump(all_eval_jsons, f_json_details, indent=2)
        logger.Log(f"Detailed JSON evaluation results saved to: {json_output_path}", 1)

    except IOError as e:
        logger.Log(f"Error writing evaluation report to {args.Output}: {e}", 7)

    end_time_s = time.time()
    total_eval_time_s = round(end_time_s - start_time_s)
    logger.Log(f"Evaluation Script Finished. Total time: {total_eval_time_s}s.", 0)
    logger.close()


if __name__ == "__main__":
    main()
