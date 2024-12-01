import sys
import time
import re
import json
import os
from datetime import datetime

import openai
from joblib import Memory
from loguru import logger
from omegaconf import DictConfig
from openai import OpenAIError
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_fixed,
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
    client = openai.OpenAI(
        api_key=llm_config.glhf_auth_token,
        base_url="https://glhf.chat/api/openai/v1",
    )

    messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]

    start = datetime.now()
    final_response = ""

    try:
        response = client.chat.completions.create(
            model=llm_config.model,
            messages=messages,
        )
        final_response = response.choices[0].message.content

    except OpenAIError as exception:
        raise AppUsageException(str(exception)) from exception
    took = datetime.now() - start

    logger.debug(f"{system=}")
    logger.debug(f"{prompt=}")
    logger.debug(f"{took=}")
    logger.debug("\n---- RESPONSE:")
    logger.debug(f"{final_response=}")

    return final_response


class StoryAgent:
    def __init__(self, llm_config, prompt_engine=None, form='novel', n_crop_previous=400):
        if prompt_engine is None:
            import prompts
            self.prompt_engine = prompts
        else:
            self.prompt_engine = prompt_engine

        self.form = form
        self.llm_config = llm_config
        self.n_crop_previous = n_crop_previous

    def query_chat(self, messages, retries=3):
        prompt = ''.join(generate_prompt_parts(messages))
        system_message = messages[0]['content']

        combined_prompt = f"{system_message}\n### USER: {prompt}"

        result = make_call(system_message, combined_prompt, self.llm_config)
        return result

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

        for field in self.prompt_engine.book_spec_fields:
            while not spec_dict[field]:
                messages = self.prompt_engine.missing_book_spec_messages(field, text_spec)
                missing_part = self.query_chat(messages)
                key, sep, value = missing_part.partition(':')
                if key.lower().strip() == field.lower().strip():
                    spec_dict[field] = value.strip()
        text_spec = f"Title: {title}\n" + "\n".join(f"{key}: {value}" for key, value in spec_dict.items())

        return messages, text_spec

    def enhance_book_spec(self, book_spec):
        messages = self.prompt_engine.enhance_book_spec_messages(book_spec, self.form)
        enhanced_spec = self.query_chat(messages)

        spec_dict_old = self.parse_book_spec(book_spec)
        spec_dict_new = self.parse_book_spec(enhanced_spec)

        spec_dict_merged = spec_dict_old.copy()
        spec_dict_merged.update({k: v for k, v in spec_dict_new.items() if v})

        enhanced_spec = "\n".join(f"{key}: {value}" for key, value in spec_dict_merged.items())

        return messages, enhanced_spec

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
            act = self.query_chat(messages)
            if act:
                act_dict = Plan.parse_act(act)
                while len(act_dict['chapters']) < 2:
                    act = self.query_chat(messages)
                    act_dict = Plan.parse_act(act)
                else:
                    plan[act_num] = act_dict
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
        messages = self.prompt_engine.scene_messages(scene, scene_number, chapter_number, text_plan, self.form)
        if previous_scene:
            previous_scene = utils.keep_last_n_words(previous_scene, n=self.n_crop_previous)
            messages[1]['content'] += f'{self.prompt_engine.prev_scene_intro}\"\"\"{previous_scene}\"\"\"'
        generated_scene = self.query_chat(messages)
        generated_scene = self.prepare_scene_text(generated_scene)
        logger.info(f"Generated Scene {scene_number} in Chapter {chapter_number}:\n{generated_scene}")
        return messages, generated_scene

    def continue_a_scene(self, scene, scene_number, chapter_number, plan, current_scene=None):
        text_plan = Plan.plan_2_str(plan)
        messages = self.prompt_engine.scene_messages(scene, scene_number, chapter_number, text_plan, self.form)
        if current_scene:
            current_scene = utils.keep_last_n_words(current_scene, n=self.n_crop_previous)
            messages[1]['content'] += f'{self.prompt_engine.cur_scene_intro}\"\"\"{current_scene}\"\"\"'

        generated_scene = self.query_chat(messages)
        generated_scene = self.prepare_scene_text(generated_scene)
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

    if last_role != 'assistant':
        yield '\n### ASSISTANT:'
















































