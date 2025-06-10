# File: Writer/StoryInfo.py
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
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
import json
from typing import List, Dict, Any, Optional
import Writer.Models as Models

# Heuristic: 1 word is approx 1.5 tokens in English, but can vary.
WORD_TO_TOKEN_RATIO = 1.5


def get_story_info(
    interface: Interface,
    logger: Logger,
    story_context_messages: List[Dict[str, Any]],
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
        prompt_for_stats = Prompts.STATS_PROMPT
    except AttributeError:
        logger.Log(f"STATS_PROMPT not found in Prompts module.", 7)
        return {"Error": "STATS_PROMPT is missing."}

    messages_for_info_gen = story_context_messages[:]
    messages_for_info_gen.append(interface.build_user_query(prompt_for_stats))

    final_messages_for_info_gen: List[Dict[str, Any]] = [
        interface.build_system_query(
            "You are an AI assistant skilled at summarizing content and extracting metadata in JSON format according to specific instructions."
        )
    ] + messages_for_info_gen

    try:
        # Expect a concise JSON, perhaps 200-300 words equivalent.
        MAX_TOKENS_FOR_STORY_INFO = int(300 * WORD_TO_TOKEN_RATIO)

        _response_messages, parsed_json_info = interface.safe_generate_json(
            logger,
            final_messages_for_info_gen,
            Config.INFO_MODEL,
            required_attribs=[
                "Title",
                "Summary",
                "Tags",
                "OverallRating",
            ],
            max_tokens=MAX_TOKENS_FOR_STORY_INFO,
            expected_response_model=Models.StoryMetadata,
        )

        logger.Log(
            "Story information (title, summary, tags, rating) generated and parsed successfully.",
            4,
        )
        return parsed_json_info

    except Exception as e:
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
