# File: Writer/Scene/SceneOutliner.py
# Purpose: Generates a detailed, structured list of scene outlines for a given chapter.

"""
Scene Outliner Module.

This module takes a high-level plot outline for a specific chapter and
expands it into a detailed, structured list of scene outlines. Each scene
outline serves as a blueprint for the `SceneGenerator` module to write the
full narrative text for that scene.

The process involves:
- Formatting a request to an LLM using an optimized prompt.
- Sending the request and receiving the LLM's response.
- Parsing the response (expected to be JSON or structured markdown) into
  a list of scene outline objects/dictionaries using `SceneParser`.
"""
import json
import Writer.Config as Config
import Writer.Prompts as Prompts
import Writer.Scene.SceneParser as SceneParser # For parsing the LLM response
from Writer.Interface.Wrapper import Interface # LLM interaction
from Writer.PrintUtils import Logger # Logging
from typing import List, Dict, Any, Optional


def generate_detailed_scene_outlines(
    interface: Interface, 
    logger: Logger, 
    chapter_plot_outline: str, 
    overall_story_outline: str, 
    chapter_number: int, 
    previous_chapter_context_summary: Optional[str],
    base_story_context: Optional[str] # Added for more holistic context if needed by prompt
) -> List[Dict[str, Any]]:
    """
    Generates a list of detailed scene outlines for a given chapter's plot outline.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        chapter_plot_outline (str): The specific plot outline for the current chapter.
        overall_story_outline (str): The main outline of the entire story for broader context.
        chapter_number (int): The current chapter number.
        previous_chapter_context_summary (Optional[str]): A summary of key elements from
                                                          the end of the previous chapter.
                                                          Can be None for the first chapter.
        base_story_context (Optional[str]): Overarching story context or user instructions.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents
                              a detailed scene outline. Returns an empty list if
                              generation or parsing fails.
    """
    logger.Log(f"Initiating detailed scene outlining for Chapter {chapter_number}...", 3)

    if not chapter_plot_outline or not chapter_plot_outline.strip():
        logger.Log(f"Chapter {chapter_number} plot outline is empty. Cannot generate scene outlines.", 6)
        return []

    try:
        prompt_template = Prompts.OPTIMIZED_CHAPTER_TO_SCENES_BREAKDOWN
        # Ensure all required placeholders are present in the prompt template
        # The prompt expects SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER to be formatted in.
        formatted_prompt = prompt_template.format(
            _ChapterPlotOutline=chapter_plot_outline,
            _OverallStoryOutline=overall_story_outline,
            _PreviousChapterContextSummary=previous_chapter_context_summary if previous_chapter_context_summary else "This is the first chapter; no specific summary from a preceding chapter is available. Rely on the overall story outline and this chapter's plot.",
            _ChapterNumber=chapter_number,
            _BaseStoryContext=base_story_context if base_story_context else "No additional base story context provided.",
            SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER=Config.SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER # Pass from Config
        )
    except KeyError as e:
        logger.Log(f"Formatting error in OPTIMIZED_CHAPTER_TO_SCENES_BREAKDOWN prompt for Chapter {chapter_number}: Missing key {e}", 7)
        return []
    except Exception as e:
        logger.Log(f"Unexpected error formatting scene outliner prompt for Chapter {chapter_number}: {e}", 7)
        return []

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(Prompts.DEFAULT_SYSTEM_PROMPT), # Use the expert creative writing assistant persona
        interface.build_user_query(formatted_prompt)
    ]
    
    try:
        # MODEL_SCENE_OUTLINER should be capable of generating structured JSON or easily parsable markdown.
        # The min_word_count should be enough for multiple scene descriptions.
        # For example, if min 3 scenes and each scene description is ~50-100 words, then 150-300 words.
        estimated_min_words_for_scene_outlines = 75 * Config.SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER
        
        logger.Log(
            f"Requesting LLM to generate detailed scene outlines for Chapter {chapter_number} from its plot.",
            4,
        )
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.MODEL_SCENE_OUTLINER,
            min_word_count=estimated_min_words_for_scene_outlines 
        )
        
        raw_llm_scene_outlines_text: str = interface.get_last_message_text(response_messages)

        if not raw_llm_scene_outlines_text or "Error:" in raw_llm_scene_outlines_text:
            logger.Log(f"LLM failed to generate scene outlines for Chapter {chapter_number} or returned an error: {raw_llm_scene_outlines_text[:100]}...", 6)
            return []
            
        # Parse the LLM's response into a list of structured scene outlines
        # Pass the interface and a suitable correction model to SceneParser
        detailed_scene_outlines_list = SceneParser.parse_llm_scene_outlines_response(
            interface, 
            logger, 
            raw_llm_scene_outlines_text,
            Config.EVAL_MODEL # Use EVAL_MODEL for JSON correction by default
        )
        
        if not detailed_scene_outlines_list:
            logger.Log(f"Failed to parse detailed scene outlines for Chapter {chapter_number} from LLM response. Response snippet: {raw_llm_scene_outlines_text[:200]}", 6)
            return []

        if len(detailed_scene_outlines_list) < Config.SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER:
            logger.Log(f"Warning: Generated only {len(detailed_scene_outlines_list)} scenes for Chapter {chapter_number}, less than minimum {Config.SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER}.", 6)


        logger.Log(f"Successfully generated and parsed {len(detailed_scene_outlines_list)} scene outlines for Chapter {chapter_number}.", 4)
        return detailed_scene_outlines_list

    except Exception as e:
        logger.Log(f"An unexpected error occurred during detailed scene outlining for Chapter {chapter_number}: {e}", 7)
        # import traceback; logger.Log(traceback.format_exc(), 7) # For more detailed error
        return []

# Example usage (typically called from ChapterGenerator.py)
if __name__ == "__main__":
    # This is for testing purposes only.
    class MockLogger:
        def Log(self, item: str, level: int, stream: bool = False): print(f"LOG L{level}: {item}")
        def save_langchain_interaction(self, label: str, messages: list): print(f"LANGCHAIN_SAVE: {label}")

    class MockInterface:
        def build_system_query(self, q: str): return {"role": "system", "content": q}
        def build_user_query(self, q: str): return {"role": "user", "content": q}
        def get_last_message_text(self, msgs): return msgs[-1]["content"] if msgs else ""
        
        # For SceneOutliner, safe_generate_text is called first
        def safe_generate_text(self, l, m, mo, min_word_count):
            print(f"Mock LLM Call (safe_generate_text) to {mo} with min_words {min_word_count} for scene outlining.")
            # Simulate LLM returning a JSON string of scene outlines
            mock_scene_data = [
                {"scene_number_in_chapter": 1, "scene_title": "The Old Library", "setting_description": "Dusty, ancient, filled with forgotten lore.", "key_events_actions": ["Protagonist finds a clue."], "pacing_note": "Slow, investigative"},
                {"scene_number_in_chapter": 2, "scene_title": "Ambush in the Alley", "setting_description": "Narrow, rain-slicked, midnight.", "key_events_actions": ["Protagonist is attacked."], "pacing_note": "Fast-paced action"}
            ]
            return [*m, {"role": "assistant", "content": json.dumps(mock_scene_data, indent=2)}]
        
        # SceneParser.parse_llm_scene_outlines_response might call safe_generate_json for correction
        # This mock should be part of the interface if used by the parser for correction
        def safe_generate_json(self, l, m, mo, required_attribs):
            print(f"Mock LLM Call (safe_generate_json - CORRECTION) to {mo}.")
            # This would be called if the initial text from safe_generate_text was bad JSON
            # For this test, assume safe_generate_text provides good JSON, so this won't be hit by SceneParser directly.
            # If it *were* hit, it should return a corrected JSON string as content.
            corrected_data = [{"scene_title": "Corrected Fallback Scene"}]
            return ([*m, {"role": "assistant", "content": json.dumps(corrected_data)}], corrected_data)


    mock_logger = MockLogger()
    mock_interface = MockInterface()
    
    # Setup necessary Config values for the test
    Config.MODEL_SCENE_OUTLINER = "mock_scene_outliner_model"
    Config.EVAL_MODEL = "mock_json_correction_model_for_parser" # For SceneParser's correction attempts
    Config.SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER = 2
    Prompts.DEFAULT_SYSTEM_PROMPT = "You are a scene outliner bot for testing."
    # Simplified prompt for testing the format call
    Prompts.OPTIMIZED_CHAPTER_TO_SCENES_BREAKDOWN = "Chapter: {_ChapterPlotOutline}, Overall: {_OverallStoryOutline}, Prev: {_PreviousChapterContextSummary}, Num: {_ChapterNumber}, Base: {_BaseStoryContext}, MinScenes: {SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER}"


    print("--- Testing generate_detailed_scene_outlines ---")
    chapter_plot = "The hero must infiltrate the villain's fortress to retrieve the stolen artifact."
    overall_story = "A classic tale of good vs. evil. The hero is brave, the villain is cunning."
    prev_chap_summary = "The hero learned the artifact was stolen and vowed to get it back."
    base_ctx = "The story is set in a medieval fantasy world."
    
    scene_outlines = generate_detailed_scene_outlines(
        mock_interface, 
        mock_logger, 
        chapter_plot, 
        overall_story, 
        chapter_number=3, 
        previous_chapter_context_summary=prev_chap_summary,
        base_story_context=base_ctx
    )
    
    print(f"\nGenerated Scene Outlines (Count: {len(scene_outlines)}):")
    for i, scene_outline in enumerate(scene_outlines):
        print(f"  Scene {i+1}: {scene_outline.get('scene_title', 'N/A')}")
        # print(f"    Details: {json.dumps(scene_outline, indent=2)}") # For full detail
    
    assert len(scene_outlines) == 2
    assert scene_outlines[0]["scene_title"] == "The Old Library"

    print("\n--- Test with empty chapter plot outline ---")
    empty_plot_scenes = generate_detailed_scene_outlines(
        mock_interface, 
        mock_logger, 
        "", 
        overall_story, 
        chapter_number=4, 
        previous_chapter_context_summary=prev_chap_summary,
        base_story_context=base_ctx
    )
    print(f"Generated Scene Outlines for empty plot (Count: {len(empty_plot_scenes)}): {empty_plot_scenes}")
    assert empty_plot_scenes == []