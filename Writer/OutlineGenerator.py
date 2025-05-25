# File: AIStoryWriter/Writer/OutlineGenerator.py
# Purpose: Generates the main story outline (chapter-by-chapter plot summaries)
#          based on user prompt and generated story elements. Includes a revision loop.

"""
This module orchestrates the generation of the overall story outline.
It takes the initial user prompt and the detailed story elements (from StoryElements.py)
to produce a chapter-by-chapter plot outline. This outline serves as the primary
roadmap for subsequent scene breakdown and narrative generation.

The process includes:
1. Extracting any overarching "base context" or meta-instructions from the user's prompt.
2. Generating an initial chapter-level outline using the story elements and user prompt.
3. Iteratively refining this outline using an LLM-based feedback and revision loop
   until it meets quality standards or a maximum number of revisions is reached.
"""

from typing import Tuple, List, Dict

from .. import Config  # Relative import for Config
from .. import Prompts  # Relative import for Prompts
from ..Interface.Wrapper import Interface  # Relative import for Interface
from ..PrintUtils import Logger  # Relative import for Logger
from .Outline import StoryElements  # Relative import for StoryElements module
from ..LLMEditor import (
    GetFeedbackOnOutline,
    GetOutlineRating,
)  # Relative import for LLMEditor functions


def GenerateOutline(
    interface: Interface, logger: Logger, user_story_prompt: str
) -> Tuple[str, str, str, str]:
    """
    Generates and refines the main story outline.

    Args:
        interface: The LLM interface wrapper instance.
        logger: The Logger instance for logging.
        user_story_prompt: The user's initial story idea.

    Returns:
        A tuple containing:
        - printable_full_outline (str): A string combining base context, story elements,
                                        and the final chapter-level outline for output.
        - story_elements_markdown (str): The generated story elements in Markdown.
        - final_chapter_level_outline (str): The refined chapter-by-chapter plot outline.
        - base_story_context (str): Extracted meta-instructions from the user prompt.
    """
    logger.Log("Starting Overall Story Outline Generation Process...", 2)

    # --- 1. Extract Base Context from User Prompt ---
    logger.Log("Extracting base context from user prompt...", 3)
    base_context_prompt_template = Prompts.GET_IMPORTANT_BASE_PROMPT_INFO
    formatted_base_context_prompt = base_context_prompt_template.format(
        _Prompt=user_story_prompt
    )

    base_context_messages = [
        interface.BuildSystemQuery(
            Prompts.DEFAULT_SYSTEM_PROMPT
        ),  # A capable system prompt
        interface.BuildUserQuery(formatted_base_context_prompt),
    ]

    # Using EVAL_MODEL as it's typically good for structured extraction/simple tasks
    base_context_response_messages = interface.SafeGenerateText(
        messages=base_context_messages,
        model_uri=Config.EVAL_MODEL,
        min_word_count=5,  # Expect at least "None found" or some points
    )
    base_story_context: str = interface.GetLastMessageText(
        base_context_response_messages
    )
    logger.Log(
        f"Base context extracted (snippet): {base_story_context[:150].strip()}...", 3
    )

    # --- 2. Generate Story Elements ---
    # This function is already robust and uses its own configured model
    story_elements_markdown = StoryElements.GenerateStoryElements(
        interface, logger, user_story_prompt
    )
    if "// ERROR:" in story_elements_markdown:
        logger.Log(
            "Critical error during story elements generation. Aborting outline generation.",
            7,
        )
        # Return placeholders to indicate failure
        return (
            "// ERROR IN STORY ELEMENTS //",
            story_elements_markdown,
            "// OUTLINE GENERATION ABORTED //",
            base_story_context,
        )

    # --- 3. Generate Initial Chapter-Level Outline ---
    logger.Log("Generating initial chapter-level outline...", 3)
    initial_outline_prompt_template = Prompts.OPTIMIZED_OVERALL_OUTLINE_GENERATION
    formatted_initial_outline_prompt = initial_outline_prompt_template.format(
        _UserStoryPrompt=user_story_prompt,
        _StoryElementsMarkdown=story_elements_markdown,
    )

    initial_outline_messages = [
        interface.BuildSystemQuery(Prompts.DEFAULT_SYSTEM_PROMPT),
        interface.BuildUserQuery(formatted_initial_outline_prompt),
    ]

    initial_outline_response_messages = interface.SafeGenerateText(
        messages=initial_outline_messages,
        model_uri=Config.INITIAL_OUTLINE_WRITER_MODEL,
        min_word_count=200,  # Expect a substantial outline
    )
    current_outline: str = interface.GetLastMessageText(
        initial_outline_response_messages
    )

    if not current_outline.strip() or "// ERROR:" in current_outline:
        logger.Log("LLM failed to generate a valid initial outline.", 6)
        return (
            f"{base_story_context}\n\n{story_elements_markdown}\n\n// ERROR: INITIAL OUTLINE FAILED //",
            story_elements_markdown,
            "// ERROR: INITIAL OUTLINE FAILED //",
            base_story_context,
        )
    logger.Log("Initial chapter-level outline generated successfully.", 3)

    # --- 4. Revision Loop for Overall Outline ---
    logger.Log("Starting outline revision loop...", 2)
    revision_iteration = 0
    # Start history with the system prompt and the assistant's first outline generation
    current_revision_history: List[Dict[str, str]] = [
        interface.BuildSystemQuery(Prompts.DEFAULT_SYSTEM_PROMPT),
        # We don't include the user's prompt for OPTIMIZED_OVERALL_OUTLINE_GENERATION in history
        # because ReviseOutline will receive _CurrentOutline and _Feedback directly.
        # The history for ReviseOutline starts fresh or with the last specific revision interaction.
        # For LLMEditor.GetFeedbackOnOutline, it builds its own small history.
    ]
    # To give ReviseOutline context, its history should be the one that led to current_outline.
    # So, initial_outline_response_messages contains the full exchange for the first outline.
    current_revision_history_for_revise_func = initial_outline_response_messages

    while revision_iteration < Config.OUTLINE_MAX_REVISIONS:
        revision_iteration += 1
        logger.Log(
            f"Outline Revision Iteration {revision_iteration}/{Config.OUTLINE_MAX_REVISIONS}",
            3,
        )

        feedback_on_outline = GetFeedbackOnOutline(interface, logger, current_outline)
        logger.Log(
            f"Feedback received for outline (iteration {revision_iteration}).", 3
        )
        if Config.DEBUG:
            logger.Log(
                f"Outline Feedback (Iter {revision_iteration}):\n{feedback_on_outline[:300]}...",
                1,
            )

        # GetOutlineRating returns True if complete/good, False otherwise
        is_outline_complete = GetOutlineRating(interface, logger, current_outline)
        logger.Log(
            f"Outline 'IsComplete' rating (iteration {revision_iteration}): {is_outline_complete}",
            3,
        )

        if is_outline_complete and revision_iteration > Config.OUTLINE_MIN_REVISIONS:
            logger.Log(
                "Outline meets quality standards and minimum revisions. Exiting revision loop.",
                2,
            )
            break

        if (
            revision_iteration >= Config.OUTLINE_MAX_REVISIONS
        ):  # Check here to log before breaking
            logger.Log("Maximum outline revisions reached. Exiting revision loop.", 2)
            break

        logger.Log(
            f"Revising outline based on feedback (iteration {revision_iteration})...", 3
        )
        current_outline, current_revision_history_for_revise_func = (
            _revise_outline_internal(
                interface,
                logger,
                current_outline,
                feedback_on_outline,
                current_revision_history_for_revise_func,
            )
        )
        if "// ERROR:" in current_outline:
            logger.Log("Error during outline revision. Using previous version.", 6)
            # current_outline would retain its pre-error value due to how _revise_outline_internal returns
            break
        logger.Log(f"Outline revised (iteration {revision_iteration}).", 3)

    final_chapter_level_outline = current_outline
    logger.Log("Outline revision loop finished.", 2)

    # Assemble the full printable outline
    printable_full_outline = (
        f"# Base Story Context & Instructions\n{base_story_context}\n\n"
        f"---\n# Generated Story Elements\n{story_elements_markdown}\n\n"
        f"---\n# Final Chapter-Level Plot Outline\n{final_chapter_level_outline}"
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
    current_history_for_llm: List[Dict[str, str]],
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Internal helper to call the LLM for revising an outline.
    Manages the message history specifically for the revision call.
    """
    revision_prompt_template = Prompts.OUTLINE_REVISION_PROMPT
    formatted_revision_prompt = revision_prompt_template.format(
        _Outline=current_outline_text, _Feedback=feedback_text
    )

    # The history for a revision should ideally be the conversation that LED to the current_outline_text,
    # then the feedback, then the request to revise.
    # However, to keep it simpler and avoid overly long context, we can also just send the current outline and feedback.
    # The `current_history_for_llm` here is passed from the main loop, representing the conversation so far
    # that produced `current_outline_text`. We append the new user request for revision to this.

    messages_for_revision = current_history_for_llm[
        :
    ]  # Start with the history that produced the current outline
    # The last message in current_history_for_llm is the assistant's `current_outline_text`.
    # We now add a user message asking to revise it based on new feedback.
    # The `formatted_revision_prompt` itself contains the outline and feedback.
    # So, we can just append a new user query with formatted_revision_prompt.
    # However, standard practice is: System, User, Assistant, User, Assistant...
    # The current_history_for_llm ends with an assistant message (the outline).
    # So, we should append a user message.

    messages_for_revision.append(interface.BuildUserQuery(formatted_revision_prompt))
    # The LLM will see its previous output (the outline, as part of the prompt) and the new feedback.

    response_messages = interface.SafeGenerateText(
        messages=messages_for_revision,  # Send the continued conversation
        model_uri=Config.INITIAL_OUTLINE_WRITER_MODEL,  # Or a dedicated REVISION_MODEL if configured
        min_word_count=len(current_outline_text.split())
        // 2,  # Expect revision to be substantial
    )

    revised_outline_text: str = interface.GetLastMessageText(response_messages)

    if not revised_outline_text.strip() or "// ERROR:" in revised_outline_text:
        logger.Log(
            "LLM failed to generate a valid revised outline. Returning original.", 6
        )
        return (
            current_outline_text,
            current_history_for_llm,
        )  # Return original and its history

    return (
        revised_outline_text,
        response_messages,
    )  # Return new outline and its full generating history


# Example usage (typically not run directly from here)
if __name__ == "__main__":
    # This is for testing OutlineGenerator.py itself.
    # Requires mock or actual Interface, Logger, StoryElements, LLMEditor, Config, Prompts.

    class MockConfigOutline:
        INITIAL_OUTLINE_WRITER_MODEL = "ollama://mistral:latest"
        EVAL_MODEL = "ollama://mistral:latest"  # For base context and rating
        REVISION_MODEL = "ollama://mistral:latest"  # For feedback
        OUTLINE_MIN_REVISIONS = 0
        OUTLINE_MAX_REVISIONS = 1  # Quick test
        DEBUG = True
        DEBUG_LEVEL = 1

    Config = MockConfigOutline()  # type: ignore
    Prompts.DEFAULT_SYSTEM_PROMPT = "You are an assistant."

    class MockLoggerOutline:
        def Log(self, item: str, level: int, stream_chunk: bool = False):
            print(f"LOG L{level}: {item}")

        def SaveLangchain(self, suffix: str, messages: list):
            print(f"LANGCHAIN_SAVE ({suffix}): {len(messages)} messages")

    class MockStoryElements:
        @staticmethod
        def GenerateStoryElements(interface, logger, prompt):
            logger.Log("MockStoryElements.GenerateStoryElements called.", 1)
            return "# Mock Story Elements\n- Genre: Sci-Fi\n- Character: Captain Astra"

    StoryElements = MockStoryElements()  # type: ignore

    class MockLLMEditor:
        _feedback_count = 0
        _rating_val = False

        @staticmethod
        def GetFeedbackOnOutline(interface, logger, outline):
            MockLLMEditor._feedback_count += 1
            logger.Log(
                f"MockLLMEditor.GetFeedbackOnOutline called (call {MockLLMEditor._feedback_count}).",
                1,
            )
            if MockLLMEditor._feedback_count == 1:
                return "Feedback: Needs more detail in chapter 2."
            return "Feedback: Looks good now."

        @staticmethod
        def GetOutlineRating(interface, logger, outline):
            logger.Log(
                f"MockLLMEditor.GetOutlineRating called. Current rating val: {MockLLMEditor._rating_val}",
                1,
            )
            # Simulate improvement: first False, then True
            current_val = MockLLMEditor._rating_val
            MockLLMEditor._rating_val = True  # Next time it will be true
            return current_val

    # Monkey patch LLMEditor for testing this module
    import sys

    # Create a mock module for LLMEditor
    mock_llm_editor_module = type(sys)("LLMEditor")
    mock_llm_editor_module.GetFeedbackOnOutline = MockLLMEditor.GetFeedbackOnOutline  # type: ignore
    mock_llm_editor_module.GetOutlineRating = MockLLMEditor.GetOutlineRating  # type: ignore
    sys.modules["AIStoryWriter.LLMEditor"] = mock_llm_editor_module  # type: ignore
    # And update the local import
    GetFeedbackOnOutline = MockLLMEditor.GetFeedbackOnOutline  # type: ignore
    GetOutlineRating = MockLLMEditor.GetOutlineRating  # type: ignore

    class MockInterfaceOutline:
        def __init__(self, models, logger_instance):
            pass

        def BuildSystemQuery(self, q: str):
            return {"role": "system", "content": q}

        def BuildUserQuery(self, q: str):
            return {"role": "user", "content": q}

        _gen_text_call = 0

        def SafeGenerateText(self, messages: list, model_uri: str, min_word_count: int):
            MockInterfaceOutline._gen_text_call += 1
            print(
                f"MockInterface.SafeGenerateText called for {model_uri} (call {MockInterfaceOutline._gen_text_call}). Min words: {min_word_count}. Prompt: {messages[-1]['content'][:60]}..."
            )
            if "GET_IMPORTANT_BASE_PROMPT_INFO" in messages[-1]["content"]:
                return [
                    *messages,
                    {
                        "role": "assistant",
                        "content": "# Important Additional Context\n- Write in first person.",
                    },
                ]
            if "OPTIMIZED_OVERALL_OUTLINE_GENERATION" in messages[-1]["content"]:
                return [
                    *messages,
                    {
                        "role": "assistant",
                        "content": "# Chapter 1\nPlot A\n# Chapter 2\nPlot B",
                    },
                ]
            if (
                "OUTLINE_REVISION_PROMPT" in messages[-1]["content"]
            ):  # Simulate revision
                return [
                    *messages,
                    {
                        "role": "assistant",
                        "content": "# Chapter 1\nPlot A revised\n# Chapter 2\nPlot B with more detail.",
                    },
                ]
            # Fallback for GetFeedback/GetRating if they use SafeGenerateText
            if "CRITIC_OUTLINE_PROMPT" in messages[-1]["content"]:
                return [
                    *messages,
                    {
                        "role": "assistant",
                        "content": MockLLMEditor.GetFeedbackOnOutline(
                            self, MockLoggerOutline(), "dummy outline"
                        ),
                    },
                ]
            if "OUTLINE_COMPLETE_PROMPT" in messages[-1]["content"]:
                is_complete = MockLLMEditor.GetOutlineRating(
                    self, MockLoggerOutline(), "dummy outline"
                )
                return [
                    *messages,
                    {
                        "role": "assistant",
                        "content": json.dumps({"IsComplete": is_complete}),
                    },
                ]
            return [
                *messages,
                {"role": "assistant", "content": "Default mock response."},
            ]

        def GetLastMessageText(self, messages: list):
            return messages[-1]["content"] if messages else ""

    mock_logger_outline = MockLoggerOutline()
    mock_interface_outline = MockInterfaceOutline(models=[], logger_instance=mock_logger_outline)  # type: ignore

    test_user_prompt = "A space opera about a lost kitten."

    print("\n--- Testing GenerateOutline ---")
    full_outline, elements, chapter_outline, base_ctx = GenerateOutline(mock_interface_outline, mock_logger_outline, test_user_prompt)  # type: ignore

    print("\n--- Results ---")
    print(f"Base Context:\n{base_ctx}")
    print(f"\nStory Elements:\n{elements}")
    print(f"\nFinal Chapter-Level Outline:\n{chapter_outline}")
    # print(f"\nPrintable Full Outline:\n{full_outline}") # This can be very long
