import sys
import time
import re
import json
import os
from datetime import datetime

import ollama
from joblib import Memory
from loguru import logger
from omegaconf import DictConfig
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_fixed,
    stop_after_delay,
)

import utils
from plan import Plan
from classes import AppUsageException
import config

memory = Memory(".joblib_cache", verbose=0)

def log_retry(state):
    message = f"Tenacity retry {state.fn.__name__}: {state.attempt_number=}, {state.idle_for=}, {state.seconds_since_start=}"

    logger.exception(message)

@memory.cache()
@retry(
    wait=wait_fixed(config.RETRY_WAIT),
    stop=stop_after_attempt(3),
    before_sleep=log_retry,
    retry=retry_if_not_exception_type(AppUsageException),
)
def make_call(system: str, prompt: str, llm_config: DictConfig) -> str:
    messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]

    start = datetime.now()
    final_response = ""

    try:
        response = ollama.chat(
            model=llm_config.model,
            messages=messages,
            timeout = config.TIMEOUT,
        )
        final_response = response['message']['content']

    except Exception as exception:
        raise AppUsageException(str(exception)) from exception
    took = datetime.now() - start

    logger.debug(f"{system=}")
    logger.debug(f"{prompt=}")
    logger.debug(f"{took=}")
    logger.debug("\n---- RESPONSE:")
    logger.debug(f"{final_response=}")

    return final_response

class StoryAgent:
    def __init__(self, llm_config, prompt_engine=None, form='novel', n_crop_previous=400, max_combined_length=1500):
        if prompt_engine is None:
            import prompts
            self.prompt_engine = prompts
        else:
            self.prompt_engine = prompt_engine

        self.form = form
        self.llm_config = llm_config
        self.n_crop_previous = n_crop_previous
        self.max_combined_length = max_combined_length
        self.story_context = {
            "plot_summary": "",
            "characters": {},
            "events": [],
            "theme": "", #we will have the model specify the theme later, for now use ""
            "scene_summaries": []
        }

    def query_chat(self, messages, retries=3):
        prompt = ''.join(generate_prompt_parts(messages))
        system_message = messages[0]['content']

        combined_prompt = f"{system_message}\n### USER: {prompt}"

        result = make_call(system_message, combined_prompt, self.llm_config)
        return result

    def _summarize_text(self, text, length_in_words=60):
        messages = self.prompt_engine.summarization_messages(text, length_in_words)
        summary = self.query_chat(messages)
        return summary

    def parse_book_spec(self, text_spec):
        fields = self.prompt_engine.book_spec_fields
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

    def init_book_spec(self, topic, title):
        messages = self.prompt_engine.init_book_spec_messages(topic, self.form)
        text_spec = self.query_chat(messages)
        spec_dict = self.parse_book_spec(text_spec)

        text_spec = f"Title: {title}\n" + "\n".join(f"{key}: {value}" for key, value in spec_dict.items())
        self.story_context['theme'] = spec_dict['Themes']

        for field in self.prompt_engine.book_spec_fields:
            while not spec_dict[field]:
                messages = self.prompt_engine.missing_book_spec_messages(field, text_spec)
                missing_part = self.query_chat(messages)
                key, sep, value = missing_part.partition(':')
                if key.lower().strip() == field.lower().strip():
                    spec_dict[field] = value.strip()
        text_spec = f"Title: {title}\n" + "\n".join(f"{key}: {value}" for key, value in spec_dict.items())

        # Initialize Characters in story_context from book spec
        characters = spec_dict.get('Characters', '').split(',')
        for char in characters:
            char = char.strip()
            if char:
               self.story_context['characters'][char] = {
                   'description':'',
                   'relationships':[],
                   'motivation':''
                }

        return messages, text_spec

    def enhance_book_spec(self, book_spec):

        summary_messages = self.prompt_engine.enhance_book_spec_messages(book_spec, self.form)
        summary_prompt = ''.join(generate_prompt_parts(summary_messages))
        system_message = summary_messages[0]['content']

        enhanced_spec = book_spec
        num_passes = 5
        length_in_words = 80

        for i in range(num_passes):
             prompt = f"{summary_prompt} \n\n {enhanced_spec} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the book specification which are missing from the previously generated summary and are the most relevant.\n\n      - Step 2: Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the missing entities.\n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous summary\n      - Faithful: present in the book specification\n      - Anywhere: located anywhere in the book specification\n\n      Guidelines:\n      - The first summary should be long (4-5 sentences, approx. 80 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous summary to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the book specification.\n\n      - Missing entities can appear anywhere in the new summary.\n\n      - Never drop entities from the previous summary. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each summary.\n      > Write the missing entities in missing_entities\n      > Write the summary in denser_summary\n      > Repeat the steps {num_passes} times per instructions above"

             if len(prompt) > self.max_combined_length:
                prompt = f"{summary_prompt} \n\n {self._summarize_text(enhanced_spec)} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the book specification which are missing from the previously generated summary and are the most relevant.\n\n      - Step 2: Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the missing entities.\n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous summary\n      - Faithful: present in the book specification\n- Anywhere: located anywhere in the book specification\n\n      Guidelines:\n      - The first summary should be long (4-5 sentences, approx. 80 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous summary to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the book specification.\n\n      - Missing entities can appear anywhere in the new summary.\n\n      - Never drop entities from the previous summary. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each summary.\n      > Write the missing entities in missing_entities\n      > Write the summary in denser_summary\n      > Repeat the steps {num_passes} times per instructions above"
             result = make_call(system_message, prompt, self.llm_config)
             if result:
                try:
                    start_missing = result.find("missing_entities:") + len("missing_entities:")
                    end_missing = result.find("denser_summary:")
                    missing_entities = result[start_missing:end_missing].strip()

                    start_summary = result.find("denser_summary:") + len("denser_summary:")
                    denser_summary = result[start_summary:].strip()

                    enhanced_spec = denser_summary
                except Exception as e:
                    logger.warning(f'Failed to parse enhance book spec response: {e}, skipping to next step, raw response was:\n{result}')
                    continue
             else:
                logger.warning(f'Failed to get a response from the model, skipping to next step')
                continue

        enhanced_spec = f"Title: {book_spec.splitlines()[0].split(': ')[1]}\n" + enhanced_spec

        return summary_messages, enhanced_spec

    def create_plot_chapters(self, book_spec):
        messages = self.prompt_engine.create_plot_chapters_messages(book_spec, self.form)
        plan = []
        while not plan:
            text_plan = self.query_chat(messages)
            if text_plan:
                plan = Plan.parse_text_plan(text_plan)
        return messages, plan

    def enhance_plot_chapters(self, book_spec, plan):
        text_plan = Plan.plan_2_str(plan)
        all_messages = []
        for act_num in range(3):
            messages = self.prompt_engine.enhance_plot_chapters_messages(act_num, text_plan, book_spec, self.form)

            summary_prompt = ''.join(generate_prompt_parts(messages))
            system_message = messages[0]['content']

            enhanced_act = ''
            num_passes = 5
            length_in_words = 80

            for i in range(num_passes):
                prompt = f"{summary_prompt} \n\n {enhanced_act} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the act which are missing from the previously generated summary and are the most relevant.\n\n      - Step 2: Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the missing entities.\n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous summary\n      - Faithful: present in the act description\n      - Anywhere: located anywhere in the act description\n\n      Guidelines:\n      - The first summary should be long (4-5 sentences, approx. 80 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous summary to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the act description.\n\n      - Missing entities can appear anywhere in the new summary.\n\n      - Never drop entities from the previous summary. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each summary.\n      > Write the missing entities in missing_entities\n      > Write the summary in denser_summary\n      > Repeat the steps {num_passes} times per instructions above"

                if len(prompt) > self.max_combined_length:
                    prompt = f"{summary_prompt} \n\n {self._summarize_text(enhanced_act)} \n\n  You must repeat the following 2 steps {num_passes} times.\

\n      - Step 1: Identify 1-3 informative entities from the act which are missing from the previously generated summary and are the most relevant.\n\n      - Step 2: Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the missing entities.\n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous summary\n      - Faithful: present in the act description\n      - Anywhere: located anywhere in the act description\n\n      Guidelines:\n      - The first summary should be long (4-5 sentences, approx. 80 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous summary to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the act description.\n\n      - Missing entities can appear anywhere in the new summary.\n\n      - Never drop entities from the previous summary. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each summary.\n      > Write the missing entities in missing_entities\n      > Write the summary in denser_summary\n      > Repeat the steps {num_passes} times per instructions above"

                result = make_call(system_message, prompt, self.llm_config)

                if result:
                    try:
                        start_missing = result.find("missing_entities:") + len("missing_entities:")
                        end_missing = result.find("denser_summary:")
                        missing_entities = result[start_missing:end_missing].strip()

                        start_summary = result.find("denser_summary:") + len("denser_summary:")
                        denser_summary = result[start_summary:].strip()

                        enhanced_act = denser_summary
                    except Exception as e:
                        logger.warning(f'Failed to parse enhance plot chapter act response: {e}, skipping to next step, raw response was:\n{result}')
                        continue
                else:
                   logger.warning(f'Failed to get a response from the model, skipping to next step')
                   continue

            if enhanced_act:
                try:
                    act_dict = Plan.parse_act(enhanced_act)
                    while len(act_dict['chapters']) < 2:

                        prompt = f"{summary_prompt} \n\n {enhanced_act} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the act which are missing from the previously generated summary and are the most relevant.\n\n      - Step 2: Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the missing entities.\n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous summary\n      - Faithful: present in the act description\n      - Anywhere: located anywhere in the act description\n\n      Guidelines:\n      - The first summary should be long (4-5 sentences, approx. 80 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous summary to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the act description.\n\n      - Missing entities can appear anywhere in the new summary.\n\n      - Never drop entities from the previous summary. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each summary.\n      > Write the missing entities in missing_entities\n      > Write the summary in denser_summary\n      > Repeat the steps {num_passes} times per instructions above"

                        if len(prompt) > self.max_combined_length:
                            prompt = f"{summary_prompt} \n\n {self._summarize_text(enhanced_act)} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the act which are missing from the previously generated summary and are the most relevant.\n\n      - Step 2: Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the missing entities.\n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous summary\n      - Faithful: present in the act description\n      - Anywhere: located anywhere in the act description\n\n      Guidelines:\n      - The first summary should be long (4-5 sentences, approx. 80 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous summary to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the act description.\n\n      - Missing entities can appear anywhere in the new summary.\n\n      - Never drop entities from the previous summary. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each summary.\n      > Write the missing entities in missing_entities\n      > Write the summary in denser_summary\n      > Repeat the steps {num_passes} times per instructions above"

                        result = make_call(system_message, prompt, self.llm_config)
                        if result:
                            try:

                                start_missing = result.find("missing_entities:") + len("missing_entities:")
                                end_missing = result.find("denser_summary:")
                                missing_entities = result[start_missing:end_missing].strip()

                                start_summary = result.find("denser_summary:") + len("denser_summary:")
                                denser_summary = result[start_summary:].strip()

                                enhanced_act = denser_summary

                            except Exception as e:
                                logger.warning(f'Failed to parse enhance plot chapter while loop response: {e}, skipping to next step, raw response was:\n{result}')
                                continue
                        else:
                            logger.warning(f'Failed to get a response from the model, skipping to next step')
                            continue
                    else:
                        plan[act_num] = act_dict
                except Exception as e:
                    logger.warning(f'Failed to parse act dict in enhance plot chapters response: {e}, skipping to next step')
                    continue
                text_plan = Plan.plan_2_str(plan)
            all_messages.append(messages)
        return all_messages, plan

    def split_chapters_into_scenes(self, plan):
        all_messages = []
        act_chapters = {}
        for i, act in enumerate(plan, start=1):
            text_act, chs = Plan.act_2_str(plan, i)
            act_chapters[i] = chs
            messages = self.prompt_engine.split_chapters_into_scenes_messages(i, text_act, self.form)
            act_scenes = self.query_chat(messages)
            act['act_scenes'] = act_scenes
            all_messages.append(messages)

        for i, act in enumerate(plan, start=1):
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

    @staticmethod
    def prepare_scene_text(text):
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

    def write_a_scene(self, scene, scene_number, chapter_number, plan, previous_scene=None):
        text_plan = Plan.plan_2_str(plan)

        #Add the plot summary to context.
        self.story_context['plot_summary'] = self._summarize_text(text_plan, 60)

        #use previous scene summaries if they exist
        if self.story_context['scene_summaries']:
            prev_scene_summary = self.story_context['scene_summaries'][-1]
        else:
            prev_scene_summary = None

        messages = self.prompt_engine.scene_messages(
            scene,
            scene_number,
            chapter_number,
            text_plan,
            self.form,
            plot_summary = self.story_context['plot_summary'],
            characters = self.story_context['characters'],
            events = self.story_context['events'],
            theme = self.story_context['theme'],
            prev_scene_summary = prev_scene_summary
        )

        summary_prompt = ''.join(generate_prompt_parts(messages))
        system_message = messages[0]['content']

        generated_scene = ''
        num_passes = 3 # reduced for now to save on tokens
        length_in_words = 120

        if previous_scene:
            previous_scene = utils.keep_last_n_words(previous_scene, n=self.n_crop_previous)

        for i in range(num_passes):
            prompt = f"{summary_prompt} \n\n {generated_scene} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the scene specification which are missing from the previously generated scene and are the most relevant. Include details from the previous scene as needed. If a previous scene summary exists include details from it as needed.\n\n      - Step 2: Write a new, denser scene of identical length which covers every entity and detail from the previous scene plus the missing entities. \n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous scene\n      - Faithful: present in the scene specification and prior scene\n      - Anywhere: located anywhere in the scene specification and prior scene\n\n      Guidelines:\n      - The first scene should be long (4-5 sentences, approx. 120 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous scene to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The scenes should become highly dense and concise yet self-contained, e.g., easily understood without the scene specification.\n\n      - Missing entities can appear anywhere in the new scene.\n\n      - Never drop entities from the previous scene. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each scene.\n      > Write the missing entities in missing_entities\n      > Write the scene in denser_scene\n      > Repeat the steps {num_passes} times per instructions above"

            if previous_scene:
                 prompt += f'{self.prompt_engine.prev_scene_intro}\"\"\"{previous_scene}\"\"\"'

            if prev_scene_summary:
                prompt += f'\n\nPrevious scene summary: \"\"\"{prev_scene_summary}\"\"\"'


            if len(prompt) > self.max_combined_length:
                prompt = f"{summary_prompt} \n\n {self._summarize_text(generated_scene, length_in_words=length_in_words)} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the scene specification which are missing from the previously generated scene and are the most relevant. Include details from the previous scene as needed. If a previous scene summary exists include details from it as needed.\n\n      - Step 2: Write a new, denser scene of identical length which covers every entity and detail from the previous scene plus the missing entities.\n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous scene\n      - Faithful: present in the scene specification and prior scene\n      - Anywhere: located anywhere in the scene specification and prior scene\n\n      Guidelines:\n      - The first scene should be long (4-5 sentences, approx. 120 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous scene to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The scenes should become highly dense and concise yet self-contained, e.g., easily understood without the scene specification.\n\n      - Missing entities can appear anywhere in the new scene.\n\n      - Never drop entities from the previous scene. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each scene.\n      > Write the missing entities in missing_entities\n      > Write the scene in denser_scene\n      > Repeat the steps {num_passes} times per instructions above"

            if previous_scene:
                 prompt += f'{self.prompt_engine.prev_scene_intro}\"\"\"{previous_scene}\"\"\"'

            if prev_scene_summary:
                prompt += f'\n\nPrevious scene summary: \"\"\"{prev_scene_summary}\"\"\"'

            result = make_call(system_message, prompt, self.llm_config)
            if result:
                try:

                    start_missing = result.find("missing_entities:") + len("missing_entities:")
                    end_missing = result.find("denser_scene:")
                    missing_entities = result[start_missing:end_missing].strip()

                    start_scene = result.find("denser_scene:") + len("denser_scene:")
                    denser_scene = result[start_scene:].strip()

                    generated_scene = denser_scene
                except Exception as e:
                   logger.warning(f'Failed to parse write a scene response: {e}, skipping to next step, raw response was:\n{result}')
                   continue
            else:
                logger.warning(f'Failed to get a response from the model, skipping to next step')
                continue

        # Update events in story context
        event_summary = self._summarize_text(generated_scene, length_in_words=20)
        self.story_context['events'].append(event_summary)

        #Summarize the scene and add to story_context
        scene_summary = self._summarize_text(generated_scene, length_in_words=60)
        self.story_context['scene_summaries'].append(scene_summary)

        generated_scene = self.prepare_scene_text(generated_scene)
        logger.info(f"Generated Scene {scene_number} in Chapter {chapter_number}:\n{generated_scene}")
        return messages, generated_scene

    def continue_a_scene(self, scene, scene_number, chapter_number, plan, current_scene=None):
        text_plan = Plan.plan_2_str(plan)

        #Add the plot summary to context.
        self.story_context['plot_summary'] = self._summarize_text(text_plan, 60)

        #use previous scene summaries if they exist
        if self.story_context['scene_summaries']:
            prev_scene_summary = self.story_context['scene_summaries'][-1]
        else:
            prev_scene_summary = None

        messages = self.prompt_engine.scene_messages(
            scene,
            scene_number,
            chapter_number,
            text_plan,
            self.form,
            plot_summary = self.story_context['plot_summary'],
            characters = self.story_context['characters'],
            events = self.story_context['events'],
            theme = self.story_context['theme'],
            prev_scene_summary = prev_scene_summary
        )

        summary_prompt = ''.join(generate_prompt_parts(messages))
        system_message = messages[0]['content']

        generated_scene = ''
        num_passes = 3 # reduced for now to save on tokens
        length_in_words = 120

        if current_scene:
            current_scene = utils.keep_last_n_words(current_scene, n=self.n_crop_previous)

        for i in range(num_passes):
             prompt = f"{summary_prompt} \n\n {generated_scene} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the scene specification which are missing from the previously generated scene and are the most relevant. Include details from the current scene as needed. If a previous scene summary exists include details from it as needed.\n\n      - Step 2: Write a new, denser scene of identical length which covers every entity and detail from the previous scene plus the missing entities.\n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous scene\n      - Faithful: present in the scene specification and current scene\n      - Anywhere: located anywhere in the scene specification and current scene\n\n      Guidelines:\n      - The first scene should be long (4-5 sentences, approx. 120 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous scene to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The scenes should become highly dense and concise yet self-contained, e.g., easily understood without the scene specification.\n\n      - Missing entities can appear anywhere in the new scene.\n\n      - Never drop entities from the previous scene. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each scene.\n      > Write the missing entities in missing_entities\n      > Write the scene in denser_scene\n      > Repeat the steps {num_passes} times per instructions above"

             if current_scene:
                prompt += f'{self.prompt_engine.cur_scene_intro}\"\"\"{current_scene}\"\"\"'

             if prev_scene_summary:
                 prompt += f'\n\nPrevious scene summary: \"\"\"{prev_scene_summary}\"\"\"'

             if len(prompt) > self.max_combined_length:
                 prompt = f"{summary_prompt} \n\n {self._summarize_text(generated_scene, length_in_words=length_in_words)} \n\n  You must repeat the following 2 steps {num_passes} times.\n\n      - Step 1: Identify 1-3 informative entities from the scene specification which are missing from the previously generated scene and are the most relevant. Include details from the current scene as needed. If a previous scene summary exists include details from it as needed.\n\n      - Step 2: Write a new, denser scene of identical length which covers every entity and detail from the previous scene plus the missing entities.\n\n      A Missing Entity is:\n\n      - Relevant: to the main story\n      - Specific: descriptive yet concise (5 words or fewer)\n      - Novel: not in the previous scene\n      - Faithful: present in the scene specification and current scene\n      - Anywhere: located anywhere in the scene specification and current scene\n\n      Guidelines:\n      - The first scene should be long (4-5 sentences, approx. 120 words) yet highly non-specific, containing little information beyond the entities marked as missing.\n\n      - Use overly verbose language and fillers (e.g. \"this article discusses\") to reach approximately {length_in_words} words.\n\n      - Make every word count: re-write the previous scene to improve flow and make space for additional entities.\n\n      - Make space with fusion, compression, and removal of uninformative phrases like \"the article discusses\"\n\n      - The scenes should become highly dense and concise yet self-contained, e.g., easily understood without the scene specification.\n\n      - Missing entities can appear anywhere in the new scene.\n\n      - Never drop entities from the previous scene. If space cannot be made, add fewer new entities.\n\n      > Remember to use the exact same number of words for each scene.\n      > Write the missing entities in missing_entities\n      > Write the scene in denser_scene\n      > Repeat the steps {num_passes} times per instructions above"


             if current_scene:
                prompt += f'{self.prompt_engine.cur_scene_intro}\"\"\"{current_scene}\"\"\"'

             if prev_scene_summary:
                 prompt += f'\n\nPrevious scene summary: \"\"\"{prev_scene_summary}\"\"\"'

             result = make_call(system_message, prompt, self.llm_config)
             if result:
                 try:

                    start_missing = result.find("missing_entities:") + len("missing_entities:")
                    end_missing = result.find("denser_scene:")
                    missing_entities = result[start_missing:end_missing].strip()

                    start_scene = result.find("denser_scene:") + len("denser_scene:")
                    denser_scene = result[start_scene:].strip()

                    generated_scene = denser_scene
                 except Exception as e:
                    logger.warning(f'Failed to parse continue a scene response: {e}, skipping to next step, raw response was:\n{result}')
                    continue
             else:
                logger.warning(f'Failed to get a response from the model, skipping to next step')
                continue

        generated_scene = self.prepare_scene_text(generated_scene)

        #Summarize the scene and add to story_context
        scene_summary = self._summarize_text(generated_scene, length_in_words=60)
        self.story_context['scene_summaries'].append(scene_summary)

        logger.info(f"Enhanced Scene {scene_number} in Chapter {chapter_number}:\n{generated_scene}")
        return messages, generated_scene

    def generate_title(self, topic):
        messages = self.prompt_engine.title_generation_messages(topic)
        response = self.query_chat(messages)

        # Extract title using regex (more robust)
        match = re.match(r"^(.*?)(?:\n\n|$)", response) # Match everything up to \n\n or end of string
        if match:
            title = match.group(1).strip()
        else:
            title = "Untitled Story"  # Default if no title is found

        return title
def generate_prompt_parts(messages, include_roles=set(('user', 'assistant', 'system'))):
    last_role = None
    messages = [message for message in messages if message['role'] in include_roles]
    for i, message in enumerate(messages):
        nl = "\n" if i > 0 else ""

        if message['role'] == 'system':
            if i > 0 and last_role not in (None, "system"):
                raise ValueError("system message not at start")
            yield f"{message['content']}"
        elif message['role'] == 'user':
            yield f"{nl}### USER: {message['content']}"
        elif message['role'] == 'assistant':
            yield f"{nl}### ASSISTANT: {message['content']}"
        last_role = message['role']
