# -*- coding: utf-8 -*-
"""
genre_templates.py - Genre-specific templates and generation guidance
"""
from enum import Enum
from typing import Dict


class Genre(str, Enum):
    """Supported genres for fiction generation."""
    FANTASY = "fantasy"
    SCIENCE_FICTION = "science_fiction"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    HORROR = "horror"
    THRILLER = "thriller"
    LITERARY_FICTION = "literary_fiction"
    HISTORICAL_FICTION = "historical_fiction"
    YOUNG_ADULT = "young_adult"
    CONTEMPORARY_FICTION = "contemporary_fiction"


class GenreTemplate:
    """Base class for genre-specific generation templates."""

    def __init__(self, genre: Genre):
        self.genre = genre

    def get_outline_guidance(self) -> str:
        """Get genre-specific guidance for outline generation."""
        return self._get_guidance_template().get('outline_guidance', '')

    def get_content_guidance(self) -> str:
        """Get genre-specific guidance for content generation."""
        return self._get_guidance_template().get('content_guidance', '')

    def get_quality_criteria(self) -> Dict:
        """Get genre-specific quality criteria adjustments."""
        return self._get_guidance_template().get('quality_criteria', {})

    def _get_guidance_template(self) -> Dict:
        """Return the template dict for this genre."""
        return TEMPLATES.get(self.genre, {})


TEMPLATES = {
    Genre.FANTASY: {
        'outline_guidance': """
**FANTASY OUTLINE GUIDANCE:**

Focus on world-building elements:
- Magic systems: Define rules, limitations, costs, and consequences
- World history: Ancient events, myths, legends that shape current story
- Unique cultures: Different societies with their own customs, beliefs, and conflicts
- Political structures: Kingdoms, empires, councils, and power dynamics

Character archetypes to consider:
- The chosen one/unexpected hero
- The wise mentor
- The dark lord/villain
- The companion(s) with diverse skills
- The shapeshifter/ally with questionable loyalty

Plot elements to emphasize:
- The journey/quest structure
- Rising magical abilities or knowledge
- Tests of character through magical challenges
- World-altering stakes (saving of realm/world)

Setting focus:
- Describe magical landscapes and phenomena
- Incorporate sensory details of fantasy settings
- Balance wonder with danger
""",
        'content_guidance': """
**FANTASY CONTENT GENERATION:**

When writing fantasy chapters:
1. Ground magical elements in concrete details - how do they look, sound, feel?
2. Show magic's impact on characters and environment, not just its existence
3. Weave world-building naturally into action and dialogue, not as exposition dumps
4. Maintain internal consistency with established magic rules
5. Use fantasy settings to create atmosphere and mood

Writing style tips:
- Use evocative, sensory-rich descriptions
- Balance action sequences with moments of wonder/awe
- Let characters react emotionally to fantastical elements
- Include cultural touches: food, clothing, architecture, customs
""",
        'quality_criteria': {
            'description_focus': 'high',
            'dialogue_ratio_range': (0.2, 0.6),
            'pacing_notes': 'Allow room for descriptive passages, maintain forward momentum'
        }
    },

    Genre.MYSTERY: {
        'outline_guidance': """
**MYSTERY OUTLINE GUIDANCE:**

Focus on puzzle elements:
- The crime/inciting incident: What happened, when, where?
- The victim: Who are they, why do they matter?
- Clues: Physical evidence, witness statements, contradictions
- Red herrings: False leads, misdirection, suspicious behavior
- The detective/investigator: Their methods, personality, personal stakes

Plot structure elements:
- Discovery of crime
- Initial investigation and gathering clues
- False leads and dead ends
- Rising tension as stakes increase
- The breakthrough/clue that changes everything
- The confrontation/revelation

Character dynamics:
- Suspects with motives, means, and opportunities
- Witnesses with incomplete or unreliable information
- Antagonist who is clever and resourceful
- Allies who may have their own agendas
""",
        'content_guidance': """
**MYSTERY CONTENT GENERATION:**

When writing mystery chapters:
1. Plant clues naturally in action and dialogue - make them subtle
2. Create tension through information gaps - what characters don't know
3. Use red herrings judiciously - misdirect, don't mislead unfairly
4. Show, don't tell: Let readers discover clues alongside characters
5. Maintain reader trust: Play fair with puzzle

Writing style tips:
- Maintain careful pacing - slower during investigation, faster during action
- Use atmosphere to create mood and tension
- Keep dialogue purposeful: conceal, reveal, misdirect
- End chapters with questions, not answers
- Balance procedural elements with character development
""",
        'quality_criteria': {
            'dialogue_ratio_range': (0.3, 0.7),
            'pacing_notes': 'Vary pacing for investigation vs. action sequences'
        }
    },

    Genre.ROMANCE: {
        'outline_guidance': """
**ROMANCE OUTLINE GUIDANCE:**

Focus on emotional arcs:
- The meet-cute/inciting meeting: First impression, initial attraction or conflict
- Growing connection: Shared experiences, vulnerability, chemistry
- Internal conflicts: Past wounds, fears, miscommunications
- External obstacles: Family, society, ex-partners, career pressures
- The black moment: Crisis that threatens everything
- The resolution: Growth, compromise, commitment

Character development arcs:
- Protagonist 1: What they need to learn/overcome
- Protagonist 2: What they need to learn/overcome
- Together: How they complement/challenge each other

Relationship milestones:
- First meaningful conversation
- First vulnerable moment
- First kiss/intimacy
- First real conflict
- Realization of love
- Commitment
""",
        'content_guidance': """
**ROMANCE CONTENT GENERATION:**

When writing romance chapters:
1. Build chemistry through small details: glances, touches, word choices
2. Show attraction through action, not internal monologue
3. Create tension: want + obstacles = romance
4. Balance emotional beats with external plot
5. Let characters earn their happy ending through growth

Writing style tips:
- Focus on micro-moments: hands touching, meaningful looks, what's unsaid
- Use sensory details to create intimacy
- Develop distinct voices for each romantic partner
- Avoid insta-love - build connection gradually
- End scenes with emotional resonance or tension
""",
        'quality_criteria': {
            'dialogue_ratio_range': (0.4, 0.75),
            'pacing_notes': 'Slow down for romantic scenes, maintain plot momentum'
        }
    },

    Genre.SCIENCE_FICTION: {
        'outline_guidance': """
**SCIENCE FICTION OUTLINE GUIDANCE:**

Focus on speculative elements:
- The "what if?" premise: What scientific concept or technology drives to story?
- World implications: How does this tech/concept change society, culture, daily life?
- Scientific plausibility: Internal logic that follows from premise
- Near vs. far future: How much does the world resemble ours?

Character roles:
- Scientist/researcher: Discoverer or victim of premise
- Everyman: Grounded perspective experiencing the extraordinary
- Authority figure: Represents establishment, order, or threat
- Revolutionary/challenger: Questions the status quo

Plot frameworks:
- Discovery: Something new changes everything
- Dystopian/utopian: Societal implications of technology
- First contact: Encounter with alien intelligence
- Space exploration: Human expansion, survival, discovery
- AI/technology: Questions of consciousness, ethics, control
""",
        'content_guidance': """
**SCIENCE FICTION CONTENT GENERATION:**

When writing sci-fi chapters:
1. Make speculative elements concrete and tangible
2. Show technology's human consequences, not just specs
3. Balance scientific detail with emotional resonance
4. Maintain internal consistency with established tech/rules
5. Let characters react as real people to extraordinary situations

Writing style tips:
- Use precise language for technical elements
- Create wonder through novel concepts and discoveries
- Ground high-concept ideas in human experiences
- Consider implications: social, ethical, philosophical
- Balance action with intellectual engagement
""",
        'quality_criteria': {
            'description_focus': 'medium',
            'dialogue_ratio_range': (0.25, 0.65),
            'pacing_notes': 'Allow for conceptual explanation but integrate naturally'
        }
    },

    Genre.HORROR: {
        'outline_guidance': """
**HORROR OUTLINE GUIDANCE:**

Focus on fear and tension:
- The source of horror: Monster, situation, madness, unknown
- The stakes: What will be lost? Life, sanity, loved ones, humanity?
- The setting: Isolated, claustrophobic, atmospheric
- The escalation: From unease to dread to terror

Character dynamics:
- The protagonist: Vulnerable but resourceful
- The skeptic: Denies danger until too late
- The first victim: Establishes stakes
- The knowledgeable one: Understands threat
- The redemptive arc: Character who must overcome fear

Horror elements:
- Uncanny: Familiar made strange
- Body horror: Visceral, visceral fear
- Psychological: Madness, paranoia, unreality
- Supernatural: Rules and limitations of threat
- Survival: Resources depleting, hope diminishing
""",
        'content_guidance': """
**HORROR CONTENT GENERATION:**

When writing horror chapters:
1. Build tension gradually - start with unease, escalate to terror
2. Use sensory details: sound, smell, touch for visceral impact
3. Show, don't tell: Let readers experience horror through characters
4. Balance gore with psychological horror - what's unseen can be scarier
5. Maintain protagonist's humanity even in extreme situations

Writing style tips:
- Use short, punchy sentences to increase tension
- Employ rule of threes for scares: setup, escalation, payoff
- End chapters with cliffhangers or lingering dread
- Use setting as antagonist: isolation, darkness, decay
- Let fear manifest physically: racing heart, shallow breath, trembling
""",
        'quality_criteria': {
            'description_focus': 'high',
            'dialogue_ratio_range': (0.2, 0.5),
            'pacing_notes': 'Slow burn for tension, accelerate for terror sequences'
        }
    },

    Genre.THRILLER: {
        'outline_guidance': """
**THRILLER OUTLINE GUIDANCE:**

Focus on suspense and pacing:
- The hook: Immediate danger, stakes, or mystery
- The protagonist: Competent but outmatched
- The antagonist: Clever, resourceful, menacing
- The stakes: Personal, immediate, escalating
- The clock: Time pressure that increases tension

Plot frameworks:
- Chase/escape: Protagonist fleeing or pursuing
- Investigation: Uncovering conspiracy or truth
- Psychological: Cat-and-mouse games
- Action: Physical danger and confrontation

Thriller elements:
- Near misses: Escaping by narrow margins
- Complications: Plans go wrong, new obstacles
- Escalation: Stakes increase, situations worsen
- Betrayal: Allies aren't trustworthy
- Reversals: What seems true isn't
""",
        'content_guidance': """
**THRILLER CONTENT GENERATION:**

When writing thriller chapters:
1. Maintain forward momentum - every scene should advance to plot
2. Create tension through information gaps and uncertainty
3. Use short chapters and cliffhangers to maintain pace
4. Raise stakes continuously - what's lost gets worse
5. Balance action sequences with quieter moments of tension

Writing style tips:
- Use active verbs and concise prose
- End chapters mid-action or mid-revelation
- Make danger feel real and immediate
- Let characters be smart but fallible
- Use pacing to control tension: fast for action, slow for dread
""",
        'quality_criteria': {
            'dialogue_ratio_range': (0.3, 0.6),
            'pacing_notes': 'Maintain consistent forward momentum'
        }
    },

    Genre.LITERARY_FICTION: {
        'outline_guidance': """
**LITERARY FICTION OUTLINE GUIDANCE:**

Focus on character and theme:
- The protagonist: Complex, flawed, evolving
- Internal conflict: What do they want vs. what do they need?
- External conflict: How internal struggle manifests in world
- Themes: What questions about human experience does this explore?
- Symbolism: Objects, places, events that carry deeper meaning

Character development:
- Backstory: Events that shaped them
- Flaws: What holds them back
- Growth: How they change (or fail to change)
- Relationships: How they reveal character
- Choices: What they do under pressure

Narrative elements:
- Voice: Distinctive perspective and tone
- Structure: May be nonlinear, fragmented, experimental
- Prose style: Emphasis on language itself
- Ambiguity: Multiple interpretations welcome
""",
        'content_guidance': """
**LITERARY FICTION CONTENT GENERATION:**

When writing literary fiction chapters:
1. Focus on interiority - character's thoughts, feelings, perceptions
2. Use prose consciously: word choice, rhythm, sound, image
3. Let action emerge from character rather than drive character
4. Explore nuance: ambiguity, contradiction, complexity
5. Trust reader: Show, don't explain

Writing style tips:
- Pay attention to sentence construction and rhythm
- Use imagery and metaphor to deepen meaning
- Explore small, revealing moments
- Balance interiority with external action
- Consider cumulative emotional effect
""",
        'quality_criteria': {
            'description_focus': 'high',
            'dialogue_ratio_range': (0.2, 0.6),
            'pacing_notes': 'Allow time for reflection and character development'
        }
    },

    Genre.HISTORICAL_FICTION: {
        'outline_guidance': """
**HISTORICAL FICTION OUTLINE GUIDANCE:**

Focus on research and authenticity:
- The historical context: Time period, events, social conditions
- Historical figures: Real people with documented lives
- Fictional characters: How they intersect with history
- Research anchors: Real events, places, details
- Modern relevance: Why does this story matter now?

Character dynamics:
- The protagonist: Often a fictional lens into historical events
- Historical figures: Grounded in documented character
- Social position: Class, race, gender, privilege constraints
- Historical pressures: Wars, revolutions, social changes

Plot integration:
- Use real events as structural anchors
- Respect historical constraints and consequences
- Show how larger events affect individuals
- Balance historical accuracy with narrative needs
""",
        'content_guidance': """
**HISTORICAL FICTION CONTENT GENERATION:**

When writing historical fiction chapters:
1. Use authentic details: clothing, food, technology, language
2. Show, don't tell historical context through character experience
3. Balance research with story - don't lecture
4. Understand period attitudes and worldviews, even if they differ from modern ones
5. Connect past to present: Why does this history matter?

Writing style tips:
- Use period-appropriate language (but readable)
- Incorporate historical details naturally in action
- Show how events transform society and individuals
- Let characters be people of their time, not modern views in costume
- Consider what's known vs. what's imagined about period
""",
        'quality_criteria': {
            'description_focus': 'high',
            'dialogue_ratio_range': (0.25, 0.6),
            'pacing_notes': 'Respect historical timeline, maintain narrative momentum'
        }
    },

    Genre.YOUNG_ADULT: {
        'outline_guidance': """
**YOUNG ADULT OUTLINE GUIDANCE:**

Focus on coming-of-age:
- The protagonist: Teen/young adult facing pivotal challenges
- The change: What must they learn or become?
- Identity: Questions of who they are and where they belong
- First experiences: Love, loss, independence, responsibility
- The world: School, family, friends, society

Character development:
- Growth arc: From child to adult (or toward it)
- Relationships: Family, friends, romantic interests
- Rebellion vs. conformity: Finding one's own path
- Self-discovery: Understanding strengths, weaknesses, desires

Plot elements:
- High stakes that feel life-changing to protagonist
- External conflicts that mirror internal struggles
- Meaningful choices with real consequences
- Community or connection with peers
- A sense of hope or possibility
""",
        'content_guidance': """
**YOUNG ADULT CONTENT GENERATION:**

When writing YA chapters:
1. Capture authentic teen voice: slang, attitudes, priorities
2. Focus on first experiences and their emotional impact
3. Balance intensity with moments of humor and connection
4. Don't talk down - treat readers with respect
5. Address real issues teens face

Writing style tips:
- Use first-person or close third for immediacy
- Keep prose accessible but not simplistic
- Include relatable friendships and family dynamics
- Show growth through mistakes and learning
- Balance external plot with internal development
""",
        'quality_criteria': {
            'dialogue_ratio_range': (0.35, 0.7),
            'pacing_notes': 'Engage quickly, maintain forward momentum'
        }
    },

    Genre.CONTEMPORARY_FICTION: {
        'outline_guidance': """
**CONTEMPORARY FICTION OUTLINE GUIDANCE:**

Focus on relatable human experience:
- The protagonist: Ordinary person in extraordinary circumstances
- The conflict: Internal, relational, or situational
- The setting: Contemporary world readers recognize
- The change: How circumstances transform protagonist
- The meaning: What does this story say about life?

Character dynamics:
- Family: Complicated relationships with history
- Work: Career aspirations, colleagues, workplace dynamics
- Friends: Chosen family, support systems, conflicts
- Society: Current issues, cultural context, pressures

Plot frameworks:
- Family drama: Secrets, conflicts, reconciliations
- Personal journey: Self-discovery, growth, change
- Relationship stories: Romance, friendship, found family
- Social issues: Contemporary problems through character lens
""",
        'content_guidance': """
**CONTEMPORARY FICTION CONTENT GENERATION:**

When writing contemporary fiction chapters:
1. Create relatable, three-dimensional characters
2. Use authentic details of modern life
3. Balance humor and gravity in realistic proportion
4. Let characters feel like people readers know
5. Connect personal stories to universal experiences

Writing style tips:
- Use accessible prose with moments of beauty
- Ground drama in recognizable reality
- Show character through action and small details
- Balance dialogue with internal thought
- Create scenes that illuminate character
""",
        'quality_criteria': {
            'dialogue_ratio_range': (0.3, 0.65),
            'pacing_notes': 'Realistic pacing - slower for reflection, faster for conflict'
        }
    }
}


def get_genre_template(genre: str) -> GenreTemplate:
    """
    Get a genre template for specified genre.
    
    Args:
        genre: String name of genre
        
    Returns:
        GenreTemplate object
    """
    try:
        genre_enum = Genre(genre.lower())
    except ValueError:
        genre_enum = Genre.CONTEMPORARY_FICTION
    
    return GenreTemplate(genre_enum)


def detect_genre_from_outline(outline_text: str) -> Genre:
    """
    Attempt to detect genre from an outline description.
    Returns CONTEMPORARY_FICTION if unable to detect.
    """
    text_lower = outline_text.lower()
    
    genre_keywords = {
        Genre.FANTASY: ['magic', 'wizard', 'dragon', 'kingdom', 'quest', 'spell', 'enchanted', 'sword'],
        Genre.SCIENCE_FICTION: ['space', 'robot', 'future', 'alien', 'technology', 'spaceship', 'ai', 'cyber'],
        Genre.MYSTERY: ['murder', 'detective', 'clue', 'crime', 'suspect', 'investigation', 'whodunit'],
        Genre.ROMANCE: ['love', 'romance', 'relationship', 'heart', 'kiss', 'wedding', 'affair'],
        Genre.HORROR: ['ghost', 'monster', 'scary', 'haunted', 'killer', 'terror', 'nightmare'],
        Genre.THRILLER: ['chase', 'spy', 'conspiracy', 'assassin', 'escape', 'danger', 'suspense'],
        Genre.HISTORICAL_FICTION: ['war', 'medieval', 'victorian', 'ancient', 'revolution', 'historical'],
        Genre.YOUNG_ADULT: ['teen', 'school', 'coming of age', 'adolescent', 'high school']
    }
    
    for genre, keywords in genre_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return genre
    
    return Genre.CONTEMPORARY_FICTION
