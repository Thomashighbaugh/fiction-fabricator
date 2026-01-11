# -*- coding: utf-8 -*-
"""
config.py - Centralized configuration for the Fiction Fabricator project.
"""

# --- Model and API Configuration ---
# Using NVIDIA API with DeepSeek model
MODEL_NAME = "deepseek-ai/deepseek-v3.1-terminus"

# --- API Retry Configuration ---
MAX_API_RETRIES = 3
API_RETRY_BACKOFF_FACTOR = 2  # Base seconds for backoff (e.g., 2s, 4s, 8s)

# --- Formatting and Naming Conventions ---
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT_FOR_FOLDER = "%Y%m%d"

# --- Self-Critique & Auto-Refinement Configuration ---
# Maximum number of refinement iterations per chapter
MAX_REFINEMENT_ITERATIONS = 3
# Quality thresholds (1-10 scale, 6+ = acceptable)
MIN_QUALITY_SCORE = 6
# Enable/disable auto-critique after generation
ENABLE_AUTO_CRITIQUE = True
# Enable/disable auto-refinement if quality threshold not met
ENABLE_AUTO_REFINE = True

# --- Adaptive Sub-beat Configuration ---
# Target word count per chapter (used for calculating sub-beat count)
TARGET_WORD_COUNT_PER_CHAPTER = 4500
# Average words per sub-beat (sub-beats generate 2-3 paragraphs)
AVG_WORDS_PER_SUB_BEAT = 150
# Minimum and maximum sub-beats per beat (adaptive bounds)
MIN_SUB_BEATS_PER_BEAT = 2
MAX_SUB_BEATS_PER_BEAT = 8
# Enable/disable adaptive sub-beat counting
ENABLE_ADAPTIVE_SUB_BEATS = True

# --- Character State Tracker Configuration ---
# Enable/disable character state tracking across chapters
ENABLE_CHARACTER_STATE_TRACKING = True
# Maximum number of knowledge items to track per character
MAX_KNOWLEDGE_ITEMS = 20

# --- Plot Thread Management Configuration ---
# Enable/disable plot thread tracking
ENABLE_PLOT_THREAD_TRACKING = True
# Warn about unresolved plot threads at story end
WARN_UNRESOLVED_THREADS = True

# --- Dialogue Quality Pass Configuration ---
# Enable/disable dialogue-specific refinement
ENABLE_DIALOGUE_QUALITY_PASS = True
# Minimum dialogue quality score (1-10 scale)
MIN_DIALOGUE_QUALITY_SCORE = 7
# Number of dialogue refinement iterations
MAX_DIALOGUE_REFINEMENT_ITERATIONS = 1

# --- Descriptive Enhancement Pass Configuration ---
# Enable/disable descriptive/sensory enhancement
ENABLE_DESCRIPTIVE_ENHANCEMENT_PASS = True
# Minimum description quality score (1-10 scale)
MIN_DESCRIPTION_QUALITY_SCORE = 6
# Number of description refinement iterations
MAX_DESCRIPTION_REFINEMENT_ITERATIONS = 1
# Sensory categories to evaluate
SENSORY_CATEGORIES = ["sight", "sound", "smell", "touch", "taste"]

# --- Pacing Analysis Configuration ---
# Enable/disable pacing analysis and suggestions
ENABLE_PACING_ANALYSIS = True
# Target words per paragraph for proper pacing
TARGET_WORDS_PER_PARAGRAPH = 150
# Pacing variance tolerance (percentage)
PACING_VARIANCE_TOLERANCE = 0.3  # 30% variance acceptable
# Minimum words per sub-beat
MIN_WORDS_PER_SUB_BEAT = 100
# Maximum words per sub-beat
MAX_WORDS_PER_SUB_BEAT = 300

# --- Quality Metrics Configuration ---
# Enable/disable quality metrics system
ENABLE_QUALITY_METRICS = True
# Minimum word count per chapter (reject below this)
MIN_WORDS_PER_CHAPTER = 2000
# Dialogue-to-narrative ratio (dialogue / total words, 0.0-1.0)
MIN_DIALOGUE_RATIO = 0.15  # At least 15% should be dialogue
MAX_DIALOGUE_RATIO = 0.70  # At most 70% should be dialogue
# Sentence variety threshold (short < 10, medium 10-25, long > 25 words)
MIN_SENTENCE_VARIETY_SCORE = 5  # Score 1-10, below this lacks variety
# Vocabulary richness threshold (unique word ratio)
MIN_VOCABULARY_RICHNESS_SCORE = 6  # Score 1-10, below this is poor vocabulary
# Auto-reject content that doesn't meet thresholds
AUTO_REJECT_BELOW_THRESHOLDS = True
# Maximum auto-regeneration attempts per chapter
MAX_AUTO_REGEN_ATTEMPTS = 2

# --- Continuity Management Configuration ---
# Enable/disable continuity tracking
ENABLE_CONTINUITY_TRACKING = True
# Warn about entity inconsistencies
WARN_ENTITY_INCONSISTENCIES = True
# Enable world rule tracking
ENABLE_WORLD_RULE_TRACKING = True

# --- Batch-Aware Generation Configuration ---
# Enable/disable smart batching
ENABLE_SMART_BATCHING = True
# Maximum tokens per batch
MAX_BATCH_TOKENS = 8000
# Minimum chapters per batch
MIN_CHAPTERS_PER_BATCH = 1
# Maximum chapters per batch
MAX_CHAPTERS_PER_BATCH = 5

# --- Rollback & Regeneration Configuration ---
# Enable/disable automatic rollback system
ENABLE_AUTOMATIC_ROLLBACK = True
# Maximum regeneration attempts per chapter
MAX_REGENERATION_ATTEMPTS = 3
# Number of versions to keep per chapter
VERSIONS_TO_KEEP = 3

# --- Content Enhancement Configuration ---
# Enable/disable content enhancement tools
ENABLE_CONTENT_ENHANCEMENTS = True
# Sub-beat validation threshold
MIN_SUB_BEAT_COHERENCE_SCORE = 0.6
MIN_SUB_BEAT_COMPREHENSIVENESS_SCORE = 0.6
# Word count prediction adjustment
AVG_WORDS_PER_SUB_BEAT = 150
COMPLEXITY_MULTIPLIER_RANGE = (0.9, 1.3)
# Dialogue tag variety threshold
MIN_DIALOGUE_TAG_VARIETY_SCORE = 0.4
DIALOGUE_TAG_OVERUSE_THRESHOLD = 0.2  # 20% of dialogue lines
# Sentence variety target distribution
SENTENCE_LENGTH_TARGETS = {
    'short': 0.25,      # 25% should be < 10 words
    'medium': 0.45,     # 45% should be 10-25 words
    'long': 0.20,        # 20% should be 25-40 words
    'very_long': 0.10     # 10% should be 40+ words
}
# Generate chapter hooks
ENABLE_CHAPTER_HOOK_GENERATION = True

# --- Font Configuration ---
# Default fonts used if no custom font is selected
DEFAULT_TITLE_FONT = "Georgia"
DEFAULT_CHAPTER_FONT = "Georgia"

# Popular Google Fonts options for chapter headings
GOOGLE_FONT_OPTIONS = [
    "Merriweather",
    "Playfair Display",
    "Crimson Text",
    "EB Garamond",
    "Libre Baskerville",
    "Cormorant Garamond",
    "Lora",
    "Source Serif Pro",
    "Vollkorn",
    "PT Serif",
    "Gentium Plus",
    "Noto Serif",
    "Bitter",
    "Alegreya",
    "Cardo"
]

# Font URLs mapping (Google Fonts)
GOOGLE_FONT_URLS = {
    "Merriweather": "https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&display=swap",
    "Playfair Display": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap",
    "Crimson Text": "https://fonts.googleapis.com/css2?family=Crimson+Text:wght@400;600;700&display=swap",
    "EB Garamond": "https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap",
    "Libre Baskerville": "https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&display=swap",
    "Cormorant Garamond": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&display=swap",
    "Lora": "https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600;700&display=swap",
    "Source Serif Pro": "https://fonts.googleapis.com/css2?family=Source+Serif+Pro:wght@400;600;700&display=swap",
    "Vollkorn": "https://fonts.googleapis.com/css2?family=Vollkorn:wght@400;600;700&display=swap",
    "PT Serif": "https://fonts.googleapis.com/css2?family=PT+Serif:wght@400;700&display=swap",
    "Gentium Plus": "https://fonts.googleapis.com/css2?family=Gentium+Plus:wght@400;700&display=swap",
    "Noto Serif": "https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;700&display=swap",
    "Bitter": "https://fonts.googleapis.com/css2?family=Bitter:wght@400;500;600;700&display=swap",
    "Alegreya": "https://fonts.googleapis.com/css2?family=Alegreya:wght@400;500;700&display=swap",
    "Cardo": "https://fonts.googleapis.com/css2?family=Cardo:wght@400;700&display=swap"
}
