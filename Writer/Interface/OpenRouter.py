# File: AIStoryWriter/Writer/Interface/OpenRouter.py
# Purpose: Client for interacting with the OpenRouter API.

import json
import requests # type: ignore
import time
from typing import Any, List, Mapping, Optional, Literal, Union, TypedDict, cast

# Define Message and ProviderPreferences types for clarity (can be refined)
class MessageTypeDef(TypedDict):
    role: Literal['user', 'assistant', 'system', 'tool']
    content: str

class ProviderPreferencesTypeDef(TypedDict, total=False):
    allow_fallbacks: Optional[bool]
    require_parameters: Optional[bool]
    data_collection: Union[Literal['deny'], Literal['allow'], None]
    order: Optional[List[Literal[
        'OpenAI', 'Anthropic', 'HuggingFace', 'Google', 'Together', 'DeepInfra', 'Azure', 'Modal',
        'AnyScale', 'Replicate', 'Perplexity', 'Recursal', 'Fireworks', 'Mistral', 'Groq', 'Cohere',
        'Lepton', 'OctoAI', 'Novita', 'DeepSeek', 'Infermatic', 'AI21', 'Featherless', 'Mancer',
        'Mancer 2', 'Lynn 2', 'Lynn' # This list can grow, keep it representative
    ]]]

class OpenRouter:
    """
    A client for interacting with the OpenRouter.ai API.
    Handles request formatting, API calls, and basic error management.
    Reference: https://openrouter.ai/docs
    """

    DEFAULT_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_TIMEOUT_SECONDS = 360 # 6 minutes

    def __init__(self,
                 api_key: str,
                 model: str = "mistralai/mistral-7b-instruct", # A common default
                 provider_preferences: Optional[ProviderPreferencesTypeDef] = None,
                 max_tokens: Optional[int] = None, # Let model decide by default
                 temperature: Optional[float] = 0.7,
                 top_k: Optional[int] = 0, # 0 often means disabled or default handling
                 top_p: Optional[float] = 1.0,
                 presence_penalty: Optional[float] = 0.0,
                 frequency_penalty: Optional[float] = 0.0,
                 repetition_penalty: Optional[float] = 1.0, # Default 1.0 (no penalty)
                 min_p: Optional[float] = 0.0,
                 top_a: Optional[float] = 0.0,
                 seed: Optional[int] = None,
                 logit_bias: Optional[Mapping[int, float]] = None, # Note: OpenRouter expects float values
                 response_format: Optional[Mapping[str, str]] = None, # e.g., {"type": "json_object"}
                 stop: Optional[Union[str, List[str]]] = None,
                 api_url: str = DEFAULT_API_URL,
                 timeout: int = DEFAULT_TIMEOUT_SECONDS,
                 site_url_header: str = "https://github.com/your-repo/AIStoryWriter", # Replace with actual repo URL
                 app_name_header: str = "AIStoryWriter"
                 ):

        if not api_key:
            raise ValueError("OpenRouter API key is required.")

        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout
        self.site_url_header = site_url_header
        self.app_name_header = app_name_header

        # Store parameters to be sent with each request
        self.params: Dict[str, Any] = {
            "model": model,
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
            "stream": False # This client currently does not support true streaming from OpenRouter
        }
        # Filter out None values from initial params, so they don't override model defaults if not set
        self.params = {k: v for k, v in self.params.items() if v is not None}


    def set_params(self, **kwargs: Any) -> None:
        """
        Updates the stored parameters for subsequent API calls.
        Only provided parameters are updated.
        Example: client.set_params(temperature=0.5, max_tokens=500)
        """
        for key, value in kwargs.items():
            if key == "model": # Special handling for model name
                self.params["model"] = value
            elif value is not None: # Update if value is not None
                self.params[key] = value
            elif key in self.params: # Remove if value is None and key exists
                del self.params[key]

    @property
    def model(self) -> str:
        return cast(str, self.params.get("model", ""))

    @model.setter
    def model(self, value: str) -> None:
        self.params["model"] = value


    def _prepare_request_data(self, messages: List[MessageTypeDef], seed_override: Optional[int] = None) -> Dict[str, Any]:
        """Prepares the data payload for the API request."""
        request_data = self.params.copy() # Start with stored defaults/overrides
        request_data["messages"] = messages
        if seed_override is not None:
            request_data["seed"] = seed_override
        
        # Ensure logit_bias keys are strings if they are integers, as per some API requirements
        if "logit_bias" in request_data and request_data["logit_bias"]:
            logit_bias_processed = {}
            for k, v_bias in request_data["logit_bias"].items():
                logit_bias_processed[str(k)] = v_bias
            request_data["logit_bias"] = logit_bias_processed
            
        return request_data

    def chat(self,
             messages: List[MessageTypeDef],
             max_retries: int = 5, # Increased default retries
             seed: Optional[int] = None # Allows overriding seed per-call
             ) -> str:
        """
        Sends a chat completion request to the OpenRouter API.

        Args:
            messages: A list of message objects.
            max_retries: Maximum number of retries for transient errors.
            seed: Optional seed for this specific call, overriding instance default.

        Returns:
            The content of the assistant's response message.

        Raises:
            Exception: If the request fails after all retries or for critical errors.
        """
        if not self.params.get("model"):
            raise ValueError("Model not set for OpenRouter client.")

        request_data = self._prepare_request_data(messages, seed_override=seed)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url_header, # Recommended by OpenRouter
            "X-Title": self.app_name_header      # Recommended by OpenRouter
        }

        current_retry = 0
        while current_retry < max_retries:
            try:
                response = requests.post(
                    url=self.api_url,
                    headers=headers,
                    data=json.dumps(request_data),
                    timeout=self.timeout
                )
                response.raise_for_status() # Raises HTTPError for 4XX/5XX status codes

                response_json = response.json()

                if 'choices' in response_json and response_json['choices']:
                    first_choice = response_json['choices'][0]
                    if 'message' in first_choice and 'content' in first_choice['message']:
                        return str(first_choice['message']['content'])
                    else:
                        # This case should ideally not happen with a valid response
                        raise ValueError("OpenRouter response 'message' or 'content' missing in choice.")
                elif 'error' in response_json:
                    error_data = response_json['error']
                    error_code = error_data.get('code')
                    error_message = error_data.get('message', 'Unknown error from OpenRouter.')
                    # print(f"OpenRouter API Error (Code: {error_code}): {error_message}. Attempt {current_retry + 1}/{max_retries}.") # Replaced by logger

                    if error_code == 401: # Unauthorized
                        raise Exception(f"OpenRouter Authentication Error (401): {error_message}. Check API key.")
                    if error_code == 402: # Payment Required
                        raise Exception(f"OpenRouter Payment Error (402): {error_message}. Check account credits.")
                    if error_code == 429: # Rate limit
                        # print("Rate limited by OpenRouter. Waiting before retry...") # Replaced by logger
                        time.sleep(min(10 * (2 ** current_retry), 60)) # Exponential backoff, max 60s
                    # For other errors, just retry if not max_retries
                else:
                    # Unexpected response structure
                    raise ValueError(f"OpenRouter response missing 'choices' or 'error' field. Response: {response_json}")

            except requests.exceptions.HTTPError as http_err:
                # print(f"HTTP error occurred: {http_err} - Status: {http_err.response.status_code}. Attempt {current_retry + 1}/{max_retries}.") # Replaced by logger
                if http_err.response.status_code == 524: # Cloudflare timeout specific to OpenRouter sometimes
                    time.sleep(min(10 * (2 ** current_retry), 60))
                # Other HTTP errors will also trigger a retry up to max_retries
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as conn_err:
                # print(f"Connection/Timeout error: {conn_err}. Attempt {current_retry + 1}/{max_retries}.") # Replaced by logger
                time.sleep(min(5 * (2 ** current_retry), 30)) # Shorter backoff for network issues
            except json.JSONDecodeError as json_err:
                 # print(f"Failed to decode JSON response from OpenRouter: {json_err}. Response text: {response.text[:200]}... Attempt {current_retry + 1}/{max_retries}.") # Replaced by logger
                 # This is usually a server-side issue if status was 200 but content isn't JSON
                 pass
            except Exception as e: # Catch any other unexpected errors
                # print(f"An unexpected error occurred with OpenRouter client: {e}. Attempt {current_retry + 1}/{max_retries}.") # Replaced by logger
                # Decide if this error is retryable or should raise immediately
                if not isinstance(e, (ValueError)): # Retry general exceptions unless it's a ValueError we raised
                    time.sleep(1) # Short delay for truly unexpected errors before retry
                else: # If it's a ValueError we raised (e.g. bad response structure), re-raise after logging if max retries.
                    if current_retry >= max_retries - 1:
                        raise
                    else:
                        pass

            current_retry += 1

        raise Exception(f"OpenRouter request failed after {max_retries} retries for model {self.model}.")

if __name__ == '__main__':
    # Example Usage (requires OPENROUTER_API_KEY in .env or environment)
    # This part is for testing and would not be in the final library file.
    from dotenv import load_dotenv
    import os
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Please set OPENROUTER_API_KEY in your environment or .env file to run this example.")
    else:
        try:
            # Test with a common free model
            client = OpenRouter(api_key=api_key, model="mistralai/mistral-7b-instruct")
            
            # Test parameter setting
            client.set_params(temperature=0.8, max_tokens=150)
            print(f"Client configured for model: {client.model} with params: {client.params}")

            messages_test: List[MessageTypeDef] = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": "What is the capital of France?"}
            ]
            
            print("\nSending chat request...")
            response_content = client.chat(messages=messages_test)
            print("\nAssistant's Response:")
            print(response_content)

            # Test JSON mode (if model supports it, e.g. some OpenAI models via OpenRouter)
            # Note: Not all models on OpenRouter explicitly support the 'json_object' response_format.
            # You might need to use a model known for good JSON output and prompt engineering.
            # client.set_params(model="openai/gpt-3.5-turbo", response_format={"type": "json_object"})
            # messages_json_test: List[MessageTypeDef] = [
            #     {"role": "user", "content": "Provide a JSON object with two keys: 'city' and 'country', for Paris."}
            # ]
            # print("\nSending JSON mode chat request...")
            # response_json_content = client.chat(messages=messages_json_test)
            # print("\nAssistant's JSON Response:")
            # print(response_json_content)
            # try:
            #     parsed_json = json.loads(response_json_content)
            #     print("Parsed JSON:", parsed_json)
            # except json.JSONDecodeError:
            #     print("Failed to parse response as JSON.")

        except Exception as e:
            print(f"An error occurred during the example: {e}")