# .github/documentation/usage.md
# Fiction Fabricator - User Guide

This document provides a guide for using the Fiction Fabricator application.

## 1. Getting Started

### 1.1. Prerequisites

*   **Python:**  You need Python 3.9 or higher installed.
*   **Ollama:** You need a local Ollama instance running.  See the [Ollama documentation](https://ollama.ai/) for installation instructions.  Make sure you have pulled at least one model (e.g., `mistral`).
* **Dependencies** Install with `pip install -r requirements.txt` within a virtual environment.

### 1.2. Running the Application

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd gui-fab-fict
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    It is recommended doing this step within a virtual environment.

3.  **Run the application:**
    ```bash
    ./run
    ```
    This will start the Streamlit application. You can access it in your web browser at the URL provided by Streamlit (usually `http://localhost:8501`).

## 2. Application Workflow

The Fiction Fabricator guides you through a step-by-step process to generate your novel:

### 2.1. Sidebar - Settings & Project

*   **Select Ollama Model:**  Choose the Ollama model you want to use from the dropdown menu.  This allows you to experiment with different models. The available models are fetched from your local Ollama instance.
*   **Project Management:**
    *   **New Project:** Create a new project by entering a name in the "New Project Name" field and clicking "Save Project".
    *   **Select Project:** Choose an existing project from the dropdown menu.
    *   **Save Project:** Saves the current state of your project (all generated content, settings, etc.) to a JSON file.
    *   **Load Project:** Loads a previously saved project from a JSON file.  This will restore the entire application state.

### 2.2. Main Panel - Novel Generation Workflow

The main panel is divided into two columns: the **Workflow** column on the left and the **Display** column on the right.  The Workflow column guides you through the content generation steps.  The Display column shows the current state of your generated content.

1.  **Story Idea:**
    *   Enter your initial story idea in the text area. This is the starting point for your novel.

2.  **Book Specification:**
    *   Click "Generate Book Specification" to generate a detailed book specification based on your story idea.
    *   The generated Book Spec will be displayed in JSON format in the Display column.
    *   You can edit the Book Specification directly in the expandable "Edit Book Specification" section.  Use the "Save Book Spec" button to save your changes, and the "Enhance Book Spec" button to have the LLM improve it.

3.  **Plot Outline:**
    *   Once you have a Book Specification, click "Generate Plot Outline" to create a three-act plot outline.
    *   The generated Plot Outline (Act One, Act Two, Act Three) will be displayed in the Display column.
    *   You can edit the Plot Outline in the expandable "Edit Plot Outline" section.  Use the "Save Plot Outline" button to save edits, and the "Enhance Plot Outline" button for LLM-powered improvements.

4.  **Chapter Outlines:**
    *   Specify the desired "Number of Chapters".
    *   Click "Generate Chapter Outlines" to generate outlines for each chapter, based on the Plot Outline.
    *   The generated Chapter Outlines will be displayed.
    *   You can edit each chapter outline in the "Edit Chapter Outlines" expander and use the "Save Chapter Outlines" and "Enhance Chapter Outlines" buttons.

5.  **Scene Outlines:**
    *   Specify the "Maximum Scenes per Chapter".
    *   Click "Generate Scene Outlines (All Chapters)" to generate scene outlines for all chapters.  The number of scenes per chapter will be randomly chosen between 2 and the maximum you set.
    *   The generated Scene Outlines will be displayed, organized by chapter.
    *   Each chapter has an "Edit Scene Outlines - Chapter [Number]" expander, containing a form for editing the scene outlines within that chapter. You can "Save" and "Enhance" scene outlines for each chapter independently.

6.  **Scene Parts - Text Generation:**
    *   Click "Generate Scene Parts Text (All Scenes)" to generate the actual text content for each scene, broken down into parts. This might take some time.
    *    Once generated, you can individually enhance specific parts and scenes by selecting those options and pressing the "Enhance Part [#] of Scene [#], Chapter [#]" button

## 3. Tips and Best Practices

*   **Iterative Refinement:** The Fiction Fabricator is designed for iterative refinement.  Don't be afraid to go back and edit previous steps (e.g., modify the Book Spec after generating the Plot Outline).
*   **Experiment with Models:** Try different Ollama models to see how they affect the generated content.
*   **Save Frequently:** Save your project often, especially after making significant changes or generating content.
*   **Enhance:** Use the "Enhance" buttons at each stage to improve the quality and coherence of the generated content.
* **Provide Detailed Input**: Supply a detailed story idea and well-thought edits to guide the model effectively.

## 4. Troubleshooting

*   **No models found:** Ensure your Ollama instance is running and that you have pulled at least one model.
*   **Generation errors:** If generation fails, try again, potentially with a slightly modified input or a different model. Check the application logs (in the terminal where you ran `streamlit run`) for more detailed error messages.
*   **Slow generation:**  Generating content, especially scene parts, can take time depending on the model and your hardware. Be patient.

This guide provides a basic overview of how to use the Fiction Fabricator application.  Experiment with the different features and workflow steps to discover the best way to create your novel!