# menu.py
import os
import sys
import json
from datetime import datetime
import subprocess

from joblib import Memory
from loguru import logger
from omegaconf import DictConfig, OmegaConf

from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_fixed,
)
import questionary
import asyncio
import threading
import argparse

from storytelling_agent import StoryAgent
from plan import Plan
from classes import AppUsageException
import config

memory = Memory(".joblib_cache", verbose=0)

def log_retry(state):
    message = f"Tenacity retry {state.fn.__name__}: {state.attempt_number=}, {state.idle_for=}, {state.seconds_since_start=}"
    logger.exception(message)


def get_ollama_models():
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
        models = [line.split()[0] for line in result.stdout.strip().split("\n")[1:]]
        return models
    except subprocess.CalledProcessError as e:
        logger.error(f"Error listing Ollama models: {e}")
        return []


def initialize_story_agent(model_name, summary_model):
    llm_config = OmegaConf.create()
    llm_config.model = model_name
    summary_config = OmegaConf.create()
    summary_config.model = summary_model
    return StoryAgent(llm_config=llm_config, summary_config=summary_config)


def run_questionary(question):
    """Runs questionary in a separate thread and returns the result."""
    result = {"answer": None}

    def run():
        result["answer"] = question.ask()

    thread = threading.Thread(target=run)
    thread.start()
    thread.join()
    return result["answer"]


async def process_action(action, agent, output_dir, book_specification, plan, topic, title, loop):
    stage_dir = os.path.join(output_dir, action.replace(" ", "_"))
    os.makedirs(stage_dir, exist_ok=True)
    try:
        if action == "Initialize Book Specification":
            result = await agent.init_book_spec(topic, title, loop)
            if result:
              messages, book_specification = result
              logger.info(f"Book Specification:\n{book_specification}")
              with open(os.path.join(stage_dir, "book_specification.md"), "w") as f:
                  f.write(book_specification)
            else:
                logger.warning("Book specification failed to initialize")
            return book_specification, plan
        elif action == "Enhance Book Specification":
            if not book_specification:
                logger.warning("Please initialize a book specification first.")
                return book_specification, plan
            result = await agent.enhance_book_spec(
                book_specification, loop
            )
            if result:
              messages, book_specification = result
              logger.info(f"Enhanced Book Specification:\n{book_specification}")
              with open(
                  os.path.join(stage_dir, "enhanced_book_specification.md"), "w"
              ) as f:
                  f.write(book_specification)
            return book_specification, plan
        elif action == "Create Plot Chapters":
            if not book_specification:
                logger.warning("Please initialize a book specification first.")
                return book_specification, plan
            result = await agent.create_plot_chapters(book_specification, loop)
            if result:
              messages, plan = result
              text_plan = Plan.plan_2_str(plan)
              logger.info(f"Plot Chapters:\n{text_plan}")
              with open(os.path.join(stage_dir, "plot_chapters.md"), "w") as f:
                  f.write(text_plan)
            return book_specification, plan
        elif action == "Enhance Plot Chapters":
            if not plan:
                logger.warning("Please create plot chapters first.")
                return book_specification, plan
            result = await agent.enhance_plot_chapters(book_specification, plan, loop)
            if result:
              messages, plan = result
              text_plan = Plan.plan_2_str(plan)
              logger.info(f"Enhanced Plot Chapters:\n{text_plan}")
              with open(
                  os.path.join(stage_dir, "enhanced_plot_chapters.md"), "w"
              ) as f:
                  f.write(text_plan)
            return book_specification, plan
        elif action == "Split Chapters into Scenes":
            if not plan:
                logger.warning("Please create plot chapters first.")
                return book_specification, plan
            result = await agent.split_chapters_into_scenes(plan, loop)
            if result:
              messages, plan = result
              text_plan = Plan.plan_2_str(plan)
              logger.info(
                  f"Scene Breakdown (Not full plan, just a readable version):\n{text_plan}"
              )

              with open(os.path.join(stage_dir, "scene_breakdown.md"), "w") as f:
                  plan_json = json.dumps(plan, indent=4)
                  f.write(plan_json)
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
                        result = await agent.write_a_scene(
                            scene,
                            sc_num,
                            ch_num,
                            plan,
                            previous_scene=previous_scene, loop=loop
                        )
                        if result:
                          messages, generated_scene = result
                          if generated_scene is not None:
                            form_text.append(generated_scene)
                            scene_filename = (
                                f"scene_{sc_num}_chapter_{ch_num}_act_{act_num + 1}.md"
                            )
                            with open(
                                os.path.join(stage_dir, scene_filename), "w"
                            ) as f:
                                f.write(generated_scene)
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
                        result = await agent.continue_a_scene(
                            scene, sc_num, ch_num, plan, current_scene=current_scene, loop=loop
                        )
                        if result:
                            messages, generated_scene = result
                            if generated_scene is not None:
                                form_text.append(generated_scene)
                                scene_filename = f"enhanced_scene_{sc_num}_chapter_{ch_num}_act_{act_num + 1}.md"
                                with open(
                                    os.path.join(stage_dir, scene_filename), "w"
                                ) as f:
                                    f.write(generated_scene)
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

    model_name = run_questionary(questionary.select("Select a model for story generation:", choices=model_choices))
    summary_model = run_questionary(questionary.select("Select a model for text summarization:", choices=model_choices))

    config.MODEL_NAME = model_name  # Sets config variable
    config.SUMMARY_MODEL_NAME = summary_model


    agent = initialize_story_agent(model_name, summary_model)

    topic = run_questionary(questionary.text("Enter a topic for your story:"))

    # Generate and add title to book spec:
    loop = asyncio.get_event_loop()
    title = await agent.generate_title(topic, loop)
    logger.info(f"Generated Title: {title}")

    book_specification = None
    plan = None

    output_dir = os.path.join(".output", title.replace(" ", "_"))  # title-based subdir
    os.makedirs(output_dir, exist_ok=True)

    while True:
        action = run_questionary(
            questionary.select(
                "What do you want to do?",
                choices=[
                    "Initialize Book Specification",
                    "Enhance Book Specification",
                    "Create Plot Chapters",
                    "Enhance Plot Chapters",
                    "Split Chapters into Scenes",
                    "Write All Scenes",
                    "Enhance All Scenes",
                    "Exit",
                ],
            )
        )

        if action == "Exit":
            break

        if action == "Initialize Book Specification":
             book_specification, plan = await process_action(action, agent, output_dir, book_specification, plan, topic, title, loop)
             if book_specification: #Only continue the loop if the initialization did not fail
                 continue

        book_specification, plan = await process_action(action, agent, output_dir, book_specification, plan, topic, title, loop)


if __name__ == "__main__":
    asyncio.run(main())
