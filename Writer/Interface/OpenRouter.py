# File: AIStoryWriter/Writer/Interface/OpenRouter.py
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
    # These are set at the class level as they are constant for all instances
    # but can be overridden if an instance needs specific headers (though not implemented here).
    _BASE_HEADERS = {
        "HTTP-Referer": "https://github.com/TerrapinTales/AIStoryWriter",  # Your project's URL
        "X-Title": "AIStoryWriter",  # Your project's name
        "Content-Type": "application/json",
        "Accept": "application/json",  # Expect JSON responses
    }

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        api_url: str = DEFAULT_API_URL,
        timeout: int = DEFAULT_TIMEOUT,
        provider_preferences: Optional[ProviderPreferences] = None,
        max_tokens: Optional[int] = None,  # Let model decide by default
        temperature: Optional[float] = 1.0,
        top_k: Optional[int] = 0,  # 0 means disabled for some models
        top_p: Optional[float] = 1.0,
        presence_penalty: Optional[float] = 0.0,
        frequency_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = 1.0,  # Often called "repeat_penalty"
        min_p: Optional[float] = 0.0,
        top_a: Optional[float] = 0.0,
        seed: Optional[int] = None,
        logit_bias: Optional[Mapping[int, float]] = None,  # Note: value is float
        response_format: Optional[
            Mapping[str, str]
        ] = None,  # e.g., {"type": "json_object"}
        stop: Optional[Union[str, List[str]]] = None,
        set_p50_defaults: bool = False,  # Fetch p50 percentile params for the model
        set_p90_defaults: bool = False,  # Fetch p90 percentile params for the model
    ):
        """
        Initializes the OpenRouter client.

        Args:
            api_key (str): Your OpenRouter API key.
            model (str, optional): Default model identifier. Defaults to DEFAULT_MODEL.
            api_url (str, optional): API endpoint URL. Defaults to DEFAULT_API_URL.
            timeout (int, optional): Request timeout in seconds. Defaults to DEFAULT_TIMEOUT.
            provider_preferences (ProviderPreferences, optional): Routing preferences.
            max_tokens (int, optional): Max tokens to generate.
            temperature (float, optional): Sampling temperature.
            ... (other LLM parameters)
            set_p50_defaults (bool, optional): If True, fetches and sets p50 default parameters for the model.
            set_p90_defaults (bool, optional): If True, fetches and sets p90 default parameters for the model.
        """
        if not api_key:
            raise ValueError("OpenRouter API key is required.")

        self.api_key = api_key
        self.model = model
        self.api_url = api_url
        self.timeout = timeout

        # Store parameters dynamically to allow easy update via set_params
        self.params: Dict[str, Any] = {
            "provider": provider_preferences,
            "max_tokens": max_tokens,  # API may call this "max_length" or similar depending on model
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
        # Filter out None values from initial params, as some APIs are sensitive
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
            response = requests.get(
                parameters_url, headers=headers, timeout=10
            )  # Short timeout for this meta-call
            response.raise_for_status()
            param_data = response.json().get("data", {})

            # Map OpenRouter percentile param names to our internal param names
            # (names are mostly consistent)
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
        """
        Updates the LLM parameters for subsequent calls.
        Only non-None values will update existing parameters.

        Example:
            `client.set_params(temperature=0.7, max_tokens=500)`
        """
        for key, value in kwargs.items():
            if value is not None:
                self.params[key] = value
            elif (
                key in self.params
            ):  # Allow setting a param back to None (or model default)
                self.params[key] = None
        # Clean up None values again after update
        self.params = {k: v for k, v in self.params.items() if v is not None}

    def _ensure_message_list(
        self, messages_input: Union[Message, List[Message]]
    ) -> List[Message]:
        """Ensures the input messages conform to a list of Message TypedDicts."""
        if isinstance(messages_input, list):
            # Validate structure of each message if it's already a list
            for msg in messages_input:
                if not (isinstance(msg, dict) and "role" in msg and "content" in msg):
                    raise ValueError(
                        "Invalid message structure in list. Each message must be a dict with 'role' and 'content'."
                    )
            return cast(
                List[Message], messages_input
            )  # Assuming structure is correct now
        elif (
            isinstance(messages_input, dict)
            and "role" in messages_input
            and "content" in messages_input
        ):
            return [cast(Message, messages_input)]
        else:
            raise ValueError(
                "Input messages must be a Message dictionary or a list of Message dictionaries."
            )

    def chat(
        self,
        messages: Union[Message, List[Message]],
        max_retries: int = 5,  # Reduced default retries from original
        seed: Optional[int] = None,  # Allow overriding instance seed per call
    ) -> str:
        """
        Sends a chat completion request to the OpenRouter API.

        Args:
            messages (Union[Message, List[Message]]): A single message or a list of messages.
            max_retries (int, optional): Number of retries for transient errors. Defaults to 5.
            seed (Optional[int], optional): Seed for this specific call, overrides instance seed if provided.

        Returns:
            str: The content of the assistant's response.

        Raises:
            requests.exceptions.HTTPError: For unrecoverable HTTP errors.
            Exception: For other critical errors or if max retries are exhausted.
        """
        processed_messages = self._ensure_message_list(messages)

        headers = {**self._BASE_HEADERS, "Authorization": f"Bearer {self.api_key}"}

        # Prepare body, merging call-specific seed if provided
        current_call_params = self.params.copy()
        if seed is not None:
            current_call_params["seed"] = seed

        body: Dict[str, Any] = {
            "model": self.model,
            "messages": processed_messages,
            "stream": False,  # This client does not handle streaming responses from OpenRouter
            **current_call_params,  # Spread operator for Python 3.5+ dicts
        }
        # Remove None values from body to avoid issues with some model providers via OpenRouter
        body = {k: v for k, v in body.items() if v is not None}

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url=self.api_url,
                    headers=headers,
                    data=json.dumps(body),
                    timeout=self.timeout,
                )
                response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses

                response_json = response.json()

                if "choices" in response_json and response_json["choices"]:
                    first_choice = response_json["choices"][0]
                    if (
                        "message" in first_choice
                        and "content" in first_choice["message"]
                    ):
                        return str(first_choice["message"]["content"])
                    else:
                        # This case should ideally not happen with a valid API response
                        error_detail = "Response 'choices' structure is missing 'message' or 'content'."
                elif "error" in response_json:
                    error_detail = response_json["error"].get(
                        "message", "Unknown error structure in API response."
                    )
                    error_code = response_json["error"].get(
                        "code", None
                    )  # OpenRouter often includes a code

                    print(
                        f"OpenRouter API Error (Code: {error_code}, Attempt {attempt + 1}/{max_retries}): {error_detail}"
                    )

                    # Specific handling for retryable errors
                    if error_code == 429 or (
                        isinstance(error_code, str)
                        and "rate_limit" in error_code.lower()
                    ):  # Rate limit
                        sleep_time = (
                            2**attempt
                        ) * 2  # Exponential backoff, starting at 2s
                        print(
                            f"Rate limited. Waiting {sleep_time} seconds before retrying..."
                        )
                        time.sleep(sleep_time)
                        continue  # Retry
                    elif (
                        error_code == 502
                        or error_code == 503
                        or (isinstance(error_code, int) and error_code >= 500)
                    ):  # Server-side errors
                        sleep_time = 2**attempt
                        print(
                            f"Server-side error ({error_code}). Waiting {sleep_time} seconds before retrying..."
                        )
                        time.sleep(sleep_time)
                        continue  # Retry
                    # Non-retryable client errors based on OpenRouter's typical codes
                    elif (
                        error_code == 400
                    ):  # Bad Request (often non-retryable if params are bad)
                        raise requests.exceptions.HTTPError(
                            f"OpenRouter Bad Request (400): {error_detail}",
                            response=response,
                        )
                    elif error_code == 401:  # Unauthorized
                        raise requests.exceptions.HTTPError(
                            f"OpenRouter Unauthorized (401): Invalid API key or credentials.",
                            response=response,
                        )
                    elif error_code == 402:  # Payment Required
                        raise requests.exceptions.HTTPError(
                            f"OpenRouter Payment Required (402): Insufficient credits.",
                            response=response,
                        )
                    # Other errors might be logged and retried by default by the loop
                else:
                    error_detail = "Unexpected response structure from OpenRouter (missing 'choices' or 'error')."

                print(
                    f"API Response Issue (Attempt {attempt + 1}/{max_retries}): {error_detail}. Full response: {response.text[:500]}"
                )

            except requests.exceptions.Timeout as e:
                print(f"Request timed out (Attempt {attempt + 1}/{max_retries}): {e}")
            except requests.exceptions.ConnectionError as e:
                print(f"Connection error (Attempt {attempt + 1}/{max_retries}): {e}")
            except (
                requests.exceptions.HTTPError
            ) as e:  # Catch errors raised by response.raise_for_status()
                print(
                    f"HTTP error occurred (Attempt {attempt + 1}/{max_retries}): {e}. Status: {e.response.status_code if e.response else 'N/A'}"
                )
                # Check if this HTTP error is one we want to retry (e.g. 5xx)
                if e.response is not None and e.response.status_code >= 500:
                    # Potentially retry for 5xx errors not caught by OpenRouter's specific error codes
                    pass  # Let the loop handle retry with backoff
                else:
                    raise  # Re-raise client-side HTTP errors (4xx) not handled above
            except json.JSONDecodeError as e:
                print(
                    f"Failed to decode JSON response (Attempt {attempt + 1}/{max_retries}): {e}. Response text: {response.text[:500]}"
                )
            except (
                Exception
            ) as e:  # Catch-all for other unexpected errors during the attempt
                print(
                    f"An unexpected error occurred during API call (Attempt {attempt + 1}/{max_retries}): {e}"
                )

            if attempt < max_retries - 1:  # If not the last attempt
                sleep_duration = 2**attempt  # Exponential backoff (1, 2, 4, 8 seconds)
                print(f"Retrying in {sleep_duration} seconds...")
                time.sleep(sleep_duration)
            else:  # Max retries reached
                raise Exception(
                    f"Failed to get a valid response from OpenRouter after {max_retries} attempts for model {self.model}."
                )

        # This part should ideally not be reached if the loop logic is correct
        raise Exception(
            "Exited retry loop without success or specific exception for OpenRouter chat."
        )
