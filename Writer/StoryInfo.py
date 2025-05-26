# File: AIStoryWriter/Writer/StoryInfo.py
# Purpose: Extracts final story metadata (title, summary, tags) using an LLM.

"""
Story Information Extraction Module.

This module uses an LLM to generate metadata for a completed story or a
comprehensive outline. The metadata typically includes:
- A compelling title for the story.
- A concise summary of the overall plot.
- Relevant tags or keywords for categorization.
- An optional overall quality rating (though this might be subjective).

The generated information is useful for display, archival, or as input for
other systems.
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface  # LLM interaction
from Writer.PrintUtils import Logger  # Logging
import json
from typing import List, Dict, Any, Optional


def get_story_info(
    interface: Interface,
    logger: Logger,
    story_context_messages: List[
        Dict[str, Any]
    ],  # Messages containing the story/outline
) -> Dict[str, Any]:
    """
    Generates metadata (title, summary, tags, rating) for a story using an LLM.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        story_context_messages (List[Dict[str, Any]]): A list of messages that
            provide the context of the story for the LLM. This should ideally
            contain the full story text or a comprehensive outline as the
            last user message.

    Returns:
        Dict[str, Any]: A dictionary containing the extracted story information.
                        Keys typically include "Title", "Summary", "Tags", "OverallRating".
                        Returns an empty dictionary or a dict with error info if generation fails.
    """
    logger.Log(
        "Requesting LLM to generate final story information (title, summary, tags)...",
        3,
    )

    if (
        not story_context_messages
        or not interface.get_last_message_text(story_context_messages).strip()
    ):
        logger.Log("Story context for GetStoryInfo is empty. Cannot generate info.", 6)
        return {"Error": "Story context was empty."}

    try:
        # The STATS_PROMPT asks the LLM to generate the JSON with specific fields.
        # It's appended to the existing story_context_messages.
        prompt_for_stats = Prompts.STATS_PROMPT
    except AttributeError:  # Should not happen if Prompts.py is correct
        logger.Log(f"STATS_PROMPT not found in Prompts module.", 7)
        return {"Error": "STATS_PROMPT is missing."}

    # Create a new list of messages for this specific request
    # We append the stats prompt as a new user query to the provided context.
    messages_for_info_gen = story_context_messages[:]  # Make a copy
    messages_for_info_gen.append(interface.build_user_query(prompt_for_stats))

    # Add a system prompt to guide the Info model if it's different or needs specific instruction
    # This prepends a system message, which is generally a good practice.
    final_messages_for_info_gen: List[Dict[str, Any]] = [
        interface.build_system_query(
            "You are an AI assistant skilled at summarizing content and extracting metadata in JSON format according to specific instructions."
        )
    ] + messages_for_info_gen

    try:
        # INFO_MODEL should be good at JSON generation and summarization/tagging.
        # The STATS_PROMPT itself requests JSON, so SafeGenerateJSON is appropriate.
        _response_messages, parsed_json_info = interface.safe_generate_json(
            logger,
            final_messages_for_info_gen,  # Use the combined messages list
            Config.INFO_MODEL,
            required_attribs=[
                "Title",
                "Summary",
                "Tags",
                "OverallRating",
            ],  # Ensure these keys exist
        )

        # Validate types if necessary, though safe_generate_json primarily checks for key existence.
        # Example: if not isinstance(parsed_json_info.get("OverallRating"), int): ...

        logger.Log(
            "Story information (title, summary, tags, rating) generated and parsed successfully.",
            4,
        )
        return parsed_json_info

    except Exception as e:
        # This catches failures from safe_generate_json (e.g., max retries for valid JSON)
        # or other unexpected issues during the call.
        logger.Log(
            f"An critical error occurred during story information generation: {e}", 7
        )
        return {
            "Error": f"Failed to generate story info: {e}",
            "Title": "Error Generating Title",
            "Summary": "Error Generating Summary",
            "Tags": "Error",
            "OverallRating": 0,
        }


# Example usage (typically called from Write.py)
if __name__ == "__main__":
    # This is for testing purposes only.
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

        # Mock for safe_generate_json
        def safe_generate_json(self, l, m, mo, required_attribs):
            print(
                f"Mock LLM Call (safe_generate_json) to {mo} for story info. Required: {required_attribs}"
            )
            # Simulate LLM generating the stats JSON
            # The last user message 'm[-1]' should contain Prompts.STATS_PROMPT
            if Prompts.STATS_PROMPT in m[-1]["content"]:
                mock_info = {
                    "Title": "The Grand Mock Adventure",
                    "Summary": "A tale of heroic mocks and simulated quests, leading to a testable conclusion.",
                    "Tags": "mock, test, adventure, python, ai",
                    "OverallRating": 85,  # Example rating
                }
                # Simulate the full message list that safe_generate_json would return
                response_msg_list = m + [
                    {"role": "assistant", "content": json.dumps(mock_info)}
                ]
                return (response_msg_list, mock_info)
            else:
                # Should not happen if called correctly
                error_info = {"Error": "Mock: STATS_PROMPT not found in messages."}
                return (
                    m + [{"role": "assistant", "content": json.dumps(error_info)}],
                    error_info,
                )

    mock_logger = MockLogger()
    mock_interface = MockInterface()

    Config.INFO_MODEL = "mock_info_gen_model"
    # Prompts.STATS_PROMPT is defined in Prompts.py and used directly.

    print("--- Testing get_story_info ---")

    # Simulate the context messages that would be passed (e.g., the full story outline)
    sample_story_outline_for_context = """
    # Chapter 1: The Beginning
    Our hero, Mockus, discovers a strange artifact.
    # Chapter 2: The Journey
    Mockus travels to the Giggling Mountains, facing Pythonic challenges.
    # Chapter 3: The Climax
    Mockus confronts the Bug King and uses the artifact to restore order.
    """
    story_context = [
        # Potentially other messages in history if GetStoryInfo is called mid-process,
        # but for this test, just the outline as user content.
        mock_interface.build_user_query(sample_story_outline_for_context)
    ]

    story_metadata = get_story_info(mock_interface, mock_logger, story_context)

    print("\nGenerated Story Info (Mocked):")
    print(f"  Title: {story_metadata.get('Title')}")
    print(f"  Summary: {story_metadata.get('Summary')}")
    print(f"  Tags: {story_metadata.get('Tags')}")
    print(f"  Rating: {story_metadata.get('OverallRating')}\n")

    assert story_metadata.get("Title") == "The Grand Mock Adventure"
    assert "heroic mocks" in story_metadata.get("Summary", "")
    assert isinstance(story_metadata.get("OverallRating"), int)

    print("--- Test with empty story context ---")
    empty_context_info = get_story_info(
        mock_interface, mock_logger, [mock_interface.build_user_query(" ")]
    )
    print(f"Info from empty context: {empty_context_info}\n")
    assert "Error" in empty_context_info

    print("--- Test with no messages (pathological) ---")
    no_messages_info = get_story_info(mock_interface, mock_logger, [])
    print(f"Info from no messages: {no_messages_info}\n")
    assert "Error" in no_messages_info
