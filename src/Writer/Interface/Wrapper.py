#!/usr/bin/python3

import os
import time
import json
import random
import platform
import re
import signal
from urllib.parse import parse_qs, urlparse

# Import Prompts to access the new JSON_PARSE_ERROR template
import Writer.Config
import Writer.Prompts
from Writer.PrintUtils import Logger

# --- Langchain Provider Imports ---
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_models import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_groq import ChatGroq
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import AzureChatOpenAI, ChatOpenAI

# --- Custom Provider Imports ---


# Whitelist of supported bindable parameters for each provider to prevent 422 errors.
SAFE_PARAMS = {
    "google": ["temperature", "top_p", "top_k", "max_output_tokens", "response_mime_type"],
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
        self.History: list = []
        self.LoadModels(Models)

    def GetModelAndProvider(self, _Model: str) -> (str, str, str, dict):
        """
        Parses a model string like 'Provider://Model@Host?param1=val1' using robust string splitting.
        """
        if "://" not in _Model:
            return "ollama", _Model, "localhost:11434", {}

        parsed_url = urlparse(_Model)
        provider = parsed_url.scheme
        model_part = parsed_url.netloc + parsed_url.path
        
        provider_model = model_part
        host = None
        if "@" in model_part:
            provider_model, host = model_part.split("@", 1)

        if provider == 'ollama' and not host:
            host = 'localhost:11434'

        flat_params = {}
        if parsed_url.query:
            for key, values in parse_qs(parsed_url.query).items():
                val = values[0]
                try:
                    if val.isdigit() and '.' not in val:
                        flat_params[key] = int(val)
                    else:
                        flat_params[key] = float(val)
                except ValueError:
                    if val.lower() in ['true', 'false']:
                        flat_params[key] = val.lower() == 'true'
                    else:
                        flat_params[key] = val

        return provider, provider_model, host, flat_params


    def LoadModels(self, Models: list):
        _Logger = Logger()
        for Model in list(set(Models)): # Use set to avoid redundant loads
            base_model_uri = Model.split('?')[0]
            if base_model_uri in self.Clients:
                continue

            Provider, ProviderModel, ModelHost, ModelOptions = self.GetModelAndProvider(Model)
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
                else:
                    raise ValueError(f"Model Provider '{Provider}' for '{Model}' is not supported.")

                _Logger.Log(f"Successfully verified config for '{base_model_uri}'.", 3)
            except Exception as e:
                _Logger.Log(f"CRITICAL: Failed to load config for model '{Model}'. Error: {e}", 7)

    def SafeGenerateText(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _Format: str = None, min_word_count_target: int = 50) -> list:
        _Messages = [msg for msg in _Messages if msg.get("content", "").strip()]
        max_tokens_override = int(min_word_count_target * 5)
        NewMsgHistory = self.ChatAndStreamResponse(_Logger, _Messages, _Model, _SeedOverride, _Format, max_tokens_override=max_tokens_override)
        last_response_text = self.GetLastMessageText(NewMsgHistory)
        word_count = len(re.findall(r'\b\w+\b', last_response_text))

        if not last_response_text.strip() or word_count < min_word_count_target or "[ERROR:" in last_response_text:
            log_reason = "empty response" if not last_response_text.strip() else "error in response" if "[ERROR:" in last_response_text else f"response too short ({word_count} words, target: {min_word_count_target})"
            _Logger.Log(f"SafeGenerateText: Generation failed ({log_reason}). Forcing a retry...", 7)

            if NewMsgHistory and NewMsgHistory[-1].get("role") == "assistant":
                NewMsgHistory.pop()

            forceful_retry_prompt = f"The previous response was insufficient. You MUST generate a detailed and comprehensive response of AT LEAST {min_word_count_target} words. Do not stop writing until you have met this requirement. Fulfill the original request completely and at the required length."
            NewMsgHistory.append(self.BuildUserQuery(forceful_retry_prompt))

            max_tokens_override_retry = int(min_word_count_target * 8)
            NewMsgHistory = self.ChatAndStreamResponse(_Logger, NewMsgHistory, _Model, random.randint(0, 99999), _Format, max_tokens_override=max_tokens_override_retry)

        return NewMsgHistory

    def SafeGenerateJSON(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _RequiredAttribs: list = [], _MaxRetries: int = 3) -> (list, dict):
        max_tokens_override = 8192
        messages_copy = list(_Messages)
        for attempt in range(_MaxRetries):
            current_seed = _SeedOverride if _SeedOverride != -1 and attempt == 0 else random.randint(0, 99999)
            ResponseHistory = self.ChatAndStreamResponse(_Logger, messages_copy, _Model, current_seed, _Format="json", max_tokens_override=max_tokens_override)
            RawResponse = self.GetLastMessageText(ResponseHistory)
            try:
                if '```json' in RawResponse:
                    json_text_match = re.search(r'```json\s*([\s\S]+?)\s*```', RawResponse)
                    json_text = json_text_match.group(1) if json_text_match else RawResponse
                else:
                    start_brace = RawResponse.find('{')
                    end_brace = RawResponse.rfind('}')
                    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
                        json_text = RawResponse[start_brace : end_brace + 1]
                    else:
                        json_text = RawResponse
                
                JSONResponse = json.loads(json_text)
                missing_attribs = [attr for attr in _RequiredAttribs if attr not in JSONResponse]
                if missing_attribs:
                    raise KeyError(f"Required attribute(s) '{', '.join(missing_attribs)}' not in JSON response.")
                return ResponseHistory, JSONResponse
            except (json.JSONDecodeError, KeyError) as e:
                log_message = f"JSON Error (Attempt {attempt + 1}/{_MaxRetries}): {e}."
                if Writer.Config.DEBUG:
                    log_message += f"\n--- Faulty Response Text ---\n{RawResponse}\n--------------------------"
                _Logger.Log(log_message, 7)

                messages_copy = list(ResponseHistory)
                if messages_copy and messages_copy[-1].get("role") == "assistant":
                    messages_copy.pop()

                error_correction_prompt = Writer.Prompts.JSON_PARSE_ERROR.format(_Error=str(e))
                messages_copy.append(self.BuildUserQuery(error_correction_prompt))
                continue

        _Logger.Log(f"CRITICAL: Failed to generate valid JSON after {_MaxRetries} attempts. Returning empty dictionary.", 7)
        return messages_copy, {}


    def ChatAndStreamResponse(self, _Logger: Logger, _Messages: list, _Model: str, _SeedOverride: int = -1, _Format: str = None, max_tokens_override: int = None) -> list:
        Provider, ProviderModel, ModelHost, ModelOptions = self.GetModelAndProvider(_Model)
        
        # --- THE CORRECT FIX ---
        # This line ensures we are always using a string as the key, not a list.
        base_model_uri = _Model.split('?')[0]

        if not self.Clients.get(base_model_uri):
             _Logger.Log(f"Model client for '{base_model_uri}' not loaded. Attempting to load now.", 6)
             self.LoadModels([_Model])

        client = self.Clients.get(base_model_uri)
        if not client:
            _Logger.Log(f"Model client for '{base_model_uri}' could not be loaded or created. Aborting.", 7)
            return _Messages + [{"role": "assistant", "content": f"[ERROR: Model {base_model_uri} not loaded.]"}]

        if _SeedOverride != -1:
            ModelOptions['seed'] = _SeedOverride
        elif 'seed' not in ModelOptions and Writer.Config.SEED != -1:
            ModelOptions['seed'] = Writer.Config.SEED

        if _Format and _Format.lower() == 'json':
            if Provider == 'ollama':
                ModelOptions['format'] = 'json'
            elif Provider == 'google':
                ModelOptions['response_mime_type'] = 'application/json'

        if max_tokens_override is not None:
            if Provider == 'ollama':
                ModelOptions['num_predict'] = max_tokens_override
            elif Provider == 'google':
                ModelOptions['max_output_tokens'] = max_tokens_override
            else:
                ModelOptions['max_tokens'] = max_tokens_override


        provider_safe_params = SAFE_PARAMS.get(Provider, [])
        filtered_options = {k: v for k, v in ModelOptions.items() if k in provider_safe_params}

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
        timeout_duration = Writer.Config.OLLAMA_TIMEOUT if Provider == 'ollama' else Writer.Config.DEFAULT_TIMEOUT

        if platform.system() != "Windows":
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_duration)

        try:
            if Provider == 'google':
                generation_config = {k: v for k, v in filtered_options.items() if k in SAFE_PARAMS['google']}
                stream = client.stream(langchain_messages, generation_config=generation_config)
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
            full_response = f"[ERROR: Generation failed. {e}]"
            _Logger.Log(f"CRITICAL: Exception during LLM call to '{_Model}': {e}", 7)
        finally:
            if platform.system() != "Windows":
                signal.alarm(0)

        _Logger.Log(f"Generated response in {time.time() - start_time:.2f}s", 4)
        _Messages.append({"role": "assistant", "content": full_response})
        return _Messages

    def BuildUserQuery(self, _Query: str) -> dict:
        return {"role": "user", "content": _Query}

    def BuildSystemQuery(self, _Query: str) -> dict:
        return {"role": "system", "content": _Query}

    def BuildAssistantQuery(self, _Query: str) -> dict:
        return {"role": "assistant", "content": _Query}

    def GetLastMessageText(self, _Messages: list) -> str:
        return _Messages[-1].get("content", "") if _Messages else ""
