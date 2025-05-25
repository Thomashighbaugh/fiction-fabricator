# File: AIStoryWriter/Writer/Outline/StoryElements.py
# Purpose: Generates foundational story elements (genre, theme, plot, characters, etc.)
#          based on an initial user prompt, using an LLM.

"""
This module is responsible for generating the core creative elements of a story.
It takes a user's initial story idea and uses an LLM, guided by an optimized prompt,
to flesh out details like genre, themes, a basic plot structure, character profiles,
and setting descriptions. These elements serve as a foundational guide for the
subsequent outlining and chapter/scene generation processes.
"""

from .. import Config  # Relative import for Config
from .. import Prompts  # Relative import for Prompts
from ..Interface.Wrapper import Interface  # Relative import for Interface
from ..PrintUtils import Logger  # Relative import for Logger


def GenerateStoryElements(
    interface: Interface, logger: Logger, user_story_prompt: str
) -> str:
    """
    Generates detailed story elements using an LLM based on the user's initial prompt.

    Args:
        interface: The LLM interface wrapper instance.
        logger: The Logger instance for logging messages.
        user_story_prompt: The user's initial idea or prompt for the story.

    Returns:
        A string containing the generated story elements, typically in Markdown format.
        Returns an empty string or error message if generation fails.
    """
    logger.Log("Initiating story elements generation...", 2)

    if not user_story_prompt or not user_story_prompt.strip():
        logger.Log("User story prompt is empty. Cannot generate story elements.", 5)
        return "// ERROR: User story prompt was empty. //"

    try:
        # Select the optimized prompt template for story elements
        prompt_template = Prompts.OPTIMIZED_STORY_ELEMENTS_GENERATION
        formatted_prompt = prompt_template.format(_UserStoryPrompt=user_story_prompt)

        messages = [
            interface.BuildSystemQuery(
                Prompts.DEFAULT_SYSTEM_PROMPT
            ),  # Use a capable system persona
            interface.BuildUserQuery(formatted_prompt),
        ]

        logger.Log(
            f"Sending request to LLM for story elements using model: {Config.MODEL_STORY_ELEMENTS_GENERATOR}",
            1,
        )

        # Use SafeGenerateText to ensure a substantive response
        response_messages = interface.SafeGenerateText(
            messages=messages,
            model_uri=Config.MODEL_STORY_ELEMENTS_GENERATOR,
            min_word_count=250,  # Expect a reasonably detailed output for story elements
        )

        elements_markdown: str = interface.GetLastMessageText(response_messages)

        if (
            not elements_markdown.strip() or "ERROR:" in elements_markdown
        ):  # Check if SafeGenerateText returned an error placeholder
            logger.Log("LLM failed to generate valid story elements.", 6)
            return f"// ERROR: LLM failed to generate story elements. Response: {elements_markdown[:200]}... //"

        logger.Log("Story elements generated successfully.", 2)
        if Config.DEBUG:
            logger.Log(
                f"Generated Story Elements (snippet):\n{elements_markdown[:500]}...", 1
            )

        return elements_markdown

    except Exception as e:
        logger.Log(
            f"An unexpected error occurred during story element generation: {e}", 7
        )
        # Log the full stack trace if in debug mode
        if Config.DEBUG:
            import traceback

            logger.Log(f"Traceback:\n{traceback.format_exc()}", 7)
        return f"// ERROR: An unexpected critical error occurred: {e} //"


# Example usage (typically not run directly from here)
if __name__ == "__main__":
    # This is for testing StoryElements.py itself
    # It requires a mock or actual Interface and Logger, and Config to be set up.

    # Setup mock Config for testing
    class MockConfig:
        MODEL_STORY_ELEMENTS_GENERATOR = (
            "ollama://mistral:latest"  # Use a fast local model for test
        )
        DEBUG = True
        DEBUG_LEVEL = 1  # For detailed logging during test

    Config = MockConfig()  # type: ignore
    Prompts.DEFAULT_SYSTEM_PROMPT = (
        "You are a helpful assistant."  # Simpler system prompt for test
    )

    # Mock Logger
    class MockLogger:
        def Log(self, item: str, level: int, stream_chunk: bool = False):
            print(f"LOG L{level}: {item}")

        def SaveLangchain(self, suffix: str, messages: list):
            print(f"LANGCHAIN_SAVE ({suffix}): {len(messages)} messages")

    # Mock Interface
    class MockInterface:
        def __init__(self, models, logger_instance):
            pass

        def BuildSystemQuery(self, q: str):
            return {"role": "system", "content": q}

        def BuildUserQuery(self, q: str):
            return {"role": "user", "content": q}

        def SafeGenerateText(self, messages: list, model_uri: str, min_word_count: int):
            print(
                f"SafeGenerateText called for {model_uri} with {len(messages)} messages. Min words: {min_word_count}"
            )
            # Simulate LLM response for story elements
            return [
                *messages,
                {
                    "role": "assistant",
                    "content": "# Story Title:\nThe Mockingbird's Shadow\n\n## Genre:\n- Mystery\n\n## Characters:\n### Main Character:\n- Name: Alex",
                },
            ]

        def GetLastMessageText(self, messages: list):
            return messages[-1]["content"] if messages else ""

    mock_logger = MockLogger()
    mock_interface = MockInterface(models=[], logger_instance=mock_logger)  # type: ignore

    test_prompt = "A detective in a cyberpunk city investigates a series of digital ghosts haunting the net."

    print("\n--- Testing GenerateStoryElements ---")
    generated_elements = GenerateStoryElements(mock_interface, mock_logger, test_prompt)  # type: ignore

    print("\n--- Generated Elements ---")
    print(generated_elements)

    print("\n--- Testing with empty prompt ---")
    empty_prompt_elements = GenerateStoryElements(mock_interface, mock_logger, "")  # type: ignore
    print(empty_prompt_elements)
