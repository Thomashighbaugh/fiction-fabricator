#!/usr/bin/python3

import re
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
            _ChapterNum, _TotalChapters,
            Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
            narrative_context
        )

        # STAGE 2: Character Development
        char_dev_text = execute_generation_stage(
            Interface, _Logger, "Character Development",
            Writer.Prompts.CHAPTER_GENERATION_STAGE2,
            {"ThisChapterOutline": chapter_specific_outline, "Stage1Chapter": plot_text, "Feedback": ""},
            _ChapterNum, _TotalChapters,
            Writer.Config.CHAPTER_STAGE2_WRITER_MODEL,
            narrative_context
        )

        # STAGE 3: Dialogue
        dialogue_text = execute_generation_stage(
            Interface, _Logger, "Dialogue Addition",
            Writer.Prompts.CHAPTER_GENERATION_STAGE3,
            {"ThisChapterOutline": chapter_specific_outline, "Stage2Chapter": char_dev_text, "Feedback": ""},
            _ChapterNum, _TotalChapters,
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
            revision_messages = [
                Interface.BuildSystemQuery(Writer.Prompts.LITERARY_STYLE_GUIDE),
                Interface.BuildUserQuery(revision_prompt)
            ]

            # Use robust word count and a high floor for revisions
            word_count = len(re.findall(r'\b\w+\b', current_chapter_text))
            min_word_count_target = max(150, int(word_count * 0.8))

            revision_messages = Interface.SafeGenerateText(
                _Logger, revision_messages, Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
                min_word_count_target=min_word_count_target
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
    
    narrative_context_str = narrative_context.get_context_for_chapter_generation(chapter_num)

    full_format_args = {
        "narrative_context": narrative_context_str,
        "_ChapterNum": chapter_num,
        "_TotalChapters": total_chapters,
        **format_args
    }
    prompt = prompt_template.format(**full_format_args)
    messages = [
        Interface.BuildSystemQuery(Writer.Prompts.LITERARY_STYLE_GUIDE),
        Interface.BuildUserQuery(prompt)
    ]

    # Set minimum word count with a high floor to prevent cascading failures
    min_words = 200  # Default for Stage 1 (Plot)
    if "Stage2Chapter" in format_args: # Stage 3 (Dialogue)
        word_count = len(re.findall(r'\b\w+\b', format_args["Stage2Chapter"]))
        min_words = max(250, int(word_count * 0.95))
    elif "Stage1Chapter" in format_args: # Stage 2 (Char Dev)
        word_count = len(re.findall(r'\b\w+\b', format_args["Stage1Chapter"]))
        min_words = max(250, int(word_count * 0.95))

    messages = Interface.SafeGenerateText(
        _Logger, messages, model, min_word_count_target=min_words
    )
    initial_content = Interface.GetLastMessageText(messages)

    # --- Critique and Revise ---
    _Logger.Log(f"Critiquing and revising content for {stage_name}...", 3)

    task_description = f"You are writing a novel. Your current task is '{stage_name}' for Chapter {chapter_num}. You need to generate content that fulfills this stage's specific goal (e.g., plot, character development, dialogue) while remaining coherent with the overall story and adhering to a dark, literary style."

    revised_content = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_content,
        task_description=task_description,
        narrative_context_summary=narrative_context_str,
        initial_user_prompt=narrative_context.initial_prompt,
        style_guide=narrative_context.style_guide,
    )

    _Logger.Log(f"Finished stage: {stage_name}", 5)
    return revised_content
