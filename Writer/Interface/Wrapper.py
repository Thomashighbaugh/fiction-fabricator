#!/usr/bin/python3

import os
import time
import json
import random
import inspect
import signal
import platform
import re
from urllib.parse import parse_qs

import Writer.Config
from Writer.PrintUtils import Logger

# --- Langchain Provider Imports ---
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.chat_models import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_groq import ChatGroq
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import AzureChatOpenAI, ChatOpenAI

# Note: dotenv is loaded at the main entry point in Write.py.

# Whitelist of supported bindable parameters for each provider to prevent 422 errors.
SAFE_PARAMS = {
    "google": ["temperature", "top_p", "top_k", "max_output_tokens", "seed", "response_mime_type"],
    "groq": ["temperature", "top_p", "max_tokens", "seed"],
    "nvidia": ["temperature", "top_p", "max_tokens", "seed"],
    "github": ["temperature", "top_p", "max_tokens"],
    "ollama": ["temperature", "top_p", "top_k", "seed", "format", "num_predict"],
    "mistralai": ["temperature", "top_p", "max_tokens"]
}


class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

class Interface:

    def __init__(self, Models: list = []):
        self.Clients: dict = {}
        self.History = []
        self.LoadModels(Models)

    def GetModelAndProvider(self, _Model: str) -> (str, str, str, dict):
        """
        Parses a model string like 'Provider://Model@Host?param1=val1' using robust string splitting.
        """
        if "://" not in _Model:
            return "ollama", _Model, "localhost:11434", {}

        provider_part, rest = _Model.split("://", 1)
        Provider = provider_part
        main_part = rest
        query_part = ""
        if "?" in rest:
            main_part, query_part = rest.split("?", 1)

        Host = None
        ProviderModel = main_part
        if "@" in main_part:
            ProviderModel, Host = main_part.split("@", 1)

        if Provider == 'ollama' and not Host:
            Host = 'localhost:11434'

        FlatParams = {}
        if query_part:
            for key, values in parse_qs(query_part).items():
                val = values[0]
                try:
                    if val.isdigit() and '.' not in val:
                        FlatParams[key] = int(val)
                    else:
                        FlatParams[key] = float(val)
                except ValueError:
                    if val.lower() in ['true', 'false']:
                        FlatParams[key] = val.lower() == 'true'
                    else:
                        FlatParams[key] = val

        return Provider, ProviderModel, Host, FlatParams

    def LoadModels(self, Models: list):
        for Model in Models:
            base_model_uri = Model.split('?')[0]
            if base_model_uri in self.Clients:
                continue

            Provider, ProviderModel, ModelHost, ModelOptions = self.GetModelAndProvider(Model)
            _Logger = Logger()
            _Logger.Log(f"Verifying config for Model '{ProviderModel}' from '{Provider}'", 2)
            try:
                if Provider == "ollama":
                    self.Clients[base_model_uri] = ChatOllama(model=ProviderModel, base_url=f"http://{ModelHost}" if ModelHost else "http://localhost:11434")
                elif Provider == "google":
                    self.Clients[base_model_uri] = ChatGoogleGenerativeAI(model=ProviderModel, convert_system_message_to_human=True)
                elif Provider == "mistralai":
                    self.Clients[base_model_uri] = ChatMistralAI(model=ProviderModel)
                elif Provider == "groq":
                    self.Clients[base_model_uri] = ChatGroq(model_name=ProviderModel)
                elif Provider == "nvidia":
                     self.Clients[base_model_uri] = ChatNVIDIA(model=ProviderModel, base_url=os.environ.get("NVIDIA_BASE_URL") or Writer.Config.NVIDIA_BASE_URL)
                elif Provider == "github":
                    if not os.environ.get("GITHUB_ACCESS_TOKEN") or not os.environ.get("AZURE_OPENAI_ENDPOINT"):
                        raise ValueError("GITHUB_ACCESS_TOKEN or AZURE_OPENAI_ENDPOINT not in environment variables.")
                    self.Clients[base_model_uri] = "GITHUB_PLACEHOLDER"
                else:
                    raise ValueError(f"Model Provider '{Provider}' for '{Model}' is not supported.")

                _Logger.Log(f"Successfully verified config for '{base_model_uri}'.", 3)
            except Exception as e:
                _Logger.Log(f"CRITICAL: Failed to verify config for model '{Model}'. Error: {e}", 7)

    def SafeGenerateText(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _Format: str = None, min_word_count_target: int = 50) -> list:
        _Messages = [msg for msg in _Messages if msg.get("content", "").strip()]

        # Dynamically set max_tokens to give the model enough headroom.
        # Assume ~2.5 tokens per word for a generous buffer.
        max_tokens_override = int(min_word_count_target * 2.5)


        # --- First Attempt ---
        NewMsgHistory = self.ChatAndStreamResponse(_Logger, _Messages, _Model, _SeedOverride, _Format, max_tokens_override=max_tokens_override)

        last_response_text = self.GetLastMessageText(NewMsgHistory)
        word_count = len(re.findall(r'\b\w+\b', last_response_text))

        # --- Check and Retry Logic ---
        if not last_response_text.strip() or word_count < min_word_count_target:
            if not last_response_text.strip():
                _Logger.Log("SafeGenerateText: Generation failed (empty). Retrying...", 7)
            else:
                _Logger.Log(f"SafeGenerateText: Generation failed (short response: {word_count} words, target: {min_word_count_target}). Retrying...", 7)

            if NewMsgHistory and NewMsgHistory[-1].get("role") == "assistant":
                NewMsgHistory.pop() # Remove the failed assistant response

            forceful_retry_prompt = f"The previous response was too short. It is crucial that you generate a detailed and comprehensive, multi-paragraph response that is AT LEAST {min_word_count_target} words long. Do not stop writing until you have met this requirement. Fulfill the original request completely and at the required length."
            NewMsgHistory.append(self.BuildUserQuery(forceful_retry_prompt))

            # --- Second Attempt ---
            # Increase the max_tokens even more for the retry
            max_tokens_override_retry = int(min_word_count_target * 4)
            NewMsgHistory = self.ChatAndStreamResponse(_Logger, NewMsgHistory, _Model, random.randint(0, 99999), _Format, max_tokens_override=max_tokens_override_retry)

            last_response_text = self.GetLastMessageText(NewMsgHistory)
            word_count = len(re.findall(r'\b\w+\b', last_response_text))

            # --- Final Check with User Interaction ---
            if not last_response_text.strip() or word_count < min_word_count_target:
                _Logger.Log(f"SafeGenerateText: Retry also failed to meet word count (got {word_count}, target {min_word_count_target}).", 6)
                while True:
                    user_choice = input("Do you want to [c]ontinue with the short response or [t]ry again? (c/t): ").lower()
                    if user_choice == 't':
                        if NewMsgHistory and NewMsgHistory[-1].get("role") == "assistant":
                            NewMsgHistory.pop() # Remove the second failed response

                        NewMsgHistory.append(self.BuildUserQuery(forceful_retry_prompt))
                        NewMsgHistory = self.ChatAndStreamResponse(_Logger, NewMsgHistory, _Model, random.randint(0, 99999), _Format, max_tokens_override=max_tokens_override_retry)
                        last_response_text = self.GetLastMessageText(NewMsgHistory)
                        word_count = len(re.findall(r'\b\w+\b', last_response_text))
                        if word_count >= min_word_count_target:
                            _Logger.Log("Success on manual retry.", 5)
                            break
                        else:
                             _Logger.Log(f"Manual retry also failed (got {word_count}).", 6)
                    elif user_choice == 'c':
                        _Logger.Log("User chose to continue with the short response.", 4)
                        break
                    else:
                        print("Invalid input. Please enter 'c' or 't'.")

        return NewMsgHistory

    def SafeGenerateJSON(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _RequiredAttribs: list = []) -> (list, dict):
        while True:
            # For JSON, we don't need a word count, but we still need a reasonable max_tokens
            max_tokens_override = 2048
            ResponseHistory = self.ChatAndStreamResponse(_Logger, _Messages, _Model, _SeedOverride, _Format="json", max_tokens_override=max_tokens_override)
            try:
                RawResponse = self.GetLastMessageText(ResponseHistory).replace("```json", "").replace("```", "").strip()
                JSONResponse = json.loads(RawResponse)
                for _Attrib in _RequiredAttribs:
                    if _Attrib not in JSONResponse:
                        raise KeyError(f"Required attribute '{_Attrib}' not in JSON response.")
                return ResponseHistory, JSONResponse
            except (json.JSONDecodeError, KeyError) as e:
                _Logger.Log(f"JSON Error: {e}. Retrying...", 7)
                if ResponseHistory and ResponseHistory[-1].get("role") == "assistant":
                    ResponseHistory.pop()
                _SeedOverride = random.randint(0, 99999)

    def ChatAndStreamResponse(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _Format: str = None, max_tokens_override: int = None) -> list:
        Provider, ProviderModel, ModelHost, ModelOptions = self.GetModelAndProvider(_Model)
        base_model_uri = _Model.split('?')[0]

        if _SeedOverride != -1:
            ModelOptions['seed'] = _SeedOverride
        elif 'seed' not in ModelOptions and Writer.Config.SEED != -1:
            ModelOptions['seed'] = Writer.Config.SEED

        if _Format and _Format.lower() == 'json':
            if Provider == 'ollama':
                ModelOptions['format'] = 'json'
            elif Provider == 'google':
                ModelOptions['response_mime_type'] = 'application/json'

        # Set max_tokens override if provided
        if max_tokens_override is not None:
            if Provider == 'ollama':
                ModelOptions['num_predict'] = max_tokens_override
            elif Provider == 'google':
                ModelOptions['max_output_tokens'] = max_tokens_override
            else:
                ModelOptions['max_tokens'] = max_tokens_override


        client = None
        if Provider == "github":
            try:
                github_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
                github_token = os.environ.get("GITHUB_ACCESS_TOKEN")

                if ProviderModel.startswith("mistral-ai/"):
                    _Logger.Log(f"Using MistralAI client for GitHub model: {ProviderModel}", 1)
                    client = ChatMistralAI(endpoint=github_endpoint, api_key=github_token, model=ProviderModel)
                elif ProviderModel.startswith(("openai/", "cohere/", "xai/", "deepseek/")):
                    _Logger.Log(f"Using OpenAI-compatible client for GitHub model: {ProviderModel}", 1)
                    client = ChatOpenAI(base_url=github_endpoint, api_key=github_token, model=ProviderModel)
                else:
                    _Logger.Log(f"Using AzureOpenAI client for GitHub model: {ProviderModel}", 1)
                    client = AzureChatOpenAI(azure_endpoint=github_endpoint, api_key=github_token, azure_deployment=ProviderModel, api_version=Writer.Config.GITHUB_API_VERSION)
            except Exception as e:
                _Logger.Log(f"Failed to create on-demand GitHub client for '{ProviderModel}'. Error: {e}", 7)
                _Messages.append({"role": "assistant", "content": f"[ERROR: Failed to create GitHub client.]"})
                return _Messages
        else:
            client = self.Clients.get(base_model_uri)

        if not client:
            _Logger.Log(f"Model client for '{base_model_uri}' could not be loaded or created. Aborting.", 7)
            _Messages.append({"role": "assistant", "content": f"[ERROR: Model {base_model_uri} not loaded.]"})
            return _Messages

        provider_safe_params = SAFE_PARAMS.get(Provider, [])
        filtered_options = {k: v for k, v in ModelOptions.items() if k in provider_safe_params}

        # Handle provider-specific parameter name changes if they weren't caught by the override logic
        if Provider == 'ollama' and 'max_tokens' in filtered_options:
            filtered_options['num_predict'] = filtered_options.pop('max_tokens')
        if Provider == 'google' and 'max_tokens' in filtered_options:
            filtered_options['max_output_tokens'] = filtered_options.pop('max_tokens')


        _Logger.Log(f"Using Model '{ProviderModel}' from '{Provider}'", 4)
        if Writer.Config.DEBUG:
            _Logger.Log(f"Message History:\n{json.dumps(_Messages, indent=2)}", 1)
            if filtered_options:
                _Logger.Log(f"Applying SAFE Params for {Provider}: {filtered_options}", 1)

        langchain_messages = [SystemMessage(content=msg["content"]) if msg["role"] == "system" else AIMessage(content=msg["content"]) if msg["role"] == "assistant" else HumanMessage(content=msg["content"]) for msg in _Messages]

        start_time = time.time()
        full_response = ""

        # Determine appropriate timeout
        timeout_duration = Writer.Config.OLLAMA_TIMEOUT if Provider == 'ollama' else Writer.Config.DEFAULT_TIMEOUT

        # Set up signal handler for timeout, only on non-Windows systems
        if platform.system() != "Windows":
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_duration)

        try:
            if Provider == 'ollama':
                stream = client.stream(langchain_messages, options=filtered_options)
            elif Provider == 'google':
                gen_config_keys = ["temperature", "top_p", "top_k", "max_output_tokens", "response_mime_type"]
                generation_config = {k: v for k, v in filtered_options.items() if k in gen_config_keys}

                seed_to_bind = {}
                if 'seed' in filtered_options:
                    seed_to_bind['seed'] = filtered_options['seed']

                bound_client = client.bind(**seed_to_bind) if seed_to_bind else client
                stream = bound_client.stream(langchain_messages, generation_config=generation_config)
            else:
                bound_client = client.bind(**filtered_options) if filtered_options else client
                stream = bound_client.stream(langchain_messages)

            _Logger.Log(f"Streaming response (timeout set to {timeout_duration}s)...", 0)
            for chunk in stream:
                chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
                full_response += chunk_text
                print(chunk_text, end="", flush=True)
            print("\n")
        except TimeoutException:
            full_response = f"[ERROR: Generation timed out after {timeout_duration} seconds.]"
            _Logger.Log(f"CRITICAL: LLM call to '{_Model}' timed out.", 7)
        except Exception as e:
            _Logger.Log(f"CRITICAL: Exception during LLM call to '{_Model}': {e}", 7)
            full_response = f"[ERROR: Generation failed. {e}]"
        finally:
            # Disable the alarm
            if platform.system() != "Windows":
                signal.alarm(0)

        elapsed = time.time() - start_time
        _Logger.Log(f"Generated response in {elapsed:.2f}s", 4)
        _Messages.append({"role": "assistant", "content": full_response})
        return _Messages

    def BuildUserQuery(self, _Query: str) -> dict:
        return {"role": "user", "content": _Query}

    def BuildSystemQuery(self, _Query: str) -> dict:
        return {"role": "system", "content": _Query}

    def BuildAssistantQuery(self, _Query: str) -> dict:
        return {"role": "assistant", "content": _Query}

    def GetLastMessageText(self, _Messages: list) -> str:
        if not _Messages:
            return ""
        return _Messages[-1].get("content", "")
