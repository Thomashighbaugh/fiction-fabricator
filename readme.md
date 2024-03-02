# the Fiction Fabricator

A realistic means of generating fiction with AI in a structured, organized and customizable manner.  This application is designed to help authors develop their novels by providing a structured framework for outlining, character development, setting, scene creation and content generation from a terminal based menu system. It also uses GPT4Free as a Drop in Replacement for OpenAI's API calls to generate content based on the author's input without needing to pay for the pleasure.

## Introduction

Plenty of projects exist that take a single line of text and turn that into a book written in markdown, just not a very good book because the technology is not quite there yet to do that (though it is pretty close if you chain your prompts together).

There is also the issue of iteration when one line of text input is all you have to guide the generative AI model, which leaves a huge amount of potential customization unexploited and rather large surface for a minor error to play out into a big mess over hundreds of pages of text.

This is my attempt to address these issues by giving the user more control at a variety of critical points and using the content of files the user is free to modify themselves at any point as well. I wrote this hopefully pump out smutty erotica novels for Kindle to make a quick buck, which I won't give myself away as to what they are titled or my pen name but I will say that it works for that (using the uncensored mixtral-8x7b model it seems).

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/).

```bash
git clone https://github.com/Thomashighbaugh/fiction-fabricator

cd fiction-fabricator

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

Since this is tooled with GPT4Free as a replacement for openAI's API, you need to set your OpenAI environmental variable to a HuggingFace key, details can be found on GPT4Free's [README.md](https://github.com/xtekky/gpt4free), then export the environmental variable in your terminal session.

```bash

export OPENAI_API_KEY=your-huggingface-api-key

```

> **NOTE**
> GPT4Free enables the use of additional models other than the GPT-3.5 and GPT-4.0 related models one can access with the OPENAI  API. DIfferent models work differently with some content and may or may not jailbreak effectively if you are generating sufficiently NSFW material. I reccomend trying mixtral-7x8b and Gemini-Pro as well as GPT-4-32k and gpt-3.5-turbo-16k.

> **ADDITIONAL NOTE**
> I may move the API calls to a "pure GPT4Free" version of this application in the future, but for now, it is a drop-in replacement for OpenAI's API.

## Usage

To begin, set the style, genre, and themes in the text files located in the `/development/config/*.txt` files. You can do this within the menu  system if you like (see below), or with your favorite text editor as there is no prompting going on with those aspects of the process, they are just value stores.

* `author_style.txt` - Your preferred writing style. Avoid using names of living authors or those protected by copyright.
* `description.txt` - A single-sentence description of your novel's style.
* `genre.txt` - The concise genre of your novel (e.g., "science fiction").
* `themes.txt` - A bulleted list of the primary themes you wish to explore in your novel.
* `tone.txt` -  The tone for the prose of your novel.

### Running the Application

> Note:
> This application is a command-line tool for the time being as my interest is in generating text files with it, not reading them in an application window as I can do that with programs I don't have to maintain.

Initiate it using:

```bash
python main.py
```

In general, the process involves crafting "seeds" (akin to seeds of an idea). These seeds are brief outlines describing characters, settings, scenes, etc., which the LLM expands upon. All developmental writing is directed into the `development` sub-folders for now, until I determine how best to keep the blank files and work products separate.

### Menus

Navigate through the command-line menus using the numbers adjacent to each menu option and the 'x' key to go back.

The commands should be executed in sequence as they gradually define the novel and flesh out characters, settings, scenes, etc.

> Note:
> If a dependency is necessary but I did not list it in the requirements.txt file, please let me know by filing an issue on the repository and I will update the file.

### Terminology

The following terms are used in the menus and to organize prompts and development material:

- Outline: This is a high-level summary of the book's structure, including main events and turning points. It helps maintain the story's pacing and coherence, ensuring that all elements are connected and consistent.
- Characters: These are detailed descriptions of each character, including their appearance, personality, background, motivations, relationships, and development arc. This helps maintain consistency in character behavior and dialogue, as well as create well-rounded and believable characters.
- Settings: Detailed notes about the story's settings, including geographical, historical, and cultural context. This helps create a vivid and immersive world for their readers.
- Scenes: A breakdown of the story into individual scenes, with brief descriptions of each. This helps track the progression of the story and ensure a proper balance of action, dialogue, and description.
- Research (not implemented): Any research conducted for the book, including historical, scientific, or cultural information relevant to the story.
- Timeline (not implemented): A chronological list of events, often including dates and times, that helps authors maintain consistency in their narrative and ensure that the story's events unfold logically.
- Style guide (not implemented): A list of guidelines for the author's writing style, including preferred grammar, punctuation, and formatting. This helps authors maintain consistency throughout the book and makes the editing process smoother.
