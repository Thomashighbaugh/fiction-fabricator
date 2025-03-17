# core/content_generation/scene_outline_generation.py
from typing import Optional, List

import re

from core.plot_outline import ChapterOutline, SceneOutline
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger


async def generate_scene_outlines(
    content_generator, chapter_outline: ChapterOutline, num_scenes: int
) -> Optional[List[SceneOutline]]:
    """
    Generates scene outlines for a given chapter outline.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        generation_prompt_template = (
            prompt_manager.create_scene_outlines_generation_prompt()
        )  # Correct: Get template
        variables = {
            "chapter_outline": chapter_outline.summary,  # Remains a string.
            "num_scenes_per_chapter": str(num_scenes),
        }

        generation_prompt = generation_prompt_template(
            **variables
        )  # Correct: THEN call with variables

        generated_text = await ollama_client.generate_text(
            prompt=generation_prompt,
            model_name=content_generator.model_name,
        )

        if not generated_text:
            logger.error("Failed to generate scene outlines.")
            return None

        # --- Critique and Rewrite ---
        critique_prompt_template = (
            prompt_manager.create_scene_outlines_critique_prompt()
        )  # Correct
        rewrite_prompt_template = (
            prompt_manager.create_scene_outlines_rewrite_prompt()
        )  # Correct

        critique_variables = {"current_outlines": generated_text}
        critique_prompt = critique_prompt_template(**critique_variables)  # Correct
        critique = await ollama_client.generate_text(
            model_name=content_generator.model_name, prompt=critique_prompt
        )
        if critique:
            rewrite_variables = {
                "current_outlines": generated_text,
                "critique": critique,
            }
            rewrite_prompt = rewrite_prompt_template(**rewrite_variables)  # Correct
            generated_text = await ollama_client.generate_text(
                model_name=content_generator.model_name, prompt=rewrite_prompt
            )
            if not generated_text:
                logger.error("Failed to rewrite scene outlines after critique.")
                return None
        else:
            logger.warning("Critique failed; proceeding with original output.")

        scene_outlines: List[SceneOutline] = []
        scene_pattern = re.compile(
            r"Scene\s*(\d+):?\s*(.*?)(?=(?:\nScene|$))",
            re.DOTALL | re.IGNORECASE,
        )
        scene_matches = scene_pattern.finditer(generated_text)
        found_scenes = 0

        for match in scene_matches:
            scene_number = int(match.group(1))
            scene_summary = match.group(2).strip()
            if scene_summary:
                scene_outlines.append(
                    SceneOutline(scene_number=scene_number, summary=scene_summary)
                )
                found_scenes += 1
                logger.debug(
                    "Parsed scene %d-%d outline: %s...",
                    chapter_outline.chapter_number,
                    scene_number,
                    scene_summary[:50],
                )

            if found_scenes < num_scenes:
                logger.warning(
                    "Expected %d scenes, but only parsed %d for chapter %d. "
                    "Review LLM output for parsing errors.",
                    num_scenes,
                    found_scenes,
                    chapter_outline.chapter_number,
                )
            elif found_scenes > num_scenes:
                scene_outlines = scene_outlines[:num_scenes]
                logger.warning(
                    "LLM generated %d scenes, trimming to requested %d, for chapter %d.",
                    found_scenes,
                    num_scenes,
                    chapter_outline.chapter_number,
                )
        logger.debug(
            f"{len(scene_outlines)} scene outlines generated for chapter {chapter_outline.chapter_number} successfully."
        )

        return scene_outlines

    except (TypeError, ValueError, re.error) as e:
        logger.error("Error processing SceneOutline responses: %s", e)
        logger.debug("Raw LLM response: %s", generated_text)
        return None


async def enhance_scene_outlines(
    content_generator, current_outlines: List[SceneOutline]
) -> Optional[List[SceneOutline]]:
    """
    Asynchronously enhances existing scene outlines.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    outline_texts = [
        f"Scene {so.scene_number}:\n{so.summary}" for so in current_outlines
    ]
    critique_prompt_template = (
        prompt_manager.create_scene_outlines_critique_prompt()
    )  # Correct
    rewrite_prompt_template = (
        prompt_manager.create_scene_outlines_rewrite_prompt()
    )  # Correct

    current_outlines_text = "\n".join(outline_texts)
    variables = {
        "current_outlines": current_outlines_text,
    }
    critique_prompt_str = critique_prompt_template(**variables)  # Correct

    try:
        critique = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=critique_prompt_str,
        )

        if not critique:
            logger.error("Failed to generate critique for scene outlines.")
            return None

        rewrite_prompt_str = rewrite_prompt_template(  # Correct
            **variables,
            critique=critique,
            current_outlines=current_outlines_text,
        )
        enhanced_outlines_text = await ollama_client.generate_text(
            model_name=content_generator.model_name, prompt=rewrite_prompt_str
        )

        if enhanced_outlines_text:
            scene_outlines: List[SceneOutline] = []
            try:
                scene_pattern = re.compile(
                    r"Scene\s*(\d+):?\s*(.*?)(?=(?:\nScene|$))",
                    re.DOTALL | re.IGNORECASE,
                )
                scene_matches = scene_pattern.finditer(enhanced_outlines_text)

                for match in scene_matches:
                    scene_number = int(match.group(1))
                    scene_summary = match.group(2).strip()
                    scene_outlines.append(
                        SceneOutline(scene_number=scene_number, summary=scene_summary)
                    )
                logger.info("Scene outlines enhanced successfully.")
                return scene_outlines
            except (TypeError, ValueError) as e:
                logger.error("Error processing SceneOutline responses: %s", e)
                logger.debug("Raw LLM response: %s", enhanced_outlines_text)
                return None
        else:
            logger.error("Failed to rewrite scene outlines.")
            return None

    except Exception as e:
        logger.error(f"Error enhancing scene outlines: {e}")
        return None
