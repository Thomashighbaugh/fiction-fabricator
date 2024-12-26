# storytelling_agent.py
import sys
from loguru import logger
import re
import asyncio
from embedding_manager import EmbeddingManager
from prompt_constructor import PromptConstructor
from plan import Plan
from world_model import WorldModel
import utils
import config


class StoryAgent:
    def __init__(self, llm_config, summary_config, system_prompt = None, prompt_engine=None, form='novel', n_crop_previous=400, max_combined_length=1500):

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

    async def query_chat(self, prompt, system_message, loop):
        return await self.prompt_constructor.make_call(system_message, prompt, loop)

    async def generate_title(self, topic, loop):
        messages = self.prompt_constructor.title_generation_messages(topic)
        response = await self.query_chat(messages[1]['content'], messages[0]['content'], loop)

        if response is None:
            return "Untitled Story"

        match = re.match(r"^(.*?)(?:\n\n|$)", response)
        if match:
            title = match.group(1).strip()
        else:
            title = "Untitled Story"
        return title

    def _prepare_scene_text(self, text):
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

    async def init_book_spec(self, topic, title, loop):
        try:
            messages = self.prompt_constructor.init_book_spec_messages(topic, self.form)
            text_spec = await self.query_chat(messages[1]['content'], messages[0]['content'], loop)
            if text_spec is None:
                logger.error("Failed to initialize book specification")
                return None, ""

            spec_dict = self._parse_book_spec(text_spec)
            text_spec = f"Title: {title}\n" + "\n".join(f"{key}: {value}" for key, value in spec_dict.items())
            self.world_model.init_world_model_from_spec(spec_dict)

            for field in self.prompt_constructor.book_spec_fields:
                while not spec_dict[field]:
                    messages = self.prompt_constructor.missing_book_spec_messages(field, text_spec)
                    missing_part = await self.query_chat(messages[1]['content'], messages[0]['content'], loop)
                    if missing_part is None:
                        logger.error(f"Failed to get missing field {field}")
                        return None, ""
                    key, sep, value = missing_part.partition(':')
                    if key.lower().strip() == field.lower().strip():
                        spec_dict[field] = value.strip()
            text_spec = f"Title: {title}\n" + "\n".join(f"{key}: {value}" for key, value in spec_dict.items())

            # Only add the embedding once at initialization:
            self.embedding_manager.add_embedding("book_spec", text_spec)
            return messages, text_spec

        except Exception as e:
            logger.error(f'Failed to initialize book specification: {e}')
            return None, ""

    async def enhance_book_spec(self, book_spec, loop):
        try:
            messages = self.prompt_constructor.enhance_book_spec_messages(book_spec, self.form)
            enhanced_spec = await self.query_chat(messages[1]['content'], messages[0]['content'], loop)
            if enhanced_spec is None:
                return None, ""

            enhanced_spec = f"Title: {book_spec.splitlines()[0].split(': ')[1]}\n" + enhanced_spec
            # Only add the embedding once at enhancement:
            self.embedding_manager.add_embedding("enhanced_book_spec", enhanced_spec)
            return messages, enhanced_spec
        except Exception as e:
            logger.error(f"Failed to enhance book spec: {e}")
            return None, ""

    async def create_plot_chapters(self, book_spec, loop):
        try:
            messages = self.prompt_constructor.create_plot_chapters_messages(book_spec, self.form)
            text_plan_string = await self.query_chat(messages[1]['content'], messages[0]['content'], loop)

            if text_plan_string is None:
               logger.error("Failed to create plot chapters.")
               return None, []

            plan = Plan.parse_text_plan(text_plan_string)
            # Only add the embedding when creating plot chapters:
            self.embedding_manager.add_embedding("plot_chapters", Plan.plan_2_str(plan))
            return messages, plan

        except Exception as e:
            logger.error(f'Failed to create plot chapters: {e}')
            return None, []

    async def enhance_plot_chapters(self, book_spec, plan, loop):
        try:
            text_plan = Plan.plan_2_str(plan)
            all_messages = []
            enhanced_acts = []
            for act_num in range(len(plan)):
                messages = self.prompt_constructor.enhance_plot_chapters_messages(act_num, text_plan, book_spec, self.form)
                enhanced_act = await self.query_chat(messages[1]['content'], messages[0]['content'], loop)
                if enhanced_act is None:
                    logger.error(f"Failed to enhance plot chapter for act {act_num}")
                    all_messages.append(messages)
                    enhanced_acts.append(None)
                    continue

                try:
                    act_dict = Plan.parse_act(enhanced_act)
                    if len(act_dict['chapters']) < 2:
                        logger.warning(f"Failed to generate a useable act for act: {act_num}, skipping")
                        enhanced_acts.append(None)
                        continue
                    else:
                        enhanced_acts.append(act_dict)

                    text_plan = Plan.plan_2_str(plan)
                    # Only add the embedding when enhancing the plot:
                    self.embedding_manager.add_embedding(f"enhanced_act_{act_num}", text_plan)
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
                return all_messages, enhanced_acts
        except Exception as e:
            logger.error(f'Failed to enhance plot chapters: {e}')
            return None, []

    async def split_chapters_into_scenes(self, plan, loop):
        try:
            all_messages = []
            act_chapters = {}
            for i, act in enumerate(plan, start=1):
                text_act, chs = Plan.act_2_str(plan, i)
                act_chapters[i] = chs
                messages = self.prompt_constructor.split_chapters_into_scenes_messages(i, text_act, self.form)
                act_scenes = await self.query_chat(messages[1]['content'], messages[0]['content'], loop)

                if act_scenes:
                    act['act_scenes'] = act_scenes
                    all_messages.append(messages)
                else:
                    logger.error(f'Failed to split scenes in act {i}')
                    all_messages.append(messages)
                    continue

            for i, act in enumerate(plan, start=1):
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
            return all_messages, plan
        except Exception as e:
            logger.error(f'Failed to split chapter into scenes: {e}')
            return None, []

    async def write_a_scene(self, scene, scene_number, chapter_number, plan, previous_scene=None, loop=None):
        try:
            text_plan = Plan.plan_2_str(plan)

            #Add the plot summary to context.
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

            generated_scene = await self.generate_scene_content(messages, loop)
            if generated_scene:
                event_summary = await self.summarize_text(generated_scene, length_in_words=20, loop=loop)
                if event_summary:
                  self.world_model.add_event(event_summary)
                scene_summary = await self.summarize_text(generated_scene, length_in_words=60, loop=loop)
                if scene_summary:
                   self.world_model.add_scene_summary(scene_summary)
                # Only add embeddings when scenes are written and enhanced
                self.embedding_manager.add_embedding(f"scene_{scene_number}_chapter_{chapter_number}", generated_scene)
                self.world_model.add_previous_scene(generated_scene)
                generated_scene = self._prepare_scene_text(generated_scene)
                logger.info(f"Generated Scene {scene_number} in Chapter {chapter_number}:\n{generated_scene}")


            return messages, generated_scene or ""

        except Exception as e:
            logger.error(f'Failed to write a scene: {e}')
            return None, ""

    async def continue_a_scene(self, scene, scene_number, chapter_number, plan, current_scene, loop=None):
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

             generated_scene = await self.generate_scene_content(messages, loop)
             if generated_scene:
                  scene_summary = await self.summarize_text(generated_scene, length_in_words=60, loop=loop)
                  if scene_summary:
                      self.world_model.add_scene_summary(scene_summary)
                   # Only add embeddings when scenes are written and enhanced
                  self.embedding_manager.add_embedding(f"enhanced_scene_{scene_number}_chapter_{chapter_number}",
                                                     generated_scene)
                  self.world_model.add_previous_scene(generated_scene)
                  generated_scene = self._prepare_scene_text(generated_scene)
                  logger.info(f"Generated Scene {scene_number} in Chapter {chapter_number}:\n{generated_scene}")


             return messages, generated_scene or ""
         except Exception as e:
              logger.error(f'Failed to continue a scene: {e}')
              return None, ""

    def _parse_book_spec(self, text_spec):
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
        try:
            messages = self.prompt_constructor.summarization_messages(text, length_in_words)
            summary = await self.query_chat(messages[1]['content'], messages[0]['content'], loop)
            return summary
        except Exception as e:
            logger.error(f'Failed to summarize text: {e}')
            return None

    async def generate_scene_content(self, messages, loop):
       try:
            summary_prompt = ''.join(generate_prompt_parts(messages))
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
                   prompt = f"{summary_prompt} \n\n {self.summarize_text(generated_scene, length_in_words=length_in_words, loop=loop)} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the scene specification which are missing from the previously generated scene and are the most relevant. Include details from the previous scene as needed. If a previous scene summary exists include details from it as needed.\n\n      - Step 2: Write a new, denser scene of identical length which covers every entity and detail from the previous scene plus the missing entities.\n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous scene\n      - Faithful: present in the scene specification and prior scene\n      - Anywhere: located anywhere in the scene specification and prior scene\n\n      Guidelines:\n      - The first scene should be long (4-5 sentences, approx. 120 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous scene to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The scenes should become highly dense and concise yet self-contained, e.g., easily understood without the scene specification.\n\n      - Missing entities can appear anywhere in the new scene.\n\n      - Never drop entities from the previous scene. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each scene.\n      > Write the missing entities in missing_entities\n      > Write the scene in denser_scene\n      > Repeat the steps {num_passes} times per instructions above"

                   if previous_scene:
                      prompt += f'{self.prompt_constructor.prev_scene_intro}\"\"\"{previous_scene}\"\"\"'
                   if prev_scene_summary:
                        prompt += f'\n\nPrevious scene summary: \"\"\"{prev_scene_summary}\"\"\"'
                   if retrieved_context:
                      prompt += f"\n\nRetrieved context:\n{retrieved_context}"


                result = await self.query_chat(prompt, system_message, loop)

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
def generate_prompt_parts(messages):
  for message in messages:
    yield message['content']
