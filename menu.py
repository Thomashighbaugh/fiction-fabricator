# /home/tlh/fiction-fabricator/menu.py
import os
import sys
import json
from datetime import datetime
import subprocess
import asyncio
import threading
import argparse
import questionary
from loguru import logger
from omegaconf import DictConfig, OmegaConf
from joblib import Memory

from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from storytelling_agent import StoryAgent
from plan import Plan
from classes import AppUsageException
import config
from utils import edit_text_with_editor
from stages.book_specification import initialize_book_specification, enhance_book_specification
from stages.plot_development import create_plot_outline, enhance_plot_outline, split_into_scenes, create_chapters
from stages.scene_generation import generate_scene, continue_scene
from classes import AppUsageException
from prompts import (
    init_book_spec_messages,
    missing_book_spec_messages,
    enhance_book_spec_messages,
    create_plot_chapters_messages,
    enhance_plot_chapters_messages,
    split_chapters_into_scenes_messages,
    scene_messages,
    title_generation_messages,
    summarization_messages,
    book_spec_fields,
    prev_scene_intro,
    cur_scene_intro
)

memory = Memory(".joblib_cache", verbose=0)

def log_retry(state):
    message = f"Tenacity retry {state.fn.__name__}: {state.attempt_number=}, {state.idle_for=}, {state.seconds_since_start=}"
    logger.exception(message)

class OutputManager:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        os.makedirs(self.project_dir, exist_ok=True)

    def save_output(self, filename, content):
        filepath = os.path.join(self.project_dir, f"{filename}.md")
        with open(filepath, "w") as f:
            f.write(content)
        logger.info(f"Saved output to {filepath}")

    def load_output(self, filename):
        filepath = os.path.join(self.project_dir, f"{filename}.md")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return f.read()
        return None

def get_ollama_models():
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
        # Attempt to split and extract the model name, handling potential variations in output format
        models = []
        for line in result.stdout.strip().split("\n")[1:]:
             parts = line.split()
             if parts:
                 models.append(parts[0])
        return models
    except subprocess.CalledProcessError as e:
        logger.error(f"Error listing Ollama models: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error parsing ollama models: {e}")
        return []

def initialize_story_agent(model_name, summary_model):
    llm_config = OmegaConf.create()
    llm_config.model = model_name
    summary_config = OmegaConf.create()
    summary_config.model = summary_model
    prompt_engine = {
        "init_book_spec_messages":init_book_spec_messages,
        "missing_book_spec_messages": missing_book_spec_messages,
        "enhance_book_spec_messages": enhance_book_spec_messages,
        "create_plot_chapters_messages": create_plot_chapters_messages,
        "enhance_plot_chapters_messages": enhance_plot_chapters_messages,
        "split_chapters_into_scenes_messages": split_chapters_into_scenes_messages,
        "scene_messages": scene_messages,
        "title_generation_messages": title_generation_messages,
        "summarization_messages": summarization_messages,
        "book_spec_fields":book_spec_fields,
        "prev_scene_intro":prev_scene_intro,
        "cur_scene_intro":cur_scene_intro
    }
    return StoryAgent(llm_config=llm_config, summary_config=summary_config, prompt_engine = prompt_engine)

async def run_questionary(question):
    """Runs questionary in a separate thread and returns the result."""
    result = {"answer": None}

    async def run():
        result["answer"] = await question.ask_async()
    
    await run()
    return result["answer"]

async def process_action(action, agent, output_manager, book_specification, plan, topic, project_title, loop):
    stage_dir = os.path.join(output_manager.project_dir, f"{action.replace(' ', '_')}")
    os.makedirs(stage_dir, exist_ok=True)

    async def handle_edit(text, description, output_name, parse_function=None):
          if await questionary.confirm(f"Edit the {description.lower()}?").ask_async():
              edited_text = await edit_text_with_editor(text, description) or text
              output_manager.save_output(output_name, edited_text)
              if parse_function:
                return parse_function(edited_text)
              return edited_text
          return text

    try:
        if action == "Initialize Book Specification":
            messages, book_specification = await agent.init_book(topic, loop, output_manager)
            if book_specification:
                logger.info(f"Book Specification:\n{book_specification}")
                book_specification = await handle_edit(book_specification, "Book Specification", "book_specification")
            else:
                logger.warning("Book specification failed to initialize")
            return book_specification, plan

        elif action == "Enhance Book Specification":
            if not book_specification:
                logger.warning("Please initialize a book specification first.")
                return book_specification, plan
            messages, book_specification = await agent.enhance_book(book_specification, loop, output_manager)
            if book_specification:
              logger.info(f"Enhanced Book Specification:\n{book_specification}")
              book_specification = await handle_edit(book_specification, "Enhanced Book Specification", "enhanced_book_spec")
            return book_specification, plan
        
        elif action == "Create Plot Outline":
            if not book_specification:
                logger.warning("Please initialize a book specification first.")
                return book_specification, plan
            messages, plan = await agent.create_plot(book_specification, loop, output_manager)
            if plan:
                text_plan = Plan.plan_2_str(plan)
                logger.info(f"Plot Acts:\n{text_plan}")
                plan = await handle_edit(text_plan, "plot acts", "plot_acts", Plan.parse_text_plan) or plan
            return book_specification, plan

        elif action == "Create Chapter Descriptions":
            if not plan:
                logger.warning("Please create plot acts first.")
                return book_specification, plan
            # Ensure the plan is in the correct format before passing to create_chapters
            if isinstance(plan, str):
                logger.warning("Plan is a string. Parsing it into the correct format.")
                plan = Plan.parse_text_plan(plan)
            elif not all(isinstance(item, dict) and 'act_descr' in item and 'chapters' in item for item in plan):
                logger.error("Invalid plan format: 'plan' must be a list of dictionaries with 'act_descr' and 'chapters' keys.")
                return book_specification, plan

            messages, enhanced_plan = await agent.create_chapters(book_specification, plan, loop, output_manager)
            if enhanced_plan:
                text_plan = Plan.plan_2_str(enhanced_plan)
                logger.info(f"Initial Chapter Descriptions:\n{text_plan}")
                enhanced_plan = await handle_edit(text_plan, "chapter descriptions", "plot_chapters", Plan.parse_text_plan) or enhanced_plan
            else:
                logger.warning("Failed to create chapter descriptions.")
            return book_specification, enhanced_plan

        elif action == "Enhance Plot Outline":
            if not plan:
                logger.warning("Please create plot chapters first.")
                return book_specification, plan
            messages, plan = await agent.enhance_plot(book_specification, plan, loop, output_manager)
            if plan:
                text_plan = Plan.plan_2_str(plan)
                logger.info(f"Enhanced Plot Chapters:\n{text_plan}")
                plan = await handle_edit(text_plan, "enhanced plot outline", "enhanced_plot_chapters", Plan.parse_text_plan) or plan
            return book_specification, plan

        elif action == "Split Chapters into Scenes":
            if not plan:
                logger.warning("Please create plot chapters first.")
                return book_specification, plan
            messages, plan = await agent.split_scenes(plan, loop, output_manager)
            if plan:
                text_plan = Plan.plan_2_str(plan)
                logger.info(f"Scene Breakdown (Not full plan, just a readable version):\n{text_plan}")
                if await questionary.confirm("Edit the scene breakdown?").ask_async():
                    for i, act in enumerate(plan):
                        if act.get('act_scenes'):
                            act_num = i + 1
                            edited_act_scenes = await edit_text_with_editor(act['act_scenes'], f"Scene Breakdown for Act {act_num}") or act['act_scenes']
                            # Update act_scenes only if the user didn't cancel the edit
                            if edited_act_scenes is not None:
                                act['act_scenes'] = edited_act_scenes
                    output_manager.save_output("scenes_breakdown", Plan.plan_2_str(plan))
            return book_specification, plan

        elif action == "Write All Scenes":
            if not plan:
                logger.warning("Please complete the planning stages first")
                return book_specification, plan
            form_text = []
            for act_num, act in enumerate(plan):
                for ch_num, chapter in act["chapter_scenes"].items():
                    sc_num = 1
                    for scene_idx, scene in enumerate(chapter):
                        previous_scene = form_text[-1] if form_text else None
                        messages, generated_scene = await agent.write_scene(
                            scene,
                            sc_num,
                            ch_num,
                            plan,
                            previous_scene=previous_scene, loop=loop, output_manager=output_manager
                        )
                        if generated_scene:
                           form_text.append(generated_scene)
                           scene_filename = (
                                f"scene_{sc_num}_chapter_{ch_num}_act_{act_num + 1}.md"
                            )
                        sc_num += 1
            return book_specification, plan

        elif action == "Enhance All Scenes":
            if not plan:
                logger.warning("Please complete the planning stages first")
                return book_specification, plan
            form_text = []
            for act_num, act in enumerate(plan):
                for ch_num, chapter in act["chapter_scenes"].items():
                    sc_num = 1
                    for scene_idx, scene in enumerate(chapter):
                       current_scene = form_text[-1] if form_text else None
                       messages, generated_scene = await agent.continue_scene(
                            scene, sc_num, ch_num, plan, current_scene=current_scene, loop=loop, output_manager=output_manager
                        )
                       if generated_scene:
                            form_text.append(generated_scene)
                            scene_filename = f"enhanced_scene_{sc_num}_chapter_{ch_num}_act_{act_num + 1}.md"
                            sc_num += 1

            return book_specification, plan
        return book_specification, plan
    except Exception as exception:
        logger.exception(f"An error occurred: {exception}")
        return book_specification, plan

async def main():
    parser = argparse.ArgumentParser(description="Storytelling Agent")
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    args = parser.parse_args()

    logger.remove()
    logger.add(sys.stderr, level=args.log_level)

    # Model Selection using ollama
    model_choices = get_ollama_models()
    if not model_choices:
        logger.error(
            "No Ollama models found. Please ensure Ollama is running and has models downloaded."
        )
        sys.exit(1)

    model_name = await run_questionary(questionary.select("Select a model for story generation:", choices=model_choices))
    summary_model = await run_questionary(questionary.select("Select a model for text summarization:", choices=model_choices))

    config.MODEL_NAME = model_name  # Sets config variable
    config.SUMMARY_MODEL_NAME = summary_model

    agent = initialize_story_agent(model_name, summary_model)

    topic = await run_questionary(questionary.text("Enter a topic for your story:"))

    # Generate and add title to book spec:
    loop = asyncio.get_event_loop()
    title = await agent.generate_title(topic, loop)
    logger.info(f"Generated Title: {title}")
    project_title = title.replace(" ", "_")
    book_specification = None
    plan = None

    output_dir = os.path.join("output", project_title)
    output_manager = OutputManager(output_dir)  # Initialize OutputManager
    os.makedirs(output_dir, exist_ok=True)
    agent.set_project_name(project_title)

    menu_choices=[
                    "Initialize Book Specification",
                    "Enhance Book Specification",
                    "Create Plot Outline",
                    "Create Chapter Descriptions",
                    "Enhance Plot Outline",
                    "Split Chapters into Scenes",
                    "Write All Scenes",
                    "Enhance All Scenes",
                    "Exit",
                ]
    action_num = 1
    while True:
        action = await run_questionary(
            questionary.select(
                "What do you want to do?",
                choices=menu_choices,
            )
        )
        if action == "Exit":
            break
        book_specification, plan = await process_action(action, agent, output_manager, book_specification, plan, topic, project_title, loop)

if __name__ == "__main__":
    asyncio.run(main())