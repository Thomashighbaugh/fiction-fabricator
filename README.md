# fiction fabricator

---

**What is it?** `fiction fabricator` is a command-line tool that uses AI (Google Gemini) to automatically write a complete first-draft novel or short story based on your idea/prompt. It handles outlining, chapter writing, and interactive AI-assisted editing.

Heavily inspired by [pulpgen](https://github.com/pulpgen-dev/pulpgen) and other projects generating text with agentic AI but with a more modular architecture and (coming soon) a broader set of API providers. The use of XML for state management and patching is also a key innovation that all credit is owed to **pulpgen** for.

---

##  Quick Start

1.  **Install:** Requires Python 3.13+ and `uv`.
    ```bash
    # Clone or download the code first
    cd fiction-fabricator
    uv sync
    ```
2.  **API Key:** Create a `.env` file in the `fiction fabricator` directory with `GEMINI_API_KEY=YOUR_KEY_HERE`
    API Key can be created in Google AI Studio: https://aistudio.google.com/app/apikey

3.  **Run (New Project):**

    ```bash
    # Example using a prompt file:
    uv run python main.py --prompt your_idea.txt

    # Or run without --prompt to enter your idea interactively:
    uv run python main.py
    ```

4.  **Run (Resume Project):**
    ```bash
    uv run python main.py --resume path/to/your/project_folder
    ```
5.  **Output:** Finds/creates a project folder (like `YYYYMMDD-slug-uuid`) containing XML state files and exported manuscripts.

---

## Usage

Launch the `fiction fabricator` agent from your terminal within the project directory:

```bash
uv run python main.py [OPTIONS]
```

**Command-Line Options:**

- `--resume FOLDER_PATH`: Point to an existing project folder (e.g., `20240315-space-opera-saga-f3a4b1c9`) to continue a previously started job.
- `--prompt FILE_PATH`: Provide the path to a `.txt` file containing your book idea. This is only used when starting a _new_ project (ignored if `--resume` is used).
- `--lorebook JSON_FILE`: Load a Tavern AI format lorebook to provide world-building context during story generation.
- `--create-lorebook JSON_FILE`: Launch the interactive lorebook manager to create or edit lorebooks with LLM assistance.
- `--create-prompt`: Transform a basic story idea into a comprehensive, detailed prompt using LLM assistance.

## Project Files

`fiction fabricator` keeps its work organized in a dedicated project folder (e.g., `20240315-robot-romance-a1b2c3d4`):

- **`YYYYMMDD-slug-uuid/` (Project Folder):** The main case file, named with the date, a slugified title, and a unique ID.
- **`outline.xml`:** The initial blueprint. Contains metadata (title, synopsis, your idea), character profiles, and chapter/scene summaries generated in Phase 1. This is the starting map.
- **`patch-NN.xml`:** Sequential dispatch logs. Each patch records a chunk of generated chapter content (Phase 2) or the results of an editing action (Phase 3). When resuming, `fiction fabricator` replays these patches to reconstruct the story's current state.
- **Exported Files:** The `Export Menu` in the editing phase allows you to create various output files, such as `my-story.epub`, `my-story-full.md`, and individual chapter markdown files.

## Lorebook Features

`fiction fabricator` includes comprehensive lorebook support for consistent world-building:

- **Automatic Context Injection:** Lorebook entries are automatically included in story generation when their keywords match the content being created
- **Interactive Lorebook Manager:** Create and edit lorebooks with the `--create-lorebook` flag  
- **LLM-Assisted Creation:** AI helps expand basic entries into rich, detailed world-building content
- **Tavern AI Compatible:** Uses standard Tavern AI lorebook format for compatibility with existing tools

**Quick Examples:**
```bash
# Create a new lorebook
uv run python main.py --create-lorebook fantasy_world.json

# Use lorebook with story generation  
uv run python main.py --lorebook fantasy_world.json --prompt story_idea.txt
```

For complete lorebook documentation, see [LOREBOOK.md](LOREBOOK.md) or [LOREBOOK_QUICK.md](LOREBOOK_QUICK.md) for a quick reference.

## Prompt Enhancement Features

Transform your basic story ideas into comprehensive, detailed prompts with AI assistance:

- **Interactive Enhancement:** The `--create-prompt` flag launches an interactive session to expand your ideas
- **Smart Expansion:** AI transforms simple concepts into rich prompts with character development, world-building, and thematic depth
- **Story Type Selection:** Choose between novel, short story, or let AI decide the best format
- **Genre Integration:** Specify genre preferences or let AI determine the best fit
- **Lorebook Integration:** Automatically incorporates relevant world-building context when available
- **Multiple Output Options:** Save enhanced prompts to files, copy for manual use, or immediately start story generation

**Quick Examples:**
```bash
# Create an enhanced prompt interactively
uv run python main.py --create-prompt

# Use with existing lorebook for richer context
uv run python main.py --create-prompt --lorebook world.json
```

## Content Pipeline

This is a multiphase process:

**Phase 1: Outline Generation**

- **User Choice:** First, you'll choose whether to generate a multi-chapter **Novel** or a 3-5 scene **Short Story**.
- **Agent Action:** Takes your initial idea. Instructs the AI to flesh out:
  - A compelling title and synopsis.
  - A cast of characters (`<characters>`).
  - Detailed summaries for each chapter or scene (`<chapters>`).
- **Output:** Saves the complete structure to `outline.xml`.

**Phase 2: Content Drafting**

- **Agent Action:** Systematically works through the `outline.xml`. Selects batches of chapters/scenes needing content. Instructs the AI to write the full prose for each selected chapter, guided by its summary and the overall narrative context. XML creates a much better overall structure in the output using per-paragraph IDs 
- **Output:** Saves generated content in sequential `patch-NN.xml` files.

**Phase 3: Interactive Revision & Refinement**

- **Agent Action:** This is where you step back in! `fiction fabricator` presents an interactive menu with powerful editing tools that leverage the AI:
  - **Make Chapter(s) Longer:** Select chapters and specify a target word count.
  - **Rewrite Chapter (with instructions):** Choose a chapter and provide specific instructions for a rewrite.
  - **Rewrite Chapter (Fresh Rewrite):** Similar to above, but the AI is _not_ shown the chapter's _current_ content, encouraging a completely fresh take.
  - **Ask LLM for Edit Suggestions:** The AI analyzes the _entire_ current draft and provides a numbered list of potential improvements.
- **User Interaction:** You select the tool, provide necessary input, and **confirm** whether to apply the AI-generated patches.

**Phase 4: Exporting**

- From the editing menu, you can access the **Export Menu** at any time.
- **Output:** You can generate the manuscript in various formats:
  - Single Markdown file
  - One Markdown file per chapter
  - EPUB e-book format
  - HTML format

## Tips for Success

1.  **Clear and Explicit Ideas:** The quality of the output heavily depends on the clarity of your initial idea/prompt. Be as specific and detailed as possible.
2.  **Iterate and Refine:** Use the interactive editing tools to refine and improve the draft. Don't hesitate to ask for rewrites or make chapters longer.
3.  **Human in the Loop:** While `fiction fabricator` can generate a complete draft, consider it a starting point. Review and polish the manuscript to ensure it meets your standards.
4.  **Experiment:** Try different genres, styles, and story ideas to see how the AI responds. Each run can yield unique results.

## License

MIT License. See the [LICENSE](LICENSE) file for the legalese.
