# File: Writer/Prompts.py
# Purpose: A centralized repository for all LLM prompt templates used in the project.
# Refactored to improve clarity, flexibility, and robustness.

# ======================================================================================
# Prompts for Outline and Story Structure
# ======================================================================================

# A flexible style guide to be used as a system prompt for most creative tasks.
LITERARY_STYLE_GUIDE = """
Your writing must be sophisticated, clear, and compelling. Strive for prose that is rich with detail and psychological depth.

**Core Tenets of Your Writing Style:**
1.  **Show, Don't Tell:** Do not state an emotion; describe the actions and sensory details that reveal it. Let the narrative unfold organically through character actions and dialogue.
2.  **Psychological Depth:** Delve into the inner workings of your characters' minds. Their motivations should be complex and their reliability questionable. The psychological landscape is as important as the physical one.
3.  **Avoid AI Tropes:** Do not start sentences with predictable phrases like "Meanwhile," or "As the sun began to set,". Avoid overly simplistic emotional descriptions. The narrative should feel organic and unpredictable.
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
- **Exposition**:
- **Rising Action**:
- **Climax**:
- **Falling Action**:
- **Resolution**: (The story's conclusion, which should be a logical outcome of the premise.)

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
- Ensure it is very clear what content belongs in each chapter. Add significant detail to guide the writing process.
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
- For each scene, please provide a clear heading, a list of characters, a description of the setting, and a summary of the key events.

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
Write the PLOT for chapter {_ChapterNum} of {_TotalChapters}.
Base your writing on the following chapter outline. Your main goal is to establish the sequence of events.
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
Expand upon the provided chapter plot by adding CHARACTER DEVELOPMENT for chapter {_ChapterNum} of {_TotalChapters}.
Do not remove existing content; instead, enrich it with character thoughts, feelings, and motivations, adhering to the established literary style.

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
Expand upon the provided chapter content by adding DIALOGUE for chapter {_ChapterNum} of {_TotalChapters}.
Do not remove existing content; instead, weave natural and purposeful conversations into the scenes. Dialogue should reveal character and subtext.

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
    "## Scene 1: The Confrontation\\n- **Characters:** Kaelan, Informant\\n- **Setting:** The Rusty Flagon...",
    "## Scene 2: The Escape\\n- **Characters:** Kaelan\\n- **Setting:** The city streets..."
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
Do not include any other text. Example: `{{ "IsComplete": true }}`
"""
