#!/usr/bin/python3
import argparse
import time
import os
import sys
import json
import dotenv
import termcolor

# --- Add necessary paths ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Writer'))


import Writer.Config
import Writer.Interface.Wrapper
import Writer.PrintUtils
import Writer.Chapter.ChapterGenerator
import Writer.StoryInfo
import Writer.Prompts
from Writer.NarrativeContext import NarrativeContext

def write_web_novel_chapter(prompt_file: str, chapter_number: int, output: str = "", seed: int = Writer.Config.SEED, debug: bool = Writer.Config.DEBUG,
                             chapter_outline_model: str = Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL,
                             chapter_s1_model: str = Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
                             chapter_s2_model: str = Writer.Config.CHAPTER_STAGE2_WRITER_MODEL,
                             chapter_s3_model: str = Writer.Config.CHAPTER_STAGE3_WRITER_MODEL,
                             chapter_s4_model: str = Writer.Config.CHAPTER_STAGE4_WRITER_MODEL,
                             chapter_revision_model: str = Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
                             info_model: str = Writer.Config.INFO_MODEL,
                             checker_model: str = Writer.Config.CHECKER_MODEL,
                             no_chapter_revision: bool = Writer.Config.CHAPTER_NO_REVISIONS,
                             scene_generation_pipeline: bool = Writer.Config.SCENE_GENERATION_PIPELINE,
                             lore_book: str = None):
    """
    Writes a single chapter of a web novel based on a prompt file and chapter number.
    """
    StartTime = time.time()
    SysLogger = Writer.PrintUtils.Logger()
    SysLogger.Log(f"Welcome to the {Writer.Config.PROJECT_NAME} Web Novel Chapter Generator!", 2)

    # --- Configuration Setup ---
    Writer.Config.PROMPT = prompt_file
    Writer.Config.OPTIONAL_OUTPUT_NAME = output
    Writer.Config.SEED = seed
    Writer.Config.DEBUG = debug
    Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL = chapter_outline_model
    Writer.Config.CHAPTER_STAGE1_WRITER_MODEL = chapter_s1_model
    Writer.Config.CHAPTER_STAGE2_WRITER_MODEL = chapter_s2_model
    Writer.Config.CHAPTER_STAGE3_WRITER_MODEL = chapter_s3_model
    Writer.Config.CHAPTER_STAGE4_WRITER_MODEL = chapter_s4_model
    Writer.Config.CHAPTER_REVISION_WRITER_MODEL = chapter_revision_model
    Writer.Config.INFO_MODEL = info_model
    Writer.Config.CHECKER_MODEL = checker_model
    Writer.Config.CHAPTER_NO_REVISIONS = no_chapter_revision
    Writer.Config.SCENE_GENERATION_PIPELINE = scene_generation_pipeline

    # --- Model and Interface Initialization ---
    models_to_load = list(set([
        Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
        Writer.Config.CHAPTER_STAGE2_WRITER_MODEL, Writer.Config.CHAPTER_STAGE3_WRITER_MODEL,
        Writer.Config.CHAPTER_STAGE4_WRITER_MODEL, Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
        Writer.Config.INFO_MODEL, Writer.Config.CHECKER_MODEL
    ]))
    Interface = Writer.Interface.Wrapper.Interface(models_to_load)

    # --- Load Prompt and Initialize Narrative Context ---
    try:
        with open(prompt_file, "r", encoding='utf-8') as f:
            Prompt = f.read()
    except FileNotFoundError:
        SysLogger.Log(f"Error: Prompt file not found at {prompt_file}", 7)
        return

    lore_book_content = None
    if lore_book:
        try:
            with open(lore_book, "r", encoding='utf-8') as f:
                lore_book_content = f.read()
        except FileNotFoundError:
            SysLogger.Log(f"Error: Lore book file not found at {lore_book}", 7)
            return

    narrative_context = NarrativeContext(initial_prompt=Prompt, style_guide=Writer.Prompts.LITERARY_STYLE_GUIDE, lore_book_content=lore_book_content)
    
    # For web novels, we assume the outline is part of the prompt.
    # We will treat the entire prompt as the base outline.
    narrative_context.base_novel_outline_markdown = Prompt

    # --- Chapter Generation ---
    SysLogger.Log(f"Starting Generation for Chapter {chapter_number}...", 2)
    
    # The total number of chapters is unknown in a web novel context, so we pass 0
    Writer.Chapter.ChapterGenerator.GenerateChapter(Interface, SysLogger, chapter_number, 0, narrative_context)

    # --- Finalization ---
    if not narrative_context.chapters:
        SysLogger.Log(f"Chapter {chapter_number} generation failed. No content was produced.", 7)
        return

    chapter_content = narrative_context.chapters[-1].generated_content
    Title = f"Chapter {chapter_number}"

    SysLogger.Log(f"Chapter Title: {Title}", 5)
    ElapsedTime = time.time() - StartTime
    TotalWords = Writer.Statistics.GetWordCount(chapter_content)
    SysLogger.Log(f"Total chapter word count: {TotalWords}", 4)

    StatsString = f"""
## Work Statistics
- **Title**: {Title}
- **Generation Time**: {ElapsedTime:.2f}s
- **Average WPM**: {60 * (TotalWords / ElapsedTime) if ElapsedTime > 0 else 0:.2f}
- **Generator**: {Writer.Config.PROJECT_NAME} (Web Novel Mode)
"""

    # --- File Output ---
    os.makedirs(os.path.join("Generated_Content", "Web_Novel_Chapters"), exist_ok=True)
    
    # Use the prompt file name to create a directory for the story
    story_name = os.path.splitext(os.path.basename(prompt_file))[0]
    story_dir = os.path.join("Generated_Content", "Web_Novel_Chapters", story_name)
    os.makedirs(story_dir, exist_ok=True)

    file_name_base = f"{story_dir}/Chapter_{chapter_number}"
    if Writer.Config.OPTIONAL_OUTPUT_NAME:
        file_name_base = f"{story_dir}/{Writer.Config.OPTIONAL_OUTPUT_NAME}"

    md_file_path = f"{file_name_base}.md"
    json_file_path = f"{file_name_base}.json"

    with open(md_file_path, "w", encoding="utf-8") as f:
        output_content = f"# {Title}\n\n{chapter_content}\n\n---\n\n{StatsString}"
        f.write(output_content)

    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(narrative_context.chapters[-1].to_dict(), f, indent=4)

    SysLogger.Log("Chapter generation complete!", 5)
    final_message = f"""
--------------------------------------------------
Output Files Saved:
- Markdown Chapter: {os.path.abspath(md_file_path)}
- JSON Data File: {os.path.abspath(json_file_path)}
--------------------------------------------------"""
    print(termcolor.colored(final_message, "green"))


if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description=f"Run the {Writer.Config.PROJECT_NAME} web novel chapter generation.")
    Parser.add_argument("-Prompt", required=True, help="Path to the prompt file containing the story outline and context.")
    Parser.add_argument("-Chapter", required=True, type=int, help="The chapter number to generate.")
    Parser.add_argument("-Output", default="", type=str, help="Optional output file name (without extension).")
    Parser.add_argument("-Seed", default=Writer.Config.SEED, type=int)
    Parser.add_argument("-Debug", action="store_true", default=Writer.Config.DEBUG)
    Parser.add_argument("-ChapterOutlineModel", default=Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS1Model", default=Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS2Model", default=Writer.Config.CHAPTER_STAGE2_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS3Model", default=Writer.Config.CHAPTER_STAGE3_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS4Model", default=Writer.Config.CHAPTER_STAGE4_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterRevisionModel", default=Writer.Config.CHAPTER_REVISION_WRITER_MODEL, type=str)
    Parser.add_argument("-InfoModel", default=Writer.Config.INFO_MODEL, type=str)
    Parser.add_argument("-CheckerModel", default=Writer.Config.CHECKER_MODEL, type=str)
    Parser.add_argument("-NoChapterRevision", action="store_true", default=Writer.Config.CHAPTER_NO_REVISIONS)
    Parser.add_argument("-NoSceneGenerationPipeline", action="store_false", dest="SceneGenerationPipeline", default=Writer.Config.SCENE_GENERATION_PIPELINE)
    Parser.add_argument("-LoreBook", default=None, type=str, help="Path to the lore book file.")
    Args = Parser.parse_args()

    write_web_novel_chapter(
        prompt_file=Args.Prompt,
        chapter_number=Args.Chapter,
        output=Args.Output,
        seed=Args.Seed,
        debug=Args.Debug,
        chapter_outline_model=Args.ChapterOutlineModel,
        chapter_s1_model=Args.ChapterS1Model,
        chapter_s2_model=Args.ChapterS2Model,
        chapter_s3_model=Args.ChapterS3Model,
        chapter_s4_model=Args.ChapterS4Model,
        chapter_revision_model=Args.ChapterRevisionModel,
        info_model=Args.InfoModel,
        checker_model=Args.CheckerModel,
        no_chapter_revision=Args.NoChapterRevision,
        scene_generation_pipeline=Args.SceneGenerationPipeline,
        lore_book=Args.LoreBook
    )
