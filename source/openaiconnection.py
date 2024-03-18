import os
import openai
from retry import retry

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
        self.chatbot_model_long = "mistral-7b"
        self.chatbot_contextmax_long = 32768

        self.chatbot_model_4 = "mixtral-8x7b"
        self.chatbot_model_4_long = "mistral-7b"
        self.chatbot_contextmax_4 = 8192
        self.chatbot_contextmax_4_long = 32768

    @retry(tries=5, delay=5)
    def chat(
        self,
        messages: list[dict],
        long: bool = True,
        verbose: bool = True,
        version4: bool = False,
    ) -> str:
        if verbose:
            self.print_messages(messages)

        if version4:
            model = self.chatbot_model_4 if not long else self.chatbot_model_4_long
            max_tokens = (
                self.chatbot_contextmax_4
                if not long
                else self.chatbot_contextmax_4_long
            )
        else:
            model = self.chatbot_model_long
            max_tokens = self.chatbot_contextmax_long

        response = openai.ChatCompletion.create(
            model=model, max_tokens=max_tokens, messages=messages
        )

        response = response["choices"][0]["message"]

        if verbose:
            self.print_messages([response])

        return response

    def print_messages(self, messages: list[dict]):
        for message in messages:
            print("\033[92m", end="")
            print(f"{message['role']}:")
            print("\033[95m", end="")
            print(f"{message['content']}")
            print("")
            print("\033[0m", end="")
