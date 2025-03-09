# core/content_generation/plot_outline_generation.py
from typing import Optional
import tomli_w  # Import tomli_w
import tomli
from core.book_spec import BookSpec
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger
from .content_generation_utils import PlotOutline  # Import PlotOutline model


async def generate_plot_outline(content_generator, book_spec: BookSpec) -> Optional[PlotOutline]:
    """
    Generates a PlotOutline object based on a BookSpec.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        generation_prompt_template = prompt_manager.create_plot_outline_generation_prompt()
        logger.debug("generate_plot_outline - Generation prompt template loaded.")

        variables = {
            "book_spec_toml": tomli_w.dumps(book_spec.model_dump()),  # Convert to TOML
        }
        full_prompt = generation_prompt_template.format(**variables)
        logger.debug("generate_plot_outline - Generation prompt formatted.")
        logger.debug(
            f"generate_plot_outline - Full generation prompt: %s", full_prompt
        )

        logger.debug("generate_plot_outline - Sending prompt to OllamaClient...")
        generated_text = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=full_prompt,
        )

        if not generated_text:
            logger.error("Failed to generate plot outline.")
            return None

        logger.debug(f"Raw LLM Plot Outline Response: {generated_text}")

        # --- TOML Validation and Correction ---
        expected_schema = """
        [act_one]
        block_one = ["string", "string"]
        block_two = ["string", "string"]
        block_three = ["string", "string"]

        [act_two]
        block_one = ["string", "string"]
        block_two = ["string", "string"]
        block_three = ["string", "string"]

        [act_three]
        block_one = ["string", "string"]
        block_two = ["string", "string"]
        block_three = ["string", "string"]
        """
        validated_text = await content_generator._validate_and_correct_toml(
            generated_text, expected_schema
        )
        if not validated_text:
          logger.error("TOML Validation Failed")
          return None
        generated_text = validated_text
        # --- End TOML Validation ---
        try:
            logger.debug("generate_plot_outline - Attempting to parse PlotOutline.")
            plot_outline_dict = tomli.loads(generated_text) # Use tomli
            plot_outline = PlotOutline(
                act_one_block_one=plot_outline_dict.get('act_one',{}).get('block_one',[]),
                act_one_block_two=plot_outline_dict.get('act_one',{}).get('block_two',[]),
                act_one_block_three=plot_outline_dict.get('act_one',{}).get('block_three',[]),
                act_two_block_one=plot_outline_dict.get('act_two',{}).get('block_one',[]),
                act_two_block_two=plot_outline_dict.get('act_two',{}).get('block_two',[]),
                act_two_block_three=plot_outline_dict.get('act_two',{}).get('block_three',[]),
                act_three_block_one=plot_outline_dict.get('act_three',{}).get('block_one',[]),
                act_three_block_two=plot_outline_dict.get('act_three',{}).get('block_two',[]),
                act_three_block_three=plot_outline_dict.get('act_three', {}).get('block_three',[])
            )
            logger.debug("generate_plot_outline - PlotOutline parsing successful.")
            logger.info("Plot outline generated successfully.")
            return plot_outline
        except (TypeError, ValueError, tomli.TOMLDecodeError) as e:
            logger.error(f"Error processing PlotOutline response: {e}")
            logger.debug("Raw LLM response: %s", generated_text)
            return None
    except Exception as e:
        logger.exception("generate_plot_outline - Exception occurred: {e}")
        return None


async def enhance_plot_outline(
    content_generator, current_outline: PlotOutline
) -> Optional[PlotOutline]:  # Modified Return Type
    """
    Asynchronously enhances an existing plot outline.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        critique_prompt_template = prompt_manager.create_plot_outline_critique_prompt()
        rewrite_prompt_template = prompt_manager.create_plot_outline_rewrite_prompt()

        # Use TOML string input
        variables = {"current_outline_toml": tomli_w.dumps(current_outline.model_dump())} # toml
        critique_prompt_str = critique_prompt_template.format(**variables)

        critique = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=critique_prompt_str,
        )

        if not critique:
            logger.error("Failed to generate critique for plot outline.")
            return None

        rewrite_prompt_str = rewrite_prompt_template.format(
            current_outline_toml=variables["current_outline_toml"], critique=critique
        )  # Use TOML string
        enhanced_outline_toml = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=rewrite_prompt_str,
        )
        if not enhanced_outline_toml:
            logger.error("Failed to generate enhanced plot outline")
            return None

        # --- TOML Validation and Correction ---
        expected_schema = """
        [act_one]
        block_one = ["string", "string"]
        block_two = ["string", "string"]
        block_three = ["string", "string"]

        [act_two]
        block_one = ["string", "string"]
        block_two = ["string", "string"]
        block_three = ["string", "string"]

        [act_three]
        block_one = ["string", "string"]
        block_two = ["string", "string"]
        block_three = ["string", "string"]
        """
        validated_text = await content_generator._validate_and_correct_toml(
            enhanced_outline_toml, expected_schema
        )
        if not validated_text:
            logger.error("TOML Validation Failed")
            return None
        enhanced_outline_toml = validated_text
        # --- End TOML Validation ---

        try:
            enhanced_outline_dict = tomli.loads(enhanced_outline_toml)  # Use tomli
            enhanced_outline = PlotOutline(
                act_one_block_one=enhanced_outline_dict.get('act_one',{}).get('block_one',[]),
                act_one_block_two=enhanced_outline_dict.get('act_one',{}).get('block_two',[]),
                act_one_block_three=enhanced_outline_dict.get('act_one',{}).get('block_three',[]),
                act_two_block_one=enhanced_outline_dict.get('act_two',{}).get('block_one',[]),
                act_two_block_two=enhanced_outline_dict.get('act_two',{}).get('block_two',[]),
                act_two_block_three=enhanced_outline_dict.get('act_two',{}).get('block_three',[]),
                act_three_block_one=enhanced_outline_dict.get('act_three',{}).get('block_one',[]),
                act_three_block_two=enhanced_outline_dict.get('act_three',{}).get('block_two',[]),
                act_three_block_three=enhanced_outline_dict.get('act_three', {}).get('block_three',[])
            )

            logger.info("Plot outline enhanced successfully.")
            return enhanced_outline
        except (TypeError, ValueError, tomli.TOMLDecodeError) as e:
            logger.error(f"Error processing enhanced PlotOutline response: {e}")
            logger.debug("Raw LLM response: %s", enhanced_outline_toml)
            return None

    except Exception as e:
        logger.exception("Exception occurred during plot outline enhancement.")
        return Nones