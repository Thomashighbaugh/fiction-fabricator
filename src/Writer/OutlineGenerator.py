#!/usr/bin/python3

import re
import Writer.Config
import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Prompts
import Writer.CritiqueRevision
from Writer.Outline.StoryElements import GenerateStoryElements
import Writer.Chapter.ChapterDetector
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext
from Writer.PrintUtils import Logger

# ---------------------------------------------------------------------------
# Short Story Outline Generation
# ---------------------------------------------------------------------------

def GenerateShortStoryOutline(
    Interface: Interface,
    _Logger: Logger,
    _OutlinePrompt: str,
    narrative_context: NarrativeContext,
    selected_model: str,
) -> NarrativeContext:
    """Generates a short story outline (scene-by-scene) and stores it in the narrative context.

    Flow:
    1. Extract any important non-plot base context from the user prompt (style / meta instructions).
    2. Generate story elements (shared with novel flow) if not already present.
    3. Produce a scene-by-scene short story outline using SHORT_STORY_OUTLINE_PROMPT.

    Returns the updated NarrativeContext.
    """
    _Logger.Log("Starting short story outline generation...", 3)
    _Logger.Log(f"[Model Trace] Using model '{selected_model}' for short story outline generation.", 4)

    # Step 1: Extract base prompt important info (similar to novel flow)
    base_context_prompt = Writer.Prompts.GET_IMPORTANT_BASE_PROMPT_INFO.format(
        _Prompt=_OutlinePrompt
    )
    messages = [Interface.BuildUserQuery(base_context_prompt)]
    _Logger.Log(f"[Model Trace] Base context extraction model (short story): {selected_model}", 5)
    messages = Interface.SafeGenerateText(_Logger, messages, selected_model, min_word_count_target=40)
    base_context = Interface.GetLastMessageText(messages)
    narrative_context.set_base_prompt_important_info(base_context)

    # Step 2: Story Elements (generate if missing)
    if not narrative_context.story_elements_markdown:
        _Logger.Log("Generating story elements for short story...", 4)
        story_elements = GenerateStoryElements(Interface, _Logger, _OutlinePrompt, selected_model)
        narrative_context.set_story_elements(story_elements)
    else:
        story_elements = narrative_context.story_elements_markdown
        _Logger.Log("Re-using existing story elements in context.", 5)

    # Step 3: Generate Short Story Outline
    target_word_count = narrative_context.word_count if narrative_context.word_count > 0 else 2500
    short_story_outline_prompt = Writer.Prompts.SHORT_STORY_OUTLINE_PROMPT.format(
        style_guide=narrative_context.style_guide,
        _OutlinePrompt=_OutlinePrompt,
        StoryElements=story_elements,
        word_count=target_word_count,
    )
    outline_messages = [
        Interface.BuildSystemQuery(narrative_context.style_guide),
        Interface.BuildUserQuery(short_story_outline_prompt),
    ]
    _Logger.Log(f"[Model Trace] Short story outline model: {selected_model}", 5)
    outline_messages = Interface.SafeGenerateText(
        _Logger, outline_messages, selected_model, min_word_count_target=300
    )
    outline_text = Interface.GetLastMessageText(outline_messages)

    # --- Step 3.5: Verify Outline Completeness ---
    _Logger.Log("Verifying short story outline completeness...", 3)
    outline_text = _verify_and_complete_outline(Interface, _Logger, outline_text, selected_model, "short story")

    # Store result
    narrative_context.set_base_novel_outline(outline_text)
    _Logger.Log("Short story outline generation complete.", 3)

    return narrative_context


def GenerateOutline(
    Interface: Interface,
    _Logger: Logger,
    _OutlinePrompt: str,
    narrative_context: NarrativeContext,
    selected_model: str,
) -> NarrativeContext:
    """
    Generates the complete story outline, including story elements and chapter breakdowns,
    and populates the provided NarrativeContext object.
    """
    _Logger.Log(f"[Model Trace] Using model '{selected_model}' for outline generation.", 4)
    if narrative_context.story_type == "short_story":
        return GenerateShortStoryOutline(Interface, _Logger, _OutlinePrompt, narrative_context, selected_model)

    # --- Step 1: Extract Important Base Context ---
    _Logger.Log("Extracting important base context from prompt...", 4)
    base_context_prompt = Writer.Prompts.GET_IMPORTANT_BASE_PROMPT_INFO.format(
        _Prompt=_OutlinePrompt
    )
    messages = [Interface.BuildUserQuery(base_context_prompt)]
    _Logger.Log(f"[Model Trace] Base context extraction model: {selected_model}", 5)
    messages = Interface.SafeGenerateText(_Logger, messages, selected_model, min_word_count_target=50)
    base_context = Interface.GetLastMessageText(messages)
    narrative_context.set_base_prompt_important_info(base_context)
    _Logger.Log("Done extracting important base context.", 4)

    # --- Step 2: Generate Story Elements ---
    _Logger.Log(f"[Model Trace] Story elements generation model: {selected_model}", 5)
    story_elements = GenerateStoryElements(
        Interface, _Logger, _OutlinePrompt, selected_model
    )
    narrative_context.set_story_elements(story_elements)

    # --- Step 3: Generate Initial Rough Outline ---
    _Logger.Log("Generating initial rough outline...", 4)
    initial_outline_prompt = Writer.Prompts.INITIAL_OUTLINE_PROMPT.format(
        StoryElements=story_elements,
        _OutlinePrompt=_OutlinePrompt,
        style_guide=narrative_context.style_guide,
    )
    messages = [Interface.BuildUserQuery(initial_outline_prompt)]
    _Logger.Log(f"[Model Trace] Initial rough outline model: {selected_model}", 5)
    messages = Interface.SafeGenerateText(
        _Logger, messages, selected_model, min_word_count_target=250
    )
    outline = Interface.GetLastMessageText(messages)
    _Logger.Log("Done generating initial rough outline.", 4)

    # --- Step 3.5: Verify Outline Completeness ---
    _Logger.Log("Verifying novel outline completeness...", 3)
    outline = _verify_and_complete_outline(Interface, _Logger, outline, selected_model, "novel")

    # --- Step 5: Single Critique/Revision for the Rough Outline ---
    _Logger.Log("Running single critique/revision for the rough outline...", 3)
    outline_critique_prompt = Writer.Prompts.OUTLINE_STRUCTURE_CRITIQUE_PROMPT.format(outline_text=outline)
    outline_revision_prompt = Writer.Prompts.REVISE_OUTLINE_STRUCTURE_PROMPT
    _Logger.Log(f"[Model Trace] Outline critique/revision model: {selected_model}", 5)
    outline = Writer.CritiqueRevision.run_outline_structure_revision(
        Interface,
        _Logger,
        outline,
        outline_critique_prompt,
        outline_revision_prompt,
        selected_model
    )
    _Logger.Log("Done revising outline.", 4)

    # --- Step 6: Enforce Chapter Count ---
    if narrative_context.chapter_count > 0:
        num_chapters = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, _Logger, outline, selected_model)
        if 0 < num_chapters < narrative_context.chapter_count:
            missing = narrative_context.chapter_count - num_chapters
            _Logger.Log(f"Outline has {num_chapters} chapters, desired {narrative_context.chapter_count}. Appending {missing} missing chapters instead of regenerating entire outline...", 6)

            # Heuristic: provide last 2 chapters (or all if fewer) for continuity context
            # Support variants like 'Chapter', 'Ch.' or 'Ch' (case-insensitive)
            chapter_blocks = re.split(r'(^#+\s*(?:Chapter|Ch\.?)+\s+\d+.*?$)', outline, flags=re.MULTILINE | re.IGNORECASE)
            # Reconstruct blocks into pairs: header + content
            reconstructed = []
            for i in range(1, len(chapter_blocks), 2):
                header = chapter_blocks[i].strip()
                content = chapter_blocks[i+1] if i+1 < len(chapter_blocks) else ''
                reconstructed.append(f"{header}\n{content}".strip())
            last_context_chapters = reconstructed[-2:] if len(reconstructed) >= 2 else reconstructed
            last_chapters_text = "\n\n".join(last_context_chapters)

            next_start = num_chapters + 1
            next_end = narrative_context.chapter_count
            append_prompt = Writer.Prompts.APPEND_OUTLINE_MISSING_CHAPTERS_PROMPT.format(
                _CurrentChapterCount=num_chapters,
                _DesiredTotal=narrative_context.chapter_count,
                _LastChapters=last_chapters_text,
                _NextChapterStart=next_start,
                _NextChapterEnd=next_end
            )
            messages = [
                Interface.BuildSystemQuery(narrative_context.style_guide),
                Interface.BuildUserQuery(append_prompt)
            ]
            # Target a reasonable word count for new chapters without forcing full reflow
            min_word_target = max(200, missing * 150)  # ~150 words per chapter outline segment
            _Logger.Log(f"[Model Trace] Appending missing chapters with model: {selected_model}", 5)
            messages = Interface.SafeGenerateText(
                _Logger, messages, selected_model, min_word_count_target=min_word_target
            )
            new_chapters_text = Interface.GetLastMessageText(messages).strip()
            # Simple guard: if model accidentally repeats earlier chapters, try to slice from first expected header
            expected_header_pattern = re.compile(rf"^#+\s*Chapter\s+{next_start}\\b", re.IGNORECASE | re.MULTILINE)
            match = expected_header_pattern.search(new_chapters_text)
            if match:
                new_chapters_text = new_chapters_text[match.start():].strip()
            # Remove any chapters with numbers LESS than next_start (accidental rewrites)
            header_regex = re.compile(r'(^#+\s*(?:Chapter|Ch\.?)+\s+(\d+)[^\n]*$)', re.IGNORECASE | re.MULTILINE)
            cleaned_lines = []
            skip_mode = False
            current_chapter_num = None
            for line in new_chapters_text.splitlines():
                header_match = header_regex.match(line.strip())
                if header_match:
                    current_chapter_num = int(header_match.group(2))
                    skip_mode = current_chapter_num < next_start
                if not skip_mode:
                    cleaned_lines.append(line)
            new_chapters_text = "\n".join(cleaned_lines).strip()
            outline = outline.strip() + "\n\n" + new_chapters_text + "\n"
            # Recount for logging
            updated_count = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, _Logger, outline, selected_model)
            _Logger.Log(f"After appending, outline now reports {updated_count} chapters.", 5)
            if 0 < updated_count < narrative_context.chapter_count:
                _Logger.Log("Still below desired chapter count after first append attempt; performing one more append iteration.", 5)
                num_chapters = updated_count
                missing = narrative_context.chapter_count - num_chapters
                next_start = num_chapters + 1
                next_end = narrative_context.chapter_count
                last_context_chapters = re.split(r'(?:\n){2,}', new_chapters_text)[-2:]
                last_chapters_text = "\n\n".join(last_context_chapters)
                append_prompt = Writer.Prompts.APPEND_OUTLINE_MISSING_CHAPTERS_PROMPT.format(
                    _CurrentChapterCount=num_chapters,
                    _DesiredTotal=narrative_context.chapter_count,
                    _LastChapters=last_chapters_text,
                    _NextChapterStart=next_start,
                    _NextChapterEnd=next_end
                )
                messages = [
                    Interface.BuildSystemQuery(narrative_context.style_guide),
                    Interface.BuildUserQuery(append_prompt)
                ]
                min_word_target = max(200, missing * 140)
                _Logger.Log(f"[Model Trace] Second append attempt model: {selected_model}", 5)
                messages = Interface.SafeGenerateText(
                    _Logger, messages, selected_model, min_word_count_target=min_word_target
                )
                second_append_text = Interface.GetLastMessageText(messages).strip()
                second_match = expected_header_pattern.search(second_append_text)
                if second_match:
                    second_append_text = second_append_text[second_match.start():].strip()
                header_regex2 = re.compile(r'(^#+\s*(?:Chapter|Ch\.?)+\s+(\d+)[^\n]*$)', re.IGNORECASE | re.MULTILINE)
                cleaned2 = []
                skip_mode2 = False
                for line in second_append_text.splitlines():
                    m2 = header_regex2.match(line.strip())
                    if m2:
                        ch_num2 = int(m2.group(2))
                        skip_mode2 = ch_num2 < next_start
                    if not skip_mode2:
                        cleaned2.append(line)
                second_append_text = "\n".join(cleaned2).strip()
                outline = outline.strip() + "\n\n" + second_append_text + "\n"
                final_count = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, _Logger, outline, selected_model)
                _Logger.Log(f"Final chapter count after second append attempt: {final_count}", 5)

    narrative_context.set_base_novel_outline(outline)

    # --- Step 7: Generate Expanded Per-Chapter Outline (if enabled) ---
    if Writer.Config.EXPAND_OUTLINE:
        _Logger.Log("Starting per-chapter outline expansion...", 3)
        final_num_chapters = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, _Logger, outline, selected_model)

        if final_num_chapters <= 0:
            _Logger.Log(f"Could not determine valid chapter count ({final_num_chapters}). Skipping expansion.", 6)
        else:
            # REFACTORED LOGIC: Generate one chapter at a time for reliability.
            expanded_outlines = []
            full_summary_so_far = "This is the start of the novel."

            for i in range(1, final_num_chapters + 1):
                _Logger.Log(f"Processing detailed outline for Chapter {i}/{final_num_chapters}", 2)

                # Generate the detailed outline for the current chapter
                _Logger.Log(f"[Model Trace] Expanded outline generation for Chapter {i} using model: {selected_model}", 5)
                chapter_outline_text = _generate_expanded_outline_for_chapter(
                    Interface, _Logger, i, outline, narrative_context, full_summary_so_far, selected_model
                )
                expanded_outlines.append(chapter_outline_text)

                # Update the summary with the content of the chapter we just outlined
                _Logger.Log(f"Summarizing newly generated outline for Chapter {i} to build context...", 1)
                summary_prompt = Writer.Prompts.SUMMARIZE_OUTLINE_RANGE_PROMPT.format(
                    _Outline=chapter_outline_text, _StartChapter=i, _EndChapter=i
                )
                summary_messages = [Interface.BuildUserQuery(summary_prompt)]
                summary_messages = Interface.SafeGenerateText(
                    _Logger, summary_messages, selected_model, min_word_count_target=50
                )
                new_summary = Interface.GetLastMessageText(summary_messages)
                full_summary_so_far += f"\n\nSummary for Chapter {i}:\n{new_summary}"

            full_expanded_outline = "\n\n".join(expanded_outlines)
            narrative_context.set_expanded_novel_outline(full_expanded_outline)
            _Logger.Log("Finished expanding all chapter outlines.", 3)

    return narrative_context

# ---------------------------------------------------------------------------
# Helper: Generate expanded outline detail for a single chapter
# ---------------------------------------------------------------------------

def _generate_expanded_outline_for_chapter(
    Interface: Interface,
    _Logger: Logger,
    chapter_number: int,
    full_outline_markdown: str,
    narrative_context: NarrativeContext,
    summary_so_far: str,
    selected_model: str,
) -> str:
    """Generates a detailed, scene-level outline for a single chapter.

    This focuses on reliability: extract the specific chapter's high-level outline block
    then ask the model to expand only that chapter, providing prior summaries for continuity.

    Returns the expanded chapter outline markdown.
    """
    # Extract the chapter block
    pattern = re.compile(rf"(^#+\s*Chapter\s+{chapter_number}[^\n]*)([\s\S]*?)(?=^#+\s*Chapter\s+{chapter_number + 1}\\b|\Z)", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(full_outline_markdown)
    if not match:
        _Logger.Log(f"Could not locate Chapter {chapter_number} in outline. Returning placeholder.", 6)
        return f"# Chapter {chapter_number}: (Missing in base outline)\n- Placeholder: Chapter outline not found; proceed with inferred progression."

    chapter_header = match.group(1).strip()
    chapter_body = match.group(2).strip()
    base_block = f"{chapter_header}\n{chapter_body}".strip()

    # Build expansion prompt (lightweight, resilient)
    expansion_prompt = (
        "You are a master storyteller expanding a single chapter of a novel outline into a more granular scene-level plan.\n\n"
        f"# PRIOR STORY SUMMARY (Context Through Chapter {chapter_number - 1})\n{summary_so_far}\n\n"
        "# CHAPTER TO EXPAND\n" + base_block + "\n\n"
        "# YOUR TASK\n"
        f"Expand ONLY Chapter {chapter_number} into a detailed outline.\n"
        "Provide:\n"
        "- A retained top-level chapter header (do not renumber).\n"
        "- 4-8 scene subsections with markdown '## Scene X: Subtitle' headings.\n"
        "- Under each scene, bullet points of concrete events (no prose paragraphs).\n"
        "- Maintain continuity with prior chapters and foreshadow upcoming arcs.\n"
        "Do NOT outline other chapters. Output ONLY this expanded chapter."
    )

    messages = [
        Interface.BuildSystemQuery(narrative_context.style_guide),
        Interface.BuildUserQuery(expansion_prompt)
    ]
    messages = Interface.SafeGenerateText(
        _Logger, messages, selected_model, min_word_count_target=220
    )
    expanded_text = Interface.GetLastMessageText(messages)
    return expanded_text.strip()


def _verify_and_complete_outline(
    Interface: Interface,
    _Logger: Logger,
    outline_text: str,
    selected_model: str,
    story_type: str,
    max_completion_attempts: int = 3,
) -> str:
    """
    Verifies that an outline is complete and continues generation if it's cut off.
    
    Args:
        Interface: The interface for LLM communication
        _Logger: Logger instance
        outline_text: The initial outline text to verify
        selected_model: Model to use for verification and completion
        story_type: "novel" or "short story" for context
        max_completion_attempts: Maximum number of completion attempts
        
    Returns:
        The completed outline text
    """
    current_outline = outline_text
    
    for attempt in range(max_completion_attempts):
        _Logger.Log(f"Outline completion verification attempt {attempt + 1}/{max_completion_attempts}...", 3)
        
        # Check if outline appears complete
        completion_check_prompt = f"""
You are reviewing a {story_type} outline to determine if it appears complete and properly finished.

OUTLINE TO REVIEW:
---
{current_outline}
---

Analyze this outline and determine:
1. Does it appear to be cut off or incomplete? 
2. Does it have a proper ending/resolution section?
3. Does the last section seem to end abruptly or mid-sentence?
4. For novels: Are there clear chapter divisions and does the final chapter provide resolution?
5. For short stories: Is there a complete narrative arc from beginning to resolution?

Respond in JSON format with:
{{
    "is_complete": true/false,
    "reason": "Brief explanation of why it's complete or incomplete",
    "continuation_point": "If incomplete, describe where the outline should continue from"
}}
"""
        
        messages = [Interface.BuildUserQuery(completion_check_prompt)]
        _, completion_response = Interface.SafeGenerateJSON(
            _Logger, messages, selected_model, _RequiredAttribs=["is_complete", "reason"]
        )
        
        is_complete = completion_response.get("is_complete", False)
        reason = completion_response.get("reason", "Unknown")
        continuation_point = completion_response.get("continuation_point", "")
        
        _Logger.Log(f"Completeness check result: {'Complete' if is_complete else 'Incomplete'} - {reason}", 4)
        
        if is_complete:
            _Logger.Log("Outline verified as complete.", 5)
            break
            
        # If incomplete, generate continuation
        _Logger.Log("Outline appears incomplete. Generating continuation...", 4)
        
        continuation_prompt = f"""
The following {story_type} outline appears to be incomplete or cut off. Please continue writing the outline from where it left off, completing the narrative structure.

EXISTING OUTLINE:
---
{current_outline}
---

CONTINUATION INSTRUCTIONS:
- Continue from where the outline left off: {continuation_point}
- Complete the remaining narrative structure
- For novels: Ensure all remaining chapters are outlined through to a satisfying conclusion
- For short stories: Ensure the narrative arc is completed with proper resolution
- Match the style and format of the existing outline
- Do NOT rewrite or repeat the existing content, only ADD the missing parts
- Ensure the story has a proper ending/resolution

Continue the outline:
"""
        
        continuation_messages = [Interface.BuildUserQuery(continuation_prompt)]
        continuation_messages = Interface.SafeGenerateText(
            _Logger, continuation_messages, selected_model, min_word_count_target=200
        )
        continuation_text = Interface.GetLastMessageText(continuation_messages)
        
        # Append the continuation to the current outline
        current_outline = current_outline.strip() + "\n\n" + continuation_text.strip()
        _Logger.Log(f"Added continuation text. New outline length: {len(current_outline)} characters", 4)
    
    if not completion_response.get("is_complete", False):
        _Logger.Log(f"Warning: Outline may still be incomplete after {max_completion_attempts} attempts.", 6)
    
    return current_outline
