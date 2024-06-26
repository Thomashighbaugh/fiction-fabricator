# fiction-fabricator/src/llmconnection.py
import g4f
from src.prompts import get_system_prompt
import os 
def call_g4f_api(prompt):
    """
    Calls the GPT4Free API with the provided prompt and system message.

    Args:
        prompt: The prompt to send to the API.

    Returns:
        The generated text from the GPT4Free API.
    """
    api_instance = g4f.ChatCompletion()

        # Call the API with the specified parameters
    response = api_instance.create(
          
            # TODO: possibly add in a means of selecting other g4f models at the beginning of the program.
            provider=g4f.Provider.DeepInfra,
            api_key=os.getenv("G4F_API_KEY"),
            model="microsoft/WizardLM-2-8x22B",
            # TODO: Create interactive means of changing the system prompt
            messages=[{"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": prompt}],

        )

        # Extract and return the generated text
    generated_text = response

    return generated_text
