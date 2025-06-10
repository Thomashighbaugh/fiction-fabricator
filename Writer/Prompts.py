# File: Writer/Prompts.py
# Purpose: Central repository for all optimized LLM prompt templates.

"""
Optimized LLM prompt templates for FictionFabricator.

This module contains meticulously crafted prompts designed to:
- Elicit high-quality, vivid, and human-like prose.
- Reduce redundancy and improve narrative coherence.
- Facilitate scene-by-scene generation with smooth transitions.
- Guide LLMs for effective outlining, context summarization, and revision.
- Address pacing and ensure focus on crucial plot points.

Each prompt is versioned implicitly by its content and the `OPTIMIZE_PROMPTS_VERSION`
in Config.py.
"""

# --- System Prompts ---
DEFAULT_SYSTEM_PROMPT: str = """
You are an expert creative writing assistant, recognized for your ability to craft vivid narratives, develop compelling characters, and ensure coherent plot progression. Your prose is engaging, sophisticated, and indistinguishable from that of a seasoned human author. You excel at maintaining consistent tone, pacing, and character voice throughout a story. You are also adept at understanding and following complex instructions for structuring and refining literary works.
"""

# --- Story Foundation Prompts ---
OPTIMIZED_STORY_ELEMENTS_GENERATION: str = """
Based on the user's story idea below, please generate a comprehensive set of story elements.
Your response must be in well-structured Markdown format.

**User's Story Idea:**
<UserStoryPrompt>
{_UserStoryPrompt}
</UserStoryPrompt>

**Required Story Elements (Provide rich, descriptive details for each):**

# Story Title:
(Suggest a compelling title)

## Genre:
- **Primary Genre**: (e.g., Science Fiction, Fantasy, Mystery)
- **Subgenre/Tropes**: (e.g., Space Opera, Urban Fantasy, Hardboiled Detective, Coming-of-Age)

## Core Themes:
- **Central Idea(s) or Message(s)**: (What underlying messages or questions does the story explore?)

## Target Pacing:
- **Overall Pace**: (e.g., Fast-paced with constant action, Deliberate and character-focused, Mix of slow-burn suspense and explosive climaxes)
- **Pacing Variation**: (How should pacing shift across the story's acts or key sequences?)

## Desired Writing Style:
- **Narrative Voice/Tone**: (e.g., Lyrical and introspective, Gritty and direct, Whimsical and humorous, Ominous and suspenseful)
- **Descriptive Language**: (e.g., Richly detailed environments, Focus on sensory experiences, Sparse and impactful)
- **Sentence Structure & Vocabulary**: (e.g., Complex and varied, Short and punchy, Evocative and literary)

## Plot Synopsis (Five-Act Structure preferred):
- **Exposition**: (Introduction of main characters, setting, initial conflict/inciting incident)
- **Rising Action**: (Series of events escalating conflict, developing characters, building tension)
- **Climax**: (The turning point, highest tension, where the main conflict comes to a head)
- **Falling Action**: (Immediate consequences of the climax, tying up subplots)
- **Resolution**: (The new normal, lingering questions, thematic takeaways)

## Setting(s):
(Describe at least one primary setting in detail. Add more if central to the plot.)
### Setting 1: [Name of Setting]
- **Time Period**: (e.g., Distant future, Alternate present, Specific historical era)
- **Location Details**: (e.g., A decaying megacity on Mars, A hidden magical academy in modern London, A remote, storm-swept island)
- **Culture & Society**: (Key cultural norms, societal structure, technology level, belief systems)
- **Atmosphere & Mood**: (The dominant feeling the setting should evoke: e.g., oppressive, wondrous, dangerous, melancholic)

## Primary Conflict:
- **Type**: (e.g., Character vs. Character, Character vs. Society, Character vs. Nature, Character vs. Self, Character vs. Technology/Supernatural)
- **Detailed Description**: (What is the central struggle? Who are the opposing forces? What are the stakes?)

## Key Symbolism (Optional, but encouraged):
### Symbol 1:
- **Symbol**: (The object, concept, or character)
- **Intended Meaning/Representation**: (What deeper ideas does it represent?)

## Characters:
### Main Character 1:
- **Name**:
- **Archetype/Role**: (e.g., The Reluctant Hero, The Mentor, The Anti-Hero)
- **Physical Description**: (Distinctive features, general appearance, style)
- **Personality Traits**: (Key positive and negative traits, quirks, fears, desires)
- **Background/History**: (Relevant past experiences shaping them)
- **Motivations & Goals**: (What drives them through the story?)
- **Internal Conflict**: (Their primary inner struggle)
- **Potential Character Arc**: (How might they change or grow?)

(Repeat for other Main Characters if any)

### Supporting Character 1 (Example - provide 3-5 key supporting characters):
- **Name**:
- **Relationship to Main Character(s)**:
- **Role in Story**: (e.g., Ally, Antagonist, Foil, Comic Relief, Catalyst)
- **Brief Description**: (Key traits, appearance, motivation)

Ensure your output is detailed, imaginative, and provides a strong foundation for a compelling narrative. Avoid generic descriptions; aim for unique and memorable elements.
"""

OPTIMIZED_OVERALL_OUTLINE_GENERATION: str = """
Based on the user's story idea and the detailed story elements provided, generate a chapter-by-chapter plot outline for a novel.
The outline should be engaging, well-paced, and clearly delineate the narrative progression for each chapter.

**User's Story Idea:**
<UserStoryPrompt>
{_UserStoryPrompt}
</UserStoryPrompt>

**Detailed Story Elements:**
<StoryElementsMarkdown>
{_StoryElementsMarkdown}
</StoryElementsMarkdown>

**Instructions for the Outline:**
1.  **Structure**: Present the outline as a list of chapters (e.g., "Chapter 1: [Chapter Title/Theme]", "Chapter 2: [Chapter Title/Theme]", etc.).
2.  **Content per Chapter**: For each chapter, provide a concise summary (3-5 sentences) covering:
    *   Key plot events that occur.
    *   Significant character actions, decisions, or development.
    *   How the chapter contributes to the overall plot and themes.
    *   The intended pacing and tone for the chapter (e.g., "Builds suspense leading to a minor confrontation," "Focuses on character introspection after a major loss").
    *   A clear hook or transition into the next chapter.
3.  **Narrative Arc**: Ensure the outline follows a clear narrative arc (e.g., five-act structure if specified in elements, or a similar logical progression). Pay attention to the exposition, rising action, climax, falling action, and resolution across the chapters.
4.  **Pacing**: Distribute plot points effectively to maintain reader engagement. Vary pacing as appropriate for the story's needs.
5.  **Character Development**: Show, through chapter events, how main characters evolve, face challenges, and pursue their goals.
6.  **Cohesion**: Ensure chapters flow logically from one to the next, building upon previous events.
7.  **Vividness**: Even in summary form, use evocative language to hint at the story's atmosphere and potential.

Output the entire outline in Markdown format.
"""

# --- Scene-Level Prompts ---
OPTIMIZED_CHAPTER_TO_SCENES_BREAKDOWN: str = """
You are tasked with breaking down a chapter's plot outline into a sequence of distinct, detailed scenes.
This will serve as a blueprint for writing the chapter. Your output MUST be a single, valid JSON object that conforms to the `SceneOutlinesList` Pydantic model.

**Overall Story Outline (for context):**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Plot Outline for Chapter {_ChapterNumber}:**
<ChapterPlotOutline>
{_ChapterPlotOutline}
</ChapterPlotOutline>

**Context from Previous Chapter (if applicable):**
<PreviousChapterContextSummary>
{_PreviousChapterContextSummary}
</PreviousChapterContextSummary>

**Base Story Context (if any user instructions apply globally):**
<BaseStoryContext>
{_BaseStoryContext}
</BaseStoryContext>

**Instructions:**
Generate a JSON object with a single key "scenes" which contains a list of scene objects. Each scene object must include all the keys from the `SceneOutline` Pydantic model:
-   `scene_number_in_chapter` (int)
-   `scene_title` (str)
-   `setting_description` (str)
-   `characters_present` (List[str])
-   `character_goals_moods` (str)
-   `key_events_actions` (List[str])
-   `dialogue_points` (List[str])
-   `pacing_note` (str)
-   `tone` (str)
-   `purpose_in_chapter` (str)
-   `transition_out_hook` (str)

**CRITICAL RULE: All string values in the JSON must be valid JSON strings. DO NOT use Python-style string concatenation (e.g., `'text' + 'more text'`) or unescaped characters within the strings.**

Ensure a minimum of {SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER} scenes are outlined. Be creative and add depth.
Output ONLY the JSON object. Do not include any other text, narration, or markdown formatting.
"""

OPTIMIZED_SCENE_NARRATIVE_GENERATION: str = """
Your task is to write a compelling and vivid narrative for the scene detailed below.
Adhere closely to the provided blueprint, ensuring the scene is engaging, well-paced, and contributes effectively to the story.

**Overall Story Context (abbreviated):**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Immediate Previous Context (from last scene/chapter end):**
<PreviousSceneContextSummary>
{_PreviousSceneContextSummary}
</PreviousSceneContextSummary>

**Base Story Context (if any user instructions apply globally):**
<BaseStoryContext>
{_BaseStoryContext}
</BaseStoryContext>

**Current Chapter:** {_ChapterNumber}
**Scene Number in Chapter:** {_SceneNumberInChapter}

**Scene Blueprint:**
-   **Title**: "{_SceneTitle}"
-   **Setting**: {_SceneSettingDescription}
-   **Characters Present & Their Immediate State**: {_SceneCharactersPresentAndGoals}
-   **Key Events/Actions to Depict**: {_SceneKeyEvents}
-   **Essential Dialogue Points/Topics**: {_SceneDialogueHighlights}
-   **Intended Pacing**: {_ScenePacingNote}
-   **Dominant Tone**: {_SceneTone}
-   **Scene's Purpose**: {_ScenePurposeInChapter}
-   **Concluding Hook/Transition**: {_SceneTransitionOutHook}

**Writing Instructions:**
1.  **Immersive Setting**: Bring the setting to life with vivid sensory details.
2.  **Character Actions & Voice**: Ensure character actions and dialogue are distinctive and logical.
3.  **Integrate Key Elements**: Naturally weave the specified "Key Events/Actions" and "Dialogue Points" into the narrative.
4.  **Pacing and Tone**: Masterfully control the pacing and maintain the specified tone.
5.  **Show, Don't Tell**: Use actions, dialogue, and descriptions to convey information and emotion.
6.  **Prose Quality**: Employ rich vocabulary and varied sentence structures. Avoid clichés.
7.  **Dialogue Craft**: Dialogue must be realistic, reveal character, and advance the plot.
8.  **Smooth Transitions**: Conclude the scene by fulfilling the "Concluding Hook/Transition".
9.  **Length**: Aim for a substantial scene, typically {SCENE_NARRATIVE_MIN_WORDS} words or more.

Produce ONLY the narrative text for this single scene. Do not include titles, author notes, or any meta-commentary.
"""

# --- Context and Transition Prompts ---
OPTIMIZED_PREVIOUS_CHAPTER_SUMMARY_FOR_CONTEXT: str = """
Analyze the provided text of a completed chapter and the overall story outline.
Generate a concise yet comprehensive summary focusing *only* on elements crucial for writing the *immediately following* chapter.

**Completed Chapter Text (Chapter {_ChapterNumberOfCompletedChapter}):**
<CompletedChapterText>
{_CompletedChapterText}
</CompletedChapterText>

**Overall Story Outline (for broader context):**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Your summary should highlight:**
1.  **Key Plot Advancements**: What major events occurred and what are their direct consequences leading into the next chapter?
2.  **Character States at Chapter End**: What is the emotional, physical, and situational state of the main characters as this chapter concludes?
3.  **Unresolved Threads/New Questions**: What immediate conflicts, mysteries, or questions are left open that the next chapter might address?
4.  **Thematic Resonance**: Briefly note any thematic elements that were strongly emphasized.
5.  **Concluding Tone & Pacing**: What was the feeling and speed of the narrative at the very end of this chapter?

This summary's purpose is to ensure seamless continuity. Be specific and actionable.
"""

OPTIMIZED_PREVIOUS_SCENE_SUMMARY_FOR_CONTEXT: str = """
Analyze the provided text of a completed scene and its original outline.
Generate a very brief summary (1-2 sentences) focusing *only* on the critical information needed to write the *immediately following scene* within the same chapter.

**Completed Scene Text:**
<CompletedSceneText>
{_CompletedSceneText}
</CompletedSceneText>

**Outline of the Completed Scene (for reference):**
<CurrentSceneOutline>
{_CurrentSceneOutline}
</CurrentSceneOutline>

**Your brief summary should capture:**
1.  **Final Action/Dialogue**: The last significant thing that happened or was said.
2.  **Immediate Character State/Decision**: The most relevant character's disposition or choice at the scene's close.
3.  **Direct Hook/Setup**: Any explicit setup or unresolved micro-tension for the next scene.
"""

# --- Feedback, Revision, and Evaluation Prompts ---
OPTIMIZED_CRITIC_OUTLINE_PROMPT: str = """
You are a discerning editor. Provide a constructive critique of the following story outline. Your feedback should be actionable and aim to elevate its quality.

<OUTLINE>
{_Outline}
</OUTLINE>

**Evaluate based on these criteria, providing specific examples:**
1.  **Plot Cohesion & Clarity**: Is the plot logical? Are there inconsistencies? Is the central conflict compelling?
2.  **Pacing & Structure**: Does the pacing seem appropriate? Are key events well-developed? Is the structure balanced?
3.  **Chapter Flow & Transitions**: Do chapters connect logically and build momentum?
4.  **Character Arcs & Development**: Are character goals, motivations, and arcs clear and engaging?
5.  **Originality & Engagement**: Is the story fresh and engaging? Are the stakes compelling?

**Format your feedback:**
-   Start with an overall assessment.
-   Provide specific, constructive points of critique.
-   Offer concrete suggestions for improvement.
"""

OPTIMIZED_CRITIC_CHAPTER_PROMPT: str = """
You are an experienced manuscript editor. Provide a detailed and constructive critique of the following chapter text.

**Chapter Text:**
<CHAPTER_TEXT>
{_ChapterText}
</CHAPTER_TEXT>

**Overall Story Outline (for context):**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Critique the chapter based on the following, with specific examples:**
1.  **Prose Quality & Style**: Clarity, vividness, word choice, sentence fluency, and tone.
2.  **Pacing & Flow**: Pacing within the chapter and transitions between scenes.
3.  **Characterization & Dialogue**: Consistency, depth, and naturalness of dialogue.
4.  **Plot & Structure**: Purpose of scenes, handling of conflict/tension, and alignment with the overall outline.
5.  **Reader Engagement**: Immersion and emotional impact.

**Structure your feedback:**
-   Begin with a general impression.
-   Address each criterion with specific, actionable points.
-   Conclude with 2-3 key recommendations for revision.
"""

OUTLINE_REVISION_PROMPT: str = """
Revise and enhance the following story outline based on the provided feedback. Your goal is to produce a stronger, more compelling outline that addresses all critiques.

**Original Outline:**
<OUTLINE>
{_Outline}
</OUTLINE>

**Feedback for Revision:**
<FEEDBACK>
{_Feedback}
</FEEDBACK>

**Instructions for Revision:**
1.  Incorporate the suggestions to improve plot cohesion, pacing, character arcs, and chapter flow.
2.  Add more detail where requested or restructure sections as needed.
3.  Ensure the revised outline is a complete, standalone version.

Output the complete revised outline in Markdown format.
"""

CHAPTER_REVISION_PROMPT: str = """
Revise the following chapter text based on the provided editorial feedback. Your aim is to significantly improve the chapter's quality by addressing all points of critique.

**Original Chapter Text:**
<CHAPTER_CONTENT>
{_Chapter}
</CHAPTER_CONTENT>

**Editorial Feedback for Revision:**
<FEEDBACK>
{_Feedback}
</FEEDBACK>

**Instructions for Revision:**
1.  Thoroughly review the feedback and apply the suggested changes.
2.  Rewrite, expand, or condense sections as needed to address issues with prose, pacing, dialogue, and plot.
3.  Focus on "showing" rather than "telling."
4.  The output should be the complete, revised chapter text.

Do not reflect on the revisions or include any author notes. Just provide the improved chapter.
"""

# --- Evaluation & Utility Prompts ---
OUTLINE_COMPLETE_PROMPT: str = """
Analyze the story outline below. Determine if it meets a high standard of quality for plot, pacing, structure, and character development.

<OUTLINE>
{_Outline}
</OUTLINE>

Respond with a JSON object containing a single key "IsComplete" with a boolean value (true/false).
-   `true`: if the outline is well-structured and ready for detailed scene outlining.
-   `false`: if the outline has significant flaws and requires revision.

**Example Response:**
`{{"IsComplete": true}}`

Provide ONLY the JSON response.
"""

CHAPTER_COMPLETE_PROMPT: str = """
Analyze the chapter text below. Determine if it meets a publishable standard for prose, pacing, characterization, and plot advancement.

<CHAPTER>
{_Chapter}
</CHAPTER>

Respond with a JSON object containing a single key "IsComplete" with a boolean value (true/false).
-   `true`: if the chapter is well-written and generally ready.
-   `false`: if the chapter has notable issues and needs revision.

**Example Response:**
`{{"IsComplete": false}}`

Provide ONLY the JSON response.
"""

CHAPTER_COUNT_PROMPT: str = """
Analyze the provided story outline below.
<OUTLINE>
{_Outline}
</OUTLINE>

Based on the structure and headings (e.g., "Chapter 1", "## Chapter Two"), determine the total number of distinct chapters.
Respond with a JSON object containing a single key "TotalChapters" with an integer value.

**Example Response:**
`{{"TotalChapters": 12}}`

If the outline is unclear, return 0. Provide ONLY the JSON response.
"""

GET_IMPORTANT_BASE_PROMPT_INFO: str = """
Review the user's story prompt below.
<USER_PROMPT>
{_Prompt}
</USER_PROMPT>

Extract any specific instructions, constraints, or stylistic visions that are important for the writing process but are not part of the core plot idea.
This includes:
-   Desired length or word count.
-   Specific "do's" or "don'ts" regarding content or style.
-   Information about the target audience.
-   Any meta-instructions about how the AI should behave.

Present these points as a Markdown list under the heading "# Important Additional Context".
If none are found, respond with "# Important Additional Context\n- None found."
Do NOT summarize the plot. Focus only on auxiliary instructions. Be concise.
"""

JSON_PARSE_ERROR: str = """
Your previous response was expected to be a valid JSON object but could not be parsed.
**Original Text with Error:**
<ORIGINAL_TEXT>
{_OriginalText}
</ORIGINAL_TEXT>

**Error Message:**
<ERROR_MESSAGE>
{_Error}
</ERROR_MESSAGE>

Please correct the original text to produce a single, valid JSON object that conforms to the requested schema. Pay close attention to syntax errors like missing commas, incorrect quoting, or unescaped characters.
Provide ONLY the corrected, valid JSON object as your entire response.
"""

# --- Specialized Prompts ---
GLOBAL_NOVEL_CHAPTER_EDIT_PROMPT: str = """
You are performing a global consistency and flow edit on Chapter {ChapterNum} of a novel.
Consider this chapter within the context of the overall story outline and the text of all preceding chapters.

**Overall Story Outline:**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Novel Text Leading Up To This Chapter:**
<NovelTextSoFar>
{_NovelTextSoFar}
</NovelTextSoFar>

**Current Chapter {ChapterNum} for Editing:**
<ChapterTextToEdit>
{_ChapterTextToEdit}
</ChapterTextToEdit>

**Editing Focus:**
1.  **Continuity**: Ensure events, character knowledge, and facts are consistent with previous chapters.
2.  **Foreshadowing/Payoff**: Subtly enhance setup or resolution of plot points.
3.  **Pacing within Global Arc**: Adjust the chapter's pacing to fit the novel's overall rhythm.
4.  **Thematic Resonance**: Strengthen thematic connections to the broader story.
5.  **Character Arc Progression**: Ensure character actions are a logical step in their overall development.

**Instructions:**
-   Make surgical edits rather than wholesale rewrites. Preserve the core plot.
-   Your output should be ONLY the revised text of Chapter {ChapterNum}.
"""

CHAPTER_SCRUB_PROMPT: str = """
Review the following chapter text.
<CHAPTER>
{_Chapter}
</CHAPTER>

Your task is to meticulously clean this text for final publication.
1.  Remove any leftover author notes, editorial comments, or bracketed instructions.
2.  Delete any headings or outline markers not part of the narrative.
3.  Ensure consistent formatting and correct obvious typos.

The goal is to produce pure, clean narrative text. Do not change the story content itself.
Output ONLY the cleaned chapter text.
"""

STATS_PROMPT: str = """
Analyze the complete story context. Generate a JSON object that conforms to the `StoryMetadata` Pydantic model with the following information: "Title", "Summary", "Tags", and "OverallRating".

Ensure your response is ONLY this JSON object.
"""

TRANSLATE_PROMPT: str = """
Translate the following text into {_Language}.
Convey the original meaning and tone accurately and naturally. Do not add commentary.

<TEXT_TO_TRANSLATE>
{_Prompt}
</TEXT_TO_TRANSLATE>

Translated text:
"""

CHAPTER_TRANSLATE_PROMPT: str = """
Translate the following story chapter into {_Language}.
Preserve the narrative style, character voices, and emotional tone.

<CHAPTER_TEXT>
{_Chapter}
</CHAPTER_TEXT>

Translated Chapter Text in {_Language}:
"""

FALLBACK_CHAPTER_PLOT_GENERATION_PROMPT: str = """
The main story outline is provided below. Chapter {ChapterNum} out of {TotalChapters} has a missing plot description.
Generate a concise, plausible plot summary (2-4 sentences) for Chapter {ChapterNum} that fits logically within the narrative flow, considering the base story context.

**Overall Story Outline:**
<OverallStoryOutline>
{OverallStoryOutline}
</OverallStoryOutline>

**Base Story Context/Instructions (if any):**
<BaseStoryContext>
{BaseStoryContext}
</BaseStoryContext>

Provide ONLY the plot summary for Chapter {ChapterNum}.
"""