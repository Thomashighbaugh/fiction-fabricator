# File: AIStoryWriter/Writer/Prompts.py
# Purpose: Central repository for all optimized LLM prompt templates.

"""
Optimized LLM prompt templates for AIStoryWriter.

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
This will serve as a blueprint for writing the chapter.

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

**Instructions:**
Generate a JSON list where each element is an object representing a single scene. Each scene object must include the following keys:
-   `"scene_number_in_chapter"`: (Integer) e.g., 1, 2, 3.
-   `"scene_title"`: (String) A brief, evocative title for the scene.
-   `"setting_description"`: (String) Detailed description of the location, time of day, and prevailing atmosphere (e.g., "A dimly lit, rain-slicked alleyway at midnight, smelling of refuse and despair. The only light comes from a flickering neon sign.").
-   `"characters_present"`: (List of Strings) Names of characters actively participating in this scene.
-   `"character_goals_moods"`: (String) Brief description of what each key character present wants to achieve or their emotional state at the start of the scene.
-   `"key_events_actions"`: (List of Strings) Bullet points describing the critical plot developments, actions, or discoveries that *must* occur in this scene. Be specific.
-   `"dialogue_points"`: (List of Strings) Key topics of conversation or specific impactful lines of dialogue that should be included.
-   `"pacing_note"`: (String) Suggested pacing for the scene (e.g., "Fast-paced action sequence," "Slow, tense dialogue exchange," "Quick, transitional scene," "Introspective and reflective").
-   `"tone"`: (String) The dominant emotional tone the scene should convey (e.g., "Suspenseful," "Romantic," "Tragic," "Hopeful," "Humorous").
-   `"purpose_in_chapter"`: (String) How this scene specifically contributes to the chapter's overall objectives (e.g., "Introduces a new obstacle," "Reveals a character's hidden motive," "Escalates the central conflict of the chapter").
-   `"transition_out_hook"`: (String) How the scene should end to effectively lead into the next scene or provide a minor cliffhanger/point of reflection if it's the chapter's end.

Ensure a minimum of {SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER} scenes are outlined for this chapter. The scenes should logically progress the chapter's plot as described in its outline. Be creative and add depth.

**Output ONLY the JSON list of scene objects.** Do not include any other text, narration, or markdown formatting outside the JSON structure.
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
1.  **Immersive Setting**: Bring the setting to life with vivid sensory details (sight, sound, smell, touch, taste where appropriate). Establish the atmosphere effectively.
2.  **Character Actions & Voice**: Ensure character actions are logical and their dialogue is distinctive, reflecting their personalities, motivations, and current emotional states as per the blueprint.
3.  **Integrate Key Elements**: Naturally weave the specified "Key Events/Actions" and "Dialogue Points" into the narrative. These are mandatory plot beats.
4.  **Pacing and Tone**: Masterfully control the pacing and maintain the specified tone throughout the scene. Use sentence structure, description length, and action/dialogue balance to achieve this.
5.  **Show, Don't Tell**: Use actions, dialogue, internal thoughts (if POV allows), and descriptions to convey information and emotion, rather than stating it directly.
6.  **Prose Quality**: Employ rich vocabulary, varied sentence structures, and strong verbs. Strive for human-like, engaging, and descriptive prose. Avoid clichés and filler words.
7.  **Dialogue Craft**: Dialogue should be realistic for the characters and situation, reveal character, and advance the plot or develop relationships.
8.  **Smooth Transitions**: Conclude the scene by fulfilling the "Concluding Hook/Transition" to ensure a natural flow to what comes next.
9.  **Length**: Aim for a substantial scene, typically {SCENE_NARRATIVE_MIN_WORDS} words or more, unless the "Pacing_Note" suggests a very brief scene.

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
2.  **Character States at Chapter End**: What is the emotional, physical, and situational state of the main characters as this chapter concludes? Note any significant decisions made or changes they underwent.
3.  **Unresolved Threads/New Questions**: What immediate conflicts, mysteries, or questions are left open that the next chapter might address?
4.  **Thematic Resonance**: Briefly note any thematic elements that were strongly emphasized and might carry over.
5.  **Concluding Tone & Pacing**: What was the feeling and speed of the narrative at the very end of this chapter?

This summary's purpose is to ensure seamless continuity and narrative cohesion for the writer of the next chapter. Be specific and actionable.
Avoid re-telling the entire chapter; focus on the "hand-off" points.
"""

OPTIMIZED_PREVIOUS_SCENE_SUMMARY_FOR_CONTEXT: str = """
Analyze the provided text of a completed scene and its original outline.
Generate a very brief summary focusing *only* on the critical information needed to write the *immediately following scene* within the same chapter.

**Completed Scene Text:**
<CompletedSceneText>
{_CompletedSceneText}
</CompletedSceneText>

**Outline of the Completed Scene (for reference of its goals):**
<CurrentSceneOutline>
{_CurrentSceneOutline}
</CurrentSceneOutline>

**Your brief summary should capture:**
1.  **Final Action/Dialogue**: The last significant thing that happened or was said.
2.  **Immediate Character State/Decision**: The most relevant character's immediate disposition or choice at the scene's close.
3.  **Direct Hook/Setup**: Any explicit setup or unresolved micro-tension that the next scene is expected to pick up on.

This is for ultra-short-term continuity. Be extremely concise (1-2 sentences).
"""

# --- Feedback, Revision, and Evaluation Prompts ---
OPTIMIZED_CRITIC_OUTLINE_PROMPT: str = """
You are a discerning editor. Please provide a constructive critique of the following story outline.
Your feedback should be actionable and aim to elevate the outline's quality.

<OUTLINE>
{_Outline}
</OUTLINE>

**Evaluate the outline based on these criteria, providing specific examples where possible:**
1.  **Plot Cohesion & Clarity**:
    *   Is the overall plot logical and easy to follow?
    *   Are there any apparent plot holes, inconsistencies, or unresolved threads?
    *   Is the central conflict compelling and well-developed throughout the chapters?
2.  **Pacing & Structure**:
    *   Does the pacing seem appropriate for the story's genre and themes? Are key events given adequate development time?
    *   Are there sections that might feel rushed or dragged out?
    *   Does the distribution of exposition, rising action, climax, falling action, and resolution across chapters feel balanced and effective?
3.  **Chapter Flow & Transitions**:
    *   Do the chapter summaries suggest smooth and logical transitions from one chapter to the next?
    *   Does each chapter build effectively on the previous one?
4.  **Character Arcs & Development**:
    *   Are the main characters' goals, motivations, and potential arcs clear and engaging?
    *   Does the outline provide sufficient opportunities for meaningful character development?
5.  **Originality & Engagement**:
    *   Does the outline promise a fresh and engaging story, or does it rely heavily on predictable tropes without a unique spin?
    *   Are the stakes clear and compelling?
6.  **World-Building & Setting Integration** (if applicable):
    *   Is the setting well-integrated into the plot, or does it feel like a backdrop?
    *   Are unique aspects of the world effectively utilized in the chapter events?

**Format your feedback:**
-   Start with an overall assessment.
-   Then, provide specific points of critique, ideally referencing chapter numbers or specific plot points.
-   Offer concrete suggestions for improvement.
Maintain a professional and constructive tone.
"""

OPTIMIZED_CRITIC_CHAPTER_PROMPT: str = """
You are an experienced manuscript editor. Please provide a detailed and constructive critique of the following chapter text.
Your goal is to help the author improve its quality significantly.

**Chapter Text:**
<CHAPTER_TEXT>
{_ChapterText}
</CHAPTER_TEXT>

**Overall Story Outline (for context on the chapter's role):**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Critique the chapter based on the following aspects, providing specific examples from the text:**

1.  **Prose Quality & Style**:
    *   **Clarity & Conciseness**: Is the language clear? Are there run-on sentences, awkward phrasing, or unnecessary jargon?
    *   **Vividness & Imagery**: Does the writing create strong mental images? Is sensory detail used effectively? (Show, don't tell).
    *   **Word Choice**: Is the vocabulary precise, evocative, and appropriate for the tone? Are there repetitive words or phrases?
    *   **Sentence Fluency**: Do sentences flow well? Is there good variation in sentence structure and length?
    *   **Voice & Tone**: Is the narrative voice consistent and engaging? Does the tone match the chapter's content and intent?

2.  **Pacing & Flow**:
    *   **Intra-Chapter Pacing**: Does the pacing within the chapter feel right? Do scenes speed up or slow down appropriately?
    *   **Scene Transitions**: If the chapter contains multiple scenes, do they transition smoothly?
    *   **Overall Contribution**: Does this chapter advance the plot at an appropriate rate for its place in the story?

3.  **Characterization & Dialogue**:
    *   **Consistency**: Do characters behave and speak in ways consistent with their established personalities and motivations?
    *   **Depth**: Are characters (especially the POV character, if any) portrayed with believable thoughts and emotions?
    *   **Dialogue**: Is the dialogue natural, engaging, and purposeful? Does it reveal character, advance plot, or build tension? Does each character have a distinct voice?

4.  **Plot & Structure (within the chapter)**:
    *   **Scene Purpose**: Does each scene (if discernible) have a clear purpose?
    *   **Conflict & Tension**: Is there sufficient conflict or tension to keep the reader engaged? Is it resolved or escalated effectively within the chapter?
    *   **Alignment with Outline**: Does the chapter generally follow its intended purpose as per the overall story outline?

5.  **Reader Engagement**:
    *   **Immersion**: Does the chapter draw the reader into the story?
    *   **Emotional Impact**: Does it evoke the intended emotions?

**Structure your feedback:**
-   Begin with a general impression.
-   Address each criterion above with specific, actionable points. Quote short snippets from the text to illustrate your points where helpful.
-   Conclude with 2-3 key recommendations for revision.
Your tone should be professional, encouraging, and focused on tangible improvements.
"""

OUTLINE_REVISION_PROMPT: str = """
Please revise and enhance the following story outline based on the provided feedback.
Your goal is to address the critique and produce a stronger, more compelling outline.

**Original Outline:**
<OUTLINE>
{_Outline}
</OUTLINE>

**Feedback for Revision:**
<FEEDBACK>
{_Feedback}
</FEEDBACK>

**Instructions for Revision:**
1.  Carefully consider each point in the feedback.
2.  Incorporate the suggestions to improve plot cohesion, pacing, character arcs, and chapter flow.
3.  Add more detail where requested, or restructure sections as needed to address critiques.
4.  Expand upon existing ideas to add depth and originality if the feedback points to weaknesses there.
5.  Ensure the revised outline maintains a clear chapter-by-chapter structure with concise summaries for each, highlighting key events, character development, and transitions.
6.  The revised outline should be a complete, standalone version that supersedes the original.

As you revise, remember the core elements of good storytelling:
-   Compelling conflict.
-   Well-motivated characters with clear arcs.
-   Logical plot progression with appropriate pacing.
-   Engaging setting and atmosphere.
-   Smooth transitions between narrative segments.

Output the complete revised outline in Markdown format.
"""

CHAPTER_REVISION_PROMPT: str = """
Please revise the following chapter text based on the provided editorial feedback.
Your aim is to significantly improve the chapter's quality by addressing all points of critique.

**Original Chapter Text:**
<CHAPTER_CONTENT>
{_Chapter}
</CHAPTER_CONTENT>

**Editorial Feedback for Revision:**
<FEEDBACK>
{_Feedback}
</FEEDBACK>

**Instructions for Revision:**
1.  Thoroughly review the feedback, paying close attention to specific examples and suggestions.
2.  Rewrite, expand, or condense sections of the chapter as needed to address issues related to prose quality, pacing, characterization, dialogue, plot development, and engagement.
3.  Focus on "showing" rather than "telling," using vivid descriptions and actions.
4.  Ensure dialogue is natural, purposeful, and character-specific.
5.  Improve sentence flow, word choice, and eliminate redundancy.
6.  Strengthen transitions between scenes or paragraphs if weaknesses were noted.
7.  Do not simply make minor edits; undertake substantial revisions where the feedback indicates necessity.
8.  The output should be the complete, revised chapter text, ready for further review.

Do not reflect on the revisions or include any author notes. Just provide the improved chapter.
"""

# --- Evaluation & Utility Prompts ---
OUTLINE_COMPLETE_PROMPT: str = """
Analyze the following story outline.
<OUTLINE>
{_Outline}
</OUTLINE>

Based on your understanding of a well-structured and comprehensive story outline, determine if this outline meets a high standard of quality across the following criteria:
-   **Plot Cohesion & Clarity**: The plot is logical, clear, and engaging.
-   **Pacing & Structure**: The story's pacing and structural divisions (e.g., acts, chapter progression) are well-considered and effective.
-   **Chapter Flow & Transitions**: Chapters connect logically, and the narrative progresses smoothly.
-   **Character Arc Potential**: Main characters have clear motivations and opportunities for development.
-   **Detail & Sufficiency**: The outline provides enough detail per chapter to guide scene breakdown and writing.

Respond with a JSON object containing a single key "IsComplete" with a boolean value (true or false).
-   `true`: if the outline is largely complete, well-structured, and ready for detailed scene outlining.
-   `false`: if the outline has significant flaws in the criteria above and requires further revision.

**Example Response:**
`{{"IsComplete": true}}`

Provide ONLY the JSON response.
"""

CHAPTER_COMPLETE_PROMPT: str = """
Analyze the following chapter text.
<CHAPTER>
{_Chapter}
</CHAPTER>

Based on your understanding of high-quality fiction writing, determine if this chapter meets a publishable standard across these criteria:
-   **Prose Quality**: The writing is vivid, clear, engaging, and largely free of grammatical errors or awkward phrasing.
-   **Pacing & Flow**: The chapter is well-paced, and scenes/paragraphs transition smoothly.
-   **Characterization & Dialogue**: Characters are consistent and believable; dialogue is natural and purposeful.
-   **Plot Advancement**: The chapter effectively moves the plot forward according to its likely role in a larger narrative.
-   **Engagement**: The chapter is interesting and successfully evokes the intended mood/emotions.

Respond with a JSON object containing a single key "IsComplete" with a boolean value (true or false).
-   `true`: if the chapter is well-written and generally ready.
-   `false`: if the chapter has notable issues in the criteria above and needs revision.

**Example Response:**
`{{"IsComplete": false}}`

Provide ONLY the JSON response.
"""

CHAPTER_COUNT_PROMPT: str = """
Analyze the provided story outline below.
<OUTLINE>
{_Outline}
</OUTLINE>

Based on the structure and headings (e.g., "Chapter 1", "Chapter X"), determine the total number of distinct chapters in this outline.
Respond with a JSON object containing a single key "TotalChapters" with an integer value representing the count.

**Example Response:**
`{{"TotalChapters": 12}}`

If the outline is unclear or does not seem to be divided into chapters, return 0.
Provide ONLY the JSON response.
"""

GET_IMPORTANT_BASE_PROMPT_INFO: str = """
Carefully review the user's initial story prompt provided below.
<USER_PROMPT>
{_Prompt}
</USER_PROMPT>

Extract any specific instructions, constraints, or overarching visions mentioned by the user that are NOT part of the core plot/character ideas but are important for the *process* of writing or the *style* of the final story.
This includes things like:
-   Desired chapter length or total word count.
-   Specific formatting requests (e.g., for dialogue).
-   Explicit "do's" or "don'ts" regarding content or style.
-   Information about the target audience if mentioned.
-   Any meta-instructions about how the AI should behave or approach the task.

Present these extracted points as a Markdown list under the heading "# Important Additional Context".
If no such specific instructions are found, respond with "# Important Additional Context\n- None found."

Do NOT summarize the plot or story idea itself. Focus only on auxiliary instructions.
Keep your response concise.
"""

JSON_PARSE_ERROR: str = """
Your previous response was expected to be a valid JSON object, but it could not be parsed.
It produced the following error:
<ERROR_MESSAGE>
{_Error}
</ERROR_MESSAGE>

Please carefully review your intended JSON structure and ensure it is correctly formatted.
Common issues include:
-   Missing or extra commas.
-   Mismatched braces `{{}}` or brackets `[]`.
-   Keys or string values not enclosed in double quotes.
-   Unescaped special characters within strings.

Provide ONLY the corrected, valid JSON object as your entire response. Do not include any explanatory text before or after the JSON.
"""

# --- Specialized Prompts ---
GLOBAL_NOVEL_CHAPTER_EDIT_PROMPT: str = """
You are performing a global consistency and flow edit on Chapter {ChapterNum} of a novel.
Consider this chapter within the context of the overall story outline and the text of all preceding chapters.

**Overall Story Outline (for high-level plot and character arcs):**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Novel Text Leading Up To This Chapter:**
(This section may be very long if many prior chapters exist. Focus on the most recent 1-2 chapters if context is overwhelming)
<NovelTextSoFar>
{_NovelTextSoFar}
</NovelTextSoFar>

**Current Chapter {ChapterNum} for Editing:**
<ChapterTextToEdit>
{_ChapterTextToEdit}
</ChapterTextToEdit>

**Editing Focus:**
1.  **Continuity**: Ensure events, character knowledge, and established facts in this chapter are consistent with what has occurred in previous chapters and align with the overall outline.
2.  **Foreshadowing/Payoff**: If this chapter should set up future events (per outline) or resolve earlier foreshadowing, subtly enhance these elements.
3.  **Pacing within Global Arc**: Adjust descriptions, dialogue length, or action sequences to ensure this chapter's pacing contributes effectively to the novel's overall rhythm. Avoid making it feel too rushed or slow relative to its importance.
4.  **Thematic Resonance**: Strengthen thematic connections to the broader story.
5.  **Character Arc Progression**: Ensure character actions and internal states in this chapter are a logical step in their overall development as indicated by the outline and previous chapters.

**Instructions:**
-   Make surgical edits rather than wholesale rewrites, unless absolutely necessary for global consistency.
-   Preserve the core plot and events of the chapter.
-   Your output should be ONLY the revised text of Chapter {ChapterNum}.

Revised Chapter {ChapterNum} Text:
"""

OPTIMIZED_CONTENT_VS_OUTLINE_CHECK_PROMPT: str = """
You are an AI assistant tasked with verifying if a piece of generated content accurately reflects its guiding outline/plan.

**Guiding Outline/Plan for the Content:**
<REFERENCE_OUTLINE_OR_PLAN>
{_ReferenceOutlineOrPlan}
</REFERENCE_OUTLINE_OR_PLAN>

**Generated Content to Check:**
<GENERATED_CONTENT>
{_GeneratedContent}
</GENERATED_CONTENT>

**Task:**
Compare the "Generated Content" against the "Guiding Outline/Plan".
Respond with a JSON object containing the following fields:

{{
  "did_follow_outline": <boolean>,
  "alignment_score": <integer, 0-100, representing how well it followed, 100 is perfect>,
  "explanation": "<string, a brief explanation of your reasoning for the score and boolean value. Highlight key matches or deviations.>",
  "suggestions_for_improvement": "<string, if not perfectly aligned or if did_follow_outline is false, provide concise, actionable suggestions for the writer to better adhere to the plan in a revision. If it followed well, this can be minimal or state 'Excellent alignment.'>"
}}

-   `did_follow_outline`: `true` if the content substantially covers the key points and intent of the outline/plan; `false` otherwise. Minor creative liberties are acceptable if they don't contradict the core plan.
-   `alignment_score`: Your subjective assessment of adherence.
-   `explanation`: Justify your `did_follow_outline` and `alignment_score`.
-   `suggestions_for_improvement`: Focus on how to better meet the outline's goals.

Provide ONLY the JSON response.
"""

# --- Prompts for Scrubber, Translator, StoryInfo (can be similar to original or slightly optimized) ---
CHAPTER_SCRUB_PROMPT: str = """
Review the following chapter text.
<CHAPTER>
{_Chapter}
</CHAPTER>

Your task is to meticulously clean this text for final publication. This involves:
1.  Removing any leftover author notes, editorial comments, or bracketed instructions (e.g., "[Insert dramatic reveal here]", "TODO: Describe the sunset").
2.  Deleting any headings, subheadings, or outline markers that are not part of the narrative itself (e.g., "Scene 1:", "Character Development:", "Plot Point A:").
3.  Ensuring consistent formatting for dialogue (e.g., using standard quotation marks).
4.  Correcting any obvious typographical errors or formatting inconsistencies that might have been missed.

The goal is to produce pure, clean narrative text suitable for a reader.
Do not add, remove, or change the story content itself beyond these cleanup tasks.
Do not summarize, critique, or add any commentary.

Output ONLY the cleaned chapter text.
"""

STATS_PROMPT: str = """
Analyze the complete story context provided in previous messages (or the provided full outline).
Based on this, generate a JSON object with the following information:

{{
  "Title": "<string, A compelling and concise title for the story, ideally 3-8 words.>",
  "Summary": "<string, A 1-2 paragraph summary covering the main plot from beginning to end, including key conflicts and resolution.>",
  "Tags": "<string, A comma-separated list of 5-10 relevant keywords or tags that categorize the story (e.g., sci-fi, adventure, romance, betrayal, alien invasion, dystopian future).>",
  "OverallRating": "<integer, Your subjective overall quality score for the story based on its coherence, engagement, and creativity, from 0 to 100.>"
}}

Ensure your response is ONLY this JSON object, with no additional text before or after.
Strive for a creative and fitting title, a comprehensive yet succinct summary, and relevant tags.
"""

TRANSLATE_PROMPT: str = """
Translate the following text into { _Language}.
Focus on conveying the original meaning and tone accurately and naturally in {_Language}.
Do not add any commentary, interpretation, or formatting beyond what is necessary for a faithful translation.

<TEXT_TO_TRANSLATE>
{_Prompt}
</TEXT_TO_TRANSLATE>

Translated text:
"""

CHAPTER_TRANSLATE_PROMPT: str = """
Translate the following story chapter into {_Language}.
Preserve the narrative style, character voices, and emotional tone of the original as much as possible.
Ensure the translation is fluent and natural-sounding in {_Language}.

<CHAPTER_TEXT>
{_Chapter}
</CHAPTER_TEXT>

Translated Chapter Text in {_Language}:
"""