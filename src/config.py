# -*- coding: utf-8 -*-
"""
config.py - Centralized configuration for the Fiction Fabricator project.
"""
from google.generativeai import types

# --- Model and API Configuration ---
WRITING_MODEL_NAME = "gemini-2.5-flash-lite"
WRITING_MODEL_CONFIG = types.GenerationConfig(
    temperature=1,
    max_output_tokens=65536,  # Max for gemini-2.5-flash to avoid truncation
    top_p=0.95,
    top_k=40,
)

# Safety settings to disable all user-controllable content filtering
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# --- API Retry Configuration ---
MAX_API_RETRIES = 3
API_RETRY_BACKOFF_FACTOR = 2  # Base seconds for backoff (e.g., 2s, 4s, 8s)

# --- Formatting and Naming Conventions ---
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT_FOR_FOLDER = "%Y%m%d"

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
