# /home/tlh/fiction-fabricator/stages/scene_generation.py
from loguru import logger
import asyncio
import os
from utils import edit_text_with_editor
from embedding_manager import EmbeddingManager
from prompt_constructor import PromptConstructor
from plan import Plan
import utils

async def generate_scene(agent, scene_spec, scene_number, chapter_number, plan, previous_scene, loop, output_manager):
    """Generates content for a scene by querying the LLM.

    Args:
        agent (StoryAgent): The main story agent instance.
        scene_spec (str): The specification for the scene.
        scene_number (int): The scene number.
        chapter_number (int): The chapter number.
        plan (list): The plot plan.
        previous_scene (str, optional): The content of the previous scene.
        loop (asyncio.AbstractEventLoop): The event loop.
        output_manager (OutputManager): An object to handle output and loading.

    Returns:
        tuple: A tuple containing the messages and the generated scene content, or (None, "").
    """
    logger.info(f"Generating Scene {scene_number} in Chapter {chapter_number}...")
    messages, generated_scene = await agent._write_scene_content(
        scene_spec, scene_number, chapter_number, plan, previous_scene, loop
    )

    if generated_scene:
        # Allow user to edit the generated scene
        edited_scene = await edit_text_with_editor(generated_scene, f"Scene {scene_number}, Chapter {chapter_number}")
        if edited_scene is not None:
            generated_scene = edited_scene
            output_manager.save_output(f"chapter_{chapter_number}_scene_{scene_number}", generated_scene)
            agent.embedding_manager.add_embedding(f"scene_{scene_number}_chapter_{chapter_number}", generated_scene)
            agent.world_model.add_previous_scene(generated_scene)
            logger.info(f"Scene {scene_number} in Chapter {chapter_number} generated and saved.")
        else:
            logger.warning(f"Scene {scene_number} in Chapter {chapter_number} generation incomplete due to editing cancellation.")

    return messages, generated_scene

async def continue_scene(agent, scene_spec, scene_number, chapter_number, plan, current_scene, loop, output_manager):
    """Continues writing content for an existing scene by querying the LLM.

    Args:
        agent (StoryAgent): The main story agent instance.
        scene_spec (str): The specification for the scene.
        scene_number (int): The scene number.
        chapter_number (int): The chapter number.
        plan (list): The plot plan.
        current_scene (str): The current content of the scene.
        loop (asyncio.AbstractEventLoop): The event loop.
        output_manager (OutputManager): An object to handle output and loading.

    Returns:
        tuple: A tuple containing the messages and the continued scene content, or (None, "").
    """
    logger.info(f"Continuing Scene {scene_number} in Chapter {chapter_number}...")
    messages, continued_scene = await agent._continue_scene_content(
        scene_spec, scene_number, chapter_number, plan, current_scene, loop
    )

    if continued_scene:
        # Allow user to edit the continued scene
        edited_scene = await edit_text_with_editor(continued_scene, f"Continuing Scene {scene_number}, Chapter {chapter_number}")
        if edited_scene is not None:
            continued_scene = edited_scene
            output_manager.save_output(f"chapter_{chapter_number}_scene_{scene_number}", continued_scene)
            agent.embedding_manager.add_embedding(f"enhanced_scene_{scene_number}_chapter_{chapter_number}", continued_scene)
            agent.world_model.add_previous_scene(continued_scene)
            logger.info(f"Scene {scene_number} in Chapter {chapter_number} continued and saved.")
        else:
            logger.warning(f"Scene {scene_number} in Chapter {chapter_number} continuation incomplete due to editing cancellation.")

    return messages, continued_scene