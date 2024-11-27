import os
import sys
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
    wait_exponential,
)
import questionary

from storytelling_agent import StoryAgent, make_call
from plan import Plan
from classes import AppUsageException
import config

memory = Memory(".joblib_cache", verbose=0)

def log_retry(state):
    message = f"Tenacity retry {state.fn.__name__}: {state.attempt_number=}, {state.idle_for=}, {state.seconds_since_start=}"
    if state.attempt_number < 1:
        logger.warning(message)
    else:
        logger.exception(message)

def main():
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

    llm_config = OmegaConf.create()
    llm_config.glhf_auth_token = os.environ.get("GLHF_AUTH_TOKEN")
    llm_config.model = config.MODEL_NAME

    if not llm_config.glhf_auth_token:
        logger.error("GLHF_AUTH_TOKEN environment variable not set. Please set it and try again.")
        sys.exit(1)

    topic = questionary.text("Enter a topic for your story:").ask()
    agent = StoryAgent(llm_config=llm_config)
    book_specification = None
    plan = None

    while True:
        action = questionary.select(
            "What do you want to do?",
            choices=[
                "Initialize Book Specification",
                "Enhance Book Specification",
                "Create Plot Chapters",
                "Enhance Plot Chapters",
                "Split Chapters into Scenes",
                "Write a Scene",
                "Continue a Scene",
                "Generate Full Story",
                "Exit",
            ],
        ).ask()

        if action == "Exit":
            break

        try:
            if action == "Initialize Book Specification":
                messages, book_specification = agent.init_book_spec(topic)
                logger.info(f"Book Specification:\n{book_specification}")
            elif action == "Enhance Book Specification":
                if not book_specification:
                    logger.warning("Please initialize a book specification first.")
                    continue
                messages, book_specification = agent.enhance_book_spec(book_specification)
                logger.info(f"Enhanced Book Specification:\n{book_specification}")
            elif action == "Create Plot Chapters":
                if not book_specification:
                    logger.warning("Please initialize a book specification first.")
                    continue
                messages, plan = agent.create_plot_chapters(book_specification)
                logger.info(f"Plot Chapters:\n{Plan.plan_2_str(plan)}")
            elif action == "Enhance Plot Chapters":
                if not plan:
                    logger.warning("Please create plot chapters first.")
                    continue
                messages, plan = agent.enhance_plot_chapters(book_specification, plan)
                logger.info(f"Enhanced Plot Chapters:\n{Plan.plan_2_str(plan)}")
            elif action == "Split Chapters into Scenes":
                if not plan:
                    logger.warning("Please create plot chapters first.")
                    continue
                messages, plan = agent.split_chapters_into_scenes(plan)
                logger.info(f"Scene Breakdown:\n{plan}")
            elif action == "Generate Full Story":
                if not plan:
                    logger.warning("Please complete the planning stages first.")
                    continue
                story = agent.generate_story(topic)
                save_path = questionary.path("Enter a file path to save the story (or press Enter to skip):").ask()
                if save_path:
                    with open(save_path, "w") as file:
                        file.write("\n\n".join(story))
                    logger.info(f"Story saved to {save_path}")
                else:
                    logger.info(f"Generated Story:\n\n\n{'*'*20}\n\n".join(story))
            elif action == "Write a Scene":
                if not plan:
                    logger.warning("Please complete the planning stages first")
                    continue

                act_number = questionary.select("Select Act:", choices=[str(i + 1) for i in range(len(plan))]).ask()
                act_number = int(act_number) - 1

                available_chapters = list(plan[act_number]['chapter_scenes'].keys())
                chapter_number = questionary.select("Select Chapter:", choices=[str(chapter) for chapter in available_chapters]).ask()
                chapter_number = int(chapter_number)

                scene_number = questionary.text("Enter Scene Number:").ask()
                try:
                    scene_number = int(scene_number)
                    if not 1 <= scene_number <= len(plan[act_number]['chapter_scenes'][chapter_number]):
                        raise ValueError
                except ValueError:
                    logger.error(f"Invalid scene number. Please enter a number between 1 and {len(plan[act_number]['chapter_scenes'][chapter_number])}")
                    continue

                scene_specification = plan[act_number]['chapter_scenes'][chapter_number][scene_number - 1]
                messages, generated_scene = agent.write_a_scene(scene_specification, scene_number, chapter_number, plan)
                logger.info(f"Generated Scene:\n{generated_scene}")

            elif action == "Continue a Scene":
                if not plan:
                    logger.warning("Please complete the planning stages first")
                    continue

                act_number = questionary.select("Select Act:", choices=[str(i + 1) for i in range(len(plan))]).ask()
                act_number = int(act_number) - 1

                available_chapters = list(plan[act_number]['chapter_scenes'].keys())
                chapter_number = questionary.select("Select Chapter:", choices=[str(ch) for ch in available_chapters]).ask()
                chapter_number = int(chapter_number)

                scene_number = questionary.text("Enter Scene Number:").ask()
                try:
                    scene_number = int(scene_number)
                    if not 1 <= scene_number <= len(plan[act_number]['chapter_scenes'][chapter_number]):
                        raise ValueError
                except ValueError:
                    logger.error(f"Invalid scene number. Please enter a number between 1 and {len(plan[act_number]['chapter_scenes'][chapter_number])}")
                    continue

                scene_specification = plan[act_number]['chapter_scenes'][chapter_number][scene_number - 1]
                messages, generated_scene = agent.continue_a_scene(scene_specification, scene_number, chapter_number, plan)
                logger.info(f"Continued Scene:\n{generated_scene}")

        except Exception as exception:
            logger.exception(f"An error occurred: {exception}")


if __name__ == "__main__":
    main()
