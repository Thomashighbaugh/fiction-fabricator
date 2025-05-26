# Project Structure

```
AIStoryWriter/
├── Writer/
│   ├── Chapter/
│   │   ├── ChapterDetector.py
│   │   ├── ChapterGenSummaryCheck.py
│   │   └── ChapterGenerator.py
│   ├── Interface/
│   │   ├── OpenRouter.py
│   │   └── Wrapper.py
│   ├── Outline/
│   │   └── StoryElements.py
│   ├── Scene/
│   │   ├── ChapterByScene.py
│   │   ├── ChapterOutlineToScenes.py
│   │   ├── SceneOutlineToScene.py
│   │   └── ScenesToJSON.py
│   ├── Config.py
│   ├── LLMEditor.py
│   ├── NovelEditor.py
│   ├── OutlineGenerator.py
│   ├── PrintUtils.py
│   ├── Prompts.py
│   ├── Scrubber.py
│   ├── Statistics.py
│   ├── StoryInfo.py
│   └── Translator.py
├── Write.py
└── requirements.txt
```

# Project Files

## File: `Writer/Chapter/ChapterDetector.py`

```python
import Writer.Config
import Writer.Prompts

import re
import json


def LLMCountChapters(Interface, _Logger, _Summary):

    Prompt = Writer.Prompts.CHAPTER_COUNT_PROMPT.format(_Summary=_Summary)

    _Logger.Log("Prompting LLM To Get ChapterCount JSON", 5)
    Messages = []
    Messages.append(Interface.BuildUserQuery(Prompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.EVAL_MODEL, _Format="json"
    )
    _Logger.Log("Finished Getting ChapterCount JSON", 5)

    Iters: int = 0

    while True:

        RawResponse = Interface.GetLastMessageText(Messages)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            TotalChapters = json.loads(RawResponse)["TotalChapters"]
            _Logger.Log("Got Total Chapter Count At {TotalChapters}", 5)
            return TotalChapters
        except Exception as E:
            if Iters > 4:
                _Logger.Log("Critical Error Parsing JSON", 7)
                return -1
            _Logger.Log("Error Parsing JSON Written By LLM, Asking For Edits", 7)
            EditPrompt: str = (
                f"Please revise your JSON. It encountered the following error during parsing: {E}. Remember that your entire response is plugged directly into a JSON parser, so don't write **anything** except pure json."
            )
            Messages.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("Asking LLM TO Revise", 7)
            Messages = Interface.SafeGenerateText(
                _Logger, Messages, Writer.Config.EVAL_MODEL, _Format="json"
            )
            _Logger.Log("Done Asking LLM TO Revise JSON", 6)

```

## File: `Writer/Chapter/ChapterGenSummaryCheck.py`

```python
import json

import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Prompts


def LLMSummaryCheck(Interface, _Logger, _RefSummary: str, _Work: str):
    """
    Generates a summary of the work provided, and compares that to the reference summary, asking if they answered the prompt correctly.
    """

    # LLM Length Check - Firstly, check if the length of the response was at least 100 words.
    if len(_Work.split(" ")) < 100:
        _Logger.Log(
            "Previous response didn't meet the length requirement, so it probably tried to cheat around writing.",
            7,
        )
        return False, ""

    # Build Summariziation Langchain
    SummaryLangchain: list = []
    SummaryLangchain.append(
        Interface.BuildSystemQuery(Writer.Prompts.SUMMARY_CHECK_INTRO)
    )
    SummaryLangchain.append(
        Interface.BuildUserQuery(
            Writer.Prompts.SUMMARY_CHECK_PROMPT.format(_Work=_Work)
        )
    )
    SummaryLangchain = Interface.SafeGenerateText(
        _Logger, SummaryLangchain, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL
    )  # CHANGE THIS MODEL EVENTUALLY - BUT IT WORKS FOR NOW!!!
    WorkSummary: str = Interface.GetLastMessageText(SummaryLangchain)

    # Now Summarize The Outline
    SummaryLangchain: list = []
    SummaryLangchain.append(
        Interface.BuildSystemQuery(Writer.Prompts.SUMMARY_OUTLINE_INTRO)
    )
    SummaryLangchain.append(
        Interface.BuildUserQuery(
            Writer.Prompts.SUMMARY_OUTLINE_PROMPT.format(_RefSummary=_RefSummary)
        )
    )
    SummaryLangchain = Interface.SafeGenerateText(
        _Logger, SummaryLangchain, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL
    )  # CHANGE THIS MODEL EVENTUALLY - BUT IT WORKS FOR NOW!!!
    OutlineSummary: str = Interface.GetLastMessageText(SummaryLangchain)

    # Now, generate a comparison JSON value.
    ComparisonLangchain: list = []
    ComparisonLangchain.append(
        Interface.BuildSystemQuery(Writer.Prompts.SUMMARY_COMPARE_INTRO)
    )
    ComparisonLangchain.append(
        Interface.BuildUserQuery(
            Writer.Prompts.SUMMARY_COMPARE_PROMPT.format(
                WorkSummary=WorkSummary, OutlineSummary=OutlineSummary
            )
        )
    )
    ComparisonLangchain = Interface.SafeGenerateText(
        _Logger, ComparisonLangchain, Writer.Config.REVISION_MODEL, _Format="json"
    )  # CHANGE THIS MODEL EVENTUALLY - BUT IT WORKS FOR NOW!!!

    Iters: int = 0
    while True:

        RawResponse = Interface.GetLastMessageText(ComparisonLangchain)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            Dict = json.loads(RawResponse)
            return (
                Dict["DidFollowOutline"],
                "### Extra Suggestions:\n" + Dict["Suggestions"],
            )
        except Exception as E:
            if Iters > 4:
                _Logger.Log("Critical Error Parsing JSON", 7)
                return False, ""

            _Logger.Log("Error Parsing JSON Written By LLM, Asking For Edits", 7)
            EditPrompt: str = (
                f"Please revise your JSON. It encountered the following error during parsing: {E}. Remember that your entire response is plugged directly into a JSON parser, so don't write **anything** except pure json."
            )
            ComparisonLangchain.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("Asking LLM TO Revise", 7)
            ComparisonLangchain = Interface.SafeGenerateText(
                _Logger,
                ComparisonLangchain,
                Writer.Config.REVISION_MODEL,
                _Format="json",
            )
            _Logger.Log("Done Asking LLM TO Revise JSON", 6)

```

## File: `Writer/Chapter/ChapterGenerator.py`

```python
import json

import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Chapter.ChapterGenSummaryCheck
import Writer.Prompts

import Writer.Scene.ChapterByScene

def GenerateChapter(
    Interface,
    _Logger,
    _ChapterNum: int,
    _TotalChapters: int,
    _Outline: str,
    _Chapters: list = [],
    _QualityThreshold: int = 85,
    _BaseContext:str = ""
):

    # Some important notes
    # We're going to remind the author model of the previous chapters here, so it knows what has been written before.

    #### Stage 0: Create base language chain
    _Logger.Log(f"Creating Base Langchain For Chapter {_ChapterNum} Generation", 2)
    MesssageHistory: list = []
    MesssageHistory.append(
        Interface.BuildSystemQuery(
            Writer.Prompts.CHAPTER_GENERATION_INTRO.format(
                _ChapterNum=_ChapterNum, _TotalChapters=_TotalChapters
            )
        )
    )

    ContextHistoryInsert: str = ""

    if len(_Chapters) > 0:

        ChapterSuperlist: str = ""
        for Chapter in _Chapters:
            ChapterSuperlist += f"{Chapter}\n"

        ContextHistoryInsert += Writer.Prompts.CHAPTER_HISTORY_INSERT.format(
            _Outline=_Outline, ChapterSuperlist=ChapterSuperlist
        )

    #
    # MesssageHistory.append(Interface.BuildUserQuery(f"""
    # Here is the novel so far.
    # """))
    # MesssageHistory.append(Interface.BuildUserQuery(ChapterSuperlist))
    # MesssageHistory.append(Interface.BuildSystemQuery("Make sure to pay attention to the content that has happened in these previous chapters. It's okay to deviate from the outline a little in order to ensure you continue the same story from previous chapters."))

    # Now, extract the this-chapter-outline segment
    _Logger.Log(f"Extracting Chapter Specific Outline", 4)
    ThisChapterOutline: str = ""
    ChapterSegmentMessages = []
    ChapterSegmentMessages.append(
        Interface.BuildSystemQuery(Writer.Prompts.CHAPTER_GENERATION_INTRO)
    )
    ChapterSegmentMessages.append(
        Interface.BuildUserQuery(
            Writer.Prompts.CHAPTER_GENERATION_PROMPT.format(
                _Outline=_Outline, _ChapterNum=_ChapterNum
            )
        )
    )
    ChapterSegmentMessages = Interface.SafeGenerateText(
        _Logger,
        ChapterSegmentMessages,
        Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, _MinWordCount=120
    )  # CHANGE THIS MODEL EVENTUALLY - BUT IT WORKS FOR NOW!!!
    ThisChapterOutline: str = Interface.GetLastMessageText(ChapterSegmentMessages)
    _Logger.Log(f"Created Chapter Specific Outline", 4)

    # Generate Summary of Last Chapter If Applicable
    FormattedLastChapterSummary: str = ""
    if len(_Chapters) > 0:
        _Logger.Log(f"Creating Summary Of Last Chapter Info", 3)
        ChapterSummaryMessages = []
        ChapterSummaryMessages.append(
            Interface.BuildSystemQuery(Writer.Prompts.CHAPTER_SUMMARY_INTRO)
        )
        ChapterSummaryMessages.append(
            Interface.BuildUserQuery(
                Writer.Prompts.CHAPTER_SUMMARY_PROMPT.format(
                    _ChapterNum=_ChapterNum,
                    _TotalChapters=_TotalChapters,
                    _Outline=_Outline,
                    _LastChapter=_Chapters[-1],
                )
            )
        )
        ChapterSummaryMessages = Interface.SafeGenerateText(
            _Logger,
            ChapterSummaryMessages,
            Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, _MinWordCount=100
        )  # CHANGE THIS MODEL EVENTUALLY - BUT IT WORKS FOR NOW!!!
        FormattedLastChapterSummary: str = Interface.GetLastMessageText(
            ChapterSummaryMessages
        )
        _Logger.Log(f"Created Summary Of Last Chapter Info", 3)

    DetailedChapterOutline: str = ThisChapterOutline
    if FormattedLastChapterSummary != "":
        DetailedChapterOutline = ThisChapterOutline

    _Logger.Log(f"Done with base langchain setup", 2)


    # If scene generation disabled, use the normal initial plot generator
    Stage1Chapter = ""
    if (not Writer.Config.SCENE_GENERATION_PIPELINE):

        #### STAGE 1: Create Initial Plot
        IterCounter: int = 0
        Feedback: str = ""
        while True:
            Prompt = Writer.Prompts.CHAPTER_GENERATION_STAGE1.format(
                ContextHistoryInsert=ContextHistoryInsert,
                _ChapterNum=_ChapterNum,
                _TotalChapters=_TotalChapters,
                ThisChapterOutline=ThisChapterOutline,
                FormattedLastChapterSummary=FormattedLastChapterSummary,
                Feedback=Feedback,
                _BaseContext=_BaseContext
            )

            # Generate Initial Chapter
            _Logger.Log(
                f"Generating Initial Chapter (Stage 1: Plot) {_ChapterNum}/{_TotalChapters} (Iteration {IterCounter})",
                5,
            )
            Messages = MesssageHistory.copy()
            Messages.append(Interface.BuildUserQuery(Prompt))

            Messages = Interface.SafeGenerateText(
                _Logger,
                Messages,
                Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
                _SeedOverride=IterCounter + Writer.Config.SEED,
                _MinWordCount=100
            )
            IterCounter += 1
            Stage1Chapter: str = Interface.GetLastMessageText(Messages)
            _Logger.Log(
                f"Finished Initial Generation For Initial Chapter (Stage 1: Plot)  {_ChapterNum}/{_TotalChapters}",
                5,
            )

            # Check if LLM did the work
            if IterCounter > Writer.Config.CHAPTER_MAX_REVISIONS:
                _Logger.Log(
                    "Chapter Summary-Based Revision Seems Stuck - Forcefully Exiting", 7
                )
                break
            Result, Feedback = Writer.Chapter.ChapterGenSummaryCheck.LLMSummaryCheck(
                Interface, _Logger, DetailedChapterOutline, Stage1Chapter
            )
            if Result:
                _Logger.Log(
                    f"Done Generating Initial Chapter (Stage 1: Plot)  {_ChapterNum}/{_TotalChapters}",
                    5,
                )
                break
    
    else:

        Stage1Chapter = Writer.Scene.ChapterByScene.ChapterByScene(Interface, _Logger, ThisChapterOutline, _Outline, _BaseContext)


    #### STAGE 2: Add Character Development
    Stage2Chapter = ""
    IterCounter: int = 0
    Feedback: str = ""
    while True:
        Prompt = Writer.Prompts.CHAPTER_GENERATION_STAGE2.format(
            ContextHistoryInsert=ContextHistoryInsert,
            _ChapterNum=_ChapterNum,
            _TotalChapters=_TotalChapters,
            ThisChapterOutline=ThisChapterOutline,
            FormattedLastChapterSummary=FormattedLastChapterSummary,
            Stage1Chapter=Stage1Chapter,
            Feedback=Feedback,
            _BaseContext=_BaseContext
        )

        # Generate Initial Chapter
        _Logger.Log(
            f"Generating Initial Chapter (Stage 2: Character Development) {_ChapterNum}/{_TotalChapters} (Iteration {IterCounter})",
            5,
        )
        Messages = MesssageHistory.copy()
        Messages.append(Interface.BuildUserQuery(Prompt))

        Messages = Interface.SafeGenerateText(
            _Logger,
            Messages,
            Writer.Config.CHAPTER_STAGE2_WRITER_MODEL,
            _SeedOverride=IterCounter + Writer.Config.SEED,
            _MinWordCount=100
        )
        IterCounter += 1
        Stage2Chapter: str = Interface.GetLastMessageText(Messages)
        _Logger.Log(
            f"Finished Initial Generation For Initial Chapter (Stage 2: Character Development)  {_ChapterNum}/{_TotalChapters}",
            5,
        )

        # Check if LLM did the work
        if IterCounter > Writer.Config.CHAPTER_MAX_REVISIONS:
            _Logger.Log(
                "Chapter Summary-Based Revision Seems Stuck - Forcefully Exiting", 7
            )
            break
        Result, Feedback = Writer.Chapter.ChapterGenSummaryCheck.LLMSummaryCheck(
            Interface, _Logger, DetailedChapterOutline, Stage2Chapter
        )
        if Result:
            _Logger.Log(
                f"Done Generating Initial Chapter (Stage 2: Character Development)  {_ChapterNum}/{_TotalChapters}",
                5,
            )
            break

    #### STAGE 3: Add Dialogue
    Stage3Chapter = ""
    IterCounter: int = 0
    Feedback: str = ""
    while True:
        Prompt = Writer.Prompts.CHAPTER_GENERATION_STAGE3.format(
            ContextHistoryInsert=ContextHistoryInsert,
            _ChapterNum=_ChapterNum,
            _TotalChapters=_TotalChapters,
            ThisChapterOutline=ThisChapterOutline,
            FormattedLastChapterSummary=FormattedLastChapterSummary,
            Stage2Chapter=Stage2Chapter,
            Feedback=Feedback,
            _BaseContext=_BaseContext
        )
        # Generate Initial Chapter
        _Logger.Log(
            f"Generating Initial Chapter (Stage 3: Dialogue) {_ChapterNum}/{_TotalChapters} (Iteration {IterCounter})",
            5,
        )
        Messages = MesssageHistory.copy()
        Messages.append(Interface.BuildUserQuery(Prompt))

        Messages = Interface.SafeGenerateText(
            _Logger,
            Messages,
            Writer.Config.CHAPTER_STAGE3_WRITER_MODEL,
            _SeedOverride=IterCounter + Writer.Config.SEED,
            _MinWordCount=100
        )
        IterCounter += 1
        Stage3Chapter: str = Interface.GetLastMessageText(Messages)
        _Logger.Log(
            f"Finished Initial Generation For Initial Chapter (Stage 3: Dialogue)  {_ChapterNum}/{_TotalChapters}",
            5,
        )

        # Check if LLM did the work
        if IterCounter > Writer.Config.CHAPTER_MAX_REVISIONS:
            _Logger.Log(
                "Chapter Summary-Based Revision Seems Stuck - Forcefully Exiting", 7
            )
            break
        Result, Feedback = Writer.Chapter.ChapterGenSummaryCheck.LLMSummaryCheck(
            Interface, _Logger, DetailedChapterOutline, Stage3Chapter
        )
        if Result:
            _Logger.Log(
                f"Done Generating Initial Chapter (Stage 3: Dialogue)  {_ChapterNum}/{_TotalChapters}",
                5,
            )
            break

        #     #### STAGE 4: Final-Pre-Revision Edit Pass
        # Prompt = Writer.Prompts.CHAPTER_GENERATION_STAGE4.format(
        #    ContextHistoryInsert=ContextHistoryInsert,
        #     _ChapterNum=_ChapterNum,
        #     _TotalChapters=_TotalChapters,
        #     _Outline=_Outline,
        #     Stage3Chapter=Stage3Chapter,
        #     Feedback=Feedback,
        # )

    #     # Generate Initial Chapter
    #     _Logger.Log(f"Generating Initial Chapter (Stage 4: Final Pass) {_ChapterNum}/{_TotalChapters}", 5)
    #     Messages = MesssageHistory.copy()
    #     Messages.append(Interface.BuildUserQuery(Prompt))

    #     Messages = Interface.SafeGenerateText(_Logger, Messages, Writer.Config.CHAPTER_STAGE4_WRITER_MODEL)
    #     Chapter:str = Interface.GetLastMessageText(Messages)
    #     _Logger.Log(f"Done Generating Initial Chapter (Stage 4: Final Pass)  {_ChapterNum}/{_TotalChapters}", 5)
    Chapter: str = Stage3Chapter

    #### Stage 5: Revision Cycle
    if Writer.Config.CHAPTER_NO_REVISIONS:
        _Logger.Log(f"Chapter Revision Disabled In Config, Exiting Now", 5)
        return Chapter

    _Logger.Log(
        f"Entering Feedback/Revision Loop (Stage 5) For Chapter {_ChapterNum}/{_TotalChapters}",
        4,
    )
    WritingHistory = MesssageHistory.copy()
    Rating: int = 0
    Iterations: int = 0
    while True:
        Iterations += 1
        Feedback = Writer.LLMEditor.GetFeedbackOnChapter(
            Interface, _Logger, Chapter, _Outline
        )
        Rating = Writer.LLMEditor.GetChapterRating(Interface, _Logger, Chapter)

        if Iterations > Writer.Config.CHAPTER_MAX_REVISIONS:
            break
        if (Iterations > Writer.Config.CHAPTER_MIN_REVISIONS) and (Rating == True):
            break
        Chapter, WritingHistory = ReviseChapter(
            Interface, _Logger, Chapter, Feedback, WritingHistory
        )

    _Logger.Log(
        f"Quality Standard Met, Exiting Feedback/Revision Loop (Stage 5) For Chapter {_ChapterNum}/{_TotalChapters}",
        4,
    )

    return Chapter


def ReviseChapter(Interface, _Logger, _Chapter, _Feedback, _History: list = []):

    RevisionPrompt = Writer.Prompts.CHAPTER_REVISION.format(
        _Chapter=_Chapter, _Feedback=_Feedback
    )

    _Logger.Log("Revising Chapter", 5)
    Messages = _History
    Messages.append(Interface.BuildUserQuery(RevisionPrompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
        _MinWordCount=100
    )
    SummaryText: str = Interface.GetLastMessageText(Messages)
    _Logger.Log("Done Revising Chapter", 5)

    return SummaryText, Messages

```

## File: `Writer/Interface/OpenRouter.py`

```python
# File: AIStoryWriter/Writer/Interface/OpenRouter.py
# Purpose: Client for interacting with the OpenRouter API.

import json
import requests # type: ignore
import time
from typing import Any, List, Mapping, Optional, Literal, Union, TypedDict, cast

# Define Message and ProviderPreferences types for clarity (can be refined)
class MessageTypeDef(TypedDict):
    role: Literal['user', 'assistant', 'system', 'tool']
    content: str

class ProviderPreferencesTypeDef(TypedDict, total=False):
    allow_fallbacks: Optional[bool]
    require_parameters: Optional[bool]
    data_collection: Union[Literal['deny'], Literal['allow'], None]
    order: Optional[List[Literal[
        'OpenAI', 'Anthropic', 'HuggingFace', 'Google', 'Together', 'DeepInfra', 'Azure', 'Modal',
        'AnyScale', 'Replicate', 'Perplexity', 'Recursal', 'Fireworks', 'Mistral', 'Groq', 'Cohere',
        'Lepton', 'OctoAI', 'Novita', 'DeepSeek', 'Infermatic', 'AI21', 'Featherless', 'Mancer',
        'Mancer 2', 'Lynn 2', 'Lynn' # This list can grow, keep it representative
    ]]]

class OpenRouter:
    """
    A client for interacting with the OpenRouter.ai API.
    Handles request formatting, API calls, and basic error management.
    Reference: https://openrouter.ai/docs
    """

    DEFAULT_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_TIMEOUT_SECONDS = 360 # 6 minutes

    def __init__(self,
                 api_key: str,
                 model: str = "mistralai/mistral-7b-instruct", # A common default
                 provider_preferences: Optional[ProviderPreferencesTypeDef] = None,
                 max_tokens: Optional[int] = None, # Let model decide by default
                 temperature: Optional[float] = 0.7,
                 top_k: Optional[int] = 0, # 0 often means disabled or default handling
                 top_p: Optional[float] = 1.0,
                 presence_penalty: Optional[float] = 0.0,
                 frequency_penalty: Optional[float] = 0.0,
                 repetition_penalty: Optional[float] = 1.0, # Default 1.0 (no penalty)
                 min_p: Optional[float] = 0.0,
                 top_a: Optional[float] = 0.0,
                 seed: Optional[int] = None,
                 logit_bias: Optional[Mapping[int, float]] = None, # Note: OpenRouter expects float values
                 response_format: Optional[Mapping[str, str]] = None, # e.g., {"type": "json_object"}
                 stop: Optional[Union[str, List[str]]] = None,
                 api_url: str = DEFAULT_API_URL,
                 timeout: int = DEFAULT_TIMEOUT_SECONDS,
                 site_url_header: str = "https://github.com/your-repo/AIStoryWriter", # Replace with actual repo URL
                 app_name_header: str = "AIStoryWriter"
                 ):

        if not api_key:
            raise ValueError("OpenRouter API key is required.")

        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout
        self.site_url_header = site_url_header
        self.app_name_header = app_name_header

        # Store parameters to be sent with each request
        self.params: Dict[str, Any] = {
            "model": model,
            "provider": provider_preferences,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "repetition_penalty": repetition_penalty,
            "min_p": min_p,
            "top_a": top_a,
            "seed": seed,
            "logit_bias": logit_bias,
            "response_format": response_format,
            "stop": stop,
            "stream": False # This client currently does not support true streaming from OpenRouter
        }
        # Filter out None values from initial params, so they don't override model defaults if not set
        self.params = {k: v for k, v in self.params.items() if v is not None}


    def set_params(self, **kwargs: Any) -> None:
        """
        Updates the stored parameters for subsequent API calls.
        Only provided parameters are updated.
        Example: client.set_params(temperature=0.5, max_tokens=500)
        """
        for key, value in kwargs.items():
            if key == "model": # Special handling for model name
                self.params["model"] = value
            elif value is not None: # Update if value is not None
                self.params[key] = value
            elif key in self.params: # Remove if value is None and key exists
                del self.params[key]

    @property
    def model(self) -> str:
        return cast(str, self.params.get("model", ""))

    @model.setter
    def model(self, value: str) -> None:
        self.params["model"] = value


    def _prepare_request_data(self, messages: List[MessageTypeDef], seed_override: Optional[int] = None) -> Dict[str, Any]:
        """Prepares the data payload for the API request."""
        request_data = self.params.copy() # Start with stored defaults/overrides
        request_data["messages"] = messages
        if seed_override is not None:
            request_data["seed"] = seed_override
        
        # Ensure logit_bias keys are strings if they are integers, as per some API requirements
        if "logit_bias" in request_data and request_data["logit_bias"]:
            logit_bias_processed = {}
            for k, v_bias in request_data["logit_bias"].items():
                logit_bias_processed[str(k)] = v_bias
            request_data["logit_bias"] = logit_bias_processed
            
        return request_data

    def chat(self,
             messages: List[MessageTypeDef],
             max_retries: int = 5, # Increased default retries
             seed: Optional[int] = None # Allows overriding seed per-call
             ) -> str:
        """
        Sends a chat completion request to the OpenRouter API.

        Args:
            messages: A list of message objects.
            max_retries: Maximum number of retries for transient errors.
            seed: Optional seed for this specific call, overriding instance default.

        Returns:
            The content of the assistant's response message.

        Raises:
            Exception: If the request fails after all retries or for critical errors.
        """
        if not self.params.get("model"):
            raise ValueError("Model not set for OpenRouter client.")

        request_data = self._prepare_request_data(messages, seed_override=seed)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url_header, # Recommended by OpenRouter
            "X-Title": self.app_name_header      # Recommended by OpenRouter
        }

        current_retry = 0
        while current_retry < max_retries:
            try:
                response = requests.post(
                    url=self.api_url,
                    headers=headers,
                    data=json.dumps(request_data),
                    timeout=self.timeout
                )
                response.raise_for_status() # Raises HTTPError for 4XX/5XX status codes

                response_json = response.json()

                if 'choices' in response_json and response_json['choices']:
                    first_choice = response_json['choices'][0]
                    if 'message' in first_choice and 'content' in first_choice['message']:
                        return str(first_choice['message']['content'])
                    else:
                        # This case should ideally not happen with a valid response
                        raise ValueError("OpenRouter response 'message' or 'content' missing in choice.")
                elif 'error' in response_json:
                    error_data = response_json['error']
                    error_code = error_data.get('code')
                    error_message = error_data.get('message', 'Unknown error from OpenRouter.')
                    # print(f"OpenRouter API Error (Code: {error_code}): {error_message}. Attempt {current_retry + 1}/{max_retries}.") # Replaced by logger

                    if error_code == 401: # Unauthorized
                        raise Exception(f"OpenRouter Authentication Error (401): {error_message}. Check API key.")
                    if error_code == 402: # Payment Required
                        raise Exception(f"OpenRouter Payment Error (402): {error_message}. Check account credits.")
                    if error_code == 429: # Rate limit
                        # print("Rate limited by OpenRouter. Waiting before retry...") # Replaced by logger
                        time.sleep(min(10 * (2 ** current_retry), 60)) # Exponential backoff, max 60s
                    # For other errors, just retry if not max_retries
                else:
                    # Unexpected response structure
                    raise ValueError(f"OpenRouter response missing 'choices' or 'error' field. Response: {response_json}")

            except requests.exceptions.HTTPError as http_err:
                # print(f"HTTP error occurred: {http_err} - Status: {http_err.response.status_code}. Attempt {current_retry + 1}/{max_retries}.") # Replaced by logger
                if http_err.response.status_code == 524: # Cloudflare timeout specific to OpenRouter sometimes
                    time.sleep(min(10 * (2 ** current_retry), 60))
                # Other HTTP errors will also trigger a retry up to max_retries
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as conn_err:
                # print(f"Connection/Timeout error: {conn_err}. Attempt {current_retry + 1}/{max_retries}.") # Replaced by logger
                time.sleep(min(5 * (2 ** current_retry), 30)) # Shorter backoff for network issues
            except json.JSONDecodeError as json_err:
                 # print(f"Failed to decode JSON response from OpenRouter: {json_err}. Response text: {response.text[:200]}... Attempt {current_retry + 1}/{max_retries}.") # Replaced by logger
                 # This is usually a server-side issue if status was 200 but content isn't JSON
                 pass
            except Exception as e: # Catch any other unexpected errors
                # print(f"An unexpected error occurred with OpenRouter client: {e}. Attempt {current_retry + 1}/{max_retries}.") # Replaced by logger
                # Decide if this error is retryable or should raise immediately
                if not isinstance(e, (ValueError)): # Retry general exceptions unless it's a ValueError we raised
                    time.sleep(1) # Short delay for truly unexpected errors before retry
                else: # If it's a ValueError we raised (e.g. bad response structure), re-raise after logging if max retries.
                    if current_retry >= max_retries - 1:
                        raise
                    else:
                        pass

            current_retry += 1

        raise Exception(f"OpenRouter request failed after {max_retries} retries for model {self.model}.")

if __name__ == '__main__':
    # Example Usage (requires OPENROUTER_API_KEY in .env or environment)
    # This part is for testing and would not be in the final library file.
    from dotenv import load_dotenv
    import os
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Please set OPENROUTER_API_KEY in your environment or .env file to run this example.")
    else:
        try:
            # Test with a common free model
            client = OpenRouter(api_key=api_key, model="mistralai/mistral-7b-instruct")
            
            # Test parameter setting
            client.set_params(temperature=0.8, max_tokens=150)
            print(f"Client configured for model: {client.model} with params: {client.params}")

            messages_test: List[MessageTypeDef] = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": "What is the capital of France?"}
            ]
            
            print("\nSending chat request...")
            response_content = client.chat(messages=messages_test)
            print("\nAssistant's Response:")
            print(response_content)

            # Test JSON mode (if model supports it, e.g. some OpenAI models via OpenRouter)
            # Note: Not all models on OpenRouter explicitly support the 'json_object' response_format.
            # You might need to use a model known for good JSON output and prompt engineering.
            # client.set_params(model="openai/gpt-3.5-turbo", response_format={"type": "json_object"})
            # messages_json_test: List[MessageTypeDef] = [
            #     {"role": "user", "content": "Provide a JSON object with two keys: 'city' and 'country', for Paris."}
            # ]
            # print("\nSending JSON mode chat request...")
            # response_json_content = client.chat(messages=messages_json_test)
            # print("\nAssistant's JSON Response:")
            # print(response_json_content)
            # try:
            #     parsed_json = json.loads(response_json_content)
            #     print("Parsed JSON:", parsed_json)
            # except json.JSONDecodeError:
            #     print("Failed to parse response as JSON.")

        except Exception as e:
            print(f"An error occurred during the example: {e}")
```

## File: `Writer/Interface/Wrapper.py`

```python
# File: AIStoryWriter/Writer/Interface/Wrapper.py
# Purpose: Wraps LLM API interactions, providing a consistent interface and handling retries, logging, and streaming.

"""
LLM Interface Wrapper.

This module provides a standardized way to interact with various LLM providers (Ollama, Google, OpenRouter).
It handles:
- Loading models and initializing clients.
- Dynamic installation of required packages.
- Parsing model URI strings for provider, host, and parameters.
- Streaming responses for interactive output.
- Safe generation methods with retries for empty or short responses (`SafeGenerateText`).
- Safe JSON generation with validation and retries (`SafeGenerateJSON`).
- Logging of LLM calls and their contexts.
- Seed management for reproducibility.
"""

import dotenv
import inspect
import json
import os
import time
import random
import importlib
import subprocess
import sys
from urllib.parse import parse_qs, urlparse
from typing import List, Dict, Any, Tuple, Optional, Literal
import Writer.Config as Config  # Renamed for clarity
import Writer.Prompts as Prompts  # For JSON_PARSE_ERROR prompt


# Load environment variables from .env file (e.g., API keys)
dotenv.load_dotenv()


class Interface:
    """
    Manages connections and interactions with various Large Language Models.
    """

    def __init__(self, models_to_load: List[str] = []):
        """
        Initializes the Interface and loads specified models.

        Args:
            models_to_load (List[str]): A list of model URI strings to preload.
        """
        self.clients: Dict[str, Any] = (
            {}
        )  # Stores initialized LLM clients, keyed by model_uri
        self.load_models(models_to_load)

    def _ensure_package_is_installed(
        self, package_name: str, logger: Optional[Any] = None
    ) -> None:
        """
        Checks if a package is installed and installs it if not.
        Uses a passed logger if available.
        """
        try:
            importlib.import_module(package_name)
            if logger:
                logger.Log(f"Package '{package_name}' is already installed.", 0)
        except ImportError:
            log_msg = f"Package '{package_name}' not found. Attempting installation..."
            if logger:
                logger.Log(log_msg, 1)
            else:
                print(log_msg)

            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package_name]
                )
                log_msg_success = f"Package '{package_name}' installed successfully."
                if logger:
                    logger.Log(log_msg_success, 0)
                else:
                    print(log_msg_success)
            except subprocess.CalledProcessError as e:
                log_msg_fail = f"Failed to install package '{package_name}': {e}"
                if logger:
                    logger.Log(log_msg_fail, 7)
                else:
                    print(log_msg_fail)
                raise ImportError(
                    f"Could not install required package: {package_name}"
                ) from e

    def load_models(self, model_uris: List[str], logger: Optional[Any] = None) -> None:
        """
        Loads and initializes clients for the specified models.

        Args:
            model_uris (List[str]): A list of model URI strings.
            logger (Optional[Any]): Logger instance for logging messages.
        """
        for model_uri in model_uris:
            if model_uri in self.clients:
                if logger:
                    logger.Log(f"Model '{model_uri}' already loaded.", 0)
                continue

            provider, provider_model_name, model_host, model_options = (
                self._get_model_and_provider(model_uri)
            )
            log_msg_load = f"Loading Model: '{provider_model_name}' from Provider: '{provider}' at Host: '{model_host or 'default'}' with options: {model_options or '{}'}"
            if logger:
                logger.Log(log_msg_load, 1)
            else:
                print(log_msg_load)

            try:
                if provider == "ollama":
                    self._ensure_package_is_installed("ollama", logger)
                    import ollama  # type: ignore

                    effective_ollama_host = (
                        model_host if model_host else Config.OLLAMA_HOST
                    )

                    # Check if model is available and download if not
                    try:
                        ollama.Client(host=effective_ollama_host).show(
                            provider_model_name
                        )
                        if logger:
                            logger.Log(
                                f"Ollama model '{provider_model_name}' found locally at {effective_ollama_host}.",
                                0,
                            )
                    except (
                        ollama.ResponseError
                    ):  # More specific exception for model not found
                        log_msg_download = f"Ollama model '{provider_model_name}' not found at {effective_ollama_host}. Attempting download..."
                        if logger:
                            logger.Log(log_msg_download, 1)
                        else:
                            print(log_msg_download)

                        ollama_download_stream = ollama.Client(
                            host=effective_ollama_host
                        ).pull(provider_model_name, stream=True)
                        for chunk in ollama_download_stream:
                            status = chunk.get("status", "")
                            completed = chunk.get("completed", 0)
                            total = chunk.get("total", 0)
                            if total > 0 and completed > 0:
                                progress = (completed / total) * 100
                                print(
                                    f"Downloading {provider_model_name}: {progress:.2f}% ({completed/1024**2:.2f}MB / {total/1024**2:.2f}MB)",
                                    end="\r",
                                )
                            else:
                                print(f"{status} {provider_model_name}...", end="\r")
                        print(
                            "\nDownload complete."
                            if total > 0
                            else f"\nFinished: {status}"
                        )

                    self.clients[model_uri] = ollama.Client(host=effective_ollama_host)

                elif provider == "google":
                    self._ensure_package_is_installed("google-generativeai", logger)
                    import google.generativeai as genai  # type: ignore

                    google_api_key = os.environ.get("GOOGLE_API_KEY")
                    if not google_api_key:
                        raise ValueError(
                            "GOOGLE_API_KEY not found in environment variables for Google provider."
                        )
                    genai.configure(api_key=google_api_key)
                    self.clients[model_uri] = genai.GenerativeModel(
                        model_name=provider_model_name
                    )

                elif provider == "openrouter":
                    self._ensure_package_is_installed(
                        "requests", logger
                    )  # OpenRouter client uses requests
                    from Writer.Interface.OpenRouter import OpenRouter  # Local import

                    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
                    if not openrouter_api_key:
                        raise ValueError(
                            "OPENROUTER_API_KEY not found in environment variables for OpenRouter provider."
                        )
                    self.clients[model_uri] = OpenRouter(
                        api_key=openrouter_api_key, model=provider_model_name
                    )

                # Add other providers like Anthropic here if needed
                # elif provider == "anthropic":
                #     self._ensure_package_is_installed("anthropic", logger)
                #     # ... anthropic client setup ...

                else:
                    error_msg = f"Unsupported model provider '{provider}' for model URI '{model_uri}'."
                    if logger:
                        logger.Log(error_msg, 7)
                    raise ValueError(error_msg)

                log_msg_success = f"Successfully loaded model '{provider_model_name}' for URI '{model_uri}'."
                if logger:
                    logger.Log(log_msg_success, 1)
                else:
                    print(log_msg_success)

            except Exception as e:
                error_msg_load = f"Failed to load model for URI '{model_uri}': {e}"
                if logger:
                    logger.Log(error_msg_load, 7)
                else:
                    print(error_msg_load)
                # Optionally, re-raise or handle as appropriate (e.g., skip model if non-critical)

    def _get_model_and_provider(
        self, model_uri: str
    ) -> Tuple[str, str, Optional[str], Optional[Dict[str, Any]]]:
        """
        Parses a model URI string to extract provider, model name, host, and query parameters.
        Format: "provider://model_identifier@host?param1=value1¶m2=value2"
        If no "://" is present, defaults to "ollama".
        """
        if "://" not in model_uri:
            # Default to ollama provider if no scheme is specified
            # This assumes the model_uri is just the model name for ollama
            # and uses the default Config.OLLAMA_HOST
            parsed_path = model_uri.split("@")
            model_name = parsed_path[0]
            host = parsed_path[1] if len(parsed_path) > 1 else Config.OLLAMA_HOST
            return "ollama", model_name, host, None

        parsed = urlparse(model_uri)
        provider = parsed.scheme.lower()

        path_parts = parsed.path.strip("/").split(
            "@"
        )  # Remove leading/trailing slashes from path
        model_identifier_from_path = path_parts[0]
        host_from_path = path_parts[1] if len(path_parts) > 1 else None

        # Combine netloc and path for model identifier if netloc is part of it
        # (e.g., huggingface.co/DavidAU/...)
        if parsed.netloc:
            model_name = (
                f"{parsed.netloc}{parsed.path.split('@')[0]}"
                if parsed.path
                else parsed.netloc
            )
        else:
            model_name = model_identifier_from_path  # Should not happen if "://" is present and scheme is not file

        host = host_from_path  # Host from path takes precedence if specified with @
        if (
            not host and provider == "ollama"
        ):  # Default host for ollama if not specified
            host = Config.OLLAMA_HOST

        query_params: Optional[Dict[str, Any]] = None
        if parsed.query:
            query_params = {}
            for key, value_list in parse_qs(parsed.query).items():
                value = value_list[0]  # Take the first value for each param
                try:
                    # Attempt to convert to float or int if possible
                    if "." in value:
                        query_params[key] = float(value)
                    else:
                        query_params[key] = int(value)
                except ValueError:
                    # Keep as string if conversion fails
                    if value.lower() == "true":
                        query_params[key] = True
                    elif value.lower() == "false":
                        query_params[key] = False
                    else:
                        query_params[key] = value

        return provider, model_name, host, query_params

    def _clean_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes messages with empty or whitespace-only content, except possibly the last one if it's an assistant placeholder."""
        cleaned = []
        for i, msg in enumerate(messages):
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip() == "":
                if (
                    i == len(messages) - 1 and msg.get("role") == "assistant"
                ):  # Keep placeholder
                    cleaned.append(msg)
                continue  # Skip other empty messages
            cleaned.append(msg)
        return cleaned

    def safe_generate_text(
        self,
        logger: Any,
        messages: List[Dict[str, Any]],
        model_uri: str,
        seed_override: int = -1,
        output_format: Optional[
            Literal["json"]
        ] = None,  # Changed from _Format to output_format
        min_word_count: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Ensures the LLM response is not empty/whitespace and meets a minimum word count.
        Retries with modified prompts if initial attempts fail.

        Args:
            logger: Logger instance.
            messages: List of message dictionaries for the LLM.
            model_uri: The URI string of the model to use.
            seed_override: Specific seed for this generation, or -1 for default.
            output_format: Optional. If "json", instructs capable models to output JSON.
            min_word_count: Minimum number of words required in the response.

        Returns:
            The list of messages including the LLM's successful response.
        """
        current_messages = self._clean_messages(messages)

        max_retries_sgt = 3
        for attempt in range(max_retries_sgt):
            effective_seed = (
                seed_override if seed_override != -1 else (Config.SEED + attempt)
            )  # Vary seed on retries

            response_messages = self.chat_and_stream_response(
                logger, current_messages, model_uri, effective_seed, output_format
            )

            last_response_text = self.get_last_message_text(response_messages)
            word_count = len(last_response_text.split())

            if last_response_text.strip() != "" and word_count >= min_word_count:
                return response_messages  # Success

            # Prepare for retry
            logger.Log(
                f"SafeGenerateText (Attempt {attempt + 1}/{max_retries_sgt}): Response failed criteria "
                f"(Empty: {last_response_text.strip() == ''}, Words: {word_count}, Min: {min_word_count}). Retrying.",
                (
                    6 if attempt < max_retries_sgt - 1 else 7
                ),  # Log as warning, then error on final fail
            )

            # Modify current_messages for retry:
            # Remove the last assistant's failed response.
            # Add a user message asking to try again or be more verbose.
            if response_messages and response_messages[-1]["role"] == "assistant":
                current_messages = response_messages[
                    :-1
                ]  # Remove failed assistant response

            if word_count < min_word_count and last_response_text.strip() != "":
                current_messages.append(
                    self.build_user_query(
                        f"Your previous response was too short ({word_count} words, minimum {min_word_count}). Please elaborate and provide a more detailed answer."
                    )
                )
            else:  # Was empty
                current_messages.append(
                    self.build_user_query(
                        "Your previous response was empty. Please try generating a response again."
                    )
                )

            if attempt == max_retries_sgt - 1:  # Last attempt failed
                logger.Log(
                    f"SafeGenerateText: Failed to get adequate response for {model_uri} after {max_retries_sgt} attempts. Last response: '{last_response_text[:100]}...'",
                    7,
                )
                # Return the last failed response, but mark it or handle upstream
                return response_messages

        return response_messages  # Should be unreachable if loop logic is correct

    def safe_generate_json(
        self,
        logger: Any,
        messages: List[Dict[str, Any]],
        model_uri: str,
        seed_override: int = -1,
        required_attribs: List[str] = [],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Ensures the LLM response is valid JSON and contains required attributes.
        Retries with corrective prompts if parsing fails or attributes are missing.

        Args:
            logger: Logger instance.
            messages: List of message dictionaries for the LLM.
            model_uri: The URI string of the model to use.
            seed_override: Specific seed for this generation, or -1 for default.
            required_attribs: A list of attribute keys that must be present in the JSON response.

        Returns:
            A tuple containing the full message list (including the valid JSON response)
            and the parsed JSON dictionary.

        Raises:
            Exception if a valid JSON response cannot be obtained after max retries.
        """
        current_messages = self._clean_messages(messages)

        max_json_attempts = 3
        for attempt in range(max_json_attempts):
            effective_seed = (
                seed_override if seed_override != -1 else (Config.SEED + attempt)
            )

            response_messages = self.chat_and_stream_response(
                logger,
                current_messages,
                model_uri,
                effective_seed,
                output_format="json",
            )
            last_response_text = self.get_last_message_text(response_messages)

            try:
                # Pre-process common JSON issues (like markdown code blocks)
                cleaned_response_text = last_response_text.strip()
                if cleaned_response_text.startswith("```json"):
                    cleaned_response_text = cleaned_response_text[7:]
                if cleaned_response_text.endswith("```"):
                    cleaned_response_text = cleaned_response_text[:-3]
                cleaned_response_text = cleaned_response_text.strip()

                if not cleaned_response_text:
                    raise json.JSONDecodeError(
                        "Empty response cannot be parsed as JSON.", "", 0
                    )

                parsed_json = json.loads(cleaned_response_text)

                missing_attribs = [
                    attr for attr in required_attribs if attr not in parsed_json
                ]
                if not missing_attribs:
                    return response_messages, parsed_json  # Success

                # Attributes missing, prepare for retry
                logger.Log(
                    f"SafeGenerateJSON (Attempt {attempt + 1}/{max_json_attempts}): JSON response missing attributes: {missing_attribs}. Retrying.",
                    6,
                )
                current_messages = response_messages  # Keep history
                current_messages.append(
                    self.build_user_query(
                        f"Your JSON response was missing the following required attributes: {', '.join(missing_attribs)}. "
                        f"Please ensure your response is a valid JSON object containing all attributes: {', '.join(required_attribs)}."
                    )
                )

            except json.JSONDecodeError as e:
                logger.Log(
                    f"SafeGenerateJSON (Attempt {attempt + 1}/{max_json_attempts}): JSONDecodeError: {e}. Response: '{last_response_text[:200]}...'. Retrying.",
                    6,
                )
                current_messages = response_messages  # Keep history
                current_messages.append(
                    self.build_user_query(
                        Prompts.JSON_PARSE_ERROR.format(_Error=str(e))
                    )
                )

            if attempt == max_json_attempts - 1:  # Last attempt failed
                logger.Log(
                    f"SafeGenerateJSON: Failed to generate valid JSON for {model_uri} after {max_json_attempts} attempts.",
                    7,
                )
                raise Exception(
                    f"Failed to generate valid JSON for {model_uri} after {max_json_attempts} attempts. Last response: {last_response_text}"
                )

        # Should be unreachable
        raise Exception(f"SafeGenerateJSON logic error for {model_uri}")

    def chat_and_stream_response(
        self,
        logger: Any,
        messages: List[Dict[str, Any]],
        model_uri: str,
        seed_override: int = -1,
        output_format: Optional[Literal["json"]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Sends messages to the specified LLM and streams the response.
        Handles provider-specific logic and includes error retries for the LLM call itself.

        Args:
            logger: Logger instance.
            messages: List of message dictionaries.
            model_uri: The URI string of the model to use.
            seed_override: Specific seed, or -1 for default.
            output_format: If "json", attempts to instruct the model for JSON output.

        Returns:
            The updated list of messages, including the assistant's response.
        """
        provider, provider_model_name, model_host, model_options_from_uri = (
            self._get_model_and_provider(model_uri)
        )
        effective_seed = Config.SEED if seed_override == -1 else seed_override

        # Logging context length
        total_chars = sum(len(str(msg.get("content", ""))) for msg in messages)
        estimated_tokens = total_chars / 4.5  # Rough estimate
        logger.Log(
            f"Initiating LLM call to '{provider_model_name}' ({provider}). Seed: {effective_seed}. Format: {output_format}. Est. Tokens: ~{estimated_tokens:.0f}",
            4,
        )
        if estimated_tokens > (
            Config.OLLAMA_CTX * 0.8
        ):  # Warning if approaching context limit
            logger.Log(
                f"Warning: Estimated token count ({estimated_tokens:.0f}) is high for context window {Config.OLLAMA_CTX}.",
                6,
            )

        if Config.DEBUG:
            logger.Log(
                "--------- Message History START ---------", 0, stream=True
            )  # Use stream=True for multiline debug
            for i, msg in enumerate(messages):
                role = msg.get("role", "unknown")
                content_preview = (
                    str(msg.get("content", ""))[:100] + "..."
                    if len(str(msg.get("content", ""))) > 100
                    else str(msg.get("content", ""))
                )
                logger.Log(
                    f"  {i}. Role: {role}, Content: '{content_preview}'", 0, stream=True
                )
            logger.Log("--------- Message History END ---------", 0, stream=True)

        start_time = time.time()
        full_response_content = ""

        # Combine URI options with any dynamic options, URI options take precedence
        final_model_options = {}
        if Config.DEBUG_LEVEL > 1:
            logger.Log(
                f"Base model options from Config for {provider}: {final_model_options}",
                0,
            )  # Placeholder for future provider-specific base options
        if model_options_from_uri:
            final_model_options.update(model_options_from_uri)
            if Config.DEBUG_LEVEL > 1:
                logger.Log(
                    f"Updated model options with URI params: {final_model_options}", 0
                )

        max_llm_retries = 2  # Retries for the LLM call itself (e.g., network errors)
        for attempt in range(max_llm_retries):
            try:
                if provider == "ollama":
                    import ollama  # type: ignore

                    ollama_options = final_model_options.copy()
                    ollama_options["seed"] = effective_seed
                    if "num_ctx" not in ollama_options:
                        ollama_options["num_ctx"] = Config.OLLAMA_CTX
                    if output_format == "json":
                        ollama_options["format"] = "json"
                    if Config.DEBUG_LEVEL > 0:
                        logger.Log(f"Ollama options: {ollama_options}", 0)

                    stream = self.clients[model_uri].chat(
                        model=provider_model_name,
                        messages=messages,
                        stream=True,
                        options=ollama_options,
                    )
                    full_response_content = self._stream_response_internal(
                        stream, provider, logger
                    )

                elif provider == "google":
                    import google.generativeai as genai  # type: ignore
                    from google.generativeai.types import HarmCategory, HarmBlockThreshold  # type: ignore

                    # Format messages for Google API
                    google_messages = []
                    for msg in messages:
                        role = msg["role"]
                        if role == "system":
                            # Convert system messages to user prompts for Google
                            google_messages.append(
                                {"author": "user", "content": str(msg["content"])}
                            )
                        elif role == "assistant":
                            google_messages.append(
                                {"author": "model", "content": str(msg["content"])}
                            )
                        else:
                            # For user and other roles, use as is
                            google_messages.append(
                                {"author": role, "content": str(msg["content"])}
                            )

                    generation_config = (
                        genai.types.GenerationConfig(**final_model_options)
                        if final_model_options
                        else None
                    )
                    if output_format == "json" and generation_config:
                        generation_config.response_mime_type = "application/json"
                    elif output_format == "json":  # Create config if None
                        generation_config = genai.types.GenerationConfig(
                            response_mime_type="application/json"
                        )
                    if Config.DEBUG_LEVEL > 0:
                        logger.Log(
                            f"Google messages: {google_messages}, GenConfig: {generation_config}",
                            0,
                        )

                    safety_settings = {
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    }
                    stream = self.clients[model_uri].generate_content(
                        contents=google_messages,
                        stream=True,
                        safety_settings=safety_settings,
                        generation_config=generation_config,
                    )
                    full_response_content = self._stream_response_internal(
                        stream, provider, logger
                    )

                elif provider == "openrouter":
                    from Writer.Interface.OpenRouter import OpenRouter  # Local import

                    client: OpenRouter = self.clients[model_uri]
                    client.set_params(**final_model_options)  # Apply dynamic options
                    client.model = provider_model_name  # Ensure correct model is set

                    if output_format == "json":  # OpenRouter specific JSON mode
                        client.set_params(response_format={"type": "json_object"})

                    if Config.DEBUG_LEVEL > 0:
                        logger.Log(f"OpenRouter params: {client.__dict__}", 0)

                    # OpenRouter client currently doesn't stream in this implementation, directly gets content
                    full_response_content = client.chat(
                        messages=messages, seed=effective_seed
                    )
                    logger.Log(
                        f"OpenRouter full response received (length: {len(full_response_content)}).",
                        4,
                        stream=False,
                    )

                else:
                    raise NotImplementedError(
                        f"Provider '{provider}' not implemented in chat_and_stream_response."
                    )

                # If successful, break retry loop
                break

            except Exception as e:
                logger.Log(
                    f"LLM Call Error (Attempt {attempt + 1}/{max_llm_retries}) for {model_uri}: {e}",
                    7,
                )
                if attempt == max_llm_retries - 1:  # Last attempt
                    full_response_content = f"ERROR: LLM call failed after {max_llm_retries} attempts. Last error: {e}"
                    # Fall through to return the error message
                time.sleep(1.5**attempt)  # Exponential backoff

        end_time = time.time()
        duration = end_time - start_time
        response_tokens = len(full_response_content.split())  # Very rough token count
        tokens_per_sec = response_tokens / duration if duration > 0 else 0
        logger.Log(
            f"Generated response in {duration:.2f}s. Approx. {response_tokens} words, ~{tokens_per_sec:.2f} words/s.",
            4,
        )

        # Append assistant's response to the messages list
        updated_messages = messages + [
            {"role": "assistant", "content": full_response_content}
        ]

        # Save to Langchain debug log
        # Get caller function name dynamically for better log naming
        caller_function_name = "UnknownCaller"
        try:
            # stack returns a list of FrameInfo objects
            # FrameInfo(frame, filename, lineno, function, code_context, index)
            # We want the function name of the function that called ChatAndStreamResponse
            # The first frame (index 0) is ChatAndStreamResponse itself.
            # The second frame (index 1) is the function that called it (e.g. SafeGenerateText)
            # The third frame (index 2) is the function that called SafeGenerateText (e.g. GenerateOutline)
            # We'll construct a call path like "Grandparent.Parent.Child"
            call_stack = inspect.stack()
            relevant_frames = []
            for i in range(1, min(4, len(call_stack))):  # Max 3 levels up from current
                frame_name = call_stack[i].function
                if frame_name == "<module>":
                    frame_name = "Main"
                relevant_frames.append(frame_name)
            caller_function_name = (
                ".".join(reversed(relevant_frames)) if relevant_frames else "DirectCall"
            )

        except IndexError:
            pass  # Keep "UnknownCaller" if stack is too shallow

        logger.SaveLangchain(
            f"{caller_function_name}.{provider_model_name.replace('/','_')}",
            updated_messages,
        )

        return updated_messages

    def _stream_response_internal(
        self, stream_iterator: Any, provider: str, logger: Any
    ) -> str:
        """Helper to consolidate streaming logic for different providers."""
        response_text = ""
        chunk_count = 0
        stream_start_time = time.time()

        # Console output for streaming can be very verbose, toggle with DEBUG_LEVEL
        enable_console_stream = Config.DEBUG and Config.DEBUG_LEVEL > 1

        for chunk in stream_iterator:
            chunk_count += 1
            current_chunk_text = ""
            if provider == "ollama":
                current_chunk_text = chunk.get("message", {}).get("content", "")
            elif provider == "google":
                try:  # Google's stream can have empty chunks or non-text parts
                    current_chunk_text = chunk.text
                except Exception:  # ValueError, AttributeError if chunk has no .text
                    if Config.DEBUG_LEVEL > 1:
                        logger.Log(f"Google stream chunk without text: {chunk}", 0)
                    continue  # Skip if no text
            # Add other providers here
            else:
                # This should not be reached if called correctly
                logger.Log(f"Streaming not implemented for provider: {provider}", 7)
                break

            if current_chunk_text:
                response_text += current_chunk_text
                if enable_console_stream:
                    print(current_chunk_text, end="", flush=True)

        if enable_console_stream:
            print()  # Newline after streaming is done

        stream_duration = time.time() - stream_start_time
        logger.Log(
            f"Streamed {chunk_count} chunks for {provider} in {stream_duration:.2f}s.",
            0,
            stream=True,
        )  # Log this at a lower level
        return response_text

    def build_user_query(self, query_text: str) -> Dict[str, str]:
        """Constructs a user message dictionary."""
        return {"role": "user", "content": query_text}

    def build_system_query(self, query_text: str) -> Dict[str, str]:
        """Constructs a system message dictionary."""
        return {"role": "system", "content": query_text}

    def build_assistant_query(self, query_text: str) -> Dict[str, str]:
        """Constructs an assistant message dictionary."""
        return {"role": "assistant", "content": query_text}

    def get_last_message_text(self, messages: List[Dict[str, Any]]) -> str:
        """Safely retrieves the content of the last message."""
        if messages and isinstance(messages, list) and len(messages) > 0:
            last_msg = messages[-1]
            if isinstance(last_msg, dict):
                content = last_msg.get("content", "")
                return str(content) if content is not None else ""
        return ""

```

## File: `Writer/Outline/StoryElements.py`

```python
# File: AIStoryWriter/Writer/Outline/StoryElements.py
# Purpose: Generates foundational story elements (genre, theme, plot, characters, etc.)
#          based on an initial user prompt, using an LLM.

"""
This module is responsible for generating the core creative elements of a story.
It takes a user's initial story idea and uses an LLM, guided by an optimized prompt,
to flesh out details like genre, themes, a basic plot structure, character profiles,
and setting descriptions. These elements serve as a foundational guide for the
subsequent outlining and chapter/scene generation processes.
"""

from .. import Config  # Relative import for Config
from .. import Prompts  # Relative import for Prompts
from ..Interface.Wrapper import Interface  # Relative import for Interface
from ..PrintUtils import Logger  # Relative import for Logger


def GenerateStoryElements(
    interface: Interface, logger: Logger, user_story_prompt: str
) -> str:
    """
    Generates detailed story elements using an LLM based on the user's initial prompt.

    Args:
        interface: The LLM interface wrapper instance.
        logger: The Logger instance for logging messages.
        user_story_prompt: The user's initial idea or prompt for the story.

    Returns:
        A string containing the generated story elements, typically in Markdown format.
        Returns an empty string or error message if generation fails.
    """
    logger.Log("Initiating story elements generation...", 2)

    if not user_story_prompt or not user_story_prompt.strip():
        logger.Log("User story prompt is empty. Cannot generate story elements.", 5)
        return "// ERROR: User story prompt was empty. //"

    try:
        # Select the optimized prompt template for story elements
        prompt_template = Prompts.OPTIMIZED_STORY_ELEMENTS_GENERATION
        formatted_prompt = prompt_template.format(_UserStoryPrompt=user_story_prompt)

        messages = [
            interface.BuildSystemQuery(
                Prompts.DEFAULT_SYSTEM_PROMPT
            ),  # Use a capable system persona
            interface.BuildUserQuery(formatted_prompt),
        ]

        logger.Log(
            f"Sending request to LLM for story elements using model: {Config.MODEL_STORY_ELEMENTS_GENERATOR}",
            1,
        )

        # Use SafeGenerateText to ensure a substantive response
        response_messages = interface.SafeGenerateText(
            messages=messages,
            model_uri=Config.MODEL_STORY_ELEMENTS_GENERATOR,
            min_word_count=250,  # Expect a reasonably detailed output for story elements
        )

        elements_markdown: str = interface.GetLastMessageText(response_messages)

        if (
            not elements_markdown.strip() or "ERROR:" in elements_markdown
        ):  # Check if SafeGenerateText returned an error placeholder
            logger.Log("LLM failed to generate valid story elements.", 6)
            return f"// ERROR: LLM failed to generate story elements. Response: {elements_markdown[:200]}... //"

        logger.Log("Story elements generated successfully.", 2)
        if Config.DEBUG:
            logger.Log(
                f"Generated Story Elements (snippet):\n{elements_markdown[:500]}...", 1
            )

        return elements_markdown

    except Exception as e:
        logger.Log(
            f"An unexpected error occurred during story element generation: {e}", 7
        )
        # Log the full stack trace if in debug mode
        if Config.DEBUG:
            import traceback

            logger.Log(f"Traceback:\n{traceback.format_exc()}", 7)
        return f"// ERROR: An unexpected critical error occurred: {e} //"


# Example usage (typically not run directly from here)
if __name__ == "__main__":
    # This is for testing StoryElements.py itself
    # It requires a mock or actual Interface and Logger, and Config to be set up.

    # Setup mock Config for testing
    class MockConfig:
        MODEL_STORY_ELEMENTS_GENERATOR = (
            "ollama://mistral:latest"  # Use a fast local model for test
        )
        DEBUG = True
        DEBUG_LEVEL = 1  # For detailed logging during test

    Config = MockConfig()  # type: ignore
    Prompts.DEFAULT_SYSTEM_PROMPT = (
        "You are a helpful assistant."  # Simpler system prompt for test
    )

    # Mock Logger
    class MockLogger:
        def Log(self, item: str, level: int, stream_chunk: bool = False):
            print(f"LOG L{level}: {item}")

        def SaveLangchain(self, suffix: str, messages: list):
            print(f"LANGCHAIN_SAVE ({suffix}): {len(messages)} messages")

    # Mock Interface
    class MockInterface:
        def __init__(self, models, logger_instance):
            pass

        def BuildSystemQuery(self, q: str):
            return {"role": "system", "content": q}

        def BuildUserQuery(self, q: str):
            return {"role": "user", "content": q}

        def SafeGenerateText(self, messages: list, model_uri: str, min_word_count: int):
            print(
                f"SafeGenerateText called for {model_uri} with {len(messages)} messages. Min words: {min_word_count}"
            )
            # Simulate LLM response for story elements
            return [
                *messages,
                {
                    "role": "assistant",
                    "content": "# Story Title:\nThe Mockingbird's Shadow\n\n## Genre:\n- Mystery\n\n## Characters:\n### Main Character:\n- Name: Alex",
                },
            ]

        def GetLastMessageText(self, messages: list):
            return messages[-1]["content"] if messages else ""

    mock_logger = MockLogger()
    mock_interface = MockInterface(models=[], logger_instance=mock_logger)  # type: ignore

    test_prompt = "A detective in a cyberpunk city investigates a series of digital ghosts haunting the net."

    print("\n--- Testing GenerateStoryElements ---")
    generated_elements = GenerateStoryElements(mock_interface, mock_logger, test_prompt)  # type: ignore

    print("\n--- Generated Elements ---")
    print(generated_elements)

    print("\n--- Testing with empty prompt ---")
    empty_prompt_elements = GenerateStoryElements(mock_interface, mock_logger, "")  # type: ignore
    print(empty_prompt_elements)

```

## File: `Writer/Scene/ChapterByScene.py`

```python
import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Chapter.ChapterGenSummaryCheck
import Writer.Prompts
import Writer.Scene.ChapterOutlineToScenes
import Writer.Scene.ScenesToJSON
import Writer.Scene.SceneOutlineToScene



def ChapterByScene(Interface, _Logger, _ThisChapter:str, _Outline:str, _BaseContext:str = ""):

    # This function calls all other scene-by-scene generation functions and creates a full chapter based on the new scene pipeline.

    _Logger.Log(f"Starting Scene-By-Scene Chapter Generation Pipeline", 2)

    SceneBySceneOutline = Writer.Scene.ChapterOutlineToScenes.ChapterOutlineToScenes(Interface, _Logger, _ThisChapter, _Outline, _BaseContext=_BaseContext)

    SceneJSONList = Writer.Scene.ScenesToJSON.ScenesToJSON(Interface, _Logger, SceneBySceneOutline)


    # Now we iterate through each scene one at a time and write it, then add it to this rough chapter, which is then returned for further editing
    RoughChapter:str = ""
    for Scene in SceneJSONList:
        RoughChapter += Writer.Scene.SceneOutlineToScene.SceneOutlineToScene(Interface, _Logger, Scene, _Outline, _BaseContext)


    _Logger.Log(f"Starting Scene-By-Scene Chapter Generation Pipeline", 2)

    return RoughChapter

```

## File: `Writer/Scene/ChapterOutlineToScenes.py`

```python
import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Chapter.ChapterGenSummaryCheck
import Writer.Prompts


def ChapterOutlineToScenes(Interface, _Logger, _ThisChapter:str, _Outline:str, _BaseContext: str = ""):

    # We're now going to convert the chapter outline into a more detailed outline for each scene.
    # The scene by scene outline will be returned, JSONified, and then later converted into fully written scenes
    # These will then be concatenated into chapters and revised


    _Logger.Log(f"Splitting Chapter Into Scenes", 2)
    MesssageHistory: list = []
    MesssageHistory.append(Interface.BuildSystemQuery(Writer.Prompts.DEFAULT_SYSTEM_PROMPT))
    MesssageHistory.append(Interface.BuildUserQuery(Writer.Prompts.CHAPTER_TO_SCENES.format(_ThisChapter=_ThisChapter, _Outline=_Outline)))

    Response = Interface.SafeGenerateText(_Logger, MesssageHistory, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, _MinWordCount=100)
    _Logger.Log(f"Finished Splitting Chapter Into Scenes", 5)

    return Interface.GetLastMessageText(Response)

```

## File: `Writer/Scene/SceneOutlineToScene.py`

```python
import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Chapter.ChapterGenSummaryCheck
import Writer.Prompts


def SceneOutlineToScene(Interface, _Logger, _ThisSceneOutline:str, _Outline:str, _BaseContext: str = ""):

    # Now we're finally going to go and write the scene provided.


    _Logger.Log(f"Starting SceneOutline->Scene", 2)
    MesssageHistory: list = []
    MesssageHistory.append(Interface.BuildSystemQuery(Writer.Prompts.DEFAULT_SYSTEM_PROMPT))
    MesssageHistory.append(Interface.BuildUserQuery(Writer.Prompts.SCENE_OUTLINE_TO_SCENE.format(_SceneOutline=_ThisSceneOutline, _Outline=_Outline)))

    Response = Interface.SafeGenerateText(_Logger, MesssageHistory, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, _MinWordCount=100)
    _Logger.Log(f"Finished SceneOutline->Scene", 5)

    return Interface.GetLastMessageText(Response)

```

## File: `Writer/Scene/ScenesToJSON.py`

```python
import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Chapter.ChapterGenSummaryCheck
import Writer.Prompts


def ScenesToJSON(Interface, _Logger, _Scenes:str):

    # This function converts the given scene list (from markdown format, to a specified JSON format).

    _Logger.Log(f"Starting ChapterScenes->JSON", 2)
    MesssageHistory: list = []
    MesssageHistory.append(Interface.BuildSystemQuery(Writer.Prompts.DEFAULT_SYSTEM_PROMPT))
    MesssageHistory.append(Interface.BuildUserQuery(Writer.Prompts.SCENES_TO_JSON.format(_Scenes=_Scenes)))

    _, SceneList = Interface.SafeGenerateJSON(_Logger, MesssageHistory, Writer.Config.CHECKER_MODEL)
    _Logger.Log(f"Finished ChapterScenes->JSON ({len(SceneList)} Scenes Found)", 5)

    return SceneList

```

## File: `Writer/Config.py`

```python
# File: AIStoryWriter/Writer/Config.py
# Purpose: Central configuration for models, API keys, and generation parameters.

"""
Central configuration module for the AIStoryWriter.

This module defines default values for various settings, including:
- LLM model identifiers for different generation tasks.
- API keys and endpoint configurations (though sensitive keys are best loaded from .env).
- Parameters controlling the generation process (e.g., revision counts, seed).
- Flags for enabling/disabling features (e.g., debugging, translation).

These default values can be overridden by command-line arguments at runtime.
"""

# --- Model Configuration ---
# These will be populated by argparse or default values.
# It's recommended to use specific, descriptive names for each model's role.
# Example format: "provider://model_identifier@host?param1=value1¶m2=value2"
# or "provider://model_identifier" (host/params optional or provider-specific)

# Core Creative Models
INITIAL_OUTLINE_WRITER_MODEL: str = "huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF"
MODEL_STORY_ELEMENTS_GENERATOR: str = "ollama://llama3:latest" # For generating detailed story elements
MODEL_SCENE_OUTLINER: str = "ollama://llama3:latest" # For breaking chapters into scene outlines
MODEL_SCENE_NARRATIVE_GENERATOR: str = "ollama://llama3:latest" # For writing individual scene narratives
MODEL_CHAPTER_ASSEMBLY_REFINER: str = "ollama://llama3:latest" # For refining assembled scenes into a cohesive chapter

# Supporting and Utility Models
MODEL_CHAPTER_CONTEXT_SUMMARIZER: str = "ollama://llama3:latest" # For summarizing previous chapter/scene for context
REVISION_MODEL: str = "ollama://llama3:latest" # For providing critique/feedback
CHAPTER_REVISION_WRITER_MODEL: str = "ollama://llama3:latest" # For revising chapters based on feedback
EVAL_MODEL: str = "ollama://llama3:latest" # For evaluation tasks (e.g., IsComplete checks, JSON ratings)
INFO_MODEL: str = "ollama://llama3:latest" # For extracting story metadata (title, summary, tags)
SCRUB_MODEL: str = "ollama://llama3:latest" # For cleaning final output
CHECKER_MODEL: str = "ollama://llama3:latest" # For JSON parsing checks or simple validations
TRANSLATOR_MODEL: str = "ollama://llama3:latest" # For translation tasks

# --- API and System Settings ---
OLLAMA_CTX: int = 8192  # Default context window size for Ollama models
OLLAMA_HOST: str = "http://localhost:11434" # Default Ollama host URL

# API keys should ideally be loaded from environment variables (.env file)
# and not hardcoded here. The Wrapper.py handles loading from os.environ.
# Example (actual values will be loaded from .env by the interface):
# GOOGLE_API_KEY: Optional[str] = None
# OPENROUTER_API_KEY: Optional[str] = None

SEED: int = 42  # Default seed for reproducibility, can be overridden by argparse

# --- Generation Parameters ---
TRANSLATE_LANGUAGE: str = ""  # Target language for story translation (e.g., "French")
TRANSLATE_PROMPT_LANGUAGE: str = ""  # Target language for initial user prompt translation

# Outline revision settings
OUTLINE_MIN_REVISIONS: int = 1  # Minimum number of revision cycles for the main outline
OUTLINE_MAX_REVISIONS: int = 3  # Maximum number of revision cycles for the main outline

# Chapter/Scene revision settings
CHAPTER_NO_REVISIONS: bool = False  # If True, skips feedback/revision loops for assembled chapters
CHAPTER_MIN_REVISIONS: int = 1  # Minimum revision cycles for an assembled chapter
CHAPTER_MAX_REVISIONS: int = 3  # Maximum revision cycles for an assembled chapter

# Scene-specific generation parameters
SCENE_NARRATIVE_MIN_WORDS: int = 150  # Minimum expected word count for a single generated scene narrative
SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER: int = 3 # Minimum scenes expected from the scene outliner per chapter

# --- Feature Flags ---
SCRUB_NO_SCRUB: bool = False  # If True, skips the final scrubbing pass
# EXPAND_OUTLINE is deprecated as scene-by-scene is the primary flow.
# The main outline is now expected to be a chapter-level plot outline.
ENABLE_FINAL_EDIT_PASS: bool = True # Enables a global novel editing pass after all chapters are assembled

SCENE_GENERATION_PIPELINE: bool = True  # Master flag for scene-by-scene generation (should be True for this refactor)
OPTIMIZE_PROMPTS_VERSION: str = "v2.1" # Version for tracking prompt sets, useful for A/B testing or updates

# --- Output Settings ---
OPTIONAL_OUTPUT_NAME: str = ""  # If set, overrides default output filename generation

# --- Debugging and Logging ---
DEBUG: bool = False  # Enables verbose logging, including potentially printing full prompts/responses
DEBUG_LEVEL: int = 0 # 0: Normal, 1: Basic Debug, 2: Detailed Debug (e.g. stream chunks)

# --- Model Endpoint Overrides from Args (will be populated by Write.py) ---
# These are placeholders to indicate that Write.py will manage overriding the above defaults.
# For example, ARGS_INITIAL_OUTLINE_WRITER_MODEL: Optional[str] = None
# Actual update logic is in Write.py
```

## File: `Writer/LLMEditor.py`

```python
import Writer.PrintUtils
import Writer.Prompts

import json


def GetFeedbackOnOutline(Interface, _Logger, _Outline: str):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(Writer.Prompts.CRITIC_OUTLINE_INTRO))

    StartingPrompt: str = Writer.Prompts.CRITIC_OUTLINE_PROMPT.format(_Outline=_Outline)

    _Logger.Log("Prompting LLM To Critique Outline", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.REVISION_MODEL, _MinWordCount=70
    )
    _Logger.Log("Finished Getting Outline Feedback", 5)

    return Interface.GetLastMessageText(History)


def GetOutlineRating(
    Interface,
    _Logger,
    _Outline: str,
):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(Writer.Prompts.OUTLINE_COMPLETE_INTRO))

    StartingPrompt: str = Writer.Prompts.OUTLINE_COMPLETE_PROMPT.format(
        _Outline=_Outline
    )

    _Logger.Log("Prompting LLM To Get Review JSON", 5)

    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.EVAL_MODEL, _Format="json"
    )
    _Logger.Log("Finished Getting Review JSON", 5)

    Iters: int = 0
    while True:

        RawResponse = Interface.GetLastMessageText(History)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            Rating = json.loads(RawResponse)["IsComplete"]
            _Logger.Log(f"Editor Determined IsComplete: {Rating}", 5)
            return Rating
        except Exception as E:
            if Iters > 4:
                _Logger.Log("Critical Error Parsing JSON", 7)
                return False
            _Logger.Log("Error Parsing JSON Written By LLM, Asking For Edits", 7)
            EditPrompt: str = Writer.Prompts.JSON_PARSE_ERROR.format(_Error=E)
            History.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("Asking LLM TO Revise", 7)
            History = Interface.SafeGenerateText(
                _Logger, History, Writer.Config.EVAL_MODEL, _Format="json"
            )
            _Logger.Log("Done Asking LLM TO Revise JSON", 6)


def GetFeedbackOnChapter(Interface, _Logger, _Chapter: str, _Outline: str):

    # Setup Initial Context History
    History = []
    History.append(
        Interface.BuildSystemQuery(
            Writer.Prompts.CRITIC_CHAPTER_INTRO.format(_Chapter=_Chapter)
        )
    )

    # Disabled seeing the outline too.
    StartingPrompt: str = Writer.Prompts.CRITIC_CHAPTER_PROMPT.format(
        _Chapter=_Chapter, _Outline=_Outline
    )

    _Logger.Log("Prompting LLM To Critique Chapter", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    Messages = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.REVISION_MODEL
    )
    _Logger.Log("Finished Getting Chapter Feedback", 5)

    return Interface.GetLastMessageText(Messages)


# Switch this to iscomplete true/false (similar to outline)
def GetChapterRating(Interface, _Logger, _Chapter: str):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(Writer.Prompts.CHAPTER_COMPLETE_INTRO))

    StartingPrompt: str = Writer.Prompts.CHAPTER_COMPLETE_PROMPT.format(
        _Chapter=_Chapter
    )

    _Logger.Log("Prompting LLM To Get Review JSON", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.EVAL_MODEL
    )
    _Logger.Log("Finished Getting Review JSON", 5)

    Iters: int = 0
    while True:

        RawResponse = Interface.GetLastMessageText(History)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            Rating = json.loads(RawResponse)["IsComplete"]
            _Logger.Log(f"Editor Determined IsComplete: {Rating}", 5)
            return Rating
        except Exception as E:
            if Iters > 4:
                _Logger.Log("Critical Error Parsing JSON", 7)
                return False

            _Logger.Log("Error Parsing JSON Written By LLM, Asking For Edits", 7)
            EditPrompt: str = Writer.Prompts.JSON_PARSE_ERROR.format(_Error=E)
            History.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("Asking LLM TO Revise", 7)
            History = Interface.SafeGenerateText(
                _Logger, History, Writer.Config.EVAL_MODEL
            )
            _Logger.Log("Done Asking LLM TO Revise JSON", 6)

```

## File: `Writer/NovelEditor.py`

```python
import Writer.PrintUtils
import Writer.Config
import Writer.Prompts


def EditNovel(Interface, _Logger, _Chapters: list, _Outline: str, _TotalChapters: int):

    EditedChapters = _Chapters

    for i in range(1, _TotalChapters + 1):

        NovelText: str = ""
        for Chapter in EditedChapters:
            NovelText += Chapter

        Prompt: str = Writer.Prompts.CHAPTER_EDIT_PROMPT.format(
            _Chapter=EditedChapters[i], NovelText=NovelText, i=i
        )

        _Logger.Log(
            f"Prompting LLM To Perform Chapter {i} Second Pass In-Place Edit", 5
        )
        Messages = []
        Messages.append(Interface.BuildUserQuery(Prompt))
        Messages = Interface.SafeGenerateText(
            _Logger, Messages, Writer.Config.CHAPTER_WRITER_MODEL
        )
        _Logger.Log(f"Finished Chapter {i} Second Pass In-Place Edit", 5)

        NewChapter = Interface.GetLastMessageText(Messages)
        EditedChapters[i] = NewChapter
        ChapterWordCount = Writer.Statistics.GetWordCount(NewChapter)
        _Logger.Log(f"New Chapter Word Count: {ChapterWordCount}", 3)

    return EditedChapters

```

## File: `Writer/OutlineGenerator.py`

```python
# File: AIStoryWriter/Writer/OutlineGenerator.py
# Purpose: Generates the main story outline (chapter-by-chapter plot summaries)
#          based on user prompt and generated story elements. Includes a revision loop.

"""
This module orchestrates the generation of the overall story outline.
It takes the initial user prompt and the detailed story elements (from StoryElements.py)
to produce a chapter-by-chapter plot outline. This outline serves as the primary
roadmap for subsequent scene breakdown and narrative generation.

The process includes:
1. Extracting any overarching "base context" or meta-instructions from the user's prompt.
2. Generating an initial chapter-level outline using the story elements and user prompt.
3. Iteratively refining this outline using an LLM-based feedback and revision loop
   until it meets quality standards or a maximum number of revisions is reached.
"""

from typing import Tuple, List, Dict

from .. import Config  # Relative import for Config
from .. import Prompts  # Relative import for Prompts
from ..Interface.Wrapper import Interface  # Relative import for Interface
from ..PrintUtils import Logger  # Relative import for Logger
from .Outline import StoryElements  # Relative import for StoryElements module
from ..LLMEditor import (
    GetFeedbackOnOutline,
    GetOutlineRating,
)  # Relative import for LLMEditor functions


def GenerateOutline(
    interface: Interface, logger: Logger, user_story_prompt: str
) -> Tuple[str, str, str, str]:
    """
    Generates and refines the main story outline.

    Args:
        interface: The LLM interface wrapper instance.
        logger: The Logger instance for logging.
        user_story_prompt: The user's initial story idea.

    Returns:
        A tuple containing:
        - printable_full_outline (str): A string combining base context, story elements,
                                        and the final chapter-level outline for output.
        - story_elements_markdown (str): The generated story elements in Markdown.
        - final_chapter_level_outline (str): The refined chapter-by-chapter plot outline.
        - base_story_context (str): Extracted meta-instructions from the user prompt.
    """
    logger.Log("Starting Overall Story Outline Generation Process...", 2)

    # --- 1. Extract Base Context from User Prompt ---
    logger.Log("Extracting base context from user prompt...", 3)
    base_context_prompt_template = Prompts.GET_IMPORTANT_BASE_PROMPT_INFO
    formatted_base_context_prompt = base_context_prompt_template.format(
        _Prompt=user_story_prompt
    )

    base_context_messages = [
        interface.BuildSystemQuery(
            Prompts.DEFAULT_SYSTEM_PROMPT
        ),  # A capable system prompt
        interface.BuildUserQuery(formatted_base_context_prompt),
    ]

    # Using EVAL_MODEL as it's typically good for structured extraction/simple tasks
    base_context_response_messages = interface.SafeGenerateText(
        messages=base_context_messages,
        model_uri=Config.EVAL_MODEL,
        min_word_count=5,  # Expect at least "None found" or some points
    )
    base_story_context: str = interface.GetLastMessageText(
        base_context_response_messages
    )
    logger.Log(
        f"Base context extracted (snippet): {base_story_context[:150].strip()}...", 3
    )

    # --- 2. Generate Story Elements ---
    # This function is already robust and uses its own configured model
    story_elements_markdown = StoryElements.GenerateStoryElements(
        interface, logger, user_story_prompt
    )
    if "// ERROR:" in story_elements_markdown:
        logger.Log(
            "Critical error during story elements generation. Aborting outline generation.",
            7,
        )
        # Return placeholders to indicate failure
        return (
            "// ERROR IN STORY ELEMENTS //",
            story_elements_markdown,
            "// OUTLINE GENERATION ABORTED //",
            base_story_context,
        )

    # --- 3. Generate Initial Chapter-Level Outline ---
    logger.Log("Generating initial chapter-level outline...", 3)
    initial_outline_prompt_template = Prompts.OPTIMIZED_OVERALL_OUTLINE_GENERATION
    formatted_initial_outline_prompt = initial_outline_prompt_template.format(
        _UserStoryPrompt=user_story_prompt,
        _StoryElementsMarkdown=story_elements_markdown,
    )

    initial_outline_messages = [
        interface.BuildSystemQuery(Prompts.DEFAULT_SYSTEM_PROMPT),
        interface.BuildUserQuery(formatted_initial_outline_prompt),
    ]

    initial_outline_response_messages = interface.SafeGenerateText(
        messages=initial_outline_messages,
        model_uri=Config.INITIAL_OUTLINE_WRITER_MODEL,
        min_word_count=200,  # Expect a substantial outline
    )
    current_outline: str = interface.GetLastMessageText(
        initial_outline_response_messages
    )

    if not current_outline.strip() or "// ERROR:" in current_outline:
        logger.Log("LLM failed to generate a valid initial outline.", 6)
        return (
            f"{base_story_context}\n\n{story_elements_markdown}\n\n// ERROR: INITIAL OUTLINE FAILED //",
            story_elements_markdown,
            "// ERROR: INITIAL OUTLINE FAILED //",
            base_story_context,
        )
    logger.Log("Initial chapter-level outline generated successfully.", 3)

    # --- 4. Revision Loop for Overall Outline ---
    logger.Log("Starting outline revision loop...", 2)
    revision_iteration = 0
    # Start history with the system prompt and the assistant's first outline generation
    current_revision_history: List[Dict[str, str]] = [
        interface.BuildSystemQuery(Prompts.DEFAULT_SYSTEM_PROMPT),
        # We don't include the user's prompt for OPTIMIZED_OVERALL_OUTLINE_GENERATION in history
        # because ReviseOutline will receive _CurrentOutline and _Feedback directly.
        # The history for ReviseOutline starts fresh or with the last specific revision interaction.
        # For LLMEditor.GetFeedbackOnOutline, it builds its own small history.
    ]
    # To give ReviseOutline context, its history should be the one that led to current_outline.
    # So, initial_outline_response_messages contains the full exchange for the first outline.
    current_revision_history_for_revise_func = initial_outline_response_messages

    while revision_iteration < Config.OUTLINE_MAX_REVISIONS:
        revision_iteration += 1
        logger.Log(
            f"Outline Revision Iteration {revision_iteration}/{Config.OUTLINE_MAX_REVISIONS}",
            3,
        )

        feedback_on_outline = GetFeedbackOnOutline(interface, logger, current_outline)
        logger.Log(
            f"Feedback received for outline (iteration {revision_iteration}).", 3
        )
        if Config.DEBUG:
            logger.Log(
                f"Outline Feedback (Iter {revision_iteration}):\n{feedback_on_outline[:300]}...",
                1,
            )

        # GetOutlineRating returns True if complete/good, False otherwise
        is_outline_complete = GetOutlineRating(interface, logger, current_outline)
        logger.Log(
            f"Outline 'IsComplete' rating (iteration {revision_iteration}): {is_outline_complete}",
            3,
        )

        if is_outline_complete and revision_iteration > Config.OUTLINE_MIN_REVISIONS:
            logger.Log(
                "Outline meets quality standards and minimum revisions. Exiting revision loop.",
                2,
            )
            break

        if (
            revision_iteration >= Config.OUTLINE_MAX_REVISIONS
        ):  # Check here to log before breaking
            logger.Log("Maximum outline revisions reached. Exiting revision loop.", 2)
            break

        logger.Log(
            f"Revising outline based on feedback (iteration {revision_iteration})...", 3
        )
        current_outline, current_revision_history_for_revise_func = (
            _revise_outline_internal(
                interface,
                logger,
                current_outline,
                feedback_on_outline,
                current_revision_history_for_revise_func,
            )
        )
        if "// ERROR:" in current_outline:
            logger.Log("Error during outline revision. Using previous version.", 6)
            # current_outline would retain its pre-error value due to how _revise_outline_internal returns
            break
        logger.Log(f"Outline revised (iteration {revision_iteration}).", 3)

    final_chapter_level_outline = current_outline
    logger.Log("Outline revision loop finished.", 2)

    # Assemble the full printable outline
    printable_full_outline = (
        f"# Base Story Context & Instructions\n{base_story_context}\n\n"
        f"---\n# Generated Story Elements\n{story_elements_markdown}\n\n"
        f"---\n# Final Chapter-Level Plot Outline\n{final_chapter_level_outline}"
    )

    logger.Log("Overall Story Outline Generation Process Complete.", 2)
    return (
        printable_full_outline,
        story_elements_markdown,
        final_chapter_level_outline,
        base_story_context,
    )


def _revise_outline_internal(
    interface: Interface,
    logger: Logger,
    current_outline_text: str,
    feedback_text: str,
    current_history_for_llm: List[Dict[str, str]],
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Internal helper to call the LLM for revising an outline.
    Manages the message history specifically for the revision call.
    """
    revision_prompt_template = Prompts.OUTLINE_REVISION_PROMPT
    formatted_revision_prompt = revision_prompt_template.format(
        _Outline=current_outline_text, _Feedback=feedback_text
    )

    # The history for a revision should ideally be the conversation that LED to the current_outline_text,
    # then the feedback, then the request to revise.
    # However, to keep it simpler and avoid overly long context, we can also just send the current outline and feedback.
    # The `current_history_for_llm` here is passed from the main loop, representing the conversation so far
    # that produced `current_outline_text`. We append the new user request for revision to this.

    messages_for_revision = current_history_for_llm[
        :
    ]  # Start with the history that produced the current outline
    # The last message in current_history_for_llm is the assistant's `current_outline_text`.
    # We now add a user message asking to revise it based on new feedback.
    # The `formatted_revision_prompt` itself contains the outline and feedback.
    # So, we can just append a new user query with formatted_revision_prompt.
    # However, standard practice is: System, User, Assistant, User, Assistant...
    # The current_history_for_llm ends with an assistant message (the outline).
    # So, we should append a user message.

    messages_for_revision.append(interface.BuildUserQuery(formatted_revision_prompt))
    # The LLM will see its previous output (the outline, as part of the prompt) and the new feedback.

    response_messages = interface.SafeGenerateText(
        messages=messages_for_revision,  # Send the continued conversation
        model_uri=Config.INITIAL_OUTLINE_WRITER_MODEL,  # Or a dedicated REVISION_MODEL if configured
        min_word_count=len(current_outline_text.split())
        // 2,  # Expect revision to be substantial
    )

    revised_outline_text: str = interface.GetLastMessageText(response_messages)

    if not revised_outline_text.strip() or "// ERROR:" in revised_outline_text:
        logger.Log(
            "LLM failed to generate a valid revised outline. Returning original.", 6
        )
        return (
            current_outline_text,
            current_history_for_llm,
        )  # Return original and its history

    return (
        revised_outline_text,
        response_messages,
    )  # Return new outline and its full generating history


# Example usage (typically not run directly from here)
if __name__ == "__main__":
    # This is for testing OutlineGenerator.py itself.
    # Requires mock or actual Interface, Logger, StoryElements, LLMEditor, Config, Prompts.

    class MockConfigOutline:
        INITIAL_OUTLINE_WRITER_MODEL = "ollama://mistral:latest"
        EVAL_MODEL = "ollama://mistral:latest"  # For base context and rating
        REVISION_MODEL = "ollama://mistral:latest"  # For feedback
        OUTLINE_MIN_REVISIONS = 0
        OUTLINE_MAX_REVISIONS = 1  # Quick test
        DEBUG = True
        DEBUG_LEVEL = 1

    Config = MockConfigOutline()  # type: ignore
    Prompts.DEFAULT_SYSTEM_PROMPT = "You are an assistant."

    class MockLoggerOutline:
        def Log(self, item: str, level: int, stream_chunk: bool = False):
            print(f"LOG L{level}: {item}")

        def SaveLangchain(self, suffix: str, messages: list):
            print(f"LANGCHAIN_SAVE ({suffix}): {len(messages)} messages")

    class MockStoryElements:
        @staticmethod
        def GenerateStoryElements(interface, logger, prompt):
            logger.Log("MockStoryElements.GenerateStoryElements called.", 1)
            return "# Mock Story Elements\n- Genre: Sci-Fi\n- Character: Captain Astra"

    StoryElements = MockStoryElements()  # type: ignore

    class MockLLMEditor:
        _feedback_count = 0
        _rating_val = False

        @staticmethod
        def GetFeedbackOnOutline(interface, logger, outline):
            MockLLMEditor._feedback_count += 1
            logger.Log(
                f"MockLLMEditor.GetFeedbackOnOutline called (call {MockLLMEditor._feedback_count}).",
                1,
            )
            if MockLLMEditor._feedback_count == 1:
                return "Feedback: Needs more detail in chapter 2."
            return "Feedback: Looks good now."

        @staticmethod
        def GetOutlineRating(interface, logger, outline):
            logger.Log(
                f"MockLLMEditor.GetOutlineRating called. Current rating val: {MockLLMEditor._rating_val}",
                1,
            )
            # Simulate improvement: first False, then True
            current_val = MockLLMEditor._rating_val
            MockLLMEditor._rating_val = True  # Next time it will be true
            return current_val

    # Monkey patch LLMEditor for testing this module
    import sys

    # Create a mock module for LLMEditor
    mock_llm_editor_module = type(sys)("LLMEditor")
    mock_llm_editor_module.GetFeedbackOnOutline = MockLLMEditor.GetFeedbackOnOutline  # type: ignore
    mock_llm_editor_module.GetOutlineRating = MockLLMEditor.GetOutlineRating  # type: ignore
    sys.modules["AIStoryWriter.LLMEditor"] = mock_llm_editor_module  # type: ignore
    # And update the local import
    GetFeedbackOnOutline = MockLLMEditor.GetFeedbackOnOutline  # type: ignore
    GetOutlineRating = MockLLMEditor.GetOutlineRating  # type: ignore

    class MockInterfaceOutline:
        def __init__(self, models, logger_instance):
            pass

        def BuildSystemQuery(self, q: str):
            return {"role": "system", "content": q}

        def BuildUserQuery(self, q: str):
            return {"role": "user", "content": q}

        _gen_text_call = 0

        def SafeGenerateText(self, messages: list, model_uri: str, min_word_count: int):
            MockInterfaceOutline._gen_text_call += 1
            print(
                f"MockInterface.SafeGenerateText called for {model_uri} (call {MockInterfaceOutline._gen_text_call}). Min words: {min_word_count}. Prompt: {messages[-1]['content'][:60]}..."
            )
            if "GET_IMPORTANT_BASE_PROMPT_INFO" in messages[-1]["content"]:
                return [
                    *messages,
                    {
                        "role": "assistant",
                        "content": "# Important Additional Context\n- Write in first person.",
                    },
                ]
            if "OPTIMIZED_OVERALL_OUTLINE_GENERATION" in messages[-1]["content"]:
                return [
                    *messages,
                    {
                        "role": "assistant",
                        "content": "# Chapter 1\nPlot A\n# Chapter 2\nPlot B",
                    },
                ]
            if (
                "OUTLINE_REVISION_PROMPT" in messages[-1]["content"]
            ):  # Simulate revision
                return [
                    *messages,
                    {
                        "role": "assistant",
                        "content": "# Chapter 1\nPlot A revised\n# Chapter 2\nPlot B with more detail.",
                    },
                ]
            # Fallback for GetFeedback/GetRating if they use SafeGenerateText
            if "CRITIC_OUTLINE_PROMPT" in messages[-1]["content"]:
                return [
                    *messages,
                    {
                        "role": "assistant",
                        "content": MockLLMEditor.GetFeedbackOnOutline(
                            self, MockLoggerOutline(), "dummy outline"
                        ),
                    },
                ]
            if "OUTLINE_COMPLETE_PROMPT" in messages[-1]["content"]:
                is_complete = MockLLMEditor.GetOutlineRating(
                    self, MockLoggerOutline(), "dummy outline"
                )
                return [
                    *messages,
                    {
                        "role": "assistant",
                        "content": json.dumps({"IsComplete": is_complete}),
                    },
                ]
            return [
                *messages,
                {"role": "assistant", "content": "Default mock response."},
            ]

        def GetLastMessageText(self, messages: list):
            return messages[-1]["content"] if messages else ""

    mock_logger_outline = MockLoggerOutline()
    mock_interface_outline = MockInterfaceOutline(models=[], logger_instance=mock_logger_outline)  # type: ignore

    test_user_prompt = "A space opera about a lost kitten."

    print("\n--- Testing GenerateOutline ---")
    full_outline, elements, chapter_outline, base_ctx = GenerateOutline(mock_interface_outline, mock_logger_outline, test_user_prompt)  # type: ignore

    print("\n--- Results ---")
    print(f"Base Context:\n{base_ctx}")
    print(f"\nStory Elements:\n{elements}")
    print(f"\nFinal Chapter-Level Outline:\n{chapter_outline}")
    # print(f"\nPrintable Full Outline:\n{full_outline}") # This can be very long

```

## File: `Writer/PrintUtils.py`

```python
# File: AIStoryWriter/Writer/PrintUtils.py
# Purpose: Provides logging utilities with timestamping, leveling, and file output.
#          Includes functionality to save Langchain message history for debugging.

import termcolor  # type: ignore
import datetime
import os
import json
from typing import List, Dict, Optional, IO

# Attempt to import Config for DEBUG_LEVEL, handle if not available during early init
try:
    from .. import Config
except ImportError:
    # Mock Config if it's not available (e.g., if PrintUtils is used standalone for some reason)
    class MockConfig:
        DEBUG = False
        DEBUG_LEVEL = 0

    Config = MockConfig()  # type: ignore


class Logger:
    """
    Handles logging of messages to console and file with different levels.
    Also supports saving Langchain message sequences for debugging.
    """

    def __init__(self, log_file_prefix: str = "Logs", log_to_console: bool = True):
        self.log_to_console = log_to_console
        self.log_dir_prefix: str = ""
        self.log_path: str = ""
        self.file_handler: Optional[IO[str]] = None
        self.langchain_log_id_counter: int = 0
        self.log_items_buffer: List[str] = []  # In-memory buffer for recent logs

        self._initialize_logging(log_file_prefix)

    def _initialize_logging(self, log_file_prefix: str) -> None:
        """Sets up the log directory and main log file."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.log_dir_prefix = os.path.join(
                log_file_prefix, f"Generation_{timestamp}"
            )

            langchain_debug_dir = os.path.join(self.log_dir_prefix, "LangchainDebug")
            os.makedirs(langchain_debug_dir, exist_ok=True)

            self.log_path = os.path.join(self.log_dir_prefix, "Main.log")
            self.file_handler = open(self.log_path, "a", encoding="utf-8")

            self.Log(f"Logger initialized. Log directory: {self.log_dir_prefix}", 0)
        except OSError as e:
            # Fallback if directory creation fails (e.g. permissions)
            print(
                f"Error initializing logger directory: {e}. Logging to console only.",
                file=sys.stderr,
            )
            self.file_handler = None
            self.log_dir_prefix = ""  # Ensure no file operations are attempted

    def SaveLangchain(
        self, langchain_id_suffix: str, langchain_messages: List[Dict[str, str]]
    ) -> None:
        """
        Saves a Langchain message sequence to JSON and Markdown files for debugging.

        Args:
            langchain_id_suffix: A descriptive suffix for the log files (e.g., "ModuleName.FunctionName").
            langchain_messages: The list of message dictionaries to save.
        """
        if (
            not self.log_dir_prefix or not self.file_handler
        ):  # Logging to file disabled or failed
            if Config.DEBUG:
                print(
                    f"Debug (Console Only): Would save Langchain for {langchain_id_suffix}. Messages: {len(langchain_messages)}",
                    file=sys.stderr,
                )
            return

        current_log_id = self.langchain_log_id_counter
        self.langchain_log_id_counter += 1

        # Sanitize langchain_id_suffix to be a valid filename part
        safe_suffix = "".join(
            c if c.isalnum() or c in [".", "_"] else "_" for c in langchain_id_suffix
        )
        base_filename = f"{current_log_id:03d}_{safe_suffix}"[
            :200
        ]  # Cap filename length

        json_file_path = os.path.join(
            self.log_dir_prefix, "LangchainDebug", f"{base_filename}.json"
        )
        md_file_path = os.path.join(
            self.log_dir_prefix, "LangchainDebug", f"{base_filename}.md"
        )

        try:
            # Save JSON version
            with open(json_file_path, "w", encoding="utf-8") as f_json:
                json.dump(langchain_messages, f_json, indent=2, ensure_ascii=False)

            # Save Markdown version
            md_content = [f"# Debug LangChain: {base_filename}\n"]
            md_content.append(f"**Source Suffix:** `{langchain_id_suffix}`\n")
            md_content.append(
                f"**Timestamp:** `{datetime.datetime.now().isoformat()}`\n"
            )
            md_content.append("---\n")

            for msg_idx, message in enumerate(langchain_messages):
                role = message.get("role", "unknown_role")
                content = str(message.get("content", ""))  # Ensure content is string

                md_content.append(f"## Message {msg_idx + 1}: Role `{role}`\n")
                # Use text block for content to handle ``` within content
                md_content.append("```text")
                md_content.append(content if content.strip() else "[EMPTY CONTENT]")
                md_content.append("```\n")

            with open(md_file_path, "w", encoding="utf-8") as f_md:
                f_md.write("\n".join(md_content))

            self.Log(
                f"Saved Langchain debug data for '{base_filename}'", 1
            )  # Lowered log level for this
        except IOError as e:
            self.Log(f"Error saving Langchain debug data for '{base_filename}': {e}", 6)
        except Exception as e_gen:  # Catch any other unexpected error
            self.Log(
                f"Unexpected error saving Langchain debug for '{base_filename}': {e_gen}",
                7,
            )

    def SaveStory(
        self, story_content: str, filename: str = "Generated_Story.md"
    ) -> None:
        """Saves the provided story content to a file in the log directory."""
        if not self.log_dir_prefix or not self.file_handler:
            if Config.DEBUG:
                print(
                    f"Debug (Console Only): Would save story '{filename}'. Content length: {len(story_content)}",
                    file=sys.stderr,
                )
            return

        # Sanitize filename
        safe_filename = "".join(
            c if c.isalnum() or c in [".", "_", "-"] else "_" for c in filename
        )
        story_file_path = os.path.join(self.log_dir_prefix, safe_filename)

        try:
            with open(story_file_path, "w", encoding="utf-8") as f_story:
                f_story.write(story_content)
            self.Log(f"Story content saved to: {story_file_path}", 2)
        except IOError as e:
            self.Log(f"Error saving story content to '{story_file_path}': {e}", 6)

    def Log(self, item: str, level: int, stream_chunk: bool = False) -> None:
        """
        Logs a message to the console (if enabled) and to the main log file.

        Args:
            item: The message string to log.
            level: An integer indicating the log level (0-7).
                   Higher numbers indicate higher severity or importance.
                   0: Trace/Verbose, 1: Debug, 2: Info, 3: Notice,
                   4: Warning, 5: Error, 6: Critical, 7: Fatal/Alert
            stream_chunk: If True, indicates this is part of a streamed response.
                          May be handled differently for console output to avoid clutter.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[
            :-3
        ]  # Milliseconds
        log_entry = f"[{level}] [{timestamp}] {item}"

        # Write to file if handler is available
        if self.file_handler and not self.file_handler.closed:
            try:
                self.file_handler.write(log_entry + "\n")
                self.file_handler.flush()  # Ensure it's written immediately for tailing
            except Exception as e:
                # If file logging fails, print an error to console and disable file handler
                if self.log_to_console:
                    print(
                        f"CRITICAL: Failed to write to log file '{self.log_path}': {e}. Further file logging disabled.",
                        file=sys.stderr,
                    )
                self.file_handler.close()  # type: ignore # Close it to prevent further attempts
                self.file_handler = None

        # Add to in-memory buffer (e.g., for showing recent logs on error)
        self.log_items_buffer.append(log_entry)
        if len(self.log_items_buffer) > 200:  # Keep last 200 logs
            self.log_items_buffer.pop(0)

        # Print to console if enabled
        if self.log_to_console:
            # Conditional printing for stream chunks to reduce console noise
            # Only print stream chunks if DEBUG mode is on and DEBUG_LEVEL is high enough
            if stream_chunk and not (Config.DEBUG and Config.DEBUG_LEVEL > 1):
                return  # Skip console output for this stream chunk

            color_map = {
                0: "grey",  # Trace
                1: "cyan",  # Debug (was grey, changed for better visibility)
                2: "green",  # Info
                3: "blue",  # Notice
                4: "yellow",  # Warning
                5: "red",  # Error
                6: "magenta",  # Critical (was yellow)
                7: "red",  # Fatal (attrs=['bold'] could be added)
            }
            attrs_map = {7: ["bold"]}

            color = color_map.get(level, "white")  # Default to white
            attrs = attrs_map.get(level)

            try:
                colored_log_entry = termcolor.colored(log_entry, color, attrs=attrs)
                print(colored_log_entry)
            except Exception:  # termcolor might not be available or fail
                print(log_entry)

    def GetRecentLogs(self, count: int = 20) -> List[str]:
        """Returns the most recent 'count' log entries from the buffer."""
        return self.log_items_buffer[-count:]

    def Close(self) -> None:
        """Closes the log file handler if it's open."""
        if self.file_handler and not self.file_handler.closed:
            self.Log("Logger shutting down. Closing log file.", 0)
            self.file_handler.close()
            self.file_handler = None

    def __del__(self) -> None:
        self.Close()


# Example usage (typically not run directly from here)
if __name__ == "__main__":
    # This is for testing PrintUtils.py itself
    Config.DEBUG = True  # Enable debug mode for this test
    Config.DEBUG_LEVEL = 2  # Show stream chunks

    test_logger = Logger(log_file_prefix="TestLogs")
    test_logger.Log("This is a trace message (level 0).", 0)
    test_logger.Log("This is a debug message (level 1).", 1)
    test_logger.Log("This is an info message (level 2).", 2)
    test_logger.Log("This is a notice message (level 3).", 3)
    test_logger.Log("This is a warning message (level 4).", 4)
    test_logger.Log("This is an error message (level 5).", 5)
    test_logger.Log("This is a critical message (level 6).", 6)
    test_logger.Log("This is a fatal message (level 7).", 7)

    test_logger.Log("Simulating a stream chunk...", 2, stream_chunk=True)
    test_logger.Log("Another stream chunk...", 2, stream_chunk=True)

    mock_langchain_messages = [
        {"role": "system", "content": "You are an assistant."},
        {"role": "user", "content": "Hello, world!"},
        {"role": "assistant", "content": "Hello to you too! ```code``` example."},
    ]
    test_logger.SaveLangchain("Test.ExampleFunction", mock_langchain_messages)
    test_logger.SaveStory("# My Test Story\n\nOnce upon a time...", "TestStory.md")

    print("\nRecent logs:")
    for entry in test_logger.GetRecentLogs(5):
        print(entry)

    test_logger.Close()
    print("Test logger closed. Check TestLogs directory.")

```

## File: `Writer/Prompts.py`

```python
# File: AIStoryWriter/Writer/Prompts.py
# Purpose: Central repository for all optimized LLM prompt templates.

"""
Optimized LLM prompt templates for AIStoryWriter.

This module contains meticulously crafted prompts designed to:
- Elicit high-quality, vivid, and human-like prose.
- Reduce redundancy and improve narrative coherence.
- Facilitate scene-by-scene generation with smooth transitions.
- Guide LLMs for effective outlining, context summarization, and revision.
- Address pacing and ensure focus on crucial plot points.

Each prompt is versioned implicitly by its content and the `OPTIMIZE_PROMPTS_VERSION`
in Config.py.
"""

# --- System Prompts ---
DEFAULT_SYSTEM_PROMPT: str = """
You are an expert creative writing assistant, recognized for your ability to craft vivid narratives, develop compelling characters, and ensure coherent plot progression. Your prose is engaging, sophisticated, and indistinguishable from that of a seasoned human author. You excel at maintaining consistent tone, pacing, and character voice throughout a story. You are also adept at understanding and following complex instructions for structuring and refining literary works.
"""

# --- Story Foundation Prompts ---
OPTIMIZED_STORY_ELEMENTS_GENERATION: str = """
Based on the user's story idea below, please generate a comprehensive set of story elements.
Your response must be in well-structured Markdown format.

**User's Story Idea:**
<UserStoryPrompt>
{_UserStoryPrompt}
</UserStoryPrompt>

**Required Story Elements (Provide rich, descriptive details for each):**

# Story Title:
(Suggest a compelling title)

## Genre:
- **Primary Genre**: (e.g., Science Fiction, Fantasy, Mystery)
- **Subgenre/Tropes**: (e.g., Space Opera, Urban Fantasy, Hardboiled Detective, Coming-of-Age)

## Core Themes:
- **Central Idea(s) or Message(s)**: (What underlying messages or questions does the story explore?)

## Target Pacing:
- **Overall Pace**: (e.g., Fast-paced with constant action, Deliberate and character-focused, Mix of slow-burn suspense and explosive climaxes)
- **Pacing Variation**: (How should pacing shift across the story's acts or key sequences?)

## Desired Writing Style:
- **Narrative Voice/Tone**: (e.g., Lyrical and introspective, Gritty and direct, Whimsical and humorous, Ominous and suspenseful)
- **Descriptive Language**: (e.g., Richly detailed environments, Focus on sensory experiences, Sparse and impactful)
- **Sentence Structure & Vocabulary**: (e.g., Complex and varied, Short and punchy, Evocative and literary)

## Plot Synopsis (Five-Act Structure preferred):
- **Exposition**: (Introduction of main characters, setting, initial conflict/inciting incident)
- **Rising Action**: (Series of events escalating conflict, developing characters, building tension)
- **Climax**: (The turning point, highest tension, where the main conflict comes to a head)
- **Falling Action**: (Immediate consequences of the climax, tying up subplots)
- **Resolution**: (The new normal, lingering questions, thematic takeaways)

## Setting(s):
(Describe at least one primary setting in detail. Add more if central to the plot.)
### Setting 1: [Name of Setting]
- **Time Period**: (e.g., Distant future, Alternate present, Specific historical era)
- **Location Details**: (e.g., A decaying megacity on Mars, A hidden magical academy in modern London, A remote, storm-swept island)
- **Culture & Society**: (Key cultural norms, societal structure, technology level, belief systems)
- **Atmosphere & Mood**: (The dominant feeling the setting should evoke: e.g., oppressive, wondrous, dangerous, melancholic)

## Primary Conflict:
- **Type**: (e.g., Character vs. Character, Character vs. Society, Character vs. Nature, Character vs. Self, Character vs. Technology/Supernatural)
- **Detailed Description**: (What is the central struggle? Who are the opposing forces? What are the stakes?)

## Key Symbolism (Optional, but encouraged):
### Symbol 1:
- **Symbol**: (The object, concept, or character)
- **Intended Meaning/Representation**: (What deeper ideas does it represent?)

## Characters:
### Main Character 1:
- **Name**:
- **Archetype/Role**: (e.g., The Reluctant Hero, The Mentor, The Anti-Hero)
- **Physical Description**: (Distinctive features, general appearance, style)
- **Personality Traits**: (Key positive and negative traits, quirks, fears, desires)
- **Background/History**: (Relevant past experiences shaping them)
- **Motivations & Goals**: (What drives them through the story?)
- **Internal Conflict**: (Their primary inner struggle)
- **Potential Character Arc**: (How might they change or grow?)

(Repeat for other Main Characters if any)

### Supporting Character 1 (Example - provide 3-5 key supporting characters):
- **Name**:
- **Relationship to Main Character(s)**:
- **Role in Story**: (e.g., Ally, Antagonist, Foil, Comic Relief, Catalyst)
- **Brief Description**: (Key traits, appearance, motivation)

Ensure your output is detailed, imaginative, and provides a strong foundation for a compelling narrative. Avoid generic descriptions; aim for unique and memorable elements.
"""

OPTIMIZED_OVERALL_OUTLINE_GENERATION: str = """
Based on the user's story idea and the detailed story elements provided, generate a chapter-by-chapter plot outline for a novel.
The outline should be engaging, well-paced, and clearly delineate the narrative progression for each chapter.

**User's Story Idea:**
<UserStoryPrompt>
{_UserStoryPrompt}
</UserStoryPrompt>

**Detailed Story Elements:**
<StoryElementsMarkdown>
{_StoryElementsMarkdown}
</StoryElementsMarkdown>

**Instructions for the Outline:**
1.  **Structure**: Present the outline as a list of chapters (e.g., "Chapter 1: [Chapter Title/Theme]", "Chapter 2: [Chapter Title/Theme]", etc.).
2.  **Content per Chapter**: For each chapter, provide a concise summary (3-5 sentences) covering:
    *   Key plot events that occur.
    *   Significant character actions, decisions, or development.
    *   How the chapter contributes to the overall plot and themes.
    *   The intended pacing and tone for the chapter (e.g., "Builds suspense leading to a minor confrontation," "Focuses on character introspection after a major loss").
    *   A clear hook or transition into the next chapter.
3.  **Narrative Arc**: Ensure the outline follows a clear narrative arc (e.g., five-act structure if specified in elements, or a similar logical progression). Pay attention to the exposition, rising action, climax, falling action, and resolution across the chapters.
4.  **Pacing**: Distribute plot points effectively to maintain reader engagement. Vary pacing as appropriate for the story's needs.
5.  **Character Development**: Show, through chapter events, how main characters evolve, face challenges, and pursue their goals.
6.  **Cohesion**: Ensure chapters flow logically from one to the next, building upon previous events.
7.  **Vividness**: Even in summary form, use evocative language to hint at the story's atmosphere and potential.

Output the entire outline in Markdown format.
"""

# --- Scene-Level Prompts ---
OPTIMIZED_CHAPTER_TO_SCENES_BREAKDOWN: str = """
You are tasked with breaking down a chapter's plot outline into a sequence of distinct, detailed scenes.
This will serve as a blueprint for writing the chapter.

**Overall Story Outline (for context):**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Plot Outline for Chapter {_ChapterNumber}:**
<ChapterPlotOutline>
{_ChapterPlotOutline}
</ChapterPlotOutline>

**Context from Previous Chapter (if applicable):**
<PreviousChapterContextSummary>
{_PreviousChapterContextSummary}
</PreviousChapterContextSummary>

**Instructions:**
Generate a JSON list where each element is an object representing a single scene. Each scene object must include the following keys:
-   `"scene_number_in_chapter"`: (Integer) e.g., 1, 2, 3.
-   `"scene_title"`: (String) A brief, evocative title for the scene.
-   `"setting_description"`: (String) Detailed description of the location, time of day, and prevailing atmosphere (e.g., "A dimly lit, rain-slicked alleyway at midnight, smelling of refuse and despair. The only light comes from a flickering neon sign.").
-   `"characters_present"`: (List of Strings) Names of characters actively participating in this scene.
-   `"character_goals_moods"`: (String) Brief description of what each key character present wants to achieve or their emotional state at the start of the scene.
-   `"key_events_actions"`: (List of Strings) Bullet points describing the critical plot developments, actions, or discoveries that *must* occur in this scene. Be specific.
-   `"dialogue_points"`: (List of Strings) Key topics of conversation or specific impactful lines of dialogue that should be included.
-   `"pacing_note"`: (String) Suggested pacing for the scene (e.g., "Fast-paced action sequence," "Slow, tense dialogue exchange," "Quick, transitional scene," "Introspective and reflective").
-   `"tone"`: (String) The dominant emotional tone the scene should convey (e.g., "Suspenseful," "Romantic," "Tragic," "Hopeful," "Humorous").
-   `"purpose_in_chapter"`: (String) How this scene specifically contributes to the chapter's overall objectives (e.g., "Introduces a new obstacle," "Reveals a character's hidden motive," "Escalates the central conflict of the chapter").
-   `"transition_out_hook"`: (String) How the scene should end to effectively lead into the next scene or provide a minor cliffhanger/point of reflection if it's the chapter's end.

Ensure a minimum of {SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER} scenes are outlined for this chapter. The scenes should logically progress the chapter's plot as described in its outline. Be creative and add depth.

**Output ONLY the JSON list of scene objects.** Do not include any other text, narration, or markdown formatting outside the JSON structure.
"""

OPTIMIZED_SCENE_NARRATIVE_GENERATION: str = """
Your task is to write a compelling and vivid narrative for the scene detailed below.
Adhere closely to the provided blueprint, ensuring the scene is engaging, well-paced, and contributes effectively to the story.

**Overall Story Context (abbreviated):**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Immediate Previous Context (from last scene/chapter end):**
<PreviousSceneContextSummary>
{_PreviousSceneContextSummary}
</PreviousSceneContextSummary>

**Current Chapter:** {_ChapterNumber}
**Scene Number in Chapter:** {_SceneNumberInChapter}

**Scene Blueprint:**
-   **Title**: "{_SceneTitle}"
-   **Setting**: {_SceneSettingDescription}
-   **Characters Present & Their Immediate State**: {_SceneCharactersPresentAndGoals}
-   **Key Events/Actions to Depict**: {_SceneKeyEvents}
-   **Essential Dialogue Points/Topics**: {_SceneDialogueHighlights}
-   **Intended Pacing**: {_ScenePacingNote}
-   **Dominant Tone**: {_SceneTone}
-   **Scene's Purpose**: {_ScenePurposeInChapter}
-   **Concluding Hook/Transition**: {_SceneTransitionOutHook}

**Writing Instructions:**
1.  **Immersive Setting**: Bring the setting to life with vivid sensory details (sight, sound, smell, touch, taste where appropriate). Establish the atmosphere effectively.
2.  **Character Actions & Voice**: Ensure character actions are logical and their dialogue is distinctive, reflecting their personalities, motivations, and current emotional states as per the blueprint.
3.  **Integrate Key Elements**: Naturally weave the specified "Key Events/Actions" and "Dialogue Points" into the narrative. These are mandatory plot beats.
4.  **Pacing and Tone**: Masterfully control the pacing and maintain the specified tone throughout the scene. Use sentence structure, description length, and action/dialogue balance to achieve this.
5.  **Show, Don't Tell**: Use actions, dialogue, internal thoughts (if POV allows), and descriptions to convey information and emotion, rather than stating it directly.
6.  **Prose Quality**: Employ rich vocabulary, varied sentence structures, and strong verbs. Strive for human-like, engaging, and descriptive prose. Avoid clichés and filler words.
7.  **Dialogue Craft**: Dialogue should be realistic for the characters and situation, reveal character, and advance the plot or develop relationships.
8.  **Smooth Transitions**: Conclude the scene by fulfilling the "Concluding Hook/Transition" to ensure a natural flow to what comes next.
9.  **Length**: Aim for a substantial scene, typically {SCENE_NARRATIVE_MIN_WORDS} words or more, unless the "Pacing_Note" suggests a very brief scene.

Produce ONLY the narrative text for this single scene. Do not include titles, author notes, or any meta-commentary.
"""

# --- Context and Transition Prompts ---
OPTIMIZED_PREVIOUS_CHAPTER_SUMMARY_FOR_CONTEXT: str = """
Analyze the provided text of a completed chapter and the overall story outline.
Generate a concise yet comprehensive summary focusing *only* on elements crucial for writing the *immediately following* chapter.

**Completed Chapter Text (Chapter {_ChapterNumberOfCompletedChapter}):**
<CompletedChapterText>
{_CompletedChapterText}
</CompletedChapterText>

**Overall Story Outline (for broader context):**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Your summary should highlight:**
1.  **Key Plot Advancements**: What major events occurred and what are their direct consequences leading into the next chapter?
2.  **Character States at Chapter End**: What is the emotional, physical, and situational state of the main characters as this chapter concludes? Note any significant decisions made or changes they underwent.
3.  **Unresolved Threads/New Questions**: What immediate conflicts, mysteries, or questions are left open that the next chapter might address?
4.  **Thematic Resonance**: Briefly note any thematic elements that were strongly emphasized and might carry over.
5.  **Concluding Tone & Pacing**: What was the feeling and speed of the narrative at the very end of this chapter?

This summary's purpose is to ensure seamless continuity and narrative cohesion for the writer of the next chapter. Be specific and actionable.
Avoid re-telling the entire chapter; focus on the "hand-off" points.
"""

OPTIMIZED_PREVIOUS_SCENE_SUMMARY_FOR_CONTEXT: str = """
Analyze the provided text of a completed scene and its original outline.
Generate a very brief summary focusing *only* on the critical information needed to write the *immediately following scene* within the same chapter.

**Completed Scene Text:**
<CompletedSceneText>
{_CompletedSceneText}
</CompletedSceneText>

**Outline of the Completed Scene (for reference of its goals):**
<CurrentSceneOutline>
{_CurrentSceneOutline}
</CurrentSceneOutline>

**Your brief summary should capture:**
1.  **Final Action/Dialogue**: The last significant thing that happened or was said.
2.  **Immediate Character State/Decision**: The most relevant character's immediate disposition or choice at the scene's close.
3.  **Direct Hook/Setup**: Any explicit setup or unresolved micro-tension that the next scene is expected to pick up on.

This is for ultra-short-term continuity. Be extremely concise (1-2 sentences).
"""

# --- Feedback, Revision, and Evaluation Prompts ---
OPTIMIZED_CRITIC_OUTLINE_PROMPT: str = """
You are a discerning editor. Please provide a constructive critique of the following story outline.
Your feedback should be actionable and aim to elevate the outline's quality.

<OUTLINE>
{_Outline}
</OUTLINE>

**Evaluate the outline based on these criteria, providing specific examples where possible:**
1.  **Plot Cohesion & Clarity**:
    *   Is the overall plot logical and easy to follow?
    *   Are there any apparent plot holes, inconsistencies, or unresolved threads?
    *   Is the central conflict compelling and well-developed throughout the chapters?
2.  **Pacing & Structure**:
    *   Does the pacing seem appropriate for the story's genre and themes? Are key events given adequate development time?
    *   Are there sections that might feel rushed or dragged out?
    *   Does the distribution of exposition, rising action, climax, falling action, and resolution across chapters feel balanced and effective?
3.  **Chapter Flow & Transitions**:
    *   Do the chapter summaries suggest smooth and logical transitions from one chapter to the next?
    *   Does each chapter build effectively on the previous one?
4.  **Character Arcs & Development**:
    *   Are the main characters' goals, motivations, and potential arcs clear and engaging?
    *   Does the outline provide sufficient opportunities for meaningful character development?
5.  **Originality & Engagement**:
    *   Does the outline promise a fresh and engaging story, or does it rely heavily on predictable tropes without a unique spin?
    *   Are the stakes clear and compelling?
6.  **World-Building & Setting Integration** (if applicable):
    *   Is the setting well-integrated into the plot, or does it feel like a backdrop?
    *   Are unique aspects of the world effectively utilized in the chapter events?

**Format your feedback:**
-   Start with an overall assessment.
-   Then, provide specific points of critique, ideally referencing chapter numbers or specific plot points.
-   Offer concrete suggestions for improvement.
Maintain a professional and constructive tone.
"""

OPTIMIZED_CRITIC_CHAPTER_PROMPT: str = """
You are an experienced manuscript editor. Please provide a detailed and constructive critique of the following chapter text.
Your goal is to help the author improve its quality significantly.

**Chapter Text:**
<CHAPTER_TEXT>
{_ChapterText}
</CHAPTER_TEXT>

**Overall Story Outline (for context on the chapter's role):**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Critique the chapter based on the following aspects, providing specific examples from the text:**

1.  **Prose Quality & Style**:
    *   **Clarity & Conciseness**: Is the language clear? Are there run-on sentences, awkward phrasing, or unnecessary jargon?
    *   **Vividness & Imagery**: Does the writing create strong mental images? Is sensory detail used effectively? (Show, don't tell).
    *   **Word Choice**: Is the vocabulary precise, evocative, and appropriate for the tone? Are there repetitive words or phrases?
    *   **Sentence Fluency**: Do sentences flow well? Is there good variation in sentence structure and length?
    *   **Voice & Tone**: Is the narrative voice consistent and engaging? Does the tone match the chapter's content and intent?

2.  **Pacing & Flow**:
    *   **Intra-Chapter Pacing**: Does the pacing within the chapter feel right? Do scenes speed up or slow down appropriately?
    *   **Scene Transitions**: If the chapter contains multiple scenes, do they transition smoothly?
    *   **Overall Contribution**: Does this chapter advance the plot at an appropriate rate for its place in the story?

3.  **Characterization & Dialogue**:
    *   **Consistency**: Do characters behave and speak in ways consistent with their established personalities and motivations?
    *   **Depth**: Are characters (especially the POV character, if any) portrayed with believable thoughts and emotions?
    *   **Dialogue**: Is the dialogue natural, engaging, and purposeful? Does it reveal character, advance plot, or build tension? Does each character have a distinct voice?

4.  **Plot & Structure (within the chapter)**:
    *   **Scene Purpose**: Does each scene (if discernible) have a clear purpose?
    *   **Conflict & Tension**: Is there sufficient conflict or tension to keep the reader engaged? Is it resolved or escalated effectively within the chapter?
    *   **Alignment with Outline**: Does the chapter generally follow its intended purpose as per the overall story outline?

5.  **Reader Engagement**:
    *   **Immersion**: Does the chapter draw the reader into the story?
    *   **Emotional Impact**: Does it evoke the intended emotions?

**Structure your feedback:**
-   Begin with a general impression.
-   Address each criterion above with specific, actionable points. Quote short snippets from the text to illustrate your points where helpful.
-   Conclude with 2-3 key recommendations for revision.
Your tone should be professional, encouraging, and focused on tangible improvements.
"""

OUTLINE_REVISION_PROMPT: str = """
Please revise and enhance the following story outline based on the provided feedback.
Your goal is to address the critique and produce a stronger, more compelling outline.

**Original Outline:**
<OUTLINE>
{_Outline}
</OUTLINE>

**Feedback for Revision:**
<FEEDBACK>
{_Feedback}
</FEEDBACK>

**Instructions for Revision:**
1.  Carefully consider each point in the feedback.
2.  Incorporate the suggestions to improve plot cohesion, pacing, character arcs, and chapter flow.
3.  Add more detail where requested, or restructure sections as needed to address critiques.
4.  Expand upon existing ideas to add depth and originality if the feedback points to weaknesses there.
5.  Ensure the revised outline maintains a clear chapter-by-chapter structure with concise summaries for each, highlighting key events, character development, and transitions.
6.  The revised outline should be a complete, standalone version that supersedes the original.

As you revise, remember the core elements of good storytelling:
-   Compelling conflict.
-   Well-motivated characters with clear arcs.
-   Logical plot progression with appropriate pacing.
-   Engaging setting and atmosphere.
-   Smooth transitions between narrative segments.

Output the complete revised outline in Markdown format.
"""

CHAPTER_REVISION_PROMPT: str = """
Please revise the following chapter text based on the provided editorial feedback.
Your aim is to significantly improve the chapter's quality by addressing all points of critique.

**Original Chapter Text:**
<CHAPTER_CONTENT>
{_Chapter}
</CHAPTER_CONTENT>

**Editorial Feedback for Revision:**
<FEEDBACK>
{_Feedback}
</FEEDBACK>

**Instructions for Revision:**
1.  Thoroughly review the feedback, paying close attention to specific examples and suggestions.
2.  Rewrite, expand, or condense sections of the chapter as needed to address issues related to prose quality, pacing, characterization, dialogue, plot development, and engagement.
3.  Focus on "showing" rather than "telling," using vivid descriptions and actions.
4.  Ensure dialogue is natural, purposeful, and character-specific.
5.  Improve sentence flow, word choice, and eliminate redundancy.
6.  Strengthen transitions between scenes or paragraphs if weaknesses were noted.
7.  Do not simply make minor edits; undertake substantial revisions where the feedback indicates necessity.
8.  The output should be the complete, revised chapter text, ready for further review.

Do not reflect on the revisions or include any author notes. Just provide the improved chapter.
"""

# --- Evaluation & Utility Prompts ---
OUTLINE_COMPLETE_PROMPT: str = """
Analyze the following story outline.
<OUTLINE>
{_Outline}
</OUTLINE>

Based on your understanding of a well-structured and comprehensive story outline, determine if this outline meets a high standard of quality across the following criteria:
-   **Plot Cohesion & Clarity**: The plot is logical, clear, and engaging.
-   **Pacing & Structure**: The story's pacing and structural divisions (e.g., acts, chapter progression) are well-considered and effective.
-   **Chapter Flow & Transitions**: Chapters connect logically, and the narrative progresses smoothly.
-   **Character Arc Potential**: Main characters have clear motivations and opportunities for development.
-   **Detail & Sufficiency**: The outline provides enough detail per chapter to guide scene breakdown and writing.

Respond with a JSON object containing a single key "IsComplete" with a boolean value (true or false).
-   `true`: if the outline is largely complete, well-structured, and ready for detailed scene outlining.
-   `false`: if the outline has significant flaws in the criteria above and requires further revision.

**Example Response:**
`{{"IsComplete": true}}`

Provide ONLY the JSON response.
"""

CHAPTER_COMPLETE_PROMPT: str = """
Analyze the following chapter text.
<CHAPTER>
{_Chapter}
</CHAPTER>

Based on your understanding of high-quality fiction writing, determine if this chapter meets a publishable standard across these criteria:
-   **Prose Quality**: The writing is vivid, clear, engaging, and largely free of grammatical errors or awkward phrasing.
-   **Pacing & Flow**: The chapter is well-paced, and scenes/paragraphs transition smoothly.
-   **Characterization & Dialogue**: Characters are consistent and believable; dialogue is natural and purposeful.
-   **Plot Advancement**: The chapter effectively moves the plot forward according to its likely role in a larger narrative.
-   **Engagement**: The chapter is interesting and successfully evokes the intended mood/emotions.

Respond with a JSON object containing a single key "IsComplete" with a boolean value (true or false).
-   `true`: if the chapter is well-written and generally ready.
-   `false`: if the chapter has notable issues in the criteria above and needs revision.

**Example Response:**
`{{"IsComplete": false}}`

Provide ONLY the JSON response.
"""

CHAPTER_COUNT_PROMPT: str = """
Analyze the provided story outline below.
<OUTLINE>
{_Outline}
</OUTLINE>

Based on the structure and headings (e.g., "Chapter 1", "Chapter X"), determine the total number of distinct chapters in this outline.
Respond with a JSON object containing a single key "TotalChapters" with an integer value representing the count.

**Example Response:**
`{{"TotalChapters": 12}}`

If the outline is unclear or does not seem to be divided into chapters, return 0.
Provide ONLY the JSON response.
"""

GET_IMPORTANT_BASE_PROMPT_INFO: str = """
Carefully review the user's initial story prompt provided below.
<USER_PROMPT>
{_Prompt}
</USER_PROMPT>

Extract any specific instructions, constraints, or overarching visions mentioned by the user that are NOT part of the core plot/character ideas but are important for the *process* of writing or the *style* of the final story.
This includes things like:
-   Desired chapter length or total word count.
-   Specific formatting requests (e.g., for dialogue).
-   Explicit "do's" or "don'ts" regarding content or style.
-   Information about the target audience if mentioned.
-   Any meta-instructions about how the AI should behave or approach the task.

Present these extracted points as a Markdown list under the heading "# Important Additional Context".
If no such specific instructions are found, respond with "# Important Additional Context\n- None found."

Do NOT summarize the plot or story idea itself. Focus only on auxiliary instructions.
Keep your response concise.
"""

JSON_PARSE_ERROR: str = """
Your previous response was expected to be a valid JSON object, but it could not be parsed.
It produced the following error:
<ERROR_MESSAGE>
{_Error}
</ERROR_MESSAGE>

Please carefully review your intended JSON structure and ensure it is correctly formatted.
Common issues include:
-   Missing or extra commas.
-   Mismatched braces `{{}}` or brackets `[]`.
-   Keys or string values not enclosed in double quotes.
-   Unescaped special characters within strings.

Provide ONLY the corrected, valid JSON object as your entire response. Do not include any explanatory text before or after the JSON.
"""

# --- Specialized Prompts ---
GLOBAL_NOVEL_CHAPTER_EDIT_PROMPT: str = """
You are performing a global consistency and flow edit on Chapter {ChapterNum} of a novel.
Consider this chapter within the context of the overall story outline and the text of all preceding chapters.

**Overall Story Outline (for high-level plot and character arcs):**
<OverallStoryOutline>
{_OverallStoryOutline}
</OverallStoryOutline>

**Novel Text Leading Up To This Chapter:**
(This section may be very long if many prior chapters exist. Focus on the most recent 1-2 chapters if context is overwhelming)
<NovelTextSoFar>
{_NovelTextSoFar}
</NovelTextSoFar>

**Current Chapter {ChapterNum} for Editing:**
<ChapterTextToEdit>
{_ChapterTextToEdit}
</ChapterTextToEdit>

**Editing Focus:**
1.  **Continuity**: Ensure events, character knowledge, and established facts in this chapter are consistent with what has occurred in previous chapters and align with the overall outline.
2.  **Foreshadowing/Payoff**: If this chapter should set up future events (per outline) or resolve earlier foreshadowing, subtly enhance these elements.
3.  **Pacing within Global Arc**: Adjust descriptions, dialogue length, or action sequences to ensure this chapter's pacing contributes effectively to the novel's overall rhythm. Avoid making it feel too rushed or slow relative to its importance.
4.  **Thematic Resonance**: Strengthen thematic connections to the broader story.
5.  **Character Arc Progression**: Ensure character actions and internal states in this chapter are a logical step in their overall development as indicated by the outline and previous chapters.

**Instructions:**
-   Make surgical edits rather than wholesale rewrites, unless absolutely necessary for global consistency.
-   Preserve the core plot and events of the chapter.
-   Your output should be ONLY the revised text of Chapter {ChapterNum}.

Revised Chapter {ChapterNum} Text:
"""

OPTIMIZED_CONTENT_VS_OUTLINE_CHECK_PROMPT: str = """
You are an AI assistant tasked with verifying if a piece of generated content accurately reflects its guiding outline/plan.

**Guiding Outline/Plan for the Content:**
<REFERENCE_OUTLINE_OR_PLAN>
{_ReferenceOutlineOrPlan}
</REFERENCE_OUTLINE_OR_PLAN>

**Generated Content to Check:**
<GENERATED_CONTENT>
{_GeneratedContent}
</GENERATED_CONTENT>

**Task:**
Compare the "Generated Content" against the "Guiding Outline/Plan".
Respond with a JSON object containing the following fields:

{{
  "did_follow_outline": <boolean>,
  "alignment_score": <integer, 0-100, representing how well it followed, 100 is perfect>,
  "explanation": "<string, a brief explanation of your reasoning for the score and boolean value. Highlight key matches or deviations.>",
  "suggestions_for_improvement": "<string, if not perfectly aligned or if did_follow_outline is false, provide concise, actionable suggestions for the writer to better adhere to the plan in a revision. If it followed well, this can be minimal or state 'Excellent alignment.'>"
}}

-   `did_follow_outline`: `true` if the content substantially covers the key points and intent of the outline/plan; `false` otherwise. Minor creative liberties are acceptable if they don't contradict the core plan.
-   `alignment_score`: Your subjective assessment of adherence.
-   `explanation`: Justify your `did_follow_outline` and `alignment_score`.
-   `suggestions_for_improvement`: Focus on how to better meet the outline's goals.

Provide ONLY the JSON response.
"""

# --- Prompts for Scrubber, Translator, StoryInfo (can be similar to original or slightly optimized) ---
CHAPTER_SCRUB_PROMPT: str = """
Review the following chapter text.
<CHAPTER>
{_Chapter}
</CHAPTER>

Your task is to meticulously clean this text for final publication. This involves:
1.  Removing any leftover author notes, editorial comments, or bracketed instructions (e.g., "[Insert dramatic reveal here]", "TODO: Describe the sunset").
2.  Deleting any headings, subheadings, or outline markers that are not part of the narrative itself (e.g., "Scene 1:", "Character Development:", "Plot Point A:").
3.  Ensuring consistent formatting for dialogue (e.g., using standard quotation marks).
4.  Correcting any obvious typographical errors or formatting inconsistencies that might have been missed.

The goal is to produce pure, clean narrative text suitable for a reader.
Do not add, remove, or change the story content itself beyond these cleanup tasks.
Do not summarize, critique, or add any commentary.

Output ONLY the cleaned chapter text.
"""

STATS_PROMPT: str = """
Analyze the complete story context provided in previous messages (or the provided full outline).
Based on this, generate a JSON object with the following information:

{{
  "Title": "<string, A compelling and concise title for the story, ideally 3-8 words.>",
  "Summary": "<string, A 1-2 paragraph summary covering the main plot from beginning to end, including key conflicts and resolution.>",
  "Tags": "<string, A comma-separated list of 5-10 relevant keywords or tags that categorize the story (e.g., sci-fi, adventure, romance, betrayal, alien invasion, dystopian future).>",
  "OverallRating": "<integer, Your subjective overall quality score for the story based on its coherence, engagement, and creativity, from 0 to 100.>"
}}

Ensure your response is ONLY this JSON object, with no additional text before or after.
Strive for a creative and fitting title, a comprehensive yet succinct summary, and relevant tags.
"""

TRANSLATE_PROMPT: str = """
Translate the following text into { _Language}.
Focus on conveying the original meaning and tone accurately and naturally in {_Language}.
Do not add any commentary, interpretation, or formatting beyond what is necessary for a faithful translation.

<TEXT_TO_TRANSLATE>
{_Prompt}
</TEXT_TO_TRANSLATE>

Translated text:
"""

CHAPTER_TRANSLATE_PROMPT: str = """
Translate the following story chapter into {_Language}.
Preserve the narrative style, character voices, and emotional tone of the original as much as possible.
Ensure the translation is fluent and natural-sounding in {_Language}.

<CHAPTER_TEXT>
{_Chapter}
</CHAPTER_TEXT>

Translated Chapter Text in {_Language}:
"""
```

## File: `Writer/Scrubber.py`

```python
import Writer.PrintUtils
import Writer.Prompts


def ScrubNovel(Interface, _Logger, _Chapters: list, _TotalChapters: int):

    EditedChapters = _Chapters

    for i in range(_TotalChapters):

        Prompt: str = Writer.Prompts.CHAPTER_SCRUB_PROMPT.format(
            _Chapter=EditedChapters[i]
        )
        _Logger.Log(f"Prompting LLM To Perform Chapter {i+1} Scrubbing Edit", 5)
        Messages = []
        Messages.append(Interface.BuildUserQuery(Prompt))
        Messages = Interface.SafeGenerateText(
            _Logger, Messages, Writer.Config.SCRUB_MODEL
        )
        _Logger.Log(f"Finished Chapter {i+1} Scrubbing Edit", 5)

        NewChapter = Interface.GetLastMessageText(Messages)
        EditedChapters[i] = NewChapter
        ChapterWordCount = Writer.Statistics.GetWordCount(NewChapter)
        _Logger.Log(f"Scrubbed Chapter Word Count: {ChapterWordCount}", 3)

    return EditedChapters

```

## File: `Writer/Statistics.py`

```python
# File: AIStoryWriter/Writer/Statistics.py
# Purpose: Provides utility functions for text statistics, primarily word count.

"""
Utility functions for calculating simple text statistics.
Currently, this module focuses on word count, but could be expanded
for other metrics like sentence count, character count, readability scores, etc.
"""


def GetWordCount(text: str) -> int:
    """
    Calculates the number of words in a given string.
    Words are defined as sequences of characters separated by whitespace.

    Args:
        text: The input string.

    Returns:
        The total number of words in the string. Returns 0 for None or empty/whitespace-only strings.
    """
    if not text or not text.strip():
        return 0

    # Simple split by whitespace. This is a basic word count and doesn't
    # handle complex punctuation or hyphenation in a sophisticated way,
    # but is generally sufficient for LLM output estimation.
    words = text.split()
    return len(words)


# Example usage (not typically run directly from here)
if __name__ == "__main__":
    test_string_1 = "This is a simple test string with seven words."
    test_string_2 = "  Leading and trailing whitespace.  "
    test_string_3 = "OneWord"
    test_string_4 = ""
    test_string_5 = "    "  # Whitespace only
    test_string_6 = None  # type: ignore

    print(
        f"'{test_string_1}' -> Word count: {GetWordCount(test_string_1)}"
    )  # Expected: 7
    print(
        f"'{test_string_2}' -> Word count: {GetWordCount(test_string_2)}"
    )  # Expected: 4
    print(
        f"'{test_string_3}' -> Word count: {GetWordCount(test_string_3)}"
    )  # Expected: 1
    print(
        f"'{test_string_4}' -> Word count: {GetWordCount(test_string_4)}"
    )  # Expected: 0
    print(
        f"'{test_string_5}' -> Word count: {GetWordCount(test_string_5)}"
    )  # Expected: 0
    print(
        f"'{test_string_6}' -> Word count: {GetWordCount(test_string_6)}"
    )  # Expected: 0

    multi_line_string = """
    This is a
    multi-line string.
    It should count words correctly.
    """
    print(
        f"\nMulti-line string -> Word count: {GetWordCount(multi_line_string)}"
    )  # Expected: 10

    # Test with punctuation
    punctuation_string = "Hello, world! This is a test. (With parentheses)."
    # Basic split will count "world!" as one word, "parentheses)." as one word.
    print(
        f"'{punctuation_string}' -> Word count: {GetWordCount(punctuation_string)}"
    )  # Expected: 8

```

## File: `Writer/StoryInfo.py`

```python
import Writer.Config
import json


def GetStoryInfo(Interface, _Logger, _Messages: list):

    Prompt: str = Writer.Prompts.STATS_PROMPT

    _Logger.Log("Prompting LLM To Generate Stats", 5)
    Messages = _Messages
    Messages.append(Interface.BuildUserQuery(Prompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.INFO_MODEL, _Format="json"
    )
    _Logger.Log("Finished Getting Stats Feedback", 5)

    Iters: int = 0
    while True:

        RawResponse = Interface.GetLastMessageText(Messages)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            Dict = json.loads(RawResponse)
            return Dict
        except Exception as E:
            if Iters > 4:
                _Logger.Log("Critical Error Parsing JSON", 7)
                return {}
            _Logger.Log("Error Parsing JSON Written By LLM, Asking For Edits", 7)
            EditPrompt: str = (
                f"Please revise your JSON. It encountered the following error during parsing: {E}. Remember that your entire response is plugged directly into a JSON parser, so don't write **anything** except pure json."
            )
            Messages.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("Asking LLM TO Revise", 7)
            Messages = Interface.SafeGenerateText(
                _Logger, Messages, Writer.Config.INFO_MODEL, _Format="json"
            )
            _Logger.Log("Done Asking LLM TO Revise JSON", 6)

```

## File: `Writer/Translator.py`

```python
import Writer.PrintUtils
import Writer.Config
import Writer.Prompts


def TranslatePrompt(Interface, _Logger, _Prompt: str, _Language: str = "French"):

    Prompt: str = Writer.Prompts.TRANSLATE_PROMPT.format(
        _Prompt=_Prompt, _Language=_Language
    )
    _Logger.Log(f"Prompting LLM To Translate User Prompt", 5)
    Messages = []
    Messages.append(Interface.BuildUserQuery(Prompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.TRANSLATOR_MODEL, _MinWordCount=50
    )
    _Logger.Log(f"Finished Prompt Translation", 5)

    return Interface.GetLastMessageText(Messages)


def TranslateNovel(
    Interface, _Logger, _Chapters: list, _TotalChapters: int, _Language: str = "French"
):

    EditedChapters = _Chapters

    for i in range(_TotalChapters):

        Prompt: str = Writer.Prompts.CHAPTER_TRANSLATE_PROMPT.format(
            _Chapter=EditedChapters[i], _Language=_Language
        )
        _Logger.Log(f"Prompting LLM To Perform Chapter {i+1} Translation", 5)
        Messages = []
        Messages.append(Interface.BuildUserQuery(Prompt))
        Messages = Interface.SafeGenerateText(
            _Logger, Messages, Writer.Config.TRANSLATOR_MODEL
        )
        _Logger.Log(f"Finished Chapter {i+1} Translation", 5)

        NewChapter = Interface.GetLastMessageText(Messages)
        EditedChapters[i] = NewChapter
        ChapterWordCount = Writer.Statistics.GetWordCount(NewChapter)
        _Logger.Log(f"Translation Chapter Word Count: {ChapterWordCount}", 3)

    return EditedChapters

```

## File: `Write.py`

```python
#!/bin/python3

import argparse
import time
import datetime
import os
import json

import Writer.Config

import Writer.Interface.Wrapper
import Writer.PrintUtils
import Writer.Chapter.ChapterDetector
import Writer.Scrubber
import Writer.Statistics
import Writer.OutlineGenerator
import Writer.Chapter.ChapterGenerator
import Writer.StoryInfo
import Writer.NovelEditor
import Writer.Translator


# Setup Argparser
Parser = argparse.ArgumentParser()
Parser.add_argument("-Prompt", help="Path to file containing the prompt")
Parser.add_argument(
    "-Output",
    default="",
    type=str,
    help="Optional file output path, if none is speciifed, we will autogenerate a file name based on the story title",
)
Parser.add_argument(
    "-InitialOutlineModel",
    default=Writer.Config.INITIAL_OUTLINE_WRITER_MODEL,
    type=str,
    help="Model to use for writing the base outline content",
)
Parser.add_argument(
    "-ChapterOutlineModel",
    default=Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL,
    type=str,
    help="Model to use for writing the per-chapter outline content",
)
Parser.add_argument(
    "-ChapterS1Model",
    default=Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
    type=str,
    help="Model to use for writing the chapter (stage 1: plot)",
)
Parser.add_argument(
    "-ChapterS2Model",
    default=Writer.Config.CHAPTER_STAGE2_WRITER_MODEL,
    type=str,
    help="Model to use for writing the chapter (stage 2: character development)",
)
Parser.add_argument(
    "-ChapterS3Model",
    default=Writer.Config.CHAPTER_STAGE3_WRITER_MODEL,
    type=str,
    help="Model to use for writing the chapter (stage 3: dialogue)",
)
Parser.add_argument(
    "-ChapterS4Model",
    default=Writer.Config.CHAPTER_STAGE4_WRITER_MODEL,
    type=str,
    help="Model to use for writing the chapter (stage 4: final correction pass)",
)
Parser.add_argument(
    "-ChapterRevisionModel",
    default=Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
    type=str,
    help="Model to use for revising the chapter until it meets criteria",
)
Parser.add_argument(
    "-RevisionModel",
    default=Writer.Config.REVISION_MODEL,
    type=str,
    help="Model to use for generating constructive criticism",
)
Parser.add_argument(
    "-EvalModel",
    default=Writer.Config.EVAL_MODEL,
    type=str,
    help="Model to use for evaluating the rating out of 100",
)
Parser.add_argument(
    "-InfoModel",
    default=Writer.Config.INFO_MODEL,
    type=str,
    help="Model to use when generating summary/info at the end",
)
Parser.add_argument(
    "-ScrubModel",
    default=Writer.Config.SCRUB_MODEL,
    type=str,
    help="Model to use when scrubbing the story at the end",
)
Parser.add_argument(
    "-CheckerModel",
    default=Writer.Config.CHECKER_MODEL,
    type=str,
    help="Model to use when checking if the LLM cheated or not",
)
Parser.add_argument(
    "-TranslatorModel",
    default=Writer.Config.TRANSLATOR_MODEL,
    type=str,
    help="Model to use if translation of the story is enabled",
)
Parser.add_argument(
    "-Translate",
    default="",
    type=str,
    help="Specify a language to translate the story to - will not translate by default. Ex: 'French'",
)
Parser.add_argument(
    "-TranslatePrompt",
    default="",
    type=str,
    help="Specify a language to translate your input prompt to. Ex: 'French'",
)
Parser.add_argument("-Seed", default=12, type=int, help="Used to seed models.")
Parser.add_argument(
    "-OutlineMinRevisions",
    default=0,
    type=int,
    help="Number of minimum revisions that the outline must be given prior to proceeding",
)
Parser.add_argument(
    "-OutlineMaxRevisions",
    default=3,
    type=int,
    help="Max number of revisions that the outline may have",
)
Parser.add_argument(
    "-ChapterMinRevisions",
    default=0,
    type=int,
    help="Number of minimum revisions that the chapter must be given prior to proceeding",
)
Parser.add_argument(
    "-ChapterMaxRevisions",
    default=3,
    type=int,
    help="Max number of revisions that the chapter may have",
)
Parser.add_argument(
    "-NoChapterRevision", action="store_true", help="Disables Chapter Revisions"
)
Parser.add_argument(
    "-NoScrubChapters",
    action="store_true",
    help="Disables a final pass over the story to remove prompt leftovers/outline tidbits",
)
Parser.add_argument(
    "-ExpandOutline",
    action="store_true",
    default=True,
    help="Disables the system from expanding the outline for the story chapter by chapter prior to writing the story's chapter content",
)
Parser.add_argument(
    "-EnableFinalEditPass",
    action="store_true",
    help="Enable a final edit pass of the whole story prior to scrubbing",
)
Parser.add_argument(
    "-Debug",
    action="store_true",
    help="Print system prompts to stdout during generation",
)
Parser.add_argument(
    "-SceneGenerationPipeline",
    action="store_true",
    default=True,
    help="Use the new scene-by-scene generation pipeline as an initial starting point for chapter writing",
)
Args = Parser.parse_args()


# Measure Generation Time
StartTime = time.time()


# Setup Config
Writer.Config.SEED = Args.Seed

Writer.Config.INITIAL_OUTLINE_WRITER_MODEL = Args.InitialOutlineModel
Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL = Args.ChapterOutlineModel
Writer.Config.CHAPTER_STAGE1_WRITER_MODEL = Args.ChapterS1Model
Writer.Config.CHAPTER_STAGE2_WRITER_MODEL = Args.ChapterS2Model
Writer.Config.CHAPTER_STAGE3_WRITER_MODEL = Args.ChapterS3Model
Writer.Config.CHAPTER_STAGE4_WRITER_MODEL = Args.ChapterS4Model
Writer.Config.CHAPTER_REVISION_WRITER_MODEL = Args.ChapterRevisionModel
Writer.Config.EVAL_MODEL = Args.EvalModel
Writer.Config.REVISION_MODEL = Args.RevisionModel
Writer.Config.INFO_MODEL = Args.InfoModel
Writer.Config.SCRUB_MODEL = Args.ScrubModel
Writer.Config.CHECKER_MODEL = Args.CheckerModel
Writer.Config.TRANSLATOR_MODEL = Args.TranslatorModel

Writer.Config.TRANSLATE_LANGUAGE = Args.Translate
Writer.Config.TRANSLATE_PROMPT_LANGUAGE = Args.TranslatePrompt

Writer.Config.OUTLINE_MIN_REVISIONS = Args.OutlineMinRevisions
Writer.Config.OUTLINE_MAX_REVISIONS = Args.OutlineMaxRevisions

Writer.Config.CHAPTER_MIN_REVISIONS = Args.ChapterMinRevisions
Writer.Config.CHAPTER_MAX_REVISIONS = Args.ChapterMaxRevisions
Writer.Config.CHAPTER_NO_REVISIONS = Args.NoChapterRevision

Writer.Config.SCRUB_NO_SCRUB = Args.NoScrubChapters
Writer.Config.EXPAND_OUTLINE = Args.ExpandOutline
Writer.Config.ENABLE_FINAL_EDIT_PASS = Args.EnableFinalEditPass

Writer.Config.OPTIONAL_OUTPUT_NAME = Args.Output
Writer.Config.SCENE_GENERATION_PIPELINE = Args.SceneGenerationPipeline
Writer.Config.DEBUG = Args.Debug

# Get a list of all used providers
Models = [
    Writer.Config.INITIAL_OUTLINE_WRITER_MODEL,
    Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL,
    Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
    Writer.Config.CHAPTER_STAGE2_WRITER_MODEL,
    Writer.Config.CHAPTER_STAGE3_WRITER_MODEL,
    Writer.Config.CHAPTER_STAGE4_WRITER_MODEL,
    Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
    Writer.Config.EVAL_MODEL,
    Writer.Config.REVISION_MODEL,
    Writer.Config.INFO_MODEL,
    Writer.Config.SCRUB_MODEL,
    Writer.Config.CHECKER_MODEL,
    Writer.Config.TRANSLATOR_MODEL,
]
Models = list(set(Models))

# Setup Logger
SysLogger = Writer.PrintUtils.Logger()

# Initialize Interface
SysLogger.Log("Created OLLAMA Interface", 5)
Interface = Writer.Interface.Wrapper.Interface(Models)

# Load User Prompt
Prompt: str = ""
if Args.Prompt is None:
    raise Exception("No Prompt Provided")
with open(Args.Prompt, "r") as f:
    Prompt = f.read()


# If user wants their prompt translated, do so
if Writer.Config.TRANSLATE_PROMPT_LANGUAGE != "":
    Prompt = Writer.Translator.TranslatePrompt(
        Interface, SysLogger, Prompt, Writer.Config.TRANSLATE_PROMPT_LANGUAGE
    )


# Generate the Outline
Outline, Elements, RoughChapterOutline, BaseContext = (
    Writer.OutlineGenerator.GenerateOutline(
        Interface, SysLogger, Prompt, Writer.Config.OUTLINE_QUALITY
    )
)
BasePrompt = Prompt


# Detect the number of chapters
SysLogger.Log("Detecting Chapters", 5)
Messages = [Interface.BuildUserQuery(Outline)]
NumChapters: int = Writer.Chapter.ChapterDetector.LLMCountChapters(
    Interface, SysLogger, Interface.GetLastMessageText(Messages)
)
SysLogger.Log(f"Found {NumChapters} Chapter(s)", 5)


## Write Per-Chapter Outline
Prompt = f"""
Please help me expand upon the following outline, chapter by chapter.

```
{Outline}
```
    
"""
Messages = [Interface.BuildUserQuery(Prompt)]
ChapterOutlines: list = []
if Writer.Config.EXPAND_OUTLINE:
    for Chapter in range(1, NumChapters + 1):
        ChapterOutline, Messages = Writer.OutlineGenerator.GeneratePerChapterOutline(
            Interface, SysLogger, Chapter, Outline, Messages
        )
        ChapterOutlines.append(ChapterOutline)


# Create MegaOutline
DetailedOutline: str = ""
for Chapter in ChapterOutlines:
    DetailedOutline += Chapter
MegaOutline: str = f"""

# Base Outline
{Elements}

# Detailed Outline
{DetailedOutline}

"""

# Setup Base Prompt For Per-Chapter Generation
UsedOutline: str = Outline
if Writer.Config.EXPAND_OUTLINE:
    UsedOutline = MegaOutline


# Write the chapters
SysLogger.Log("Starting Chapter Writing", 5)
Chapters = []
for i in range(1, NumChapters + 1):

    Chapter = Writer.Chapter.ChapterGenerator.GenerateChapter(
        Interface,
        SysLogger,
        i,
        NumChapters,
        Outline,
        Chapters,
        Writer.Config.OUTLINE_QUALITY,
        BaseContext,
    )

    Chapter = f"### Chapter {i}\n\n{Chapter}"
    Chapters.append(Chapter)
    ChapterWordCount = Writer.Statistics.GetWordCount(Chapter)
    SysLogger.Log(f"Chapter Word Count: {ChapterWordCount}", 2)


# Now edit the whole thing together
StoryBodyText: str = ""
StoryInfoJSON: dict = {"Outline": Outline}
StoryInfoJSON.update({"StoryElements": Elements})
StoryInfoJSON.update({"RoughChapterOutline": RoughChapterOutline})
StoryInfoJSON.update({"BaseContext": BaseContext})

if Writer.Config.ENABLE_FINAL_EDIT_PASS:
    NewChapters = Writer.NovelEditor.EditNovel(
        Interface, SysLogger, Chapters, Outline, NumChapters
    )
NewChapters = Chapters
StoryInfoJSON.update({"UnscrubbedChapters": NewChapters})

# Now scrub it (if enabled)
if not Writer.Config.SCRUB_NO_SCRUB:
    NewChapters = Writer.Scrubber.ScrubNovel(
        Interface, SysLogger, NewChapters, NumChapters
    )
else:
    SysLogger.Log(f"Skipping Scrubbing Due To Config", 4)
StoryInfoJSON.update({"ScrubbedChapter": NewChapters})


# If enabled, translate the novel
if Writer.Config.TRANSLATE_LANGUAGE != "":
    NewChapters = Writer.Translator.TranslateNovel(
        Interface, SysLogger, NewChapters, NumChapters, Writer.Config.TRANSLATE_LANGUAGE
    )
else:
    SysLogger.Log(f"No Novel Translation Requested, Skipping Translation Step", 4)
StoryInfoJSON.update({"TranslatedChapters": NewChapters})


# Compile The Story
for Chapter in NewChapters:
    StoryBodyText += Chapter + "\n\n\n"


# Now Generate Info
Messages = []
Messages.append(Interface.BuildUserQuery(Outline))
Info = Writer.StoryInfo.GetStoryInfo(Interface, SysLogger, Messages)
Title = Info["Title"]
StoryInfoJSON.update({"Title": Info["Title"]})
Summary = Info["Summary"]
StoryInfoJSON.update({"Summary": Info["Summary"]})
Tags = Info["Tags"]
StoryInfoJSON.update({"Tags": Info["Tags"]})

print("---------------------------------------------")
print(f"Story Title: {Title}")
print(f"Summary: {Summary}")
print(f"Tags: {Tags}")
print("---------------------------------------------")

ElapsedTime = time.time() - StartTime


# Calculate Total Words
TotalWords: int = Writer.Statistics.GetWordCount(StoryBodyText)
SysLogger.Log(f"Story Total Word Count: {TotalWords}", 4)

StatsString: str = "Work Statistics:  \n"
StatsString += " - Total Words: " + str(TotalWords) + "  \n"
StatsString += f" - Title: {Title}  \n"
StatsString += f" - Summary: {Summary}  \n"
StatsString += f" - Tags: {Tags}  \n"
StatsString += f" - Generation Start Date: {datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}  \n"
StatsString += f" - Generation Total Time: {ElapsedTime}s  \n"
StatsString += f" - Generation Average WPM: {60 * (TotalWords/ElapsedTime)}  \n"

StatsString += "\n\nUser Settings:  \n"
StatsString += f" - Base Prompt: {BasePrompt}  \n"

StatsString += "\n\nGeneration Settings:  \n"
StatsString += f" - Generator: AIStoryGenerator_2024-06-27  \n"
StatsString += (
    f" - Base Outline Writer Model: {Writer.Config.INITIAL_OUTLINE_WRITER_MODEL}  \n"
)
StatsString += (
    f" - Chapter Outline Writer Model: {Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL}  \n"
)
StatsString += f" - Chapter Writer (Stage 1: Plot) Model: {Writer.Config.CHAPTER_STAGE1_WRITER_MODEL}  \n"
StatsString += f" - Chapter Writer (Stage 2: Char Development) Model: {Writer.Config.CHAPTER_STAGE2_WRITER_MODEL}  \n"
StatsString += f" - Chapter Writer (Stage 3: Dialogue) Model: {Writer.Config.CHAPTER_STAGE3_WRITER_MODEL}  \n"
StatsString += f" - Chapter Writer (Stage 4: Final Pass) Model: {Writer.Config.CHAPTER_STAGE4_WRITER_MODEL}  \n"
StatsString += f" - Chapter Writer (Revision) Model: {Writer.Config.CHAPTER_REVISION_WRITER_MODEL}  \n"
StatsString += f" - Revision Model: {Writer.Config.REVISION_MODEL}  \n"
StatsString += f" - Eval Model: {Writer.Config.EVAL_MODEL}  \n"
StatsString += f" - Info Model: {Writer.Config.INFO_MODEL}  \n"
StatsString += f" - Scrub Model: {Writer.Config.SCRUB_MODEL}  \n"
StatsString += f" - Seed: {Writer.Config.SEED}  \n"
# StatsString += f" - Outline Quality: {Writer.Config.OUTLINE_QUALITY}  \n"
StatsString += f" - Outline Min Revisions: {Writer.Config.OUTLINE_MIN_REVISIONS}  \n"
StatsString += f" - Outline Max Revisions: {Writer.Config.OUTLINE_MAX_REVISIONS}  \n"
# StatsString += f" - Chapter Quality: {Writer.Config.CHAPTER_QUALITY}  \n"
StatsString += f" - Chapter Min Revisions: {Writer.Config.CHAPTER_MIN_REVISIONS}  \n"
StatsString += f" - Chapter Max Revisions: {Writer.Config.CHAPTER_MAX_REVISIONS}  \n"
StatsString += f" - Chapter Disable Revisions: {Writer.Config.CHAPTER_NO_REVISIONS}  \n"
StatsString += f" - Disable Scrubbing: {Writer.Config.SCRUB_NO_SCRUB}  \n"


# Save The Story To Disk
SysLogger.Log("Saving Story To Disk", 3)
os.makedirs("Stories", exist_ok=True)
FName = f"Stories/Story_{Title.replace(' ', '_')}"
if Writer.Config.OPTIONAL_OUTPUT_NAME != "":
    FName = Writer.Config.OPTIONAL_OUTPUT_NAME
with open(f"{FName}.md", "w", encoding="utf-8") as F:
    Out = f"""
{StatsString}

---

Note: An outline of the story is available at the bottom of this document.
Please scroll to the bottom if you wish to read that.

---
# {Title}

{StoryBodyText}


---
# Outline
```
{Outline}
```
"""
    SysLogger.SaveStory(Out)
    F.write(Out)

# Save JSON
with open(f"{FName}.json", "w", encoding="utf-8") as F:
    F.write(json.dumps(StoryInfoJSON, indent=4))


```

## File: `requirements.txt`

```text
ollama
termcolor
google.generativeai
python-dotenv
```

