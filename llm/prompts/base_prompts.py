# llm/prompts/base_prompts.py

COMMON_PREAMBLE = """You are a world-class novelist assisting with various stages of novel creation.
Your responses should be creative, detailed, and consistent with any provided context."""

TOML_FORMAT_INSTRUCTIONS = """Critically important: Your ENTIRE response MUST be valid TOML. Adhere strictly to this format, ensuring correct data types and escaping.
Output ONLY valid TOML, nothing else. No markdown code blocks, no explanations, no extra text before or after the TOML object."""

TOML_FORMAT_INSTRUCTIONS_BOOKS_SPEC = """Critically important: Your ENTIRE response MUST be valid TOML.  Adhere strictly to this format, ensuring correct data types and escaping. Output ONLY valid TOML, nothing else. No markdown code blocks, no explanations, no extra text before or after the TOML object.
Critically important: the value for "setting" MUST be a SINGLE STRING, describing location and time period.
"""
TOML_FORMAT_INSTRUCTIONS_PLOT_OUTLINE = """Critically important: Your ENTIRE response MUST be valid TOML.  Adhere strictly to this format, ensuring correct data types and escaping. Output ONLY valid TOML, nothing else. No markdown code blocks, no explanations, no extra text before or after the TOML object.

The structure should be:
```toml
[act_one]
block_one = ["string", "string"]
block_two = ["string", "string"]
block_three = ["string", "string"]

[act_two]
block_one = ["string", "string"]
block_two = ["string", "string"]
block_three = ["string", "string"]

[act_three]
block_one = ["string", "string"]
block_two = ["string", "string"]
block_three = ["string", "string"]
```
"""

TOML_FORMAT_INSTRUCTIONS_CHAPTER_OUTLINE = """Critically important: Your ENTIRE response MUST be valid TOML. Adhere strictly to this format, ensuring correct data types and escaping. Output ONLY valid TOML, nothing else. No markdown code blocks, no explanations, no extra text before or after the TOML object.
The structure should be a table called 'chapters' containing an array of tables, each with fields 'chapter_number' and 'summary'. Example:
```toml
chapters = [
    {chapter_number = 1, summary = "string"},
    {chapter_number = 2, summary = "string"},
    # ... more chapters
]
```
"""

TOML_FORMAT_INSTRUCTIONS_CHAPTER_OUTLINE_27 = """Critically important: Your ENTIRE response MUST be valid TOML. Adhere strictly to this format, ensuring correct data types and escaping. Output ONLY valid TOML, nothing else. No markdown code blocks, no explanations, no extra text before or after the TOML object.
The structure should be a table called 'chapters' containing an array of tables, each with fields 'chapter_number', 'role', and 'summary'.  Example:
```toml
chapters = [
    {chapter_number = 1, role = "string", summary = "string"},
    {chapter_number = 2, role = "string", summary = "string"},
    # ... more chapters
]
```
"""

CRITIQUE_REQUEST = """Provide a concise critique (2-3 sentences) that identifies specific areas for improvement. Focus on aspects such as clarity, detail, coherence, plot/character/scene development, thematic consistency, and the integration of any specified elements (e.g., dark or erotic themes). The critique should be actionable and guide the revision process."""

REWRITE_REQUEST = """Rewrite the following based on the critique, focusing on the identified areas for improvement. Maintain consistency with any provided context (book specification, chapter outline, scene outline, etc.). The rewritten content should be more engaging, immersive, and thematically resonant."""

METHODOLOGY_MARKDOWN = """
# 27 Chapter Plot Outline Method

The 27 chapter plot outline method divides the plot into acts, then divides the acts into blocks and finally divides the blocks into chapters as demonstrated in the example below. The chapters are typically assigned a certain role in the story's progression, which are here presented as descriptions following each enumerated chapter. Note that these are not strict assignments and a good novel tends not to be so formulaic in its arrangement, so taking creative liberty and deviating from the strict adherence to this structure is advised for authors working with this method.

Instead of being intended to provide a strict course of the action within a novel, it gives the author a loose guide that they can use to begin filling out their novel in a non-linear but still organized fashion without risking a lapse into the swirling infinity that a book can become if written without an outline beforehand.

## The Plot Structure

```md
1.  ACT I

    -   BLOCK 1 – This block will introduce the protagonist and their ordinary world (Setup)
        -   Chapter 1 – Introduction – introduce the main character(s) and their normal world (setup)
        -   Chapter 2 – Inciting Incident – something happens to disrupt the status quo (conflict)
        -   Chapter 3 – Immediate Reaction– main character(s) react to the inciting incident (resolution)
    -   BLOCK 2 – in this block, a problem disrupts the protagonist’s normal life (Conflict)
        -   Chapter 4– Reaction – the main character(s) plan what they should do (setup)
        -   Chapter 5– Action – something prevents the character(s) from implementing their plan(conflict)
        -   Chapter 6 – Consequence – the result of the character(s) plan being hindered(resolution)
    -   BLOCK 3 – this block focuses on how the protagonist’s life has changed (Resolution)
        -   Chapter 7– Pressure – something happens to add pressure to the situation (setup)
        -   Chapter 8– Pinch – the antagonistic forces of the story become better known (conflict)
        -   Chapter 9– Push – the character(s) move into a new world/are now changed forever (resolution)

2.  ACT II

    -   BLOCK 1 – in this block the protagonist explores their new world (Setup)
        -   Chapter 10 – New World – the character(s) explore new world/new way of seeingthe world (setup)
        -   Chapter 11 – Fun and Games – the character(s) develop through bonding, having funand learning about themselves and their environment (event/conflict)
        -   Chapter 12 – Old World Contrast– show how the new world is so different from whatthe character(s) knew before (resolution)
    -   BLOCK 2 – in this block the protagonist discovers the crisis of the new world (Conflict)
        -   Chapter 13 – Build Up – secrets are revealed(setup)
        -   Chapter 14 – Midpoint – something makes everything change… again (conflict)
        -   Chapter 15 – Reversal something that has appeared to be one thing, turns out to be something else, e.g. good guy is really a bad guy (resolution)
    -   BLOCK 3 – here the protagonists dedicate themselves to finding a solution (resolution)
        -   Chapter 16 – Reaction – the character(s) react to the reversal (setup)
        -   Chapter 17 – Action – action is taken against the events in the reversal (conflict)
        -   Chapter 18 – Dedication – the character(s) regroup. They gather supplies they need, learn skills they need to learn (resolution)

3.  ACT III
    -   BLOCK 1 – here the protagonist faces defeat and victory seems impossible (Setup)
        -   Chapter 19 – Trials – the Character(s) know what they must do now, what they must overcome (setup)
        -   Chapter 20 – Pinch – somebody or something gets in the way of the character(s) doing what they need to do (event/conflict)
        -   Chapter 21 – Darkest Moment – All seems lost (resolution)
    -   BLOCK 2 – here the protagonist must find power and take action (Conflict)
        -   Chapter 22 – Power Within – the character(s) rally and refuse to give up (setup)
        -   Chapter 23 – Action – the antagonistic forces rear their ugly head again and must be thwarted (conflict)
        -   Chapter 24 – Converge the character(s) gather themselves for a sort of last supper (resolution)
    -   BLOCK 3 – here the protagonist fights, wins and resolves the quest (Resolution)
        -   Chapter 25 – Battle – the time has come for the final battle (can be literal or figurative) (setup)
        -   Chapter 26 – Climax– the battle is either lost or won (depending on the type of story you’re telling) (conflict)
        -   Chapter 27 – Resolution – the aftermath of the battle, the character(s) have grown into different people from those at the beginning of the story(resolution)
```
"""
