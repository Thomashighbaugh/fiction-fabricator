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
import os
from typing import Dict, Any, Tuple, List, Optional

import Writer.Config as Config
import Writer.Interface.Wrapper as Wrapper
import Writer.PrintUtils as PrintUtils
import Writer.Models as Models

# Heuristic: 1 word is approx 1.5 tokens in English, but can vary.
WORD_TO_TOKEN_RATIO = 1.5

# --- Evaluation Prompts (Could be moved to Prompts.py) ---

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
2.  **Chapter Structure & Flow**:
    *   Do the individual chapter summaries suggest a clear purpose and progression?
    *   Do the chapters seem to flow logically from one to the next?
3.  **Pacing (as suggested by outline)**:
    *   Does the outline suggest effective pacing for the story's genre and themes?
4.  **Character Arc Potential**:
    *   Do the main characters' goals, motivations, and potential for development seem clear and compelling?
5.  **Originality & Engagement**:
    *   Overall, which outline promises a more original, engaging, and satisfying story?

**Response Format:**
Please provide your response strictly in JSON format using the Pydantic model `OutlineComparison`.
Your explanations should be concise but insightful.
"""

EVALUATE_CHAPTERS_PROMPT_TEMPLATE = """
You are an expert literary editor AI. Your task is to compare two distinct chapters of fictional writing.
Evaluate them independently on their own merits, then comparatively.

**Chapter A:**
<CHAPTER_A>
{_ChapterA}
</CHAPTER_A>

**Chapter B:**
<CHAPTER_B>
{_ChapterB}
</CHAPTER_B>

**Evaluation Criteria (For each, choose A, B, or Tie, and provide a brief explanation):**
1.  **Prose Quality & Style**: Clarity, vividness, word choice, sentence fluency, narrative voice.
2.  **Pacing & Flow**: How well the chapter manages pacing and transitions.
3.  **Dialogue Quality**: Naturalness, purpose, and character-specificity of dialogue.
4.  **Character Portrayal**: Consistency and believability of characters.
5.  **Plot Advancement/Scene Purpose**: Effectiveness in advancing the plot or serving a narrative purpose.
6.  **Engagement & Impact**: Which chapter is more immersive and impactful.

**Response Format:**
Please provide your response strictly in JSON format using the Pydantic model `ChapterComparison`.
"""

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
            "You are an AI literary critic specializing in outline analysis. Respond strictly in JSON."
        ),
        interface.build_user_query(prompt),
    ]

    MAX_TOKENS_FOR_OUTLINE_COMPARISON = int(500 * WORD_TO_TOKEN_RATIO)

    try:
        _response_messages, parsed_json_data = interface.safe_generate_json(
            logger,
            messages,
            evaluation_model_uri,
            required_attribs=[],
            max_tokens=MAX_TOKENS_FOR_OUTLINE_COMPARISON,
            expected_response_model=Models.OutlineComparison,
        )

        eval_json = parsed_json_data

        report_snippet = f"  Overall Thoughts: {eval_json.get('OverallThoughts', 'N/A')}\n"
        for key, value in eval_json.items():
            if isinstance(value, dict) and "Winner" in value:
                report_snippet += f"  - {key} Winner: {value.get('Winner', 'N/A')} (Reason: {value.get('Explanation', 'N/A')[:100]}...)\n"
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
            "You are an AI literary editor specializing in chapter analysis. Respond strictly in JSON."
        ),
        interface.build_user_query(prompt),
    ]

    MAX_TOKENS_FOR_CHAPTER_COMPARISON = int(500 * WORD_TO_TOKEN_RATIO)

    try:
        _response_messages, parsed_json_data = interface.safe_generate_json(
            logger,
            messages,
            evaluation_model_uri,
            required_attribs=[],
            max_tokens=MAX_TOKENS_FOR_CHAPTER_COMPARISON,
            expected_response_model=Models.ChapterComparison,
        )

        eval_json = parsed_json_data

        report_snippet = f"  Overall Thoughts: {eval_json.get('OverallThoughts', 'N/A')}\n"
        for key, value in eval_json.items():
            if isinstance(value, dict) and "Winner" in value:
                report_snippet += f"  - {key} Winner: {value.get('Winner', 'N/A')} (Reason: {value.get('Explanation', 'N/A')[:100]}...)\n"
        report_snippet += f"  Overall Winner: {eval_json.get('OverallWinner', 'N/A')}\n"

        logger.Log("Chapter evaluation complete.", 4)
        return report_snippet, eval_json

    except Exception as e:
        logger.Log(f"Error during chapter evaluation: {e}", 7)
        return f"Error in chapter evaluation: {e}", {"Error": str(e)}


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
    args = parser.parse_args()

    Config.EVAL_MODEL = args.Model

    start_time_s = time.time()
    logger = PrintUtils.Logger(log_dir_base="EvaluationLogs")
    logger.Log("Evaluation Script Started.", 0)

    try:
        interface = Wrapper.Interface(logger=logger, models_to_load=[args.Model])
        logger.Log("LLM Interface initialized for evaluation.", 1)
        story1_data = load_story_json(args.Story1, logger)
        story2_data = load_story_json(args.Story2, logger)
    except Exception as e:
        logger.Log(f"Fatal error during initialization or file loading: {e}. Aborting.", 7)
        logger.close()
        return

    full_report_content = f"# AI Story Evaluation Report\n\n"
    full_report_content += f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    full_report_content += f"**Story A (Source):** `{args.Story1}`\n"
    full_report_content += f"**Story B (Source):** `{args.Story2}`\n"
    full_report_content += f"**Evaluation Model:** `{args.Model}`\n\n---\n\n"

    all_eval_jsons: Dict[str, Any] = {}

    outline1 = story1_data.get("chapter_level_plot_outline", "")
    outline2 = story2_data.get("chapter_level_plot_outline", "")

    if outline1.strip() and outline2.strip():
        full_report_content += "## I. Outline Comparison\n\n"
        outline_report_snippet, outline_eval_json = evaluate_outlines(
            interface, logger, outline1, outline2, args.Model
        )
        full_report_content += outline_report_snippet + "\n\n---\n\n"
        all_eval_jsons["OutlineComparison"] = outline_eval_json
    else:
        full_report_content += "## I. Outline Comparison\n\n*Skipped: Outline data not found.*\n\n---\n\n"

    chapters1_key_options = ["scrubbed_chapters", "translated_chapters", "globally_edited_chapters", "chapters_initial_assembly"]
    chapters1 = next((story1_data.get(key) for key in chapters1_key_options if story1_data.get(key)), [])
    chapters2 = next((story2_data.get(key) for key in chapters1_key_options if story2_data.get(key)), [])

    if chapters1 and chapters2:
        full_report_content += "## II. Chapter-by-Chapter Comparison\n\n"
        num_chapters_to_compare = min(len(chapters1), len(chapters2))
        all_eval_jsons["ChapterComparisons"] = []
        for i in range(num_chapters_to_compare):
            chapter_report_snippet, chapter_eval_json = evaluate_chapters(
                interface, logger, chapters1[i], chapters2[i], args.Model
            )
            full_report_content += f"### Chapter {i+1} Comparison\n{chapter_report_snippet}\n"
            all_eval_jsons["ChapterComparisons"].append(chapter_eval_json)
    else:
        full_report_content += "## II. Chapter-by-Chapter Comparison\n\n*Skipped: Chapter data not found.*\n\n"

    total_a_votes, total_b_votes, total_tie_votes = 0, 0, 0
    if "OutlineComparison" in all_eval_jsons:
        for key, value in all_eval_jsons["OutlineComparison"].items():
            if isinstance(value, dict) and "Winner" in value:
                if value["Winner"] == "A": total_a_votes += 1
                elif value["Winner"] == "B": total_b_votes += 1
                else: total_tie_votes += 1

    if "ChapterComparisons" in all_eval_jsons:
        for chapter_eval in all_eval_jsons["ChapterComparisons"]:
            for key, value in chapter_eval.items():
                if isinstance(value, dict) and "Winner" in value:
                    if value["Winner"] == "A": total_a_votes += 1
                    elif value["Winner"] == "B": total_b_votes += 1
                    else: total_tie_votes += 1
    
    full_report_content += f"\n---\n\n## III. Vote Summary\n- Total 'A' Wins: {total_a_votes}\n- Total 'B' Wins: {total_b_votes}\n- Total Ties: {total_tie_votes}\n"

    try:
        with open(args.Output, "w", encoding="utf-8") as f:
            f.write(full_report_content)
        logger.Log(f"Evaluation report saved to: {args.Output}", 1)
        json_output_path = args.Output.replace(".md", "_details.json")
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(all_eval_jsons, f, indent=2)
        logger.Log(f"Detailed JSON results saved to: {json_output_path}", 1)
    except IOError as e:
        logger.Log(f"Error writing evaluation report: {e}", 7)

    total_eval_time_s = round(time.time() - start_time_s)
    logger.Log(f"Evaluation Script Finished. Total time: {total_eval_time_s}s.", 0)
    logger.close()

if __name__ == "__main__":
    main()