import json
import os
import subprocess
import sys

import questionary
from joblib import Memory
from loguru import logger
from omegaconf import OmegaConf

import config
from plan import Plan
from storytelling_agent import StoryAgent

# Initialize joblib memory for caching
memory = Memory(".joblib_cache", verbose=0)

def log_retry(state):
    """Logs retry attempts with details."""
    message = f"Tenacity retry {state.fn.__name__}: attempt={state.attempt_number}, idle_for={state.idle_for}, seconds_since_start={state.seconds_since_start}"
    logger.exception(message)

def get_ollama_models():
    """Retrieves available Ollama models."""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
        # Extract model names from the output
        models = [line.split()[0] for line in result.stdout.strip().split("\n")[1:]]
        return models
    except subprocess.CalledProcessError as e:
        logger.error(f"Error listing Ollama models: {e}")
        return []

def initialize_story_agent(model_name):
    """Initializes the StoryAgent with the selected model."""
    config.MODEL_NAME = model_name
    llm_config = OmegaConf.create()
    llm_config.model = config.MODEL_NAME
    return StoryAgent(llm_config=llm_config)

def initialize_output_directory(title):
    """Creates the output directory based on the story title."""
    output_dir = os.path.join(".output", title.replace(" ", "_"))
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def process_action(action, agent, output_dir, book_specification=None, plan=None):
     """Processes the user selected action"""
     stage_dir = os.path.join(output_dir, action.replace(" ", "_"))
     os.makedirs(stage_dir, exist_ok=True)

     if action == "Initialize Book Specification":
          messages, book_specification = agent.init_book_spec(topic, title)
          logger.info(f"Book Specification:\n{book_specification}")
          with open(os.path.join(stage_dir, "book_specification.md"), "w") as f:
              f.write(book_specification)
          return book_specification, plan
     elif action == "Enhance Book Specification":
          if not book_specification:
               logger.warning("Please initialize a book specification first.")
               return book_specification, plan
          messages, book_specification = agent.enhance_book_spec(book_specification)
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
          messages, plan = agent.create_plot_chapters(book_specification)
          text_plan = Plan.plan_2_str(plan)
          logger.info(f"Plot Chapters:\n{text_plan}")
          with open(os.path.join(stage_dir, "plot_chapters.md"), "w") as f:
                f.write(text_plan)
          return book_specification, plan
     elif action == "Enhance Plot Chapters":
          if not plan:
                logger.warning("Please create plot chapters first.")
                return book_specification, plan
          messages, plan = agent.enhance_plot_chapters(book_specification, plan)
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
          messages, plan = agent.split_chapters_into_scenes(plan)
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
                        messages, generated_scene = agent.write_a_scene(
                                 scene,
                                sc_num,
                                ch_num,
                                plan,
                                previous_scene=previous_scene,
                        )
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
                          messages, generated_scene = agent.continue_a_scene(
                                scene, sc_num, ch_num, plan, current_scene=current_scene
                          )
                          form_text.append(generated_scene)
                          scene_filename = f"enhanced_scene_{sc_num}_chapter_{ch_num}_act_{act_num + 1}.md"
                          with open(
                                os.path.join(stage_dir, scene_filename), "w"
                          ) as f:
                                f.write(generated_scene)
                          sc_num += 1
          return book_specification, plan
     return book_specification, plan


def main():
    """Main function to run the story generation menu."""
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

    # Model Selection
    model_choices = get_ollama_models()
    if not model_choices:
        logger.error(
            "No Ollama models found. Ensure Ollama is running and has models downloaded."
        )
        sys.exit(1)
    model_name = questionary.select("Select a model:", choices=model_choices).ask()

    # Initialize Story Agent
    agent = initialize_story_agent(model_name)

    # Get story topic
    topic = questionary.text("Enter a topic for your story:").ask()

    # Generate and add title to book spec
    title = agent.generate_title(topic)
    logger.info(f"Generated Title: {title}")

    # Initialize Variables
    book_specification = None
    plan = None

    # Set output directory
    output_dir = initialize_output_directory(title)

    # Main loop for menu interactions
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
        if action == "Exit":
             break

        try:
            book_specification, plan = process_action(action, agent, output_dir, book_specification, plan)

        except Exception as exception:
             logger.exception(f"An error occurred: {exception}")


if __name__ == "__main__":
    main()
