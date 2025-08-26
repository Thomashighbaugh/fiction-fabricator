# Project To-Do List

My rough list and attempt to keep some order and sanity in my work on this project moving forward. Using special highlighting and todo tracking via GitHub issues and Neovim plugins that _hopefully_ will prompt me to refer back to this list and keep it updated.

## Of Immediate Concern

These are items I am intending to get to sooner rather than later, this list will guide subsequent commits I make to the project repo directly.

- [ ] TODO Three books were not enough to exorcise the ghost in this machine, so like a second 5 year plan here are another three books to make this government obsolete(lol /snarky historical reference)

  - [x] DONE Book 4:
    - garbage, absolute garbage, the thing was a smear of one sentence paragraphs and the critique and revision steps were not working properly, so I made them stricter and more more focused.
  - [ ] TODO Book 5:

  - [ ] TODO Book 6:

- [ ]
- [ ] TODO to mitigate errors from critique and revision over scenes in the pipelines that generate the text itself (short stories, novels, web novels, etc), each scene within a chapter should be critiqued and revised separately, with the critique and revision steps being applied to each scene individually, in generating the final book, the scenes should each be their own markdown files, which then are stitched together in order into chapter files that are then stitched together into the final book. Both chapter and scene files should be presented with the file book file in the directory tat the end of the novel generation process to mitigate any hiccups in the process rendering the whole process a waste of time.

## Intended in Future

These are not pressing needs, but medium to long term mile markers along the project roadmap (**_pull requests always welcome_**).

- [ ] TODO means of picking back up from an uncompleted generation attempt

## Archive

These are items that have been completed, obviously. Kept here for posterity and as a means of seeing how much progress has been made trekking towards that horizon of feature-completeness. They are **not** in any particular order, sometimes I have added the new items to the bottom of the list, other times to the top depending on my focus at the time and if I cared about the order of the list at all when moving them. Also items that were nested were generally pulled as they finished, thus are not nested(except for the books, they wanted to stay together to aide my interpretation of the list so this would not work as a changelog to deduce my creative process or ideation process from. But from this admission, my earnest commitment to informative documentation and transparency in my work should be clear.

- [x] DONE Create a unified menu the user can use to select if they want to generate a book, short story, generate ideas or generate a novel prompt
- [x] DONE Create a tool to write short stories using the project's infrastructure, using the same prompt as a novel but with a shorter length
- [x] DONE create a tool to write individual chapters for a web based lightnovel or CYOA style story
- [x] DONE rebase on original project, refactoring while preserving more of original functionality
- [x] DONE integrate Nvidia NIM endpoints efficiently
- [x] DONE Integrating at least some of the Github Models using the means provided on the model playground pages _vis-a-vis_ GitHub Models
- [x] DONE timeout for generations, preventing hanging calls from compromising generation pipeline
- [x] DONE Create tool to generate the ideas to feed into `Tools/PromptGeneration.py`
- [x] DONE create documentation for the project and link to it on the README.md
- [x] DONE separate the critique and revision into three separate critique and revision steps one checking the consistency within the general plot and related to plot points immeadiately before and after, a critique and revision cycle specific to stylistic, tone,gere and theme adherence and a structural+length checks
- [x] DONE debug cycle by using project to create at least 3 books and catch any errors during that process.
  - [x] DONE Book 1: Still too short, need to break the scene generation into smaller chunks
  - [x] DONE Book 2: Still too short, cut off in critique phase and cut offs in the beginning contextual generation, which have been fixed and the generation cycle is now more iterative. Still getting more errors than I would like from the word count minimum checks but we will see how it goes.
  - [x] DONE Book 3: still too short, original text is long enough but the critique and revision steps are cutting it off too early or trying to do too much at once, so I will break these into smaller chunks and see how it goes. I will also try to use the new menu system to select a premise and prompt from the generated list of premises and prompts, which should help with consistency and coherence in the generation process.
- [x] DONE create a numerical scoring system for application before each of the critique steps to determine if the generated context is sufficiently low enough to warrant the critique and revision
- [x] DONE create a way to select from the generated premises and prompts from a list when prompted for a premise/prompt input by the new menu system
- [x] DONE for short stories, full novels, and webnovel/lightnovel chapters, create a means of optionally including a "lore book" or "world book" that can be used to provide context for the generation process, which can be used to generate more consistent and coherent stories and be part of the consistency checks against the outline applied by the critique and revision steps
  - [x] DONE the inclusion of a "lore book" or "world book" should be optional, in the generation steps that support it the user should be able to select if they want to include it, then if they select yes they can select from a lorebook in a specific directory or they can select to generate a new lorebook manually based on a template file, modify an existing lorebook, or generate a new lorebook from scratch with the LLM
  - [x] DONE tool and associated menu item to generate a "lore book" or "world book" that can be used to provide context for the generation process, which can be used to generate more consistent and coherent stories and be part of the consistency checks against the outline applied by the critique and revision steps
  - [x] DONE Lorebook generated by the prompt or premise selected already in those pipelines in which the user has already selected such
- [x] DONE Presently, operation of the program makes an absolute mess of the project directory, where `LoreBooks/`, `PromptGenLogs/`, `Short_Story/`, `Stories/`, `Web_Novel_Chapters/`, `Prompts/`, `Premises/` all crowd the two important `Writer/` and `Tools/` directories that house the code while `Evaluate.py` is not in any directory at all. This is a mess. Generated, final content (including Prompts, but not Premises which are inputs for Prompt Generation) should be nested in a `Generated_Content` within which the directories they are currently output into should be located. Logs and other input items (like the Premises that are used as Prompt Generation inputs) should be nested in a general `Logs/` directory within the subdirectories they are cached in already. These new directories should be appended to the end of the `.gitignore` file and the `Evaluate.py` should be in the `Tools/` directory
- [x] DONE the `Tools/` and `Writer/` directories must be nested within a `src` directory and the `main.py` script adjusted to accommodate these changes.
- [x] DONE update the cleanup script to remove Logs but not generated content, as the generated content is now in a `Generated_Content/` directory and the logs are in a `Logs/` directory. The cleanup script should also be updated to NOT remove the `LoreBooks/` directory and its contents,
- [x] DONE make the needed documentation updates reflecting the addition of Lorebooks, detailing the added features and how they are interacted with. Additionally documentation should be updated to reflect the new locations of python code to the `src/` subdirectory and the new locations of logs within the `Log/` directory and the Generated Content in the `Generated_Content/` directory
- [x] DONE refactor prompt generation to not only have the sections recently added to it, but to title these sections in the content it outputs so the user can appreciate the structure of the prompt quickly and easily.
- [x] DONE Make a lorebook entry on the main menu for creating a lorebook, entries in a new or existing lorebook or editing/removing existing entries/lorebooks without needing to be in a generation pipeline. This should include prompting the LLM to make lorebook entries based on user prompting or existing lorebook entries, as well as the ability to edit existing lorebook entries and remove them from the lorebook. This should also include the ability to generate a new lorebook from scratch with the LLM, which can be used to provide context for the generation process, which can be used to generate more consistent and coherent stories and be part of the consistency checks against the outline applied by the critique and revision steps.
- [x] DONE outline generation, after being supplied with the prompt should then ask if it is a short story or novel, if the latter it should ask for the number of chapters, if the former it should ask for the length in words with a default of 15,000, then it should generate an outline based on that information and the prompt, with the critique and revision steps, then the expanded per-scene outlines and their critique and revision steps.Short story and novel outlines should be separated from each other.
- [x] DONE the outline is still turning into prose, and making no sense, due to the critique and revision steps, so create specific critique and revision steps specific for the outline generation process (just one of them, comprehensively critiquing and revising the general outline and another for each chapter's expanded outline.)
- [x] DONE short story generation should now require an outline
- [x] DONE Create an additional outline type specifically for web novels, which are more open ended and continuous thus are not limited to a finite number of chapters or scenes within the story thus outlining them one should be able to append new chapters to an existing web model outline or create a new one entirely. When selecting if an outline is for short story or novel, a third "web novel" option should now be available enabling the selection of a previous web novel outline or creating a new outline, after the selection asking how many chapters to add to the outline and then what events should occur in these chapters``
