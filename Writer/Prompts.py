# ======================================================================================
# Prompts for Outline and Chapter Structure
# ======================================================================================

GENERATE_STORY_ELEMENTS_PROMPT = """
I'm working on writing a fictional story, and I'd like your help writing out the story elements.

Here's the prompt for my story.
<PROMPT>
{_OutlinePrompt}
</PROMPT>

Please make your response have the following format:

<RESPONSE_TEMPLATE>
# Story Title

## Genre
- **Category**: (e.g., romance, mystery, science fiction, fantasy, horror)

## Theme
- **Central Idea or Message**:

## Pacing
- **Speed**: (e.g., slow, fast)

## Style
- **Language Use**: (e.g., sentence structure, vocabulary, tone, figurative language)

## Plot
- **Exposition**:
- **Rising Action**:
- **Climax**:
- **Falling Action**:
- **Resolution**:

## Setting
### Setting 1
- **Time**: (e.g., present day, future, past)
- **Location**: (e.g., city, countryside, another planet)
- **Culture**: (e.g., modern, medieval, alien)
- **Mood**: (e.g., gloomy, high-tech, dystopian)

(Repeat the above structure for additional settings)

## Conflict
- **Type**: (e.g., internal, external)
- **Description**:

## Symbolism
### Symbol 1
- **Symbol**:
- **Meaning**:

(Repeat the above structure for additional symbols)

## Characters
### Main Character(s)
#### Main Character 1
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Motivation**:

(Repeat the above structure for additional main characters)


### Supporting Characters
#### Character 1
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

(Repeat the above structure for additional supporting character)

</RESPONSE_TEMPLATE>

Of course, don't include the XML tags - those are just to indicate the example.
Also, the items in parenthesis are just to give you a better idea of what to write about, and should also be omitted from your response.
"""

CHAPTER_COUNT_PROMPT = """
<OUTLINE>
{_Summary}
</OUTLINE>

Please provide a JSON formatted response containing the total number of chapters in the above outline.

Respond with {{"TotalChapters": <total chapter count>}}
Please do not include any other text, just the JSON as your response will be parsed by a computer.
"""

INITIAL_OUTLINE_PROMPT = """
Please write a markdown formatted outline based on the following prompt:

<PROMPT>
{_OutlinePrompt}
</PROMPT>

<ELEMENTS>
{StoryElements}
</ELEMENTS>

As you write, remember to ask yourself the following questions:
    - What is the conflict?
    - Who are the characters (at least two characters)?
    - What do the characters mean to each other?
    - Where are we located?
    - What are the stakes (is it high, is it low, what is at stake here)?
    - What is the goal or solution to the conflict?

Don't answer these questions directly; instead, make your outline implicitly answer them. (Show, don't tell)

Please keep your outline clear as to what content is in what chapter.
Make sure to add lots of detail as you write.

Also, include information about the different characters and how they change over the course of the story.
We want to have rich and complex character development!"""

OUTLINE_REVISION_PROMPT = """
Please revise the following outline:
<OUTLINE>
{_Outline}
</OUTLINE>

Based on the following feedback:
<FEEDBACK>
{_Feedback}
</FEEDBACK>

Remember to expand upon your outline and add content to make it as best as it can be!

As you write, keep the following in mind:
    - What is the conflict?
    - Who are the characters (at least two characters)?
    - What do the characters mean to each other?
    - Where are we located?
    - What are the stakes (is it high, is it low, what is at stake here)?
    - What is the goal or solution to the conflict?

Please keep your outline clear as to what content is in what chapter.
Make sure to add lots of detail as you write.

Don't answer these questions directly; instead, make your writing implicitly answer them. (Show, don't tell)
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

Do NOT write the outline itself, just the extra context. Keep your responses short and in a bulleted list.
If no such context exists, respond with "No additional context found."
"""

EXPAND_OUTLINE_TO_MIN_CHAPTERS_PROMPT = """
You are a master story developer and editor. Your task is to revise a novel outline to meet a minimum chapter count.
The current outline is too short and needs to be expanded thoughtfully.

# CURRENT OUTLINE
---
{_Outline}
---

# TASK
Revise the outline so that it contains at least **{_MinChapters}** chapters.
Do NOT just split existing chapters. Instead, expand the story by:
- Developing subplots.
- Giving more space to character arcs.
- Adding new events or complications that are consistent with the story's theme and plot.
- Fleshing out the rising action, climax, or falling action with more detail and steps.

The goal is a richer, more detailed story that naturally fills the required number of chapters, not a stretched-out version of the original.
Your response should be the new, complete, chapter-by-chapter markdown outline.
"""

CHAPTER_OUTLINE_PROMPT = """
You are a master storyteller and outliner. Your task is to expand a single chapter from a high-level novel outline into a more detailed, scene-by-scene breakdown.

# FULL NOVEL OUTLINE
Here is the complete outline for the story, providing context for the chapter you are about to detail.
---
{_Outline}
---

# YOUR TASK
Now, focus *only* on **Chapter {_Chapter}** from the outline above.
Expand this single chapter into a detailed scene-by-scene outline.

For each scene, please provide:
- A clear heading (e.g., "Scene 1: The Ambush").
- A list of characters present.
- A description of the setting.
- A summary of the key events and actions that take place.
- Notes on character development or important dialogue beats.

Your output should be formatted in markdown and contain *only* the detailed outline for Chapter {_Chapter}. Do not re-state the full outline or add introductory text.
"""

# ======================================================================================
# Prompts for Chapter Generation Stages
# ======================================================================================

CHAPTER_GENERATION_INTRO = """You are a great fiction writer, working on a new novel. You are about to write a chapter based on an outline and the story so far. Pay close attention to the provided context to ensure continuity."""

CHAPTER_GENERATION_PROMPT = """
Please help me extract the part of this outline that is just for chapter {_ChapterNum}.

<OUTLINE>
{_Outline}
</OUTLINE>

Do not include anything else in your response except just the content for chapter {_ChapterNum}.
"""

# The following stage prompts are simplified by using a single context block.
CHAPTER_GENERATION_STAGE1 = """
# Context
Here is the context for the novel so far, including themes, motifs, and summaries of previous chapters. Use this to ensure your writing is coherent and flows logically from what has come before.
---
{narrative_context}
---

# Your Task
Write the PLOT for chapter {_ChapterNum} of {_TotalChapters}.
Base your writing on the following chapter outline. Your main goal is to establish the sequence of events.
It is imperative that your writing connects well with the previous chapter and flows into the next.

<CHAPTER_OUTLINE>
{ThisChapterOutline}
</CHAPTER_OUTLINE>

As you write, ensure you are implicitly addressing these questions about the plot:
- Pacing: Are you skipping days at a time? Don't summarize events; add scenes to detail them. Is the story rushing over certain plot points?
- Flow: Does the plot make logical sense? Does it follow a clear narrative structure?
- Genre: What is the genre? Does the plot support the genre?

{Feedback}"""

CHAPTER_GENERATION_STAGE2 = """
# Context
Here is the context for the novel so far. Use this to inform your writing.
---
{narrative_context}
---

# Your Task
Expand upon the provided chapter plot by adding CHARACTER DEVELOPMENT for chapter {_ChapterNum} of {_TotalChapters}.
Do not remove existing content; instead, enrich it with character thoughts, feelings, and motivations.

Here is what I have for the current chapter's plot:
<CHAPTER_PLOT>
{Stage1Chapter}
</CHAPTER_PLOT>

Expand on the work above, keeping these criteria in mind:
- Characters: Who are the characters in this chapter? What is the situation between them? Is there conflict or tension?
- Development: What are the goals of each character? Do they exhibit growth or change? Do their goals shift?
- Details: (Show, don't tell) Implicitly answer the questions above by weaving them into the narrative.

Remember, your goal is to enhance the character depth of the chapter.

{Feedback}"""

CHAPTER_GENERATION_STAGE3 = """
# Context
Here is the context for the novel so far. Use this to inform your writing.
---
{narrative_context}
---

# Your Task
Expand upon the provided chapter content by adding DIALOGUE for chapter {_ChapterNum} of {_TotalChapters}.
Do not remove existing content; instead, weave natural and purposeful conversations into the scenes.

Here's what I have so far for this chapter:
<CHAPTER_CONTENT>
{Stage2Chapter}
</CHAPTER_CONTENT>

As you add dialogue, keep the following in mind:
- Dialogue: Does the dialogue make sense for the situation and characters? Is its pacing appropriate for the scene (e.g., fast-paced during action, slow during a thoughtful moment)?
- Disruptions: If dialogue is disrupted, what is the cause? How does it affect the conversation?
- Purpose: Does the dialogue reveal character, advance the plot, or provide exposition?

Also, please remove any leftover headings or author notes from the text. Your output should be the clean, final chapter text.

{Feedback}"""

CHAPTER_GENERATION_STAGE4 = """
Please provide a final edit of the following chapter. Your goal is to polish the writing, ensuring it's seamless and ready for publication.
Do not summarize. Expand where needed to improve flow, but do not add major new plot points.

For your reference, here is the full story outline:
<OUTLINE>
{_Outline}
</OUTLINE>

And here is the chapter to tweak and improve:
<CHAPTER>
{Stage3Chapter}
</CHAPTER>

As you edit, focus on these criteria:
- Pacing and Flow: Smooth out transitions between scenes.
- Character Voice: Ensure character thoughts and dialogue are consistent.
- Description: Refine descriptions. Is the language too flowery or too plain?
- Consistency: Ensure the chapter aligns with the outline and the tone of the novel.

Remember to remove any author notes or non-chapter text.
"""

# ======================================================================================
# Prompts for Summarization and Coherence (NEW)
# ======================================================================================

SUMMARIZE_SCENE_PROMPT = """
Please analyze the following scene and provide a structured JSON response.

<SCENE_TEXT>
{scene_text}
</SCENE_TEXT>

Your response must be a single JSON object with two keys:
1. "summary": A concise paragraph summarizing the key events, character interactions, and setting of the scene.
2. "key_points_for_next_scene": A list of 2-4 bullet points identifying crucial pieces of information (e.g., unresolved conflicts, new character goals, important objects, lingering questions) that must be carried forward to ensure continuity in the next scene.

Example Response Format:
{{
  "summary": "In the dimly lit tavern, Kaelan confronts the mysterious informant, learning that the stolen artifact is not a mere trinket but a key to the city's ancient defenses. The informant slips away after a cryptic warning about a traitor in the city guard, leaving Kaelan with more questions than answers.",
  "key_points_for_next_scene": [
    "Kaelan now knows the artifact is a key.",
    "A traitor is suspected within the city guard.",
    "The informant's warning was cryptic and needs deciphering.",
    "Kaelan is left alone in the tavern, contemplating his next move."
  ]
}}

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

# ======================================================================================
# Prompts for Critique and Revision (NEW)
# ======================================================================================

CRITIQUE_CREATIVE_CONTENT_PROMPT = """
You are a literary editor providing feedback on a piece of writing for a novel.
Your goal is to provide specific, constructive criticism to help the author improve the piece, ensuring it aligns with the original creative vision.

# ORIGINAL USER PROMPT (The Source of Truth)
This is the core idea the author started with. All generated content should serve this vision.
---
{initial_user_prompt}
---

# CONTEXT OF THE STORY SO FAR
This is a summary of events that have been written so far.
---
{narrative_context_summary}
---

# TASK DESCRIPTION
The author was trying to accomplish the following with this piece of writing:
"{task_description}"

# TEXT TO CRITIQUE
---
{text_to_critique}
---

# YOUR INSTRUCTIONS
Please critique the "TEXT TO CRITIQUE" based on its adherence to the "ORIGINAL USER PROMPT", the task it was supposed to accomplish, and its coherence with the story's context.
Focus on:
- **Prompt Adherence:** Does the text honor the core ideas, characters, and constraints from the original user prompt?
- **Coherence:** Does it logically follow from the story context? Does it maintain character voice and plot continuity?
- **Task Fulfillment:** Did it successfully achieve the goal described in the "TASK DESCRIPTION"?
- **Quality:** Is the writing engaging? Is the pacing effective? Is there anything unclear or confusing?

Provide a few bullet points of direct, actionable feedback.
{is_json_output}
"""

REVISE_CREATIVE_CONTENT_BASED_ON_CRITIQUE_PROMPT = """
You are a master fiction writer tasked with revising a piece of text based on an editor's critique.

# ORIGINAL USER PROMPT (The Source of Truth)
Your revision MUST align with this core idea.
---
{initial_user_prompt}
---

# CONTEXT OF THE STORY SO FAR
This is the background for the story you are working on.
---
{narrative_context_summary}
---

# ORIGINAL TEXT
This was the first draft of the text.
---
{original_text}
---

# EDITOR'S CRITIQUE
Here is the feedback you must address in your revision.
---
{critique}
---

# YOUR TASK
Your goal is to rewrite the "ORIGINAL TEXT" to address the points raised in the "EDITOR'S CRITIQUE".
- You MUST stay true to the original text's purpose, as described here: "{task_description}".
- You MUST ensure your revision is strongly aligned with the "ORIGINAL USER PROMPT".
- You MUST incorporate the feedback from the critique.
- You MUST ensure the revised text is coherent with the story's context.

{json_instructions}
"""

# ======================================================================================
# Prompts for Legacy Revision and Checking
# ======================================================================================

CHAPTER_REVISION = """
Please revise the following chapter:

<CHAPTER_CONTENT>
{_Chapter}
</CHAPTER_CONTENT>

Based on the following feedback:
<FEEDBACK>
{_Feedback}
</FEEDBACK>

Do not reflect on the revisions; just write the improved chapter that addresses the feedback and prompt criteria.
Remember not to include any author notes.
"""

SUMMARY_CHECK_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
SUMMARY_CHECK_PROMPT = """
Please summarize the following chapter:

<CHAPTER>
{_Work}
</CHAPTER>

Do not include anything in your response except the summary."""
SUMMARY_OUTLINE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
SUMMARY_OUTLINE_PROMPT = """
Please summarize the following chapter outline:

<OUTLINE>
{_RefSummary}
</OUTLINE>

Do not include anything in your response except the summary."""
SUMMARY_COMPARE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
SUMMARY_COMPARE_PROMPT = """
Please compare the provided summary of a chapter and the associated outline, and indicate if the provided content roughly follows the outline.

Please write a JSON formatted response with no other content with the following keys.
Note that a computer is parsing this JSON so it must be correct.

<CHAPTER_SUMMARY>
{WorkSummary}
</CHAPTER_SUMMARY>

<OUTLINE>
{OutlineSummary}
</OUTLINE>

Please respond with the following JSON fields:

{{
"Suggestions": "str",
"DidFollowOutline": "true/false"
}}

Suggestions should include a string containing detailed markdown formatted feedback that will be used to prompt the writer on the next iteration of generation.
Specify general things that would help the writer remember what to do in the next iteration.
The writer is not aware of each iteration - so provide detailed information in the prompt that will help guide it.
Start your suggestions with 'Important things to keep in mind as you write: \\n'.

It's okay if the summary isn't a perfect match, but it should have roughly the same plot and pacing.

Again, remember to make your response JSON formatted with no extra words. It will be fed directly to a JSON parser.
"""
CRITIC_OUTLINE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
CRITIC_OUTLINE_PROMPT = """
Please critique the following outline - make sure to provide constructive criticism on how it can be improved and point out any problems with it.

<OUTLINE>
{_Outline}
</OUTLINE>

As you revise, consider the following criteria:
    - Pacing: Is the story rushing over certain plot points and excessively focusing on others?
    - Details: How are things described? Is it repetitive?
    - Flow: Does each chapter flow into the next? Does the plot make logical sense?
    - Genre: What is the genre? Do the scenes and tone support the genre?

Also, please check if the outline is written chapter-by-chapter, not in sections spanning multiple chapters or subsections.
It should be very clear which chapter is which, and the content in each chapter."""

OUTLINE_COMPLETE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
OUTLINE_COMPLETE_PROMPT = """
<OUTLINE>
{_Outline}
</OUTLINE>

Does this outline meet all of the following criteria?
    - Pacing: The story does not rush over important plot points or excessively focus on minor ones.
    - Flow: Chapters flow logically into each other with a clear and consistent narrative structure.
    - Genre: The tone and content of the outline clearly support a specific genre.

Give a JSON formatted response, containing the key \"IsComplete\" with a boolean value (true/false).
Please do not include any other text, just the JSON as your response will be parsed by a computer.
"""
JSON_PARSE_ERROR = "Please revise your JSON. It encountered the following error during parsing: {_Error}. Remember that your entire response is plugged directly into a JSON parser, so don't write **anything** except pure json."
CRITIC_CHAPTER_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
CRITIC_CHAPTER_PROMPT = """<CHAPTER>
{_Chapter}
</CHAPTER>

Please give feedback on the above chapter based on the following criteria:
    - Pacing & Flow: Is the pacing effective? Does the chapter connect well with an implied previous chapter?
    - Characterization: Are the characters believable? Is their dialogue and development effective?
    - Narrative Quality: Is the writing engaging? Is the plot advanced in a meaningful way?
"""
CHAPTER_COMPLETE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
CHAPTER_COMPLETE_PROMPT = """
<CHAPTER>
{_Chapter}
</CHAPTER>

Does this chapter meet the following criteria?
    - Pacing and Flow: The chapter is well-paced and flows logically.
    - Quality Writing: The chapter is engaging, detailed, and contributes effectively to the story.
    - Narrative Cohesion: The chapter feels like a complete and coherent part of a larger novel.

Give a JSON formatted response, containing the key \"IsComplete\", with a boolean value (true/false).
Please do not include any other text, just the JSON as your response will be parsed by a computer.
"""
CHAPTER_EDIT_PROMPT = """
You are a developmental editor performing a holistic edit on a chapter to ensure it fits perfectly within the novel.

# FULL STORY OUTLINE
For context, here is the master outline for the entire novel.
---
{_Outline}
---

# FULL TEXT OF OTHER CHAPTERS
Here is the text of the surrounding chapters. Use this to ensure seamless transitions, consistent character voice, and coherent plot progression.
---
{NovelText}
---

# CHAPTER TO EDIT
Now, please perform a detailed edit of the following chapter, Chapter {i}.
---
{_Chapter}
---

# YOUR TASK
Rewrite Chapter {i}. Improve its prose, pacing, dialogue, and character moments. Most importantly, ensure it aligns perfectly with the full story outline and connects seamlessly with the other chapters provided. Do not just summarize; perform a deep, line-by-line developmental edit. Output only the revised chapter text.
"""
CHAPTER_SCRUB_PROMPT = """
<CHAPTER>
{_Chapter}
</CHAPTER>

Given the above chapter, please clean it up so that it is ready to be published.
That is, please remove any leftover outlines, author notes, or editorial comments, leaving only the finished story text.

Do not comment on your task, as your output will be the final print version.
"""
STATS_PROMPT = """
Please write a JSON formatted response with no other content with the following keys.
Note that a computer is parsing this JSON so it must be correct.

Base your answers on the story written in previous messages.

{{
"Title": "a short title that's three to eight words",
"Summary": "a paragraph or two that summarizes the story from start to finish",
"Tags": "a string of tags separated by commas that describe the story",
"OverallRating": "your overall score for the story from 0-100"
}}

Again, remember to make your response JSON formatted with no extra words. It will be fed directly to a JSON parser.
"""

# ======================================================================================
# Prompts for Scene-by-Scene Generation
# ======================================================================================

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant."""
CHAPTER_TO_SCENES = """
# CONTEXT #
I am writing a story based on the high-level user prompt below. This is the ultimate source of truth for the story's direction.
<USER_PROMPT>
{_Prompt}
</USER_PROMPT>

Below is my overall novel outline, which was derived from the user prompt:
<OUTLINE>
{_Outline}
</OUTLINE>

# OBJECTIVE #
Create a scene-by-scene outline for the chapter detailed below.
This outline will be used to write the chapter, so be detailed. For each scene, describe what happens, its tone, the characters present, and the setting.
Crucially, ensure the scenes you design are directly inspired by and consistent with the original <USER_PROMPT>.

Here's the specific chapter outline that we need to split up into scenes:
<CHAPTER_OUTLINE>
{_ThisChapter}
</CHAPTER_OUTLINE>

# STYLE #
Provide a creative response that adds depth and plot to the story while still following the provided chapter outline and, most importantly, the original user prompt.
Format your response in markdown, with clear headings for each scene.

# RESPONSE #
Be detailed and well-formatted in your response, yet ensure you have a well-thought-out and creative output.
"""
SCENES_TO_JSON = """
# CONTEXT #
I need to convert the following scene-by-scene outline into a JSON formatted list of strings.
<SCENE_OUTLINE>
{_Scenes}
</SCENE_OUTLINE>

# OBJECTIVE #
Create a JSON list where each element in the list is a string containing the full markdown content for that scene.
Example:
[
    "## Scene 1: The Confrontation\\n- **Characters:** Kaelan, Informant\\n- **Setting:** The Rusty Flagon tavern\\n- **Events:** Kaelan meets the informant...",
    "## Scene 2: The Escape\\n- **Characters:** Kaelan\\n- **Setting:** The city streets\\n- **Events:** Kaelan is pursued by city guards..."
]

Do not include any other json fields; it must be a simple list of strings.

# STYLE #
Respond in pure, valid JSON.

# RESPONSE #
Do not lose any information from the original outline; just format it to fit into a JSON list of strings.
"""
SCENE_OUTLINE_TO_SCENE = """
# CONTEXT #
You are a creative writer. I need your help writing a full scene based on the scene outline below.
For context, here is a summary of the story and relevant events so far:
---
{narrative_context}
---

# OBJECTIVE #
Write a full, engaging scene based on the following scene outline.
Include dialogue, character actions, thoughts, and descriptions as appropriate to bring the scene to life.

<SCENE_OUTLINE>
{_SceneOutline}
</SCENE_OUTLINE>

# STYLE #
Your writing style should be creative and match the tone described in the scene outline. If no tone is specified, use your best judgment based on the events and character motivations. (Show, don't tell).

# RESPONSE #
Ensure your response is a well-thought-out and creative piece of writing that follows the provided scene outline and fits coherently into the larger story based on the context provided. Output only the scene's text.
"""
