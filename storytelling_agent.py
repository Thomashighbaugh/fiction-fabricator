# /home/tlh/fiction-fabricator/storytelling_agent.py
import sys
from loguru import logger
import re
import asyncio
import os
from embedding_manager import EmbeddingManager
from prompt_constructor import PromptConstructor
from plan import Plan
from world_model import WorldModel
import utils
import config
from stages.book_specification import initialize_book_specification, enhance_book_specification
from stages.plot_development import create_plot_outline, enhance_plot_outline, split_into_scenes, create_chapters
from stages.scene_generation import generate_scene, continue_scene

class StoryAgent:
    """
    A class to manage the storytelling process, integrating various stages from book specification to scene generation.
    """
    def __init__(self, llm_config, summary_config, system_prompt=None, prompt_engine=None, form='novel', n_crop_previous=400, max_combined_length=1500):
        """Initializes the StoryAgent.

        Args:
            llm_config (DictConfig): Configuration for the main language model.
            summary_config (DictConfig): Configuration for the summarization language model.
            system_prompt (str, optional): A system-level prompt for the LLM. Defaults to None.
            prompt_engine (dict, optional): An object to manage prompts. Defaults to None.
            form (str, optional): The form of the story (e.g., 'novel', 'short story'). Defaults to 'novel'.
            n_crop_previous (int, optional): Number of words to keep from the previous scene. Defaults to 400.
            max_combined_length (int, optional): Maximum combined length for LLM input. Defaults to 1500.
        """
        self.form = form
        self.llm_config = llm_config
        self.summary_config = summary_config
        self.n_crop_previous = n_crop_previous
        self.max_combined_length = max_combined_length
        self.system_prompt = system_prompt

        # Initialize helper classes
        self.embedding_manager = EmbeddingManager(llm_config=llm_config)
        self.prompt_constructor = PromptConstructor(prompt_engine, llm_config=llm_config, summary_config=summary_config)
        if self.system_prompt:
            self.prompt_constructor.system_message = self.system_prompt
        self.world_model = WorldModel()
        self.project_name = None  # To store the current project name

    def set_project_name(self, project_name):
        """Sets the current project name."""
        self.project_name = project_name

    def get_project_directory(self):
        """Returns the directory for the current project."""
        if not self.project_name:
            raise ValueError("Project name not set.")
        return os.path.join("output", self.project_name)

    async def query_chat(self, prompt, system_message, loop=None):
        """Queries the chat model with the given prompt and system message.

        Args:
            prompt (str): The user prompt.
            system_message (str): The system message.
            loop (asyncio.AbstractEventLoop, optional): The event loop. Defaults to None.

        Returns:
            str: The response from the chat model.
        """
        return await self.prompt_constructor.make_call(prompt, system_message)

    async def generate_title(self, topic, loop):
         """Generates a single title for the story based on the topic.

         Args:
            topic (str): The topic of the story.
            loop (asyncio.AbstractEventLoop): The event loop.

         Returns:
            str: The generated title.
         """
         logger.info("Generating title...")
         messages = self.prompt_constructor.title_generation_messages(topic)
         response = await self.query_chat(messages[1]['content'], messages[0]['content'])

         if response is None or response == "":
             logger.warning("Failed to generate title, using default.")
             return "Untitled Story"

         # Extract the first sentence and truncate if necessary
         title = response.split('.')[0].strip(' "\n')
         if len(title) > 100:
             title = title[:97] + "..."  # Truncate and add ellipsis if too long
         logger.info(f"Generated title: {title}")
         return title

    def _prepare_scene_text(self, text):
        """Prepares the scene text by removing leading chapter/scene markers.

        Args:
            text (str): The raw scene text.

        Returns:
            str: The prepared scene text.
        """
        lines = text.split('\n')
        chapter_ids = [i for i in range(5) if 'Chapter ' in lines[i]]
        if chapter_ids:
            lines = lines[chapter_ids[-1] + 1:]
        scene_ids = [i for i in range(5) if 'Scene ' in lines[i]]
        if scene_ids:
            lines = lines[scene_ids[-1] + 1:]

        placeholder_index = None
        for i in range(len(lines)):
            if lines[i].startswith('Chapter ') or lines[i].startswith('Scene '):
                placeholder_index = i
                break
        if placeholder_index is not None:
            lines = lines[:i]

        text = '\n'.join(lines)
        return text

    async def init_book(self, topic, loop, output_manager):
        """Initializes the book specification.

        Args:
            topic (str): The topic of the story.
            loop (asyncio.AbstractEventLoop): The event loop.
            output_manager (OutputManager): An object to handle output and loading.

        Returns:
            tuple: A tuple containing the messages and the book specification text.
        """
        return await initialize_book_specification(self, topic, loop, output_manager)

    async def enhance_book(self, book_spec, loop, output_manager):
        """Enhances the book specification.

        Args:
            book_spec (str): The initial book specification.
            loop (asyncio.AbstractEventLoop): The event loop.
            output_manager (OutputManager): An object to handle output and loading.

        Returns:
           tuple: A tuple containing the messages and the enhanced book specification text.
        """
        return await enhance_book_specification(self, book_spec, loop, output_manager)

    async def create_plot(self, book_spec, loop, output_manager):
        """Creates the plot outline.

        Args:
            book_spec (str): The book specification.
            loop (asyncio.AbstractEventLoop): The event loop.
            output_manager (OutputManager): An object to handle output and loading.

        Returns:
             tuple: A tuple containing the messages and the plot plan.
        """
        return await create_plot_outline(self, book_spec, loop, output_manager)

    async def create_chapters(self, book_spec, plan, loop, output_manager):
        """Creates the chapter descriptions.

        Args:
            book_spec (str): The book specification.
            plan (list): The initial plot plan.
            loop (asyncio.AbstractEventLoop): The event loop.
            output_manager (OutputManager): An object to handle output and loading.

        Returns:
             tuple: A tuple containing the messages and the enhanced plot plan.
        """
        return await create_chapters(self, book_spec, plan, loop, output_manager)

    async def enhance_plot(self, book_spec, plan, loop, output_manager):
        """Enhances the plot outline.

        Args:
            book_spec (str): The book specification.
            plan (list): The initial plot plan.
            loop (asyncio.AbstractEventLoop): The event loop.
            output_manager (OutputManager): An object to handle output and loading.

        Returns:
            tuple: A tuple containing the messages and the enhanced plot plan.
        """
        return await enhance_plot_outline(self, book_spec, plan, loop, output_manager)

    async def split_scenes(self, plan, loop, output_manager):
        """Splits chapters into scenes.

        Args:
            plan (list): The plot plan.
            loop (asyncio.AbstractEventLoop): The event loop.
            output_manager (OutputManager): An object to handle output and loading.

        Returns:
            tuple: A tuple containing the messages and the plan with scenes.
        """
        return await split_into_scenes(self, plan, loop, output_manager)

    async def write_scene(self, scene, scene_number, chapter_number, plan, previous_scene, loop, output_manager):
        """Writes a scene.

         Args:
            scene (str): The specification for the scene.
            scene_number (int): The scene number.
            chapter_number (int): The chapter number.
            plan (list): The plot plan.
            previous_scene (str, optional): The content of the previous scene.
            loop (asyncio.AbstractEventLoop): The event loop.
            output_manager (OutputManager): An object to handle output and loading.

        Returns:
            tuple: A tuple containing the messages and the generated scene content.
        """
        return await generate_scene(self, scene, scene_number, chapter_number, plan, previous_scene, loop, output_manager)

    async def continue_scene(self, scene, scene_number, chapter_number, plan, current_scene, loop, output_manager):
        """Continues a scene.

        Args:
            scene (str): The specification for the scene.
            scene_number (int): The scene number.
            chapter_number (int): The chapter number.
            plan (list): The plot plan.
            current_scene (str): The current content of the scene.
            loop (asyncio.AbstractEventLoop): The event loop.
            output_manager (OutputManager): An object to handle output and loading.

        Returns:
           tuple: A tuple containing the messages and the continued scene content.
        """
        return await continue_scene(self, scene, scene_number, chapter_number, plan, current_scene, loop, output_manager)

    async def _write_scene_content(self, scene, scene_number, chapter_number, plan, previous_scene=None, loop=None):
        """Generates the content for a scene.

        Args:
            scene (str): The specification for the scene.
            scene_number (int): The scene number.
            chapter_number (int): The chapter number.
            plan (list): The plot plan.
            previous_scene (str, optional): The content of the previous scene.
            loop (asyncio.AbstractEventLoop, optional): The event loop. Defaults to None.

         Returns:
            tuple: A tuple containing the messages and the generated scene content, or (None, "").
        """
        try:
            text_plan = Plan.plan_2_str(plan)

            # Add the plot summary to context.
            plot_summary = await self.summarize_text(text_plan, 60, loop)
            if plot_summary is None:
                plot_summary = ""
            self.world_model.story_context['plot_summary'] = plot_summary

            if previous_scene:
                self.world_model.add_previous_scene(previous_scene)

            prev_scene_summary = self.world_model.get_previous_scene_summary()
            retrieved_context = self.embedding_manager.retrieve_relevant_embeddings(f"{scene} {text_plan}")

            messages = self.prompt_constructor.scene_messages(
                scene,
                scene_number,
                chapter_number,
                text_plan,
                self.form,
                plot_summary=plot_summary,
                characters=self.world_model.story_context['characters'],
                events=self.world_model.story_context['events'],
                theme=self.world_model.story_context['theme'],
                prev_scene_summary=prev_scene_summary,
                retrieved_context=retrieved_context
            )
            if messages is None:
                logger.error(f'Failed to generate messages for scene {scene_number}')
                return None, ""

            generated_scene = await self._generate_enhanced_scene_content(messages, loop)
            if generated_scene:
                event_summary = await self.summarize_text(generated_scene, length_in_words=20, loop=loop)
                if event_summary:
                    self.world_model.add_event(event_summary)
                scene_summary = await self.summarize_text(generated_scene, length_in_words=60, loop=loop)
                if scene_summary:
                    self.world_model.add_scene_summary(scene_summary)
                self.world_model.add_previous_scene(generated_scene)
                generated_scene = self._prepare_scene_text(generated_scene)
                logger.info(f"Generated Scene {scene_number} in Chapter {chapter_number}:\n{generated_scene[:100]}...")  # Show snippet

            return messages, generated_scene or ""

        except Exception as e:
            logger.error(f'Failed to write a scene: {e}')
            return None, ""

    async def _continue_scene_content(self, scene, scene_number, chapter_number, plan, current_scene, loop=None):
        """Continues generating content for an existing scene.

        Args:
            scene (str): The specification for the scene.
            scene_number (int): The scene number.
            chapter_number (int): The chapter number.
            plan (list): The plot plan.
            current_scene (str): The current content of the scene.
            loop (asyncio.AbstractEventLoop, optional): The event loop. Defaults to None.

        Returns:
            tuple: A tuple containing the messages and the continued scene content, or (None, "").
        """
        try:
            text_plan = Plan.plan_2_str(plan)

            # Add the plot summary to context.
            plot_summary = await self.summarize_text(text_plan, 60, loop)
            if plot_summary is None:
                plot_summary = ""
            self.world_model.story_context['plot_summary'] = plot_summary

            if current_scene:
                self.world_model.add_previous_scene(current_scene)

            prev_scene_summary = self.world_model.get_previous_scene_summary()

            retrieved_context = self.embedding_manager.retrieve_relevant_embeddings(f"{scene} {text_plan}")

            messages = self.prompt_constructor.scene_messages(
                scene,
                scene_number,
                chapter_number,
                text_plan,
                self.form,
                plot_summary=plot_summary,
                characters=self.world_model.story_context['characters'],
                events=self.world_model.story_context['events'],
                theme=self.world_model.story_context['theme'],
                prev_scene_summary=prev_scene_summary,
                retrieved_context=retrieved_context
            )
            if messages is None:
                logger.error(f'Failed to generate messages for continuing scene {scene_number}')
                return None, ""

            generated_scene = await self._generate_enhanced_scene_content(messages, loop=loop)
            if generated_scene:
                scene_summary = await self.summarize_text(generated_scene, length_in_words=60, loop=loop)
                if scene_summary:
                    self.world_model.add_scene_summary(scene_summary)
                self.world_model.add_previous_scene(generated_scene)
                generated_scene = self._prepare_scene_text(generated_scene)
                logger.info(f"Continued Scene {scene_number} in Chapter {chapter_number}:\n{generated_scene[:100]}...")  # Show snippet

            return messages, generated_scene or ""
        except Exception as e:
            logger.error(f'Failed to continue a scene: {e}')
            return None, ""

    def _parse_book_spec(self, text_spec):
        """Parses the book specification text into a dictionary.

         Args:
            text_spec (str): The raw book specification text.

        Returns:
            dict: A dictionary representation of the book specification.
        """
        fields = self.prompt_constructor.book_spec_fields
        spec_dict = {field: '' for field in fields}
        last_field = None
        if "\"\"\"" in text_spec[:int(len(text_spec) / 2)]:
            header, sep, text_spec = text_spec.partition("\"\"\"")
        text_spec = text_spec.strip()

        for line in text_spec.split('\n'):
            pseudokey, sep, value = line.partition(':')
            pseudokey = pseudokey.lower().strip()
            matched_key = [key for key in fields
                           if (key.lower().strip() in pseudokey)
                           and (len(pseudokey) < (2 * len(key.strip())))]
            if (':' in line) and (len(matched_key) == 1):
                last_field = matched_key[0]
                if last_field in spec_dict:
                    spec_dict[last_field] += value.strip()
            elif ':' in line:
                last_field = 'other'
                spec_dict[last_field] = ''
            else:
                if last_field:
                    spec_dict[last_field] += ' ' + line.strip()
        spec_dict.pop('other', None)
        return spec_dict

    async def summarize_text(self, text, length_in_words=60, loop=None):
        """Summarizes the given text.

        Args:
            text (str): The text to summarize.
            length_in_words (int, optional): The desired length of the summary in words. Defaults to 60.
            loop (asyncio.AbstractEventLoop, optional): The event loop. Defaults to None.

        Returns:
           str: The summary of the text.
        """
        try:
            messages = self.prompt_constructor.summarization_messages(text, length_in_words)
            summary = await self.query_chat(messages[1]['content'], messages[0]['content'])
            return summary
        except Exception as e:
            logger.error(f'Failed to summarize text: {e}')
            return None

    async def _generate_enhanced_scene_content(self, messages, loop=None):
        """Generates scene content with iterative enhancement.

         Args:
            messages (list): The list of messages for prompt construction.
            loop (asyncio.AbstractEventLoop, optional): The event loop. Defaults to None.

        Returns:
            str: The enhanced scene content.
        """
        try:
            summary_prompt = ''.join(self.prompt_constructor.generate_prompt_parts(messages))
            system_message = messages[0]['content']

            generated_scene = ''
            num_passes = 3
            length_in_words = 120

            previous_scene = self.world_model.get_previous_scene()
            if previous_scene:
                previous_scene = utils.keep_last_n_words(previous_scene, n=self.n_crop_previous)
            prev_scene_summary = self.world_model.get_previous_scene_summary()
            retrieved_context = self.embedding_manager.retrieve_relevant_embeddings(f"{messages[1]['content']} {self.world_model.story_context.get('plot_summary', '')}")

            for i in range(num_passes):
                prompt = f"{summary_prompt} \n\n {generated_scene} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the scene specification which are missing from the previously generated scene and are the most relevant. Include details from the previous scene as needed. If a previous scene summary exists include details from it as needed.\n\n      - Step 2: Write a new, denser scene of identical length which covers every entity and detail from the previous scene plus the missing entities. \n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous scene\n      - Faithful: present in the scene specification and prior scene\n      - Anywhere: located anywhere in the scene specification and prior scene\n\n      Guidelines:\n      - The first scene should be long (4-5 sentences, approx. 120 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous scene to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The scenes should become highly dense and concise yet self-contained, e.g., easily understood without the scene specification.\n\n      - Missing entities can appear anywhere in the new scene.\n\n      - Never drop entities from the previous scene. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each scene.\n      > Write the missing entities in missing_entities\n      > Write the scene in denser_scene\n      > Repeat the steps {num_passes} times per instructions above"

                if previous_scene:
                    prompt += f'{self.prompt_constructor.prev_scene_intro}\"\"\"{previous_scene}\"\"\"'
                if prev_scene_summary:
                    prompt += f'\n\nPrevious scene summary: \"\"\"{prev_scene_summary}\"\"\"'
                if retrieved_context:
                    prompt += f"\n\nRetrieved context:\n{retrieved_context}"

                if len(prompt) > self.max_combined_length:
                    prompt = f"{summary_prompt} \n\n {await self.summarize_text(generated_scene, length_in_words=length_in_words, loop=loop)} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the scene specification which are missing from the previously generated scene and are the most relevant. Include details from the previous scene as needed. If a previous scene summary exists include details from it as needed.\n\n      - Step 2: Write a new, denser scene of identical length which covers every entity and detail from the previous scene plus the missing entities.\n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous scene\n      - Faithful: present in the scene specification and prior scene\n      - Anywhere: located anywhere in the scene specification and prior scene\n\n      Guidelines:\n      - The first scene should be long (4-5 sentences, approx. 120 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous scene to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The scenes should become highly dense and concise yet self-contained, e.g., easily understood without the scene specification.\n\n      - Missing entities can appear anywhere in the new scene.\n\n      - Never drop entities from the previous scene. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each scene.\n      > Write the missing entities in missing_entities\n      > Write the scene in denser_scene\n      > Repeat the steps {num_passes} times per instructions above"

                    if previous_scene:
                        prompt += f'{self.prompt_constructor.prev_scene_intro}\"\"\"{previous_scene}\"\"\"'
                    if prev_scene_summary:
                        prompt += f'\n\nPrevious scene summary: \"\"\"{prev_scene_summary}\"\"\"'
                    if retrieved_context:
                        prompt += f"\n\nRetrieved context:\n{retrieved_context}"

                result = await self.query_chat(prompt, system_message)

                if result:
                    try:
                        start_missing = result.find("missing_entities:") + len("missing_entities:")
                        end_missing = result.find("denser_scene:")
                        missing_entities = result[start_missing:end_missing].strip()

                        start_scene = result.find("denser_scene:") + len("denser_scene:")
                        denser_scene = result[start_scene:].strip()

                        generated_scene = denser_scene
                    except Exception as e:
                        logger.warning(f'Failed to parse scene generation response: {e}, skipping to next step, raw response was:\n{result}')
                        continue
                else:
                    logger.warning(f'Failed to get a response from the model, skipping to next step')
                    continue

            return generated_scene
        except Exception as e:
            logger.error(f"Failed to generate scene content: {e}")
            return ""