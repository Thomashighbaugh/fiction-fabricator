#!/usr/bin/python3

import Writer.Config
import Writer.SummarizationUtils
import Writer.Scene.ChapterOutlineToScenes
import Writer.Scene.ScenesToJSON
import Writer.Scene.SceneOutlineToScene
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext, ChapterContext, SceneContext
from Writer.PrintUtils import Logger
from Writer.Scene.SceneFileManager import SceneFileManager


def ChapterByScene(
    Interface: Interface,
    _Logger: Logger,
    chapter_context: ChapterContext, # Now receives the chapter context object
    narrative_context: NarrativeContext,
    selected_model: str,
    file_manager: SceneFileManager = None,
) -> str:
    """
    Calls all other scene-by-scene generation functions and creates a full chapter
    based on the new scene pipeline. Now saves individual scene files for error resilience.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        chapter_context: The context object for the chapter to be written.
        narrative_context: The overall context object for the novel.
        file_manager: Optional SceneFileManager for saving individual files.

    Returns:
        The fully generated chapter text, assembled from its scenes.
    """
    _Logger.Log(f"Starting Scene-By-Scene Chapter Generation Pipeline for Chapter {chapter_context.chapter_number}", 2)

    # Step 1: Get the detailed, scene-by-scene markdown outline for this chapter
    scene_by_scene_outline_md = Writer.Scene.ChapterOutlineToScenes.ChapterOutlineToScenes(
        Interface,
        _Logger,
        chapter_context.initial_outline,
        narrative_context,
        chapter_context.chapter_number,
        selected_model,
    )

    # Step 2: Convert the markdown outline into a structured JSON list of scene outlines
    scene_json_list = Writer.Scene.ScenesToJSON.ScenesToJSON(
        Interface, _Logger, scene_by_scene_outline_md, selected_model
    )

    if not scene_json_list:
        _Logger.Log(f"Failed to generate or parse scene list for Chapter {chapter_context.chapter_number}. Aborting scene pipeline for this chapter.", 7)
        return f"// ERROR: Scene generation failed for Chapter {chapter_context.chapter_number}. Could not break the chapter into scenes. //"


    # Step 3: Iterate through each scene, write it, summarize it, and build the chapter
    rough_chapter_text: str = ""
    for i, scene_outline in enumerate(scene_json_list):
        scene_num = i + 1
        _Logger.Log(f"--- Processing Chapter {chapter_context.chapter_number}, Scene {scene_num} ---", 3)

        # A. Create a context object for the current scene. This object will be mutated by the generation function.
        current_scene_context = SceneContext(scene_number=scene_num, initial_outline=scene_outline)
        
        # B. Generate the full text for the scene using the iterative, piece-by-piece method.
        # This function will populate the current_scene_context with its generated pieces.
        Writer.Scene.SceneOutlineToScene.SceneOutlineToScene(
            Interface,
            _Logger,
            current_scene_context,
            narrative_context,
            chapter_context.chapter_number,
            scene_num,
            selected_model,
        )
        
        # C. Save the individual scene file immediately for error resilience
        if file_manager:
            scene_word_count = len(current_scene_context.generated_content.split())
            scene_file_path = file_manager.save_scene_file(
                current_scene_context, 
                chapter_context.chapter_number, 
                scene_word_count
            )
            if scene_file_path:
                _Logger.Log(f"Saved scene file: {scene_file_path}", 3)
        
        # D. Append the fully assembled scene text to the chapter
        scene_text = current_scene_context.generated_content
        rough_chapter_text += scene_text + "\n\n"

        # E. Generate a final, holistic summary for the completed scene and extract key points for coherence
        final_summary_data = Writer.SummarizationUtils.summarize_scene_and_extract_key_points(
            Interface,
            _Logger,
            scene_text,
            narrative_context,
            chapter_context.chapter_number,
            scene_num,
        )
        current_scene_context.set_final_summary(final_summary_data.get("summary"))
        for point in final_summary_data.get("key_points_for_next_scene", []):
            current_scene_context.add_key_point(point)
        
        _Logger.Log(f"Scene {scene_num} Final Summary: {current_scene_context.final_summary}", 1)
        _Logger.Log(f"Scene {scene_num} Key Points for Next Scene: {current_scene_context.key_points_for_next_scene}", 1)

        # F. Add the completed scene context (now full of pieces and a final summary) to the chapter context
        chapter_context.add_scene(current_scene_context)
        _Logger.Log(f"--- Finished processing Scene {scene_num} ---", 3)


    _Logger.Log(f"Finished Scene-By-Scene Chapter Generation Pipeline for Chapter {chapter_context.chapter_number}", 2)

    return rough_chapter_text.strip()
