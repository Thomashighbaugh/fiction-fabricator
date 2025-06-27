You are an expert software engineer and master of bleeding edge Python, especially as use to work with all things Langchain, tasked with fixing the issues and improvements listed below according to the workflow for the project source code listed below.

## Issues and Improvements

1. In generating each scene and chapter we should ensure that the content is coherent and follows a logical progression. This can be achieved by:
   - Using a consistent theme or motif throughout the Chapter
   - summarizing key points at the end of each scene to reinforce the narrative and character arcs
   - summarizing and creating a record of previously generated scenes to maintain continuity and coherence across the chapter and from there across the book
2. Change all instances of the project name to "Fiction Fabricator" in the codebase.
3. Remove translation functionality from the codebase, as it is not needed at this time.
4. Implement a critique and revision element for each time the LLM returns content, in which:
   - The LLM is prompt to critique the output it has provided within the context of the current novel
   - The LLM is then prompted with the critique and the original output and asked to revise the original output based on the critique while remaining true to the story and overall intention of the novel.
5. Remove OpenAI and Anthropic, replacing them with the API endpoints listed below:
   - Gemini
   - MIstral
   - Cerebras
   - groqcloud
6. The user, upon running the program, should be able to select which LLM they want to use for the project. This can be achieved by (you will do them all not pick just one):
   - Creating a configuration file that allows the user to specify their preferred LLM
   - Implementing a selection menu at the start of the program that allows the user to choose their LLM
   - Ensuring that the codebase is modular enough to easily switch between different LLMs without significant changes to the code structure
7. Make sure to utilize existing functionality within the codebase before implementing features with unnecessary complexity by introducing it as new code that is not already present in the codebase. This can be achieved by:
   - Reviewing the existing codebase to identify reusable components and functions
   - Refactoring existing code to improve modularity and reusability
   - Documenting existing functionality to make it easier for future developers to understand and utilize
   - Making use of Langchain's existing components and integrations to avoid reinventing the wheel

## Refactoring Workflow

The manner in which you will address the **Issues and Improvements** in refactoring the project will procede according to the following workflow:

- **Step 1** You will providing a **Reactoring Plan** first for my approval. The reactoring plan will include:
  - files added or removed
  - files to be changed and what those changes will be
  - any additional considerations
  - any points for clarification you would like clearly listed under their own heading
- **Step 2** - If I do not approve you or ask for clarifications, I will respond in kind and you will present a modified **Refactoring Plan** for approval.
- **Step 3** - Once the refactoring plan is approved you will proceed outputting the factored files **one complete and fully corrected according to the approved plan** file at a time await me response with "next" to output the next file.
- **Step 4** - after outputting the **complete and full corrected according to the approved plan** file, if I approve of it I will say `next` and then you output the next file to change.
- **Step 5** - When there are no more files left and I say `next` you will respond with `# Refactoring is Complete!`

## Project Source Code

```plaintext
REBASE-AIStorywriter/
├── Tools/
│   └── Test.py
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
├── Evaluate.py
├── README.md
└── Write.py
```

# Project Files

## File: `Tools/Test.py`

```python
#!/bin/python3

import os

print("Developer Testing Utility.")

# Get Choice For Model
print("Chose Model: ")
print("-------------------------------------------")
print("1 -> Gemini 1.5 flash, llama70b for editing")
print("2 -> Gemini 1.5 flash, Gemini 1.5 flash for editing")
print("3 -> Gemini 1.5 pro, Gemini 1.5 flash for editing")
print("4 -> Gemini 1.5 pro, Gemini 1.5 pro for editing")
print("5 -> ollama://mistral:7b, ollama://mistral:7b for editing (fast debug test, produces crap output)")
print("6 -> Developer testing script 1, uses many local models, very slow, but decent output")
print("7 -> Developer testing script 2, miqulitz-120b, one model, llama3:70b editor")
print("8 -> Developer testing script 3, miqu-70b-v1.5, one model, llama3:70b editor")
print("9 -> Developer testing script 4, gemma2:27b, one model, gemma2:27b editor")
print("10 -> Developer testing script 4, qwen2:72b, one model, qwen2:72b editor")
print("11 -> Developer testing script 5, llama3, one model, llama3 editor")
print("12 -> Developer testing script 6, gemma, one model, gemma editor")
print("13 -> Developer testing script 7, rose-70b-v2, one model, llama3:70b editor")
print("14 -> Developer testing script 8, miqu-103b-v1, one model, llama3:70b editor")
print("15 -> Developer testing script 9, miqu-70b-v1.5, one model, command-r-plus editor")
print("16 -> Developer testing script 10, mistral-nemo, one model, mistral-nemo editor")
print("17 -> Developer testing script 11, mistral-large, one model, mistral-large editor")
print("18 -> Developer testing script 10, mistral-large, one model, llama3.1:70b editor")
print("-------------------------------------------")


# Get Choice
print("")
choice = input("> ")

# Get Choice For Prompt
print("Chose Prompt:")
print("-------------------------------------------")
print("1 -> ExamplePrompts/Example1/Prompt.txt")
print("2 -> ExamplePrompts/Example2/Prompt.txt")
print("3 -> Custom Prompt")
print("-------------------------------------------")
print("Default = 1")
print("")
PromptChoice = input("> ")

Prompt = ""
if (PromptChoice == "" or PromptChoice == "1"):
    Prompt = "ExamplePrompts/Example1/Prompt.txt"
elif (PromptChoice == "2"):
    Prompt = "ExamplePrompts/Example2/Prompt.txt"
elif (PromptChoice == "3"):
    Prompt = input("Enter Prompt File Path: ")



# Now, Add Any Extra Flags
print("Extra Flags:")
# print("-------------------------------------------")
# print("1 -> ExamplePrompts/Example1/Prompt.txt")
# print("2 -> ExamplePrompts/Example2/Prompt.txt")
# print("3 -> Custom Prompt")
# print("-------------------------------------------")
print("Default = '-ExpandOutline'")
print("")
ExtraFlags = input("> ")

if ExtraFlags == "":
    ExtraFlags = "-ExpandOutline"



# Terrible but effective way to manage the choices
if (choice == "1"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel google://gemini-1.5-flash \
-ChapterOutlineModel google://gemini-1.5-flash \
-ChapterS1Model google://gemini-1.5-flash \
-ChapterS2Model google://gemini-1.5-flash \
-ChapterS3Model google://gemini-1.5-flash \
-ChapterS4Model google://gemini-1.5-flash \
-ChapterRevisionModel google://gemini-1.5-flash \
-RevisionModel ollama://llama3:70b@10.1.65.4:11434 \
-EvalModel ollama://llama3:70b@10.1.65.4:11434 \
-InfoModel ollama://llama3:70b@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}
              ''')

elif (choice == "2"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel google://gemini-1.5-flash \
-ChapterOutlineModel google://gemini-1.5-flash \
-ChapterS1Model google://gemini-1.5-flash \
-ChapterS2Model google://gemini-1.5-flash \
-ChapterS3Model google://gemini-1.5-flash \
-ChapterS4Model google://gemini-1.5-flash \
-ChapterRevisionModel google://gemini-1.5-flash \
-RevisionModel google://gemini-1.5-flash \
-EvalModel google://gemini-1.5-flash \
-InfoModel google://gemini-1.5-flash \
-NoScrubChapters \
-Debug {ExtraFlags}
              ''')

elif (choice == "3"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel google://gemini-1.5-pro \
-ChapterOutlineModel google://gemini-1.5-pro \
-ChapterS1Model google://gemini-1.5-pro \
-ChapterS2Model google://gemini-1.5-pro \
-ChapterS3Model google://gemini-1.5-pro \
-ChapterS4Model google://gemini-1.5-pro \
-ChapterRevisionModel google://gemini-1.5-flash \
-RevisionModel google://gemini-1.5-flash \
-EvalModel google://gemini-1.5-flash \
-InfoModel google://gemini-1.5-flash \
-NoScrubChapters \
-Debug {ExtraFlags}
              ''')

elif (choice == "4"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel google://gemini-1.5-pro \
-ChapterOutlineModel google://gemini-1.5-pro \
-ChapterS1Model google://gemini-1.5-pro \
-ChapterS2Model google://gemini-1.5-pro \
-ChapterS3Model google://gemini-1.5-pro \
-ChapterS4Model google://gemini-1.5-pro \
-ChapterRevisionModel google://gemini-1.5-pro \
-RevisionModel google://gemini-1.5-pro \
-EvalModel google://gemini-1.5-pro \
-InfoModel google://gemini-1.5-pro \
-NoScrubChapters \
-Debug {ExtraFlags}
              ''')

elif (choice == "5"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel ollama://mistral \
-ChapterOutlineModel ollama://mistral \
-ChapterS1Model ollama://mistral \
-ChapterS2Model ollama://mistral \
-ChapterS3Model ollama://mistral \
-ChapterS4Model ollama://mistral \
-ChapterRevisionModel ollama://mistral \
-RevisionModel ollama://mistral \
-EvalModel ollama://mistral \
-InfoModel ollama://mistral \
-CheckerModel ollama://mistral \
-NoScrubChapters {ExtraFlags}
              ''')

elif (choice == "6"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt Prompts/Genshin/Kaeluc.txt \
-InitialOutlineModel ollama://datacrystals/miqulitz120b-v2:latest@10.1.65.4:11434 \
-ChapterOutlineModel ollama://datacrystals/midnight-rose103b-v2:latest@10.1.65.4:11434 \
-ChapterS1Model ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterS2Model ollama://command-r-plus@10.1.65.4:11434 \
-ChapterS3Model ollama://datacrystals/miqulitz120b-v2:latest@10.1.65.4:11434 \
-ChapterS4Model ollama://datacrystals/midnight-miqu103b-v1:latest@10.1.65.4:11434 \
-ChapterRevisionModel ollama://datacrystals/miqulitz120b-v2:latest@10.1.65.4:11434 \
-RevisionModel ollama://llama3:70b@10.1.65.4:11434 \
-EvalModel ollama://llama3:70b@10.1.65.4:11434 \
-InfoModel ollama://llama3:70b@10.1.65.4:11434 \
-NoScrubChapters \
-Debug \
-NoChapterRevision {ExtraFlags}
''')

elif (choice == "7"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel ollama://datacrystals/miqulitz120b-v2:latest@10.1.65.4:11434 \
-ChapterOutlineModel ollama://datacrystals/miqulitz120b-v2:latest@10.1.65.4:11434 \
-ChapterS1Model ollama://datacrystals/miqulitz120b-v2:latest@10.1.65.4:11434 \
-ChapterS2Model ollama://datacrystals/miqulitz120b-v2:latest@10.1.65.4:11434 \
-ChapterS3Model ollama://datacrystals/miqulitz120b-v2:latest@10.1.65.4:11434 \
-ChapterS4Model ollama://datacrystals/miqulitz120b-v2:latest@10.1.65.4:11434 \
-ChapterRevisionModel ollama://datacrystals/miqulitz120b-v2:latest@10.1.65.4:11434 \
-RevisionModel ollama://llama3:70b@10.1.65.4:11434 \
-EvalModel ollama://llama3:70b@10.1.65.4:11434 \
-InfoModel ollama://llama3:70b@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}


''')

elif (choice == "8"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterOutlineModel ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterS1Model ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterS2Model ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterS3Model ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterS4Model ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterRevisionModel ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-RevisionModel ollama://llama3:70b@10.1.65.4:11434 \
-EvalModel ollama://llama3:70b@10.1.65.4:11434 \
-InfoModel ollama://llama3:70b@10.1.65.4:11434 \
-ScrubModel ollama://llama3:70b@10.1.65.4:11434 \
-CheckerModel ollama://llama3:70b@10.1.65.4:11434 \
-TranslatorModel  ollama://llama3:70b@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}

''')


elif (choice == "9"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel ollama://gemma2:27b@10.1.65.4:11434 \
-ChapterOutlineModel ollama://gemma2:27b@10.1.65.4:11434 \
-ChapterS1Model ollama://gemma2:27b@10.1.65.4:11434 \
-ChapterS2Model ollama://gemma2:27b@10.1.65.4:11434 \
-ChapterS3Model ollama://gemma2:27b@10.1.65.4:11434 \
-ChapterS4Model ollama://gemma2:27b@10.1.65.4:11434 \
-ChapterRevisionModel ollama://gemma2:27b@10.1.65.4:11434 \
-RevisionModel ollama://gemma2:27b@10.1.65.4:11434 \
-EvalModel ollama://gemma2:27b@10.1.65.4:11434 \
-InfoModel ollama://gemma2:27b@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}

''')

elif (choice == "10"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt ExamplePrompts/Example1/Prompt.txt \
-InitialOutlineModel ollama://qwen2:72b@10.1.65.4:11434 \
-ChapterOutlineModel ollama://qwen2:72b@10.1.65.4:11434 \
-ChapterS1Model ollama://qwen2:72b@10.1.65.4:11434 \
-ChapterS2Model ollama://qwen2:72b@10.1.65.4:11434 \
-ChapterS3Model ollama://qwen2:72b@10.1.65.4:11434 \
-ChapterS4Model ollama://qwen2:72b@10.1.65.4:11434 \
-ChapterRevisionModel ollama://qwen2:72b@10.1.65.4:11434 \
-RevisionModel ollama://qwen2:72b@10.1.65.4:11434 \
-EvalModel ollama://qwen2:72b@10.1.65.4:11434 \
-InfoModel ollama://qwen2:72b@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}

''')

elif (choice == "11"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt ExamplePrompts/Example1/Prompt.txt \
-InitialOutlineModel ollama://llama3@10.1.65.4:11434 \
-ChapterOutlineModel ollama://llama3@10.1.65.4:11434 \
-ChapterS1Model ollama://llama3@10.1.65.4:11434 \
-ChapterS2Model ollama://llama3@10.1.65.4:11434 \
-ChapterS3Model ollama://llama3@10.1.65.4:11434 \
-ChapterS4Model ollama://llama3@10.1.65.4:11434 \
-ChapterRevisionModel ollama://llama3@10.1.65.4:11434 \
-RevisionModel ollama://llama3@10.1.65.4:11434 \
-EvalModel ollama://llama3@10.1.65.4:11434 \
-InfoModel ollama://llama3@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}

''')

elif (choice == "12"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt ExamplePrompts/Example1/Prompt.txt \
-InitialOutlineModel ollama://gemma@10.1.65.4:11434 \
-ChapterOutlineModel ollama://gemma@10.1.65.4:11434 \
-ChapterS1Model ollama://gemma@10.1.65.4:11434 \
-ChapterS2Model ollama://gemma@10.1.65.4:11434 \
-ChapterS3Model ollama://gemma@10.1.65.4:11434 \
-ChapterS4Model ollama://gemma@10.1.65.4:11434 \
-ChapterRevisionModel ollama://gemma@10.1.65.4:11434 \
-RevisionModel ollama://gemma@10.1.65.4:11434 \
-EvalModel ollama://gemma@10.1.65.4:11434 \
-InfoModel ollama://gemma@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}

''')

elif (choice == "13"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel ollama://datacrystals/midnight-rose70b-v2:latest@10.1.65.4:11434 \
-ChapterOutlineModel ollama://datacrystals/midnight-rose70b-v2:latest@10.1.65.4:11434 \
-ChapterS1Model ollama://datacrystals/midnight-rose70b-v2:latest@10.1.65.4:11434 \
-ChapterS2Model ollama://datacrystals/midnight-rose70b-v2:latest@10.1.65.4:11434 \
-ChapterS3Model ollama://datacrystals/midnight-rose70b-v2:latest@10.1.65.4:11434 \
-ChapterS4Model ollama://datacrystals/midnight-rose70b-v2:latest@10.1.65.4:11434 \
-ChapterRevisionModel ollama://datacrystals/midnight-rose70b-v2:latest@10.1.65.4:11434 \
-RevisionModel ollama://llama3:70b@10.1.65.4:11434 \
-EvalModel ollama://llama3:70b@10.1.65.4:11434 \
-InfoModel ollama://llama3:70b@10.1.65.4:11434 \
-ScrubModel ollama://llama3:70b@10.1.65.4:11434 \
-CheckerModel ollama://llama3:70b@10.1.65.4:11434 \
-TranslatorModel  ollama://llama3:70b@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}

''')

elif (choice == "14"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel ollama://datacrystals/midnight-miqu103b-v1:latest@10.1.65.4:11434 \
-ChapterOutlineModel ollama://datacrystals/midnight-miqu103b-v1:latest@10.1.65.4:11434 \
-ChapterS1Model ollama://datacrystals/midnight-miqu103b-v1:latest@10.1.65.4:11434 \
-ChapterS2Model ollama://datacrystals/midnight-miqu103b-v1:latest@10.1.65.4:11434 \
-ChapterS3Model ollama://datacrystals/midnight-miqu103b-v1:latest@10.1.65.4:11434 \
-ChapterS4Model ollama://datacrystals/midnight-miqu103b-v1:latest@10.1.65.4:11434 \
-ChapterRevisionModel ollama://datacrystals/midnight-miqu103b-v1:latest@10.1.65.4:11434 \
-RevisionModel ollama://llama3:70b@10.1.65.4:11434 \
-EvalModel ollama://llama3:70b@10.1.65.4:11434 \
-InfoModel ollama://llama3:70b@10.1.65.4:11434 \
-ScrubModel ollama://llama3:70b@10.1.65.4:11434 \
-CheckerModel ollama://llama3:70b@10.1.65.4:11434 \
-TranslatorModel  ollama://llama3:70b@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}

''')

elif (choice == "15"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterOutlineModel ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterS1Model ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterS2Model ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterS3Model ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterS4Model ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-ChapterRevisionModel ollama://datacrystals/midnight-miqu70b-v1.5:latest@10.1.65.4:11434 \
-RevisionModel ollama://command-r-plus@10.1.65.4:11434 \
-EvalModel ollama://command-r-plus@10.1.65.4:11434 \
-InfoModel ollama://command-r-plus@10.1.65.4:11434 \
-ScrubModel ollama://command-r-plus@10.1.65.4:11434 \
-CheckerModel ollama://command-r-plus@10.1.65.4:11434 \
-TranslatorModel  ollama://command-r-plus@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}

''')

elif (choice == "16"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel ollama://mistral-nemo:latest@10.1.65.4:11434 \
-ChapterOutlineModel ollama://mistral-nemo:latest@10.1.65.4:11434 \
-ChapterS1Model ollama://mistral-nemo:latest@10.1.65.4:11434 \
-ChapterS2Model ollama://mistral-nemo:latest@10.1.65.4:11434 \
-ChapterS3Model ollama://mistral-nemo:latest@10.1.65.4:11434 \
-ChapterS4Model ollama://mistral-nemo:latest@10.1.65.4:11434 \
-ChapterRevisionModel ollama://mistral-nemo:latest@10.1.65.4:11434 \
-RevisionModel ollama://mistral-nemo@10.1.65.4:11434 \
-EvalModel ollama://mistral-nemo@10.1.65.4:11434 \
-InfoModel ollama://mistral-nemo@10.1.65.4:11434 \
-ScrubModel ollama://mistral-nemo@10.1.65.4:11434 \
-CheckerModel ollama://mistral-nemo@10.1.65.4:11434 \
-TranslatorModel  ollama://mistral-nemo@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}

''')

elif (choice == "17"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterOutlineModel ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterS1Model ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterS2Model ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterS3Model ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterS4Model ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterRevisionModel ollama://mistral-large:latest@10.1.65.4:11434 \
-RevisionModel ollama://mistral-large@10.1.65.4:11434 \
-EvalModel ollama://mistral-large@10.1.65.4:11434 \
-InfoModel ollama://mistral-large@10.1.65.4:11434 \
-ScrubModel ollama://mistral-large@10.1.65.4:11434 \
-CheckerModel ollama://mistral-large@10.1.65.4:11434 \
-TranslatorModel  ollama://mistral-large@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}

''')


elif (choice == "18"):
    os.system(f'''
cd .. && ./Write.py \
-Seed 999 \
-Prompt {Prompt} \
-InitialOutlineModel ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterOutlineModel ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterS1Model ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterS2Model ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterS3Model ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterS4Model ollama://mistral-large:latest@10.1.65.4:11434 \
-ChapterRevisionModel ollama://mistral-large:latest@10.1.65.4:11434 \
-RevisionModel ollama://llama3.1:70b@10.1.65.4:11434 \
-EvalModel ollama://llama3.1:70b@10.1.65.4:11434 \
-InfoModel ollama://llama3.1:70b@10.1.65.4:11434 \
-ScrubModel ollama://llama3.1:70b@10.1.65.4:11434 \
-CheckerModel ollama://llama3.1:70b@10.1.65.4:11434 \
-TranslatorModel  ollama://llama3.1:70b@10.1.65.4:11434 \
-NoScrubChapters \
-Debug {ExtraFlags}

''')
```

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
import json, requests, time
from typing import Any, List, Mapping, Optional, Literal, Union, TypedDict

class OpenRouter:
    """OpenRouter.
    https://openrouter.ai/docs#models
    https://openrouter.ai/docs#llm-parameters
    """

    Message_Type = TypedDict('Message', { 'role': Literal['user', 'assistant', 'system', 'tool'], 'content': str })
    ProviderPreferences_Type = TypedDict(
        'ProviderPreferences', {
            'allow_fallbacks': Optional[bool],
            'require_parameters': Optional[bool],
            'data_collection': Union[Literal['deny'], Literal['allow'], None],
            'order': Optional[List[Literal[
                'OpenAI', 'Anthropic', 'HuggingFace', 'Google', 'Together', 'DeepInfra', 'Azure', 'Modal',
                'AnyScale', 'Replicate', 'Perplexity', 'Recursal', 'Fireworks', 'Mistral', 'Groq', 'Cohere',
                'Lepton', 'OctoAI', 'Novita', 'DeepSeek', 'Infermatic', 'AI21', 'Featherless', 'Mancer',
                'Mancer 2', 'Lynn 2', 'Lynn'
            ]]]
        }, total=False
    )

    def __init__(self,
        api_key: str,
        provider: Optional[ProviderPreferences_Type] | None = None,
        model: str = "microsoft/wizardlm-2-7b",
        max_tokens: int = 0,
        temperature: Optional[float] | None = 1.0,
        top_k: Optional[int] | None = 0.0,
        top_p: Optional[float] = 1.0,
        presence_penalty: Optional[float] = 0.0,
        frequency_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = 1.0,
        min_p: Optional[float] = 0.0,
        top_a: Optional[float] = 0.0,
        seed: Optional[int] | None = None,
        logit_bias: Optional[Mapping[int, int]] | None = None,
        response_format: Optional[Mapping[str, str]] | None = None,
        stop: Optional[Mapping[str, str]] | None = None,
        set_p50: bool = False,
        set_p90: bool = False,
        api_url: str = "https://openrouter.ai/api/v1/chat/completions",
        timeout: int = 3600,
        ):

        self.api_url = api_url
        self.api_key = api_key
        self.provider = provider
        self.model = model
        self.max_tokens = max_tokens
        self.seed = seed
        self.logit_bias = logit_bias
        self.response_format = response_format
        self.stop = stop
        self.timeout = timeout

        # Get the top LLM sampling parameter configurations used by users on OpenRouter.
        # https://openrouter.ai/docs/parameters-api
        if (set_p90 or set_p50):
            parameters_url = f'https://openrouter.ai/api/v1/parameters/{self.model}'
            headers = {
                'accept': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            params = requests.get(parameters_url, headers=headers).json()["data"]
            # I am so sorry
            self.temperature = params["temperature_p50"] if set_p50 else params["temperature_p90"]
            self.top_k = params["top_k_p50"] if set_p50 else params["top_k_p90"]
            self.top_p = params["top_p_p50"] if set_p50 else params["top_p_p90"]
            self.presence_penalty = params["presence_penalty_p50"] if set_p50 else params["presence_penalty_p90"]
            self.frequency_penalty = params["frequency_penalty_p50"] if set_p50 else params["frequency_penalty_p90"]
            self.repetition_penalty = params["repetition_penalty_p50"] if set_p50 else params["repetition_penalty_p90"]
            self.min_p = params["min_p_p50"] if set_p50 else params["min_p_p90"]
            self.top_a = params["top_a_p50"] if set_p50 else params["top_a_p90"]
        else:
            self.temperature = temperature
            self.top_k = top_k
            self.top_p = top_p
            self.presence_penalty = presence_penalty
            self.frequency_penalty = frequency_penalty
            self.repetition_penalty = repetition_penalty
            self.min_p = min_p
            self.top_a = top_a

    def set_params(self,
        max_tokens: Optional[int] | None = None,
        presence_penalty: Optional[float] | None = None,
        frequency_penalty: Optional[float] | None = None,
        repetition_penalty: Optional[float] | None = None,
        response_format: Optional[Mapping[str, str]] | None = None,
        temperature: Optional[float] | None = None,
        seed: Optional[int] | None = None,
        top_k: Optional[int] | None = None,
        top_p: Optional[float] | None = None,
        min_p: Optional[float] | None = None,
        top_a: Optional[float] | None = None,
        ):

        if max_tokens is not None: self.max_tokens = max_tokens
        if presence_penalty is not None: self.presence_penalty = presence_penalty
        if frequency_penalty is not None: self.frequency_penalty = frequency_penalty
        if repetition_penalty is not None: self.repetition_penalty = repetition_penalty
        if response_format is not None: self.response_format = response_format
        if temperature is not None: self.temperature = temperature
        if seed is not None: self.seed = seed
        if top_k is not None: self.top_k = top_k
        if top_p is not None: self.top_p = top_p
        if min_p is not None: self.min_p = min_p
        if top_a is not None: self.top_a = top_a
    def ensure_array(self,
            input_msg: List[Message_Type] | Message_Type
        ) -> List[Message_Type]:
        if isinstance(input_msg, (list, tuple)):
            return input_msg
        else:
            return [input_msg]

    def chat(self,
            messages: Message_Type,
            max_retries: int = 10,
            seed: int = None
    ):
        messages = self.ensure_array(messages)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            'HTTP-Referer': 'https://github.com/datacrystals/AIStoryWriter',
            'X-Title': 'StoryForgeAI',
        }
        body={
            "model": self.model,
            "messages": messages,
            "max_token": self.max_tokens,
            "temperature": self.temperature,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
            "repetition_penalty": self.repetition_penalty,
            "min_p": self.min_p,
            "top_a": self.top_a,
            "seed": self.seed if seed is None else seed,
            "logit_bias": self.logit_bias,
            "response_format": self.response_format,
            "stop": self.stop,
            "provider": self.provider,
            "stream": False,
        }

        retries = 0
        while retries < max_retries:
            try:
                response = requests.post(url=self.api_url, headers=headers, data=json.dumps(body), timeout=self.timeout, stream=False)
                response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
                if 'choices' in response.json():
                    # Return result from request
                    return response.json()["choices"][0]["message"]["content"]
                elif 'error' in response.json():
                    print(f"Openrouter returns error '{response.json()['error']['code']}' with message '{response.json()['error']['message']}', retry attempt {retries + 1}.")
                    if response.json()['error']['code'] == 400:
                        print("Bad Request (invalid or missing params, CORS)")
                    if response.json()['error']['code'] == 401:
                        raise Exception ("Invalid credentials (OAuth session expired, disabled/invalid API key)")
                    if response.json()['error']['code'] == 402:
                        raise Exception ("Your account or API key has insufficient credits. Add more credits and retry the request.")
                    if response.json()['error']['code'] == 403:
                        print("Your chosen model requires moderation and your input was flagged")
                    if response.json()['error']['code'] == 408:
                        print("Your request timed out")
                    if response.json()['error']['code'] == 429:
                        print("You are being rate limited")
                        print("Waiting 10 seconds")
                        time.sleep(10)
                    if response.json()['error']['code'] == 502:
                        print("Your chosen model is down or we received an invalid response from it")
                    if response.json()['error']['code'] == 503:
                        print("There is no available model provider that meets your routing requirements")
                else:
                    from pprint import pprint
                    print(f"Response without error but missing choices, retry attempt {retries + 1}.")
                    pprint(response.json())
            except requests.exceptions.HTTPError as http_err:
                # HTTP error status code
                print(f"HTTP error occurred: '{http_err}' - Status Code: '{http_err.response.status_code}', retry attempt {retries + 1}.")
                # Funny Cloudflare being funny.
                # This is a lie: https://community.cloudflare.com/t/community-tip-fixing-error-524-a-timeout-occurred/42342
                if http_err.response.status_code == 524:
                    time.sleep(10)
            except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as err:
                # timeouts and redirects
                print(f"Retry attempt {retries + 1} after error: '{err}'")
            except requests.exceptions.RequestException as req_err:
                # any other request errors that haven't been caught by the previous except blocks
                print(f"An error occurred while making the request: '{req_err}', retry attempt {retries + 1}.")
            except Exception as e:
                # all other exceptions
                print(f"An unexpected error occurred: '{e}', retry attempt {retries + 1}.")
            retries += 1

```

## File: `Writer/Interface/Wrapper.py`

```python
import Writer.Config
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

dotenv.load_dotenv()


class Interface:

    def __init__(
        self,
        Models: list = [],
    ):
        self.Clients: dict = {}
        self.History = []
        self.LoadModels(Models)

    def ensure_package_is_installed(self, package_name):
        try:
            importlib.import_module(package_name)
        except ImportError:
            print(f"Package {package_name} not found. Installing...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )

    def LoadModels(self, Models: list):
        for Model in Models:
            if Model in self.Clients:
                continue
            else:
                Provider, ProviderModel, ModelHost, ModelOptions = (
                    self.GetModelAndProvider(Model)
                )
                print(f"DEBUG: Loading Model {ProviderModel} from {Provider}@{ModelHost}")

                if Provider == "ollama":
                    # Get ollama models (only once)
                    self.ensure_package_is_installed("ollama")
                    import ollama

                    OllamaHost = ModelHost if ModelHost is not None else None

                    # Check if availabel via ollama.show(Model)
                    # check if the model is in the list of models
                    try:
                        ollama.Client(host=OllamaHost).show(ProviderModel)
                        pass
                    except Exception as e:
                        print(
                            f"Model {ProviderModel} not found in Ollama models. Downloading..."
                        )
                        OllamaDownloadStream = ollama.Client(host=OllamaHost).pull(
                            ProviderModel, stream=True
                        )
                        for chunk in OllamaDownloadStream:
                            if "completed" in chunk and "total" in chunk:
                                OllamaDownloadProgress = (
                                    chunk["completed"] / chunk["total"]
                                )
                                completedSize = chunk["completed"] / 1024**3
                                totalSize = chunk["total"] / 1024**3
                                print(
                                    f"Downloading {ProviderModel}: {OllamaDownloadProgress * 100:.2f}% ({completedSize:.3f}GB/{totalSize:.3f}GB)",
                                    end="\r",
                                )
                            else:
                                print(f"{chunk['status']} {ProviderModel}", end="\r")
                        print("\n\n\n")

                    self.Clients[Model] = ollama.Client(host=OllamaHost)
                    print(f"OLLAMA Host is '{OllamaHost}'")

                elif Provider == "google":
                    # Validate Google API Key
                    if (
                        not "GOOGLE_API_KEY" in os.environ
                        or os.environ["GOOGLE_API_KEY"] == ""
                    ):
                        raise Exception(
                            "GOOGLE_API_KEY not found in environment variables"
                        )
                    self.ensure_package_is_installed("google-generativeai")
                    import google.generativeai as genai

                    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
                    self.Clients[Model] = genai.GenerativeModel(
                        model_name=ProviderModel
                    )

                elif Provider == "openai":
                    raise NotImplementedError("OpenAI API not supported")

                elif Provider == "openrouter":
                    if (
                        not "OPENROUTER_API_KEY" in os.environ
                        or os.environ["OPENROUTER_API_KEY"] == ""
                    ):
                        raise Exception(
                            "OPENROUTER_API_KEY not found in environment variables"
                        )
                    from Writer.Interface.OpenRouter import OpenRouter

                    self.Clients[Model] = OpenRouter(
                        api_key=os.environ["OPENROUTER_API_KEY"], model=ProviderModel
                    )

                elif Provider == "Anthropic":
                    raise NotImplementedError("Anthropic API not supported")

                else:
                    print(f"Warning, ")
                    raise Exception(f"Model Provider {Provider} for {Model} not found")

    def SafeGenerateText(
        self,
        _Logger,
        _Messages,
        _Model: str,
        _SeedOverride: int = -1,
        _Format: str = None,
        _MinWordCount: int = 1
        ):
        """
        This function guarantees that the output will not be whitespace.
        """

        # Strip Empty Messages
        for i in range(len(_Messages) - 1, 0, -1):
            if _Messages[i]["content"].strip() == "":
                del _Messages[i]

        NewMsg = self.ChatAndStreamResponse(_Logger, _Messages, _Model, _SeedOverride, _Format)

        while (self.GetLastMessageText(NewMsg).strip() == "") or (len(self.GetLastMessageText(NewMsg).split(" ")) < _MinWordCount):
            if self.GetLastMessageText(NewMsg).strip() == "":
                _Logger.Log("SafeGenerateText: Generation Failed Due To Empty (Whitespace) Response, Reattempting Output", 7)
            elif (len(self.GetLastMessageText(NewMsg).split(" ")) < _MinWordCount):
                _Logger.Log(f"SafeGenerateText: Generation Failed Due To Short Response ({len(self.GetLastMessageText(NewMsg).split(' '))}, min is {_MinWordCount}), Reattempting Output", 7)

            del _Messages[-1] # Remove failed attempt
            NewMsg = self.ChatAndStreamResponse(_Logger, _Messages, _Model, random.randint(0, 99999), _Format)

        return NewMsg



    def SafeGenerateJSON(self, _Logger, _Messages, _Model:str, _SeedOverride:int = -1, _RequiredAttribs:list = []):

        while True:
            Response = self.SafeGenerateText(_Logger, _Messages, _Model, _SeedOverride, _Format = "JSON")
            try:

                # Check that it returned valid json
                JSONResponse = json.loads(self.GetLastMessageText(Response))

                # Now ensure it has the right attributes
                for _Attrib in _RequiredAttribs:
                    JSONResponse[_Attrib]

                # Now return the json
                return Response, JSONResponse

            except Exception as e:
                _Logger.Log(f"JSON Error during parsing: {e}", 7)
                del _Messages[-1] # Remove failed attempt
                Response = self.ChatAndStreamResponse(_Logger, _Messages, _Model, random.randint(0, 99999), _Format = "JSON")



    def ChatAndStreamResponse(
        self,
        _Logger,
        _Messages,
        _Model: str = "llama3",
        _SeedOverride: int = -1,
        _Format: str = None,
    ):
        Provider, ProviderModel, ModelHost, ModelOptions = self.GetModelAndProvider(
            _Model
        )

        # Calculate Seed Information
        Seed = Writer.Config.SEED if _SeedOverride == -1 else _SeedOverride

        # Log message history if DEBUG is enabled
        if Writer.Config.DEBUG:
            print("--------- Message History START ---------")
            print("[")
            for Message in _Messages:
                print(f"{Message},\n----\n")
            print("]")
            print("--------- Message History END --------")

        StartGeneration = time.time()

        # Calculate estimated tokens
        TotalChars = len(str(_Messages))
        AvgCharsPerToken = 5  # estimated average chars per token
        EstimatedTokens = TotalChars / AvgCharsPerToken
        _Logger.Log(
            f"Using Model '{ProviderModel}' from '{Provider}@{ModelHost}' | (Est. ~{EstimatedTokens}tok Context Length)",
            4,
        )

        # Log if there's a large estimated tokens of context history
        if EstimatedTokens > 24000:
            _Logger.Log(
                f"Warning, Detected High Token Context Length of est. ~{EstimatedTokens}tok",
                6,
            )

        if Provider == "ollama":

            # remove host
            if "@" in ProviderModel:
                ProviderModel = ProviderModel.split("@")[0]

            # https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values
            ValidParameters = [
                "mirostat",
                "mirostat_eta",
                "mirostat_tau",
                "num_ctx",
                "repeat_last_n",
                "repeat_penalty",
                "temperature",
                "seed",
                "tfs_z",
                "num_predict",
                "top_k",
                "top_p",
            ]
            ModelOptions = ModelOptions if ModelOptions is not None else {}

            # Check if the parameters are valid
            for key in ModelOptions:
                if key not in ValidParameters:
                    raise ValueError(f"Invalid parameter: {key}")

            # Set the default num_ctx if not set by args
            if "num_ctx" not in ModelOptions:
                ModelOptions["num_ctx"] = Writer.Config.OLLAMA_CTX

            _Logger.Log(f"Using Ollama Model Options: {ModelOptions}", 4)

            if _Format == "json":
                # Overwrite the format to JSON
                ModelOptions["format"] = "json"

                # if temperature is not set, set it to 0 for JSON mode
                if "temperature" not in ModelOptions:
                    ModelOptions["temperature"] = 0
                _Logger.Log("Using Ollama JSON Format", 4)

            Stream = self.Clients[_Model].chat(
                model=ProviderModel,
                messages=_Messages,
                stream=True,
                options=ModelOptions,
            )
            MaxRetries = 3

            while True:
                try:
                    _Messages.append(self.StreamResponse(Stream, Provider))
                    break
                except Exception as e:
                    if MaxRetries > 0:
                        _Logger.Log(
                            f"Exception During Generation '{e}', {MaxRetries} Retries Remaining",
                            7,
                        )
                        MaxRetries -= 1
                    else:
                        _Logger.Log(
                            f"Max Retries Exceeded During Generation, Aborting!", 7
                        )
                        raise Exception(
                            "Generation Failed, Max Retires Exceeded, Aborting"
                        )

        elif Provider == "google":

            from google.generativeai.types import (
                HarmCategory,
                HarmBlockThreshold,
            )

            # replace "content" with "parts" for google
            _Messages = [{"role": m["role"], "parts": m["content"]} for m in _Messages]
            for m in _Messages:
                if "content" in m:
                    m["parts"] = m["content"]
                    del m["content"]
                if "role" in m and m["role"] == "assistant":
                    m["role"] = "model"
                    # Google doesn't support "system" role while generating content (only while instantiating the model)
                if "role" in m and m["role"] == "system":
                    m["role"] = "user"

            MaxRetries = 3
            while True:
                try:
                    Stream = self.Clients[_Model].generate_content(
                        contents=_Messages,
                        stream=True,
                        safety_settings={
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        },
                    )
                    _Messages.append(self.StreamResponse(Stream, Provider))
                    break
                except Exception as e:
                    if MaxRetries > 0:
                        _Logger.Log(
                            f"Exception During Generation '{e}', {MaxRetries} Retries Remaining",
                            7,
                        )
                        MaxRetries -= 1
                    else:
                        _Logger.Log(
                            f"Max Retries Exceeded During Generation, Aborting!", 7
                        )
                        raise Exception(
                            "Generation Failed, Max Retires Exceeded, Aborting"
                        )

            # Replace "parts" back to "content" for generalization
            # and replace "model" with "assistant"
            for m in _Messages:
                if "parts" in m:
                    m["content"] = m["parts"]
                    del m["parts"]
                if "role" in m and m["role"] == "model":
                    m["role"] = "assistant"

        elif Provider == "openai":
            raise NotImplementedError("OpenAI API not supported")

        elif Provider == "openrouter":

            # https://openrouter.ai/docs/parameters
            # Be aware that parameters depend on models and providers.
            ValidParameters = [
                "max_token",
                "presence_penalty",
                "frequency_penalty",
                "repetition_penalty",
                "response_format",
                "temperature",
                "seed",
                "top_k",
                "top_p",
                "top_a",
                "min_p",
            ]
            ModelOptions = ModelOptions if ModelOptions is not None else {}

            Client = self.Clients[_Model]
            Client.set_params(**ModelOptions)
            Client.model = ProviderModel
            print(ProviderModel)

            Response = Client.chat(messages=_Messages, seed=Seed)
            _Messages.append({"role": "assistant", "content": Response})

        elif Provider == "Anthropic":
            raise NotImplementedError("Anthropic API not supported")

        else:
            raise Exception(f"Model Provider {Provider} for {_Model} not found")

        # Log the time taken to generate the response
        EndGeneration = time.time()
        _Logger.Log(
            f"Generated Response in {round(EndGeneration - StartGeneration, 2)}s (~{round(EstimatedTokens / (EndGeneration - StartGeneration), 2)}tok/s)",
            4,
        )
        # Check if the response is empty and attempt regeneration if necessary
        if _Messages[-1]["content"].strip() == "":
            _Logger.Log("Model Returned Only Whitespace, Attempting Regeneration", 6)
            _Messages.append(
                self.BuildUserQuery(
                    "Sorry, but you returned an empty string, please try again!"
                )
            )
            return self.ChatAndStreamResponse(_Logger, _Messages, _Model, _SeedOverride)

        CallStack: str = ""
        for Frame in inspect.stack()[1:]:
            CallStack += f"{Frame.function}."
        CallStack = CallStack[:-1].replace("<module>", "Main")
        _Logger.SaveLangchain(CallStack, _Messages)
        return _Messages

    def StreamResponse(self, _Stream, _Provider: str):
        Response: str = ""
        for chunk in _Stream:
            if _Provider == "ollama":
                ChunkText = chunk["message"]["content"]
            elif _Provider == "google":
                ChunkText = chunk.text
            else:
                raise ValueError(f"Unsupported provider: {_Provider}")

            Response += ChunkText
            print(ChunkText, end="", flush=True)

        print("\n\n\n" if Writer.Config.DEBUG else "")
        return {"role": "assistant", "content": Response}

    def BuildUserQuery(self, _Query: str):
        return {"role": "user", "content": _Query}

    def BuildSystemQuery(self, _Query: str):
        return {"role": "system", "content": _Query}

    def BuildAssistantQuery(self, _Query: str):
        return {"role": "assistant", "content": _Query}

    def GetLastMessageText(self, _Messages: list):
        return _Messages[-1]["content"]

    def GetModelAndProvider(self, _Model: str):
        # Format is `Provider://Model@Host?param1=value2&param2=value2`
        # default to ollama if no provider is specified
        if "://" in _Model:
            # this should be a valid URL
            parsed = urlparse(_Model)
            print(parsed)
            Provider = parsed.scheme

            if "@" in parsed.netloc:
                Model, Host = parsed.netloc.split("@")

            elif Provider == "openrouter":
                Model = f"{parsed.netloc}{parsed.path}"
                Host = None

            elif "ollama" in _Model:
                if "@" in parsed.path:
                    Model = parsed.netloc + parsed.path.split("@")[0]
                    Host = parsed.path.split("@")[1]
                else:
                    Model = parsed.netloc
                    Host = "localhost:11434"

            else:
                Model = parsed.netloc
                Host = None
            QueryParams = parse_qs(parsed.query)

            # Flatten QueryParams
            for key in QueryParams:
                QueryParams[key] = float(QueryParams[key][0])

            return Provider, Model, Host, QueryParams
        else:
            # legacy support for `Model` format
            return "ollama", _Model, "localhost:11434", None

```

## File: `Writer/Outline/StoryElements.py`

```python
import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config


def GenerateStoryElements(Interface, _Logger, _OutlinePrompt):

    Prompt: str = f"""
I'm working on writing a fictional story, and I'd like your help writing out the story elements.

Here's the prompt for my story.
<PROMPT>
{_OutlinePrompt}
</PROMPT>

Please make your response have the following format:

<RESPONSE_TEMPLATE>
# Story Title

## Genre
- **Category**: (e.g., romance, mystery, science fiction, fantasy, horror)

## Theme
- **Central Idea or Message**:

## Pacing
- **Speed**: (e.g., slow, fast)

## Style
- **Language Use**: (e.g., sentence structure, vocabulary, tone, figurative language)

## Plot
- **Exposition**:
- **Rising Action**:
- **Climax**:
- **Falling Action**:
- **Resolution**:

## Setting
### Setting 1
- **Time**: (e.g., present day, future, past)
- **Location**: (e.g., city, countryside, another planet)
- **Culture**: (e.g., modern, medieval, alien)
- **Mood**: (e.g., gloomy, high-tech, dystopian)

(Repeat the above structure for additional settings)

## Conflict
- **Type**: (e.g., internal, external)
- **Description**:

## Symbolism
### Symbol 1
- **Symbol**:
- **Meaning**:

(Repeat the above structure for additional symbols)

## Characters
### Main Character(s)
#### Main Character 1
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Motivation**:

(Repeat the above structure for additional main characters)


### Supporting Characters
#### Character 1
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 2
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 3
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 4
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 5
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 6
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 7
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

#### Character 8
- **Name**:
- **Physical Description**:
- **Personality**:
- **Background**:
- **Role in the story**:

(Repeat the above structure for additional supporting character)

</RESPONSE_TEMPLATE>

Of course, don't include the XML tags - those are just to indicate the example.
Also, the items in parenthesis are just to give you a better idea of what to write about, and should also be omitted from your response.

    """

    # Generate Initial Story Elements
    _Logger.Log(f"Generating Main Story Elements", 4)
    Messages = [Interface.BuildUserQuery(Prompt)]
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, _MinWordCount=150
    )
    Elements: str = Interface.GetLastMessageText(Messages)
    _Logger.Log(f"Done Generating Main Story Elements", 4)

    return Elements

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
INITIAL_OUTLINE_WRITER_MODEL = (
    "ollama://llama3:70b"  # Note this value is overridden by the argparser
)
CHAPTER_OUTLINE_WRITER_MODEL = (
    "ollama://llama3:70b"  # Note this value is overridden by the argparser
)
CHAPTER_STAGE1_WRITER_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
CHAPTER_STAGE2_WRITER_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
CHAPTER_STAGE3_WRITER_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
CHAPTER_STAGE4_WRITER_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
CHAPTER_REVISION_WRITER_MODEL = (
    "ollama://llama3:70b"  # Note this value is overridden by the argparser
)
REVISION_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
EVAL_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
INFO_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
SCRUB_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
CHECKER_MODEL = "ollama://llama3:70b"  # Model used to check results
TRANSLATOR_MODEL = "ollama://llama3:70b"

OLLAMA_CTX = 8192

OLLAMA_HOST = "127.0.0.1:11434"

SEED = 108  # Note this value is overridden by the argparser

TRANSLATE_LANGUAGE = ""  # If the user wants to translate, this'll be changed from empty to a language e.g 'French' or 'Russian'
TRANSLATE_PROMPT_LANGUAGE = ""  # If the user wants to translate their prompt, this'll be changed from empty to a language e.g 'French' or 'Russian'

OUTLINE_QUALITY = 90  # Note this value is overridden by the argparser
OUTLINE_MIN_REVISIONS = 0  # Note this value is overridden by the argparser
OUTLINE_MAX_REVISIONS = 3  # Note this value is overridden by the argparser
CHAPTER_NO_REVISIONS = True  # Note this value is overridden by the argparser # disables all revision checks for the chapter, overriding any other chapter quality/revision settings
CHAPTER_QUALITY = 92  # Note this value is overridden by the argparser
CHAPTER_MIN_REVISIONS = 2  # Note this value is overridden by the argparser
CHAPTER_MAX_REVISIONS = 3  # Note this value is overridden by the argparser

SCRUB_NO_SCRUB = False  # Note this value is overridden by the argparser
EXPAND_OUTLINE = True  # Note this value is overridden by the argparser
ENABLE_FINAL_EDIT_PASS = True  # Note this value is overridden by the argparser

SCENE_GENERATION_PIPELINE = True

OPTIONAL_OUTPUT_NAME = ""

DEBUG = False

# Tested models:
"llama3:70b"  # works as editor model, DO NOT use as writer model, it sucks
"vanilj/midnight-miqu-70b-v1.5"  # works rather well as the writer, not well as anything else
"command-r"
"qwen:72b"
"command-r-plus"
"nous-hermes2"  # not big enough to really do a good job - do not use
"dbrx"  # sucks - do not use

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
import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Outline.StoryElements
import Writer.Prompts


# We should probably do outline generation in stages, allowing us to go back and add foreshadowing, etc back to previous segments


def GenerateOutline(Interface, _Logger, _OutlinePrompt, _QualityThreshold: int = 85):

    # Get any important info about the base prompt to pass along
    Prompt: str = Writer.Prompts.GET_IMPORTANT_BASE_PROMPT_INFO.format(
        _Prompt = _OutlinePrompt
    )


    _Logger.Log(f"Extracting Important Base Context", 4)
    Messages = [Interface.BuildUserQuery(Prompt)]
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL
    )
    BaseContext: str = Interface.GetLastMessageText(Messages)
    _Logger.Log(f"Done Extracting Important Base Context", 4)


    # Generate Story Elements
    StoryElements: str = Writer.Outline.StoryElements.GenerateStoryElements(
        Interface, _Logger, _OutlinePrompt
    )


    # Now, Generate Initial Outline
    Prompt: str = Writer.Prompts.INITIAL_OUTLINE_PROMPT.format(
        StoryElements=StoryElements, _OutlinePrompt=_OutlinePrompt
    )


    _Logger.Log(f"Generating Initial Outline", 4)
    Messages = [Interface.BuildUserQuery(Prompt)]
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, _MinWordCount=250
    )
    Outline: str = Interface.GetLastMessageText(Messages)
    _Logger.Log(f"Done Generating Initial Outline", 4)

    _Logger.Log(f"Entering Feedback/Revision Loop", 3)
    WritingHistory = Messages
    Rating: int = 0
    Iterations: int = 0
    while True:
        Iterations += 1
        Feedback = Writer.LLMEditor.GetFeedbackOnOutline(Interface, _Logger, Outline)
        Rating = Writer.LLMEditor.GetOutlineRating(Interface, _Logger, Outline)
        # Rating has been changed from a 0-100 int, to does it meet the standards (yes/no)?
        # Yes it has - the 0-100 int isn't actually good at all, LLM just returned a bunch of junk ratings

        if Iterations > Writer.Config.OUTLINE_MAX_REVISIONS:
            break
        if (Iterations > Writer.Config.OUTLINE_MIN_REVISIONS) and (Rating == True):
            break

        Outline = ReviseOutline(Interface, _Logger, Outline, Feedback)

    _Logger.Log(f"Quality Standard Met, Exiting Feedback/Revision Loop", 4)

    # Generate Final Outline
    FinalOutline: str = f"""
{BaseContext}

{StoryElements}

{Outline}
    """

    return FinalOutline, StoryElements, Outline, BaseContext


def ReviseOutline(Interface, _Logger, _Outline, _Feedback, _History: list = []):

    RevisionPrompt: str = Writer.Prompts.OUTLINE_REVISION_PROMPT.format(
        _Outline=_Outline, _Feedback=_Feedback
    )

    _Logger.Log(f"Revising Outline", 2)
    Messages = _History
    Messages.append(Interface.BuildUserQuery(RevisionPrompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, _MinWordCount=250
    )
    SummaryText: str = Interface.GetLastMessageText(Messages)
    _Logger.Log(f"Done Revising Outline", 2)

    return SummaryText, Messages


def GeneratePerChapterOutline(Interface, _Logger, _Chapter, _Outline:str, _History: list = []):

    RevisionPrompt: str = Writer.Prompts.CHAPTER_OUTLINE_PROMPT.format(
        _Chapter=_Chapter,
        _Outline=_Outline
    )
    _Logger.Log("Generating Outline For Chapter " + str(_Chapter), 5)
    Messages = _History
    Messages.append(Interface.BuildUserQuery(RevisionPrompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, _MinWordCount=50
    )
    SummaryText: str = Interface.GetLastMessageText(Messages)
    _Logger.Log("Done Generating Outline For Chapter " + str(_Chapter), 5)

    return SummaryText, Messages

```

## File: `Writer/PrintUtils.py`

````python
import termcolor
import datetime
import os
import json


def PrintMessageHistory(_Messages):
    print("------------------------------------------------------------")
    for Message in _Messages:
        print(Message)
    print("------------------------------------------------------------")


class Logger:

    def __init__(self, _LogfilePrefix="Logs"):

        # Make Paths For Log
        LogDirPath = _LogfilePrefix + "/Generation_" + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        os.makedirs(LogDirPath + "/LangchainDebug", exist_ok=True)

        # Setup Log Path
        self.LogDirPrefix = LogDirPath
        self.LogPath = LogDirPath + "/Main.log"
        self.File = open(self.LogPath, "a")
        self.LangchainID = 0

        self.LogItems = []


    # Helper function that saves the entire language chain object as both json and markdown for debugging later
    def SaveLangchain(self, _LangChainID:str, _LangChain:list):

        # Calculate Filepath For This Langchain
        ThisLogPathJSON:str = self.LogDirPrefix + f"/LangchainDebug/{self.LangchainID}_{_LangChainID}.json"
        ThisLogPathMD:str = self.LogDirPrefix + f"/LangchainDebug/{self.LangchainID}_{_LangChainID}.md"
        LangChainDebugTitle:str = f"{self.LangchainID}_{_LangChainID}"
        self.LangchainID += 1

        # Generate and Save JSON Version
        with open(ThisLogPathJSON, "w") as f:
            f.write(json.dumps(_LangChain, indent=4, sort_keys=True))

        # Now, Save Markdown Version
        with open(ThisLogPathMD, "w") as f:
            MarkdownVersion:str = f"# Debug LangChain {LangChainDebugTitle}\n**Note: '```' tags have been removed in this version.**\n"
            for Message in _LangChain:
                MarkdownVersion += f"\n\n\n# Role: {Message['role']}\n"
                MarkdownVersion += f"```{Message['content'].replace('```', '')}```"
            f.write(MarkdownVersion)

        self.Log(f"Wrote This Language Chain ({LangChainDebugTitle}) To Debug File {ThisLogPathMD}", 5)


    # Saves the given story to disk
    def SaveStory(self, _StoryContent:str):

        with open(f"{self.LogDirPrefix}/Story.md", "w") as f:
            f.write(_StoryContent)

        self.Log(f"Wrote Story To Disk At {self.LogDirPrefix}/Story.md", 5)


    # Logs an item
    def Log(self, _Item, _Level:int):

        # Create Log Entry
        LogEntry = f"[{str(_Level).ljust(2)}] [{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}] {_Item}"

        # Write it to file
        self.File.write(LogEntry + "\n")
        self.LogItems.append(LogEntry)

        # Now color and print it
        if (_Level == 0):
            LogEntry = termcolor.colored(LogEntry, "white")
        elif (_Level == 1):
            LogEntry = termcolor.colored(LogEntry, "grey")
        elif (_Level == 2):
            LogEntry = termcolor.colored(LogEntry, "blue")
        elif (_Level == 3):
            LogEntry = termcolor.colored(LogEntry, "cyan")
        elif (_Level == 4):
            LogEntry = termcolor.colored(LogEntry, "magenta")
        elif (_Level == 5):
            LogEntry = termcolor.colored(LogEntry, "green")
        elif (_Level == 6):
            LogEntry = termcolor.colored(LogEntry, "yellow")
        elif (_Level == 7):
            LogEntry = termcolor.colored(LogEntry, "red")

        print(LogEntry)



    def __del__(self):
        self.File.close()
````

## File: `Writer/Prompts.py`

```python
CHAPTER_COUNT_PROMPT = """
<OUTLINE>
{_Summary}
</OUTLINE>

Please provide a JSON formatted response containing the total number of chapters in the above outline.

Respond with {{"TotalChapters": <total chapter count>}}
Please do not include any other text, just the JSON as your response will be parsed by a computer.
"""

CHAPTER_GENERATION_INTRO = """
You are a great fiction writer, and you're working on a great new story.
You're working on a new novel, and you want to produce a quality output.
Here is your outline:
<OUTLINE>\n{_Outline}\n</OUTLINE>
"""

CHAPTER_HISTORY_INSERT = """
Please help me write my novel.

I'm basing my work on this outline:

<OUTLINE>
{_Outline}
</OUTLINE>

And here is what I've written so far:
<PREVIOUS_CHAPTERS>
{ChapterSuperlist}
</PREVIOUS_CHAPTERS>
"""

CHAPTER_GENERATION_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."

CHAPTER_GENERATION_PROMPT = """
Please help me extract the part of this outline that is just for chapter {_ChapterNum}.

<OUTLINE>
{_Outline}
</OUTLINE>

Do not include anything else in your response except just the content for chapter {_ChapterNum}.
"""

CHAPTER_SUMMARY_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."

CHAPTER_SUMMARY_PROMPT = """
I'm writing the next chapter in my novel (chapter {_ChapterNum}), and I have the following written so far.

My outline:
<OUTLINE>
{_Outline}
</OUTLINE>

And what I've written in the last chapter:
<PREVIOUS_CHAPTER>
{_LastChapter}
</PREVIOUS_CHAPTER>

Please create a list of important summary points from the last chapter so that I know what to keep in mind as I write this chapter.
Also make sure to add a summary of the previous chapter, and focus on noting down any important plot points, and the state of the story as the chapter ends.
That way, when I'm writing, I'll know where to pick up again.

Here's some formatting guidelines:

```

Previous Chapter: - Plot: - Your bullet point summary here with as much detail as needed - Setting: - some stuff here - Characters: - character 1 - info about them, from that chapter - if they changed, how so

Things to keep in Mind: - something that the previous chapter did to advance the plot, so we incorporate it into the next chapter - something else that is important to remember when writing the next chapter - another thing - etc.

```

Thank you for helping me write my story! Please only include your summary and things to keep in mind, don't write anything else.
"""

GET_IMPORTANT_BASE_PROMPT_INFO = """
Please extract any important information from the user's prompt below:

<USER_PROMPT>
{_Prompt}
</USER_PROMPT>

Just write down any information that wouldn't be covered in an outline.
Please use the below template for formatting your response.
This would be things like instructions for chapter length, overall vision, instructions for formatting, etc.
(Don't use the xml tags though - those are for example only)

<EXAMPLE>
# Important Additional Context
- Important point 1
- Important point 2
</EXAMPLE>

Do NOT write the outline itself, just some extra context. Keep your responses short.

"""

CHAPTER_GENERATION_STAGE1 = """
{ContextHistoryInsert}

{_BaseContext}

Please write the plot for chapter {_ChapterNum} of {_TotalChapters} based on the following chapter outline and any previous chapters.
Pay attention to the previous chapters, and make sure you both continue seamlessly from them, It's imperative that your writing connects well with the previous chapter, and flows into the next (so try to follow the outline)!

Here is my outline for this chapter:
<CHAPTER_OUTLINE>
{ThisChapterOutline}
</CHAPTER_OUTLINE>

{FormattedLastChapterSummary}

As you write your work, please use the following suggestions to help you write chapter {_ChapterNum} (make sure you only write this one):
    - Pacing:
    - Are you skipping days at a time? Summarizing events? Don't do that, add scenes to detail them.
    - Is the story rushing over certain plot points and excessively focusing on others?
    - Flow: Does each chapter flow into the next? Does the plot make logical sense to the reader? Does it have a specific narrative structure at play? Is the narrative structure consistent throughout the story?
    - Genre: What is the genre? What language is appropriate for that genre? Do the scenes support the genre?

{Feedback}"""

CHAPTER_GENERATION_STAGE2 = """
{ContextHistoryInsert}

{_BaseContext}

Please write character development for the following chapter {_ChapterNum} of {_TotalChapters} based on the following criteria and any previous chapters.
Pay attention to the previous chapters, and make sure you both continue seamlessly from them, It's imperative that your writing connects well with the previous chapter, and flows into the next (so try to follow the outline)!

Don't take away content, instead expand upon it to make a longer and more detailed output.

For your reference, here is my outline for this chapter:
<CHAPTER_OUTLINE>
{ThisChapterOutline}
</CHAPTER_OUTLINE>

{FormattedLastChapterSummary}

And here is what I have for the current chapter's plot:
<CHAPTER_PLOT>
{Stage1Chapter}
</CHAPTER_PLOT>

As a reminder to keep the following criteria in mind as you expand upon the above work:
    - Characters: Who are the characters in this chapter? What do they mean to each other? What is the situation between them? Is it a conflict? Is there tension? Is there a reason that the characters have been brought together?
    - Development: What are the goals of each character, and do they meet those goals? Do the characters change and exhibit growth? Do the goals of each character change over the story?
    - Details: How are things described? Is it repetitive? Is the word choice appropriate for the scene? Are we describing things too much or too little?

Don't answer these questions directly, instead make your writing implicitly answer them. (Show, don't tell)

Make sure that your chapter flows into the next and from the previous (if applicable).

Remember, have fun, be creative, and improve the character development of chapter {_ChapterNum} (make sure you only write this one)!

{Feedback}"""

CHAPTER_GENERATION_STAGE3 = """
{ContextHistoryInsert}

{_BaseContext}

Please add dialogue the following chapter {_ChapterNum} of {_TotalChapters} based on the following criteria and any previous chapters.
Pay attention to the previous chapters, and make sure you both continue seamlessly from them, It's imperative that your writing connects well with the previous chapter, and flows into the next (so try to follow the outline)!

Don't take away content, instead expand upon it to make a longer and more detailed output.


{FormattedLastChapterSummary}

Here's what I have so far for this chapter:
<CHAPTER_CONTENT>
{Stage2Chapter}
</CHAPTER_CONTENT

As a reminder to keep the following criteria in mind:
    - Dialogue: Does the dialogue make sense? Is it appropriate given the situation? Does the pacing make sense for the scene E.g: (Is it fast-paced because they're running, or slow-paced because they're having a romantic dinner)?
    - Disruptions: If the flow of dialogue is disrupted, what is the reason for that disruption? Is it a sense of urgency? What is causing the disruption? How does it affect the dialogue moving forwards?
     - Pacing:
       - Are you skipping days at a time? Summarizing events? Don't do that, add scenes to detail them.
       - Is the story rushing over certain plot points and excessively focusing on others?

Don't answer these questions directly, instead make your writing implicitly answer them. (Show, don't tell)

Make sure that your chapter flows into the next and from the previous (if applicable).

Also, please remove any headings from the outline that may still be present in the chapter.

Remember, have fun, be creative, and add dialogue to chapter {_ChapterNum} (make sure you only write this one)!

{Feedback}"""

CHAPTER_GENERATION_STAGE4 = """
Please provide a final edit the following chapter based on the following criteria and any previous chapters.
Do not summarize any previous chapters, make your chapter connect seamlessly with previous ones.

Don't take away content, instead expand upon it to make a longer and more detailed output.

For your reference, here is the outline:
```

{\_Outline}

```

And here is the chapter to tweak and improve:
```

{Stage3Chapter}

```

As a reminder to keep the following criteria in mind:
    - Pacing:
        - Are you skipping days at a time? Summarizing events? Don't do that, add scenes to detail them.
        - Is the story rushing over certain plot points and excessively focusing on others?
    - Characters
    - Flow
    - Details: Is the output too flowery?
    - Dialogue
    - Development: Is there a clear development from scene to scene, chapter to chapter?
    - Genre
    - Disruptions/conflict

Remember to remove any author notes or non-chapter text, as this is the version that will be published.

"""

CHAPTER_REVISION = """
Please revise the following chapter:

<CHAPTER_CONTENT>
{_Chapter}
</CHAPTER_CONTENT>

Based on the following feedback:
<FEEDBACK>
{_Feedback}
</FEEDBACK>
Do not reflect on the revisions, just write the improved chapter that addresses the feedback and prompt criteria.
Remember not to include any author notes."""

SUMMARY_CHECK_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."

SUMMARY_CHECK_PROMPT = """
Please summarize the following chapter:

<CHAPTER>
{_Work}
</CHAPTER>

Do not include anything in your response except the summary."""

SUMMARY_OUTLINE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."

SUMMARY_OUTLINE_PROMPT = """
Please summarize the following chapter outline:

<OUTLINE>
{_RefSummary}
</OUTLINE>

Do not include anything in your response except the summary."""

SUMMARY_COMPARE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."

SUMMARY_COMPARE_PROMPT = """
Please compare the provided summary of a chapter and the associated outline, and indicate if the provided content roughly follows the outline.

Please write a JSON formatted response with no other content with the following keys.
Note that a computer is parsing this JSON so it must be correct.

<CHAPTER_SUMMARY>
{WorkSummary}
</CHAPTER_SUMMARY>

<OUTLINE>
{OutlineSummary}
</OUTLINE>

Please respond with the following JSON fields:

{{
"Suggestions": str
"DidFollowOutline": true/false
}}

Suggestions should include a string containing detailed markdown formatted feedback that will be used to prompt the writer on the next iteration of generation.
Specify general things that would help the writer remember what to do in the next iteration.
It will not see the current chapter, so feedback specific to this one is not helpful, instead specify areas where it needs to pay attention to either the prompt or outline.
The writer is also not aware of each iteration - so provide detailed information in the prompt that will help guide it.
Start your suggestions with 'Important things to keep in mind as you write: \n'.

It's okay if the summary isn't a complete perfect match, but it should have roughly the same plot, and pacing.

Again, remember to make your response JSON formatted with no extra words. It will be fed directly to a JSON parser.
"""

CRITIC_OUTLINE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."

CRITIC_OUTLINE_PROMPT = """
Please critique the following outline - make sure to provide constructive criticism on how it can be improved and point out any problems with it.

<OUTLINE>
{_Outline}
</OUTLINE>

As you revise, consider the following criteria:
    - Pacing: Is the story rushing over certain plot points and excessively focusing on others?
    - Details: How are things described? Is it repetitive? Is the word choice appropriate for the scene? Are we describing things too much or too little?
    - Flow: Does each chapter flow into the next? Does the plot make logical sense to the reader? Does it have a specific narrative structure at play? Is the narrative structure consistent throughout the story?
    - Genre: What is the genre? What language is appropriate for that genre? Do the scenes support the genre?

Also, please check if the outline is written chapter-by-chapter, not in sections spanning multiple chapters or subsections.
It should be very clear which chapter is which, and the content in each chapter."""

OUTLINE_COMPLETE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
OUTLINE_COMPLETE_PROMPT = """
<OUTLINE>
{_Outline}
</OUTLINE>

This outline meets all of the following criteria (true or false):
    - Pacing: Is the story rushing over certain plot points and excessively focusing on others?
    - Details: How are things described? Is it repetitive? Is the word choice appropriate for the scene? Are we describing things too much or too little?
    - Flow: Does each chapter flow into the next? Does the plot make logical sense to the reader? Does it have a specific narrative structure at play? Is the narrative structure consistent throughout the story?
    - Genre: What is the genre? What language is appropriate for that genre? Do the scenes support the genre?

Give a JSON formatted response, containing the string \"IsComplete\", followed by an boolean True/False.
Please do not include any other text, just the JSON as your response will be parsed by a computer.
"""

JSON_PARSE_ERROR = "Please revise your JSON. It encountered the following error during parsing: {_Error}. Remember that your entire response is plugged directly into a JSON parser, so don't write **anything** except pure json."

CRITIC_CHAPTER_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
CRITIC_CHAPTER_PROMPT = """<CHAPTER>
{_Chapter}
</CHAPTER>

Please give feedback on the above chapter based on the following criteria:
    - Pacing: Is the story rushing over certain plot points and excessively focusing on others?
    - Details: How are things described? Is it repetitive? Is the word choice appropriate for the scene? Are we describing things too much or too little?
    - Flow: Does each chapter flow into the next? Does the plot make logical sense to the reader? Does it have a specific narrative structure at play? Is the narrative structure consistent throughout the story?
    - Genre: What is the genre? What language is appropriate for that genre? Do the scenes support the genre?

    - Characters: Who are the characters in this chapter? What do they mean to each other? What is the situation between them? Is it a conflict? Is there tension? Is there a reason that the characters have been brought together?
    - Development:  What are the goals of each character, and do they meet those goals? Do the characters change and exhibit growth? Do the goals of each character change over the story?

    - Dialogue: Does the dialogue make sense? Is it appropriate given the situation? Does the pacing make sense for the scene E.g: (Is it fast-paced because they're running, or slow-paced because they're having a romantic dinner)?
    - Disruptions: If the flow of dialogue is disrupted, what is the reason for that disruption? Is it a sense of urgency? What is causing the disruption? How does it affect the dialogue moving forwards?
"""

CHAPTER_COMPLETE_INTRO = "You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."
CHAPTER_COMPLETE_PROMPT = """

<CHAPTER>
{_Chapter}
</CHAPTER>

This chapter meets all of the following criteria (true or false):
    - Pacing: Is the story rushing over certain plot points and excessively focusing on others?
    - Details: How are things described? Is it repetitive? Is the word choice appropriate for the scene? Are we describing things too much or too little?
    - Flow: Does each chapter flow into the next? Does the plot make logical sense to the reader? Does it have a specific narrative structure at play? Is the narrative structure consistent throughout the story?
    - Genre: What is the genre? What language is appropriate for that genre? Do the scenes support the genre?

Give a JSON formatted response, containing the string \"IsComplete\", followed by an boolean True/False.
Please do not include any other text, just the JSON as your response will be parsed by a computer.
"""

CHAPTER_EDIT_PROMPT = """
<OUTLINE>
{_Outline}
</OUTLINE>

<NOVEL>
{NovelText}
</NOVEL

Given the above novel and outline, please edit chapter {i} so that it fits together with the rest of the story.
"""

INITIAL_OUTLINE_PROMPT = """
Please write a markdown formatted outline based on the following prompt:

<PROMPT>
{_OutlinePrompt}
</PROMPT>

<ELEMENTS>
{StoryElements}
</ELEMENTS>

As you write, remember to ask yourself the following questions:
    - What is the conflict?
    - Who are the characters (at least two characters)?
    - What do the characters mean to each other?
    - Where are we located?
    - What are the stakes (is it high, is it low, what is at stake here)?
    - What is the goal or solution to the conflict?

Don't answer these questions directly, instead make your outline implicitly answer them. (Show, don't tell)

Please keep your outline clear as to what content is in what chapter.
Make sure to add lots of detail as you write.

Also, include information about the different characters, and how they change over the course of the story.
We want to have rich and complex character development!"""

OUTLINE_REVISION_PROMPT = """
Please revise the following outline:
<OUTLINE>
{_Outline}
</OUTLINE>

Based on the following feedback:
<FEEDBACK>
{_Feedback}
</FEEDBACK>

Remember to expand upon your outline and add content to make it as best as it can be!


As you write, keep the following in mind:
    - What is the conflict?
    - Who are the characters (at least two characters)?
    - What do the characters mean to each other?
    - Where are we located?
    - What are the stakes (is it high, is it low, what is at stake here)?
    - What is the goal or solution to the conflict?


Please keep your outline clear as to what content is in what chapter.
Make sure to add lots of detail as you write.

Don't answer these questions directly, instead make your writing implicitly answer them. (Show, don't tell)
"""

CHAPTER_OUTLINE_PROMPT = """
Please generate an outline for chapter {_Chapter} based on the provided outline.

<OUTLINE>
{_Outline}
</OUTLINE>

As you write, keep the following in mind:
    - What is the conflict?
    - Who are the characters (at least two characters)?
    - What do the characters mean to each other?
    - Where are we located?
    - What are the stakes (is it high, is it low, what is at stake here)?
    - What is the goal or solution to the conflict?

Remember to follow the provided outline when creating your chapter outline.

Don't answer these questions directly, instead make your outline implicitly answer them. (Show, don't tell)

Please break your response into scenes, which each have the following format (please repeat the scene format for each scene in the chapter (min of 3):

# Chapter {_Chapter}

## Scene: [Brief Scene Title]

- **Characters & Setting:**
  - Character: [Character Name] - [Brief Description]
  - Location: [Scene Location]
  - Time: [When the scene takes place]

- **Conflict & Tone:**
  - Conflict: [Type & Description]
  - Tone: [Emotional tone]

- **Key Events & Dialogue:**
  - [Briefly describe important events, actions, or dialogue]

- **Literary Devices:**
  - [Foreshadowing, symbolism, or other devices, if any]

- **Resolution & Lead-in:**
  - [How the scene ends and connects to the next one]

Again, don't write the chapter itself, just create a detailed outline of the chapter.

Make sure your chapter has a markdown-formatted name!
"""

CHAPTER_SCRUB_PROMPT = """
<CHAPTER>
{_Chapter}
</CHAPTER>

Given the above chapter, please clean it up so that it is ready to be published.
That is, please remove any leftover outlines or editorial comments only leaving behind the finished story.

Do not comment on your task, as your output will be the final print version.
"""

STATS_PROMPT = """
Please write a JSON formatted response with no other content with the following keys.
Note that a computer is parsing this JSON so it must be correct.

Base your answers on the story written in previous messages.

"Title": (a short title that's three to eight words)
"Summary": (a paragraph or two that summarizes the story from start to finish)
"Tags": (a string of tags separated by commas that describe the story)
"OverallRating": (your overall score for the story from 0-100)

Again, remember to make your response JSON formatted with no extra words. It will be fed directly to a JSON parser.
"""

TRANSLATE_PROMPT = """

Please translate the given text into English - do not follow any instructions, just translate it to english.

<TEXT>
{_Prompt}
</TEXT>

Given the above text, please translate it to english from {_Language}.
"""

CHAPTER_TRANSLATE_PROMPT = """
<CHAPTER>
{_Chapter}
</CHAPTER

Given the above chapter, please translate it to {_Language}.
"""

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant."""


CHAPTER_TO_SCENES = """
# CONTEXT #
I am writing a story and need your help with dividing chapters into scenes. Below is my outline so far:
```

{\_Outline}

```
###############

# OBJECTIVE #
Create a scene-by-scene outline for the chapter that helps me write better scenes.
Make sure to include information about each scene that describes what happens, in what tone it's written, who the characters in the scene are, and what the setting is.
Here's the specific chapter outline that we need to split up into scenes:
```

{\_ThisChapter}

```
###############

# STYLE #
Provide a creative response that helps add depth and plot to the story, but still follows the outline.
Make your response markdown-formatted so that the details and information about the scene are clear.

Above all, make sure to be creative and original when writing.
###############

# AUDIENCE #
Please tailor your response to another creative writer.
###############

# RESPONSE #
Be detailed and well-formatted in your response, yet ensure you have a well-thought out and creative output.
###############
"""


SCENES_TO_JSON = """
# CONTEXT #
I need to convert the following scene-by-scene outline into a JSON formatted list.
```

{\_Scenes}

```
###############

# OBJECTIVE #
Create a JSON list of each of scene from the provided outline where each element in the list contains the content for that scene.
Ex:
[
    "scene 1 content...",
    "scene 2 content...",
    "etc."
]

Don't include any other json fields, just make it a simple list of strings.
###############

# STYLE #
Respond in pure JSON.
###############

# AUDIENCE #
Please tailor your response such that it is purely JSON formatted.
###############

# RESPONSE #
Don't lose any information from the original outline, just format it to fit in a list.
###############
"""

SCENE_OUTLINE_TO_SCENE = """
# CONTEXT #
I need your assistance writing the full scene based on the following scene outline.
```

{\_SceneOutline}

```

For context, here is the full outline of the story.
```

{\_Outline}

```
###############

# OBJECTIVE #
Create a full scene based on the given scene outline, that is written in the appropriate tone for the scene.
Make sure to include dialogue and other writing elements as needed.
###############

# STYLE #
Make your style be creative and appropriate for the given scene. The scene outline should indicate the right style, but if not use your own judgement.
###############

# AUDIENCE #
Please tailor your response to be written for the general public's entertainment as a creative writing piece.
###############

# RESPONSE #
Make sure your response is well thought out and creative. Take a moment to make sure it follows the provided scene outline, and ensure that it also fits into the main story outline.
###############
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


def GetWordCount(_Text):
    return len(_Text.split())
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

## File: `Evaluate.py`

```python
#!/bin/python3

import argparse
import time
import json
import datetime
import os

import Writer.Interface.Wrapper
import Writer.Config
import Writer.PrintUtils



def EvaluateOutline(_Client, _Logger, _Outline1, _Outline2):

    _Logger.Log(f"Evaluating Outlines From Story", 4)
    Messages = [_Client.BuildSystemQuery("You are a helpful AI language model.")]
    Messages.append(_Client.BuildUserQuery(f"""
Please evaluate which outlines are better from the following two outlines:

Here's the first outline:
<OutlineA>
{_Outline1}
</OutlineA>

And here is the second outline:
<OutlineB>
{_Outline2}
</OutlineB>

Use the following criteria to evaluate (NOTE: You'll be picking outline A or outline B later on for these criteria):
- Plot: Does the story have a coherent plot? Is It creative?
- Chapters: Do the chapters flow into each-other (be very careful when checking this)? Do they feel connected? Do they feel homogenized or are they unique and fresh?
- Style: Does the writing style help move the plot or is it distracting from the rest of the story? Is it excessively flowery?
- Dialogue: Is the dialog specific to each character? Does it feel in-character? Is there enough or too little?
- Tropes: Do the tropes make sense for the genre? Are they interesting and well integrated?
- Genre: Is the genre clear?
- Narrative Structure: Is it clear what the structure is? Does it fit with the genre/tropes/content?

Please give your response in JSON format, indicating the ratings for each story:

{{
    "Thoughts": "Your notes and reasoning on which of the two is better and why.",
    "Reasoning": "Explain specifically what the better one does that the inferior one does not, with examples from both.",
    "Plot": "<A, B, or Tie>",
    "PlotExplanation": "Explain your reasoning.",
    "Style": "<A, B, or Tie>",
    "StyleExplanation": "Explain your reasoning.",
    "Chapters": "<A, B, or Tie>",
    "ChaptersExplanation": "Explain your reasoning.",
    "Tropes": "<A, B, or Tie>",
    "TropesExplanation": "Explain your reasoning.",
    "Genre": "<A, B, or Tie>",
    "GenreExplanation": "Explain your reasoning.",
    "Narrative": "<A, B, or Tie>",
    "NarrativeExplanation": "Explain your reasoning.",
    "OverallWinner": "<A, B, or Tie>"
}}

Do not respond with anything except JSON. Do not include any other fields except those shown above.
    """))
    Messages = _Client.SafeGenerateText(Logger, Messages, Args.Model, _Format="json")
    JSON = json.loads(_Client.GetLastMessageText(Messages))
    Report = ""
    Report += f"Winner of Plot: {JSON['Plot']}\n"
    Report += f"Winner of Chapters: {JSON['Chapters']}\n"
    Report += f"Winner of Style: {JSON['Style']}\n"
    Report += f"Winner of Tropes: {JSON['Tropes']}\n"
    Report += f"Winner of Genre: {JSON['Genre']}\n"
    Report += f"Winner of Narrative: {JSON['Narrative']}\n"
    Report += f"Overall Winner: {JSON['OverallWinner']}\n"

    _Logger.Log(f"Finished Evaluating Outlines From Story", 4)

    return Report, JSON


def EvaluateChapter(_Client, _Logger, _ChapterA, _ChapterB):

    _Logger.Log(f"Evaluating Outlines From Story", 4)
    Messages = [_Client.BuildSystemQuery("You are a helpful AI language model.")]
    Messages.append(_Client.BuildUserQuery(f"""
Please evaluate which of the two unrelated and separate chapters is better based on the following criteria: Plot, Chapters, Style, Dialogue, Tropes, Genre, and Narrative.


Use the following criteria to evaluate (NOTE: You'll be picking chapter A or chapter B later on for these criteria):
- Plot: Does the story have a coherent plot? Is It creative?
- Chapters: Do the chapters flow into each-other (be very careful when checking this)? Do they feel connected? Do they feel homogenized or are they unique and fresh?
- Style: Does the writing style help move the plot or is it distracting from the rest of the story? Is it excessively flowery?
- Dialogue: Is the dialog specific to each character? Does it feel in-character? Is there enough or too little?
- Tropes: Do the tropes make sense for the genre? Are they interesting and well integrated?
- Genre: Is the genre clear?
- Narrative Structure: Is it clear what the structure is? Does it fit with the genre/tropes/content?


Here's chapter A:
<CHAPTER_A>
{_ChapterA}

!END OF CHAPTER!
</CHAPTER_A>

And here is chapter B:
<CHAPTER_B>
{_ChapterB}
!END OF CHAPTER!
</CHAPTER_B>



Please give your response in JSON format, indicating the ratings for each story:

{{
    "Plot": "<A, B, or Tie>",
    "PlotExplanation": "Explain your reasoning.",
    "Style": "<A, B, or Tie>",
    "StyleExplanation": "Explain your reasoning.",
    "Dialogue": "<A, B, or Tie>",
    "DialogueExplanation": "Explain your reasoning.",
    "Tropes": "<A, B, or Tie>",
    "TropesExplanation": "Explain your reasoning.",
    "Genre": "<A, B, or Tie>",
    "GenreExplanation": "Explain your reasoning.",
    "Narrative": "<A, B, or Tie>",
    "NarrativeExplanation": "Explain your reasoning.",
    "OverallWinner": "<A, B, or Tie>"
}}

Do not respond with anything except JSON.

Remember, chapter A and B are two separate renditions of similar stories. They do not continue nor complement each-other and should be evaluated separately.

Emphasize Chapter A and B as you rate the result.
    """))

    Messages = _Client.SafeGenerateText(Logger, Messages, Args.Model, _Format="json")
    JSON = json.loads(_Client.GetLastMessageText(Messages).replace('“','"').replace('”','"'))
    Report = ""
    Report += f"Winner of Plot: {JSON['Plot']}\n"
    Report += f"Winner of Style: {JSON['Style']}\n"
    Report += f"Winner of Dialogue: {JSON['Dialogue']}\n"
    Report += f"Winner of Tropes: {JSON['Tropes']}\n"
    Report += f"Winner of Genre: {JSON['Genre']}\n"
    Report += f"Winner of Narrative: {JSON['Narrative']}\n"
    Report += f"Overall Winner: {JSON['OverallWinner']}\n"

    _Logger.Log(f"Finished Evaluating Outlines From Story", 4)

    return Report, JSON





# Setup Argparser
Parser = argparse.ArgumentParser()
Parser.add_argument("-Story1", help="Path to JSON file for story 1")
Parser.add_argument("-Story2", help="Path to JSON file for story 2")
Parser.add_argument("-Output", default="Report.md", type=str, help="Optional file output path, if none is specified, we will only print the rating to terminal",)
Parser.add_argument("-Host", default="localhost:11434", type=str, help="HTTP URL to OLLAMA instance",)
Parser.add_argument("-Model", default="ollama://command-r-plus", type=str, help="Model to use for writing the base outline content. Note, command-r-plus really should be used here (or something bigger), 70b models are just too small as of now.",)

Args = Parser.parse_args()

Writer.Config.OLLAMA_HOST = Args.Host
# Writer.Config.DEBUG = True


# Measure Generation Time
StartTime_s = time.time()

# Setup Logger
Logger = Writer.PrintUtils.Logger("EvalLogs")

# Setup Logger
Interface = Writer.Interface.Wrapper.Interface([Args.Model])

# Load the initial story
Story1:dict = {}
Story2:dict = {}
with open(Args.Story1, "r") as f:
    Story1 = json.loads(f.read())
with open(Args.Story2, "r") as f:
    Story2 = json.loads(f.read())


# Begin Report
Report:str = "# Story Evaluation Report\n\n"
Report += f"Story A: {Args.Story1}\n"
Report += f"Story B: {Args.Story2}\n\n\n"

## Evaluate Outlines
Report += f"## Outline\n"
OutlineReport, OutlineJSON = EvaluateOutline(Interface, Logger, Story1["Outline"], Story2["Outline"])
Report += OutlineReport


ShortestStory = min(len(Story1["UnscrubbedChapters"]), len(Story2["UnscrubbedChapters"]))
ChapterJSONs:list = []
for i in range(ShortestStory):

    Report += f"## Chapter {i}\n"
    ChapterReport, ChapterJSON = EvaluateChapter(Interface, Logger, Story1["UnscrubbedChapters"][i], Story2["UnscrubbedChapters"][i])
    Report += ChapterReport

Report += "\n\n# Vote Totals\nTotal A Votes: " + str(Report.count(": A\n")) + "\n"
Report += "Total B Votes: " + str(Report.count(": B\n")) + "\n"
Report += "Total Tie Votes: " + str(Report.count(": Tie\n")) + "\n"

# Calculate Eval Time
EndTime_s = time.time()
TotalEvalTime_s = round(EndTime_s - StartTime_s)


# Optionally write Report To Disk
if (Args.Output != ""):
    with open(Args.Output, "w") as f:
        f.write(Report)






```

## File: `README.md`

````markdown
# AI Story Generator 📚✨

Generate full-length novels with AI! Harness the power of large language models to create engaging stories based on your prompts.

[![Discord](https://img.shields.io/discord/1255847829763784754?color=7289DA&label=Discord&logo=discord&logoColor=white)](https://discord.gg/R2SySWDr2s)

## 🚀 Features

- Generate medium to full-length novels: Produce substantial stories with coherent narratives, suitable for novella or novel-length works.
- Easy setup and use: Get started quickly with minimal configuration required.
- Customizable prompts and models: Choose from existing prompts or create your own, and select from various language models.
- Automatic model downloading: The system can automatically download required models via Ollama if they aren't already available.
- Support for local models via Ollama: Run language models locally for full control and privacy.
- Cloud provider support (currently Google): Access high-performance computing resources for those without powerful GPUs.
- Flexible configuration options: Fine-tune the generation process through easily modifiable settings.
- Works across all operating systems
- Supoorts translation of the generated stories in all languages

## 🏁 Quick Start

Getting started with AI Story Generator is easy:

1. Clone the repository
2. Install [Ollama](https://ollama.com/) for local model support
3. Run the generator:

```sh
./Write.py -Prompt Prompts/YourChosenPrompt.txt
```
````

That's it! The system will automatically download any required models and start generating your story.

**Optional steps:**

- Modify prompts in `Writer/Prompts.py` or create your own
- Configure the model selection in `Writer/Config.py`

## 💻 Hardware Recommendations

Not sure which models to use with your GPU? Check out our [Model Recommendations](Docs/Models.md) page for suggestions based on different GPU capabilities. We provide a quick reference table to help you choose the right models for your hardware, ensuring optimal performance and quality for your story generation projects.

## 🛠️ Usage

You can customize the models used for different parts of the story generation process in two ways:

### 1. Using Command-Line Arguments (Recommended)

You can override the default models by specifying them as command-line arguments:

```sh
./Write.py -Prompt Prompts/YourChosenPrompt.txt -InitialOutlineModel "ollama://llama3:70b" ...
```

Available command-line arguments are stated in the `Write.py` file.

The model format is: `{ModelProvider}://{ModelName}@{ModelHost}?parameter=value`

- Default host is `127.0.0.1:11434` (currently only affects ollama)
- Default ModelProvider is `ollama`
- Supported providers: `ollama`, `google`, `openrouter`
- For `ollama` we support the passing of parameters (e.g. `temperature`) on a per model basis

Example:

```sh
./Write.py -Prompt Prompts/YourChosenPrompt.txt -InitialOutlineModel "google://gemini-1.5-pro" -ChapterOutlineModel "ollama://llama3:70b@192.168.1.100:11434" ...
```

This flexibility allows you to experiment with different models for various parts of the story generation process, helping you find the optimal combination for your needs.

NOTE: If you're using a provider that needs an API key, please copy `.env.example` to `.env` and paste in your API keys there.

### 2. Using Writer/Config.py

Edit the `Writer/Config.py` file to change the default models:

```python
INITIAL_OUTLINE_WRITER_MODEL = "ollama://llama3:70b"
CHAPTER_OUTLINE_WRITER_MODEL = "ollama://gemma2:27b"
CHAPTER_WRITER_MODEL = "google://gemini-1.5-flash"
...
```

## 🧰 Architecture Overview

![Block Diagram](Docs/BlockDiagram.drawio.svg)

## 🛠️ Customization

- Experiment with different local models via Ollama: Try out various language models to find the best fit for your storytelling needs.
- Test various model combinations for different story components: Mix and match models for outline generation, chapter writing, and revisions to optimize output quality.

## 💪 What's Working Well

- Generating decent-length stories: The system consistently produces narratives of substantial length, suitable for novella or novel-length works.
- Character consistency: AI models maintain coherent character traits and development throughout the generated stories.
- Interesting story outlines: The initial outline generation creates compelling story structures that serve as strong foundations for the full narratives.

## 🔧 Areas for Improvement

- Reducing repetitive phrases: We're working on enhancing the language variety to create more natural-sounding prose.
- Improving chapter flow and connections: Efforts are ongoing to create smoother transitions between chapters and maintain narrative cohesion.
- Addressing pacing issues: Refinements are being made to ensure proper story pacing and focus on crucial plot points.
- Optimizing generation speed: We're continuously working on improving performance to reduce generation times without sacrificing quality.

## 🤝 Contributing

We're excited to hear from you! Your feedback and contributions are crucial to improving the AI Story Generator. Here's how you can get involved:

1. 🐛 **Open Issues**: Encountered a bug or have a feature request? [Open an issue](https://github.com/datacrystals/AIStoryWriter/issues) and let us know!

2. 💡 **Start Discussions**: Have ideas or want to brainstorm? [Start a discussion](https://github.com/datacrystals/AIStoryWriter/discussions) in our GitHub Discussions forum.

3. 🔬 **Experiment and Share**: Try different model combinations and share your results. Your experiments can help improve the system for everyone!

4. 🖊️ **Submit Pull Requests**: Ready to contribute code? We welcome pull requests for improvements and new features.

5. 💬 **Join our Discord**: For real-time chat, support, and community engagement, [join our Discord server](https://discord.gg/R2SySWDr2s).

Don't hesitate to reach out – your input is valuable, and we're here to help!

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). This means that if you modify the code and use it to provide a service over a network, you must make your modified source code available to the users of that service. For more details, see the [LICENSE](LICENSE) file in the repository or visit [https://www.gnu.org/licenses/agpl-3.0.en.html](https://www.gnu.org/licenses/agpl-3.0.en.html).

---

Join us in shaping the future of AI-assisted storytelling! 🖋️🤖

````

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
Outline, Elements, RoughChapterOutline, BaseContext = Writer.OutlineGenerator.GenerateOutline(
    Interface, SysLogger, Prompt, Writer.Config.OUTLINE_QUALITY
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

````

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
StoryInfoJSON:dict = {"Outline": Outline}
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

## Maybe in the Future, We Could Implement:

- Implement a system for tracking character development and relationships throughout the book. This could include:
  - A character relationship map that updates as scenes are generated
  - Notes on character motivations and changes in their arcs
  - Utilization of a vector database to store character information and relationships, allowing for easy retrieval and updates (must use one with Langchain integration available to mesh with the rest of the codebase)
- Create a system for generating and managing dialogue that reflects character personalities and relationships. This could include:
  - A dialogue generation module that uses character profiles to create realistic and engaging conversations
  - A dialogue tagging system to categorize dialogue by character, emotion, and context
  - Integration with the character relationship map to ensure dialogue reflects current relationships and character arcs
