#!/usr/bin/python3
import argparse
import time
import datetime
import os
import sys
import json
import dotenv
import termcolor

import Writer.Config
import Writer.Interface.Wrapper
import Writer.PrintUtils
import Writer.Scrubber
import Writer.Statistics
import Writer.OutlineGenerator
import Writer.Chapter.ChapterGenerator
import Writer.StoryInfo
import Writer.NovelEditor
import Writer.Prompts
from Writer.NarrativeContext import NarrativeContext

def get_ollama_models(logger):
    try:
        import ollama
        logger.Log("Querying Ollama for local models...", 1)
        models_data = ollama.list().get("models", [])
        available_models = [f"ollama://{model.get('name') or model.get('model')}" for model in models_data if model.get('name') or model.get('model')]
        print(f"-> Ollama: Found {len(available_models)} models.")
        return available_models
    except Exception as e:
        logger.Log(f"Could not get Ollama models. (Error: {e})", 6)
        return []

def get_google_models(logger):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("-> Google: GOOGLE_API_KEY not found in .env file. Skipping.")
        return []
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        logger.Log("Querying Google for available Gemini models...", 1)
        available = [f"google://{m.name.replace('models/', '')}" for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"-> Google: Found {len(available)} models.")
        return available
    except Exception as e:
        logger.Log(f"Failed to query Google models. (Error: {e})", 6)
        return []

def get_groq_models(logger):
    if not os.environ.get("GROQ_API_KEY"):
        print("-> Groq: GROQ_API_KEY not found in .env file. Skipping.")
        return []
    try:
        from groq import Groq
        logger.Log("Querying Groq for available models...", 1)
        client = Groq()
        models = client.models.list().data
        print(f"-> Groq: Found {len(models)} models.")
        base_override = os.environ.get("GROQ_API_BASE") or os.environ.get("GROQ_API_BASE_URL")
        if base_override:
            logger.Log(f"GROQ_API_BASE override detected: {base_override}", 2)
        uris = []
        for m in models:
            uris.append(f"groq://{m.id}")
        return uris
    except Exception as e:
        logger.Log(f"Failed to query Groq models. (Error: {e})", 6)
        return []

def get_mistral_models(logger):
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("-> MistralAI: MISTRAL_API_KEY not found in .env file. Skipping.")
        return []
    try:
        from mistralai.client import MistralClient
        logger.Log("Querying MistralAI for available models...", 1)
        client = MistralClient(api_key=api_key)
        models_data = client.list_models().data
        known_chat_prefixes = ['mistral-large', 'mistral-medium', 'mistral-small', 'open-mistral', 'open-mixtral']
        available_models = [f"mistralai://{model.id}" for model in models_data if any(model.id.startswith(prefix) for prefix in known_chat_prefixes)]
        print(f"-> MistralAI: Found {len(available_models)} compatible models.")
        return available_models
    except Exception as e:
        logger.Log(f"Failed to query MistralAI models. (Error: {e})", 6)
        return []

def get_nvidia_models(logger):
    """Reads the user-defined NVIDIA models from config.ini."""
    if not os.environ.get("NVIDIA_API_KEY"):
        logger.Log("NVIDIA provider skipped: NVIDIA_API_KEY not found in environment.", 6)
        return []
    
    logger.Log("Reading manual NVIDIA model list from config.ini...", 1)
    model_list_str = Writer.Config.NVIDIA_AVAILABLE_MODELS
    if not model_list_str:
        logger.Log("NVIDIA provider skipped: No models listed in config.ini under [NVIDIA_SETTINGS] -> 'available_models'.", 6)
        return []
    
    model_names = [name.strip() for name in model_list_str.split(',') if name.strip()]
    available_models = [f"nvidia://{name}" for name in model_names]
    logger.Log(f"Found {len(available_models)} NVIDIA models in config.ini.", 3)
    return available_models

def get_github_models(logger):
    """Returns a static list of available GitHub Marketplace/Azure OpenAI aggregator models (includes Grok)."""
    if not os.environ.get("GITHUB_ACCESS_TOKEN") or not os.environ.get("AZURE_OPENAI_ENDPOINT"):
        logger.Log("GitHub provider skipped: GITHUB_ACCESS_TOKEN or AZURE_OPENAI_ENDPOINT not found in environment.", 6)
        return []

    logger.Log("Loading GitHub model list...", 1)
    
    deployment_names = [
        "openai/o1", "openai/o1-mini", "openai/o1-preview", "openai/gpt-4o-mini", "openai/gpt-4o",
        "deepseek/DeepSeek-V3-0324", "deepseek/DeepSeek-R1",
        "ai21-labs/AI21-Jamba-1.5-Large", "ai21-labs/AI21-Jamba-1.5-Mini",
        "cohere/cohere-command-r", "cohere/cohere-command-r-plus", "cohere/cohere-command-a",
        "mistral-ai/Mistral-Nemo", "mistral-ai/Mistral-Small",
        "mistral-ai/Mistral-Large-2411", "mistral-ai/Codestral-22B-v0.1",
        "meta/Llama-3.2-11B-Vision-Instruct", "meta/Llama-3.2-90B-Vision-Instruct",
        "meta/Llama-3.3-70B-Instruct", "meta/Llama-3.1-8B-Instruct",
        "meta/Llama-3.1-70B-Instruct", "meta/Llama-3.1-405B-Instruct",
        "meta/Llama-3-8B-Instruct", "meta/Llama-3-70B-Instruct",
        "microsoft/Phi-4", "microsoft/Phi-3.5-MoE-instruct",
        "microsoft/Phi-3.5-mini-instruct", "microsoft/Phi-3.5-vision-instruct",
        "microsoft/Phi-3-mini-4k-instruct", "microsoft/Phi-3-mini-128k-instruct",
        "microsoft/Phi-3-small-8k-instruct", "microsoft/Phi-3-small-128k-instruct",
        "microsoft/Phi-3-medium-4k-instruct", "microsoft/Phi-3-medium-128k-instruct",
        "xai/grok-3",
        "core42/jais-30b-chat"
    ]
    
    available_models = [f"github://{name}" for name in deployment_names]
    logger.Log(f"Found {len(available_models)} GitHub models.", 3)
    return available_models

def get_llm_selection_menu_dynamic(logger):
    print("\n--- Querying available models from configured providers... ---")
    all_models = []
    all_models.extend(get_google_models(logger))
    all_models.extend(get_groq_models(logger))
    all_models.extend(get_mistral_models(logger))
    all_models.extend(get_nvidia_models(logger))
    # Additional providers
    try:
        from Writer.LLMUtils import get_cohere_models, get_together_models, get_cerebras_models
        all_models.extend(get_cohere_models(logger))
        all_models.extend(get_together_models(logger))
        all_models.extend(get_cerebras_models(logger))
    except Exception:
        pass
    all_models.extend(get_github_models(logger))
    all_models.extend(get_ollama_models(logger))
    if not all_models:
        logger.Log("No models found from any provider. Please check API keys in .env and model lists in config.ini.", 7)
        return {}
    print("\n--- Fiction Fabricator LLM Selection ---")
    print("Please select the primary model for writing:")
    sorted_models = sorted(all_models)
    for i, model in enumerate(sorted_models):
        print(f"[{i+1}] {model}")
    print("[c] Custom (use settings from config.ini or command-line args)")
    choice = input("> ").strip().lower()
    if choice.isdigit() and 1 <= int(choice) <= len(sorted_models):
        selected_model = sorted_models[int(choice) - 1]
        print(f"Selected: {selected_model}")
        return {'INITIAL_OUTLINE_WRITER_MODEL':selected_model, 'CHAPTER_OUTLINE_WRITER_MODEL':selected_model, 'CHAPTER_STAGE1_WRITER_MODEL':selected_model, 'CHAPTER_STAGE2_WRITER_MODEL':selected_model, 'CHAPTER_STAGE3_WRITER_MODEL':selected_model, 'CHAPTER_STAGE4_WRITER_MODEL':selected_model, 'CHAPTER_REVISION_WRITER_MODEL':selected_model, 'CRITIQUE_LLM':selected_model, 'REVISION_MODEL':selected_model, 'EVAL_MODEL':selected_model, 'INFO_MODEL':selected_model, 'SCRUB_MODEL':selected_model, 'CHECKER_MODEL':selected_model}
    else:
        print("Invalid choice or 'c' selected. Using custom/default configuration.")
        return {}

import os
import json
import time

from src.Writer.Interface.Wrapper import Interface
from src.Writer.NarrativeContext import NarrativeContext
import src.Writer.Config
import src.Writer.PrintUtils
import src.Writer.OutlineGenerator
import src.Writer.Chapter

def select_outline_file(logger):
    """
    Lets the user select an outline file from the Generated_Content/Outlines directory.
    """
    # Correctly determine the project root relative to the current script location
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # src root
    repo_root = os.path.dirname(project_root)
    outlines_dir = os.path.join(repo_root, "Generated_Content", "Outlines")

    if not os.path.exists(outlines_dir) or not os.listdir(outlines_dir):
        logger.Log("No outlines found in Generated_Content/Outlines. Please generate an outline first.", 6)
        return None

    outlines = [f for f in os.listdir(outlines_dir) if f.endswith(".json")]
    if not outlines:
        logger.Log("No .json outline files found in Generated_Content/Outlines.", 6)
        return None

    print("\nPlease select an outline to use for novel generation:")
    for i, outline_file in enumerate(outlines):
        print(f"[{i+1}] {outline_file}")

    while True:
        try:
            choice = input(f"> Enter your choice (1-{len(outlines)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(outlines):
                return os.path.join(outlines_dir, outlines[int(choice) - 1])
            else:
                logger.Log("Invalid selection. Please enter a number from the list.", 6)
        except ValueError:
            logger.Log("Invalid input. Please enter a number.", 6)

def write_novel(outline_file: str, output: str = "", seed: int = Writer.Config.SEED, debug: bool = Writer.Config.DEBUG,
                      chapter_outline_model: str = Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL,
                      chapter_s1_model: str = Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
                      chapter_s2_model: str = Writer.Config.CHAPTER_STAGE2_WRITER_MODEL,
                      chapter_s3_model: str = Writer.Config.CHAPTER_STAGE3_WRITER_MODEL,
                      chapter_s4_model: str = Writer.Config.CHAPTER_STAGE4_WRITER_MODEL,
                      chapter_revision_model: str = Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
                      critique_llm: str = Writer.Config.CRITIQUE_LLM,
                      revision_model: str = Writer.Config.REVISION_MODEL,
                      eval_model: str = Writer.Config.EVAL_MODEL,
                      info_model: str = Writer.Config.INFO_MODEL,
                      scrub_model: str = Writer.Config.SCRUB_MODEL,
                      checker_model: str = Writer.Config.CHECKER_MODEL,
                      chapter_min_revisions: int = Writer.Config.CHAPTER_MIN_REVISIONS,
                      chapter_max_revisions: int = Writer.Config.CHAPTER_MAX_REVISIONS,
                      no_chapter_revision: bool = Writer.Config.CHAPTER_NO_REVISIONS,
                      no_scrub_chapters: bool = Writer.Config.SCRUB_NO_SCRUB,
                      enable_final_edit_pass: bool = Writer.Config.ENABLE_FINAL_EDIT_PASS,
                      scene_generation_pipeline: bool = Writer.Config.SCENE_GENERATION_PIPELINE):
    StartTime = time.time()
    SysLogger = Writer.PrintUtils.Logger()
    SysLogger.Log(f"Welcome to {Writer.Config.PROJECT_NAME}!", 2)

    selected_models = get_llm_selection_menu_dynamic(SysLogger)
    if not selected_models:
        SysLogger.Log("No model was selected or discovered. Using models from config/args.", 4)
    else:
        for key, value in selected_models.items():
            setattr(Writer.Config, key.upper(), value)

    if not outline_file:
        outline_file = select_outline_file(SysLogger)
        if not outline_file:
            return

    # --- Set up file paths ---
    outline_filename_base = os.path.splitext(os.path.basename(outline_file))[0]
    stories_dir = os.path.join(os.path.dirname(outline_file), "..", "Stories")
    os.makedirs(stories_dir, exist_ok=True)
    
    file_name_base = os.path.join(stories_dir, outline_filename_base)
    if Writer.Config.OPTIONAL_OUTPUT_NAME:
        file_name_base = os.path.join(stories_dir, Writer.Config.OPTIONAL_OUTPUT_NAME)

    json_file_path = f"{file_name_base}.json"
    md_file_path = f"{file_name_base}.md"

    # Set the config from the function arguments
    Writer.Config.OPTIONAL_OUTPUT_NAME = output
    Writer.Config.SEED = seed
    Writer.Config.DEBUG = debug
    if not selected_models:
        Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL = chapter_outline_model
        Writer.Config.CHAPTER_STAGE1_WRITER_MODEL = chapter_s1_model
        Writer.Config.CHAPTER_STAGE2_WRITER_MODEL = chapter_s2_model
        Writer.Config.CHAPTER_STAGE3_WRITER_MODEL = chapter_s3_model
        Writer.Config.CHAPTER_STAGE4_WRITER_MODEL = chapter_s4_model
        Writer.Config.CHAPTER_REVISION_WRITER_MODEL = chapter_revision_model
        Writer.Config.CRITIQUE_LLM = critique_llm
        Writer.Config.REVISION_MODEL = revision_model
        Writer.Config.EVAL_MODEL = eval_model
        Writer.Config.INFO_MODEL = info_model
        Writer.Config.SCRUB_MODEL = scrub_model
        Writer.Config.CHECKER_MODEL = checker_model
    Writer.Config.CHAPTER_MIN_REVISIONS = chapter_min_revisions
    Writer.Config.CHAPTER_MAX_REVISIONS = chapter_max_revisions
    Writer.Config.CHAPTER_NO_REVISIONS = no_chapter_revision
    Writer.Config.SCRUB_NO_SCRUB = no_scrub_chapters
    Writer.Config.ENABLE_FINAL_EDIT_PASS = enable_final_edit_pass
    Writer.Config.SCENE_GENERATION_PIPELINE = scene_generation_pipeline

    models_to_load = list(set([Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, Writer.Config.CHAPTER_STAGE2_WRITER_MODEL, Writer.Config.CHAPTER_STAGE3_WRITER_MODEL, Writer.Config.CHAPTER_STAGE4_WRITER_MODEL, Writer.Config.CHAPTER_REVISION_WRITER_MODEL, Writer.Config.CRITIQUE_LLM, Writer.Config.REVISION_MODEL, Writer.Config.EVAL_MODEL, Writer.Config.INFO_MODEL, Writer.Config.SCRUB_MODEL, Writer.Config.CHECKER_MODEL]))
    Interface = Writer.Interface.Wrapper.Interface(models_to_load)

    # --- Resume Logic ---
    narrative_context = None
    start_chapter = 1
    if os.path.exists(json_file_path):
        resume_choice = input(f"Found an existing file for this novel at '{os.path.basename(json_file_path)}'.\nDo you want to resume from the last completed chapter? (y/n): ").strip().lower()
        if resume_choice == 'y':
            try:
                with open(json_file_path, "r", encoding='utf-8') as f:
                    narrative_context_dict = json.load(f)
                    narrative_context = NarrativeContext.from_dict(narrative_context_dict)
                    start_chapter = len(narrative_context.chapters) + 1
                SysLogger.Log(f"Resuming generation from Chapter {start_chapter}.", 5)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                SysLogger.Log(f"Error loading resume file: {e}. Starting a new novel.", 6)
                narrative_context = None
        else:
            SysLogger.Log("User chose not to resume. Starting a new novel.", 3)

    if narrative_context is None:
        try:
            with open(outline_file, "r", encoding='utf-8') as f:
                narrative_context_dict = json.load(f)
                narrative_context = NarrativeContext.from_dict(narrative_context_dict)
            SysLogger.Log("Starting a new novel from outline.", 3)
        except FileNotFoundError:
            SysLogger.Log(f"Error: Outline file not found at {outline_file}", 7)
            return
        except json.JSONDecodeError:
            SysLogger.Log(f"Error: Could not decode JSON from {outline_file}", 7)
            return

    # --- Chapter Generation ---
    SysLogger.Log("Starting Chapter Writing phase...", 2)
    total_chapters = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, SysLogger, narrative_context.base_novel_outline_markdown, Writer.Config.EVAL_MODEL)
    
    if total_chapters > 0 and total_chapters < 100:
        for i in range(start_chapter, total_chapters + 1):
            SysLogger.Log(f"--- Generating Chapter {i} of {total_chapters} ---", 5)
            Writer.Chapter.ChapterGenerator.GenerateChapter(Interface, SysLogger, i, total_chapters, narrative_context, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL)
            
            # --- Progressive Save ---
            try:
                with open(json_file_path, "w", encoding="utf-8") as f:
                    json.dump(narrative_context.to_dict(), f, indent=4)
                SysLogger.Log(f"Progress for Chapter {i} saved to {os.path.basename(json_file_path)}", 2)
            except Exception as e:
                SysLogger.Log(f"Error saving progress after chapter {i}: {e}", 7)

    else:
        SysLogger.Log(f"Invalid chapter count ({total_chapters}) detected. Aborting chapter generation.", 7)

    # --- Finalization ---
    SysLogger.Log("Novel generation process finished. Proceeding to finalization.", 5)

    if Writer.Config.ENABLE_FINAL_EDIT_PASS:
        narrative_context = Writer.NovelEditor.EditNovel(Interface, SysLogger, narrative_context, Writer.Config.REVISION_MODEL)
    if not Writer.Config.SCRUB_NO_SCRUB:
        narrative_context = Writer.Scrubber.ScrubNovel(Interface, SysLogger, narrative_context, Writer.Config.SCRUB_MODEL)
    else:
        SysLogger.Log("Skipping final scrubbing pass due to config.", 4)

    StoryBodyText = "\n\n\n".join([f"### Chapter {chap.chapter_number}\n\n{chap.generated_content}" for chap in narrative_context.chapters if chap.generated_content])
    
    # Use a default prompt if initial_prompt is missing
    base_prompt_summary = getattr(narrative_context, 'initial_prompt', 'Prompt not available')
    if len(base_prompt_summary) > 150:
        base_prompt_summary = base_prompt_summary[:150] + "..."

    info_messages = [Interface.BuildUserQuery(narrative_context.base_novel_outline_markdown)]
    Info = Writer.StoryInfo.GetStoryInfo(Interface, SysLogger, info_messages, Writer.Config.INFO_MODEL)
    Title = Info.get("Title", outline_filename_base.replace('_', ' ')) # Use outline name as fallback title

    SysLogger.Log(f"Story Title: {Title}", 5)
    SysLogger.Log(f"Summary: {Info.get('Summary', 'N/A')}", 3)
    ElapsedTime = time.time() - StartTime
    TotalWords = Writer.Statistics.GetWordCount(StoryBodyText)
    SysLogger.Log(f"Total story word count: {TotalWords}", 4)

    StatsString = f"""
## Work Statistics
- **Title**: {Title}
- **Summary**: {Info.get('Summary', 'N/A')}
- **Tags**: {Info.get('Tags', 'N/A')}
- **Generation Time**: {ElapsedTime:.2f}s
- **Average WPM**: {60 * (TotalWords / ElapsedTime) if ElapsedTime > 0 else 0:.2f}
- **Generator**: {Writer.Config.PROJECT_NAME}

## Generation Settings
- **Base Prompt**: {base_prompt_summary}
- **Seed**: {Writer.Config.SEED}
- **Primary Model Used**: {Writer.Config.INITIAL_OUTLINE_WRITER_MODEL} (and others if set by args)
"""
    # Final save of MD and JSON
    with open(md_file_path, "w", encoding="utf-8") as f:
        output_content = f"# {Title}\n\n{StoryBodyText}\n\n---\n\n{StatsString}\n\n---\n\n## Full Outline\n```\n{narrative_context.base_novel_outline_markdown}\n```"
        f.write(output_content)

    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(narrative_context.to_dict(), f, indent=4)
    
    SysLogger.Log("Generation complete!", 5)
    final_message = f"""
--------------------------------------------------
Output Files Saved:
- Markdown Story: {os.path.abspath(md_file_path)}
- JSON Data File: {os.path.abspath(json_file_path)}
--------------------------------------------------"""
    print(termcolor.colored(final_message, "green"))


if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description=f"Run the {Writer.Config.PROJECT_NAME} novel generation pipeline.")
    Parser.add_argument("-Outline", help="Path to the outline file.")
    Parser.add_argument("-Output", default="", type=str)
    Parser.add_argument("-Seed", default=Writer.Config.SEED, type=int)
    Parser.add_argument("-Debug", action="store_true", default=Writer.Config.DEBUG)
    Parser.add_argument("-ChapterOutlineModel", default=Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS1Model", default=Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS2Model", default=Writer.Config.CHAPTER_STAGE2_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS3Model", default=Writer.Config.CHAPTER_STAGE3_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterS4Model", default=Writer.Config.CHAPTER_STAGE4_WRITER_MODEL, type=str)
    Parser.add_argument("-ChapterRevisionModel", default=Writer.Config.CHAPTER_REVISION_WRITER_MODEL, type=str)
    Parser.add_argument("-CritiqueLLM", default=Writer.Config.CRITIQUE_LLM, type=str)
    Parser.add_argument("-RevisionModel", default=Writer.Config.REVISION_MODEL, type=str)
    Parser.add_argument("-EvalModel", default=Writer.Config.EVAL_MODEL, type=str)
    Parser.add_argument("-InfoModel", default=Writer.Config.INFO_MODEL, type=str)
    Parser.add_argument("-ScrubModel", default=Writer.Config.SCRUB_MODEL, type=str)
    Parser.add_argument("-CheckerModel", default=Writer.Config.CHECKER_MODEL, type=str)
    Parser.add_argument("-ChapterMinRevisions", default=Writer.Config.CHAPTER_MIN_REVISIONS, type=int)
    Parser.add_argument("-ChapterMaxRevisions", default=Writer.Config.CHAPTER_MAX_REVISIONS, type=int)
    Parser.add_argument("-NoChapterRevision", action="store_true", default=Writer.Config.CHAPTER_NO_REVISIONS)
    Parser.add_argument("-NoScrubChapters", action="store_true", default=Writer.Config.SCRUB_NO_SCRUB)
    Parser.add_argument("-EnableFinalEditPass", action="store_true", default=Writer.Config.ENABLE_FINAL_EDIT_PASS)
    Parser.add_argument("-NoSceneGenerationPipeline", action="store_false", dest="SceneGenerationPipeline", default=Writer.Config.SCENE_GENERATION_PIPELINE)
    Args = Parser.parse_args()

    write_novel(outline_file=Args.Outline, output=Args.Output, seed=Args.Seed, debug=Args.Debug,
                    chapter_outline_model=Args.ChapterOutlineModel,
                    chapter_s1_model=Args.ChapterS1Model,
                    chapter_s2_model=Args.ChapterS2Model,
                    chapter_s3_model=Args.ChapterS3Model,
                    chapter_s4_model=Args.ChapterS4Model,
                    chapter_revision_model=Args.ChapterRevisionModel,
                    critique_llm=Args.CritiqueLLM,
                    revision_model=Args.RevisionModel,
                    eval_model=Args.EvalModel,
                    info_model=Args.InfoModel,
                    scrub_model=Args.ScrubModel,
                    checker_model=Args.CheckerModel,
                    chapter_min_revisions=Args.ChapterMinRevisions,
                    chapter_max_revisions=Args.ChapterMaxRevisions,
                    no_chapter_revision=Args.NoChapterRevision,
                    no_scrub_chapters=Args.NoScrubChapters,
                    enable_final_edit_pass=Args.EnableFinalEditPass,
                    scene_generation_pipeline=Args.SceneGenerationPipeline)
