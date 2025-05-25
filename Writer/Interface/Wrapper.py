# File: AIStoryWriter/Writer/Interface/Wrapper.py
# Purpose: Provides a unified interface for interacting with various LLM APIs,
#          handling model loading, request formatting, response streaming,
#          error handling, and logging.

import وقت # Renamed to 'time' in Python, using 'time' for standard library
import json
import os
import random
import importlib
import subprocess
import sys
import inspect
from urllib.parse import parse_qs, urlparse
from typing import List, Dict, Tuple, Optional, Any, Literal

import dotenv # Keep as is, standard library name
from .. import Config # Relative import for Config
from .. import Prompts # Relative import for Prompts
from ..PrintUtils import Logger # Relative import for Logger

# Dynamically import OpenRouter if its provider is used
# This avoids a hard dependency if OpenRouter isn't configured.
try:
    from .OpenRouter import OpenRouter
except ImportError:
    OpenRouter = None # type: ignore

# Try to import google.generativeai, will be handled by ensure_package_is_installed
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    genai = None # type: ignore
    HarmCategory = None # type: ignore
    HarmBlockThreshold = None # type: ignore

# Try to import ollama, will be handled by ensure_package_is_installed
try:
    import ollama
except ImportError:
    ollama = None # type: ignore


dotenv.load_dotenv()

class Interface:
    """
    A wrapper class to interact with different LLM providers.
    Manages model loading, API calls, streaming, and error handling.
    """
    def __init__(self, models_to_load: List[str], logger_instance: Logger):
        self.clients: Dict[str, Any] = {}
        self.logger = logger_instance
        self._load_models(models_to_load)

    def _ensure_package_is_installed(self, package_name: str) -> None:
        """Checks if a package is installed and installs it if not."""
        try:
            importlib.import_module(package_name)
            self.logger.Log(f"Package '{package_name}' is already installed.", 1)
        except ImportError:
            self.logger.Log(f"Package '{package_name}' not found. Attempting installation...", 3)
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT
                )
                self.logger.Log(f"Package '{package_name}' installed successfully.", 2)
                importlib.invalidate_caches() # Ensure new package can be imported
            except subprocess.CalledProcessError as e:
                self.logger.Log(f"Failed to install package '{package_name}'. Error: {e}", 7)
                raise ImportError(f"Could not install required package: {package_name}") from e

    def _load_models(self, models_to_load: List[str]) -> None:
        """Loads and initializes clients for the specified models."""
        unique_model_uris = list(set(models_to_load)) # Avoid loading the same URI multiple times

        for model_uri in unique_model_uris:
            if model_uri in self.clients:
                self.logger.Log(f"Model URI '{model_uri}' already loaded. Skipping.", 1)
                continue

            provider, provider_model_name, model_host, model_options = self._get_model_and_provider(model_uri)
            self.logger.Log(f"Attempting to load Model URI: '{model_uri}' (Provider: {provider}, Name: {provider_model_name}, Host: {model_host}, Options: {model_options})", 2)

            try:
                if provider == "ollama":
                    self._ensure_package_is_installed("ollama")
                    global ollama # Make sure we're using the potentially newly imported one
                    if ollama is None: ollama = importlib.import_module("ollama")

                    effective_host = model_host if model_host else Config.OLLAMA_HOST
                    ollama_client = ollama.Client(host=effective_host) # type: ignore

                    try:
                        ollama_client.show(provider_model_name)
                        self.logger.Log(f"Ollama model '{provider_model_name}' found locally at host '{effective_host}'.", 2)
                    except ollama.ResponseError as e: # type: ignore
                        if "model not found" in str(e).lower():
                            self.logger.Log(f"Ollama model '{provider_model_name}' not found at host '{effective_host}'. Attempting to pull...", 3)
                            pull_stream = ollama_client.pull(provider_model_name, stream=True)
                            for chunk in pull_stream:
                                status = chunk.get("status", "")
                                completed = chunk.get("completed", 0)
                                total = chunk.get("total", 0)
                                if total > 0 and "downloading" in status.lower():
                                    progress = (completed / total) * 100
                                    completed_gb = completed / (1024**3)
                                    total_gb = total / (1024**3)
                                    print(f"Downloading {provider_model_name}: {progress:.2f}% ({completed_gb:.2f}GB/{total_gb:.2f}GB)", end='\r', flush=True)
                                else:
                                    print(f"Pulling {provider_model_name}: {status}", end='\r', flush=True)
                            print("\nPull complete." + " "*50) # Clear line after pull
                            self.logger.Log(f"Ollama model '{provider_model_name}' pulled successfully.", 2)
                        else:
                            raise
                    self.clients[model_uri] = ollama_client

                elif provider == "google":
                    self._ensure_package_is_installed("google-generativeai")
                    global genai, HarmCategory, HarmBlockThreshold # Make sure we're using potentially newly imported
                    if genai is None: genai = importlib.import_module("google.generativeai")
                    if HarmCategory is None: HarmCategory = importlib.import_module("google.generativeai.types").HarmCategory
                    if HarmBlockThreshold is None: HarmBlockThreshold = importlib.import_module("google.generativeai.types").HarmBlockThreshold


                    google_api_key = os.environ.get("GOOGLE_API_KEY")
                    if not google_api_key:
                        self.logger.Log("GOOGLE_API_KEY not found in environment variables.", 7)
                        raise ValueError("GOOGLE_API_KEY is required for Google models.")
                    genai.configure(api_key=google_api_key) # type: ignore
                    self.clients[model_uri] = genai.GenerativeModel(model_name=provider_model_name) # type: ignore
                    self.logger.Log(f"Google model '{provider_model_name}' client initialized.", 2)

                elif provider == "openrouter":
                    if OpenRouter is None: # Check if OpenRouter class was imported
                        self.logger.Log("OpenRouter client class not available. Please ensure Writer.Interface.OpenRouter.py exists.", 7)
                        raise ImportError("OpenRouter client could not be imported.")
                    
                    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
                    if not openrouter_api_key:
                        self.logger.Log("OPENROUTER_API_KEY not found in environment variables.", 7)
                        raise ValueError("OPENROUTER_API_KEY is required for OpenRouter models.")
                    
                    self.clients[model_uri] = OpenRouter(api_key=openrouter_api_key, model=provider_model_name)
                    self.logger.Log(f"OpenRouter model '{provider_model_name}' client initialized.", 2)

                # Placeholder for other providers like OpenAI, Anthropic
                # ELIF Provider == "openai":
                #     # ... OpenAI client setup ...
                # ELIF Provider == "anthropic":
                #     # ... Anthropic client setup ...

                else:
                    self.logger.Log(f"Unsupported model provider '{provider}' for URI '{model_uri}'.", 6)
                    # Optionally, could skip this model or raise an error earlier

            except Exception as e:
                self.logger.Log(f"Failed to load model URI '{model_uri}'. Error: {e}", 7)
                # Decide if this is a critical failure or if the program can continue without this model.
                # For now, log and continue, calls using this model will fail later.

    def _get_model_and_provider(self, model_uri: str) -> Tuple[str, str, Optional[str], Optional[Dict[str, Any]]]:
        """Parses a model URI into provider, model name, host, and query parameters."""
        if "://" not in model_uri:
            # Default to Ollama if no scheme is provided
            return "ollama", model_uri, Config.OLLAMA_HOST, {}

        parsed = urlparse(model_uri)
        provider = parsed.scheme.lower()
        
        path_parts = parsed.path.strip('/').split('/')
        
        model_name_from_netloc = parsed.netloc
        model_name_from_path = path_parts[0] if path_parts and path_parts[0] else ""

        host: Optional[str] = None
        options: Dict[str, Any] = {}

        if "@" in parsed.netloc:
            model_name_from_netloc_part, host_candidate = parsed.netloc.split("@", 1)
            if provider == "ollama": # Ollama specific host handling
                model_name = model_name_from_netloc_part
                host = host_candidate if host_candidate else Config.OLLAMA_HOST
            else: # Generic case, netloc is model, path might be host or part of model
                model_name = model_name_from_netloc_part # Assume this is the model
                host = host_candidate # And this is the host
        else: # No explicit host in netloc
            model_name = parsed.netloc # Assume netloc is the model name
            if provider == "ollama":
                host = Config.OLLAMA_HOST # Default Ollama host
            # For other providers, host might be implicit or not applicable
        
        if provider == "openrouter": # OpenRouter model names can be like "provider/model"
            model_name = f"{parsed.netloc}{parsed.path}".strip('/')
            host = None # OpenRouter uses a central API endpoint

        # Parse query parameters
        raw_query_params = parse_qs(parsed.query)
        for key, value_list in raw_query_params.items():
            if value_list:
                # Attempt to convert to float or int if possible, otherwise keep as string
                try:
                    val_as_float = float(value_list[0])
                    if val_as_float.is_integer():
                        options[key] = int(val_as_float)
                    else:
                        options[key] = val_as_float
                except ValueError:
                    options[key] = value_list[0]
        
        if not model_name: # Fallback if model name is still empty
            model_name = model_uri # Use the original URI as a last resort

        return provider, model_name, host, options

    def _clean_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Removes messages with empty or whitespace-only content, except potentially the last one if it's an assistant placeholder."""
        cleaned = []
        for i, msg in enumerate(messages):
            content = msg.get("content", "").strip()
            if content or (i == len(messages) - 1 and msg.get("role") == "assistant"): # Keep last assistant msg even if empty (placeholder)
                cleaned.append(msg)
        return cleaned
    
    def SafeGenerateText(
        self,
        messages: List[Dict[str, str]],
        model_uri: str,
        seed_override: int = -1,
        output_format: Optional[Literal["json"]] = None, # Changed from _Format to output_format
        min_word_count: int = 1
    ) -> List[Dict[str, str]]:
        """
        Ensures the LLM response is not empty/whitespace and meets a minimum word count.
        Retries with new seeds and corrective prompts if necessary.
        """
        current_messages = self._clean_messages(messages)
        
        MAX_SGT_RETRIES = 3
        for attempt in range(MAX_SGT_RETRIES):
            effective_seed = Config.SEED if seed_override == -1 and attempt == 0 else random.randint(0, 99999)
            
            # Make a fresh copy for each attempt to avoid accumulating corrective prompts from previous failed attempts in THIS loop
            attempt_messages = current_messages[:] 

            generated_response_messages = self.ChatAndStreamResponse(
                attempt_messages, model_uri, effective_seed, output_format
            )
            
            last_response_text = self.GetLastMessageText(generated_response_messages)
            
            if not last_response_text.strip():
                self.logger.Log(f"SafeGenerateText (Attempt {attempt + 1}/{MAX_SGT_RETRIES}): Empty response from {model_uri}. Retrying.", 6)
                if attempt < MAX_SGT_RETRIES - 1 :
                     current_messages.append(self.BuildUserQuery("Your previous response was empty. Please provide a substantive answer according to the instructions."))
                continue

            word_count = len(last_response_text.split())
            if word_count < min_word_count:
                self.logger.Log(f"SafeGenerateText (Attempt {attempt + 1}/{MAX_SGT_RETRIES}): Response too short ({word_count} words, min {min_word_count}) for {model_uri}. Retrying.", 6)
                if attempt < MAX_SGT_RETRIES - 1:
                    current_messages.append(self.BuildUserQuery(f"Your response was too short ({word_count} words, minimum is {min_word_count}). Please elaborate and provide a more complete answer."))
                continue
            
            return generated_response_messages # Success

        self.logger.Log(f"SafeGenerateText: Failed to get adequate response from {model_uri} after {MAX_SGT_RETRIES} attempts. Returning last (possibly inadequate) response.", 7)
        # Fallback: return the last attempt's messages, even if it's not ideal
        # The caller should check the content of the last message.
        # To ensure a valid list structure is always returned:
        if not generated_response_messages or generated_response_messages[-1].get("role") != "assistant":
             # Append a placeholder error message if the structure is broken
            error_message = {"role": "assistant", "content": f"ERROR: SafeGenerateText failed to obtain a valid response after {MAX_SGT_RETRIES} retries."}
            if generated_response_messages:
                generated_response_messages.append(error_message)
            else:
                generated_response_messages = messages + [error_message] # Add to original if nothing was generated

        return generated_response_messages


    def SafeGenerateJSON(
        self,
        messages: List[Dict[str, str]],
        model_uri: str,
        seed_override: int = -1,
        required_attribs: Optional[List[str]] = None
    ) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        Ensures the LLM response is valid JSON and contains required attributes.
        Retries with error feedback if parsing fails or attributes are missing.
        """
        if required_attribs is None:
            required_attribs = []
            
        current_messages = self._clean_messages(messages)
        
        MAX_JSON_RETRIES = 3
        for attempt in range(MAX_JSON_RETRIES):
            self.logger.Log(f"SafeGenerateJSON (Attempt {attempt + 1}/{MAX_JSON_RETRIES}) for model {model_uri}...", 4)
            effective_seed = Config.SEED if seed_override == -1 and attempt == 0 else random.randint(0, 99999)

            # Use a fresh copy of messages for this attempt to avoid pollution from prior corrective prompts within this loop
            attempt_messages = current_messages[:]

            response_messages = self.ChatAndStreamResponse(
                attempt_messages, model_uri, effective_seed, output_format="json"
            )
            
            last_response_text = self.GetLastMessageText(response_messages)
            
            try:
                # Pre-process common JSON-in-markdown issues
                cleaned_json_text = last_response_text.strip()
                if cleaned_json_text.startswith("```json"):
                    cleaned_json_text = cleaned_json_text[7:]
                if cleaned_json_text.endswith("```"):
                    cleaned_json_text = cleaned_json_text[:-3]
                cleaned_json_text = cleaned_json_text.strip()

                if not cleaned_json_text:
                    raise json.JSONDecodeError("Response is empty after cleaning.", cleaned_json_text, 0)

                parsed_json = json.loads(cleaned_json_text)
                
                missing_attribs = [attr for attr in required_attribs if attr not in parsed_json]
                if missing_attribs:
                    self.logger.Log(f"SafeGenerateJSON: JSON response from {model_uri} missing attributes: {missing_attribs}. Retrying.", 6)
                    # Add corrective prompt for the next iteration by modifying current_messages
                    # This prompt will be used if the loop continues.
                    current_messages = response_messages + [self.BuildUserQuery(
                        Prompts.JSON_PARSE_ERROR.format(_Error=f"Missing required attributes: {', '.join(missing_attribs)}. Ensure your JSON response includes: {', '.join(required_attribs)}.")
                    )]
                    continue # Go to next attempt

                self.logger.Log(f"SafeGenerateJSON: Successfully parsed JSON from {model_uri}.", 4)
                return response_messages, parsed_json

            except json.JSONDecodeError as e:
                self.logger.Log(f"SafeGenerateJSON: JSONDecodeError from {model_uri}: {e}. Response: '{last_response_text[:200]}...'. Retrying.", 6)
                current_messages = response_messages + [self.BuildUserQuery(
                    Prompts.JSON_PARSE_ERROR.format(_Error=str(e))
                )]
            except Exception as e_gen: # Catch other unexpected errors during parsing/validation
                self.logger.Log(f"SafeGenerateJSON: Unexpected error processing JSON from {model_uri}: {e_gen}. Retrying.", 6)
                current_messages = response_messages + [self.BuildUserQuery(
                    Prompts.JSON_PARSE_ERROR.format(_Error=f"Unexpected error: {str(e_gen)}. Please ensure valid JSON output.")
                )]
        
        self.logger.Log(f"SafeGenerateJSON: Failed to generate valid JSON from {model_uri} after {MAX_JSON_RETRIES} attempts.", 7)
        # Return the last messages and an empty dict or raise a specific exception
        error_content = {"error": "Failed to generate valid JSON", "attempts": MAX_JSON_RETRIES, "last_response_snippet": self.GetLastMessageText(response_messages)[:200]}
        if not response_messages or response_messages[-1].get("role") != "assistant":
            response_messages = current_messages + [{"role": "assistant", "content": json.dumps(error_content)}]
        else:
            response_messages[-1]["content"] = json.dumps(error_content) # Overwrite last attempt with error
            
        raise Exception(f"Failed to generate valid JSON from {model_uri} after {MAX_JSON_RETRIES} attempts. Last error content: {error_content}")


    def ChatAndStreamResponse(
        self,
        messages: List[Dict[str, str]],
        model_uri: str,
        seed_override: int = -1,
        output_format: Optional[Literal["json"]] = None
    ) -> List[Dict[str, str]]:
        """
        Sends messages to the specified LLM and streams the response.
        Handles provider-specific logic and basic error retries.
        Returns the original messages list appended with the assistant's response.
        """
        provider, provider_model_name, model_host, model_options_from_uri = self._get_model_and_provider(model_uri)
        effective_seed = Config.SEED if seed_override == -1 else seed_override

        # Deep copy messages to prevent modification of the original list passed by the caller
        # within this function's retry logic or provider-specific formatting.
        # The list returned will be a new list with the assistant's response appended.
        current_call_messages = [msg.copy() for msg in messages]

        if Config.DEBUG:
            self.logger.Log(f"--- LLM Call Start: Model URI '{model_uri}' ---", 1)
            for i, msg in enumerate(current_call_messages):
                self.logger.Log(f"  Msg {i} Role: {msg.get('role')}, Content Snippet: '{str(msg.get('content'))[:100]}...'", 1)
            self.logger.Log(f"  Effective Seed: {effective_seed}, Output Format: {output_format}", 1)

        start_time = time.time()
        estimated_tokens = sum(len(str(m.get("content", ""))) for m in current_call_messages) / 4 # Rough estimate

        full_response_content = ""
        MAX_LLM_CALL_RETRIES = 2 # Reduced from 3 in original, as SafeGenerateText/JSON has its own retries
        
        for attempt in range(MAX_LLM_CALL_RETRIES):
            try:
                if provider == "ollama":
                    if ollama is None: raise ImportError("Ollama package not available/loaded.")
                    client = self.clients.get(model_uri)
                    if not client: raise ValueError(f"Ollama client for {model_uri} not initialized.")
                    
                    combined_options = {"seed": effective_seed, "num_ctx": Config.OLLAMA_CTX}
                    if model_options_from_uri: combined_options.update(model_options_from_uri)
                    if output_format == "json": combined_options["format"] = "json"
                    if "temperature" not in combined_options and output_format == "json": combined_options["temperature"] = 0.1 # Lower for JSON
                    
                    self.logger.Log(f"Ollama Call: Model='{provider_model_name}', Options={combined_options}", 2)
                    stream = client.chat(model=provider_model_name, messages=current_call_messages, stream=True, options=combined_options)
                    full_response_content = self._stream_response_internal(stream, provider)

                elif provider == "google":
                    if genai is None: raise ImportError("Google GenAI package not available/loaded.")
                    client = self.clients.get(model_uri)
                    if not client: raise ValueError(f"Google client for {model_uri} not initialized.")

                    # Format messages for Google API (role: "user" or "model", content in "parts")
                    google_messages = []
                    for msg in current_call_messages:
                        role = msg.get("role")
                        content = msg.get("content", "")
                        if role == "system": # Google prefers system prompts at init or as leading user message
                            google_messages.append({"role": "user", "parts": [f"[System Instruction]: {content}"]})
                        elif role == "assistant":
                            google_messages.append({"role": "model", "parts": [content]})
                        else: # user
                            google_messages.append({"role": "user", "parts": [content]})
                    
                    generation_config_dict = {"temperature": 0.7} # Default
                    if model_options_from_uri: generation_config_dict.update(model_options_from_uri)
                    if output_format == "json": # Google specific way to request JSON
                        generation_config_dict["response_mime_type"] = "application/json"
                        if "temperature" not in model_options_from_uri: generation_config_dict["temperature"] = 0.1


                    safety_settings = {
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    }
                    self.logger.Log(f"Google Call: Model='{provider_model_name}', Config={generation_config_dict}", 2)
                    stream = client.generate_content(
                        contents=google_messages,
                        stream=True,
                        generation_config=genai.types.GenerationConfig(**generation_config_dict), # type: ignore
                        safety_settings=safety_settings
                    )
                    full_response_content = self._stream_response_internal(stream, provider)

                elif provider == "openrouter":
                    client = self.clients.get(model_uri) # type: OpenRouter
                    if not client: raise ValueError(f"OpenRouter client for {model_uri} not initialized.")
                    
                    client.model = provider_model_name # Ensure correct model is set on client
                    if model_options_from_uri: client.set_params(**model_options_from_uri)
                    if output_format == "json": client.set_params(response_format={"type": "json_object"}) # OpenRouter way for JSON

                    self.logger.Log(f"OpenRouter Call: Model='{provider_model_name}', Seed={effective_seed}", 2)
                    # OpenRouter client might not support true streaming in its current form in the project
                    # It makes a blocking call.
                    full_response_content = client.chat(messages=current_call_messages, seed=effective_seed)
                    if Config.DEBUG: print(full_response_content, end="", flush=True) # Simulate stream for debug
                    if Config.DEBUG: print("\n")

                else:
                    self.logger.Log(f"Provider '{provider}' not implemented in ChatAndStreamResponse.", 6)
                    raise NotImplementedError(f"Provider '{provider}' is not supported.")

                # If successful, break retry loop
                break 
            
            except Exception as e:
                self.logger.Log(f"LLM Call (Attempt {attempt + 1}/{MAX_LLM_CALL_RETRIES}) to {model_uri} failed: {type(e).__name__} - {e}", 7)
                if attempt >= MAX_LLM_CALL_RETRIES - 1:
                    self.logger.Log(f"Max retries exceeded for LLM call to {model_uri}. Saving error state.", 7)
                    # Create a new list with the original messages and the error message
                    error_msg_content = f"ERROR: LLM call to {model_uri} failed after {MAX_LLM_CALL_RETRIES} attempts. Last error: {type(e).__name__} - {e}"
                    final_messages_with_error = messages + [{"role": "assistant", "content": error_msg_content}]
                    self._save_langchain_log(final_messages_with_error, "_ERROR")
                    return final_messages_with_error # Return with error info
                
                time.sleep(1.5 ** attempt) # Exponential backoff

        end_time = time.time()
        duration = end_time - start_time
        tokens_per_sec = (len(full_response_content) / 4) / duration if duration > 0 else 0 # Rough estimate
        self.logger.Log(f"LLM call to {model_uri} completed in {duration:.2f}s. Response length: {len(full_response_content)} chars. (~{tokens_per_sec:.2f} tok/s).", 3)

        # Append successful assistant response to a new list based on the original 'messages'
        final_messages_with_response = messages + [{"role": "assistant", "content": full_response_content}]
        self._save_langchain_log(final_messages_with_response)
        
        return final_messages_with_response

    def _stream_response_internal(self, stream_iterator: Any, provider: str) -> str:
        """Helper to accumulate streamed response chunks."""
        response_text = []
        chunk_count = 0
        for chunk in stream_iterator:
            chunk_count += 1
            current_chunk_text = ""
            if provider == "ollama":
                current_chunk_text = chunk.get("message", {}).get("content", "")
            elif provider == "google":
                try:
                    current_chunk_text = chunk.text
                except Exception: # Google stream can end with non-text parts sometimes
                    pass 
            
            if current_chunk_text:
                response_text.append(current_chunk_text)
                if Config.DEBUG and Config.DEBUG_LEVEL > 1: # Only print stream chunks if detailed debug
                    print(current_chunk_text, end="", flush=True)
        
        if Config.DEBUG and Config.DEBUG_LEVEL > 1 and chunk_count > 0: 
            print("\n") # Newline after stream if chunks were printed

        return "".join(response_text)

    def _save_langchain_log(self, messages_to_log: List[Dict[str,str]], suffix: str = ""):
        """Saves the message history to a log file using the Logger instance."""
        if not hasattr(self.logger, 'SaveLangchain'): return # In case logger is a mock or basic

        try:
            # Attempt to find the caller of SafeGenerateText/JSON or ChatAndStreamResponse
            call_stack = inspect.stack()
            relevant_caller = "UnknownContext"
            # Iterate backwards from the direct caller of _save_langchain_log
            for frame_info in reversed(call_stack[1:]): 
                func_name = frame_info.function
                if func_name not in ["_save_langchain_log", "ChatAndStreamResponse", "SafeGenerateText", "SafeGenerateJSON"]:
                    # Try to get module name if possible, very simplified
                    module_name = inspect.getmodule(frame_info.frame).__name__.split('.')[-1] if inspect.getmodule(frame_info.frame) else "Main"
                    relevant_caller = f"{module_name}.{func_name}"
                    break
            
            log_id_suffix = f"{relevant_caller}{suffix}"
            self.logger.SaveLangchain(log_id_suffix, messages_to_log)
        except Exception as e_log:
            self.logger.Log(f"Error during SaveLangchain: {e_log}", 6)


    def BuildUserQuery(self, query_content: str) -> Dict[str, str]:
        """Builds a user message dictionary."""
        return {"role": "user", "content": query_content}

    def BuildSystemQuery(self, query_content: str) -> Dict[str, str]:
        """Builds a system message dictionary."""
        return {"role": "system", "content": query_content}

    def BuildAssistantQuery(self, query_content: str) -> Dict[str, str]:
        """Builds an assistant message dictionary."""
        return {"role": "assistant", "content": query_content}

    def GetLastMessageText(self, messages_list: List[Dict[str, str]]) -> str:
        """Extracts the content of the last message in a list."""
        if messages_list and isinstance(messages_list, list) and len(messages_list) > 0:
            last_msg = messages_list[-1]
            if isinstance(last_msg, dict):
                return last_msg.get("content", "")
        return ""