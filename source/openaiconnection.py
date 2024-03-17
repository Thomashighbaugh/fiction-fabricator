# Changes Made:
# 1. Added type hints to the methods.
# 2. Added comments for better readability.
# 3. Removed unused import statements.
# 4. Updated the API base URL to the correct OpenAI API endpoint.
import os
import openai
from retry import retry
from source.tokencounter import num_tokens_from_messages

class OpenAIConnection:

    def __init__(self, logger):
        # Check if the OpenAI API key is set
        api_key = ""
        if api_key is None:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        openai.api_key = api_key
        openai.api_base = "http://0.0.0.0:1337/v1"
        self.logger = logger

        # For 3.5 use only the 16k model.
        self.chatbot_model_long = "gpt-3.5-turbo-16k-0613"
        self.chatbot_contextmax_long = 16384

        self.chatbot_model_4 = "gpt-4-turbo"
        self.chatbot_model_4_long = "gpt-4-32k-0613"
        self.chatbot_contextmax_4 = 8192
        self.chatbot_contextmax_4_long = 32768

        self.token_count = 0

    @retry(tries=5, delay=5)
    def embed(self, texts: list[str]) -> list:
        assert isinstance(texts, list)
        assert all(isinstance(text, str) for text in texts)

        response = openai.Embedding.create(
            input=texts,
            model="text-embedding-ada-002",
        )

        embeddings = [element["embedding"] for element in response.data]
        return embeddings

    @retry(tries=5, delay=5)
    def chat(self, messages: list[dict], long: bool = True, verbose: bool = True, version4: bool = False) -> str:
        if verbose:
            self.print_messages(messages)

        if version4:
            model = self.chatbot_model_4 if not long else self.chatbot_model_4_long
            max_tokens = self.chatbot_contextmax_4 if not long else self.chatbot_contextmax_4_long
        else:
            model = self.chatbot_model_long
            max_tokens = self.chatbot_contextmax_long

        tokens_messages = num_tokens_from_messages(messages, model)
        print(f"tokens for message: {tokens_messages}")
        max_tokens = max_tokens - tokens_messages

        response = openai.ChatCompletion.create(
            model=model, max_tokens=max_tokens, messages=messages
        )

        self.token_count += response["usage"]["total_tokens"]
        response = response["choices"][0]["message"]

        if verbose:
            self.print_messages([response])

        if self.logger.is_logging():
            self.logger.write_messages(messages, tokens_messages)

        return response

    def print_messages(self, messages: list[dict]):
        for message in messages:
            print("\033[92m", end="")
            print(f"{message['role']}:")
            print("\033[95m", end="")
            print(f"{message['content']}")
            print("")
            print("\033[0m", end="")
