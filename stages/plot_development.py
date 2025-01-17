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
    # The plan generated by `create_plot_outline` should have exactly 3 acts.
    if len(plan) != 3:
        logger.error(f"Created plot outline does not have 3 acts. Instead, it has {len(plan)} acts.")
        return None, []

    output_manager.save_output("plot_acts", Plan.plan_2_str(plan))
    agent.embedding_manager.add_embedding("plot_acts", Plan.plan_2_str(plan))
    logger.info("Plot outline created and saved.")
    return messages, plan

async def create_chapters(agent, book_spec, plan, loop, output_manager, num_chapters):
    """
    Creates the initial chapter descriptions for the three acts by querying the LLM.

    Args:
        agent (StoryAgent): The main story agent instance.
        book_spec (str): The book specification.
        plan (list): The initial plot plan.
        loop (asyncio.AbstractEventLoop): The event loop.
        output_manager (OutputManager): An object to handle output and loading.
        num_chapters (int): The total number of chapters to create.

    Returns:
        tuple: A tuple containing the messages and the plan, or (None, []).
    """
    logger.info(f"Creating initial chapter descriptions for {num_chapters} chapters...")
    all_messages = []
    enhanced_acts = []

    if len(plan) != 3:
        logger.error(f"Plan passed into create_chapters does not have 3 acts. Instead, it has {len(plan)} acts.")
        return all_messages, plan

    # Distribute chapters among acts
    chapters_per_act = [num_chapters // 3] * 3
    for i in range(num_chapters % 3):
        chapters_per_act[i] += 1

    for act_num in range(len(plan)):
        num_chapters_in_act = chapters_per_act[act_num]
        logger.info(f"Starting chapter creation for act {act_num + 1} with {num_chapters_in_act} chapters")
        try:
            # Generate text_plan based on current state of enhanced_acts
            current_plan = plan[:act_num] + enhanced_acts[act_num:]
            text_plan = Plan.plan_2_str(current_plan)

            messages = agent.prompt_constructor.create_chapters_messages(act_num, text_plan, book_spec, agent.form, num_chapters_in_act)
            logger.info(f"Making LLM call for act {act_num + 1}...")
            enhanced_act_raw = await agent.query_chat(messages[1]['content'], messages[0]['content'], loop)
            logger.info(f"LLM call finished for act {act_num + 1}.")

            if enhanced_act_raw is None:
                logger.error(f"Failed to generate plot chapter for act {act_num + 1}")
                all_messages.append(messages)
                enhanced_acts.append(plan[act_num])  # Keep the original act if enhancement fails
                continue

            logger.debug(f"Raw LLM response for act {act_num + 1}:\n{enhanced_act_raw}")
            try:
                act_dict = Plan.parse_act_chapters(enhanced_act_raw)

                # Check if the number of chapters generated matches the expected number
                if len(act_dict['chapters']) != num_chapters_in_act:
                    logger.warning(f"Generated {len(act_dict['chapters'])} chapters for act {act_num + 1}, expected {num_chapters_in_act}. Using generated chapters.")

                if len(act_dict['chapters']) < 1:
                    logger.warning(f"Failed to generate chapters for act: {act_num + 1}, using original act")
                    logger.debug(f"Act {act_num + 1} raw response: {enhanced_act_raw}")
                    enhanced_acts.append(plan[act_num])  # Keep the original act
                    continue
                else:
                    enhanced_acts.append(act_dict)
                all_messages.append(messages)
                logger.info(f"Chapter descriptions created for act {act_num + 1}")

            except Exception as e:
                logger.warning(f"Failed to parse act dict in enhance plot chapters response: {e}, using original act")
                logger.debug(f"Act {act_num + 1} raw response: {enhanced_act_raw}")
                all_messages.append(messages)
                enhanced_acts.append(plan[act_num])  # Keep the original act
                continue
        except Exception as e:
             logger.error(f"An error occurred during chapter creation for act {act_num + 1}: {e}, using original act")
             all_messages.append(messages)
             enhanced_acts.append(plan[act_num])  # Keep the original act
             continue
        logger.info(f"Finished chapter creation for act {act_num + 1}")

    output_manager.save_output("plot_chapters", Plan.plan_2_str(enhanced_acts))
    agent.embedding_manager.add_embedding("plot_chapters", Plan.plan_2_str(enhanced_acts))
    logger.info("Chapter descriptions created and saved.")
    return all_messages, enhanced_acts

async def enhance_plot_outline(agent, book_spec, plan, loop, output_manager):
    """
    Enhances the plot outline by iteratively querying the LLM for each act.

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
    all_messages = []
    enhanced_acts = []

    for act_num in range(len(plan)):
        logger.info(f"Enhancing Act {act_num + 1}...")
        try:
            # Prepare the prompt
            messages = agent.prompt_constructor.enhance_plot_chapters_messages(act_num, Plan.plan_2_str(plan), book_spec, agent.form)
            logger.info(f"Sending request for Act {act_num + 1}...")
            enhanced_act_raw = await agent.query_chat(messages[1]['content'], messages[0]['content'], loop)
            logger.info(f"Response received for Act {act_num + 1}.")

            if enhanced_act_raw is None:
                logger.error(f"Failed to enhance Act {act_num + 1}.")
                all_messages.append(messages)
                enhanced_acts.append(plan[act_num])
                continue

            # Parse the enhanced act
            try:
                act_dict = Plan.parse_act_chapters(enhanced_act_raw)
                if not act_dict['chapters']:
                    logger.warning(f"Enhanced Act {act_num + 1} contains no chapters. Keeping the original act.")
                    enhanced_acts.append(plan[act_num])
                else:
                    enhanced_acts.append(act_dict)
                    logger.info(f"Successfully enhanced Act {act_num + 1}.")

            except Exception as e:
                logger.error(f"Failed to parse enhanced Act {act_num + 1}: {e}. Keeping the original act.")
                enhanced_acts.append(plan[act_num])

        except Exception as e:
            logger.error(f"An error occurred while enhancing Act {act_num + 1}: {e}. Keeping the original act.")
            enhanced_acts.append(plan[act_num])

        all_messages.append(messages)

    # Save and return the enhanced plan
    output_manager.save_output("enhanced_plot_outline", Plan.plan_2_str(enhanced_acts))
    agent.embedding_manager.add_embedding("enhanced_plot_outline", Plan.plan_2_str(enhanced_acts))
    logger.info("Enhanced plot outline saved.")
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