# /home/tlh/fiction-fabricator/stages/plot_development.py
from loguru import logger
import asyncio
import os
from utils import edit_text_with_editor
from embedding_manager import EmbeddingManager
from prompt_constructor import PromptConstructor
from plan import Plan
import re

async def create_plot_outline(agent, book_spec, loop, output_manager):
    """Creates the initial plot outline by querying the LLM.

    Args:
        agent (StoryAgent): The main story agent instance.
        book_spec (str): The book specification.
        loop (asyncio.AbstractEventLoop): The event loop.
        output_manager (OutputManager): An object to handle output and loading.

    Returns:
        tuple: A tuple containing the messages and the plan, or (None, []).
    """
    logger.info("Creating initial plot outline...")
    messages = agent.prompt_constructor.create_plot_chapters_messages(book_spec, agent.form)
    text_plan_string = await agent.query_chat(messages[1]['content'], messages[0]['content'], loop)

    if text_plan_string is None:
        logger.error("Failed to create plot chapters.")
        return None, []

    plan = Plan.parse_text_plan(text_plan_string)
    output_manager.save_output("plot_acts", Plan.plan_2_str(plan))
    agent.embedding_manager.add_embedding("plot_acts", Plan.plan_2_str(plan))
    logger.info("Plot outline created and saved.")
    return messages, plan


async def create_chapters(agent, book_spec, plan, loop, output_manager):
    """Creates the initial chapter descriptions for the three acts by querying the LLM.

    Args:
        agent (StoryAgent): The main story agent instance.
        book_spec (str): The book specification.
        plan (list): The initial plot plan.
        loop (asyncio.AbstractEventLoop): The event loop.
        output_manager (OutputManager): An object to handle output and loading.

    Returns:
        tuple: A tuple containing the messages and the plan, or (None, []).
    """
    logger.info("Creating initial chapter descriptions...")
    text_plan = Plan.plan_2_str(plan)
    all_messages = []
    enhanced_acts = []
    for act_num in range(len(plan)):
        messages = agent.prompt_constructor.enhance_plot_chapters_messages(act_num, text_plan, book_spec, agent.form)
        enhanced_act_raw = await agent.query_chat(messages[1]['content'], messages[0]['content'], loop)

        if enhanced_act_raw is None:
            logger.error(f"Failed to generate plot chapter for act {act_num}")
            all_messages.append(messages)
            enhanced_acts.append(None)
            continue
        try:
            act_dict = Plan.parse_act(enhanced_act_raw)
            if len(act_dict['chapters']) < 2:
                logger.warning(f"Failed to generate a usable act for act: {act_num}, skipping")
                enhanced_acts.append(None)
                continue
            else:
                enhanced_acts.append(act_dict)
            text_plan = Plan.plan_2_str(enhanced_acts)
            all_messages.append(messages)
        except Exception as e:
            logger.warning(f"Failed to parse act dict in enhance plot chapters response {e}")
            all_messages.append(messages)
            enhanced_acts.append(None)
            continue

    if any(act is None for act in enhanced_acts):
        logger.warning("One or more acts failed to enhance, returning incomplete plan")
        return all_messages, plan
    else:
        output_manager.save_output("plot_chapters", Plan.plan_2_str(enhanced_acts))
        agent.embedding_manager.add_embedding("plot_chapters", Plan.plan_2_str(enhanced_acts))
        logger.info("Chapter descriptions created and saved.")
        return all_messages, enhanced_acts

async def enhance_plot_outline(agent, book_spec, plan, loop, output_manager):
    """Enhances the plot outline by iteratively querying the LLM for each act.

    Args:
        agent (StoryAgent): The main story agent instance.
        book_spec (str): The book specification.
        plan (list): The initial plot plan.
        loop (asyncio.AbstractEventLoop): The event loop.
        output_manager (OutputManager): An object to handle output and loading.

    Returns:
        tuple: A tuple containing the messages and the enhanced plan, or (None, []).
    """
    logger.info("Enhancing plot outline...")
    text_plan = Plan.plan_2_str(plan)
    all_messages = []
    enhanced_acts = []
    for act_num in range(len(plan)):
        messages = agent.prompt_constructor.enhance_plot_chapters_messages(act_num, text_plan, book_spec, agent.form)
        enhanced_act_raw = await agent.query_chat(messages[1]['content'], messages[0]['content'], loop)

        if enhanced_act_raw is None:
            logger.error(f"Failed to enhance plot chapter for act {act_num}")
            all_messages.append(messages)
            enhanced_acts.append(None)
            continue

        try:
            act_dict = Plan.parse_act(enhanced_act_raw)
            if len(act_dict['chapters']) < 2:
                logger.warning(f"Failed to generate a usable act for act: {act_num}, skipping")
                enhanced_acts.append(None)
                continue
            else:
                enhanced_acts.append(act_dict)

            text_plan = Plan.plan_2_str(enhanced_acts) # Use the enhanced acts for the next iteration
            agent.embedding_manager.add_embedding(f"enhanced_act_{act_num}", text_plan)
            all_messages.append(messages)

        except Exception as e:
            logger.warning(f'Failed to parse act dict in enhance plot chapters response: {e}')
            all_messages.append(messages)
            enhanced_acts.append(None)
            continue

    if any(act is None for act in enhanced_acts):
        logger.warning("One or more acts failed to enhance, returning incomplete plan")
        return all_messages, plan
    else:
        # Allow user to edit the enhanced plot outline
        edited_plan_text = await edit_text_with_editor(Plan.plan_2_str(enhanced_acts), "Enhanced Plot Outline")
        if edited_plan_text is None:
            logger.warning("Enhanced plot outline editing cancelled.")
            return all_messages, plan  # Return original plan if editing is cancelled

        enhanced_acts = Plan.parse_text_plan(edited_plan_text)
        output_manager.save_output("enhanced_plot_chapters", Plan.plan_2_str(enhanced_acts))
        logger.info("Plot outline enhanced and saved.")
        return all_messages, enhanced_acts

async def split_into_scenes(agent, plan, loop, output_manager):
    """Splits chapters into scenes by querying the LLM.

    Args:
        agent (StoryAgent): The main story agent instance.
        plan (list): The plot plan.
        loop (asyncio.AbstractEventLoop): The event loop.
        output_manager (OutputManager): An object to handle output and loading.

    Returns:
        tuple: A tuple containing the messages and the plan with scenes, or (None, []).
    """
    logger.info("Splitting chapters into scenes...")
    all_messages = []
    act_chapters = {}
    updated_plan = []  # Create a new plan to avoid modifying the original during iteration
    for i, act_data in enumerate(plan, start=1):
        act = act_data.copy()  # Copy the act to avoid modifying the original
        updated_plan.append(act)
        text_act, chs = Plan.act_2_str(plan, i)
        act_chapters[i] = chs
        messages = agent.prompt_constructor.split_chapters_into_scenes_messages(i, text_act, agent.form)
        act_scenes_raw = await agent.query_chat(messages[1]['content'], messages[0]['content'], loop)

        if act_scenes_raw:
            # Allow user to edit the raw scene breakdown for the act
            edited_scenes_raw = await edit_text_with_editor(act_scenes_raw, f"Scene Breakdown for Act {i}")
            if edited_scenes_raw is None:
                logger.warning(f"Scene breakdown editing cancelled for Act {i}.")
                all_messages.append(messages)
                continue
            act['act_scenes'] = edited_scenes_raw
            all_messages.append(messages)
        else:
            logger.error(f'Failed to split scenes in act {i}')
            all_messages.append(messages)
            continue

    for i, act in enumerate(updated_plan, start=1):
        if not act.get('act_scenes'):
            logger.error(f"Act {i} has no scenes, cannot split chapters")
            continue
        act_scenes = act['act_scenes']
        act_scenes = re.split(r'Chapter (\d+)', act_scenes.strip())

        act['chapter_scenes'] = {}
        chapters = [text.strip() for text in act_scenes if (text and text.strip())]
        current_ch = None
        merged_chapters = {}
        for snippet in chapters:
            if snippet.isnumeric():
                ch_num = int(snippet)
                if ch_num != current_ch:
                    current_ch = snippet
                    merged_chapters[ch_num] = ''
                continue
            if merged_chapters:
                merged_chapters[ch_num] += snippet

        ch_nums = list(merged_chapters.keys()) if len(merged_chapters) <= len(act_chapters[i]) else act_chapters[i]
        merged_chapters = {ch_num: merged_chapters[ch_num] for ch_num in ch_nums}

        for ch_num, chapter in merged_chapters.items():
            scenes = re.split(r'Scene \d+.{0,10}?:', chapter)
            scenes = [text.strip() for text in scenes[1:] if (text and (len(text.split()) > 3))]
            if not scenes:
                continue
            act['chapter_scenes'][ch_num] = scenes

    output_manager.save_output("scenes_breakdown", Plan.plan_2_str(updated_plan))
    logger.info("Chapters split into scenes and saved.")
    return all_messages, updated_plan