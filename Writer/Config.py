#!/usr/bin/python3

import configparser
import os
import termcolor

# --- Configuration Loading ---

# Create a ConfigParser instance
config = configparser.ConfigParser()

# Define the path to config.ini relative to this file's location
# This assumes Config.py is in Writer/, and config.ini is in the project root.
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')

# Read the configuration file and add explicit, prominent logging
print(termcolor.colored("--- Initializing Configuration ---", "yellow"))
if os.path.exists(config_path):
    try:
        config.read(config_path)
        # Convert section names to lowercase for consistency
        config._sections = {k.lower(): v for k, v in config._sections.items()}
        print(termcolor.colored(f"[CONFIG] Successfully read config.ini from: {config_path}", "green"))
        loaded_sections = list(config.sections())
        print(termcolor.colored(f"[CONFIG] Found sections: {loaded_sections}", "cyan"))

        # Explicitly check for NVIDIA section and key for debugging
        if 'nvidia_settings' in loaded_sections:
            nvidia_models_value = config.get('nvidia_settings', 'available_models', fallback="[NOT FOUND]")
            nvidia_url_value = config.get('nvidia_settings', 'base_url', fallback="[NOT FOUND]")
            print(termcolor.colored(f"[CONFIG] Raw value for [nvidia_settings]/available_models: '{nvidia_models_value}'", "cyan"))
            print(termcolor.colored(f"[CONFIG] Raw value for [nvidia_settings]/base_url: '{nvidia_url_value}'", "cyan"))
        else:
            print(termcolor.colored("[CONFIG] Section [nvidia_settings] not found in config.ini.", "red"))

    except configparser.Error as e:
        print(termcolor.colored(f"[CONFIG] CRITICAL: Failed to parse config.ini. Error: {e}", "red"))
else:
    print(termcolor.colored(f"[CONFIG] WARNING: config.ini not found at expected path: {config_path}", "red"))

print(termcolor.colored("------------------------------------", "yellow"))


def get_config_or_default(section, key, default, is_bool=False, is_int=False):
    """
    Safely get a value from the config file, otherwise return the default.
    Handles type conversion for boolean and integer values.
    Uses lowercase for section names as per configparser standard.
    """
    section = section.lower()
    if is_bool:
        return config.getboolean(section, key, fallback=default)
    if is_int:
        return config.getint(section, key, fallback=default)
    return config.get(section, key, fallback=default)

# --- Project Info ---
PROJECT_NAME = get_config_or_default('PROJECT_INFO', 'project_name', 'Fiction Fabricator')


# --- LLM Model Selection ---
INITIAL_OUTLINE_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'initial_outline_writer_model', "google://gemini-1.5-pro-latest")
CHAPTER_OUTLINE_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_outline_writer_model', "google://gemini-1.5-flash-latest")
CHAPTER_STAGE1_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_stage1_writer_model', "google://gemini-1.5-flash-latest")
CHAPTER_STAGE2_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_stage2_writer_model', "google://gemini-1.5-flash-latest")
CHAPTER_STAGE3_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_stage3_writer_model', "google://gemini-1.5-flash-latest")
CHAPTER_STAGE4_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_stage4_writer_model', "google://gemini-1.5-flash-latest")
CHAPTER_REVISION_WRITER_MODEL = get_config_or_default('LLM_SELECTION', 'chapter_revision_writer_model', "google://gemini-1.5-pro-latest")
CRITIQUE_LLM = get_config_or_default('LLM_SELECTION', 'critique_llm', "google://gemini-1.5-flash-latest")
REVISION_MODEL = get_config_or_default('LLM_SELECTION', 'revision_model', "google://gemini-1.5-flash-latest")
EVAL_MODEL = get_config_or_default('LLM_SELECTION', 'eval_model', "google://gemini-1.5-flash-latest")
INFO_MODEL = get_config_or_default('LLM_SELECTION', 'info_model', "google://gemini-1.5-flash-latest")
SCRUB_MODEL = get_config_or_default('LLM_SELECTION', 'scrub_model', "google://gemini-1.5-flash-latest")
CHECKER_MODEL = get_config_or_default('LLM_SELECTION', 'checker_model', "google://gemini-1.5-flash-latest")


# --- NVIDIA Specific Settings (if used) ---
NVIDIA_AVAILABLE_MODELS = get_config_or_default('NVIDIA_SETTINGS', 'available_models', '')
NVIDIA_BASE_URL = get_config_or_default('NVIDIA_SETTINGS', 'base_url', 'https://integrate.api.nvidia.com/v1')


# --- Ollama Specific Settings (if used) ---
OLLAMA_CTX = get_config_or_default('WRITER_SETTINGS', 'ollama_ctx', 8192, is_int=True)


# --- Writer Settings ---
SEED = get_config_or_default('WRITER_SETTINGS', 'seed', 108, is_int=True)
OUTLINE_MIN_REVISIONS = get_config_or_default('WRITER_SETTINGS', 'outline_min_revisions', 0, is_int=True)
OUTLINE_MAX_REVISIONS = get_config_or_default('WRITER_SETTINGS', 'outline_max_revisions', 3, is_int=True)
CHAPTER_NO_REVISIONS = get_config_or_default('WRITER_SETTINGS', 'chapter_no_revisions', False, is_bool=True)
CHAPTER_MIN_REVISIONS = get_config_or_default('WRITER_SETTINGS', 'chapter_min_revisions', 2, is_int=True)
CHAPTER_MAX_REVISIONS = get_config_or_default('WRITER_SETTINGS', 'chapter_max_revisions', 3, is_int=True)
MINIMUM_CHAPTERS = get_config_or_default('WRITER_SETTINGS', 'minimum_chapters', 12, is_int=True)
SCRUB_NO_SCRUB = get_config_or_default('WRITER_SETTINGS', 'scrub_no_scrub', False, is_bool=True)
EXPAND_OUTLINE = get_config_or_default('WRITER_SETTINGS', 'expand_outline', True, is_bool=True)
ENABLE_FINAL_EDIT_PASS = get_config_or_default('WRITER_SETTINGS', 'enable_final_edit_pass', False, is_bool=True)
SCENE_GENERATION_PIPELINE = get_config_or_default('WRITER_SETTINGS', 'scene_generation_pipeline', True, is_bool=True)
DEBUG = get_config_or_default('WRITER_SETTINGS', 'debug', False, is_bool=True)

# Optional output name override from command-line (not set from config)
OPTIONAL_OUTPUT_NAME = ""


# Example models for reference:
# "google://gemini-1.5-pro-latest"
# "mistralai://mistral-large-latest"
# "groq://mixtral-8x7b-32768"
# "nvidia://meta/llama3-8b-instruct"
# "ollama://llama3:70b"
# "ollama://command-r-plus@10.1.65.4:11434"
