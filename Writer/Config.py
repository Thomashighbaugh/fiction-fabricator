# File: Writer/Config.py
# Purpose: Central configuration for models, API keys, and generation parameters.

"""
Central configuration module for the AIStoryWriter.

This module defines default values for various settings, including:
- LLM model identifiers for different generation tasks.
- API keys and endpoint configurations (though sensitive keys are best loaded from .env).
- Parameters controlling the generation process (e.g., revision counts, seed).
- Flags for enabling/disabling features (e.g., debugging, translation).

These default values can be overridden by command-line arguments at runtime.
"""

# --- Model Configuration ---
# These will be populated by argparse or default values.
# It's recommended to use specific, descriptive names for each model's role.
# Example format: "provider://model_identifier@host?param1=value1¶m2=value2"
# or "provider://model_identifier" (host/params optional or provider-specific)

# Core Creative Models
INITIAL_OUTLINE_WRITER_MODEL: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF"
MODEL_STORY_ELEMENTS_GENERATOR: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" # For generating detailed story elements
MODEL_SCENE_OUTLINER: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" # For breaking chapters into scene outlines
MODEL_SCENE_NARRATIVE_GENERATOR: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" # For writing individual scene narratives
MODEL_CHAPTER_ASSEMBLY_REFINER: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" # For refining assembled scenes into a cohesive chapter

# Supporting and Utility Models
MODEL_CHAPTER_CONTEXT_SUMMARIZER: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" # For summarizing previous chapter/scene for context
REVISION_MODEL: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" # For providing critique/feedback
CHAPTER_REVISION_WRITER_MODEL: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" # For revising chapters based on feedback
EVAL_MODEL: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" # For evaluation tasks (e.g., IsComplete checks, JSON ratings)
INFO_MODEL: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" # For extracting story metadata (title, summary, tags)
SCRUB_MODEL: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" # For cleaning final output
CHECKER_MODEL: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" # For JSON parsing checks or simple validations
TRANSLATOR_MODEL: str = "huggingface.co/DavidAU/DeepSeek-MOE-4X8B-R1-Distill-Llama-3.1-Deep-Thinker-Uncensored-24B-GGUF:latest " # For translation tasks

# --- API and System Settings ---
OLLAMA_CTX: int = 16384  # Default context window size for Ollama models
OLLAMA_HOST: str = "http://localhost:11434" # Default Ollama host URL

# API keys should ideally be loaded from environment variables (.env file)
# and not hardcoded here. The Wrapper.py handles loading from os.environ.
# Example (actual values will be loaded from .env by the interface):
# GOOGLE_API_KEY: Optional[str] = None
# OPENROUTER_API_KEY: Optional[str] = None

SEED: int = 108  # Default seed for reproducibility and appeasing my superstitions, can be overridden by argparse

# --- Generation Parameters ---
TRANSLATE_LANGUAGE: str = ""  # Target language for story translation (e.g., "French")
TRANSLATE_PROMPT_LANGUAGE: str = ""  # Target language for initial user prompt translation

# Outline revision settings
OUTLINE_MIN_REVISIONS: int = 1  # Minimum number of revision cycles for the main outline
OUTLINE_MAX_REVISIONS: int = 5  # Maximum number of revision cycles for the main outline

# Chapter/Scene revision settings
CHAPTER_NO_REVISIONS: bool = False  # If True, skips feedback/revision loops for assembled chapters
CHAPTER_MIN_REVISIONS: int = 1  # Minimum revision cycles for an assembled chapter
CHAPTER_MAX_REVISIONS: int = 3  # Maximum revision cycles for an assembled chapter

# Scene-specific generation parameters
SCENE_NARRATIVE_MIN_WORDS: int = 350  # Minimum expected word count for a single generated scene narrative
SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER: int = 5 # Minimum scenes expected from the scene outliner per chapter
SCENE_OUTLINE_GENERATION_MAX_ATTEMPTS: int = 3 # Max attempts to generate scene outlines if initial fails

# --- Feature Flags ---
SCRUB_NO_SCRUB: bool = False  # If True, skips the final scrubbing pass
# EXPAND_OUTLINE is deprecated as scene-by-scene is the primary flow.
# The main outline is now expected to be a chapter-level plot outline.
ENABLE_FINAL_EDIT_PASS: bool = True # Enables a global novel editing pass after all chapters are assembled

SCENE_GENERATION_PIPELINE: bool = True  # Master flag for scene-by-scene generation (should be True for this refactor)
OPTIMIZE_PROMPTS_VERSION: str = "v2.1" # Version for tracking prompt sets, useful for A/B testing or updates

# --- Output Settings ---
OPTIONAL_OUTPUT_NAME: str = ""  # If set, overrides default output filename generation

# --- Debugging and Logging ---
DEBUG: bool = False  # Enables verbose logging, including potentially printing full prompts/responses
DEBUG_LEVEL: int = 0 # 0: Normal, 1: Basic Debug, 2: Detailed Debug (e.g. stream chunks)

# --- Model Endpoint Overrides from Args (will be populated by Write.py) ---
# These are placeholders to indicate that Write.py will manage overriding the above defaults.
# For example, ARGS_INITIAL_OUTLINE_WRITER_MODEL: Optional[str] = None
# Actual update logic is in Write.py