# 1. Introduction and Features

Fiction Fabricator is an advanced, AI-powered framework for generating complete, multi-chapter novels from a single creative prompt. It leverages a suite of modern Language Learning Models (LLMs) through a unified interface, employing a sophisticated, multi-stage pipeline of outlining, scene-by-scene generation, and iterative revision to produce high-quality, coherent long-form narratives.

This project is a significantly modified and enhanced fork of **[AIStoryteller by datacrystals](https://github.com/datacrystals/AIStoryteller)**. It was created to enhance the original project with a focus on provider flexibility, improved narrative coherence, and a more powerful, user-configurable generation process.

## Purpose

The purpose of this project is to create long-form fictional prose content leveraging the text generation capabilities of modern LLMs. Fiction Fabricator is designed to be a powerful, flexible, and transparent tool for creating long-form fiction with AI, which unlike other projects that focus on content generation, Fiction Fabricator is especially tailored to creating coherent, enjoyable novels that can be read and enjoyed by humans but which require minimal human intervention during the creation process.

### Creation Workflow

To give you a high level overview of the book creation process this project enables, here is a brief outline of the workflow:

1. Human provides a prompt, which is a premise written into several sentences (Tools/PromptGenerator.py can help with this and Tools/PremiseGenerator.py can help brainstorm ideas).
2. Human selects a model from the list of available models on the screen
3. Fiction Fabricator then outlines, critiques, revises and then writes the book, chapter by chapter with each chapter being broken down into scenes.
4. Content is dumped into the `Stories/` directory, with each run generating a unique, timestamped directory containing the final story, run statistics, and detailed debug files for every LLM call, providing complete transparency into the generation process.
5. User should then read the content and make any necessary edits as the content is not guaranteed to be perfect and making edits is what case law suggests is necessary to own the copyright to the content.

Frighteningly simple, right? A lot simpler than Steven King doing a gram of cocaine per page while writing "It".

## Key Features & Modifications

- **Unified Multi-Provider Interface**: Seamlessly switch between LLM providers like **Google Gemini, Groq, Mistral, Ollama, and NVIDIA NIM** using a simple URI format (e.g., `groq://llama3-70b-8192`).
- **Robust & Predictable NVIDIA NIM Integration**: The NVIDIA integration has been specifically hardened to provide full user control. Models are **manually and explicitly listed** in the `config.ini` file, removing the unpredictability of a dynamic discovery function and ensuring that any model you have access to can be used.
- **Flexible API Configuration**: Easily configure API endpoints, including the crucial `NVIDIA_BASE_URL`, either through a `.env` file for security or directly in `config.ini` for simplicity.
- **Advanced Scene-by-Scene Generation**: Instead of attempting to generate entire chapters at once, Fiction Fabricator breaks chapter outlines down into individual scenes. It writes each scene with context from the preceding one, dramatically improving narrative flow and short-term coherence.
- **Iterative Critique & Revision Engine**: At critical stages of generation (outline, scene breakdown, chapter writing), the system uses an LLM to critique its own output and then revise it based on that feedback. This self-correction loop significantly enhances the quality of the final product.
- **Intelligent Prompt Engineering**: Includes a powerful utility (`Tools/PromptGenerator.py`) that takes a user's simple idea and uses an LLM-driven, multi-step process to expand it into a rich, detailed prompt perfect for generating a complex story.
- **Short Story Generator (`Tools/ShortStoryWriter.py`)**: A dedicated tool that uses an iterative generation process to quickly write complete, self-contained short stories from a single premise, saving them to a separate `Short_Story/` directory.
- **Episodic Chapter Generator (`Tools/WebNovelChapterWriter.py`)**: A powerful tool for writing individual chapters for web novels or other serialized content. Provide a master premise and a topic for the current chapter, and optionally provide the previous chapter to ensure perfect narrative continuity between writing sessions.
- **Comprehensive Logging**: Every run generates a unique, timestamped directory in `Logs/`, containing the final story, run statistics, and detailed debug files for every LLM call, providing complete transparency into the generation process.
- **Developer & Power-User Utilities**:
  - **`Tools/Test.py`**: A testing script for quickly running generations with different pre-defined model configurations.
  - **`Evaluate.py`**: A powerful A/B testing tool that uses an LLM to compare two generated stories on multiple axes, such as plot, style, and dialogue.
  - **`Tools/PromptGenerator.py`**: A tool to generate the more comprehensive prompt in `Prompt/` expected as a parameter by `Write.py`.
  - **`Tools/PremiseGenerator.py`**: A brainstorming tool to generate 10 unique premises from a high-level theme.
