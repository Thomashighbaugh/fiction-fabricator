# File: Writer/Prompts.py
# Purpose: A centralized repository for all LLM prompt templates used in the project.
# Refactored to improve clarity, flexibility, and robustness.

# ======================================================================================
# Prompts for Outline and Story Structure
# ======================================================================================

SHORT_STORY_OUTLINE_PROMPT = """
You are a master storyteller tasked with creating a compelling outline for a short story.

**Your Style Guide:**
---
{style_guide}
---

**Core Story Concept:**
Use the user's prompt and the defined story elements to build your outline.
<PROMPT>
{_OutlinePrompt}
</PROMPT>

<ELEMENTS>
{StoryElements}
</ELEMENTS>

**Your Task:**
Write a detailed, scene-by-scene outline for a short story of approximately {word_count} words.
- The plot must be coherent and self-contained, suitable for a short story format.
- Ensure it is very clear what content belongs in each scene.
- For each scene, provide a detailed list of plot items that will occur. This should be a list of events, not prose.
"""

# A flexible style guide to be used as a system prompt for most creative tasks.
LITERARY_STYLE_GUIDE = """
Your writing must be sophisticated, clear, and compelling. Strive for prose that is rich with detail and psychological depth.

**Core Tenets of Your Writing Style:**
1.  **Show, Don't Tell:** Do not state an emotion; describe the actions and sensory details that reveal it. Let the narrative unfold organically through character actions and dialogue.
2.  **Psychological Depth:** Delve into the inner workings of your characters' minds. Their motivations should be complex and their reliability questionable. The psychological landscape is as important as the physical one.
3.  **Avoid AI Tropes:** Do not start sentences with predictable phrases like "Meanwhile," or "As the sun began to set,". Avoid overly simplistic emotional descriptions. The narrative should feel organic and unpredictable.
4.  **Avoid Clichés:** Actively avoid overused phrases, predictable plot devices, and stereotyped characters. Strive for originality in expression and ideas.
"""

# New prompt for generating story elements, focusing on user's prompt.
GENERATE_STORY_ELEMENTS_PROMPT = """
You are a master storyteller. Your task is to analyze a user's story prompt and define its core creative elements.

<USER_PROMPT>
{_OutlinePrompt}
</USER_PROMPT>

Adhering to the spirit of the user's prompt, define the following elements in markdown format.

<RESPONSE_TEMPLATE>
# Story Title

## Genre
- **Category**: (e.g., Psychological Thriller, Sci-Fi Adventure, Fantasy Romance)

## Theme
- **Central Idea or Message**: (The core message or question explored in the story.)

## Pacing
- **Speed**: (e.g., slow-burn, relentless, feverish)

## Style
- **Language Use**: (e.g., Sparse and clinical, ornate and literary, stream-of-consciousness.)

## Plot
- **Exposition**: A list of events that will occur in the exposition.
- **Rising Action**: A list of events that will occur in the rising action.
- **Climax**: A list of events that will occur in the climax.
- **Falling Action**: A list of events that will occur in the falling action.
- **Resolution**: A list of events that will occur in the resolution.

## Setting
### Setting 1
- **Time**:
- **Location**:
- **Culture**:
- **Mood**:

(Repeat for additional settings)

## Conflict
- **Type**: (e.g., internal (man vs. self), external (man vs. society))
- **Description**: (The central conflict driving the narrative.)

## Characters
### Main Character(s)
#### Main Character 1
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Motivation**:

(Repeat for additional main characters)

### Supporting Characters
#### Character 1
- **Name**:
- **Role in the story**:

(Repeat for additional supporting characters)
</RESPONSE_TEMPLATE>

Do not include the XML tags in your response. Infuse the spirit of the user's prompt into every element you create.
"""

CHAPTER_COUNT_PROMPT = """
<OUTLINE>
{_Summary}
</OUTLINE>

Please provide a JSON formatted response containing the total number of chapters in the above outline.

Respond with {{"TotalChapters": <total chapter count>}}
Please do not include any other text, just the JSON, as your response will be parsed by a computer.
"""

INITIAL_OUTLINE_PROMPT = """
You are a master storyteller tasked with creating a compelling, chapter-by-chapter novel outline.

**Your Style Guide:**
---
{style_guide}
---

**Core Story Concept:**
Use the user's prompt and the defined story elements to build your outline.
<PROMPT>
{_OutlinePrompt}
</PROMPT>

<ELEMENTS>
{StoryElements}
</ELEMENTS>

**Your Task:**
Write a detailed, chapter-by-chapter outline in markdown format.
- The plot must be coherent, with each chapter building on the last toward a satisfying conclusion.
- For each chapter, provide a clear markdown header (e.g., # Chapter 1: Title) and a numbered or bulleted list of critical plot points/events.
- Each plot point must directly reference the premise and story elements above.
- Do NOT write any prose, summaries, or scene text—only bullet points or numbered lists of events.
- If you write prose, your output will be rejected.
"""

OUTLINE_REVISION_PROMPT = """
You are a master storyteller revising a novel outline based on editorial feedback.

**Your Style Guide:**
---
{style_guide}
---

**Outline to Revise:**
<OUTLINE>
{_Outline}
</OUTLINE>

**Editorial Feedback:**
<FEEDBACK>
{_Feedback}
</FEEDBACK>

**Your Task:**
Rewrite the entire outline, incorporating the feedback to improve it.
- For each chapter, provide a clear markdown header and a numbered or bulleted list of critical plot points/events.
- Each plot point must directly reference the premise and story elements above.
- Do NOT write any prose, summaries, or scene text—only bullet points or numbered lists of events.
- If you write prose, your output will be rejected.
- Deepen the plot, character arcs, and thematic complexity.
- Ensure the revised outline is aligned with the style guide.
- Add more detail to every chapter, making the sequence of events and character motivations crystal clear.
- The final outline must be a complete, chapter-by-chapter markdown document.
"""

GET_IMPORTANT_BASE_PROMPT_INFO = """
Please extract any important information from the user's prompt below.
Focus on instructions that are not part of the story's plot or characters, but are about the writing style, format, length, or overall vision.

<USER_PROMPT>
{_Prompt}
</USER_PROMPT>

Please use the below template for formatting your response.
(Don't use the xml tags though - those are for example only)

<EXAMPLE>
# Important Additional Context
- Important point 1
- Important point 2
</EXAMPLE>

Do NOT write the outline itself, **just the extra context**. Keep your responses short and in a bulleted list.
If the prompt provides no such context, you must respond with "No additional context found."
"""

EXPAND_OUTLINE_TO_MIN_CHAPTERS_PROMPT = """
You are a master story developer. Your task is to revise a novel outline to meet a minimum chapter count by adding meaningful content.

# CURRENT OUTLINE
---
{_Outline}
---

# TASK
Revise the outline so that it contains at least **{_MinChapters}** chapters.
Do NOT just split existing chapters. Instead, expand the story by:
- Developing subplots that explore the story's core themes.
- Giving more space to character arcs.
- Adding new events or complications that are consistent with the story's tone and plot.
- Fleshing out the rising action, climax, or falling action with more detail.

The goal is a richer, more detailed story that naturally fills the required number of chapters.
Your response should be the new, complete, chapter-by-chapter markdown outline.
"""

APPEND_OUTLINE_MISSING_CHAPTERS_PROMPT = """
You are a master story developer. The existing outline currently stops at Chapter {_CurrentChapterCount}.
Your task is to write ONLY the missing chapters needed to reach a total of {_DesiredTotal} chapters.

# EXISTING OUTLINE (LAST CHAPTERS FOR CONTEXT)
---
{_LastChapters}
---

# TASK
Write Chapters {_NextChapterStart} through {_NextChapterEnd}.

Requirements:
- Do NOT rewrite, alter, or repeat any earlier chapters.
- Begin directly with "# Chapter {_NextChapterStart}:" (or the original heading style) and continue sequentially.
- For EACH new chapter:
  - Provide a markdown header (e.g., `# Chapter X: Title` — a short, evocative title is encouraged).
  - Follow with a numbered or bulleted list of plot points/events (not prose paragraphs) that advance character arcs, conflicts, and themes.
- Maintain continuity with prior events and character motivations.
- Build escalating tension toward a satisfying resolution by the final chapter.
- If a detail is missing, infer something plausible and keep going—do not stall or ask questions.

Output ONLY the new chapters you are adding. Do not include commentary, summaries, or earlier chapters.
"""

SUMMARIZE_OUTLINE_RANGE_PROMPT = """
You are a story analyst. Your task is to read a novel outline and summarize a specific range of chapters.

# FULL NOVEL OUTLINE
---
{_Outline}
---

# YOUR TASK
Provide a concise summary of the events, character arcs, and key plot points that occur between **Chapter {_StartChapter} and Chapter {_EndChapter}**, based *only* on the full outline provided.

Your response should be a single, coherent paragraph.
"""

GENERATE_CHAPTER_GROUP_OUTLINE_PROMPT = """
You are a master storyteller. Your task is to expand a part of a novel outline into a detailed, scene-by-scene breakdown.

# FULL NOVEL OUTLINE
This is the complete outline for the entire story. Use it for high-level context.
---
{_Outline}
---

# SUMMARY OF OTHER STORY PARTS
Here is a summary of the major events from other parts of the story. You must ensure the chapters you are outlining connect logically to these events.
---
{_OtherGroupsSummary}
---

# YOUR TASK
Your sole focus is to generate detailed, scene-by-scene outlines for **Chapters {_StartChapter} through {_EndChapter}**.

For EACH chapter in this range, provide a markdown block that includes:
- A main markdown header for the chapter (e.g., `# Chapter X: The Title`).
- Multiple scene-by-scene breakdowns under that chapter header.
- For each scene, please provide a clear heading, a list of characters, a description of the setting, and a DETAILED LIST OF PLOT ITEMS that will occur in the scene. This should be a list of events, not prose.

Your output should be a single, continuous markdown document containing the detailed outlines for ALL chapters in the specified range.
"""

# ======================================================================================
# Prompts for Chapter Generation
# ======================================================================================

CHAPTER_GENERATION_PROMPT = """
Please extract the part of this outline that is just for chapter {_ChapterNum}.

<OUTLINE>
{_Outline}
</OUTLINE>

Do not include anything else in your response except just the content for chapter {_ChapterNum}.
"""

CHAPTER_GENERATION_STAGE1 = """
# Context
Here is the context for the novel so far, including themes, motifs, and summaries of previous chapters. Use this to ensure your writing is coherent.
---
{narrative_context}
---

# Your Task
You are writing chapter {_ChapterNum} of {_TotalChapters}.
Your primary goal is to continue the story from where the previous chapter left off.
Write the PLOT for the chapter, based on the chapter outline below.
It is imperative that your writing connects well with the previous chapter.

**Crucial:** You must adhere to the literary style defined in the system prompt.

<CHAPTER_OUTLINE>
{ThisChapterOutline}
</CHAPTER_OUTLINE>
"""

CHAPTER_GENERATION_STAGE2 = """
# Context
Here is the context for the novel so far. Use this to inform your writing.
---
{narrative_context}
---

# Your Task
You are continuing to write chapter {_ChapterNum} of {_TotalChapters}.
Expand upon the provided chapter plot by adding CHARACTER DEVELOPMENT.
Do not remove existing content; instead, enrich it with character thoughts, feelings, and motivations, adhering to the established literary style.
Ensure the character development is a natural continuation of the previous chapter and the story so far.

Here is the current chapter's plot:
<CHAPTER_PLOT>
{Stage1Chapter}
</CHAPTER_PLOT>
"""

CHAPTER_GENERATION_STAGE3 = """
# Context
Here is the context for the novel so far. Use this to inform your writing.
---
{narrative_context}
---

# Your Task
You are finishing chapter {_ChapterNum} of {_TotalChapters}.
Expand upon the provided chapter content by adding DIALOGUE.
Do not remove existing content; instead, weave natural and purposeful conversations into the scenes. Dialogue should reveal character and subtext, and continue the narrative from the previous chapter.

Here's what I have so far for this chapter:
<CHAPTER_CONTENT>
{Stage2Chapter}
</CHAPTER_CONTENT>

As you add dialogue, please remove any leftover headings or author notes. Your output should be clean, final chapter text.
"""


# ======================================================================================
# Prompts for Summarization and Coherence
# ======================================================================================

SUMMARIZE_SCENE_PROMPT = """
Please analyze the following scene and provide a structured JSON response.

<SCENE_TEXT>
{scene_text}
</SCENE_TEXT>

Your response must be a single JSON object with two keys:
1. "summary": A concise paragraph summarizing the key events, character interactions, and setting of the scene.
2. "key_points_for_next_scene": A list of 2-4 bullet points identifying crucial pieces of information (e.g., unresolved conflicts, new character goals, important objects, lingering questions) that must be carried forward to ensure continuity in the next scene.

Provide only the JSON object in your response.
"""

SUMMARIZE_CHAPTER_PROMPT = """
Please provide a concise, one-paragraph summary of the following chapter text.
Focus on the main plot advancements, significant character developments, and the state of the story at the chapter's conclusion.

<CHAPTER_TEXT>
{chapter_text}
</CHAPTER_TEXT>

Do not include anything in your response except the summary paragraph.
"""

SUMMARIZE_SCENE_PIECE_PROMPT = """
You are a story coherence assistant. Your task is to read a small chunk of a scene and summarize it very concisely. This summary will be used to prompt the AI to write the *next* chunk of the scene, so it must be accurate and capture the immediate state of things.

# SCENE CHUNK
---
{scene_piece_text}
---

# YOUR TASK
Provide a 1-2 sentence summary of the chunk above. Focus only on what happened in this specific text. What is the very last thing that happened? Who is present and what is their immediate situation?
"""

# ======================================================================================
# Prompts for Critique and Revision
# ======================================================================================

# --- OUTLINE-SPECIFIC CRITIQUE AND REVISION PROMPTS ---

OUTLINE_STRUCTURE_CRITIQUE_PROMPT = """
You are a master story structure editor. Your sole focus is on the clarity, organization, and completeness of the outline below.

# OUTLINE TO CRITIQUE
---
{outline_text}
---

# YOUR TASK
- Critique the outline ONLY as a chapter-by-chapter list of plot points.
- Do NOT comment on prose, style, or tone.
- Ensure each chapter has a clear header and a numbered list of critical plot points/events (not prose).
- Point out any chapters that are missing, unclear, or have plot points that are vague, redundant, or written as prose.
- Provide actionable feedback in bullet points for improving the outline structure.
"""

REVISE_OUTLINE_STRUCTURE_PROMPT = """
You are a master story developer. Your task is to revise the outline below based on editorial feedback, ensuring it remains a chapter-by-chapter list of plot points.

# ORIGINAL OUTLINE
---
{original_outline}
---

# EDITORIAL FEEDBACK
---
{critique}
---

# YOUR TASK
- Rewrite the outline so that each chapter has a clear header and a numbered list of critical plot points/events (not prose).
- Do NOT write any prose, summaries, or scene text.
- Incorporate all feedback to improve clarity, organization, and completeness.
- Output only the revised outline as a markdown document.
"""

# --- NEW: Prompts for the 3-Step Critique and Revision Process ---

# 1. CONSISTENCY CHECK
CONSISTENCY_CRITIQUE_PROMPT = """
You are a brutally honest and relentlessly critical continuity editor. Your standards are incredibly high.
Your sole focus is on plot and character consistency.
Critique the "TEXT TO CRITIQUE" based *only* on its consistency with the provided context.

# ORIGINAL USER PROMPT (The Source of Truth)
---
{initial_user_prompt}
---

# CONTEXT OF THE STORY SO FAR
---
{narrative_context_summary}
---

# TASK DESCRIPTION
The author was trying to accomplish the following: "{task_description}"

# TEXT TO CRITIQUE
---
{text_to_critique}
---

# YOUR INSTRUCTIONS
Be ruthless in your assessment.
1.  **Plot Consistency:** Does the text contradict any established plot points from the "CONTEXT OF THE STORY SO FAR"?
2.  **Character Consistency:** Do characters behave in ways that are consistent with their established personalities and motivations?
3.  **Lore Book Consistency:** Does the text adhere to the information and rules established in the **LORE BOOK**?
4.  **Task Fulfillment:** Does the text logically fulfill its "TASK DESCRIPTION" without violating continuity?
5.  **Internal Consistency:** Does the text contradict itself within its own logic?

Provide a few bullet points of direct, actionable feedback focused *only* on fixing continuity errors. If there are no errors, you must state "No consistency issues found." Do not be lenient.
"""

REVISE_FOR_CONSISTENCY_PROMPT = """
You are a writer tasked with revising a piece of text to fix continuity errors based on an editor's feedback.

# STORY CONTEXT
---
{narrative_context_summary}
---

# ORIGINAL TEXT
---
{original_text}
---

# EDITOR'S CONSISTENCY CRITIQUE
---
{critique}
---

# YOUR TASK
Rewrite the "ORIGINAL TEXT" to address the consistency issues raised in the "EDITOR'S CONSISTENCY CRITIQUE".
- Ensure the revised text is fully coherent with the "STORY CONTEXT" and the **LORE BOOK**.
- Do not change stylistic elements; focus *only* on fixing the plot and character contradictions.
- Output only the revised text.
"""

# 2. STYLE AND TONE CHECK
STYLE_CRITIQUE_PROMPT = """
You are a brutally honest and relentlessly critical stylistic editor. Your standards are incredibly high.
Your sole focus is on tone, style, and adherence to the creative vision.
Critique the "TEXT TO CRITIQUE" based *only* on its style.

# STYLE GUIDE (Non-negotiable)
---
{style_guide}
---

# ORIGINAL USER PROMPT (The Source of Truth)
---
{initial_user_prompt}
---

# TEXT TO CRITIQUE
---
{text_to_critique}
---

# YOUR INSTRUCTIONS
Be ruthless in your assessment.
1.  **Style Adherence:** Does the text's prose, pacing, and tone strictly follow the **STYLE GUIDE**?
2.  **Vision Adherence:** Does the text capture the spirit and intent of the "ORIGINAL USER PROMPT"?
3.  **Quality of Prose:** Is the writing sophisticated, clear, and compelling? Does it "show, don't tell"?
4.  **Originality:** Does the text avoid clichés in language, character, and plot?

Provide a few bullet points of direct, actionable feedback focused *only* on improving the style and tone. Do not be lenient.
"""

REVISE_FOR_STYLE_PROMPT = """
You are a master writer tasked with revising a piece of text to improve its style and tone based on an editor's feedback.

# STYLE GUIDE (Non-negotiable)
---
{style_guide}
---

# ORIGINAL TEXT
---
{original_text}
---

# EDITOR'S STYLE CRITIQUE
---
{critique}
---

# YOUR TASK
Rewrite the "ORIGINAL TEXT" to address the stylistic issues raised in the "EDITOR'S STYLE CRITIQUE".
- The revised text's prose, pacing, and tone MUST strictly adhere to the **STYLE GUIDE**.
- Focus on elevating the language, deepening the psychological complexity, and ensuring the tone is perfect.
- Output only the revised text.
"""

# 3. STRUCTURE AND LENGTH CHECK
STRUCTURE_CRITIQUE_PROMPT = """
You are a brutally honest and relentlessly critical structural editor. Your standards are incredibly high.
Your sole focus is on the structure, length, and clarity of the text.
Critique the "TEXT TO CRITIQUE" based *only* on its structural integrity.

# TASK DESCRIPTION
The author was trying to accomplish the following: "{task_description}"

# TEXT TO CRITIQUE
---
{text_to_critique}
---

# YOUR INSTRUCTIONS
Be ruthless in your assessment.
1.  **Structural Soundness:** Is the text well-organized? Does it have a clear beginning, middle, and end?
2.  **Length Appropriateness:** Is the length appropriate for its purpose as described in the "TASK DESCRIPTION"? Is it too brief or too verbose?
3.  **Clarity:** Is the text easy to follow? Are there any confusing or convoluted sections?
4.  **Pacing:** Is the pacing effective? Does it create tension and suspense where appropriate?

Provide a few bullet points of direct, actionable feedback focused *only* on improving the structure and length. Do not be lenient.
"""

# --- NEW: Prompts for Scoring the 3-Step Revisions ---

CONSISTENCY_SCORE_PROMPT = """
You are a continuity editor. Your sole focus is on plot and character consistency.
Score the "TEXT TO SCORE" from 0 to 100 on its consistency with the provided context.

# SCORING CRITERIA
- **100:** Perfect consistency. No contradictions with the story context or user prompt.
- **95-99:** Excellent. The text is almost perfectly consistent, with only trivial, easily-missed issues.
- **85-94:** Good. The text is mostly consistent, but contains a few minor issues that need addressing.
- **70-84:** Fair. The text has some noticeable inconsistencies that require revision.
- **50-69:** Poor. The text has significant contradictions that harm the narrative.
- **<50:** Unacceptable. The text is fundamentally inconsistent with the established story.

# CONTEXT OF THE STORY SO FAR
---
{narrative_context_summary}
---

# TEXT TO SCORE
---
{text_to_critique}
---

# YOUR TASK
Return a JSON object with your score and a brief justification.
Example: {{ "score": 95, "justification": "The character's motivation in the third paragraph is slightly inconsistent with their actions in the previous chapter." }}
"""

STYLE_SCORE_PROMPT = """
You are a stylistic editor. Your sole focus is on tone, style, and adherence to the creative vision.
Score the "TEXT TO SCORE" from 0 to 100 on its stylistic quality.

# SCORING CRITERIA
- **100:** Perfect stylistic adherence. The prose is masterful and perfectly matches the style guide.
- **95-99:** Excellent. The prose is masterful and perfectly matches the style guide.
- **85-94:** Good. The style is strong, but with some minor deviations or flat sections.
- **70-84:** Fair. The text generally follows the style guide, but has noticeable sections that are flat, generic, or inconsistent.
- **50-69:** Poor. The style is often generic and fails to capture the intended tone.
- **<50:** Unacceptable. The text completely ignores the style guide.

# STYLE GUIDE (Non-negotiable)
---
{style_guide}
---

# TEXT TO SCORE
---
{text_to_critique}
---

# YOUR TASK
Return a JSON object with your score and a brief justification.
Example: {{ "score": 88, "justification": "The dialogue is sharp, but the descriptive prose in the opening paragraphs is too simplistic and violates the 'Show, Don't Tell' rule." }}
"""

STRUCTURE_SCORE_PROMPT = """
You are a structural editor. Your sole focus is on the structure, length, and clarity of the text.
Score the "TEXT TO SCORE" from 0 to 100 on its structural integrity.

# SCORING CRITERIA
- **100:** Perfect structure. The text is well-organized, appropriately paced, and perfectly clear.
- **95-99:** Excellent. The structure is strong, clear, and well-paced with only trivial issues.
- **85-94:** Good. The text is generally well-structured, but has some minor organizational or pacing problems.
- **70-84:** Fair. The text has noticeable structural issues, organizational problems, or pacing flaws.
- **50-69:** Poor. The structure is confusing, and the length is inappropriate for the task.
- **<50:** Unacceptable. The text is disorganized and unclear.

# TASK DESCRIPTION
The text was intended to accomplish the following: "{task_description}"

# TEXT TO SCORE
---
{text_to_critique}
---

# YOUR TASK
Return a JSON object with your score and a brief justification.
Example: {{ "score": 85, "justification": "The beginning is strong, but the middle section is disorganized and the ending feels rushed, not adequately fulfilling the task description." }}
"""

REVISE_FOR_STRUCTURE_PROMPT = """
You are a writer tasked with revising a piece of text to improve its structure and length based on an editor's feedback.

# ORIGINAL TEXT
---
{original_text}
---

# EDITOR'S STRUCTURAL CRITIQUE
---
{critique}
---

# YOUR TASK
Rewrite the "ORIGINAL TEXT" to address the structural issues raised in the "EDITOR'S STRUCTURAL CRITIQUE".
- Ensure the text is well-organized and the length is appropriate for its purpose.
- Improve clarity and flow.
- Output only the revised text.
"""


CRITIQUE_CREATIVE_CONTENT_PROMPT = """
You are a literary editor providing feedback on a piece of writing for a novel.
Your goal is to provide specific, constructive criticism to help the author improve the piece, ensuring it aligns with the original creative vision and the required literary style.

# STYLE GUIDE (Non-negotiable)
---
{style_guide}
---

# ORIGINAL USER PROMPT (The Source of Truth)
This is the core idea the author started with.
---
{initial_user_prompt}
---

# CONTEXT OF THE STORY SO FAR
This is a summary of events written so far.
---
{narrative_context_summary}
---

# TASK DESCRIPTION
The author was trying to accomplish the following: "{task_description}"

# TEXT TO CRITIQUE
---
{text_to_critique}
---

# YOUR INSTRUCTIONS
Critique the "TEXT TO CRITIQUE". Your feedback is crucial.
1.  **Style Adherence:** Does the text follow the **STYLE GUIDE**? Is it compelling and psychologically complex?
2.  **Prompt Adherence:** Does it honor the core ideas from the "ORIGINAL USER PROMPT"?
3.  **Coherence:** Does it logically follow from the "CONTEXT OF THE STORY SO FAR"?
4.  **Task Fulfillment:** Did it successfully achieve its "TASK DESCRIPTION"?

Provide a few bullet points of direct, actionable feedback.
{is_json_output}
"""

REVISE_CREATIVE_CONTENT_BASED_ON_CRITIQUE_PROMPT = """
You are a master fiction writer tasked with revising a piece of text based on an editor's critique.

# STYLE GUIDE (Non-negotiable)
Your revision must embody this style.
---
{style_guide}
---

# ORIGINAL USER PROMPT (The Source of Truth)
Your revision MUST align with this core idea.
---
{initial_user_prompt}
---

# STORY CONTEXT
This is the background for the story you are working on.
---
{narrative_context_summary}
---

# ORIGINAL TEXT
This was the first draft.
---
{original_text}
---

# EDITOR'S CRITIQUE
Here is the feedback you must address.
---
{critique}
---

# YOUR TASK
Rewrite the "ORIGINAL TEXT" to address the points in the "EDITOR'S CRITIQUE".
- You MUST stay true to the original text's purpose, as described here: "{task_description}".
- You MUST ensure your revision is strongly aligned with the "STYLE GUIDE" and "ORIGINAL USER PROMPT".
- You MUST ensure the revised text is coherent with the story's context.

{json_instructions}
"""

CLEAN_REVISED_TEXT_PROMPT = """
You are a cleanup utility. The following text was generated by an AI that was instructed to revise a piece of creative writing. It may have included extraneous notes or other non-narrative text.

# TEXT TO CLEAN
---
{text_to_clean}
---

# YOUR TASK
Your sole job is to extract and return ONLY the core, clean, narrative prose from the text above.
- Remove any headings, author notes, or meta-commentary (e.g., "Here is the revised text:").
- Return only the story content itself.
"""

CHAPTER_REVISION = """
Please revise the following chapter based on the provided feedback, adhering to the literary style defined in the system prompt.

<CHAPTER_CONTENT>
{_Chapter}
</CHAPTER_CONTENT>

<FEEDBACK>
{_Feedback}
</FEEDBACK>

Do not reflect on the revisions; just write the improved chapter.
"""

CRITIC_OUTLINE_PROMPT = """
Please critique the following outline. Provide constructive criticism on how it can be improved and point out any problems with plot, pacing, or characterization.

<OUTLINE>
{_Outline}
</OUTLINE>
"""

OUTLINE_COMPLETE_PROMPT = """
<OUTLINE>
{_Outline}
</OUTLINE>

Does this outline meet all of the following criteria?
- Pacing: The story does not rush over important plot points or excessively focus on minor ones.
- Flow: Chapters flow logically into each other with a clear and consistent narrative structure.
- Completeness: The outline presents a full and coherent story from beginning to end.

Give a JSON formatted response, containing the key \"IsComplete\" with a boolean value (true/false).
Please do not include any other text, just the JSON.
"""

# --- NEW: Specific prompt for JSON parsing errors ---
JSON_PARSE_ERROR = "Your previous response was not valid JSON and could not be parsed. The parser returned the following error: `{_Error}`. It is crucial that your entire response be a single, valid JSON object. Please correct your response and provide only the valid JSON."

CRITIC_CHAPTER_PROMPT = """<CHAPTER>
{_Chapter}
</CHAPTER>

Please give feedback on the above chapter based on pacing, flow, characterization, and overall narrative quality.
"""

CHAPTER_COMPLETE_PROMPT = """
<CHAPTER>
{_Chapter}
</CHAPTER>

Does this chapter meet the following criteria?
- Pacing and Flow: The chapter is well-paced and flows logically.
- Quality Writing: The chapter is engaging, detailed, and written in a sophisticated, human-like style.
- Narrative Cohesion: The chapter feels like a complete part of a larger novel.

Give a JSON formatted response, with the key \"IsComplete\" and a boolean value (true/false).
Please do not include any other text, just the JSON.
"""
CHAPTER_EDIT_PROMPT = """
You are a developmental editor performing a holistic edit on a chapter to ensure it fits perfectly within the novel.

# STYLE GUIDE
---
{style_guide}
---

# FULL STORY OUTLINE
For context, here is the master outline for the entire novel.
---
{_Outline}
---

# FULL TEXT OF OTHER CHAPTERS
Here is the text of the surrounding chapters. Use this to ensure seamless transitions and consistent character voice.
---
{NovelText}
---

# CHAPTER TO EDIT
Now, please perform a detailed edit of Chapter {i}.
---
{_Chapter}
---

# YOUR TASK
Rewrite Chapter {i}. Improve its prose, pacing, and dialogue. Most importantly, ensure it aligns perfectly with the STYLE GUIDE, the full story outline, and connects seamlessly with the other chapters provided. Output only the revised chapter text.
"""
CHAPTER_SCRUB_PROMPT = """
<CHAPTER>
{_Chapter}
</CHAPTER>

Given the above chapter, please clean it up so that it is ready to be published.
Remove any leftover outlines, author notes, or editorial comments, leaving only the finished story text.
Do not comment on your task; your output will be the final print version.
"""
STATS_PROMPT = """
Please write a JSON formatted response based on the story written in previous messages.

{{
"Title": "a short, evocative title for the story",
"Summary": "a paragraph that summarizes the story from start to finish",
"Tags": "a string of tags separated by commas that describe the story's genre and themes",
"OverallRating": "your overall score for the story from 0-100"
}}

Remember to make your response valid JSON with no extra words.
"""

# ======================================================================================
# Prompts for Lorebook Management
# ======================================================================================

LOREBOOK_GENERATION = """
You are a world-building assistant. Your task is to generate a structured lorebook from a user's prompt.
The lorebook should be a JSON object containing a 'lorebook_name' and a list of 'entries'.
Each entry should have a 'name' and 'content'.

<USER_PROMPT>
{prompt}
</USER_PROMPT>

Generate a comprehensive lorebook based on the user's prompt.
The response must be a single JSON object.
"""

LOREBOOK_ENTRY_GENERATION = """
You are a world-building assistant. Your task is to generate a single lorebook entry.
The entry should be a JSON object with a 'content' field.

<PROMPT>
{prompt}
</PROMPT>

Generate a detailed lorebook entry based on the user's prompt.
The response must be a single JSON object.
"""

LOREBOOK_ENTRY_EDITING = """
You are a world-building assistant. Your task is to edit an existing lorebook entry based on a prompt.
The entry should be a JSON object with a 'content' field.

<ORIGINAL_CONTENT>
{original_content}
</ORIGINAL_CONTENT>

<PROMPT>
{prompt}
</PROMPT>

Edit the lorebook entry based on the user's prompt.
The response must be a single JSON object.
"""

LOREBOOK_ENTRY_ENHANCEMENT = """
You are a world-building assistant. Your task is to enhance a manually written lorebook entry.
The entry should be a JSON object with a 'content' field.

<ORIGINAL_CONTENT>
{original_content}
</ORIGINAL_CONTENT>

Enhance the lorebook entry, making it more detailed, evocative, and consistent with a high-quality fantasy or sci-fi world.
The response must be a single JSON object.
"""

# ======================================================================================
# Prompts for Scene-by-Scene Generation (Refactored)
# ======================================================================================

CHAPTER_TO_SCENES = """
# CONTEXT
I am writing a story based on the high-level user prompt below.
<USER_PROMPT>
{_Prompt}
</USER_PROMPT>

Below is my overall novel outline derived from that prompt:
<OUTLINE>
{_Outline}
</OUTLINE>

# OBJECTIVE
Create a detailed scene-by-scene outline for the chapter detailed below. For each scene, describe what happens, its tone, the characters present, and the setting.

Here's the specific chapter outline to expand into scenes:
<CHAPTER_OUTLINE>
{_ThisChapter}
</CHAPTER_OUTLINE>

# REQUIREMENTS
- You MUST generate a minimum of 3 scenes. If the chapter outline is simple, expand it with additional character moments or complications that fit the narrative.
- Format your response in markdown, with clear headings for each scene. Add enough detail to guide the writing of a full scene.
"""

SCENES_TO_JSON = """
# CONTEXT
I need to convert the following scene-by-scene outline into a JSON formatted list of strings.
<SCENE_OUTLINE>
{_Scenes}
</SCENE_OUTLINE>

# OBJECTIVE
Create a JSON list where each element is a string containing the full markdown content for one scene.
Example:
[
    "## Scene 1: The Confrontation\n- **Characters:** Kaelan, Informant\n- **Setting:** The Rusty Flagon...",
    "## Scene 2: The Escape\n- **Characters:** Kaelan\n- **Setting:** The city streets..."
]

Do not include any other json fields; it must be a simple list of strings. Respond in pure, valid JSON. Do not lose any information from the original outline.
"""

SCENE_OUTLINE_TO_SCENE = """
# CONTEXT
You are a creative writer. I need your help writing a full scene based on the scene outline below.
Here is a summary of the story and relevant events so far:
---
{narrative_context}
---

# STYLE GUIDE
---
{style_guide}
---

# OBJECTIVE
Write a full, engaging scene based on the following scene outline. Include dialogue, character actions, thoughts, and descriptions as appropriate.

<SCENE_OUTLINE>
{_SceneOutline}
</SCENE_OUTLINE>

Your writing style must adhere to the **STYLE GUIDE**. Show, don't tell. Focus on psychological depth and sensory details.
Output only the scene's text.
"""

CONTINUE_SCENE_PIECE_PROMPT = """
# CONTEXT
You are writing a scene for a novel, continuing from where the last writer left off.
Here is a summary of what has happened in the scene so far:
---
{summary_of_previous_pieces}
---

# SCENE GOALS
This is the overall outline for the *entire* scene you are writing. Use it to understand the scene's ultimate destination.
---
{_SceneOutline}
---

# STYLE GUIDE
---
{style_guide}
---

# YOUR TASK
Write the very next part of the scene, picking up *immediately* where the previous part left off.
- Write approximately 300-400 words.
- Your writing must flow seamlessly from the summary of the previous pieces.
- Continue to advance the plot and character development towards the goals in the **SCENE GOALS**.
- Adhere strictly to the **STYLE GUIDE**.

Do not repeat what has already happened. Do not summarize. Do not add author notes. Write only the next block of prose for the scene.
"""

IS_SCENE_COMPLETE_PROMPT = """
You are a story structure analyst. You need to determine if a scene has reached a satisfactory conclusion based on its objectives.

# SCENE OUTLINE / GOALS
This is what the scene was supposed to accomplish.
---
{_SceneOutline}
---

# GENERATED SCENE TEXT
This is the full text of the scene that has been written so far.
---
{full_scene_text}
---

# YOUR TASK
Has the "GENERATED SCENE TEXT" fully and satisfactorily accomplished all the key objectives described in the "SCENE OUTLINE / GOALS"?
- Consider if the plot points have been addressed and character moments have occurred.
- Consider if the scene has reached a logical stopping point or a natural transition point.

Respond with a single JSON object with one key, "IsComplete", and a boolean value (true/false).
Do not include any other text. Example: {{ "IsComplete": true }}
"""

# ======================================================================================
# Generic Content Completion Verification
# ======================================================================================

VERIFY_CONTENT_COMPLETION_PROMPT = """
You are a content completion analyst. Your task is to determine if generated content appears to have been cut off mid-generation or is complete.

# CONTENT TYPE AND PURPOSE
Content Type: {content_type}
Expected Purpose: {expected_purpose}

# CONTENT TO ANALYZE
---
{content}
---

# YOUR TASK
Analyze the provided content to determine if it appears complete or was cut off mid-generation.

Consider these indicators of incomplete content:
- Ends mid-sentence or mid-paragraph without logical conclusion
- Missing expected sections based on the content type and purpose
- Abrupt termination that doesn't feel intentional
- Incomplete lists, outlines, or structured content
- Missing closing elements (conclusions, resolutions, etc.)

Consider these indicators of complete content:
- Ends at a natural stopping point
- Fulfills the expected purpose for this content type
- Has logical flow from beginning to end
- Contains all expected structural elements

Respond with a JSON object containing:
- "is_complete": boolean (true if complete, false if appears cut off)
- "analysis": string (brief explanation of your assessment)

Example: {{ "is_complete": false, "analysis": "The content ends abruptly mid-sentence in what appears to be the middle of describing a character, suggesting generation was cut off." }}
"""
