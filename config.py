# goat_storytelling_agent/config.py
import os

# Ollama model name
MODEL_NAME = "huggingface.co/mradermacher/Hermes3-Lumimaid-uncensored-GGUF:latest"
SUMMARY_MODEL_NAME = "huggingface.co/Novaciano/Llama-3.2-3b-NSFW_Aesir_Uncensored-GGUF:latest"

# Timeout for LLM calls (in seconds)
TIMEOUT = 300  # Increased timeout

# Retry wait time
RETRY_WAIT = 30