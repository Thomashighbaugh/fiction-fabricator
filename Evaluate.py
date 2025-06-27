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
