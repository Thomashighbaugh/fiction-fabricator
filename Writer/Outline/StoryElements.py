# File: Writer/Outline/StoryElements.py
# Purpose: Generates foundational story elements (genre, theme, plot, characters, etc.) using an LLM.

"""
Story Elements Generation Module.

This module is responsible for taking a user's initial story idea (prompt)
and expanding it into a comprehensive set of foundational story elements.
These elements serve as a structured basis for generating the more detailed
story outline and subsequent narrative content.

It utilizes an optimized LLM prompt to elicit rich, descriptive, and
imaginative details for various aspects of the story.
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface  # Assuming Interface is the class name
from Writer.PrintUtils import Logger  # Assuming Logger is the class name
from typing import Dict, Any, List


def generate_story_elements(
    interface: Interface, logger: Logger, user_story_prompt: str
) -> str:
    """
    Generates detailed story elements based on the user's initial story prompt.

    Args:
        interface (Interface): The LLM interaction wrapper instance.
        logger (Logger): The logging instance.
        user_story_prompt (str): The user's initial idea or prompt for the story.

    Returns:
        str: A Markdown formatted string containing the generated story elements.
             Returns an error message string if generation fails.
    """
    logger.Log("Initiating story elements generation...", 3)

    if not user_story_prompt or not user_story_prompt.strip():
        logger.Log("User story prompt is empty. Cannot generate story elements.", 7)
        return "Error: User story prompt was empty. Cannot generate story elements."

    try:
        prompt_template = Prompts.OPTIMIZED_STORY_ELEMENTS_GENERATION
        formatted_prompt = prompt_template.format(_UserStoryPrompt=user_story_prompt)
    except KeyError as e:
        logger.Log(
            f"Formatting error in OPTIMIZED_STORY_ELEMENTS_GENERATION prompt: Missing key {e}",
            7,
        )
        return (
            f"Error: Prompt template key error - {e}. Cannot generate story elements."
        )
    except Exception as e:  # Catch any other formatting errors
        logger.Log(
            f"Unexpected error during prompt formatting for story elements: {e}", 7
        )
        return f"Error: Unexpected prompt formatting error - {e}. Cannot generate story elements."

    messages: List[Dict[str, Any]] = [
        # Using a system prompt to guide the LLM's persona and task understanding
        interface.build_system_query(Prompts.DEFAULT_SYSTEM_PROMPT),
        interface.build_user_query(formatted_prompt),
    ]

    try:
        # Use a model suitable for creative brainstorming and structured Markdown output.
        # Config.MODEL_STORY_ELEMENTS_GENERATOR should be set appropriately.
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.MODEL_STORY_ELEMENTS_GENERATOR,
            min_word_count=250,  # Expect a substantial output for comprehensive elements
        )

        elements_markdown: str = interface.get_last_message_text(response_messages)

        if (
            not elements_markdown
            or elements_markdown.strip() == ""
            or "ERROR:" in elements_markdown
        ):
            logger.Log(
                "LLM failed to generate valid story elements or returned an error.", 6
            )
            # Check if the error was from the LLM itself or our safe_generate_text wrapper
            if "ERROR:" in elements_markdown:
                return f"Error during story element generation: LLM indicated an issue - {elements_markdown}"
            return "Error: LLM returned empty or invalid story elements."

        logger.Log("Story elements generated successfully.", 4)
        return elements_markdown

    except Exception as e:
        logger.Log(
            f"An unexpected error occurred during story elements generation: {e}", 7
        )
        # Consider logging traceback for debug: import traceback; logger.Log(traceback.format_exc(), 7)
        return f"Error: An unexpected critical error occurred: {e}. Please check logs."


# Example usage (typically called from OutlineGenerator.py or a main script)
if __name__ == "__main__":
    # This is for testing purposes only.
    # In a real run, Interface and Logger would be initialized in the main script.

    # Mock objects for testing
    class MockLogger:
        def Log(self, item: str, level: int, stream: bool = False):
            print(f"LOG L{level}: {item}")

        def save_langchain_interaction(self, label: str, messages: list):
            print(f"LANGCHAIN_SAVE: {label}")

    class MockInterface:
        def build_system_query(self, q: str):
            return {"role": "system", "content": q}

        def build_user_query(self, q: str):
            return {"role": "user", "content": q}

        def get_last_message_text(self, msgs):
            return msgs[-1]["content"] if msgs else ""

        def safe_generate_text(self, l, m, mo, min_word_count):
            print(f"Mock LLM Call to {mo} with min_words {min_word_count}")
            # Simulate an LLM response
            return [
                *m,  # original messages
                {
                    "role": "assistant",
                    "content": "# Story Title:\nThe Mock Adventure\n\n## Genre:\n- Test\n...",
                },
            ]

    mock_logger = MockLogger()
    mock_interface = MockInterface()

    # Ensure Config has a value for the model
    Config.MODEL_STORY_ELEMENTS_GENERATOR = (
        "mock_elements_model"  # Ensure this is set for test
    )
    Prompts.DEFAULT_SYSTEM_PROMPT = (
        "You are a helpful assistant for testing."  # Override for test
    )

    test_prompt = "A brave knight goes on a quest to find a legendary donut."
    print(f"Testing generate_story_elements with prompt: '{test_prompt}'\n")

    generated_elements = generate_story_elements(
        mock_interface, mock_logger, test_prompt
    )

    print("\n--- Generated Story Elements (Mocked) ---")
    print(generated_elements)

    print("\n--- Test with empty prompt ---")
    empty_prompt_elements = generate_story_elements(mock_interface, mock_logger, "")
    print(empty_prompt_elements)
