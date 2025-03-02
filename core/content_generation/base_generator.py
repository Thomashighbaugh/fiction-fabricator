# /home/tlh/refactored_gui_fict_fab/core/content_generation/base_generator.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import json
import aiohttp

from llm.llm_client import OpenAILLMClient  # Changed to OpenAILLMClient
from utils.logger import logger


class BaseContentGenerator(ABC):
    """
    Abstract base class for content generators.
    """

    def __init__(self, prompt_manager, model_name: str):
        logger.debug("BaseContentGenerator.__init__ START")
        self.prompt_manager = prompt_manager
        self.model_name = model_name
        self.openai_client = OpenAILLMClient()  # Changed to OpenAILLMClient
        logger.debug("BaseContentGenerator.__init__ END")

    @abstractmethod
    async def generate(self, *args: Any, **kwargs: Any) -> Optional[Any]:
        """
        Abstract method for generating content. Must be implemented by subclasses.
        """

    @abstractmethod
    async def enhance(self, current_content: Any) -> Optional[Any]:
        """
        Abstract method for enhancing existing content. Must be implemented by subclasses.
        """

    async def _generate_content_from_prompt(
        self, prompt_template: str, variables: Dict[str, str]
    ) -> Optional[str]:
        """
        Handles content generation from a prompt template using Ollama with lazy logging and specific exception handling.
        """
        try:
            logger.debug(f"Prompt Template before formatting: {prompt_template}")
            logger.debug(f"Variables for prompt formatting: {variables}")

            # Use simple string replacement instead of .format
            prompt = prompt_template.replace(
                "{" + "idea" + "}", variables.get("idea", "")
            )
            prompt = prompt.replace(
                "{" + "project_name" + "}", variables.get("project_name", "")
            )
            if "book_spec_json" in variables:
                prompt = prompt.replace(
                    "{" + "book_spec_json" + "}", variables.get("book_spec_json", "")
                )
            if "plot_outline" in variables:
                prompt = prompt.replace(
                    "{" + "plot_outline" + "}", variables.get("plot_outline", "")
                )
            if "current_outline" in variables:
                prompt = prompt.replace(
                    "{" + "current_outline" + "}", variables.get("current_outline", "")
                )
            if "critique" in variables:
                prompt = prompt.replace(
                    "{" + "critique" + "}", variables.get("critique", "")
                )
            if "chapter_outlines" in variables:
                prompt = prompt.replace(
                    "{" + "chapter_outlines" + "}",
                    variables.get("chapter_outlines", ""),
                )
            if "current_outlines" in variables:
                prompt = prompt.replace(
                    "{" + "current_outlines" + "}",
                    variables.get("current_outlines", ""),
                )
            if "scene_outlines" in variables:
                prompt = prompt.replace(
                    "{" + "scene_outlines" + "}", variables.get("scene_outlines", "")
                )
            if "scene_outline" in variables:
                prompt = prompt.replace(
                    "{" + "scene_outline" + "}", variables.get("scene_outline", "")
                )
            if "scene_outline_full" in variables:
                prompt = prompt.replace(
                    "{" + "scene_outline_full" + "}",
                    variables.get("scene_outline_full", ""),
                )
            if "part_number" in variables:
                prompt = prompt.replace(
                    "{" + "part_number" + "}", variables.get("part_number", "")
                )
            if "book_spec_text" in variables:
                prompt = prompt.replace(
                    "{" + "book_spec_text" + "}", variables.get("book_spec_text", "")
                )
            if "chapter_outline" in variables:
                prompt = prompt.replace(
                    "{" + "chapter_outline" + "}", variables.get("chapter_outline", "")
                )
            if "content" in variables:
                prompt = prompt.replace(
                    "{" + "content" + "}", variables.get("content", "")
                )
            if "structure_problems" in variables:
                prompt = prompt.replace(
                    "{" + "structure_problems" + "}",
                    variables.get("structure_problems", ""),
                )
            if "content_with_structure_problems" in variables:
                prompt = prompt.replace(
                    "{" + "content_with_structure_problems" + "}",
                    variables.get("content_with_structure_problems", ""),
                )
            if "json_structure" in variables:
                prompt = prompt.replace(
                    "{" + "json_structure" + "}", variables.get("json_structure", "")
                )
            if "num_chapters" in variables:
                prompt = prompt.replace(
                    "{" + "num_chapters" + "}", variables.get("num_chapters", "")
                )
            if "num_scenes_per_chapter" in variables:
                prompt = prompt.replace(
                    "{" + "num_scenes_per_chapter" + "}",
                    variables.get("num_scenes_per_chapter", ""),
                )

            logger.debug("Generated Prompt: %s...", prompt[:150])  # Lazy formatting
            generated_text = await self.openai_client.generate_text(
                model_name=self.model_name, prompt=prompt
            )  # Changed to openai_client
            if generated_text:
                return generated_text
            else:
                logger.error("LLM text generation failed or returned empty response.")
                return None

        except KeyError as e:  # Catch specific KeyError for prompt formatting issues
            logger.error(
                "Error formatting prompt due to missing variable: %s", e
            )  # Lazy formatting
            return None
        except (
            aiohttp.ClientError
        ) as e:  # Catch specific aiohttp ClientError for network/API issues
            logger.error("Error during OpenAI API call: %s", e)  # Changed error message
            return None
        except (
            json.JSONDecodeError
        ) as e:  # Catch specific JSONDecodeError for invalid JSON
            logger.error(
                "OpenAI response JSON decoding error: %s", e
            )  # Changed error message
            return None
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as e:  # Catch specific operational errors
            logger.error(
                "Operational error during content generation: %s", e
            )  # Lazy formatting
            logger.exception(e)  # Log full exception details
            return None

    @abstractmethod
    def _parse_response(self, response_text: str) -> Any:
        """
        Abstract method to parse the LLM response. Must be implemented by subclasses.
        """

    async def _structure_check_and_fix(
        self,
        content: str,
        structure_check_prompt_template: str,
        structure_fix_prompt_template: str,
    ) -> Optional[str]:
        """
        Implements structure checking and fixing logic using LLM prompts.
        """
        structure_check_variables = {"content": content}
        structure_check_prompt = structure_check_prompt_template
        for key, value in structure_check_variables.items():
            structure_check_prompt = structure_check_prompt.replace(f"{{{key}}}", value)

        structure_check_result = await self._generate_content_from_prompt(
            structure_check_prompt,
            structure_check_variables,  # Pass variables for structure check
        )

        if structure_check_result != "STRUCTURE_OK":
            logger.warning("Content structure check failed. Attempting to fix...")
            structure_fix_variables = {
                "content_with_structure_problems": content,
                "structure_problems": structure_check_result,
                "json_structure": "{}",  # Provide empty json_structure as it might be needed in the fix prompt, though not strictly used in templates provided.
            }
            structure_fix_prompt = structure_fix_prompt_template
            for key, value in structure_fix_variables.items():
                structure_fix_prompt = structure_fix_prompt.replace(f"{{{key}}}", value)

            fixed_text = await self._generate_content_from_prompt(
                structure_fix_prompt,
                structure_fix_variables,  # Pass variables for structure fix
            )
            if fixed_text:
                logger.info("Content structure fixed successfully.")
                return fixed_text
            else:
                logger.error("Failed to fix content structure.")
                return None
        else:
            logger.info("Content structure check OK.")
            return content
