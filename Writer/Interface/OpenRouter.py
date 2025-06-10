# File: Writer/Interface/OpenRouter.py
# Purpose: Client for interacting with the OpenRouter API.

"""
OpenRouter API Client.

This module provides a Python class to interact with the OpenRouter API
for Large Language Model (LLM) completions. It handles:
- API request construction with various parameters.
- Authentication using an API key.
- Setting HTTP referer and title for API calls.
- Error handling and retries for common API issues.
- Optional fetching of p50/p90 model parameters.

Note: This client, as provided in the source, does not support streaming.
It makes a blocking request and returns the full completion.
"""

import json
import requests
import time
from typing import Any, List, Mapping, Optional, Literal, Union, TypedDict, cast, Dict


# Type definitions for message structures and provider preferences
class Message(TypedDict):
    role: Literal["user", "assistant", "system", "tool"]
    content: str


ProviderName = Literal[
    "OpenAI",
    "Anthropic",
    "HuggingFace",
    "Google",
    "Together",
    "DeepInfra",
    "Azure",
    "Modal",
    "AnyScale",
    "Replicate",
    "Perplexity",
    "Recursal",
    "Fireworks",
    "Mistral",
    "Groq",
    "Cohere",
    "Lepton",
    "OctoAI",
    "Novita",
    "DeepSeek",
    "Infermatic",
    "AI21",
    "Featherless",
    "Mancer",
    "Mancer 2",
    "Lynn 2",
    "Lynn",
]


class ProviderPreferences(TypedDict, total=False):
    allow_fallbacks: Optional[bool]
    require_parameters: Optional[bool]
    data_collection: Union[Literal["deny"], Literal["allow"], None]
    order: Optional[List[ProviderName]]


class OpenRouter:
    """
    A client for making requests to the OpenRouter API.
    Reference:
    - Models: https://openrouter.ai/docs#models
    - LLM Parameters: https://openrouter.ai/docs#llm-parameters
    - Parameters API: https://openrouter.ai/docs/parameters-api
    """

    DEFAULT_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "microsoft/wizardlm-2-7b"  # A common default, can be overridden
    DEFAULT_TIMEOUT = 3600  # 1 hour, quite long

    # HTTP headers for OpenRouter requests
    _BASE_HEADERS = {
        "HTTP-Referer": "https://github.com/Thomashighbaugh/fiction-fabricator",
        "X-Title": "FictionFabricator",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        api_url: str = DEFAULT_API_URL,
        timeout: int = DEFAULT_TIMEOUT,
        provider_preferences: Optional[ProviderPreferences] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = 1.0,
        top_k: Optional[int] = 0,
        top_p: Optional[float] = 1.0,
        presence_penalty: Optional[float] = 0.0,
        frequency_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = 1.0,
        min_p: Optional[float] = 0.0,
        top_a: Optional[float] = 0.0,
        seed: Optional[int] = None,
        logit_bias: Optional[Mapping[int, float]] = None,
        response_format: Optional[Mapping[str, str]] = None,
        stop: Optional[Union[str, List[str]]] = None,
        set_p50_defaults: bool = False,
        set_p90_defaults: bool = False,
    ):
        """
        Initializes the OpenRouter client.
        """
        if not api_key:
            raise ValueError("OpenRouter API key is required.")

        self.api_key = api_key
        self.model = model
        self.api_url = api_url
        self.timeout = timeout

        self.params: Dict[str, Any] = {
            "provider": provider_preferences,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "repetition_penalty": repetition_penalty,
            "min_p": min_p,
            "top_a": top_a,
            "seed": seed,
            "logit_bias": logit_bias,
            "response_format": response_format,
            "stop": stop,
        }
        self.params = {k: v for k, v in self.params.items() if v is not None}

        if set_p50_defaults or set_p90_defaults:
            self._fetch_and_set_percentile_params(
                percentile_key_suffix="p50" if set_p50_defaults else "p90"
            )

    def _fetch_and_set_percentile_params(self, percentile_key_suffix: str) -> None:
        """Fetches p50 or p90 parameters from OpenRouter and updates instance parameters."""
        parameters_url = f"https://openrouter.ai/api/v1/parameters/{self.model}"
        headers = {**self._BASE_HEADERS, "Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(parameters_url, headers=headers, timeout=10)
            response.raise_for_status()
            param_data = response.json().get("data", {})

            percentile_params_to_update = {
                "temperature": f"temperature_{percentile_key_suffix}",
                "top_k": f"top_k_{percentile_key_suffix}",
                "top_p": f"top_p_{percentile_key_suffix}",
                "presence_penalty": f"presence_penalty_{percentile_key_suffix}",
                "frequency_penalty": f"frequency_penalty_{percentile_key_suffix}",
                "repetition_penalty": f"repetition_penalty_{percentile_key_suffix}",
                "min_p": f"min_p_{percentile_key_suffix}",
                "top_a": f"top_a_{percentile_key_suffix}",
            }

            for internal_param, openrouter_key in percentile_params_to_update.items():
                if (
                    openrouter_key in param_data
                    and param_data[openrouter_key] is not None
                ):
                    self.params[internal_param] = param_data[openrouter_key]

            print(
                f"INFO: Updated parameters with {percentile_key_suffix} defaults for model {self.model}."
            )

        except requests.exceptions.RequestException as e:
            print(
                f"WARNING: Could not fetch {percentile_key_suffix} parameters for {self.model}: {e}"
            )
        except KeyError as e:
            print(
                f"WARNING: Error parsing {percentile_key_suffix} parameters for {self.model}: Missing key {e}"
            )

    def set_params(self, **kwargs: Any) -> None:
        """Updates the LLM parameters for subsequent calls."""
        for key, value in kwargs.items():
            if value is not None:
                self.params[key] = value
            elif key in self.params:
                self.params[key] = None
        self.params = {k: v for k, v in self.params.items() if v is not None}

    def _ensure_message_list(
        self, messages_input: Union[Message, List[Message]]
    ) -> List[Message]:
        """Ensures the input messages conform to a list of Message TypedDicts."""
        if isinstance(messages_input, list):
            for msg in messages_input:
                if not (isinstance(msg, dict) and "role" in msg and "content" in msg):
                    raise ValueError(
                        "Invalid message structure. Each message must be a dict with 'role' and 'content'."
                    )
            return cast(List[Message], messages_input)
        elif (
            isinstance(messages_input, dict)
            and "role" in messages_input
            and "content" in messages_input
        ):
            return [cast(Message, messages_input)]
        else:
            raise ValueError("Input messages must be a Message or a list of Messages.")

    def chat(
        self,
        messages: Union[Message, List[Message]],
        max_retries: int = 5,
        seed: Optional[int] = None,
    ) -> str:
        """
        Sends a chat completion request to the OpenRouter API.
        """
        processed_messages = self._ensure_message_list(messages)
        headers = {**self._BASE_HEADERS, "Authorization": f"Bearer {self.api_key}"}

        current_call_params = self.params.copy()
        if seed is not None:
            current_call_params["seed"] = seed

        body: Dict[str, Any] = {
            "model": self.model,
            "messages": processed_messages,
            "stream": False,
            **current_call_params,
        }
        body = {k: v for k, v in body.items() if v is not None}

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url=self.api_url,
                    headers=headers,
                    data=json.dumps(body),
                    timeout=self.timeout,
                )
                response.raise_for_status()

                response_json = response.json()

                if "choices" in response_json and response_json["choices"]:
                    first_choice = response_json["choices"][0]
                    if (
                        "message" in first_choice
                        and "content" in first_choice["message"]
                    ):
                        return str(first_choice["message"]["content"])
                    else:
                        error_detail = "Response 'choices' structure is missing 'message' or 'content'."
                elif "error" in response_json:
                    error_detail = response_json["error"].get(
                        "message", "Unknown error structure."
                    )
                    error_code = response_json["error"].get("code", None)
                    print(
                        f"OpenRouter API Error (Code: {error_code}, Attempt {attempt + 1}/{max_retries}): {error_detail}"
                    )

                    if error_code == 429 or (
                        isinstance(error_code, str)
                        and "rate_limit" in error_code.lower()
                    ):
                        sleep_time = (2**attempt) * 2
                        print(f"Rate limited. Waiting {sleep_time} seconds...")
                        time.sleep(sleep_time)
                        continue
                    elif (
                        error_code == 502
                        or error_code == 503
                        or (isinstance(error_code, int) and error_code >= 500)
                    ):
                        sleep_time = 2**attempt
                        print(
                            f"Server-side error ({error_code}). Waiting {sleep_time} seconds..."
                        )
                        time.sleep(sleep_time)
                        continue
                    elif error_code == 400:
                        raise requests.exceptions.HTTPError(
                            f"OpenRouter Bad Request (400): {error_detail}",
                            response=response,
                        )
                    elif error_code == 401:
                        raise requests.exceptions.HTTPError(
                            f"OpenRouter Unauthorized (401): Invalid API key.",
                            response=response,
                        )
                    elif error_code == 402:
                        raise requests.exceptions.HTTPError(
                            f"OpenRouter Payment Required (402): Insufficient credits.",
                            response=response,
                        )
                else:
                    error_detail = "Unexpected response structure from OpenRouter."

                print(
                    f"API Response Issue (Attempt {attempt + 1}/{max_retries}): {error_detail}. Full response: {response.text[:500]}"
                )

            except requests.exceptions.Timeout as e:
                print(f"Request timed out (Attempt {attempt + 1}/{max_retries}): {e}")
            except requests.exceptions.ConnectionError as e:
                print(f"Connection error (Attempt {attempt + 1}/{max_retries}): {e}")
            except requests.exceptions.HTTPError as e:
                print(
                    f"HTTP error (Attempt {attempt + 1}/{max_retries}): {e}. Status: {e.response.status_code if e.response else 'N/A'}"
                )
                if e.response is not None and e.response.status_code >= 500:
                    pass
                else:
                    raise
            except json.JSONDecodeError as e:
                print(
                    f"Failed to decode JSON (Attempt {attempt + 1}/{max_retries}): {e}. Response: {response.text[:500]}"
                )
            except Exception as e:
                print(f"Unexpected error (Attempt {attempt + 1}/{max_retries}): {e}")

            if attempt < max_retries - 1:
                sleep_duration = 2**attempt
                print(f"Retrying in {sleep_duration} seconds...")
                time.sleep(sleep_duration)
            else:
                raise Exception(
                    f"Failed to get valid response from OpenRouter after {max_retries} attempts."
                )

        raise Exception("Exited retry loop without success or specific exception.")
