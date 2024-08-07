"""
This module handles communication with the Large Language Model (LLM). 

It includes functionality for loading the appropriate system prompt
and making API calls to GPT4Free (g4f) for text generation and other tasks.
"""

import json
import os

import g4f


def get_system_prompt():
    """
    Retrieves the system prompt from the project's configuration file (config.json).

    The system prompt guides the LLM's behavior and personality.
    This function reads the prompt from the configuration file.
    If the configuration file is not found or doesn't contain a 'system_prompt',
    it falls back to a default system prompt.

    Returns:
        str: The retrieved system prompt string, or the default if none is found.
    """

    project_path = os.getcwd()
    config_file = os.path.join(project_path, "config", "config.json")

    # Load system prompt from configuration if available
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        system_prompt = config_data.get("system_prompt")

        # If the 'system_prompt' key doesn't exist in config_data:
        if system_prompt is None:
            system_prompt = "You are a helpful and creative writing assistant. Please follow the user's instructions and provide high-quality responses. Be informative and detailed."
            # Add the system prompt to config_data
            config_data["system_prompt"] = system_prompt
            # Write the updated configuration back to the file
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f)

    # Use the default system prompt if config file not found
    except FileNotFoundError:
        system_prompt = "You are a helpful and creative writing assistant. Please follow the user's instructions and provide high-quality responses. Be informative and detailed."

    return system_prompt


def call_g4f_api(prompt):
    """
    Calls the GPT4Free API for text generation using the specified prompt.

    This function uses the g4f library to interact with the GPT4Free API.
    It retrieves the API key from environment variables and
    constructs the API request using the provided prompt and
    the loaded system prompt.

    Args:
        prompt (str): The prompt to guide the LLM's text generation.

    Returns:
        str: The generated text response from the GPT4Free API.
    """

    api_instance = g4f.ChatCompletion()  # Initialize g4f chat completion

    # Get the API key - you'll need to set this up in your environment
    api_key = os.getenv("G4F_API_KEY")

    # Check if the API key is found
    if api_key is None:
        raise ValueError(
            "G4F_API_KEY environment variable not set. "
            "Please set your GPT4Free API key in the environment."
        )

    response = api_instance.create(
        provider=g4f.Provider.DeepInfra,
        api_key=api_key,
        model="microsoft/WizardLM-2-8x22B",  # Using the specified model by default
        messages=[
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": prompt},
        ],
    )

    return response
