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
import random
import importlib
import subprocess
import sys
from urllib.parse import parse_qs, urlparse
from typing import List, Dict, Any, Tuple, Optional, Literal
import Writer.Config as Config  # Renamed for clarity
import Writer.Prompts as Prompts  # For JSON_PARSE_ERROR prompt


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
        self.clients: Dict[str, Any] = (
            {}
        )  # Stores initialized LLM clients, keyed by model_uri
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
            log_msg_load = f"Loading Model: '{provider_model_name}' from Provider: '{provider}' at Host: '{model_host or 'default'}' with options: {model_options or '{}'}"
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

                    # Check if model is available and download if not
                    try:
                        ollama.Client(host=effective_ollama_host).show(
                            provider_model_name
                        )
                        if logger:
                            logger.Log(
                                f"Ollama model '{provider_model_name}' found locally at {effective_ollama_host}.",
                                0,
                            )
                    except (
                        ollama.ResponseError
                    ):  # More specific exception for model not found
                        log_msg_download = f"Ollama model '{provider_model_name}' not found at {effective_ollama_host}. Attempting download..."
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
                            if total > 0 and completed > 0:
                                progress = (completed / total) * 100
                                print(
                                    f"Downloading {provider_model_name}: {progress:.2f}% ({completed/1024**2:.2f}MB / {total/1024**2:.2f}MB)",
                                    end="\r",
                                )
                            else:
                                print(f"{status} {provider_model_name}...", end="\r")
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
                            "GOOGLE_API_KEY not found in environment variables for Google provider."
                        )
                    genai.configure(api_key=google_api_key)
                    self.clients[model_uri] = genai.GenerativeModel(
                        model_name=provider_model_name
                    )

                elif provider == "openrouter":
                    self._ensure_package_is_installed(
                        "requests", logger
                    )  # OpenRouter client uses requests
                    from Writer.Interface.OpenRouter import OpenRouter  # Local import

                    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
                    if not openrouter_api_key:
                        raise ValueError(
                            "OPENROUTER_API_KEY not found in environment variables for OpenRouter provider."
                        )
                    self.clients[model_uri] = OpenRouter(
                        api_key=openrouter_api_key, model=provider_model_name
                    )

                # Add other providers like Anthropic here if needed
                # elif provider == "anthropic":
                #     self._ensure_package_is_installed("anthropic", logger)
                #     # ... anthropic client setup ...

                else:
                    error_msg = f"Unsupported model provider '{provider}' for model URI '{model_uri}'."
                    if logger:
                        logger.Log(error_msg, 7)
                    raise ValueError(error_msg)

                log_msg_success = f"Successfully loaded model '{provider_model_name}' for URI '{model_uri}'."
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
                # Optionally, re-raise or handle as appropriate (e.g., skip model if non-critical)

    def _get_model_and_provider(
        self, model_uri: str
    ) -> Tuple[str, str, Optional[str], Optional[Dict[str, Any]]]:
        """
        Parses a model URI string to extract provider, model name, host, and query parameters.
        Format: "provider://model_identifier@host?param1=value1¶m2=value2"
        If no "://" is present, defaults to "ollama".
        """
        if "://" not in model_uri:
            # Default to ollama provider if no scheme is specified
            # This assumes the model_uri is just the model name for ollama
            # and uses the default Config.OLLAMA_HOST
            parsed_path = model_uri.split("@")
            model_name = parsed_path[0]
            host = parsed_path[1] if len(parsed_path) > 1 else Config.OLLAMA_HOST
            return "ollama", model_name, host, None

        parsed = urlparse(model_uri)
        provider = parsed.scheme.lower()

        path_parts = parsed.path.strip("/").split(
            "@"
        )  # Remove leading/trailing slashes from path
        model_identifier_from_path = path_parts[0]
        host_from_path = path_parts[1] if len(path_parts) > 1 else None

        # Combine netloc and path for model identifier if netloc is part of it
        # (e.g., huggingface.co/DavidAU/...)
        if parsed.netloc:
            model_name = (
                f"{parsed.netloc}{parsed.path.split('@')[0]}"
                if parsed.path
                else parsed.netloc
            )
        else:
            model_name = model_identifier_from_path  # Should not happen if "://" is present and scheme is not file

        host = host_from_path  # Host from path takes precedence if specified with @
        if (
            not host and provider == "ollama"
        ):  # Default host for ollama if not specified
            host = Config.OLLAMA_HOST

        query_params: Optional[Dict[str, Any]] = None
        if parsed.query:
            query_params = {}
            for key, value_list in parse_qs(parsed.query).items():
                value = value_list[0]  # Take the first value for each param
                try:
                    # Attempt to convert to float or int if possible
                    if "." in value:
                        query_params[key] = float(value)
                    else:
                        query_params[key] = int(value)
                except ValueError:
                    # Keep as string if conversion fails
                    if value.lower() == "true":
                        query_params[key] = True
                    elif value.lower() == "false":
                        query_params[key] = False
                    else:
                        query_params[key] = value

        return provider, model_name, host, query_params

    def _clean_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes messages with empty or whitespace-only content, except possibly the last one if it's an assistant placeholder."""
        cleaned = []
        for i, msg in enumerate(messages):
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip() == "":
                if (
                    i == len(messages) - 1 and msg.get("role") == "assistant"
                ):  # Keep placeholder
                    cleaned.append(msg)
                continue  # Skip other empty messages
            cleaned.append(msg)
        return cleaned

    def safe_generate_text(
        self,
        logger: Any,
        messages: List[Dict[str, Any]],
        model_uri: str,
        seed_override: int = -1,
        output_format: Optional[
            Literal["json"]
        ] = None,  # Changed from _Format to output_format
        min_word_count: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Ensures the LLM response is not empty/whitespace and meets a minimum word count.
        Retries with modified prompts if initial attempts fail.

        Args:
            logger: Logger instance.
            messages: List of message dictionaries for the LLM.
            model_uri: The URI string of the model to use.
            seed_override: Specific seed for this generation, or -1 for default.
            output_format: Optional. If "json", instructs capable models to output JSON.
            min_word_count: Minimum number of words required in the response.

        Returns:
            The list of messages including the LLM's successful response.
        """
        current_messages = self._clean_messages(messages)

        max_retries_sgt = 3
        for attempt in range(max_retries_sgt):
            effective_seed = (
                seed_override if seed_override != -1 else (Config.SEED + attempt)
            )  # Vary seed on retries

            response_messages = self.chat_and_stream_response(
                logger, current_messages, model_uri, effective_seed, output_format
            )

            last_response_text = self.get_last_message_text(response_messages)
            word_count = len(last_response_text.split())

            if last_response_text.strip() != "" and word_count >= min_word_count:
                return response_messages  # Success

            # Prepare for retry
            logger.Log(
                f"SafeGenerateText (Attempt {attempt + 1}/{max_retries_sgt}): Response failed criteria "
                f"(Empty: {last_response_text.strip() == ''}, Words: {word_count}, Min: {min_word_count}). Retrying.",
                (
                    6 if attempt < max_retries_sgt - 1 else 7
                ),  # Log as warning, then error on final fail
            )

            # Modify current_messages for retry:
            # Remove the last assistant's failed response.
            # Add a user message asking to try again or be more verbose.
            if response_messages and response_messages[-1]["role"] == "assistant":
                current_messages = response_messages[
                    :-1
                ]  # Remove failed assistant response

            if word_count < min_word_count and last_response_text.strip() != "":
                current_messages.append(
                    self.build_user_query(
                        f"Your previous response was too short ({word_count} words, minimum {min_word_count}). Please elaborate and provide a more detailed answer."
                    )
                )
            else:  # Was empty
                current_messages.append(
                    self.build_user_query(
                        "Your previous response was empty. Please try generating a response again."
                    )
                )

            if attempt == max_retries_sgt - 1:  # Last attempt failed
                logger.Log(
                    f"SafeGenerateText: Failed to get adequate response for {model_uri} after {max_retries_sgt} attempts. Last response: '{last_response_text[:100]}...'",
                    7,
                )
                # Return the last failed response, but mark it or handle upstream
                return response_messages

        return response_messages  # Should be unreachable if loop logic is correct

    def safe_generate_json(
        self,
        logger: Any,
        messages: List[Dict[str, Any]],
        model_uri: str,
        seed_override: int = -1,
        required_attribs: List[str] = [],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Ensures the LLM response is valid JSON and contains required attributes.
        Retries with corrective prompts if parsing fails or attributes are missing.

        Args:
            logger: Logger instance.
            messages: List of message dictionaries for the LLM.
            model_uri: The URI string of the model to use.
            seed_override: Specific seed for this generation, or -1 for default.
            required_attribs: A list of attribute keys that must be present in the JSON response.

        Returns:
            A tuple containing the full message list (including the valid JSON response)
            and the parsed JSON dictionary.

        Raises:
            Exception if a valid JSON response cannot be obtained after max retries.
        """
        current_messages = self._clean_messages(messages)

        max_json_attempts = 3
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

            try:
                # Pre-process common JSON issues (like markdown code blocks)
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

                # Attributes missing, prepare for retry
                logger.Log(
                    f"SafeGenerateJSON (Attempt {attempt + 1}/{max_json_attempts}): JSON response missing attributes: {missing_attribs}. Retrying.",
                    6,
                )
                current_messages = response_messages  # Keep history
                current_messages.append(
                    self.build_user_query(
                        f"Your JSON response was missing the following required attributes: {', '.join(missing_attribs)}. "
                        f"Please ensure your response is a valid JSON object containing all attributes: {', '.join(required_attribs)}."
                    )
                )

            except json.JSONDecodeError as e:
                logger.Log(
                    f"SafeGenerateJSON (Attempt {attempt + 1}/{max_json_attempts}): JSONDecodeError: {e}. Response: '{last_response_text[:200]}...'. Retrying.",
                    6,
                )
                current_messages = response_messages  # Keep history
                current_messages.append(
                    self.build_user_query(
                        Prompts.JSON_PARSE_ERROR.format(_Error=str(e))
                    )
                )

            if attempt == max_json_attempts - 1:  # Last attempt failed
                logger.Log(
                    f"SafeGenerateJSON: Failed to generate valid JSON for {model_uri} after {max_json_attempts} attempts.",
                    7,
                )
                raise Exception(
                    f"Failed to generate valid JSON for {model_uri} after {max_json_attempts} attempts. Last response: {last_response_text}"
                )

        # Should be unreachable
        raise Exception(f"SafeGenerateJSON logic error for {model_uri}")

    def chat_and_stream_response(
        self,
        logger: Any,
        messages: List[Dict[str, Any]],
        model_uri: str,
        seed_override: int = -1,
        output_format: Optional[Literal["json"]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Sends messages to the specified LLM and streams the response.
        Handles provider-specific logic and includes error retries for the LLM call itself.

        Args:
            logger: Logger instance.
            messages: List of message dictionaries.
            model_uri: The URI string of the model to use.
            seed_override: Specific seed, or -1 for default.
            output_format: If "json", attempts to instruct the model for JSON output.

        Returns:
            The updated list of messages, including the assistant's response.
        """
        provider, provider_model_name, model_host, model_options_from_uri = (
            self._get_model_and_provider(model_uri)
        )
        effective_seed = Config.SEED if seed_override == -1 else seed_override

        # Logging context length
        total_chars = sum(len(str(msg.get("content", ""))) for msg in messages)
        estimated_tokens = total_chars / 4.5  # Rough estimate
        logger.Log(
            f"Initiating LLM call to '{provider_model_name}' ({provider}). Seed: {effective_seed}. Format: {output_format}. Est. Tokens: ~{estimated_tokens:.0f}",
            4,
        )
        if estimated_tokens > (
            Config.OLLAMA_CTX * 0.8
        ):  # Warning if approaching context limit
            logger.Log(
                f"Warning: Estimated token count ({estimated_tokens:.0f}) is high for context window {Config.OLLAMA_CTX}.",
                6,
            )

        if Config.DEBUG:
            logger.Log(
                "--------- Message History START ---------", 0, stream=True
            )  # Use stream=True for multiline debug
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

        # Combine URI options with any dynamic options, URI options take precedence
        final_model_options = {}
        if Config.DEBUG_LEVEL > 1:
            logger.Log(
                f"Base model options from Config for {provider}: {final_model_options}",
                0,
            )  # Placeholder for future provider-specific base options
        if model_options_from_uri:
            final_model_options.update(model_options_from_uri)
            if Config.DEBUG_LEVEL > 1:
                logger.Log(
                    f"Updated model options with URI params: {final_model_options}", 0
                )

        max_llm_retries = 2  # Retries for the LLM call itself (e.g., network errors)
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
                    import google.generativeai as genai  # type: ignore
                    from google.generativeai.types import HarmCategory, HarmBlockThreshold  # type: ignore

                    # Format messages for Google API
                    google_messages = []
                    for msg in messages:
                        role = msg["role"]
                        if role == "system":
                            # Convert system messages to user prompts for Google
                            google_messages.append(
                                {"author": "user", "content": str(msg["content"])}
                            )
                        elif role == "assistant":
                            google_messages.append(
                                {"author": "model", "content": str(msg["content"])}
                            )
                        else:
                            # For user and other roles, use as is
                            google_messages.append(
                                {"author": role, "content": str(msg["content"])}
                            )

                    generation_config = (
                        genai.types.GenerationConfig(**final_model_options)
                        if final_model_options
                        else None
                    )
                    if output_format == "json" and generation_config:
                        generation_config.response_mime_type = "application/json"
                    elif output_format == "json":  # Create config if None
                        generation_config = genai.types.GenerationConfig(
                            response_mime_type="application/json"
                        )
                    if Config.DEBUG_LEVEL > 0:
                        logger.Log(
                            f"Google messages: {google_messages}, GenConfig: {generation_config}",
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
                        generation_config=generation_config,
                    )
                    full_response_content = self._stream_response_internal(
                        stream, provider, logger
                    )

                elif provider == "openrouter":
                    from Writer.Interface.OpenRouter import OpenRouter  # Local import

                    client: OpenRouter = self.clients[model_uri]
                    client.set_params(**final_model_options)  # Apply dynamic options
                    client.model = provider_model_name  # Ensure correct model is set

                    if output_format == "json":  # OpenRouter specific JSON mode
                        client.set_params(response_format={"type": "json_object"})

                    if Config.DEBUG_LEVEL > 0:
                        logger.Log(f"OpenRouter params: {client.__dict__}", 0)

                    # OpenRouter client currently doesn't stream in this implementation, directly gets content
                    full_response_content = client.chat(
                        messages=messages, seed=effective_seed
                    )
                    logger.Log(
                        f"OpenRouter full response received (length: {len(full_response_content)}).",
                        4,
                        stream=False,
                    )

                else:
                    raise NotImplementedError(
                        f"Provider '{provider}' not implemented in chat_and_stream_response."
                    )

                # If successful, break retry loop
                break

            except Exception as e:
                logger.Log(
                    f"LLM Call Error (Attempt {attempt + 1}/{max_llm_retries}) for {model_uri}: {e}",
                    7,
                )
                if attempt == max_llm_retries - 1:  # Last attempt
                    full_response_content = f"ERROR: LLM call failed after {max_llm_retries} attempts. Last error: {e}"
                    # Fall through to return the error message
                time.sleep(1.5**attempt)  # Exponential backoff

        end_time = time.time()
        duration = end_time - start_time
        response_tokens = len(full_response_content.split())  # Very rough token count
        tokens_per_sec = response_tokens / duration if duration > 0 else 0
        logger.Log(
            f"Generated response in {duration:.2f}s. Approx. {response_tokens} words, ~{tokens_per_sec:.2f} words/s.",
            4,
        )

        # Append assistant's response to the messages list
        updated_messages = messages + [
            {"role": "assistant", "content": full_response_content}
        ]

        # Save to Langchain debug log
        # Get caller function name dynamically for better log naming
        caller_function_name = "UnknownCaller"
        try:
            # stack returns a list of FrameInfo objects
            # FrameInfo(frame, filename, lineno, function, code_context, index)
            # We want the function name of the function that called ChatAndStreamResponse
            # The first frame (index 0) is ChatAndStreamResponse itself.
            # The second frame (index 1) is the function that called it (e.g. SafeGenerateText)
            # The third frame (index 2) is the function that called SafeGenerateText (e.g. GenerateOutline)
            # We'll construct a call path like "Grandparent.Parent.Child"
            call_stack = inspect.stack()
            relevant_frames = []
            for i in range(1, min(4, len(call_stack))):  # Max 3 levels up from current
                frame_name = call_stack[i].function
                if frame_name == "<module>":
                    frame_name = "Main"
                relevant_frames.append(frame_name)
            caller_function_name = (
                ".".join(reversed(relevant_frames)) if relevant_frames else "DirectCall"
            )

        except IndexError:
            pass  # Keep "UnknownCaller" if stack is too shallow

        logger.SaveLangchain(
            f"{caller_function_name}.{provider_model_name.replace('/','_')}",
            updated_messages,
        )

        return updated_messages

    def _stream_response_internal(
        self, stream_iterator: Any, provider: str, logger: Any
    ) -> str:
        """Helper to consolidate streaming logic for different providers."""
        response_text = ""
        chunk_count = 0
        stream_start_time = time.time()

        # Console output for streaming can be very verbose, toggle with DEBUG_LEVEL
        enable_console_stream = Config.DEBUG and Config.DEBUG_LEVEL > 1

        for chunk in stream_iterator:
            chunk_count += 1
            current_chunk_text = ""
            if provider == "ollama":
                current_chunk_text = chunk.get("message", {}).get("content", "")
            elif provider == "google":
                try:  # Google's stream can have empty chunks or non-text parts
                    current_chunk_text = chunk.text
                except Exception:  # ValueError, AttributeError if chunk has no .text
                    if Config.DEBUG_LEVEL > 1:
                        logger.Log(f"Google stream chunk without text: {chunk}", 0)
                    continue  # Skip if no text
            # Add other providers here
            else:
                # This should not be reached if called correctly
                logger.Log(f"Streaming not implemented for provider: {provider}", 7)
                break

            if current_chunk_text:
                response_text += current_chunk_text
                if enable_console_stream:
                    print(current_chunk_text, end="", flush=True)

        if enable_console_stream:
            print()  # Newline after streaming is done

        stream_duration = time.time() - stream_start_time
        logger.Log(
            f"Streamed {chunk_count} chunks for {provider} in {stream_duration:.2f}s.",
            0,
            stream=True,
        )  # Log this at a lower level
        return response_text

    def build_user_query(self, query_text: str) -> Dict[str, str]:
        """Constructs a user message dictionary."""
        return {"role": "user", "content": query_text}

    def build_system_query(self, query_text: str) -> Dict[str, str]:
        """Constructs a system message dictionary."""
        return {"role": "system", "content": query_text}

    def build_assistant_query(self, query_text: str) -> Dict[str, str]:
        """Constructs an assistant message dictionary."""
        return {"role": "assistant", "content": query_text}

    def get_last_message_text(self, messages: List[Dict[str, Any]]) -> str:
        """Safely retrieves the content of the last message."""
        if messages and isinstance(messages, list) and len(messages) > 0:
            last_msg = messages[-1]
            if isinstance(last_msg, dict):
                content = last_msg.get("content", "")
                return str(content) if content is not None else ""
        return ""
