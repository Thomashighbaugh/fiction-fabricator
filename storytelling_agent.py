# goat_storytelling_agent/storytelling_agent.py
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
    wait_exponential,
)

import utils
from plan import Plan
from classes import AppUsageException


memory = Memory(".joblib_cache", verbose=0)


def log_retry(state):
    message = f"Tenacity retry {state.fn.__name__}: {state.attempt_number=}, {state.idle_for=}, {state.seconds_since_start=}"
    if state.attempt_number < 1:
        logger.warning(message)
    else:
        logger.exception(message)


@memory.cache()
@retry(
    wait=wait_exponential(multiplier=2, min=10, max=60),
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
    try:
        response = client.chat.completions.create(
            model=llm_config.model,
            messages=messages,
        )

    except OpenAIError as exception:
        raise AppUsageException(str(exception)) from exception
    took = datetime.now() - start

    chat_response = response.choices[0].message.content.strip()

    logger.debug(f"{system=}")
    logger.debug(f"{prompt=}")
    logger.debug(f"{took=}")
    logger.debug("\n---- RESPONSE:")
    logger.debug(f"{chat_response=}")

    return chat_response


class StoryAgent:
    def __init__(self, llm_config, prompt_engine=None, form='novel',
                 n_crop_previous=400):

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
        if "\"\"\"" in text_spec[:int(len(text_spec)/2)]:
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

    def init_book_spec(self, topic):
        messages = self.prompt_engine.init_book_spec_messages(topic, self.form)
        text_spec = self.query_chat(messages)
        spec_dict = self.parse_book_spec(text_spec)

        text_spec = "\n".join(f"{key}: {value}"
                              for key, value in spec_dict.items())

        for field in self.prompt_engine.book_spec_fields:
            while not spec_dict[field]:
                messages = self.prompt_engine.missing_book_spec_messages(
                    field, text_spec)
                missing_part = self.query_chat(messages)
                key, sep, value = missing_part.partition(':')
                if key.lower().strip() == field.lower().strip():
                    spec_dict[field] = value.strip()
        text_spec = "\n".join(f"{key}: {value}"
                              for key, value in spec_dict.items())
        return messages, text_spec


    def enhance_book_spec(self, book_spec):
        messages = self.prompt_engine.enhance_book_spec_messages(
            book_spec, self.form)
        text_spec = self.query_chat(messages)
        spec_dict_old = self.parse_book_spec(book_spec)
        spec_dict_new = self.parse_book_spec(text_spec)

        for field in self.prompt_engine.book_spec_fields:
            if not spec_dict_new[field]:
                spec_dict_new[field] = spec_dict_old[field]

        text_spec = "\n".join(f"{key}: {value}"
                              for key, value in spec_dict_new.items())
        return messages, text_spec

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
            messages = self.prompt_engine.enhance_plot_chapters_messages(
                act_num, text_plan, book_spec, self.form)
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
        for index, act in enumerate(plan, start=1):
            text_act, chapters = Plan.act_2_str(plan, index)
            act_chapters[index] = chapters
            messages = self.prompt_engine.split_chapters_into_scenes_messages(
                index, text_act, self.form)
            act_scenes = self.query_chat(messages)
            act['act_scenes'] = act_scenes
            all_messages.append(messages)

        for index, act in enumerate(plan, start=1):
            act_scenes = act['act_scenes']
            act_scenes = re.split(r'Chapter (\d+)', act_scenes.strip())

            act['chapter_scenes'] = {}
            chapters = [text.strip() for text in act_scenes[:]
                        if (text and text.strip())]
            current_chapter = None
            merged_chapters = {}
            for snippet in chapters:
                if snippet.isnumeric():
                    chapter_number = int(snippet)
                    if chapter_number != current_chapter:
                        current_chapter = snippet
                        merged_chapters[chapter_number] = ''
                    continue
                if merged_chapters:
                    merged_chapters[chapter_number] += snippet
            chapter_numbers = list(merged_chapters.keys()) if len(
                merged_chapters) <= len(act_chapters[index]) else act_chapters[index]
            merged_chapters = {chapter_number: merged_chapters[chapter_number]
                               for chapter_number in chapter_numbers}
            for chapter_number, chapter in merged_chapters.items():
                scenes = re.split(r'Scene \d+.{0,10}?:', chapter)
                scenes = [text.strip() for text in scenes[1:]
                          if (text and (len(text.split()) > 3))]
                if not scenes:
                    continue
                act['chapter_scenes'][chapter_number] = scenes
        return all_messages, plan

    @staticmethod
    def prepare_scene_text(text):
        lines = text.split('\n')
        chapter_ids = [i for i in range(5)
                  if 'Chapter ' in lines[i]]
        if chapter_ids:
            lines = lines[chapter_ids[-1]+1:]
        scene_ids = [i for i in range(5)
                  if 'Scene ' in lines[i]]
        if scene_ids:
            lines = lines[scene_ids[-1]+1:]

        placeholder_index = None
        for i in range(len(lines)):
            if lines[i].startswith('Chapter ') or lines[i].startswith('Scene '):
                placeholder_index = i
                break
        if placeholder_index is not None:
            lines = lines[:i]

        text = '\n'.join(lines)
        return text

    def write_a_scene(
            self, scene, scene_number, chapter_number, plan, previous_scene=None):
        text_plan = Plan.plan_2_str(plan)
        messages = self.prompt_engine.scene_messages(
            scene, scene_number, chapter_number, text_plan, self.form)
        if previous_scene:
            previous_scene = utils.keep_last_n_words(previous_scene,
                                                     n=self.n_crop_previous)
            messages[1]['content'] += f'{self.prompt_engine.prev_scene_intro}\"\"\"{previous_scene}\"\"\"'
        generated_scene = self.query_chat(messages)
        generated_scene = self.prepare_scene_text(generated_scene)
        return messages, generated_scene

    def continue_a_scene(self, scene, scene_number, chapter_number,
                         plan, current_scene=None):
        text_plan = Plan.plan_2_str(plan)
        messages = self.prompt_engine.scene_messages(
            scene, scene_number, chapter_number, text_plan, self.form)
        if current_scene:
            current_scene = utils.keep_last_n_words(current_scene,
                                                    n=self.n_crop_previous)
            messages[1]['content'] += f'{self.prompt_engine.cur_scene_intro}\"\"\"{current_scene}\"\"\"'
        generated_scene = self.query_chat(messages)
        generated_scene = self.prepare_scene_text(generated_scene)
        return messages, generated_scene

    def generate_story(self, topic):
        _, book_spec = self.init_book_spec(topic)
        _, book_spec = self.enhance_book_spec(book_spec)
        _, plan = self.create_plot_chapters(book_spec)
        _, plan = self.enhance_plot_chapters(book_spec, plan)
        _, plan = self.split_chapters_into_scenes(plan)

        form_text = []
        for act in plan:
            for chapter_number, chapter in act['chapter_scenes'].items():
                scene_number = 1
                for scene in chapter:
                    previous_scene = form_text[-1] if form_text else None
                    _, generated_scene = self.write_a_scene(
                        scene, scene_number, chapter_number, plan,
                        previous_scene=previous_scene)
                    form_text.append(generated_scene)
                    scene_number += 1
        return form_text


def generate_prompt_parts(
        messages, include_roles=set(('user', 'assistant', 'system'))):
    last_role = None
    messages = [message for message in messages if message['role'] in include_roles]
    for index, message in enumerate(messages):
        new_line = "\n" if index > 0 else ""
        if message['role'] == 'system':
            if index > 0 and last_role not in (None, "system"):
                raise ValueError("system message not at start")
            yield f"{message['content']}"
        elif message['role'] == 'user':
            yield f"{new_line}### USER: {message['content']}"
        elif message['role'] == 'assistant':
            yield f"{new_line}### ASSISTANT: {message['content']}"
        last_role = message['role']
    if last_role != 'assistant':
        yield '\n### ASSISTANT:'
      
