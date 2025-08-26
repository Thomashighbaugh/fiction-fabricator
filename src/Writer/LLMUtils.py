# File: Writer/LLMUtils.py
# Purpose: Centralized utility functions for LLM discovery and selection.

import os
import sys

# Add project root to path for imports to ensure this utility can be called from any script.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import Writer.Config
from Writer.PrintUtils import Logger

def get_ollama_models(logger: Logger):
    """Queries local Ollama for available models."""
    try:
        import ollama
        logger.Log("Querying Ollama for local models...", 1)
        models_data = ollama.list().get("models", [])
        available_models = [f"ollama://{model.get('name') or model.get('model')}" for model in models_data if model.get('name') or model.get('model')]
        logger.Log(f"Found {len(available_models)} Ollama models.", 3)
        return available_models
    except ImportError:
        logger.Log("'ollama' library not installed. Skipping Ollama provider.", 6)
        return []
    except Exception as e:
        logger.Log(f"Could not get Ollama models. (Error: {e})", 6)
        return []

def get_google_models(logger: Logger):
    """Queries Google for available Gemini models."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.Log("Google provider skipped: GOOGLE_API_KEY not found in environment.", 1)
        return []
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        logger.Log("Querying Google for available Gemini models...", 1)
        available = [f"google://{m.name.replace('models/', '')}" for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        logger.Log(f"Found {len(available)} Google models.", 3)
        return available
    except ImportError:
        logger.Log("'google-generativeai' library not installed. Skipping Google provider.", 6)
        return []
    except Exception as e:
        logger.Log(f"Failed to query Google models. (Error: {e})", 6)
        return []

def get_groq_models(logger: Logger):
    """Queries Groq for available models and returns groq:// URIs.

    Supports optional GROQ_API_BASE environment variable for proxy/alt routing (used only at runtime).
    """
    if not os.environ.get("GROQ_API_KEY"):
        logger.Log("Groq provider skipped: GROQ_API_KEY not found in environment.", 1)
        return []
    try:
        from groq import Groq
        logger.Log("Querying Groq for available models...", 1)
        client = Groq()
        models = client.models.list().data
        logger.Log(f"Found {len(models)} Groq models.", 3)
        base_override = os.environ.get("GROQ_API_BASE") or os.environ.get("GROQ_API_BASE_URL")
        if base_override:
            logger.Log(f"GROQ_API_BASE override detected: {base_override}", 2)
        return [f"groq://{model.id}" for model in models]
    except ImportError:
        logger.Log("'groq' library not installed. Skipping Groq provider.", 6)
        return []
    except Exception as e:
        logger.Log(f"Failed to query Groq models. (Error: {e})", 6)
        return []

def get_mistral_models(logger: Logger):
    """Queries MistralAI for available models."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        logger.Log("MistralAI provider skipped: MISTRAL_API_KEY not found in environment.", 1)
        return []
    try:
        from mistralai.client import MistralClient
        logger.Log("Querying MistralAI for available models...", 1)
        client = MistralClient(api_key=api_key)
        models_data = client.list_models().data
        known_chat_prefixes = ['mistral-large', 'mistral-medium', 'mistral-small', 'open-mistral', 'open-mixtral']
        available_models = [f"mistralai://{model.id}" for model in models_data if any(model.id.startswith(prefix) for prefix in known_chat_prefixes)]
        logger.Log(f"Found {len(available_models)} compatible MistralAI models.", 3)
        return available_models
    except ImportError:
        logger.Log("'mistralai' library not installed. Skipping MistralAI provider.", 6)
        return []
    except Exception as e:
        logger.Log(f"Failed to query MistralAI models. (Error: {e})", 6)
        return []

def get_nvidia_models(logger: Logger):
    """Reads the user-defined NVIDIA models from config.ini."""
    if not os.environ.get("NVIDIA_API_KEY"):
        logger.Log("NVIDIA provider skipped: NVIDIA_API_KEY not found in environment.", 1)
        return []

    logger.Log("Reading manual NVIDIA model list from config.ini...", 1)
    model_list_str = Writer.Config.NVIDIA_AVAILABLE_MODELS
    if not model_list_str:
        logger.Log("NVIDIA provider skipped: No models listed in config.ini under [NVIDIA_SETTINGS] -> 'available_models'.", 6)
        return []

    model_names = [name.strip() for name in model_list_str.split(',') if name.strip()]
    available_models = [f"nvidia://{name}" for name in model_names]
    logger.Log(f"Found {len(available_models)} NVIDIA models in config.ini.", 3)
    return available_models

def get_azure_models(logger: Logger):
    """Queries Azure for available models."""
    if not os.environ.get("AZURE_OPENAI_API_KEY") or not os.environ.get("AZURE_OPENAI_ENDPOINT"):
        logger.Log("Azure provider skipped: AZURE_OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT not found in environment.", 1)
        return []
    try:
        from openai import AzureOpenAI
        logger.Log("Querying Azure for available models...", 1)
        client = AzureOpenAI(api_version="2024-05-01-preview")
        models = client.models.list().data
        logger.Log(f"Found {len(models)} Azure models.", 3)
        return [f"azure://{model.id}" for model in models]
    except ImportError:
        logger.Log("'openai' library not installed. Skipping Azure provider.", 6)
        return []
    except Exception as e:
        logger.Log(f"Failed to query Azure models. (Error: {e})", 6)
        return []

def get_github_models(logger: Logger):
    """Returns a static list of GitHub Marketplace / Azure OpenAI aggregator models (includes Grok)."""
    if not os.environ.get("GITHUB_ACCESS_TOKEN") or not os.environ.get("AZURE_OPENAI_ENDPOINT"):
        logger.Log("GitHub provider skipped: GITHUB_ACCESS_TOKEN or AZURE_OPENAI_ENDPOINT not found in environment.", 1)
        return []
    logger.Log("Loading GitHub static model list...", 1)
    deployment_names = [
        "openai/o1", "openai/o1-mini", "openai/o1-preview", "openai/gpt-4o-mini", "openai/gpt-4o",
        "deepseek/DeepSeek-V3-0324", "deepseek/DeepSeek-R1",
        "ai21-labs/AI21-Jamba-1.5-Large", "ai21-labs/AI21-Jamba-1.5-Mini",
        "cohere/cohere-command-r", "cohere/cohere-command-r-plus", "cohere/cohere-command-a",
        "mistral-ai/Mistral-Nemo", "mistral-ai/Mistral-Small",
        "mistral-ai/Mistral-Large-2411", "mistral-ai/Codestral-22B-v0.1",
        "meta/Llama-3.2-11B-Vision-Instruct", "meta/Llama-3.2-90B-Vision-Instruct",
        "meta/Llama-3.3-70B-Instruct", "meta/Llama-3.1-8B-Instruct",
        "meta/Llama-3.1-70B-Instruct", "meta/Llama-3.1-405B-Instruct",
        "meta/Llama-3-8B-Instruct", "meta/Llama-3-70B-Instruct",
        "microsoft/Phi-4", "microsoft/Phi-3.5-MoE-instruct",
        "microsoft/Phi-3.5-mini-instruct", "microsoft/Phi-3.5-vision-instruct",
        "microsoft/Phi-3-mini-4k-instruct", "microsoft/Phi-3-mini-128k-instruct",
        "microsoft/Phi-3-small-8k-instruct", "microsoft/Phi-3-small-128k-instruct",
        "microsoft/Phi-3-medium-4k-instruct", "microsoft/Phi-3-medium-128k-instruct",
        "xai/grok-3",
        "core42/jais-30b-chat"
    ]
    available_models = [f"github://{name}" for name in deployment_names]
    logger.Log(f"Found {len(available_models)} GitHub models.", 3)
    return available_models

def get_cohere_models(logger: Logger):
    """Returns a static list of Cohere chat-capable models if API key present (listing endpoint not exposed via SDK)."""
    if not os.environ.get("COHERE_API_KEY"):
        logger.Log("Cohere provider skipped: COHERE_API_KEY not found in environment.", 1)
        return []
    # Based on Cohere model docs (command family + aya). We focus on command* and aya* chat models.
    model_ids = [
        "command-a-03-2025", "command-r7b-12-2024", "command-a-vision-07-2025", "command-r-plus-04-2024",
        "command-r-plus", "command-r-08-2024", "command-r-03-2024", "command-r", "command", "command-nightly",
        "command-light", "command-light-nightly", "c4ai-aya-expanse-8b", "c4ai-aya-expanse-32b", "c4ai-aya-vision-8b", "c4ai-aya-vision-32b"
    ]
    available = [f"cohere://{mid}" for mid in model_ids]
    logger.Log(f"Loaded {len(available)} Cohere models (static list).", 3)
    return available

def get_together_models(logger: Logger):
    """Attempts to call Together list models endpoint via requests; falls back to curated list."""
    if not os.environ.get("TOGETHERAI_API_KEY"):
        logger.Log("Together provider skipped: TOGETHERAI_API_KEY not found in environment.", 1)
        return []
    import requests
    headers = {"Authorization": f"Bearer {os.environ.get('TOGETHERAI_API_KEY')}", "Content-Type": "application/json"}
    try:
        resp = requests.get("https://api.together.xyz/v1/models", headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            models = data.get("data", [])
            chat_models = [m.get("id") for m in models if m.get("type", "").lower() in ("chat", "llm", "text")]
            available = [f"together://{m}" for m in chat_models if m]
            logger.Log(f"Found {len(available)} Together models via API.", 3)
            return available
        else:
            logger.Log(f"Together API list models failed (status {resp.status_code}). Using fallback list.", 6)
    except Exception as e:
        logger.Log(f"Together model listing error ({e}). Using fallback list.", 6)
    fallback = [
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "meta-llama/Llama-3.2-11B-Vision-Instruct", "meta-llama/Llama-3.2-90B-Vision-Instruct",
        "deepseek-ai/DeepSeek-V3", "deepseek-ai/DeepSeek-R1", "Qwen/Qwen2.5-72B-Instruct",
        "google/gemma-2-27b-it", "mistralai/Mistral-7B-Instruct-v0.3", "mistralai/Mixtral-8x22B-Instruct-v0.1"
    ]
    available = [f"together://{m}" for m in fallback]
    logger.Log(f"Loaded {len(available)} Together fallback models.", 3)
    return available

def get_cerebras_models(logger: Logger):
    """Provides a static list of common Cerebras deployed models (SDK doesn't expose list without account context)."""
    if not os.environ.get("CEREBRAS_API_KEY"):
        logger.Log("Cerebras provider skipped: CEREBRAS_API_KEY not found in environment.", 1)
        return []
    model_ids = [
        "llama3.1-8b", "llama3.1-70b", "llama3.1-405b", "llama3.2-1b", "llama3.2-3b", "llama3.2-11b-vision", "llama3.2-90b-vision"
    ]
    available = [f"cerebras://{mid}" for mid in model_ids]
    logger.Log(f"Loaded {len(available)} Cerebras models (static list).", 3)
    return available

def get_llm_selection_menu_for_tool(logger: Logger, tool_name: str = "Tool") -> str:
    """
    Queries all providers, presents a sorted menu to the user, and returns the chosen model URI.
    """
    print(f"\n--- Querying available models from configured providers for {tool_name}... ---")
    all_models = []
    all_models.extend(get_google_models(logger))
    all_models.extend(get_groq_models(logger))
    all_models.extend(get_mistral_models(logger))
    all_models.extend(get_nvidia_models(logger))
    # Additional providers
    all_models.extend(get_cohere_models(logger))
    all_models.extend(get_together_models(logger))
    all_models.extend(get_cerebras_models(logger))
    # GitHub Marketplace / Azure OpenAI aggregator models (static list)
    all_models.extend(get_github_models(logger))
    all_models.extend(get_ollama_models(logger))
    all_models.extend(get_azure_models(logger))

    if not all_models:
        logger.Log("No models found from any provider. Please check API keys in .env and model lists in config.ini. Aborting.", 7)
        return None

    print(f"\n--- {tool_name} LLM Selection ---")
    print("Please select the model for this task:")
    sorted_models = sorted(list(set(all_models)))
    for i, model in enumerate(sorted_models):
        print(f"[{i+1}] {model}")

    while True:
        try:
            choice = input(f"> ").strip().lower()
            if choice.isdigit() and 1 <= int(choice) <= len(sorted_models):
                selected_model = sorted_models[int(choice) - 1]
                print(f"Selected: {selected_model}")
                return selected_model
            else:
                print("Invalid choice. Please enter a number from the list.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter a number corresponding to your choice.")
        except (KeyboardInterrupt, EOFError):
             print("\nSelection cancelled by user.")
             return None
