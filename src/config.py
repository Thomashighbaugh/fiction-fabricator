# -*- coding: utf-8 -*-
"""
config.py - Centralized configuration for the Fiction Fabricator project.
"""
from google.generativeai import types

# --- Model and API Configuration ---
WRITING_MODEL_NAME = "gemini-2.5-flash"
WRITING_MODEL_CONFIG = types.GenerationConfig(
    temperature=1,
    max_output_tokens=65536,  # Max for gemini-2.5-flash to avoid truncation
    top_p=0.95,
    top_k=40,
)

# --- API Retry Configuration ---
MAX_API_RETRIES = 3
API_RETRY_BACKOFF_FACTOR = 2  # Base seconds for backoff (e.g., 2s, 4s, 8s)

# --- Formatting and Naming Conventions ---
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT_FOR_FOLDER = "%Y%m%d"
