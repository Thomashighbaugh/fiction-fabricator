# File: Tools/prompt_generator.py
# Purpose: Generates a refined prompt.txt for AIStoryWriter using an LLM.
# This script is self-contained and should be run from the project's root directory
# or have the project root in its Python path if run from Tools/.

"""
AIStoryWriter Prompt Generator Utility.

This script takes a basic user idea, a desired story title, and an Ollama model
to generate a more detailed and refined `prompt.txt` file. This output file
is structured to be an effective input for the main Write.py script.

The process involves:
1. Expanding the user's initial idea using the LLM.
2. Having the LLM critique its own expansion based on criteria beneficial for AIStoryWriter.
3. Refining the prompt based on this critique.
4. Saving the final prompt to `Prompts/<SanitizedTitle>/prompt.txt`.

Requirements:
- ollama Python library (`pip install ollama`)
- An accessible Ollama server with the specified model.

Usage:
python Tools/prompt_generator.py -m "ollama://huggingface.co/DavidAU/Llama-3.2-8X4B-MOE-V2-Dark-Champion-Instruct-uncensored-abliterated-21B-GGUF" -t "CrashLanded" -i "After the surveying vessel crashed on the planet it was sent to determine viability for human colonization, the spunky 23 year old mechanic Jade and the hardened 31 year old security officer Charles find the planet is not uninhabited but teeming with humans living in primitive tribal conditions and covered in the ruins of an extinct human society which had advanced technologies beyond what are known to Earth. Now they must navigate the politics of these tribes while trying to repair their communication equipment to call for rescue, while learning to work together despite their initial skepticism about the other."
"""

import argparse
import os
import sys
import json
import re
import subprocess # For checking/installing ollama
import importlib # For checking/installing ollama

# --- Self-Contained Ollama Client ---
# (Simplified version, no advanced URI parsing like in AIStoryWriter's Wrapper)

def ensure_ollama_installed():
    """Checks if the ollama library is installed and prompts for installation if not."""
    try:
        importlib.import_module("ollama")
        print("Ollama library found.")
    except ImportError:
        print("Ollama library not found.")
        try:
            print("Attempting to install ollama library...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
            print("Ollama library installed successfully. Please re-run the script.")
            sys.exit(0) # Exit so user can re-run with library now available
        except subprocess.CalledProcessError as e:
            print(f"Failed to install ollama: {e}")
            print("Please install it manually: pip install ollama")
            sys.exit(1)

ensure_ollama_installed()
import ollama # Now safe to import

class SimpleOllamaClient:
    """A basic client to interact with an Ollama model."""
    def __init__(self, model_uri: str, host: str = "http://localhost:11434"):
        self.model_name = self._parse_model_name(model_uri)
        self.host = host
        try:
            self.client = ollama.Client(host=self.host)
            # Check if model exists, try to pull if not
            try:
                self.client.show(self.model_name)
                print(f"Model '{self.model_name}' found on Ollama server at {self.host}.")
            except ollama.ResponseError:
                print(f"Model '{self.model_name}' not found locally. Attempting to pull...")
                self.client.pull(self.model_name)
                print(f"Model '{self.model_name}' pulled successfully.")
        except Exception as e:
            print(f"Error initializing Ollama client or pulling model '{self.model_name}' from '{self.host}': {e}")
            print("Please ensure Ollama server is running and the model is available.")
            sys.exit(1)

    def _parse_model_name(self, model_uri: str) -> str:
        """Extracts model name from a simple URI like ollama://model:tag."""
        if model_uri.startswith("ollama://"):
            return model_uri[len("ollama://"):]
        return model_uri # Assume it's just the model name

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Generates text using the Ollama model."""
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': user_prompt})

        try:
            print(f"\nSending request to Ollama model: {self.model_name}...")
            if len(user_prompt) > 100:
                 print(f"User Prompt (first 100 chars): {user_prompt[:100]}...")
            else:
                 print(f"User Prompt: {user_prompt}")

            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options={"temperature": temperature}
            )
            content = response['message']['content']
            print("Ollama response received.")
            return content.strip()
        except Exception as e:
            print(f"Error during Ollama generation: {e}")
            return f"Error: Could not generate response from Ollama - {e}"

# --- Prompts for this script ---

EXPAND_IDEA_PROMPT_TEMPLATE = """
You are a creative assistant helping to flesh out a story idea into a more detailed prompt suitable for an AI story generator like AIStoryWriter.
The user has provided a basic idea and a title.
Your goal is to expand this into a richer concept that AIStoryWriter can effectively use.

User's Title: "{title}"
User's Basic Idea: "{idea}"

Expand this into a more detailed story prompt. Consider including or hinting at:
- **Genre and Tone:** What kind of story is it (e.g., sci-fi, fantasy, mystery, horror, romance)? What is the desired mood (e.g., dark, humorous, adventurous, introspective)?
- **Core Conflict:** What is the central problem or challenge the characters will face?
- **Main Character(s) Sketch:** Briefly introduce 1-2 main characters. What are their key traits or motivations related to the idea?
- **Setting Snippet:** A brief hint about the world or primary location.
- **Key Plot Beats (Optional but helpful):** If any specific events or turning points come to mind from the user's idea, mention them.
- **Specific "Do's" or "Don'ts" (Optional):** Are there any constraints or desired inclusions that would be important for the AI story generator? For example, "The story must include a talking cat," or "Avoid overly graphic violence."
- **Target Audience/Style (Optional):** E.g., "Young Adult fantasy with a fast pace," or "Literary fiction with deep character exploration."

Format your response as a single block of text that would serve as a good, detailed `prompt.txt` for AIStoryWriter.
Make it engaging and provide enough substance for the AI to build upon.
"""

CRITIQUE_EXPANDED_PROMPT_TEMPLATE = """
You are an expert AI prompt engineer evaluating a story prompt intended for an advanced AI story generation system.
The system will use this prompt to generate story elements, an outline, and then the full narrative.

Here is the expanded story prompt you need to critique:
---
{expanded_prompt}
---

Critique this prompt based on the following criteria for its effectiveness as input to AIStoryWriter:
1.  **Clarity and Specificity:**
    *   Is the core story idea clear?
    *   Are genre, tone, and style sufficiently indicated or implied?
    *   Are main characters (if mentioned) distinct enough to start with?
    *   Is the central conflict understandable?
    *   Does it provide enough specific detail for the AI to avoid overly generic output, without being overly prescriptive and stifling creativity?
2.  **Completeness (for AIStoryWriter):**
    *   Does it hint at enough elements for `StoryElements.generate_story_elements` to work well (e.g., potential for themes, setting details, character motivations)?
    *   Does it provide a good foundation for `OutlineGenerator.generate_outline` to create a multi-chapter plot?
3.  **Actionability for AI:**
    *   Are there clear starting points for the AI?
    *   Are there any ambiguities or contradictions that might confuse the AI?
4.  **Engagement Factor:**
    *   Does the prompt itself sound interesting and inspire creative possibilities?

Provide your critique as a list of bullet points (strengths and weaknesses).
Be constructive. The goal is to identify areas for improvement.
Example:
- Strength: Clearly defines the sci-fi genre and a compelling central mystery.
- Weakness: Main character motivation is vague. Suggest adding a specific goal.
- Weakness: Setting is too generic. Suggest adding 1-2 unique details about the world.
"""

REFINE_PROMPT_BASED_ON_CRITIQUE_TEMPLATE = """
You are a master creative assistant. You have an expanded story prompt and a critique of that prompt.
Your task is to revise and improve the original expanded prompt based *only* on the provided critique.
The goal is to create a final, high-quality prompt.txt file that will be excellent input for an AI story generator like AIStoryWriter.

Original Expanded Story Prompt:
---
{expanded_prompt}
---

Critique of the Expanded Story Prompt:
---
{critique}
---

Revise the "Original Expanded Story Prompt" to address the points raised in the "Critique".
- Incorporate suggestions for clarity, specificity, and completeness.
- Resolve ambiguities or add details where the critique indicated they were lacking.
- Enhance the engagement factor if possible, based on the critique.
- Do NOT introduce entirely new story ideas not related to the original prompt or the critique. Focus on refining what's there according to the feedback.

Output ONLY the final, revised, and improved story prompt text. This will be saved directly as `prompt.txt`.
"""

def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be suitable for a filename or directory name."""
    name = re.sub(r'[^\w\s-]', '', name).strip() # Remove non-alphanumeric (except underscore, hyphen, space)
    name = re.sub(r'[-\s]+', '_', name) # Replace spaces and hyphens with underscores
    return name if name else "Untitled_Prompt"


def main():
    parser = argparse.ArgumentParser(description="AIStoryWriter Self-Contained Prompt Generator.")
    parser.add_argument(
        "-m", "--model",
        required=True,
        help="Ollama model URI (e.g., 'ollama://llama3:8b' or just 'llama3:8b')."
    )
    parser.add_argument(
        "-t", "--title",
        required=True,
        help="Desired title for the story (used for subdirectory name)."
    )
    parser.add_argument(
        "-i", "--idea",
        required=True,
        help="The user's basic story idea or concept."
    )
    parser.add_argument(
        "--host",
        default="http://localhost:11434",
        help="Ollama server host address (default: http://localhost:11434)."
    )
    parser.add_argument(
        "--temp",
        type=float,
        default=0.7,
        help="Temperature for LLM generation (default: 0.7)."
    )

    args = parser.parse_args()

    print("--- AIStoryWriter Prompt Generator ---")

    # Initialize Ollama client
    ollama_client = SimpleOllamaClient(model_uri=args.model, host=args.host)

    # --- Step 1: Expand User's Idea ---
    print("\nStep 1: Expanding user's idea...")
    expand_user_prompt = EXPAND_IDEA_PROMPT_TEMPLATE.format(title=args.title, idea=args.idea)
    expanded_prompt = ollama_client.generate(
        system_prompt="You are a creative assistant helping to flesh out story ideas.",
        user_prompt=expand_user_prompt,
        temperature=args.temp
    )
    if expanded_prompt.startswith("Error:"):
        print(f"Failed to expand prompt: {expanded_prompt}")
        sys.exit(1)
    print("\n--- Expanded Prompt ---")
    print(expanded_prompt)
    print("-----------------------")

    # --- Step 2: Critique the Expanded Prompt ---
    print("\nStep 2: Critiquing the expanded prompt...")
    critique_user_prompt = CRITIQUE_EXPANDED_PROMPT_TEMPLATE.format(expanded_prompt=expanded_prompt)
    critique = ollama_client.generate(
        system_prompt="You are an expert AI prompt engineer and literary critic.",
        user_prompt=critique_user_prompt,
        temperature=0.5 # Lower temp for more focused critique
    )
    if critique.startswith("Error:"):
        print(f"Failed to critique prompt: {critique}")
        # Proceed with un-critiqued prompt if critique fails? Or exit? For now, proceed.
        print("Warning: Critique failed. Proceeding with the initially expanded prompt.")
        final_prompt_text = expanded_prompt
    else:
        print("\n--- Critique ---")
        print(critique)
        print("----------------")

        # --- Step 3: Refine Prompt Based on Critique ---
        print("\nStep 3: Refining prompt based on critique...")
        refine_user_prompt = REFINE_PROMPT_BASED_ON_CRITIQUE_TEMPLATE.format(
            expanded_prompt=expanded_prompt,
            critique=critique
        )
        final_prompt_text = ollama_client.generate(
            system_prompt="You are a master creative assistant, skilled at revising text based on feedback.",
            user_prompt=refine_user_prompt,
            temperature=args.temp
        )
        if final_prompt_text.startswith("Error:"):
            print(f"Failed to refine prompt: {final_prompt_text}")
            print("Warning: Refinement failed. Using the initially expanded (but critiqued) prompt if critique was successful, or just the expanded one.")
            final_prompt_text = expanded_prompt # Fallback
    
    print("\n--- Final Refined Prompt ---")
    print(final_prompt_text)
    print("--------------------------")

    # --- Step 4: Save the Final Prompt ---
    # Determine project root relative to this script's location
    # Assuming this script is in Tools/ and Prompts/ is at the project root.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) # Moves up one level from Tools/ to 
    
    prompts_base_dir = os.path.join(project_root, "Prompts")
    if not os.path.exists(prompts_base_dir):
        try:
            os.makedirs(prompts_base_dir)
            print(f"Created base Prompts directory: {prompts_base_dir}")
        except OSError as e:
            print(f"Error: Could not create base Prompts directory at '{prompts_base_dir}': {e}")
            print("Please ensure you have write permissions or create it manually.")
            sys.exit(1)
            
    sanitized_title = sanitize_filename(args.title)
    prompt_subdir = os.path.join(prompts_base_dir, sanitized_title)

    try:
        os.makedirs(prompt_subdir, exist_ok=True)
        output_path = os.path.join(prompt_subdir, "prompt.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_prompt_text)
        print(f"\nSuccessfully generated and saved prompt to: {output_path}")
    except OSError as e:
        print(f"Error creating directory or writing file to '{prompt_subdir}': {e}")
        print("Please check permissions and path.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during file saving: {e}")
        sys.exit(1)

    print("\n--- Prompt Generation Complete ---")

if __name__ == "__main__":
    main()