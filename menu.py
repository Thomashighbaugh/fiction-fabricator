import os
import sys
import json
from datetime import datetime

import openai
from joblib import Memory
from loguru import logger
from omegaconf import DictConfig, OmegaConf
from openai import OpenAIError
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_fixed,
)
import questionary

from storytelling_agent import StoryAgent, make_call
from plan import Plan
from classes import AppUsageException
import config

memory = Memory(".joblib_cache", verbose=0)


def log_retry(state):
    message = f"Tenacity retry {state.fn.__name__}: {state.attempt_number=}, {state.idle_for=}, {state.seconds_since_start=}"
    logger.exception(message)


def main():
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

    # Model Selection
    model_choices = [
        "meta-llama/Meta-Llama-3.1-405B-Instruct",
        "mlabonne/Llama-3.1-70B-Instruct-lorablated",
        "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
        "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "DavidAU/L3-Dark_Mistress-The_Guilty-Pen-Uncensored-17.4B",
        "SzilviaB/DarkDareDevilAura-abliterated-uncensored-OAS-8b",
        "DavidAU/MN-18.5B-Celeste-V1.9-Story-Wizard-ED1-Instruct",
        "Other"  # Allow custom model entry
    ]
    model_name = questionary.select("Select a model:", choices=model_choices).ask()
    if model_name == "Other":
        model_name = questionary.text("Enter the Hugging Face model name (username/model-name):").ask()
        if not model_name:
            logger.error("Invalid model name. Exiting.")
            sys.exit(1)

    config.MODEL_NAME = f"hf:{model_name}"  # Sets config variable

    llm_config = OmegaConf.create()
    llm_config.glhf_auth_token = config.GLHF_AUTH_TOKEN
    llm_config.model = config.MODEL_NAME

    if not llm_config.glhf_auth_token:
        logger.error("GLHF_AUTH_TOKEN environment variable not set. Please set it and try again.")
        sys.exit(1)

    topic = questionary.text("Enter a topic for your story:").ask()

    agent = StoryAgent(llm_config=llm_config)

    # Generate and add title to book spec:
    title = agent.generate_title(topic)
    logger.info(f"Generated Title: {title}")

    book_specification = None
    plan = None

    output_dir = os.path.join(".output", title.replace(" ", "_"))  # title-based subdir
    os.makedirs(output_dir, exist_ok=True)

    while True:
        action = questionary.select(
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
        ).ask()

        stage_dir = os.path.join(output_dir, action.replace(" ", "_"))
        os.makedirs(stage_dir, exist_ok=True) 

        if action == "Exit":
            break

        try:
            if action == "Initialize Book Specification":
                messages, book_specification = agent.init_book_spec(topic, title)
                logger.info(f"Book Specification:\n{book_specification}")
                with open(os.path.join(stage_dir, "book_specification.md"), "w") as f:
                    f.write(book_specification)
            elif action == "Enhance Book Specification":
                if not book_specification:
                    logger.warning("Please initialize a book specification first.")
                    continue
                messages, book_specification = agent.enhance_book_spec(book_specification)
                logger.info(f"Enhanced Book Specification:\n{book_specification}")
                with open(os.path.join(stage_dir, "enhanced_book_specification.md"), "w") as f:
                    f.write(book_specification)
            elif action == "Create Plot Chapters":
                if not book_specification:
                    logger.warning("Please initialize a book specification first.")
                    continue
                messages, plan = agent.create_plot_chapters(book_specification)
                text_plan = Plan.plan_2_str(plan)
                logger.info(f"Plot Chapters:\n{text_plan}")
                with open(os.path.join(stage_dir, "plot_chapters.md"), "w") as f:
                    f.write(text_plan)
            elif action == "Enhance Plot Chapters":
                if not plan:
                    logger.warning("Please create plot chapters first.")
                    continue
                messages, plan = agent.enhance_plot_chapters(book_specification, plan)
                text_plan = Plan.plan_2_str(plan)
                logger.info(f"Enhanced Plot Chapters:\n{text_plan}")
                with open(os.path.join(stage_dir, "enhanced_plot_chapters.md"), "w") as f:
                    f.write(text_plan)
            elif action == "Split Chapters into Scenes":
                if not plan:
                    logger.warning("Please create plot chapters first.")
                    continue
                messages, plan = agent.split_chapters_into_scenes(plan)

                text_plan = Plan.plan_2_str(plan) 
                logger.info(f"Scene Breakdown (Not full plan, just a readable version):\n{text_plan}")

                with open(os.path.join(stage_dir, "scene_breakdown.md"), "w") as f:
                   plan_json = json.dumps(plan, indent=4)
                   f.write(plan_json)

            elif action == "Write All Scenes":
                if not plan:
                    logger.warning("Please complete the planning stages first")
                    continue
                form_text = []
                for act_num, act in enumerate(plan):
                    for ch_num, chapter in act['chapter_scenes'].items():
                        sc_num = 1

                        for scene_idx, scene in enumerate(chapter):
                            previous_scene = form_text[-1] if form_text else None
                            messages, generated_scene = agent.write_a_scene(scene, sc_num, ch_num, plan, previous_scene=previous_scene)
                            form_text.append(generated_scene)
                            scene_filename = f"scene_{sc_num}_chapter_{ch_num}_act_{act_num + 1}.md"
                            with open(os.path.join(stage_dir, scene_filename), "w") as f:
                                f.write(generated_scene)
                            sc_num += 1

            elif action == "Enhance All Scenes":
                if not plan:
                    logger.warning("Please complete the planning stages first")
                    continue

                form_text = []
                for act_num, act in enumerate(plan):
                    for ch_num, chapter in act['chapter_scenes'].items():
                        sc_num = 1
                        for scene_idx, scene in enumerate(chapter):
                            current_scene = form_text[-1] if form_text else None
                            messages, generated_scene = agent.continue_a_scene(scene, sc_num, ch_num, plan, current_scene=current_scene)
                            form_text.append(generated_scene)
                            scene_filename = f"enhanced_scene_{sc_num}_chapter_{ch_num}_act_{act_num + 1}.md"
                            with open(os.path.join(stage_dir, scene_filename), "w") as f:
                                f.write(generated_scene)
                            sc_num += 1

        except Exception as exception:
            logger.exception(f"An error occurred: {exception}")


if __name__ == "__main__":
    main()
