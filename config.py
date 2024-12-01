# goat_storytelling_agent/config.py
import os

# The GLHF authentication token is sourced from the environment
GLHF_AUTH_TOKEN = os.environ.get("GLHF_AUTH_TOKEN")

# OpenAI model name, initialized to a default but changed by user selection
MODEL_NAME = "hf:meta-llama/Meta-Llama-3.1-405B-Instruct"

# Timeout for LLM calls (in seconds)
TIMEOUT = 300

# Retry wait time
RETRY_WAIT = 300
