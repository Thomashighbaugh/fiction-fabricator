# /home/tlh/fiction-fabricator/stages/book_specification.py
from loguru import logger
import asyncio
import os
from utils import edit_text_with_editor
from embedding_manager import EmbeddingManager
from prompt_constructor import PromptConstructor

async def initialize_book_specification(agent, topic, loop, output_manager):
    """Initializes the book specification by querying the LLM.

    Args:
        agent (StoryAgent): The main story agent instance.
        topic (str): The topic of the story.
        loop (asyncio.AbstractEventLoop): The event loop.
        output_manager: An object to handle output and loading.

    Returns:
        tuple: A tuple containing the messages and the text specification, or (None, "").
    """
    logger.info("Initializing book specification...")
    messages = agent.prompt_constructor.init_book_spec_messages(topic, agent.form)
    response = await agent.query_chat(messages[1]['content'], messages[0]['content'], loop)

    if response is None:
        logger.error("Failed to initialize book specification")
        return None, ""

    title = await agent.generate_title(topic, loop)
    spec_dict = agent._parse_book_spec(response)
    text_spec = f"Title: {title}\n" + "\n".join(f"{key}: {value}" for key, value in spec_dict.items())

    agent.world_model.init_world_model_from_spec(spec_dict)
    output_manager.save_output("book_specification", text_spec)
    agent.embedding_manager.add_embedding("book_spec", text_spec)
    logger.info("Book specification initialized and saved.")
    return messages, text_spec

async def enhance_book_specification(agent, book_spec, loop, output_manager):
    """Enhances the book specification by querying the LLM.

    Args:
        agent (StoryAgent): The main story agent instance.
        book_spec (str): The initial book specification.
        loop (asyncio.AbstractEventLoop): The event loop.
        output_manager: An object to handle output and loading.

    Returns:
        tuple: A tuple containing the messages and the enhanced specification, or (None, "").
    """
    logger.info("Enhancing book specification...")
    messages = agent.prompt_constructor.enhance_book_spec_messages(book_spec, agent.form)
    enhanced_spec_raw = await agent.query_chat(messages[1]['content'], messages[0]['content'], loop)

    if enhanced_spec_raw is None:
        logger.error("Failed to enhance book specification.")
        return None, ""

    enhanced_spec = f"Title: {book_spec.splitlines()[0].split(': ')[1]}\n" + enhanced_spec_raw

    output_manager.save_output("enhanced_book_spec", enhanced_spec)
    agent.embedding_manager.add_embedding("enhanced_book_spec", enhanced_spec)
    logger.info("Book specification enhanced and saved.")
    return messages, enhanced_spec