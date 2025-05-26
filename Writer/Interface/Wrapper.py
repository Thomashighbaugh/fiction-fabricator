# File: AIStoryWriter/Writer/Interface/Wrapper.py
# Purpose: Wraps LLM API interactions, providing a consistent interface and handling retries, logging, and streaming.

"""
LLM Interface Wrapper.

This module provides a standardized way to interact with various LLM providers (Ollama, Google, OpenRouter).
It handles:
- Loading models and initializing clients.
- Dynamic installation of required packages.
- Parsing model URI strings for provider, host, and parameters.
- Streaming responses for interactive output.
- Safe generation methods with retries for empty or short responses (`SafeGenerateText`).
- Safe JSON generation with validation and retries (`SafeGenerateJSON`).
- Logging of LLM calls and their contexts.
- Seed management for reproducibility.
"""

import dotenv
import inspect
import json
import os
import time

# import random # No longer used directly
import importlib
import subprocess
import sys
from urllib.parse import parse_qs, urlparse
from typing import List, Dict, Any, Tuple, Optional, Literal
import Writer.Config as Config
import Writer.Prompts as Prompts


# Load environment variables from .env file (e.g., API keys)
dotenv.load_dotenv()


class Interface:
    """
    Manages connections and interactions with various Large Language Models.
    """

    def __init__(self, models_to_load: List[str] = []):
        """
        Initializes the Interface and loads specified models.

        Args:
            models_to_load (List[str]): A list of model URI strings to preload.
        """
        self.clients: Dict[str, Any] = {}
        self.load_models(models_to_load)

    def _ensure_package_is_installed(
        self, package_name: str, logger: Optional[Any] = None
    ) -> None:
        """
        Checks if a package is installed and installs it if not.
        Uses a passed logger if available.
        """
        try:
            importlib.import_module(package_name)
            if logger:
                logger.Log(f"Package '{package_name}' is already installed.", 0)
        except ImportError:
            log_msg = f"Package '{package_name}' not found. Attempting installation..."
            if logger:
                logger.Log(log_msg, 1)
            else:
                print(log_msg)

            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package_name]
                )
                log_msg_success = f"Package '{package_name}' installed successfully."
                if logger:
                    logger.Log(log_msg_success, 0)
                else:
                    print(log_msg_success)
            except subprocess.CalledProcessError as e:
                log_msg_fail = f"Failed to install package '{package_name}': {e}"
                if logger:
                    logger.Log(log_msg_fail, 7)
                else:
                    print(log_msg_fail)
                raise ImportError(
                    f"Could not install required package: {package_name}"
                ) from e

    def load_models(self, model_uris: List[str], logger: Optional[Any] = None) -> None:
        """
        Loads and initializes clients for the specified models.

        Args:
            model_uris (List[str]): A list of model URI strings.
            logger (Optional[Any]): Logger instance for logging messages.
        """
        for model_uri in model_uris:
            if model_uri in self.clients:
                if logger:
                    logger.Log(f"Model '{model_uri}' already loaded.", 0)
                continue

            provider, provider_model_name, model_host, model_options = (
                self._get_model_and_provider(model_uri)
            )
            log_msg_load = (
                f"Loading Model: '{provider_model_name}' from Provider: '{provider}' "
                f"at Host: '{model_host or 'default'}' with options: {model_options or '{}'}"
            )
            if logger:
                logger.Log(log_msg_load, 1)
            else:
                print(log_msg_load)

            try:
                if provider == "ollama":
                    self._ensure_package_is_installed("ollama", logger)
                    import ollama  # type: ignore

                    effective_ollama_host = (
                        model_host if model_host else Config.OLLAMA_HOST
                    )

                    try:
                        ollama.Client(host=effective_ollama_host).show(
                            provider_model_name
                        )
                        if logger:
                            logger.Log(
                                f"Ollama model '{provider_model_name}' found locally at "
                                f"{effective_ollama_host}.",
                                0,
                            )
                    except ollama.ResponseError:
                        log_msg_download = (
                            f"Ollama model '{provider_model_name}' not found at "
                            f"{effective_ollama_host}. Attempting download..."
                        )
                        if logger:
                            logger.Log(log_msg_download, 1)
                        else:
                            print(log_msg_download)

                        ollama_download_stream = ollama.Client(
                            host=effective_ollama_host
                        ).pull(provider_model_name, stream=True)
                        for chunk in ollama_download_stream:
                            status = chunk.get("status", "")
                            completed = chunk.get("completed", 0)
                            total = chunk.get("total", 0)
                            if total > 0 and completed >= 0:
                                progress = (completed / total) * 100 if total > 0 else 0
                                completed_size_mb = completed / (1024**2)
                                total_size_mb = total / (1024**2)
                                print(
                                    f"Downloading {provider_model_name}: {progress:.2f}% "
                                    f"({completed_size_mb:.2f}MB / {total_size_mb:.2f}MB)",
                                    end="\r",
                                    flush=True,
                                )
                            elif status:
                                print(
                                    f"{status} {provider_model_name}...",
                                    end="\r",
                                    flush=True,
                                )
                        print(
                            "\nDownload complete."
                            if total > 0
                            else f"\nFinished: {status}"
                        )
                    self.clients[model_uri] = ollama.Client(host=effective_ollama_host)

                elif provider == "google":
                    self._ensure_package_is_installed("google-generativeai", logger)
                    import google.generativeai as genai  # type: ignore

                    google_api_key = os.environ.get("GOOGLE_API_KEY")
                    if not google_api_key:
                        raise ValueError(
                            "GOOGLE_API_KEY not found for Google provider."
                        )
                    genai.configure(api_key=google_api_key)
                    self.clients[model_uri] = genai.GenerativeModel(
                        model_name=provider_model_name
                    )

                elif provider == "openrouter":
                    self._ensure_package_is_installed("requests", logger)
                    from Writer.Interface.OpenRouter import OpenRouter

                    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
                    if not openrouter_api_key:
                        raise ValueError(
                            "OPENROUTER_API_KEY not found for OpenRouter provider."
                        )
                    self.clients[model_uri] = OpenRouter(
                        api_key=openrouter_api_key, model=provider_model_name
                    )
                else:
                    error_msg = f"Unsupported provider '{provider}' for '{model_uri}'."
                    if logger:
                        logger.Log(error_msg, 7)
                    raise ValueError(error_msg)

                log_msg_success = (
                    f"Loaded model '{provider_model_name}' for '{model_uri}'."
                )
                if logger:
                    logger.Log(log_msg_success, 1)
                else:
                    print(log_msg_success)

            except Exception as e:
                error_msg_load = f"Failed to load model for URI '{model_uri}': {e}"
                if logger:
                    logger.Log(error_msg_load, 7)
                else:
                    print(error_msg_load)

    def _get_model_and_provider(
        self, model_uri: str
    ) -> Tuple[str, str, Optional[str], Optional[Dict[str, Any]]]:
        if "://" not in model_uri:
            parsed_path = model_uri.split("@")
            model_name = parsed_path[0]
            host = parsed_path[1] if len(parsed_path) > 1 else Config.OLLAMA_HOST
            return "ollama", model_name, host, None

        parsed = urlparse(model_uri)
        provider = parsed.scheme.lower()
        path_parts = parsed.path.strip("/").split("@")
        model_identifier_from_path = path_parts[0]
        host_from_path = path_parts[1] if len(path_parts) > 1 else None

        if parsed.netloc:
            model_name = (
                f"{parsed.netloc}{parsed.path.split('@')[0]}"
                if parsed.path and "@" in parsed.path
                else f"{parsed.netloc}{('/' + model_identifier_from_path) if model_identifier_from_path and not parsed.path.endswith(model_identifier_from_path) else parsed.path}"
            )
        else:
            model_name = model_identifier_from_path

        host = host_from_path
        if not host and provider == "ollama":
            host = Config.OLLAMA_HOST

        query_params: Optional[Dict[str, Any]] = None
        if parsed.query:
            query_params = {}
            for key, value_list in parse_qs(parsed.query).items():
                value = value_list[0]
                try:
                    if "." in value:
                        query_params[key] = float(value)
                    else:
                        query_params[key] = int(value)
                except ValueError:
                    if value.lower() == "true":
                        query_params[key] = True
                    elif value.lower() == "false":
                        query_params[key] = False
                    else:
                        query_params[key] = value
        return provider, model_name, host, query_params

    def _clean_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []
        for i, msg in enumerate(messages):
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip() == "":
                if i == len(messages) - 1 and msg.get("role") == "assistant":
                    cleaned.append(msg)
                continue
            cleaned.append(msg)
        return cleaned

    def safe_generate_text(
        self,
        logger: Any,
        messages: List[Dict[str, Any]],
        model_uri: str,
        seed_override: int = -1,
        output_format: Optional[Literal["json"]] = None,
        min_word_count: int = 1,
    ) -> List[Dict[str, Any]]:
        current_messages = self._clean_messages(messages)
        max_retries_sgt = 3
        for attempt in range(max_retries_sgt):
            effective_seed = (
                seed_override if seed_override != -1 else (Config.SEED + attempt)
            )
            response_messages = self.chat_and_stream_response(
                logger, current_messages, model_uri, effective_seed, output_format
            )
            last_response_text = self.get_last_message_text(response_messages)
            word_count = len(last_response_text.split())

            if last_response_text.strip() != "" and word_count >= min_word_count:
                return response_messages

            logger.Log(
                f"SafeGenerateText (Attempt {attempt + 1}/{max_retries_sgt}): Response failed "
                f"(Empty: {last_response_text.strip() == ''}, Words: {word_count}, Min: {min_word_count}). Retrying.",
                6 if attempt < max_retries_sgt - 1 else 7,
            )
            if response_messages and response_messages[-1]["role"] == "assistant":
                current_messages = response_messages[:-1]
            if word_count < min_word_count and last_response_text.strip() != "":
                current_messages.append(
                    self.build_user_query(
                        f"Your previous response was too short ({word_count} words, "
                        f"minimum {min_word_count}). Please elaborate."
                    )
                )
            else:
                current_messages.append(
                    self.build_user_query(
                        "Your previous response was empty. Please try again."
                    )
                )
            if attempt == max_retries_sgt - 1:
                logger.Log(
                    f"SafeGenerateText: Failed for {model_uri} after {max_retries_sgt} attempts. "
                    f"Last response: '{last_response_text[:100]}...'",
                    7,
                )
        return response_messages

    def safe_generate_json(
        self,
        logger: Any,
        messages: List[Dict[str, Any]],
        model_uri: str,
        seed_override: int = -1,
        required_attribs: List[str] = [],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        current_messages = self._clean_messages(messages)
        max_json_attempts = 3
        last_error_type = ""

        for attempt in range(max_json_attempts):
            effective_seed = (
                seed_override if seed_override != -1 else (Config.SEED + attempt)
            )
            response_messages = self.chat_and_stream_response(
                logger,
                current_messages,
                model_uri,
                effective_seed,
                output_format="json",
            )
            last_response_text = self.get_last_message_text(response_messages)
            parsed_json: Optional[Dict[str, Any]] = None

            try:
                cleaned_response_text = last_response_text.strip()
                if cleaned_response_text.startswith("```json"):
                    cleaned_response_text = cleaned_response_text[7:]
                if cleaned_response_text.endswith("```"):
                    cleaned_response_text = cleaned_response_text[:-3]
                cleaned_response_text = cleaned_response_text.strip()

                if not cleaned_response_text:
                    raise json.JSONDecodeError(
                        "Empty response cannot be parsed as JSON.", "", 0
                    )

                parsed_json = json.loads(cleaned_response_text)
                missing_attribs = [
                    attr for attr in required_attribs if attr not in parsed_json
                ]

                if not missing_attribs:
                    return response_messages, parsed_json  # Success

                last_error_type = "missing_attributes"
                logger.Log(
                    f"SafeGenerateJSON (Attempt {attempt + 1}/{max_json_attempts}): "
                    f"JSON missing attributes: {missing_attribs}. Retrying.",
                    6,
                )
                correction_prompt = (
                    f"Your JSON response was missing the following required attributes: {', '.join(missing_attribs)}. "
                    f"Please ensure your response is a valid JSON object containing all required attributes: {', '.join(required_attribs)}. "
                    f"The previous full JSON attempt was:\n```json\n{last_response_text}\n```"
                )

            except json.JSONDecodeError as e:
                last_error_type = "json_decode_error"
                logger.Log(
                    f"SafeGenerateJSON (Attempt {attempt + 1}/{max_json_attempts}): "
                    f"JSONDecodeError: {e}. Response: '{last_response_text[:200]}...'. Retrying.",
                    6,
                )
                # Use the generic JSON_PARSE_ERROR but also include the faulty text to help the LLM.
                correction_prompt = (
                    Prompts.JSON_PARSE_ERROR.format(_Error=str(e))
                    + f"\nThe malformed JSON text was:\n```\n{last_response_text}\n```\n"
                    + "Please provide the corrected JSON structure."
                )

            # Prepare for retry: use the response_messages that led to the error as history for correction
            current_messages = response_messages
            current_messages.append(self.build_user_query(correction_prompt))

            if attempt == max_json_attempts - 1:
                error_message = (
                    f"SafeGenerateJSON: Failed to generate valid JSON for {model_uri} "
                    f"after {max_json_attempts} attempts. Last error type: {last_error_type}."
                )
                logger.Log(error_message, 7)
                raise Exception(f"{error_message} Last response: {last_response_text}")

        # This part should be unreachable if logic is correct
        raise Exception(
            f"SafeGenerateJSON logic error for {model_uri}, exited loop unexpectedly."
        )

    def chat_and_stream_response(
        self,
        logger: Any,
        messages: List[Dict[str, Any]],
        model_uri: str,
        seed_override: int = -1,
        output_format: Optional[Literal["json"]] = None,
    ) -> List[Dict[str, Any]]:
        provider, provider_model_name, model_host, model_options_from_uri = (
            self._get_model_and_provider(model_uri)
        )
        effective_seed = Config.SEED if seed_override == -1 else seed_override
        total_chars = sum(len(str(msg.get("content", ""))) for msg in messages)
        estimated_tokens = total_chars / 4.5
        logger.Log(
            f"LLM call to '{provider_model_name}' ({provider}). Seed: {effective_seed}. "
            f"Format: {output_format}. Est. Tokens: ~{estimated_tokens:.0f}",
            4,
        )
        if estimated_tokens > (Config.OLLAMA_CTX * 0.8):
            logger.Log(
                f"Warning: Est. tokens ({estimated_tokens:.0f}) high for context "
                f"{Config.OLLAMA_CTX}.",
                6,
            )

        if Config.DEBUG:
            logger.Log("--------- Message History START ---------", 0, stream=True)
            for i, msg in enumerate(messages):
                role = msg.get("role", "unknown")
                content_preview = (
                    str(msg.get("content", ""))[:100] + "..."
                    if len(str(msg.get("content", ""))) > 100
                    else str(msg.get("content", ""))
                )
                logger.Log(
                    f"  {i}. Role: {role}, Content: '{content_preview}'", 0, stream=True
                )
            logger.Log("--------- Message History END ---------", 0, stream=True)

        start_time = time.time()
        full_response_content = ""
        final_model_options = {}
        if Config.DEBUG_LEVEL > 1:
            logger.Log(f"Base model options for {provider}: {final_model_options}", 0)
        if model_options_from_uri:
            final_model_options.update(model_options_from_uri)
            if Config.DEBUG_LEVEL > 1:
                logger.Log(
                    f"Updated model options with URI params: {final_model_options}", 0
                )

        max_llm_retries = 2
        for attempt in range(max_llm_retries):
            try:
                if provider == "ollama":
                    import ollama  # type: ignore

                    ollama_options = final_model_options.copy()
                    ollama_options["seed"] = effective_seed
                    if "num_ctx" not in ollama_options:
                        ollama_options["num_ctx"] = Config.OLLAMA_CTX
                    if output_format == "json":
                        ollama_options["format"] = "json"
                    if Config.DEBUG_LEVEL > 0:
                        logger.Log(f"Ollama options: {ollama_options}", 0)
                    stream = self.clients[model_uri].chat(
                        model=provider_model_name,
                        messages=messages,
                        stream=True,
                        options=ollama_options,
                    )
                    full_response_content = self._stream_response_internal(
                        stream, provider, logger
                    )

                elif provider == "google":
                    import google.generativeai as genai
                    from google.generativeai.types import (
                        HarmCategory,
                        HarmBlockThreshold,
                    )

                    google_messages, system_instruction_text = [], None
                    for msg in messages:
                        role, content = msg["role"], str(msg.get("content", ""))
                        if role == "system":
                            system_instruction_text = content
                            continue
                        if (
                            system_instruction_text
                            and role == "user"
                            and (
                                not google_messages
                                or all(m.get("role") != "user" for m in google_messages)
                            )
                        ):
                            content = system_instruction_text + "\n\n" + content
                            system_instruction_text = None
                        google_messages.append(
                            {
                                "role": "model" if role == "assistant" else "user",
                                "parts": [{"text": content}],
                            }
                        )
                    if system_instruction_text:
                        if not any(m["role"] == "user" for m in google_messages):
                            google_messages.insert(
                                0,
                                {
                                    "role": "user",
                                    "parts": [{"text": system_instruction_text}],
                                },
                            )
                        elif google_messages and google_messages[0]["role"] == "model":
                            google_messages.insert(
                                0,
                                {
                                    "role": "user",
                                    "parts": [{"text": system_instruction_text}],
                                },
                            )

                    gen_config_dict = final_model_options.copy()
                    if (
                        "temperature" in gen_config_dict
                        and gen_config_dict["temperature"] is None
                    ):
                        del gen_config_dict["temperature"]
                    gen_config_obj = (
                        genai.types.GenerationConfig(**gen_config_dict)
                        if gen_config_dict
                        else None
                    )
                    if output_format == "json":
                        if gen_config_obj:
                            gen_config_obj.response_mime_type = "application/json"
                        else:
                            gen_config_obj = genai.types.GenerationConfig(
                                response_mime_type="application/json"
                            )
                    if Config.DEBUG_LEVEL > 0:
                        logger.Log(
                            f"Google messages: {google_messages}, GenConfig: {gen_config_obj}",
                            0,
                        )
                    safety_settings = {
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    }
                    stream = self.clients[model_uri].generate_content(
                        contents=google_messages,
                        stream=True,
                        safety_settings=safety_settings,
                        generation_config=gen_config_obj,
                    )
                    full_response_content = self._stream_response_internal(
                        stream, provider, logger
                    )

                elif provider == "openrouter":
                    from Writer.Interface.OpenRouter import OpenRouter

                    client: OpenRouter = self.clients[model_uri]
                    client.set_params(**final_model_options)
                    client.model = provider_model_name
                    if output_format == "json":
                        client.set_params(response_format={"type": "json_object"})
                    if Config.DEBUG_LEVEL > 0:
                        logger.Log(
                            f"OpenRouter params: {client.params}, model: {client.model}",
                            0,
                        )
                    full_response_content = client.chat(
                        messages=messages, seed=effective_seed
                    )
                    logger.Log(
                        f"OpenRouter full response (len: {len(full_response_content)}).",
                        4,
                        stream=False,
                    )
                else:
                    raise NotImplementedError(f"Provider '{provider}' not implemented.")
                break
            except Exception as e:
                logger.Log(
                    f"LLM Call Error (Attempt {attempt + 1}/{max_llm_retries}) for {model_uri}: {e}",
                    7,
                )
                if attempt == max_llm_retries - 1:
                    full_response_content = f"ERROR: LLM call failed after {max_llm_retries} attempts. Error: {e}"
                time.sleep(1.5**attempt)

        duration = time.time() - start_time
        response_words = len(full_response_content.split())
        words_per_sec = response_words / duration if duration > 0 else 0
        logger.Log(
            f"Generated response in {duration:.2f}s. Approx. {response_words} words, ~{words_per_sec:.2f} words/s.",
            4,
        )
        updated_messages = messages + [
            {"role": "assistant", "content": full_response_content}
        ]

        caller_function_name = "UnknownCaller"
        try:
            call_stack = inspect.stack()
            relevant_frames = []
            for i in range(1, min(4, len(call_stack))):
                frame_info, func_name = call_stack[i], call_stack[i].function
                if func_name == "<module>":
                    if "self" in frame_info.frame.f_locals:
                        func_name = frame_info.frame.f_locals["self"].__class__.__name__
                    elif i == 1 and not relevant_frames:
                        module_name = os.path.splitext(
                            os.path.basename(frame_info.filename)
                        )[0]
                        func_name = (
                            module_name
                            if module_name != "__main__"
                            else "MainExecution"
                        )
                relevant_frames.append(func_name)
            caller_function_name = (
                ".".join(reversed(relevant_frames)) if relevant_frames else "DirectCall"
            )
        except IndexError:
            logger.Log("Could not determine full call stack for log naming.", 1)

        simple_model_name = provider_model_name.split("/")[-1].split(":")[0]
        logger.save_langchain_interaction(
            f"{caller_function_name}.{simple_model_name}", updated_messages
        )
        return updated_messages

    def _stream_response_internal(
        self, stream_iterator: Any, provider: str, logger: Any
    ) -> str:
        response_text, chunk_count = "", 0
        stream_start_time = time.time()
        enable_console_stream = Config.DEBUG and Config.DEBUG_LEVEL > 1

        for chunk in stream_iterator:
            chunk_count += 1
            current_chunk_text = ""
            if provider == "ollama":
                current_chunk_text = chunk.get("message", {}).get("content", "")
            elif provider == "google":
                try:
                    current_chunk_text = chunk.text
                except Exception:
                    if Config.DEBUG_LEVEL > 1:
                        logger.Log(f"Google stream chunk no text: {chunk}", 0)
                    continue
            else:
                logger.Log(f"Streaming not implemented for provider: {provider}", 7)
                break
            if current_chunk_text:
                response_text += current_chunk_text
                if enable_console_stream:
                    print(current_chunk_text, end="", flush=True)

        if enable_console_stream and chunk_count > 0:
            print()
        stream_duration = time.time() - stream_start_time
        if chunk_count > 0:
            logger.Log(
                f"Streamed {chunk_count} chunks for {provider} in {stream_duration:.2f}s.",
                0,
                stream=True,
            )
        return response_text

    def build_user_query(self, query_text: str) -> Dict[str, str]:
        return {"role": "user", "content": query_text}

    def build_system_query(self, query_text: str) -> Dict[str, str]:
        return {"role": "system", "content": query_text}

    def build_assistant_query(self, query_text: str) -> Dict[str, str]:
        return {"role": "assistant", "content": query_text}

    def get_last_message_text(self, messages: List[Dict[str, Any]]) -> str:
        if messages and isinstance(messages, list) and messages:
            last_msg = messages[-1]
            if isinstance(last_msg, dict):
                content = last_msg.get("content", "")
                return str(content) if content is not None else ""
        return ""
