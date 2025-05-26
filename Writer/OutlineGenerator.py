# File: AIStoryWriter/Writer/OutlineGenerator.py
# Purpose: Generates the main story outline, chapter by chapter, using story elements and LLM feedback.

"""
Overall Story Outline Generation Module.

This module orchestrates the creation of a chapter-by-chapter plot outline
for the entire story. It leverages previously generated story elements and
employs an iterative feedback loop with an LLM to refine the outline's
quality, coherence, and pacing.

The final output is a structured Markdown document detailing each chapter's
key events, character developments, and narrative purpose.
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
import Writer.LLMEditor as LLMEditor  # For feedback and rating functions
import Writer.Outline.StoryElements as StoryElements  # To generate story elements first
from Writer.Interface.Wrapper import Interface  # LLM interaction
from Writer.PrintUtils import Logger  # Logging
import json
from typing import Tuple, List, Dict, Any


def generate_outline(
    interface: Interface, logger: Logger, user_story_prompt: str
) -> Tuple[str, str, str, str]:
    """
    Generates a comprehensive, chapter-by-chapter story outline.

    The process involves:
    1. Extracting any overarching context or instructions from the user's prompt.
    2. Generating foundational story elements (genre, characters, plot synopsis, etc.).
    3. Producing an initial chapter-level outline based on the elements and prompt.
    4. Iteratively refining this outline using LLM-based feedback and quality checks.

    Args:
        interface (Interface): The LLM interaction wrapper instance.
        logger (Logger): The logging instance.
        user_story_prompt (str): The user's initial story idea or prompt.

    Returns:
        Tuple[str, str, str, str]:
            - printable_full_outline (str): A string containing the base context,
              story elements, and the final chapter-level outline, suitable for printing or saving.
            - story_elements_markdown (str): The Markdown content of the generated story elements.
            - final_chapter_level_outline (str): The refined chapter-by-chapter plot outline.
            - base_story_context (str): Extracted important context/instructions from the user prompt.
    """
    logger.Log("Starting Overall Story Outline Generation Process...", 2)

    if not user_story_prompt or not user_story_prompt.strip():
        error_msg = "User story prompt is empty. Cannot generate outline."
        logger.Log(error_msg, 7)
        return (
            error_msg,
            error_msg,
            error_msg,
            error_msg,
        )  # Return error for all tuple elements

    # 1. Extract Base Context/Instructions from the user's main prompt
    logger.Log("Extracting base context from user prompt...", 3)
    base_story_context = ""
    try:
        prompt_ctx_template = Prompts.GET_IMPORTANT_BASE_PROMPT_INFO
        formatted_prompt_ctx = prompt_ctx_template.format(_Prompt=user_story_prompt)
        messages_ctx = [interface.build_user_query(formatted_prompt_ctx)]
        # Using EVAL_MODEL as it's usually good for simple extraction and instruction following
        response_ctx_messages = interface.safe_generate_text(
            logger, messages_ctx, Config.EVAL_MODEL, min_word_count=5
        )
        base_story_context = interface.get_last_message_text(response_ctx_messages)
        logger.Log(
            f"Base story context extracted (first 100 chars): '{base_story_context[:100].replace('\n', ' ')}...'",
            3,
        )
    except KeyError as e:
        logger.Log(
            f"Formatting error in GET_IMPORTANT_BASE_PROMPT_INFO prompt: Missing key {e}",
            6,
        )  # Warning, not fatal
        base_story_context = (
            "Warning: Could not extract base context due to prompt template error."
        )
    except Exception as e:
        logger.Log(f"Unexpected error during base context extraction: {e}", 6)
        base_story_context = f"Warning: Error extracting base context - {e}."

    # 2. Generate Foundational Story Elements
    logger.Log("Generating foundational story elements...", 3)
    story_elements_markdown = StoryElements.generate_story_elements(
        interface, logger, user_story_prompt
    )
    if "Error:" in story_elements_markdown:  # Check if element generation failed
        logger.Log(f"Failed to generate story elements: {story_elements_markdown}", 7)
        # Propagate the error message
        return (
            story_elements_markdown,
            story_elements_markdown,
            story_elements_markdown,
            base_story_context,
        )

    # 3. Generate Initial Chapter-Level Outline
    logger.Log("Generating initial chapter-level outline...", 3)
    current_outline = ""
    current_history_for_revision: List[Dict[str, Any]] = []
    try:
        prompt_initial_outline_template = Prompts.OPTIMIZED_OVERALL_OUTLINE_GENERATION
        formatted_prompt_initial_outline = prompt_initial_outline_template.format(
            _UserStoryPrompt=user_story_prompt,
            _StoryElementsMarkdown=story_elements_markdown,
        )
        messages_initial_outline = [
            interface.build_system_query(Prompts.DEFAULT_SYSTEM_PROMPT),
            interface.build_user_query(formatted_prompt_initial_outline),
        ]

        response_initial_outline_messages = interface.safe_generate_text(
            logger,
            messages_initial_outline,
            Config.INITIAL_OUTLINE_WRITER_MODEL,
            min_word_count=200,  # Expect a reasonably detailed initial outline
        )
        current_outline = interface.get_last_message_text(
            response_initial_outline_messages
        )
        current_history_for_revision = (
            response_initial_outline_messages  # Save for revision loop context
        )
        logger.Log("Initial chapter-level outline generated.", 4)
    except KeyError as e:
        error_msg = f"Formatting error in OPTIMIZED_OVERALL_OUTLINE_GENERATION prompt: Missing key {e}"
        logger.Log(error_msg, 7)
        return error_msg, story_elements_markdown, error_msg, base_story_context
    except Exception as e:
        error_msg = f"Unexpected error during initial outline generation: {e}"
        logger.Log(error_msg, 7)
        return error_msg, story_elements_markdown, error_msg, base_story_context

    if not current_outline or "Error:" in current_outline:
        error_msg = (
            f"Initial outline generation failed or returned error: {current_outline}"
        )
        logger.Log(error_msg, 7)
        return error_msg, story_elements_markdown, current_outline, base_story_context

    # 4. Iterative Revision Loop for the Chapter-Level Outline
    logger.Log("Entering outline revision loop...", 3)
    iterations = 0

    while iterations < Config.OUTLINE_MAX_REVISIONS:
        iterations += 1
        logger.Log(
            f"Outline Revision Iteration {iterations}/{Config.OUTLINE_MAX_REVISIONS}", 3
        )

        try:
            feedback_on_outline = LLMEditor.GetFeedbackOnOutline(
                interface, logger, current_outline
            )
            logger.Log(
                f"Feedback received for outline (first 100 chars): '{feedback_on_outline[:100].replace('\n', ' ')}...'",
                3,
            )

            is_outline_complete = LLMEditor.GetOutlineRating(
                interface, logger, current_outline
            )
            logger.Log(f"Outline completion status: {is_outline_complete}", 3)

            if is_outline_complete and iterations > Config.OUTLINE_MIN_REVISIONS:
                logger.Log(
                    "Outline meets quality standards and minimum revision count. Exiting revision loop.",
                    4,
                )
                break

            # If it's the last iteration and still not "complete" by rating, we proceed anyway but log it.
            if iterations == Config.OUTLINE_MAX_REVISIONS and not is_outline_complete:
                logger.Log(
                    f"Max outline revisions ({Config.OUTLINE_MAX_REVISIONS}) reached. Proceeding with current outline despite IsComplete={is_outline_complete}.",
                    6,
                )
                break
            if (
                iterations == Config.OUTLINE_MAX_REVISIONS and is_outline_complete
            ):  # If complete on last iteration
                logger.Log(
                    f"Max outline revisions ({Config.OUTLINE_MAX_REVISIONS}) reached. Outline deemed complete. Exiting revision loop.",
                    4,
                )
                break

            logger.Log("Revising outline based on feedback...", 3)
            current_outline, current_history_for_revision = _revise_outline_internal(
                interface,
                logger,
                current_outline,
                feedback_on_outline,
                current_history_for_revision,
            )
            if "Error:" in current_outline:  # Check if revision step itself failed
                logger.Log(f"Outline revision failed: {current_outline}", 7)
                break  # Exit loop if revision fails critically

            logger.Log("Outline revised successfully.", 4)

        except Exception as e:
            logger.Log(
                f"Error during outline revision loop (iteration {iterations}): {e}", 7
            )
            # Potentially break or decide to proceed with the current_outline
            # For now, let's break to avoid further issues with a problematic outline
            break

    final_chapter_level_outline = current_outline

    # Assemble the full printable outline
    printable_full_outline = (
        f"# Base Story Context/Instructions:\n{base_story_context}\n\n---\n\n"
        f"# Story Elements:\n{story_elements_markdown}\n\n---\n\n"
        f"# Chapter-by-Chapter Outline:\n{final_chapter_level_outline}"
    )

    logger.Log("Overall Story Outline Generation Process Complete.", 2)
    return (
        printable_full_outline,
        story_elements_markdown,
        final_chapter_level_outline,
        base_story_context,
    )


def _revise_outline_internal(
    interface: Interface,
    logger: Logger,
    current_outline_text: str,
    feedback_text: str,
    history_messages: List[Dict[str, Any]],
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Internal helper function to revise an outline based on feedback.
    Manages the LLM call for revision.

    Args:
        interface: LLM interface.
        logger: Logger instance.
        current_outline_text: The current version of the outline.
        feedback_text: The feedback to apply.
        history_messages: The message history leading to the current outline, for context.

    Returns:
        Tuple[str, List[Dict[str, Any]]]: The revised outline text and the updated message history.
    """
    try:
        revision_prompt_template = Prompts.OUTLINE_REVISION_PROMPT
        formatted_revision_prompt = revision_prompt_template.format(
            _Outline=current_outline_text, _Feedback=feedback_text
        )
    except KeyError as e:
        error_msg = f"Formatting error in OUTLINE_REVISION_PROMPT: Missing key {e}"
        logger.Log(error_msg, 7)
        return (
            f"Error: {error_msg}",
            history_messages,
        )  # Return error and original history
    except Exception as e:
        error_msg = f"Unexpected error formatting revision prompt: {e}"
        logger.Log(error_msg, 7)
        return f"Error: {error_msg}", history_messages

    # Use a copy of the history and append the new user query for revision
    messages_for_revision = history_messages[:]
    messages_for_revision.append(interface.build_user_query(formatted_revision_prompt))

    try:
        response_revised_outline_messages = interface.safe_generate_text(
            logger,
            messages_for_revision,
            Config.INITIAL_OUTLINE_WRITER_MODEL,  # Or a dedicated REVISION_MODEL if preferred for this step
            min_word_count=len(current_outline_text.split())
            // 2,  # Expect substantial revision, not just minor tweaks
        )

        revised_outline_text: str = interface.get_last_message_text(
            response_revised_outline_messages
        )

        if not revised_outline_text or "Error:" in revised_outline_text:
            logger.Log(
                f"LLM failed to revise outline or returned an error: {revised_outline_text}",
                6,
            )
            return (
                current_outline_text,
                history_messages,
            )  # Return original outline and history on failure

        return revised_outline_text, response_revised_outline_messages

    except Exception as e:
        logger.Log(
            f"An unexpected error occurred during internal outline revision call: {e}",
            7,
        )
        return (
            f"Error: Unexpected critical error during revision - {e}",
            history_messages,
        )


# Example usage (typically called from Write.py)
if __name__ == "__main__":
    # This is for testing purposes only.
    class MockLogger:
        def Log(self, item: str, level: int, stream: bool = False):
            print(f"LOG L{level}: {item}")

        def save_langchain_interaction(self, label: str, messages: list):
            print(f"LANGCHAIN_SAVE: {label}")

    class MockInterface:
        def __init__(self):
            self.call_count = 0

        def build_system_query(self, q: str):
            return {"role": "system", "content": q}

        def build_user_query(self, q: str):
            return {"role": "user", "content": q}

        def get_last_message_text(self, msgs):
            return msgs[-1]["content"] if msgs else ""

        def safe_generate_text(self, l, m, mo, min_word_count):
            self.call_count += 1
            print(
                f"Mock LLM Call ({self.call_count}) to {mo} with min_words {min_word_count}. Prompt preview: {m[-1]['content'][:50]}..."
            )
            if "GET_IMPORTANT_BASE_PROMPT_INFO" in m[-1]["content"]:
                return [
                    *m,
                    {
                        "role": "assistant",
                        "content": "# Important Additional Context\n- Make it epic.",
                    },
                ]
            if "OPTIMIZED_STORY_ELEMENTS_GENERATION" in m[-1]["content"]:
                return [
                    *m,
                    {"role": "assistant", "content": "## Genre:\n- Epic Fantasy"},
                ]
            if "OPTIMIZED_OVERALL_OUTLINE_GENERATION" in m[-1]["content"]:
                return [
                    *m,
                    {
                        "role": "assistant",
                        "content": "Chapter 1: The Beginning\nChapter 2: The Middle",
                    },
                ]
            if "OPTIMIZED_CRITIC_OUTLINE_PROMPT" in m[-1]["content"]:
                return [*m, {"role": "assistant", "content": "Needs more dragons."}]
            if (
                "OUTLINE_COMPLETE_PROMPT" in m[-1]["content"]
            ):  # Simulate GetOutlineRating
                # To test the loop, make it return False first, then True
                if self.call_count < 6:  # Adjust this threshold based on expected calls
                    return [
                        *m,
                        {
                            "role": "assistant",
                            "content": json.dumps({"IsComplete": False}),
                        },
                    ]
                else:
                    return [
                        *m,
                        {
                            "role": "assistant",
                            "content": json.dumps({"IsComplete": True}),
                        },
                    ]
            if "OUTLINE_REVISION_PROMPT" in m[-1]["content"]:
                return [
                    *m,
                    {
                        "role": "assistant",
                        "content": "Chapter 1: The Beginning with Dragons\nChapter 2: The Middle with More Dragons",
                    },
                ]
            return [*m, {"role": "assistant", "content": "Mocked response."}]

        def safe_generate_json(
            self, l, m, mo, required_attribs
        ):  # For GetOutlineRating
            self.call_count += 1
            print(
                f"Mock LLM JSON Call ({self.call_count}) to {mo}. Prompt: {m[-1]['content'][:50]}..."
            )
            if "OUTLINE_COMPLETE_PROMPT" in m[-1]["content"]:
                if self.call_count < 6:  # Simulate a few revisions needed
                    return (
                        [
                            *m,
                            {
                                "role": "assistant",
                                "content": json.dumps({"IsComplete": False}),
                            },
                        ],
                        {"IsComplete": False},
                    )
                else:
                    return (
                        [
                            *m,
                            {
                                "role": "assistant",
                                "content": json.dumps({"IsComplete": True}),
                            },
                        ],
                        {"IsComplete": True},
                    )
            return ([*m, {"role": "assistant", "content": "{}"}], {})

    # Setup necessary Config values for the test
    Config.EVAL_MODEL = "mock_eval_model"
    Config.INITIAL_OUTLINE_WRITER_MODEL = "mock_outline_model"
    Config.MODEL_STORY_ELEMENTS_GENERATOR = "mock_elements_model"
    Config.OUTLINE_MIN_REVISIONS = 0  # For quicker test
    Config.OUTLINE_MAX_REVISIONS = 2  # For quicker test
    Prompts.DEFAULT_SYSTEM_PROMPT = "System prompt for testing."

    mock_logger = MockLogger()
    mock_interface = MockInterface()

    test_user_prompt = "A grand adventure to save the kingdom from an ancient evil."
    print(f"--- Testing generate_outline with prompt: '{test_user_prompt}' ---\n")

    full_out, elements, chap_out, base_ctx = generate_outline(
        mock_interface, mock_logger, test_user_prompt
    )

    print("\n--- Results ---")
    print(f"Base Context:\n{base_ctx}\n")
    print(f"Story Elements:\n{elements}\n")
    print(f"Chapter-Level Outline:\n{chap_out}\n")
    # print(f"Full Printable Outline:\n{full_out}") # Can be very long

    print(f"\n--- Test with empty user prompt ---")
    empty_results = generate_outline(mock_interface, mock_logger, "")
    print(empty_results)
